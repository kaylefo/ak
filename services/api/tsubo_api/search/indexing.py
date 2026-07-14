"""Build and maintain the derived OpenSearch listings index."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tsubo_api.config import get_settings
from tsubo_api.models.administrative import AdministrativeEntity
from tsubo_api.models.listings import CanonicalListing
from tsubo_api.models.sources import Source
from tsubo_api.services.search import SearchService

logger = structlog.get_logger(__name__)

LISTINGS_INDEX_MAPPING: dict[str, Any] = {
    "settings": {
        "index": {"number_of_shards": 1, "number_of_replicas": 0},
        "analysis": {
            "analyzer": {
                "ja_analyzer": {"type": "custom", "tokenizer": "kuromoji_tokenizer"},
                "en_analyzer": {"type": "english"},
            }
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "slug": {"type": "keyword"},
            "title_ja": {"type": "text", "analyzer": "ja_analyzer"},
            "title_en": {"type": "text", "analyzer": "en_analyzer"},
            "description_ja": {"type": "text", "analyzer": "ja_analyzer"},
            "description_en": {"type": "text", "analyzer": "en_analyzer"},
            "address_ja": {"type": "text", "analyzer": "ja_analyzer"},
            "address_en": {"type": "text"},
            "prefecture": {"type": "keyword"},
            "municipality": {"type": "keyword"},
            "property_type": {"type": "keyword"},
            "transaction_type": {"type": "keyword"},
            "status": {"type": "keyword"},
            "price_jpy": {"type": "long"},
            "price_kind": {"type": "keyword"},
            "location_precision": {"type": "keyword"},
            "source_class": {"type": "keyword"},
            "source_key": {"type": "keyword"},
            "last_seen_at": {"type": "date"},
            "published_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "location": {"type": "geo_point"},
        }
    },
}


def _async_database_url() -> str:
    settings = get_settings()
    url = settings.database_url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def ensure_index(search_service: SearchService) -> None:
    index_name = search_service.settings.opensearch_index_listings
    client = search_service.client
    exists = await client.indices.exists(index=index_name)
    if not exists:
        await client.indices.create(index=index_name, body=LISTINGS_INDEX_MAPPING)
        logger.info("opensearch_index_created", index=index_name)


from tsubo_api.serializers import _coords_from_geom


def listing_to_index_doc(
    listing: CanonicalListing,
    *,
    municipality: AdministrativeEntity | None,
    prefecture: AdministrativeEntity | None,
    source: Source | None,
) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "id": str(listing.id),
        "slug": listing.slug,
        "title_ja": listing.title_ja,
        "title_en": listing.title_en,
        "description_ja": listing.description_ja,
        "description_en": listing.description_en,
        "address_ja": listing.address_ja,
        "address_en": listing.address_en,
        "property_type": str(listing.property_type),
        "transaction_type": str(listing.transaction_type),
        "status": str(listing.status),
        "price_kind": str(listing.price_kind),
        "location_precision": str(listing.location_precision),
        "last_seen_at": listing.last_seen_at.isoformat() if listing.last_seen_at else None,
        "published_at": listing.published_at.isoformat() if listing.published_at else None,
        "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
    }
    if listing.price_jpy is not None:
        doc["price_jpy"] = int(listing.price_jpy)
    if municipality:
        doc["municipality"] = municipality.slug
    if prefecture:
        doc["prefecture"] = prefecture.slug
    if source:
        doc["source_key"] = source.source_key
        doc["source_class"] = str(source.source_class)
    coords = _coords_from_geom(listing.geom)
    if coords:
        doc["location"] = {"lat": coords["lat"], "lon": coords["lng"]}
    return doc


async def index_listing_batch(listing_ids: list[str]) -> dict[str, Any]:
    settings = get_settings()
    search_service = SearchService(settings)
    engine = create_async_engine(_async_database_url())
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    indexed = 0
    errors: list[str] = []

    try:
        await ensure_index(search_service)
        async with session_factory() as session:
            for listing_id in listing_ids:
                try:
                    listing = await _load_listing(session, listing_id)
                    if listing is None:
                        continue
                    doc = await _doc_for_listing(session, listing)
                    await search_service.index_listing(doc)
                    indexed += 1
                except Exception as exc:
                    errors.append(f"{listing_id}: {exc}")
    finally:
        await search_service.close()
        await engine.dispose()

    return {"indexed": indexed, "errors": errors}


async def reindex_all(batch_size: int = 500) -> dict[str, Any]:
    settings = get_settings()
    search_service = SearchService(settings)
    engine = create_async_engine(_async_database_url())
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    indexed = 0
    errors: list[str] = []

    try:
        await ensure_index(search_service)
        async with session_factory() as session:
            offset = 0
            while True:
                stmt = (
                    select(CanonicalListing)
                    .order_by(CanonicalListing.id)
                    .offset(offset)
                    .limit(batch_size)
                )
                rows = (await session.execute(stmt)).scalars().all()
                if not rows:
                    break
                for listing in rows:
                    try:
                        doc = await _doc_for_listing(session, listing)
                        await search_service.index_listing(doc)
                        indexed += 1
                    except Exception as exc:
                        errors.append(f"{listing.id}: {exc}")
                offset += batch_size
    finally:
        await search_service.close()
        await engine.dispose()

    return {"indexed": indexed, "errors": errors}


async def _load_listing(session: AsyncSession, listing_id: str) -> CanonicalListing | None:
    from uuid import UUID

    try:
        uid = UUID(listing_id)
        stmt = select(CanonicalListing).where(CanonicalListing.id == uid)
    except ValueError:
        stmt = select(CanonicalListing).where(CanonicalListing.slug == listing_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def _doc_for_listing(session: AsyncSession, listing: CanonicalListing) -> dict[str, Any]:
    municipality = None
    prefecture = None
    if listing.administrative_entity_id:
        municipality = await session.get(AdministrativeEntity, listing.administrative_entity_id)
        if municipality and municipality.parent_id:
            prefecture = await session.get(AdministrativeEntity, municipality.parent_id)
    source = await session.get(Source, listing.source_id)
    return listing_to_index_doc(listing, municipality=municipality, prefecture=prefecture, source=source)
