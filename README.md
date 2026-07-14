# Tsubo

English-first property intelligence platform aggregating official Japanese akiya and public-home-search sources.

## Quick start

```bash
cp .env.example .env
./scripts/bootstrap.sh
docker compose up -d postgres redis opensearch minio mailpit temporal
./scripts/migrate.sh
./scripts/seed.sh
./scripts/verify.sh
```

Run API locally:

```bash
cd services/api
PYTHONPATH=.:../../packages/contracts/python uvicorn tsubo_api.main:app --reload --port 8000
```

Run web locally:

```bash
pnpm install
pnpm --filter @tsubo/web dev
```

## Documentation

- [BUILD_STATUS](docs/BUILD_STATUS.md)
- [Coverage model](docs/COVERAGE_MODEL.md)
- [FX method](docs/FX_METHOD.md)
- [ADRs](docs/adrs/)

## Architecture

Monorepo with:

- `apps/web` — Next.js frontend
- `services/api` — FastAPI REST API
- `services/ingest` — Crawler adapters and normalization
- `services/worker` — Temporal workflows
- `sources/adapters` — Source-specific parsers with offline fixtures
- `packages/contracts` — Shared enums and API types
