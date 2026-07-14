"""Shared test configuration."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (
    ROOT / "services" / "api",
    ROOT / "services" / "ingest",
    ROOT / "services" / "worker",
    ROOT / "packages" / "contracts" / "python",
):
    sys.path.insert(0, str(path))
