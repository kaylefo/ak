# ADR 002: FX Provider Chain

## Status

Accepted

## Context

Tsubo displays prices in JPY and converted foreign currencies for international users. External FX APIs are unreliable, rate-limited, or occasionally deprecated.

## Decision

Implement an **ordered provider chain** configured via `FX_PROVIDER_CHAIN` (default: `frankfurter,exchangerate_host,static_fallback`).

1. **Frankfurter** — primary ECB-backed rates (no API key)
2. **ExchangeRate.host** — secondary free aggregator
3. **Static fallback** — last-resort hardcoded rates to keep the UI functional

The chain is executed in `tsubo_api.fx.refresh_fx_rates`. Each provider failure is logged; the next provider is tried. Success short-circuits the chain.

Refresh is triggered by:

- `FXRefreshWorkflow` (Temporal, scheduled or manual)
- `POST /internal/fx/refresh` (API internal endpoint)

Results are persisted in `fx_rates` with provider attribution and timestamp.

## Consequences

- No single point of failure for currency display
- Provider order is environment-configurable without code changes
- Static fallback prevents total outage but may serve stale rates (logged explicitly)
- Additional providers can be registered in `build_provider_chain`
