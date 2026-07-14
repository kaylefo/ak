"""FX rate refresh delegated to the API provider chain."""

from __future__ import annotations

from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

API_FX_REFRESH_PATH = "/internal/fx/refresh"


async def refresh_rates(api_base_url: str = "http://localhost:8000") -> dict[str, Any]:
    """Trigger FX refresh via the API internal endpoint."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{api_base_url.rstrip('/')}{API_FX_REFRESH_PATH}")
        response.raise_for_status()
        payload = response.json()
        logger.info("fx_refresh_complete", provider=payload.get("provider"))
        return payload
