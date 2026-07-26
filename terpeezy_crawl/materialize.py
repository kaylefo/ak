from __future__ import annotations

import base64
import zlib
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    payload_dir = root / "payload"
    for name in ("crawl.py", "sources.json"):
        parts = sorted(payload_dir.glob(f"{name}.z64.*"))
        if not parts:
            raise RuntimeError(f"missing payload chunks for {name}")
        encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
        target = root / name
        target.write_bytes(zlib.decompress(base64.b64decode(encoded)))
        print(f"materialized {target.name}: {target.stat().st_size} bytes")


if __name__ == "__main__":
    main()
