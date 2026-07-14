# ADR 001: Monorepo Stack

## Status

Accepted

## Context

Tsubo aggregates vacant-property listings across Japan from heterogeneous municipal and regional sources. The platform needs a consistent developer experience, shared contracts, and independently deployable services.

## Decision

Use a **pnpm + Turborepo** monorepo with:

| Layer | Technology |
|-------|------------|
| Web | Next.js (`apps/web`) |
| API | FastAPI + SQLAlchemy + Alembic |
| Worker | Temporal Python SDK |
| Ingest | Python parsers and crawlers |
| Contracts | Shared Python enums + TypeScript types |
| Data | PostgreSQL/PostGIS, Redis, OpenSearch, MinIO |
| Orchestration | Temporal |
| Local dev | Docker Compose |

Services communicate via:

- **Synchronous**: REST internal endpoints (e.g. FX refresh)
- **Asynchronous**: Temporal workflows on the `tsubo-worker` task queue
- **Shared types**: `packages/contracts`

## Consequences

- Single repo for cross-cutting changes (schema + API + worker)
- Turbo caches build/lint/test across packages
- Python services share `PYTHONPATH` conventions in Docker
- Web and API can evolve independently behind contract packages
