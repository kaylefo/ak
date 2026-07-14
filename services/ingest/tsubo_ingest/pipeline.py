"""End-to-end ingestion pipeline: fetch → snapshot → parse → canonical listing."""

from __future__ import annotations

import hashlib
import os
import re
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import structlog
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from adapters import ALL_ADAPTERS
from adapters.base import is_bot_challenge_page
from adapters.no_inventory import NoInventoryClassifier
from tsubo_contracts.enums import (
    AccessMode,
    ConditionCategory,
    EntityType,
    ListingStatus,
    LocationPrecision,
    PriceKind,
    PropertyType,
    SourceClass,
    SourceHealth,
    TransactionType,
)
from tsubo_ingest.adapter import ParsedListing
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig
from tsubo_ingest.http_client import SafeHttpClient
from tsubo_ingest.normalize.money import normalize_money
from tsubo_ingest.storage import HybridSnapshotStore
from tsubo_api.models.administrative import AdministrativeEntity
from tsubo_api.models.listings import CanonicalListing, CrawlRun, RawSnapshot, SourceListingRecord
from tsubo_api.models.sources import Source
from tsubo_api.serializers import slugify
from tsubo_api.services.translation import GlossaryTranslationService

logger = structlog.get_logger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.7",
}

_B_ID_RE = re.compile(r"/b-(\d+)/?", re.IGNORECASE)
_PREF_PATH_RE = re.compile(r"/akiyabank/(?:tohoku|kanto|chubu|kansai|chugoku|shikoku|kyushu)/([^/]+)/?")


def _adapter_for(source: SourceConfig):
    for adapter in ALL_ADAPTERS:
        if adapter.matches(source):
            return adapter
    raise ValueError(f"No adapter for source {source.source_id}")


def _source_config_from_row(row: Source) -> SourceConfig:
    meta = row.metadata_ or {}
    return SourceConfig(
        source_id=row.source_key or str(row.id),
        name=row.name,
        adapter_id=meta.get("adapter_id", "generic_html"),
        base_url=row.base_url or "",
        source_class=SourceClass(str(row.source_class)),
        access_mode=AccessMode(str(row.access_mode)),
        entity_type=EntityType(meta.get("entity_type", EntityType.MUNICIPALITY)),
        metadata=meta,
    )


def _price_kind_from_parsed(listing: ParsedListing) -> PriceKind:
    money = normalize_money(listing.price_text)
    return PriceKind(money.kind) if money.kind in PriceKind.__members__.values() else PriceKind.UNKNOWN


def _infer_property_type(title: str | None, raw: dict[str, Any]) -> PropertyType:
    text = f"{title or ''} {raw.get('category', '')}"
    if "古民家" in text or "kominka" in text.lower():
        return PropertyType.KOMINKA
    if "農地" in text or "農家" in text:
        return PropertyType.HOUSE_WITH_FARMLAND
    if "空き地" in text or "土地" in text:
        return PropertyType.VACANT_LAND
    if "店舗" in text:
        return PropertyType.SHOP_WITH_RESIDENCE
    return PropertyType.DETACHED_HOUSE


def _resolve_municipality(session: Session, address: str | None, prefecture_hint: str | None) -> uuid.UUID | None:
    if not address:
        return None
    # Match municipality name contained in address
    stmt = select(AdministrativeEntity).where(AdministrativeEntity.entity_type == EntityType.MUNICIPALITY)
    for entity in session.execute(stmt).scalars():
        if entity.canonical_name and entity.canonical_name in address:
            return entity.id
        if entity.canonical_name_en and entity.canonical_name_en.lower() in address.lower():
            return entity.id
    if prefecture_hint:
        pref_slug = slugify(prefecture_hint)
        pref = session.execute(
            select(AdministrativeEntity).where(
                AdministrativeEntity.slug == pref_slug,
                AdministrativeEntity.entity_type == EntityType.PREFECTURE,
            )
        ).scalar_one_or_none()
        if pref:
            return pref.id
    return None


def _listing_slug(external_id: str, title: str | None) -> str:
    base = slugify(title or external_id)
    return f"{base}-{external_id}".lower()[:240]


class IngestionPipeline:
    def __init__(self, database_url: str | None = None) -> None:
        db_url = database_url or os.environ.get(
            "DATABASE_URL_SYNC",
            "postgresql://tsubo:tsubo@localhost:5432/tsubo",
        )
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.http = SafeHttpClient(default_headers=DEFAULT_HEADERS)
        self.snapshots = HybridSnapshotStore()
        self.translator = GlossaryTranslationService()
        self.no_inventory = NoInventoryClassifier()

    def crawl_source_key(self, source_key: str, *, force: bool = False, max_details: int = 50) -> dict[str, Any]:
        started = datetime.now(UTC)
        errors: list[str] = []
        listings_seen = 0
        listings_upserted = 0

        with self.SessionLocal() as session:
            row = session.execute(select(Source).where(Source.source_key == source_key)).scalar_one_or_none()
            if row is None:
                raise ValueError(f"Unknown source_key: {source_key}")

            config = _source_config_from_row(row)
            adapter = _adapter_for(config)
            crawl = CrawlRun(
                source_id=row.id,
                status="running",
                started_at=started,
                records_found=0,
            )
            session.add(crawl)
            session.flush()

            try:
                result = self._crawl_index(session, row, config, adapter, crawl, force=force)
                listings_seen += result["listings_seen"]
                listings_upserted += result.get("index_upserted", 0)
                detail_urls = result["detail_urls"][:max_details]

                for detail_url in detail_urls:
                    try:
                        if self._ingest_detail(session, row, config, adapter, crawl, detail_url, force=force):
                            listings_upserted += 1
                    except Exception as exc:
                        errors.append(f"{detail_url}: {exc}")
                        logger.warning("detail_ingest_failed", url=detail_url, error=str(exc))

                row.health = SourceHealth.HEALTHY if not errors else SourceHealth.DEGRADED
                crawl.status = "completed" if not errors else "completed_with_errors"
                crawl.records_found = listings_seen
                crawl.finished_at = datetime.now(UTC)
                session.commit()
            except Exception as exc:
                crawl.status = "failed"
                crawl.error_message = str(exc)
                crawl.finished_at = datetime.now(UTC)
                row.health = SourceHealth.TEMPORARILY_UNAVAILABLE
                session.commit()
                raise

        finished = datetime.now(UTC)
        return {
            "source_id": source_key,
            "force": force,
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "listings_seen": listings_seen,
            "listings_upserted": listings_upserted,
            "errors": errors,
            "status": "completed" if not errors else "completed_with_errors",
            "snapshot_backend": self.snapshots.backend,
        }

    def _crawl_index(
        self,
        session: Session,
        source: Source,
        config: SourceConfig,
        adapter: Any,
        crawl: CrawlRun,
        *,
        force: bool,
    ) -> dict[str, Any]:
        index_url = config.metadata.get("index_url") or config.base_url
        response = self.http.get(index_url)
        stored = self.snapshots.save(config.source_id, response)
        session.add(
            RawSnapshot(
                crawl_run_id=crawl.id,
                source_id=source.id,
                s3_key=stored.key,
                content_hash=stored.sha256,
                captured_at=stored.stored_at,
                metadata_={
                    "url": response.url,
                    "backend": stored.backend,
                    "page_kind": "index",
                },
            )
        )
        ctx = CrawlContext(source=config, url=response.url, metadata=config.metadata)
        parsed = adapter.parse(ctx, response)

        # Ingest index-card listings immediately (price/address available without detail fetch)
        index_upserted = 0
        for listing in parsed.listings:
            if listing.detail_url and listing.title and not is_bot_challenge_page(response.text):
                if self._upsert_from_parsed_listing(session, source, crawl, listing, response, page_kind="index"):
                    index_upserted += 1

        detail_urls: list[str] = []
        for listing in parsed.listings:
            if listing.detail_url:
                detail_urls.append(listing.detail_url)
        for link in parsed.links:
            if link.url and "/b-" in link.url:
                detail_urls.append(link.url)

        seen: set[str] = set()
        unique_urls: list[str] = []
        for u in detail_urls:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)

        return {
            "listings_seen": len(unique_urls),
            "detail_urls": unique_urls,
            "index_upserted": index_upserted,
        }

    def _ingest_detail(
        self,
        session: Session,
        source: Source,
        config: SourceConfig,
        adapter: Any,
        crawl: CrawlRun,
        detail_url: str,
        *,
        force: bool,
    ) -> bool:
        response = self.http.get(detail_url)
        if is_bot_challenge_page(response.text, status_code=response.status_code):
            logger.info("detail_skipped_bot_challenge", url=detail_url, status=response.status_code)
            return False

        stored = self.snapshots.save(config.source_id, response)
        snapshot = RawSnapshot(
            crawl_run_id=crawl.id,
            source_id=source.id,
            s3_key=stored.key,
            content_hash=stored.sha256,
            captured_at=stored.stored_at,
            metadata_={"url": response.url, "backend": stored.backend, "page_kind": "detail"},
        )
        session.add(snapshot)
        session.flush()

        ctx = CrawlContext(source=config, url=response.url, metadata={**config.metadata, "page_kind": "detail"})
        parsed = adapter.parse(ctx, response)
        if not parsed.listings:
            return False

        listing = parsed.listings[0]
        if listing.title and listing.title.lower() == "javascript is disabled":
            return False

        return self._upsert_from_parsed_listing(session, source, crawl, listing, response, snapshot=snapshot)

    def _upsert_from_parsed_listing(
        self,
        session: Session,
        source: Source,
        crawl: CrawlRun,
        listing: ParsedListing,
        response: FetchResponse,
        *,
        snapshot: RawSnapshot | None = None,
        page_kind: str = "detail",
    ) -> bool:
        if not listing.external_id or (listing.title and listing.title.lower() == "javascript is disabled"):
            return False

        if snapshot is None:
            stored = self.snapshots.save(source.source_key or str(source.id), response)
            snapshot = RawSnapshot(
                crawl_run_id=crawl.id,
                source_id=source.id,
                s3_key=stored.key,
                content_hash=stored.sha256,
                captured_at=stored.stored_at,
                metadata_={"url": response.url, "backend": stored.backend, "page_kind": page_kind},
            )
            session.add(snapshot)
            session.flush()

        return self._upsert_canonical(session, source, snapshot, listing, response)

    def _upsert_canonical(
        self,
        session: Session,
        source: Source,
        snapshot: RawSnapshot,
        listing: ParsedListing,
        response: FetchResponse,
    ) -> bool:
        now = datetime.now(UTC)
        content_hash = hashlib.sha256(response.content).hexdigest()
        record = SourceListingRecord(
            source_id=source.id,
            raw_snapshot_id=snapshot.id,
            source_listing_id=listing.external_id,
            raw_data={
                "fields": listing.raw_fields,
                "title": listing.title,
                "price_text": listing.price_text,
                "address": listing.address,
                "detail_url": listing.detail_url,
            },
            fetched_at=now,
            content_hash=content_hash,
        )
        session.add(record)
        session.flush()

        money = normalize_money(listing.price_text)
        price_kind = money.kind
        prefecture_hint = listing.raw_fields.get("prefecture")
        municipality_id = _resolve_municipality(session, listing.address, prefecture_hint)

        title_ja = listing.title
        title_en = self.translator.translate_text(title_ja) if title_ja else None
        desc_ja = listing.raw_fields.get("description") or listing.raw_fields.get("ポイント")
        desc_en = self.translator.translate_text(desc_ja) if desc_ja else None

        existing = session.execute(
            select(CanonicalListing).where(
                CanonicalListing.source_id == source.id,
                CanonicalListing.slug == _listing_slug(listing.external_id, title_ja),
            )
        ).scalar_one_or_none()

        fields = {
            "source_listing_record_id": record.id,
            "administrative_entity_id": municipality_id,
            "status": ListingStatus.ACTIVE,
            "transaction_type": listing.transaction_type,
            "property_type": _infer_property_type(title_ja, listing.raw_fields),
            "price_jpy": Decimal(listing.price_yen) if listing.price_yen is not None else None,
            "price_kind": price_kind,
            "area_sqm": Decimal(str(listing.area_sqm)) if listing.area_sqm else None,
            "land_area_sqm": Decimal(str(listing.raw_fields.get("land_sqm"))) if listing.raw_fields.get("land_sqm") else None,
            "location_precision": LocationPrecision.MUNICIPALITY if municipality_id else LocationPrecision.UNKNOWN,
            "condition_category": ConditionCategory.UNKNOWN,
            "address_ja": listing.address,
            "title_ja": title_ja,
            "title_en": title_en,
            "description_ja": desc_ja,
            "description_en": desc_en,
            "layout": {"raw": listing.layout} if listing.layout else None,
            "last_seen_at": now,
        }

        if existing:
            for key, value in fields.items():
                setattr(existing, key, value)
            canonical = existing
        else:
            canonical = CanonicalListing(
                slug=_listing_slug(listing.external_id, title_ja),
                source_id=source.id,
                published_at=now,
                **fields,
            )
            session.add(canonical)

        session.flush()
        return True
