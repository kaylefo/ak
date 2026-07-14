#!/usr/bin/env python3
"""Import all Japanese municipalities from geolonia address CSV (derived from official LG codes)."""

from __future__ import annotations

import csv
import os
import uuid
from collections import defaultdict
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from tsubo_contracts.enums import CoverageState, EntityType

from tsubo_api.models.administrative import AdministrativeEntity, CoverageAssessment
from tsubo_api.serializers import slugify

ROOT = Path(__file__).resolve().parents[3]
CSV_PATH = ROOT / "data" / "seed" / "municipalities_raw.csv"

REGION_BY_PREF: dict[str, str] = {
    "01": "Hokkaido / Tohoku",
    "02": "Hokkaido / Tohoku",
    "03": "Hokkaido / Tohoku",
    "04": "Hokkaido / Tohoku",
    "05": "Hokkaido / Tohoku",
    "06": "Hokkaido / Tohoku",
    "07": "Hokkaido / Tohoku",
    "08": "Kanto",
    "09": "Kanto",
    "10": "Kanto",
    "11": "Kanto",
    "12": "Kanto",
    "13": "Kanto",
    "14": "Kanto",
    "15": "Chubu / Hokuriku",
    "16": "Chubu / Hokuriku",
    "17": "Chubu / Hokuriku",
    "18": "Chubu / Hokuriku",
    "19": "Chubu / Hokuriku",
    "20": "Chubu / Hokuriku",
    "21": "Chubu / Hokuriku",
    "22": "Chubu / Hokuriku",
    "23": "Chubu / Hokuriku",
    "24": "Kansai",
    "25": "Kansai",
    "26": "Kansai",
    "27": "Kansai",
    "28": "Kansai",
    "29": "Kansai",
    "30": "Kansai",
    "31": "Chugoku",
    "32": "Chugoku",
    "33": "Chugoku",
    "34": "Chugoku",
    "35": "Chugoku",
    "36": "Shikoku",
    "37": "Shikoku",
    "38": "Shikoku",
    "39": "Shikoku",
    "40": "Kyushu / Okinawa",
    "41": "Kyushu / Okinawa",
    "42": "Kyushu / Okinawa",
    "43": "Kyushu / Okinawa",
    "44": "Kyushu / Okinawa",
    "45": "Kyushu / Okinawa",
    "46": "Kyushu / Okinawa",
    "47": "Kyushu / Okinawa",
}


def _entity_type(name: str, code: str, pref_code: str) -> EntityType:
    if pref_code == "13" and name.endswith("区"):
        return EntityType.TOKYO_SPECIAL_WARD
    if name.endswith("区") and len(code) == 5 and code[2:].startswith("1"):
        return EntityType.DESIGNATED_CITY_WARD
    if name.endswith("町"):
        return EntityType.MUNICIPALITY
    if name.endswith("村"):
        return EntityType.MUNICIPALITY
    return EntityType.MUNICIPALITY


def load_municipalities() -> dict[str, dict]:
    municipalities: dict[str, dict] = {}
    with CSV_PATH.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            code = row["市区町村コード"].strip()
            if code in municipalities:
                continue
            pref_code = row["都道府県コード"].strip()
            name_ja = row["市区町村名"].strip()
            name_kana = row.get("市区町村名カナ", "").strip()
            name_romaji = row.get("市区町村名ローマ字", "").strip()
            municipalities[code] = {
                "code": code,
                "pref_code": pref_code,
                "pref_name_ja": row["都道府県名"].strip(),
                "pref_name_en": row["都道府県名ローマ字"].strip(),
                "name_ja": name_ja,
                "name_kana": name_kana,
                "name_romaji": name_romaji,
                "entity_type": _entity_type(name_ja, code, pref_code),
            }
    return municipalities


def import_geography(session: Session) -> dict[str, int]:
    municipalities = load_municipalities()
    pref_ids: dict[str, uuid.UUID] = {}

    # Prefectures from unique pref codes in municipalities
    pref_data: dict[str, dict] = {}
    for muni in municipalities.values():
        pc = muni["pref_code"]
        if pc not in pref_data:
            pref_data[pc] = {
                "code": pc,
                "name_ja": muni["pref_name_ja"],
                "name_en": muni["pref_name_en"],
            }

    for pc, pref in sorted(pref_data.items()):
        slug = slugify(pref["name_en"] or pref["name_ja"])
        existing = session.execute(
            select(AdministrativeEntity).where(
                AdministrativeEntity.code == pc,
                AdministrativeEntity.entity_type == EntityType.PREFECTURE,
            )
        ).scalar_one_or_none()
        if existing:
            pref_ids[pc] = existing.id
            continue
        entity_id = uuid.uuid4()
        session.add(
            AdministrativeEntity(
                id=entity_id,
                entity_type=EntityType.PREFECTURE,
                code=pc,
                slug=slug,
                canonical_name=pref["name_ja"],
                canonical_name_en=pref["name_en"],
                metadata_={"region": REGION_BY_PREF.get(pc, "Japan"), "dataset": "geolonia/latest.csv"},
            )
        )
        session.add(
            CoverageAssessment(
                administrative_entity_id=entity_id,
                coverage_state=CoverageState.SOURCE_MISSING,
                assessment_date=date.today(),
                notes="Prefecture registered from address-base-derived municipality dataset.",
                assessed_by="import_municipalities",
            )
        )
        pref_ids[pc] = entity_id

    muni_count = 0
    for code, muni in sorted(municipalities.items()):
        parent_id = pref_ids.get(muni["pref_code"])
        slug_base = muni["name_romaji"] or muni["name_ja"]
        slug = slugify(f"{muni['pref_name_en']}-{slug_base}")
        existing = session.execute(
            select(AdministrativeEntity).where(AdministrativeEntity.code == code)
        ).scalar_one_or_none()
        if existing:
            muni_count += 1
            continue
        entity_id = uuid.uuid4()
        session.add(
            AdministrativeEntity(
                id=entity_id,
                entity_type=muni["entity_type"],
                parent_id=parent_id,
                code=code,
                slug=slug,
                canonical_name=muni["name_ja"],
                canonical_name_en=muni["name_romaji"].title() if muni["name_romaji"] else None,
                metadata_={
                    "kana": muni["name_kana"],
                    "dataset": "geolonia/latest.csv",
                    "dataset_version": "develop",
                },
            )
        )
        session.add(
            CoverageAssessment(
                administrative_entity_id=entity_id,
                coverage_state=CoverageState.SOURCE_MISSING,
                assessment_date=date.today(),
                assessed_by="import_municipalities",
            )
        )
        muni_count += 1

    return {
        "prefectures": len(pref_data),
        "municipalities": muni_count,
        "unique_codes": len(municipalities),
    }


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing municipality CSV at {CSV_PATH}")

    db_url = os.environ.get("DATABASE_URL_SYNC", "postgresql://tsubo:tsubo@localhost:5432/tsubo")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        counts = import_geography(session)
        session.commit()
    print(f"Imported {counts['prefectures']} prefectures, {counts['unique_codes']} municipality codes")


if __name__ == "__main__":
    main()
