# Coverage Model

Tsubo tracks **what** is covered per geography, not just **how many** listings exist.

## Entities

Geography follows the `EntityType` hierarchy (country → prefecture → municipality → town, etc.). Coverage is recorded at the finest resolved entity.

## Coverage state

Each `(entity, source_class)` pair has a `CoverageState`:

| State | Meaning |
|-------|---------|
| `DIRECT_ACTIVE` | Source publishes listings for this entity |
| `DIRECT_ZERO_INVENTORY` | Source exists but currently has no listings |
| `DIRECT_REGISTRATION_REQUIRED` | Listings require account/login |
| `PREFECTURAL_ONLY` | Only prefectural portal covers this area |
| `DISCOVERED_UNPARSED` | URL found, parser not yet built |
| `SOURCE_BROKEN` | Parser or source endpoint failing |
| `NOT_APPLICABLE` | No vacant-property program for this entity |

## Source classes

`SourceClass` groups sources (municipal direct, prefectural regional, nationwide akiya bank, etc.) so coverage can be compared within a class.

## Discovery pipeline

`SourceDiscoveryWorkflow` scans for candidate URLs and writes `DISCOVERED_UNPARSED` entries. Successful `CrawlSourceWorkflow` runs promote states based on parser output.

## User-facing rules

- Maps show coverage badges, not just pins.
- Zero-inventory municipalities remain visible (`DIRECT_ZERO_INVENTORY`).
- Gaps are explicit (`SOURCE_MISSING`, `PREFECTURAL_ONLY`) rather than omitted.

See [ADR 003](adrs/003-coverage-ledger.md).
