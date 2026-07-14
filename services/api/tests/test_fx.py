from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
import respx
from httpx import Response

from tsubo_api.config import Settings
from tsubo_api.errors import FXRateUnavailableError, ValidationError
from tsubo_api.services.fx import FXService


@pytest.fixture
def fx_settings() -> Settings:
    return Settings(
        APP_ENV="test",
        FX_CACHE_TTL_SECONDS=3600,
        FX_FRANKFURTER_URL="https://api.frankfurter.dev",
    )


@pytest.fixture
def fx_service(fx_settings: Settings) -> FXService:
    return FXService(fx_settings)


def _mock_session() -> AsyncMock:
    session = AsyncMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None
    session.execute.return_value = execute_result
    return session


@pytest.mark.asyncio
@respx.mock
async def test_convert_jpy_to_usd_requires_rate(fx_service: FXService):
    respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/jpy.min.json"
    ).mock(
        return_value=Response(200, json={"date": "2026-07-14", "jpy": {"usd": 0.0067}})
    )
    session = _mock_session()
    usd, observation = await fx_service.convert_jpy_to_usd(session, Decimal("1000000"))
    assert usd == Decimal("6700")
    assert observation.provider == "fawaz_primary"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_rate_fawaz_primary(fx_service: FXService):
    respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/jpy.min.json"
    ).mock(
        return_value=Response(200, json={"date": "2026-07-14", "jpy": {"usd": 0.0067}})
    )
    session = _mock_session()
    row = await fx_service._refresh_rate(session, "JPY", "USD")
    assert row.rate == Decimal("0.0067")
    assert row.provider == "fawaz_primary"
    assert row.effective_date == date(2026, 7, 14)


@pytest.mark.asyncio
@respx.mock
async def test_fetch_rate_fallback_chain(fx_service: FXService):
    respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/jpy.min.json"
    ).mock(return_value=Response(500))
    respx.get("https://latest.currency-api.pages.dev/v1/currencies/jpy.min.json").mock(
        return_value=Response(200, json={"date": "2026-07-14", "jpy": {"usd": 0.0068}})
    )
    session = _mock_session()
    row = await fx_service._refresh_rate(session, "JPY", "USD")
    assert row.rate == Decimal("0.0068")
    assert row.provider == "fawaz_fallback"


@pytest.mark.asyncio
@respx.mock
async def test_fetch_rate_frankfurter_last_resort(fx_service: FXService, fx_settings: Settings):
    respx.get(url__regex=r".*jpy\.min\.json").mock(return_value=Response(404))
    respx.get(f"{fx_settings.fx_frankfurter_url}/v2/rates").mock(
        return_value=Response(200, json={"base": "JPY", "date": "2026-07-14", "rates": {"USD": 0.0069}})
    )
    session = _mock_session()
    row = await fx_service._refresh_rate(session, "JPY", "USD")
    assert row.rate == Decimal("0.0069")
    assert row.provider == "frankfurter"


@pytest.mark.asyncio
@respx.mock
async def test_all_providers_fail_raises(fx_service: FXService, fx_settings: Settings):
    respx.get(url__regex=r".*jpy\.min\.json").mock(return_value=Response(500))
    respx.get(f"{fx_settings.fx_frankfurter_url}/v2/rates").mock(return_value=Response(500))
    session = _mock_session()
    with pytest.raises(FXRateUnavailableError):
        await fx_service._refresh_rate(session, "JPY", "USD")


def test_invalid_currency_raises(fx_service: FXService):
    with pytest.raises(ValidationError):
        fx_service._normalize_currency("INVALID")


@pytest.mark.asyncio
@respx.mock
async def test_convert_jpy_to_usd_decimal(fx_service: FXService):
    respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/jpy.min.json"
    ).mock(
        return_value=Response(200, json={"date": "2026-07-14", "jpy": {"usd": 0.01}})
    )
    session = _mock_session()
    usd, observation = await fx_service.convert_jpy_to_usd(session, Decimal("1250000"))
    assert usd == Decimal("12500")
    assert observation.provider == "fawaz_primary"
