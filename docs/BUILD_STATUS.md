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
- [x] Prefecture seed data (47 prefectures)
- [x] Source registry seed (`sources/registry/seed_sources.yaml`)
- [x] Seed script with sample municipality coverage states and fixture-derived listing
- [ ] Full municipality import from MLIT N03 / e-Stat
- [ ] Historical administrative entity versions
- [ ] Address Base Registry geocoder integration

## Ingestion

- [x] SourceAdapter protocol and crawl context
- [x] SSRF-protected HTTP client with conditional requests
- [x] Immutable snapshot storage (S3/MinIO)
- [x] MLIT discovery and municipal-link adapters (fixture-tested)
- [x] LIFULL discovery and listing adapters (fixture-tested)
- [x] At Home discovery and listing adapters (fixture-tested)
- [x] Generic HTML, table, JSON-LD adapters
- [x] No-inventory page classifier
- [x] Japanese normalization (money, area, dates, layout, address, status)
- [x] Adapter contract tests (31 ingest tests, offline)
- [ ] Live end-to-end crawl to canonical listing in running Compose stack
- [ ] Parser drift detection and quarantine publication
- [ ] PDF and spreadsheet inventory adapters
- [ ] Representative municipal direct-source adapters (all regions)

## API

- [x] FastAPI application with OpenAPI
- [x] Listings, search, jurisdictions, sources, coverage, FX, admin routes
- [x] `/api/v1/fx/current` with JPY base and USD quote
- [x] USD filter conversion server-side
- [x] Request ID middleware and structured errors
- [x] API unit tests (21 tests)
- [ ] Authentication and user mutation endpoints
- [ ] Saved searches, favorites, alerts, buyer packets
- [ ] OpenSearch index auto-provisioning and full reindex command verified against live cluster

## FX

- [x] Fawaz jsDelivr primary (`jpy.min.json`)
- [x] Fawaz Cloudflare fallback
- [x] Frankfurter v2 fallback
- [x] Decimal arithmetic, no hardcoded rates
- [x] Effective date, provider, stale flag in storage model
- [x] FX fallback integration tests (5 tests)
- [ ] Redis cache layer for current observation
- [ ] Cross-provider deviation alerting

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
- [x] IndexListingWorkflow (stub activity)
- [ ] Scheduled cron workflows in Temporal
- [ ] Worker verified against live Temporal cluster

## Operations

- [x] `scripts/bootstrap.sh`, `migrate.sh`, `seed.sh`, `verify.sh`
- [x] `scripts/crawl.sh`, `reindex.sh`
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

- Nationwide municipality coverage is **not** complete; prefectures are seeded with explicit `SOURCE_MISSING` / `UNDER_REVIEW` states.
- Live crawling requires Docker Compose and outbound network; not verified in this CI sandbox (no Docker daemon).
- Optional enrichments (MLIT ReinfoLib, translation provider) are interface-ready but disabled without credentials.
- User features (auth, alerts, packets) are schema-ready but not yet exposed in API/UI.
