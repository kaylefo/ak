from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.dependencies import get_session
from tsubo_api.errors import NotFoundError
from tsubo_api.models.listings import CanonicalListing
from tsubo_api.models.sources import Source, SourceJurisdiction

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
async def list_sources(
    source_class: str | None = Query(None),
    health: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    stmt = select(Source)
    if source_class:
        stmt = stmt.where(Source.source_class == source_class)
    if health:
        stmt = stmt.where(Source.health == health)

    result = await session.execute(stmt.order_by(Source.name))
    items: list[dict] = []
    for source in result.scalars().all():
        listing_count = (
            await session.execute(
                select(func.count()).select_from(CanonicalListing).where(
                    CanonicalListing.source_id == source.id
                )
            )
        ).scalar_one()
        municipality_count = (
            await session.execute(
                select(func.count()).select_from(SourceJurisdiction).where(
                    SourceJurisdiction.source_id == source.id
                )
            )
        ).scalar_one()
        jurisdiction = (
            await session.execute(
                select(SourceJurisdiction)
                .where(SourceJurisdiction.source_id == source.id)
                .limit(1)
            )
        ).scalar_one_or_none()
        items.append(
            {
                "id": str(source.id),
                "slug": source.slug or source.source_key or str(source.id),
                "name": source.name_en or source.name,
                "name_ja": source.name,
                "source_class": str(source.source_class),
                "access_mode": str(source.access_mode),
                "health": str(source.health),
                "coverage_state": str(jurisdiction.coverage_state) if jurisdiction else "UNDER_REVIEW",
                "listing_count": listing_count,
                "municipality_count": municipality_count,
                "last_synced_at": source.updated_at.isoformat(),
                "homepage_url": source.base_url,
            }
        )
    return items


@router.get("/{source_ref}")
async def get_source(
    source_ref: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    from uuid import UUID

    stmt = select(Source).where(Source.slug == source_ref)
    try:
        stmt = select(Source).where(
            (Source.slug == source_ref) | (Source.id == UUID(source_ref))
        )
    except ValueError:
        pass
    result = await session.execute(stmt)
    source = result.scalar_one_or_none()
    if source is None:
        stmt = select(Source).where(Source.source_key == source_ref)
        source = (await session.execute(stmt)).scalar_one_or_none()
    if source is None:
        raise NotFoundError(f"Source {source_ref} not found")

    listing_count = (
        await session.execute(
            select(func.count()).select_from(CanonicalListing).where(
                CanonicalListing.source_id == source.id
            )
        )
    ).scalar_one()
    municipality_count = (
        await session.execute(
            select(func.count()).select_from(SourceJurisdiction).where(
                SourceJurisdiction.source_id == source.id
            )
        )
    ).scalar_one()
    jurisdiction = (
        await session.execute(
            select(SourceJurisdiction).where(SourceJurisdiction.source_id == source.id).limit(1)
        )
    ).scalar_one_or_none()

    return {
        "id": str(source.id),
        "slug": source.slug or source.source_key or str(source.id),
        "name": source.name_en or source.name,
        "name_ja": source.name,
        "source_class": str(source.source_class),
        "access_mode": str(source.access_mode),
        "health": str(source.health),
        "coverage_state": str(jurisdiction.coverage_state) if jurisdiction else "UNDER_REVIEW",
        "listing_count": listing_count,
        "municipality_count": municipality_count,
        "last_synced_at": source.updated_at.isoformat(),
        "homepage_url": source.base_url,
        "description": source.metadata_.get("description") if source.metadata_ else None,
        "prefecture_slug": None,
        "prefecture_name": None,
        "municipality_slug": None,
        "municipality_name": None,
        "parser_version": source.metadata_.get("adapter_version") if source.metadata_ else None,
        "notes": jurisdiction.notes if jurisdiction else None,
    }
