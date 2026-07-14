# Tsubo Build Status

Checklist of platform components. Items are marked done only when implementation and tests exist in this repository.

## Infrastructure

- [x] Docker Compose stack (Postgres/PostGIS, Redis, OpenSearch, MinIO, Temporal, Mailpit, API, worker, web)
- [x] Postgres extensions bootstrap (`postgis`, `pg_trgm`, `uuid-ossp`)
- [x] Terraform AWS reference skeleton
- [x] GitHub Actions CI (lint, test, Docker build)
- [ ] Production AWS deployment verified in live account
- [ ] Staging environment

## Data Layer

- [x] Alembic migrations (`001_initial_schema`, `002_slugs_and_fx_fields`)
- [x] Core schema: administrative entities, sources, coverage, listings, FX, provenance, users
- [x] Municipality import from geolonia address CSV (1894 codes → 1941 entities incl. wards)
- [x] Explicit `SOURCE_MISSING` coverage state per imported jurisdiction
- [x] Source registry seed (`sources/registry/seed_sources.yaml`)
- [ ] Historical administrative entity versions
- [ ] Address Base Registry geocoder integration

## Ingestion

- [x] SourceAdapter protocol and crawl context
- [x] SSRF-protected HTTP client with conditional requests
- [x] Hybrid immutable snapshot storage (S3/MinIO or local content-addressed files)
- [x] End-to-end ingestion pipeline (fetch → snapshot → parse → canonical listing)
- [x] MLIT discovery and municipal-link adapters (fixture + live HTML)
- [x] LIFULL discovery and listing adapters (fixture + live homes.co.jp HTML)
- [x] At Home discovery and listing adapters (fixture-tested)
- [x] Generic HTML, table, JSON-LD adapters
- [x] No-inventory page classifier
- [x] Bot-challenge / AWS WAF interstitial detection
- [x] Japanese normalization (money, area, dates, layout, address, status)
- [x] Adapter contract tests (31 ingest tests, offline)
- [x] Live LIFULL Aomori crawl verified: 30 listings, 30 with JPY prices, 0 bot-blocked titles
- [ ] Parser drift detection and quarantine publication
- [ ] PDF and spreadsheet inventory adapters
- [ ] Representative municipal direct-source adapters (all regions)

## API

- [x] FastAPI application with OpenAPI
- [x] Listings (PostgreSQL-backed), search, jurisdictions, sources, coverage, FX, admin routes
- [x] `/api/v1/fx/current` with JPY base and USD quote
- [x] USD filter conversion server-side
- [x] Request ID middleware and structured errors
- [x] OpenSearch indexing module (`tsubo_api/search/indexing.py`)
- [x] API unit tests (21 tests)
- [ ] Authentication and user mutation endpoints
- [ ] Saved searches, favorites, alerts, buyer packets
- [ ] OpenSearch index verified against live cluster (requires Docker/OpenSearch)

## FX

- [x] Fawaz jsDelivr primary (`jpy.min.json`)
- [x] Fawaz Cloudflare fallback
- [x] Frankfurter v2 fallback
- [x] Decimal arithmetic, no hardcoded rates
- [x] Effective date, provider, stale flag in storage model
- [x] FX fallback integration tests (5 tests)
- [ ] Redis cache layer for current observation
- [ ] Cross-provider deviation alerting

## Translation

- [x] Deterministic glossary translation service (`GlossaryTranslationService`)
- [x] Glossary seed (`data/glossary/terms.json`)
- [ ] External translation provider integration
- [ ] Translation review admin UI

## Frontend

- [x] Next.js 15 App Router with required public routes
- [x] Admin routes (coverage, sources, FX, system)
- [x] Currency switcher and FX disclosure component
- [x] Search, listing detail, coverage, sources pages
- [x] MapLibre coverage map placeholder
- [x] Shared `@tsubo/contracts` and `@tsubo/ui` packages
- [x] Vitest unit tests; production build passes
- [ ] Playwright E2E suite against live API
- [ ] Full filter URL state and map clustering wired to API
- [ ] WCAG 2.2 AA automated axe gate in CI

## Worker

- [x] Temporal worker entry point
- [x] FXRefreshWorkflow
- [x] CrawlSourceWorkflow (stub activity)
- [x] SourceDiscoveryWorkflow (stub activity)
- [x] IndexListingWorkflow with `reindex_all` / `index_listing_batch`
- [ ] Scheduled cron workflows in Temporal
- [ ] Worker verified against live Temporal cluster

## Operations

- [x] `scripts/bootstrap.sh`, `migrate.sh`, `seed.sh`, `verify.sh`
- [x] `scripts/crawl.sh`, `scripts/reindex.sh`, `scripts/download_municipalities.sh`
- [x] `services/api/scripts/reindex.py` (direct reindex without Temporal)
- [ ] Backup/restore runbook executed in clean environment
- [ ] Observability dashboards

## Documentation

- [x] ADR 001 — Monorepo stack
- [x] ADR 002 — FX provider chain
- [x] ADR 003 — Coverage ledger
- [x] `FX_METHOD.md`, `COVERAGE_MODEL.md`
- [ ] `DATA_DICTIONARY.md`, `SCRAPER_AUTHORING.md`, `DISASTER_RECOVERY.md`
- [ ] Operator runbook

## Known Gaps (honest)

- Docker daemon unavailable in this CI sandbox; OpenSearch/Temporal/MinIO not verified live here.
- At Home live crawl returns 403 from this environment (adapter fixtures pass offline).
- LIFULL detail pages intermittently return AWS WAF 202 challenges; index-card ingestion is primary path.
- Optional enrichments (MLIT ReinfoLib, external translation provider) disabled without credentials.
- User features (auth, alerts, packets) are schema-ready but not yet exposed in API/UI.

## Verified Commands (local Postgres)

```bash
export DATABASE_URL_SYNC=postgresql://tsubo:tsubo@localhost:5432/tsubo
./scripts/download_municipalities.sh
./scripts/seed.sh
./scripts/crawl.sh lifull_aomori_listings true
cd services/ingest && PYTHONPATH=../../services/api:../../packages/contracts/python:../../sources:. python3 -m pytest tests/ -q
```

Last verified crawl: 30 canonical listings, 30 with `price_jpy`, 0 `JavaScript is disabled` titles.
