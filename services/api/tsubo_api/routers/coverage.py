from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tsubo_contracts.enums import CoverageState, EntityType

from tsubo_api.dependencies import get_session
from tsubo_api.errors import NotFoundError
from tsubo_api.models.administrative import AdministrativeEntity, CoverageAssessment
from tsubo_api.models.listings import CanonicalListing
from tsubo_api.models.sources import Source, SourceJurisdiction
from tsubo_api.schemas.common import CoverageAssessmentResponse, PaginatedResponse

router = APIRouter(prefix="/coverage", tags=["coverage"])


@router.get("/summary")
async def coverage_summary(session: AsyncSession = Depends(get_session)) -> dict:
    listings = (await session.execute(select(func.count()).select_from(CanonicalListing))).scalar_one()
    sources = (await session.execute(select(func.count()).select_from(Source))).scalar_one()
    prefectures = (
        await session.execute(
            select(func.count()).select_from(AdministrativeEntity).where(
                AdministrativeEntity.entity_type == EntityType.PREFECTURE
            )
        )
    ).scalar_one()
    municipalities = (
        await session.execute(
            select(func.count()).select_from(AdministrativeEntity).where(
                AdministrativeEntity.entity_type == EntityType.MUNICIPALITY
            )
        )
    ).scalar_one()
    direct_active = (
        await session.execute(
            select(func.count()).select_from(CoverageAssessment).where(
                CoverageAssessment.coverage_state == CoverageState.DIRECT_ACTIVE
            )
        )
    ).scalar_one()

    by_state: dict[str, int] = {}
    state_rows = await session.execute(
        select(CoverageAssessment.coverage_state, func.count())
        .group_by(CoverageAssessment.coverage_state)
    )
    for state, count in state_rows.all():
        by_state[str(state)] = count

    return {
        "total_listings": listings,
        "total_sources": sources,
        "prefectures_covered": prefectures,
        "municipalities_covered": municipalities,
        "direct_active_count": direct_active,
        "last_updated_at": datetime.now(timezone.utc).isoformat(),
        "by_state": by_state,
    }


@router.get("/regions")
async def coverage_regions(session: AsyncSession = Depends(get_session)) -> list[dict]:
    stmt = (
        select(AdministrativeEntity)
        .where(AdministrativeEntity.entity_type == EntityType.PREFECTURE)
        .order_by(AdministrativeEntity.canonical_name)
    )
    result = await session.execute(stmt)
    regions: list[dict] = []
    for entity in result.scalars().all():
        assessment_stmt = (
            select(CoverageAssessment)
            .where(CoverageAssessment.administrative_entity_id == entity.id)
            .order_by(CoverageAssessment.assessment_date.desc())
            .limit(1)
        )
        assessment = (await session.execute(assessment_stmt)).scalar_one_or_none()
        listing_count = (
            await session.execute(
                select(func.count()).select_from(CanonicalListing).where(
                    CanonicalListing.administrative_entity_id == entity.id
                )
            )
        ).scalar_one()
        source_count = (
            await session.execute(
                select(func.count()).select_from(SourceJurisdiction).where(
                    SourceJurisdiction.administrative_entity_id == entity.id
                )
            )
        ).scalar_one()
        child_count = (
            await session.execute(
                select(func.count()).select_from(AdministrativeEntity).where(
                    AdministrativeEntity.parent_id == entity.id
                )
            )
        ).scalar_one()
        regions.append(
            {
                "slug": entity.slug or entity.code,
                "name": entity.canonical_name_en or entity.canonical_name,
                "name_ja": entity.canonical_name,
                "entity_type": str(entity.entity_type),
                "coverage_state": str(assessment.coverage_state) if assessment else CoverageState.SOURCE_MISSING,
                "listing_count": listing_count,
                "source_count": source_count,
                "child_count": child_count,
            }
        )
    return regions


@router.get("/assessments", response_model=PaginatedResponse)
async def list_coverage_assessments(
    administrative_entity_id: str | None = Query(None),
    coverage_state: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse:
    stmt = select(CoverageAssessment)
    if administrative_entity_id:
        stmt = stmt.where(CoverageAssessment.administrative_entity_id == administrative_entity_id)
    if coverage_state:
        stmt = stmt.where(CoverageAssessment.coverage_state == coverage_state)

    offset = (page - 1) * page_size
    stmt = (
        stmt.order_by(CoverageAssessment.assessment_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    items = [CoverageAssessmentResponse.model_validate(row) for row in result.scalars().all()]

    return PaginatedResponse(items=items, total=len(items), page=page, page_size=page_size)


@router.get("/assessments/{assessment_id}", response_model=CoverageAssessmentResponse)
async def get_coverage_assessment(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
) -> CoverageAssessmentResponse:
    from uuid import UUID

    stmt = select(CoverageAssessment).where(CoverageAssessment.id == UUID(assessment_id))
    result = await session.execute(stmt)
    assessment = result.scalar_one_or_none()
    if assessment is None:
        raise NotFoundError(f"Coverage assessment {assessment_id} not found")
    return CoverageAssessmentResponse.model_validate(assessment)
