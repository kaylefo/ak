from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.dependencies import get_session
from tsubo_api.errors import NotFoundError
from tsubo_api.models.administrative import AdministrativeEntity
from tsubo_api.models.sources import SourceJurisdiction
from tsubo_api.schemas.common import (
    AdministrativeEntityResponse,
    PaginatedResponse,
    SourceJurisdictionResponse,
)

router = APIRouter(prefix="/jurisdictions", tags=["jurisdictions"])


@router.get("/entities", response_model=PaginatedResponse)
async def list_administrative_entities(
    entity_type: str | None = Query(None),
    parent_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse:
    stmt = select(AdministrativeEntity)
    if entity_type:
        stmt = stmt.where(AdministrativeEntity.entity_type == entity_type)
    if parent_id:
        stmt = stmt.where(AdministrativeEntity.parent_id == parent_id)

    offset = (page - 1) * page_size
    stmt = stmt.order_by(AdministrativeEntity.canonical_name).offset(offset).limit(page_size)
    result = await session.execute(stmt)
    items = [AdministrativeEntityResponse.model_validate(row) for row in result.scalars().all()]

    return PaginatedResponse(items=items, total=len(items), page=page, page_size=page_size)


@router.get("/entities/{entity_id}", response_model=AdministrativeEntityResponse)
async def get_administrative_entity(
    entity_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> AdministrativeEntityResponse:
    stmt = select(AdministrativeEntity).where(AdministrativeEntity.id == entity_id)
    result = await session.execute(stmt)
    entity = result.scalar_one_or_none()
    if entity is None:
        raise NotFoundError(f"Administrative entity {entity_id} not found")
    return AdministrativeEntityResponse.model_validate(entity)


@router.get("/source-jurisdictions", response_model=PaginatedResponse)
async def list_source_jurisdictions(
    source_id: UUID | None = Query(None),
    administrative_entity_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse:
    stmt = select(SourceJurisdiction)
    if source_id:
        stmt = stmt.where(SourceJurisdiction.source_id == source_id)
    if administrative_entity_id:
        stmt = stmt.where(
            SourceJurisdiction.administrative_entity_id == administrative_entity_id
        )

    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    result = await session.execute(stmt)
    items = [SourceJurisdictionResponse.model_validate(row) for row in result.scalars().all()]

    return PaginatedResponse(items=items, total=len(items), page=page, page_size=page_size)
