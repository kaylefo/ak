from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api import __version__
from tsubo_api.config import Settings
from tsubo_api.dependencies import get_session, get_settings_dep
from tsubo_api.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings_dep),
    session: AsyncSession = Depends(get_session),
) -> HealthResponse:
    status = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        status = "degraded"

    return HealthResponse(
        status=status,
        app=settings.public_app_name,
        version=__version__,
        environment=settings.app_env,
    )


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}
