#!/usr/bin/env python3
"""Seed geography, sources, coverage ledger, and sample listings from fixtures."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime
from pathlib import Path

import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from tsubo_contracts.enums import (
    AccessMode,
    ConditionCategory,
    CoverageState,
    EntityType,
    ListingStatus,
    LocationPrecision,
    PriceKind,
    PropertyType,
    SourceClass,
    SourceHealth,
    TransactionType,
)

from tsubo_api.models.administrative import AdministrativeEntity, CoverageAssessment
from tsubo_api.models.listings import CanonicalListing, CrawlRun, RawSnapshot, SourceListingRecord
from tsubo_api.models.sources import Source, SourceJurisdiction
from tsubo_api.serializers import slugify

ROOT = Path(__file__).resolve().parents[3]


def _load_prefectures() -> list[dict]:
    data = json.loads((ROOT / "data/seed/prefectures.json").read_text())
    return data["prefectures"]


def _load_registry_sources() -> list[dict]:
    registry = yaml.safe_load((ROOT / "sources/registry/seed_sources.yaml").read_text())
    return registry.get("sources", [])


def seed(session: Session) -> None:
    prefecture_ids: dict[str, uuid.UUID] = {}
    for pref in _load_prefectures():
        slug = slugify(pref["name_en"])
        entity_id = uuid.uuid4()
        existing = session.execute(
            select(AdministrativeEntity).where(AdministrativeEntity.code == pref["code"])
        ).scalar_one_or_none()
        if existing:
            entity_id = existing.id
            existing.slug = slug
            existing.canonical_name = pref["name_ja"]
            existing.canonical_name_en = pref["name_en"]
        else:
            session.add(
                AdministrativeEntity(
                    id=entity_id,
                    entity_type=EntityType.PREFECTURE,
                    code=pref["code"],
                    slug=slug,
                    canonical_name=pref["name_ja"],
                    canonical_name_en=pref["name_en"],
                    metadata_={"region": pref.get("region")},
                )
            )
            session.add(
                CoverageAssessment(
                    administrative_entity_id=entity_id,
                    coverage_state=CoverageState.SOURCE_MISSING,
                    assessment_date=date.today(),
                    notes="Prefecture registered; municipal sources not yet verified.",
                    assessed_by="seed",
                )
            )
        prefecture_ids[pref["code"]] = entity_id

    municipality_samples = [
        ("13101", "Chiyoda", "千代田区", "13"),
        ("02201", "Aomori City", "青森市", "02"),
        ("01694", "Rishiri", "利尻町", "01"),
    ]
    municipality_ids: dict[str, uuid.UUID] = {}
    for code, name_en, name_ja, pref_code in municipality_samples:
        parent_id = prefecture_ids.get(pref_code)
        slug = slugify(name_en)
        existing = session.execute(
            select(AdministrativeEntity).where(AdministrativeEntity.code == code)
        ).scalar_one_or_none()
        if existing:
            municipality_ids[code] = existing.id
            continue
        entity_id = uuid.uuid4()
        session.add(
            AdministrativeEntity(
                id=entity_id,
                entity_type=EntityType.MUNICIPALITY,
                parent_id=parent_id,
                code=code,
                slug=slug,
                canonical_name=name_ja,
                canonical_name_en=name_en,
            )
        )
        session.add(
            CoverageAssessment(
                administrative_entity_id=entity_id,
                coverage_state=CoverageState.UNDER_REVIEW,
                assessment_date=date.today(),
                assessed_by="seed",
            )
        )
        municipality_ids[code] = entity_id

    source_ids: dict[str, uuid.UUID] = {}
    for entry in _load_registry_sources():
        key = entry["source_id"]
        slug = slugify(key.replace("_", "-"))
        existing = session.execute(select(Source).where(Source.source_key == key)).scalar_one_or_none()
        if existing:
            source_ids[key] = existing.id
            continue
        source_id = uuid.uuid4()
        source_class = SourceClass(entry.get("source_class", "SUPPORTING_DATA"))
        access_mode = AccessMode(entry.get("access_mode", "PUBLIC_HTML"))
        session.add(
            Source(
                id=source_id,
                source_key=key,
                slug=slug,
                source_class=source_class,
                name=entry["name"],
                name_en=entry["name"],
                base_url=entry.get("base_url"),
                access_mode=access_mode,
                health=SourceHealth.UNKNOWN,
                metadata_={
                    "adapter_id": entry.get("adapter_id"),
                    "adapter_version": "1.0.0",
                    "description": entry.get("description"),
                },
            )
        )
        source_ids[key] = source_id
        if entry.get("entity_type") == "prefecture" and entry.get("metadata", {}).get("prefecture") == "東京都":
            pref = session.execute(
                select(AdministrativeEntity).where(AdministrativeEntity.code == "13")
            ).scalar_one_or_none()
            if pref:
                session.add(
                    SourceJurisdiction(
                        source_id=source_id,
                        administrative_entity_id=pref.id,
                        coverage_state=CoverageState(entry.get("coverage_state", "UNDER_REVIEW")),
                    )
                )
        elif entry.get("entity_type") == "country":
            session.add(
                SourceJurisdiction(
                    source_id=source_id,
                    administrative_entity_id=next(iter(prefecture_ids.values())),
                    coverage_state=CoverageState(entry.get("coverage_state", "NATIONAL_BANK_ONLY")),
                    notes="Nationwide source",
                )
            )

    _seed_fixture_listings(session, source_ids, municipality_ids)
    session.commit()


def _seed_fixture_listings(
    session: Session,
    source_ids: dict[str, uuid.UUID],
    municipality_ids: dict[str, uuid.UUID],
) -> None:
    lifull_source = source_ids.get("lifull_tokyo_listings")
    if not lifull_source:
        return

    fixture_path = ROOT / "sources/fixtures/lifull_listing_detail.html"
    if not fixture_path.exists():
        return

    now = datetime.now(UTC)
    crawl = CrawlRun(
        source_id=lifull_source,
        status="completed",
        started_at=now,
        finished_at=now,
        records_found=1,
    )
    session.add(crawl)
    session.flush()

    snapshot = RawSnapshot(
        crawl_run_id=crawl.id,
        source_id=lifull_source,
        s3_key="fixtures/lifull_listing_detail.html",
        content_hash="fixture-lifull-001",
        captured_at=now,
        metadata_={"fixture": True},
    )
    session.add(snapshot)
    session.flush()

    raw_data = {
        "title_ja": "築50年の古民家、海が見える丘の上",
        "price_text": "120万円",
        "address_ja": "青森県青森市",
        "land_area": "330㎡",
        "building_area": "85㎡",
        "layout": "4DK",
        "source_url": "https://www.akiya-v.jp/example/001",
        "source_listing_id": "lifull-fixture-001",
    }
    record = SourceListingRecord(
        source_id=lifull_source,
        raw_snapshot_id=snapshot.id,
        source_listing_id="lifull-fixture-001",
        raw_data=raw_data,
        fetched_at=now,
        content_hash="record-lifull-001",
    )
    session.add(record)
    session.flush()

    municipality_id = municipality_ids.get("02201")
    listing = CanonicalListing(
        slug="aomori-kominka-ocean-view",
        source_listing_record_id=record.id,
        source_id=lifull_source,
        administrative_entity_id=municipality_id,
        status=ListingStatus.ACTIVE,
        transaction_type=TransactionType.SALE,
        property_type=PropertyType.KOMINKA,
        price_jpy=1200000,
        price_kind=PriceKind.FIXED,
        area_sqm=85,
        land_area_sqm=330,
        location_precision=LocationPrecision.MUNICIPALITY,
        condition_category=ConditionCategory.SUBSTANTIAL_REPAIR,
        title_ja=raw_data["title_ja"],
        title_en="50-year-old kominka on a hill with ocean views",
        description_ja="要補修。古民家バンク登録物件。",
        description_en="Substantial repairs indicated. Registered vacant-home bank listing.",
        address_ja=raw_data["address_ja"],
        address_en="Aomori City, Aomori Prefecture",
        layout={"raw": "4DK", "normalized": "4DK"},
        published_at=now,
        last_seen_at=now,
    )
    session.add(listing)

    if municipality_id:
        assessment = session.execute(
            select(CoverageAssessment).where(
                CoverageAssessment.administrative_entity_id == municipality_id
            )
        ).scalar_one_or_none()
        if assessment:
            assessment.coverage_state = CoverageState.NATIONAL_BANK_ONLY
            assessment.notes = "Inventory observed via nationwide akiya bank adapter fixture."


def main() -> None:
    import os

    db_url = os.environ.get("DATABASE_URL_SYNC", "postgresql://tsubo:tsubo@localhost:5432/tsubo")
    engine = create_engine(db_url)
    with Session(engine) as session:
        seed(session)
    print("Seed complete")


if __name__ == "__main__":
    main()
