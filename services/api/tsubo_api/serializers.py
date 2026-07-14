from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from geoalchemy2.shape import to_shape
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.models.administrative import AdministrativeEntity, CoverageAssessment
from tsubo_api.models.listings import CanonicalListing
from tsubo_api.models.sources import Source
from tsubo_api.services.fx import FXService


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "item"


def _coords_from_geom(geom: object | None) -> dict[str, float] | None:
    if geom is None:
        return None
    try:
        point = to_shape(geom)
        return {"lat": float(point.y), "lng": float(point.x)}
    except Exception:
        return None


async def listing_to_summary(
    listing: CanonicalListing,
    session: AsyncSession,
    fx_service: FXService,
) -> dict[str, Any]:
    prefecture_name = "Unknown"
    prefecture_slug = "unknown"
    municipality_name = None
    municipality_slug = None
    if listing.administrative_entity_id:
        entity = await session.get(AdministrativeEntity, listing.administrative_entity_id)
        if entity:
            municipality_name = entity.canonical_name
            municipality_slug = entity.slug
            if entity.parent_id:
                parent = await session.get(AdministrativeEntity, entity.parent_id)
                if parent:
                    prefecture_name = parent.canonical_name_en or parent.canonical_name
                    prefecture_slug = parent.slug or slugify(prefecture_name)

    source = await session.get(Source, listing.source_id)
    source_name = source.name_en or source.name if source else "Unknown"
    source_slug = source.slug if source else "unknown"

    usd_amount = None
    if listing.price_jpy is not None:
        usd, fx = await fx_service.convert_jpy_to_usd(session, listing.price_jpy)
        usd_amount = int(usd) if usd is not None else None

    return {
        "id": str(listing.id),
        "slug": listing.slug or str(listing.id),
        "title": listing.title_en or listing.title_ja or "Untitled listing",
        "title_ja": listing.title_ja,
        "status": str(listing.status),
        "transaction_type": str(listing.transaction_type),
        "property_type": str(listing.property_type),
        "condition": str(listing.condition_category),
        "price": {
            "amount_jpy": int(listing.price_jpy) if listing.price_jpy is not None else None,
            "amount_usd": usd_amount,
            "price_kind": str(listing.price_kind),
            "display_label": _price_label(listing.price_kind, listing.price_jpy, usd_amount),
        },
        "prefecture_slug": prefecture_slug,
        "prefecture_name": prefecture_name,
        "municipality_slug": municipality_slug,
        "municipality_name": municipality_name,
        "location_precision": str(listing.location_precision),
        "coordinates": _coords_from_geom(listing.geom),
        "floor_area_sqm": float(listing.area_sqm) if listing.area_sqm is not None else None,
        "land_area_sqm": float(listing.land_area_sqm) if listing.land_area_sqm is not None else None,
        "built_year": listing.layout.get("year_built") if listing.layout else None,
        "source_slug": source_slug,
        "source_name": source_name,
        "published_at": listing.published_at.isoformat() if listing.published_at else None,
        "updated_at": listing.updated_at.isoformat(),
    }


async def listing_to_detail(
    listing: CanonicalListing,
    session: AsyncSession,
    fx_service: FXService,
) -> dict[str, Any]:
    summary = await listing_to_summary(listing, session, fx_service)
    coverage_state = "SOURCE_MISSING"
    if listing.administrative_entity_id:
        from sqlalchemy import select

        stmt = (
            select(CoverageAssessment)
            .where(CoverageAssessment.administrative_entity_id == listing.administrative_entity_id)
            .order_by(CoverageAssessment.assessment_date.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        assessment = result.scalar_one_or_none()
        if assessment:
            coverage_state = str(assessment.coverage_state)

    source = await session.get(Source, listing.source_id)
    return {
        **summary,
        "description": listing.description_en,
        "description_ja": listing.description_ja,
        "address_display": listing.address_en or listing.address_ja,
        "address_ja": listing.address_ja,
        "images": [],
        "amenities": [],
        "source_url": source.base_url if source else None,
        "coverage_state": coverage_state,
    }


def _price_label(price_kind: Any, jpy: Decimal | None, usd: int | None) -> str | None:
    kind = str(price_kind)
    if kind in {"NEGOTIABLE", "UNDISCLOSED", "UNKNOWN"}:
        return kind.replace("_", " ").title()
    if kind in {"ZERO_PRICE", "FREE_TRANSFER"}:
        return "Free transfer" if kind == "FREE_TRANSFER" else "Zero price"
    if jpy is not None:
        return f"¥{int(jpy):,}"
    if usd is not None:
        return f"${usd:,}"
    return None


def fx_rate_to_response(row: Any) -> dict[str, Any]:
    return {
        "base_currency": row.base_currency,
        "quote_currency": row.quote_currency,
        "rate": float(row.rate),
        "effective_date": row.effective_date.isoformat() if row.effective_date else None,
        "provider": row.provider,
        "is_stale": bool(row.stale),
        "fetched_at": row.fetched_at.isoformat(),
    }
