from __future__ import annotations

from typing import Any

from temporalio import activity
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.config import get_settings
from tsubo_api.database import get_session_factory
from tsubo_api.services.fx import FXService


@activity.defn(name="refresh_fx_rates")
async def refresh_fx_rates_activity(provider_chain: str | None = None) -> dict[str, Any]:
    activity.logger.info("refresh_fx_rates_activity_started")
    settings = get_settings()
    fx_service = FXService(settings)
    async with get_session_factory()() as session:
        result = await fx_service.refresh_rates(session)
        await session.commit()
    activity.logger.info("refresh_fx_rates_activity_finished", provider=result.get("provider"))
    return result
