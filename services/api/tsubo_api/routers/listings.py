from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.dependencies import get_fx_service, get_search_service, get_session
from tsubo_api.errors import NotFoundError
from tsubo_api.models.listings import CanonicalListing
from tsubo_api.schemas.common import PaginatedResponse
from tsubo_api.serializers import listing_to_detail, listing_to_summary
from tsubo_api.services.fx import FXService
from tsubo_api.services.search import SearchService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("")
async def list_listings(
    q: str | None = Query(None),
    prefecture: str | None = Query(None),
    municipality: str | None = Query(None),
    transaction_type: str | None = Query(None),
    property_type: str | None = Query(None),
    min_price_jpy: int | None = Query(None),
    max_price_jpy: int | None = Query(None),
    min_price_usd: int | None = Query(None),
    max_price_usd: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    fx_service: FXService = Depends(get_fx_service),
) -> dict:
    stmt = select(CanonicalListing)
    if transaction_type:
        stmt = stmt.where(CanonicalListing.transaction_type == transaction_type)
    if property_type:
        stmt = stmt.where(CanonicalListing.property_type == property_type)
    if min_price_jpy is not None:
        stmt = stmt.where(CanonicalListing.price_jpy >= min_price_jpy)
    if max_price_jpy is not None:
        stmt = stmt.where(CanonicalListing.price_jpy <= max_price_jpy)
    if min_price_usd is not None or max_price_usd is not None:
        from decimal import Decimal

        min_jpy, max_jpy, fx_meta = await fx_service.convert_usd_bounds_to_jpy(
            session,
            Decimal(min_price_usd) if min_price_usd is not None else None,
            Decimal(max_price_usd) if max_price_usd is not None else None,
        )
        if min_jpy is not None:
            stmt = stmt.where(CanonicalListing.price_jpy >= min_jpy)
        if max_jpy is not None:
            stmt = stmt.where(CanonicalListing.price_jpy <= max_jpy)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(
                CanonicalListing.title_ja.ilike(pattern),
                CanonicalListing.title_en.ilike(pattern),
                CanonicalListing.address_ja.ilike(pattern),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()
    offset = (page - 1) * page_size
    result = await session.execute(
        stmt.order_by(CanonicalListing.last_seen_at.desc()).offset(offset).limit(page_size)
    )
    rows = result.scalars().all()
    items = [await listing_to_summary(row, session, fx_service) for row in rows]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": offset + len(items) < total,
    }


@router.get("/{listing_ref}")
async def get_listing(
    listing_ref: str,
    session: AsyncSession = Depends(get_session),
    fx_service: FXService = Depends(get_fx_service),
    search_service: SearchService = Depends(get_search_service),
) -> dict:
    stmt = select(CanonicalListing).where(
        or_(CanonicalListing.slug == listing_ref, CanonicalListing.id == listing_ref)
    )
    try:
        listing_uuid = UUID(listing_ref)
        stmt = select(CanonicalListing).where(
            or_(CanonicalListing.slug == listing_ref, CanonicalListing.id == listing_uuid)
        )
    except ValueError:
        pass

    result = await session.execute(stmt)
    listing = result.scalar_one_or_none()
    if listing is None:
        indexed = await search_service.get_listing(listing_ref)
        if indexed is None:
            raise NotFoundError(f"Listing {listing_ref} not found")
        return indexed
    return await listing_to_detail(listing, session, fx_service)
