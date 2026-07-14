#!/usr/bin/env python3
"""Seed sources and coverage registry — no synthetic listings."""

from __future__ import annotations

import json
import os
import uuid
from datetime import date
from pathlib import Path

import yaml
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from tsubo_contracts.enums import AccessMode, CoverageState, EntityType, SourceClass, SourceHealth

from tsubo_api.models.sources import Source, SourceJurisdiction
from tsubo_api.serializers import slugify

ROOT = Path(__file__).resolve().parents[3]


def _load_registry_sources() -> list[dict]:
    registry = yaml.safe_load((ROOT / "sources/registry/seed_sources.yaml").read_text())
    return registry.get("sources", [])


def seed_sources(session: Session) -> int:
    count = 0
    for entry in _load_registry_sources():
        key = entry["source_id"]
        slug = slugify(key.replace("_", "-"))
        existing = session.execute(select(Source).where(Source.source_key == key)).scalar_one_or_none()
        if existing:
            continue
        source_id = uuid.uuid4()
        session.add(
            Source(
                id=source_id,
                source_key=key,
                slug=slug,
                source_class=SourceClass(entry.get("source_class", "SUPPORTING_DATA")),
                name=entry["name"],
                name_en=entry.get("name_en", entry["name"]),
                base_url=entry.get("base_url"),
                access_mode=AccessMode(entry.get("access_mode", "PUBLIC_HTML")),
                health=SourceHealth.UNKNOWN,
                metadata_={
                    "adapter_id": entry.get("adapter_id"),
                    "adapter_version": "1.0.0",
                    "entity_type": entry.get("entity_type", "country"),
                    "index_url": entry.get("index_url"),
                    "allowed_hostnames": entry.get("allowed_hostnames", []),
                    **(entry.get("metadata") or {}),
                },
            )
        )
        count += 1
    return count


def main() -> None:
    db_url = os.environ.get("DATABASE_URL_SYNC", "postgresql://tsubo:tsubo@localhost:5432/tsubo")
    engine = create_engine(db_url)
    with Session(engine) as session:
        n = seed_sources(session)
        session.commit()
    print(f"Seeded {n} sources")


if __name__ == "__main__":
    main()
