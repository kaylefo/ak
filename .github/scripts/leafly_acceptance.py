from __future__ import annotations

import gzip
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from scrapling.fetchers import Fetcher

OUT = Path("acceptance-out")
OUT.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
}

DETAIL_SLUGS = ["blue-dream", "lemon-cherry-gelato", "white-widow"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def text(node) -> str | None:
    value = node.get() if node is not None else None
    return value.strip() if isinstance(value, str) and value.strip() else None


def parse_next(page) -> dict:
    raw = page.css("script#__NEXT_DATA__::text").get()
    if not raw:
        raise RuntimeError("__NEXT_DATA__ missing")
    return json.loads(raw)


def strip_html(value: str | None) -> str | None:
    if not value:
        return value
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"</p\s*>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n\s*\n+", "\n", value)
    return value.strip()


def flatten_detail(url: str, page, next_data: dict) -> dict:
    page_props = next_data.get("props", {}).get("pageProps", {})
    strain = page_props.get("strain") or {}
    reviews = page_props.get("reviews") or []
    return {
        "source": "leafly",
        "source_url": url,
        "fetched_at": now(),
        "http_status": page.status,
        "content_sha256": hashlib.sha256(page.body).hexdigest(),
        "identity": {
            "id": strain.get("id"),
            "name": strain.get("name"),
            "slug": strain.get("slug"),
            "symbol": strain.get("symbol"),
            "category": strain.get("category"),
            "phenotype": strain.get("phenotype"),
            "subtitle": strain.get("subtitle"),
        },
        "potency": {
            "cannabinoids": strain.get("cannabinoids") or {},
            "thc_listing_value": (page_props.get("strain") or {}).get("thc"),
        },
        "rating": {
            "average": strain.get("averageRating", strain.get("rating")),
            "review_count": strain.get("reviewCount"),
            "written_review_count": page_props.get("writtenReviewCount"),
            "effect_review_count": strain.get("effectReviewCount"),
            "flavor_review_count": strain.get("flavorReviewCount"),
            "negative_review_count": strain.get("negativeReviewCount"),
            "symptom_review_count": strain.get("symptomReviewCount"),
            "condition_review_count": strain.get("conditionReviewCount"),
            "traits_source_count_total": strain.get("traitsSourceCountTotal"),
            "traits_count_total": strain.get("traitsCountTotal"),
        },
        "profile": {
            "description_html": strain.get("description"),
            "description_text": strain.get("descriptionPlain") or strip_html(strain.get("description")),
            "energize_score": strain.get("energizeScore"),
            "top_effect": strain.get("topEffect"),
            "effects": strain.get("effects") or {},
            "negatives": strain.get("negatives") or {},
            "flavors": strain.get("flavors") or {},
            "terpenes": strain.get("terps") or {},
            "reported_conditions": strain.get("conditions") or {},
            "reported_symptoms": strain.get("symptoms") or {},
        },
        "genetics": {
            "parents": strain.get("parents") or [],
            "children": strain.get("children") or [],
        },
        "cultivation": strain.get("growInfo") or {},
        "media": {
            "nug_image": strain.get("nugImage"),
            "nug_image_alt_text": strain.get("nugImageAltText"),
            "stock_nug_image": strain.get("stockNugImage"),
            "flower_image_png": strain.get("flowerImagePng"),
            "flower_image_svg": strain.get("flowerImageSvg"),
            "nucleus_image_png": strain.get("nucleusImagePng"),
            "nucleus_image_svg": strain.get("nucleusImageSvg"),
            "photo_count": strain.get("photoCount"),
            "highlighted_photos": strain.get("highlightedPhotos") or [],
        },
        "awards": strain.get("award") or {},
        "followers": strain.get("totalFollowers"),
        "reviews": reviews,
        "raw_page_props": page_props,
    }


def listing_cards(page, next_data: dict) -> list[dict]:
    # Preserve DOM order from the actual /strains?page=N page.
    cards: list[dict] = []
    seen: set[str] = set()
    for anchor in page.css('a[href^="/strains/"]'):
        href = anchor.attrib.get("href")
        if not href or href in seen:
            continue
        if href.count("/") != 2:
            continue
        slug = href.rsplit("/", 1)[-1].split("?", 1)[0]
        if not slug or slug in {"lists", "new"}:
            continue
        seen.add(href)
        label = " ".join(x.strip() for x in anchor.css("::text").getall() if x.strip())
        cards.append(
            {
                "position": len(cards) + 1,
                "name_from_card": label or None,
                "slug": slug,
                "url": urljoin("https://www.leafly.com", href),
            }
        )
    return cards


def fetch(url: str):
    return Fetcher.get(
        url,
        headers=HEADERS,
        impersonate="chrome",
        stealthy_headers=True,
        timeout=60,
        retries=4,
        retry_delay=2,
    )


def main() -> None:
    listing_url = "https://www.leafly.com/strains?page=1"
    listing = fetch(listing_url)
    if listing.status != 200:
        raise RuntimeError(f"listing page HTTP {listing.status}")
    listing_next = parse_next(listing)
    cards = listing_cards(listing, listing_next)
    with gzip.open(OUT / "leafly-page-1.html.gz", "wb") as fh:
        fh.write(listing.body)
    (OUT / "leafly-page-1-next-data.json").write_text(
        json.dumps(listing_next, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "leafly-page-1-cards.json").write_text(
        json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    detail_records = []
    for slug in DETAIL_SLUGS:
        url = f"https://www.leafly.com/strains/{slug}"
        page = fetch(url)
        if page.status != 200:
            raise RuntimeError(f"{slug}: HTTP {page.status}")
        next_data = parse_next(page)
        record = flatten_detail(url, page, next_data)
        actual_slug = record["identity"].get("slug")
        if actual_slug != slug:
            raise RuntimeError(f"{slug}: parsed slug {actual_slug!r}")
        with gzip.open(OUT / f"{slug}.html.gz", "wb") as fh:
            fh.write(page.body)
        (OUT / f"{slug}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        detail_records.append(record)

    expected = ["blue-dream", "lemon-cherry-gelato", "white-widow"]
    actual_first = [x["slug"] for x in cards[:3]]
    summary = {
        "crawler": "Scrapling",
        "completed_at": now(),
        "listing_url": listing_url,
        "listing_status": listing.status,
        "listing_cards_found": len(cards),
        "first_three_expected_by_user": expected,
        "first_three_actual": actual_first,
        "first_three_match": actual_first == expected,
        "detail_pages": [
            {
                "slug": r["identity"]["slug"],
                "status": r["http_status"],
                "name": r["identity"]["name"],
                "review_count": r["rating"]["review_count"],
                "reviews_embedded": len(r["reviews"]),
                "parents": len(r["genetics"]["parents"]),
                "children": len(r["genetics"]["children"]),
                "highlighted_photos": len(r["media"]["highlighted_photos"]),
                "grow_fields": sorted(r["cultivation"].keys()),
            }
            for r in detail_records
        ],
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
