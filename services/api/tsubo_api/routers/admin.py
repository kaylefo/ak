from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tsubo_contracts.enums import EntityType

from tsubo_api import __version__
from tsubo_api.config import Settings
from tsubo_api.dependencies import get_session, get_settings_dep
from tsubo_api.errors import NotFoundError
from tsubo_api.models.administrative import AdministrativeEntity, CoverageAssessment
from tsubo_api.models.listings import CanonicalListing, CrawlRun
from tsubo_api.models.sources import Source, SourceJurisdiction
from tsubo_api.models.users import User
from tsubo_api.schemas.common import AdminStatsResponse
from tsubo_api.serializers import slugify

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def admin_stats(session: AsyncSession = Depends(get_session)) -> AdminStatsResponse:
    listings = (await session.execute(select(func.count()).select_from(CanonicalListing))).scalar_one()
    sources = (await session.execute(select(func.count()).select_from(Source))).scalar_one()
    jurisdictions = (
        await session.execute(select(func.count()).select_from(SourceJurisdiction))
    ).scalar_one()
    users = (await session.execute(select(func.count()).select_from(User))).scalar_one()

    return AdminStatsResponse(
        listings=listings,
        sources=sources,
        jurisdictions=jurisdictions,
        users=users,
    )


@router.get("/config")
async def admin_config(settings: Settings = Depends(get_settings_dep)) -> dict[str, str]:
    return {
        "app_env": settings.app_env,
        "public_app_name": settings.public_app_name,
        "opensearch_index_listings": settings.opensearch_index_listings,
    }


@router.get("/system/health")
async def system_health(session: AsyncSession = Depends(get_session)) -> dict:
    last_crawl = (
        await session.execute(select(CrawlRun.started_at).order_by(CrawlRun.started_at.desc()).limit(1))
    ).scalar_one_or_none()
    return {
        "api_status": "healthy",
        "worker_status": "degraded",
        "opensearch_status": "degraded",
        "last_ingest_at": last_crawl.isoformat() if last_crawl else None,
        "version": __version__,
    }


prefecture_router = APIRouter(prefix="/prefectures", tags=["prefectures"])
municipality_router = APIRouter(prefix="/municipalities", tags=["municipalities"])


@prefecture_router.get("/{slug}")
async def get_prefecture(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(AdministrativeEntity).where(
        AdministrativeEntity.slug == slug,
        AdministrativeEntity.entity_type == EntityType.PREFECTURE,
    )
    entity = (await session.execute(stmt)).scalar_one_or_none()
    if entity is None:
        raise NotFoundError(f"Prefecture {slug} not found")

    listing_count = (
        await session.execute(
            select(func.count()).select_from(CanonicalListing).where(
                CanonicalListing.administrative_entity_id == entity.id
            )
        )
    ).scalar_one()
    municipality_count = (
        await session.execute(
            select(func.count()).select_from(AdministrativeEntity).where(
                AdministrativeEntity.parent_id == entity.id
            )
        )
    ).scalar_one()
    assessment = (
        await session.execute(
            select(CoverageAssessment)
            .where(CoverageAssessment.administrative_entity_id == entity.id)
            .order_by(CoverageAssessment.assessment_date.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    return {
        "slug": entity.slug,
        "name": entity.canonical_name_en or entity.canonical_name,
        "name_ja": entity.canonical_name,
        "region": (entity.metadata_ or {}).get("region", "Japan"),
        "listing_count": listing_count,
        "municipality_count": municipality_count,
        "coverage_state": str(assessment.coverage_state) if assessment else "SOURCE_MISSING",
        "coordinates": {"lat": 36.0, "lng": 138.0},
    }


@municipality_router.get("/{slug}")
async def get_municipality(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(AdministrativeEntity).where(
        AdministrativeEntity.slug == slug,
        AdministrativeEntity.entity_type == EntityType.MUNICIPALITY,
    )
    entity = (await session.execute(stmt)).scalar_one_or_none()
    if entity is None:
        raise NotFoundError(f"Municipality {slug} not found")

    parent = await session.get(AdministrativeEntity, entity.parent_id) if entity.parent_id else None
    listing_count = (
        await session.execute(
            select(func.count()).select_from(CanonicalListing).where(
                CanonicalListing.administrative_entity_id == entity.id
            )
        )
    ).scalar_one()
    assessment = (
        await session.execute(
            select(CoverageAssessment)
            .where(CoverageAssessment.administrative_entity_id == entity.id)
            .order_by(CoverageAssessment.assessment_date.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    return {
        "slug": entity.slug,
        "name": entity.canonical_name_en or entity.canonical_name,
        "name_ja": entity.canonical_name,
        "prefecture_slug": parent.slug if parent else None,
        "prefecture_name": parent.canonical_name_en or parent.canonical_name if parent else None,
        "listing_count": listing_count,
        "coverage_state": str(assessment.coverage_state) if assessment else "SOURCE_MISSING",
        "coordinates": None,
    }
