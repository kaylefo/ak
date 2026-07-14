# FX Method

Tsubo converts JPY listing prices to foreign currencies using a provider chain.

## Flow

1. `FXRefreshWorkflow` runs on schedule or via operator trigger.
2. Activity calls `tsubo_api.fx.refresh_fx_rates`.
3. Providers are tried in order until one returns rates.
4. Result is stored in `fx_rates` with `provider`, `base_currency`, `rates`, `refreshed_at`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FX_PROVIDER_CHAIN` | `frankfurter,exchangerate_host,static_fallback` | Comma-separated provider names |

## Base currency

JPY. Target currencies: USD, EUR, GBP, AUD, CAD.

## Failure behavior

- Provider errors are collected and logged.
- Chain continues to the next provider.
- If all fail, activity raises `RuntimeError` and Temporal retries per workflow policy.
- Static fallback ensures degraded service rather than blank prices.

See [ADR 002](adrs/002-fx-provider-chain.md) for rationale.
