from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
import time
import traceback
from dataclasses import replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "terpeezy_crawl"))

from crawl import (
    CRAWLER_VERSION,
    SourceConfig,
    crawl_details,
    discover_leafly_api,
    json_dumps,
    utcnow,
    write_checksums,
    write_source_readme,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--output-root", default="out")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.10)
    return parser.parse_args()


async def run(args: argparse.Namespace) -> int:
    if not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard index")
    root = REPO_ROOT / "terpeezy_crawl"
    registry = json.loads((root / "sources.json").read_text(encoding="utf-8"))
    base_config = SourceConfig.from_dict("leafly", registry["leafly"])
    config = replace(base_config, concurrency=args.concurrency, delay_seconds=args.delay)
    out_dir = Path(args.output_root) / f"leafly-shard-{args.shard_index:02d}-of-{args.shard_count:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_source_readme(config, out_dir)
    (out_dir / "source_config.json").write_text(json_dumps(registry["leafly"], pretty=True), encoding="utf-8")
    started = utcnow()
    clock = time.monotonic()
    manifest = {
        "source_id": "leafly",
        "source_name": "Leafly",
        "crawler": "Scrapling",
        "crawler_version": CRAWLER_VERSION,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "started_at": started,
        "status": "running",
    }
    try:
        all_urls, listing_by_url, discovery_events = await discover_leafly_api(config, out_dir)
        selected = all_urls[args.shard_index :: args.shard_count]
        (out_dir / "all_discovered_count.txt").write_text(str(len(all_urls)) + "\n", encoding="utf-8")
        (out_dir / "discovered_urls.txt").write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
        with (out_dir / "discovery_events.jsonl").open("w", encoding="utf-8") as fh:
            for event in discovery_events:
                fh.write(json_dumps(event) + "\n")
        # The complete listing/API corpus is identical for every shard. Preserve it once.
        if args.shard_index != 0:
            (out_dir / "listing_records.jsonl").unlink(missing_ok=True)
            shutil.rmtree(out_dir / "raw" / "api", ignore_errors=True)
        stats = await crawl_details(config, out_dir, selected, listing_by_url, store_raw=False)
        manifest.update(
            {
                "all_discovered_urls": len(all_urls),
                "selected_urls": len(selected),
                "crawl": stats,
                "status": "complete" if stats.get("failed", 0) == 0 else "complete_with_failures",
            }
        )
    except Exception as exc:
        manifest.update(
            {
                "status": "fatal_error",
                "fatal_error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                },
            }
        )
        (out_dir / "fatal_error.txt").write_text(traceback.format_exc(), encoding="utf-8")
    finally:
        manifest["completed_at"] = utcnow()
        manifest["elapsed_seconds"] = round(time.monotonic() - clock, 3)
        (out_dir / "manifest.json").write_text(json_dumps(manifest, pretty=True), encoding="utf-8")
        write_checksums(out_dir)
        print("TERPEEZY_SHARD_MANIFEST=" + json_dumps(manifest), flush=True)
    return 1 if manifest["status"] == "fatal_error" else 0


def main() -> None:
    raise SystemExit(asyncio.run(run(parse_args())))


if __name__ == "__main__":
    main()
