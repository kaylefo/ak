from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.dependencies import get_fx_service, get_session
from tsubo_api.schemas.common import FXProviderHealthResponse
from tsubo_api.serializers import fx_rate_to_response
from tsubo_api.services.fx import FXService

router = APIRouter(prefix="/fx", tags=["fx"])


@router.get("/current")
async def get_current_fx(
    base: str = Query("JPY"),
    quote: str = Query("USD"),
    force_refresh: bool = Query(False),
    session: AsyncSession = Depends(get_session),
    fx_service: FXService = Depends(get_fx_service),
) -> dict:
    row = await fx_service.get_current_rate(
        session,
        base=base,
        quote=quote,
        force_refresh=force_refresh,
    )
    await session.commit()
    return fx_rate_to_response(row)


@router.get("/providers/health", response_model=list[FXProviderHealthResponse])
async def list_fx_provider_health(
    session: AsyncSession = Depends(get_session),
    fx_service: FXService = Depends(get_fx_service),
) -> list[FXProviderHealthResponse]:
    rows = await fx_service.list_provider_health(session)
    return [FXProviderHealthResponse.model_validate(row) for row in rows]
