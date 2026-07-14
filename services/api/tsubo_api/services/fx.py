from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import httpx
import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from tsubo_api.config import Settings
from tsubo_api.errors import FXRateUnavailableError, ValidationError
from tsubo_api.models.fx import FXProviderHealth, FXRate

logger = structlog.get_logger(__name__)

CANONICAL_CURRENCY = "JPY"
DEFAULT_QUOTE = "USD"
MONEY_QUANTIZE = Decimal("1")
RATE_QUANTIZE = Decimal("0.000000000001")
USD_DISPLAY_QUANTIZE = Decimal("1")


class FXService:
    PROVIDER_FAWAZ_PRIMARY = "fawaz_primary"
    PROVIDER_FAWAZ_FALLBACK = "fawaz_fallback"
    PROVIDER_FRANKFURTER = "frankfurter"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @staticmethod
    def _normalize_currency(currency: str) -> str:
        normalized = currency.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValidationError(f"Invalid currency code: {currency}")
        return normalized

    async def get_current_rate(
        self,
        session: AsyncSession,
        *,
        base: str = CANONICAL_CURRENCY,
        quote: str = DEFAULT_QUOTE,
        force_refresh: bool = False,
    ) -> FXRate:
        base = self._normalize_currency(base)
        quote = self._normalize_currency(quote)
        if base != CANONICAL_CURRENCY:
            raise ValidationError("Canonical base currency must be JPY")

        if not force_refresh:
            stored = await self._get_selected_rate(session, base, quote)
            if stored is not None and not self._is_expired(stored):
                return stored

        try:
            return await self._refresh_rate(session, base, quote)
        except FXRateUnavailableError:
            stale = await self._get_selected_rate(session, base, quote, allow_stale=True)
            if stale is not None:
                stale.stale = True
                await session.flush()
                return stale
            raise

    async def convert_jpy_to_usd(
        self,
        session: AsyncSession,
        amount_jpy: Decimal | int | None,
        *,
        force_refresh: bool = False,
    ) -> tuple[Decimal | None, FXRate]:
        observation = await self.get_current_rate(
            session,
            base=CANONICAL_CURRENCY,
            quote=DEFAULT_QUOTE,
            force_refresh=force_refresh,
        )
        if amount_jpy is None:
            return None, observation
        if not isinstance(amount_jpy, Decimal):
            amount_jpy = Decimal(str(amount_jpy))
        usd = (amount_jpy * observation.rate).quantize(
            USD_DISPLAY_QUANTIZE,
            rounding=ROUND_HALF_UP,
        )
        return usd, observation

    async def convert_usd_bounds_to_jpy(
        self,
        session: AsyncSession,
        min_usd: Decimal | None,
        max_usd: Decimal | None,
    ) -> tuple[Decimal | None, Decimal | None, FXRate]:
        observation = await self.get_current_rate(session)
        if observation.rate <= 0:
            raise FXRateUnavailableError("Invalid FX rate for conversion")
        min_jpy = None
        max_jpy = None
        if min_usd is not None:
            min_jpy = (min_usd / observation.rate).quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)
        if max_usd is not None:
            max_jpy = (max_usd / observation.rate).quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)
        return min_jpy, max_jpy, observation

    def _is_expired(self, row: FXRate) -> bool:
        age = (datetime.now(timezone.utc) - row.fetched_at).total_seconds()
        return age > self.settings.fx_cache_ttl_seconds

    async def _get_selected_rate(
        self,
        session: AsyncSession,
        base: str,
        quote: str,
        *,
        allow_stale: bool = False,
    ) -> FXRate | None:
        stmt = (
            select(FXRate)
            .where(
                FXRate.base_currency == base,
                FXRate.quote_currency == quote,
                FXRate.selected_for_display.is_(True),
            )
            .order_by(FXRate.fetched_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None and allow_stale:
            stmt = (
                select(FXRate)
                .where(FXRate.base_currency == base, FXRate.quote_currency == quote)
                .order_by(FXRate.fetched_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
        return row

    async def _refresh_rate(self, session: AsyncSession, base: str, quote: str) -> FXRate:
        rate, provider, effective_date, payload = await self._fetch_from_providers(quote)
        payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

        existing = await session.execute(
            select(FXRate).where(
                FXRate.base_currency == base,
                FXRate.quote_currency == quote,
                FXRate.effective_date == effective_date,
                FXRate.provider == provider,
            )
        )
        if existing.scalar_one_or_none() is not None:
            return await self.get_current_rate(session, base=base, quote=quote, force_refresh=False)

        await session.execute(
            update(FXRate)
            .where(FXRate.base_currency == base, FXRate.quote_currency == quote)
            .values(selected_for_display=False)
        )

        now = datetime.now(timezone.utc)
        row = FXRate(
            base_currency=base,
            quote_currency=quote,
            rate=rate,
            provider=provider,
            fetched_at=now,
            effective_date=effective_date,
            raw_payload_hash=payload_hash,
            stale=False,
            selected_for_display=True,
            validation_status="valid",
        )
        session.add(row)
        await self._update_provider_health(session, provider, success=True)
        await session.flush()
        return row

    async def _fetch_from_providers(self, quote: str) -> tuple[Decimal, str, date, dict[str, Any]]:
        providers = [
            (self.PROVIDER_FAWAZ_PRIMARY, self._fetch_fawaz_primary),
            (self.PROVIDER_FAWAZ_FALLBACK, self._fetch_fawaz_fallback),
            (self.PROVIDER_FRANKFURTER, self._fetch_frankfurter),
        ]
        errors: list[str] = []
        async with httpx.AsyncClient(timeout=15.0) as client:
            for provider_name, fetcher in providers:
                try:
                    rate, effective_date, payload = await fetcher(client, quote)
                    if rate <= 0:
                        raise ValueError("Rate must be positive")
                    return (
                        rate.quantize(RATE_QUANTIZE, rounding=ROUND_HALF_UP),
                        provider_name,
                        effective_date,
                        payload,
                    )
                except Exception as exc:
                    logger.warning("fx_provider_failed", provider=provider_name, error=str(exc))
                    errors.append(f"{provider_name}: {exc}")
                    await self._update_provider_health_standalone(provider_name, success=False)

        raise FXRateUnavailableError(
            f"Unable to fetch FX rate JPY/{quote}",
            details={"providers": errors},
        )

    async def _fetch_fawaz_primary(
        self, client: httpx.AsyncClient, quote: str
    ) -> tuple[Decimal, date, dict[str, Any]]:
        url = f"{self.settings.fx_fawaz_primary_url}/jpy.min.json"
        response = await client.get(url)
        return self._parse_fawaz_jpy_response(response, quote)

    async def _fetch_fawaz_fallback(
        self, client: httpx.AsyncClient, quote: str
    ) -> tuple[Decimal, date, dict[str, Any]]:
        url = f"{self.settings.fx_fawaz_fallback_url}/jpy.min.json"
        response = await client.get(url)
        return self._parse_fawaz_jpy_response(response, quote)

    def _parse_fawaz_jpy_response(
        self, response: httpx.Response, quote: str
    ) -> tuple[Decimal, date, dict[str, Any]]:
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        if "jpy" not in payload or not isinstance(payload["jpy"], dict):
            raise ValueError("Unexpected Fawaz JPY response shape")
        quote_key = quote.lower()
        rate_value = payload["jpy"].get(quote_key)
        if rate_value is None:
            raise ValueError(f"{quote} missing from Fawaz JPY map")
        effective = payload.get("date")
        if not effective:
            raise ValueError("Effective date missing from Fawaz response")
        return Decimal(str(rate_value)), date.fromisoformat(str(effective)), payload

    async def _fetch_frankfurter(
        self, client: httpx.AsyncClient, quote: str
    ) -> tuple[Decimal, date, dict[str, Any]]:
        url = f"{self.settings.fx_frankfurter_url}/v2/rates"
        response = await client.get(url, params={"base": CANONICAL_CURRENCY, "symbols": quote})
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        rates = payload.get("rates", {})
        rate_value = rates.get(quote)
        if rate_value is None:
            raise ValueError(f"{quote} missing from Frankfurter response")
        effective = payload.get("date")
        if not effective:
            raise ValueError("Effective date missing from Frankfurter response")
        return Decimal(str(rate_value)), date.fromisoformat(str(effective)), payload

    async def _update_provider_health(
        self,
        session: AsyncSession,
        provider: str,
        *,
        success: bool,
    ) -> None:
        now = datetime.now(timezone.utc)
        stmt = select(FXProviderHealth).where(FXProviderHealth.provider == provider)
        result = await session.execute(stmt)
        health = result.scalar_one_or_none()
        if health is None:
            health = FXProviderHealth(provider=provider)
            session.add(health)
        if success:
            health.status = "healthy"
            health.last_success_at = now
            health.consecutive_failures = 0
        else:
            health.status = "degraded"
            health.last_failure_at = now
            health.consecutive_failures += 1

    async def _update_provider_health_standalone(self, provider: str, *, success: bool) -> None:
        pass

    async def list_provider_health(self, session: AsyncSession) -> list[FXProviderHealth]:
        result = await session.execute(select(FXProviderHealth).order_by(FXProviderHealth.provider))
        return list(result.scalars().all())

    async def refresh_rates(self, session: AsyncSession) -> dict[str, Any]:
        row = await self._refresh_rate(session, CANONICAL_CURRENCY, DEFAULT_QUOTE)
        return {
            "provider": row.provider,
            "base": row.base_currency,
            "quote": row.quote_currency,
            "rate": str(row.rate),
            "effective_date": row.effective_date.isoformat() if row.effective_date else None,
            "stale": row.stale,
        }
