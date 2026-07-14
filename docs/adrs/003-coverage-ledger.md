# ADR 003: Coverage Ledger

## Status

Accepted

## Context

Japan's vacant-property ecosystem is fragmented: some municipalities publish direct listings, others delegate to prefectural portals, and many sources require registration or exist only on paper. Users need honest coverage transparency, not implied completeness.

## Decision

Model coverage as a **ledger** keyed by `(entity_type, entity_code, source_class)` with a `CoverageState` enum (see `tsubo_contracts.enums.CoverageState`).

States distinguish:

- **Direct access** — `DIRECT_ACTIVE`, `DIRECT_ZERO_INVENTORY`, `DIRECT_REGISTRATION_REQUIRED`, etc.
- **Delegated access** — `PREFECTURAL_ONLY`, `REGIONAL_ONLY`, `NATIONAL_BANK_ONLY`
- **Discovery pipeline** — `DISCOVERED_UNPARSED`, `SOURCE_BROKEN`, `SOURCE_BLOCKED`
- **Non-applicable** — `NOT_APPLICABLE`, `ADMINISTRATIVE_REFERENCE_ONLY`

`SourceDiscoveryWorkflow` populates candidate sources; parsers promote `DISCOVERED_UNPARSED` → `DIRECT_ACTIVE` after successful crawl.

The ledger is user-visible: maps and filters reflect coverage state rather than hiding gaps.

## Consequences

- Coverage is first-class data, not inferred from listing counts
- Source health (`SourceHealth` enum) is tracked separately from coverage state
- Editorial review uses `UNDER_REVIEW` without blocking ingestion
- Schema migration for full ledger tables is pending (see `BUILD_STATUS.md`)
