from __future__ import annotations

import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scrapling.fetchers import Fetcher

OUT = Path("out/smoke")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "raw" / "leafly").mkdir(parents=True, exist_ok=True)

HEADERS = {
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_gzip(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb", compresslevel=9) as fh:
        fh.write(body)


def main() -> None:
    api_url = (
        "https://consumer-api.leafly.com/api/strain_playlists/v2"
        "?enableNewFilters=false&skip=0&strain_playlist=&take=5"
    )
    api = Fetcher.get(
        api_url,
        headers=HEADERS,
        impersonate="chrome",
        stealthy_headers=True,
        timeout=45,
        retries=3,
    )
    if api.status != 200:
        raise RuntimeError(f"Leafly API returned HTTP {api.status}: {api.reason}")
    payload = api.json()
    strains = payload.get("hits", {}).get("strain", [])
    if not strains:
        raise RuntimeError("Leafly API returned no strain records")

    api_record = {
        "source": "leafly",
        "source_url": api_url,
        "fetched_at": utcnow(),
        "status": api.status,
        "sha256": hashlib.sha256(api.body).hexdigest(),
        "record_count": len(strains),
        "payload": payload,
    }
    (OUT / "leafly_api_sample.json").write_text(
        json.dumps(api_record, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    details: list[dict] = []
    for item in strains[:3]:
        slug = item.get("slug") or item.get("key")
        if not slug:
            continue
        url = f"https://www.leafly.com/strains/{slug}"
        page = Fetcher.get(
            url,
            headers={**HEADERS, "Accept": "text/html,application/xhtml+xml"},
            impersonate="chrome",
            stealthy_headers=True,
            timeout=45,
            retries=3,
        )
        raw_path = OUT / "raw" / "leafly" / f"{slug}.html.gz"
        write_gzip(raw_path, page.body)
        title = page.css("title::text").get()
        h1 = page.css("h1::text").get()
        description = page.css('meta[name="description"]::attr(content)').get()
        canonical = page.css('link[rel="canonical"]::attr(href)').get()
        json_ld = page.css('script[type="application/ld+json"]::text').getall()
        details.append(
            {
                "source": "leafly",
                "slug": slug,
                "url": url,
                "status": page.status,
                "fetched_at": utcnow(),
                "sha256": hashlib.sha256(page.body).hexdigest(),
                "raw_snapshot": str(raw_path),
                "title": title,
                "h1": h1,
                "description": description,
                "canonical_url": canonical,
                "json_ld": json_ld,
                "api_summary": item,
            }
        )

    if not details:
        raise RuntimeError("No Leafly detail pages were fetched")
    with (OUT / "leafly_details_sample.jsonl").open("w", encoding="utf-8") as fh:
        for row in details:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "completed_at": utcnow(),
        "scrapling_verified": True,
        "leafly_api_status": api.status,
        "leafly_api_records": len(strains),
        "leafly_detail_attempts": len(details),
        "leafly_detail_successes": sum(1 for x in details if x["status"] == 200),
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
