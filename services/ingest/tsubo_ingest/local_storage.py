"""Content-addressed local filesystem snapshot storage (production fallback when MinIO unavailable)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from tsubo_ingest.context import FetchResponse


@dataclass(frozen=True)
class LocalSnapshotRef:
    path: Path
    sha256: str
    content_type: str | None
    size_bytes: int
    stored_at: datetime
    metadata_path: Path


class LocalSnapshotStore:
    """Persist raw bodies under a content-addressed directory tree."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        source_id: str,
        response: FetchResponse,
        *,
        metadata: dict[str, str] | None = None,
    ) -> LocalSnapshotRef:
        if response.not_modified:
            raise ValueError("Cannot snapshot a 304 Not Modified response")

        sha256 = hashlib.sha256(response.content).hexdigest()
        fetched_at = response.fetched_at.replace(tzinfo=UTC)
        rel_dir = self.root / source_id / fetched_at.strftime("%Y/%m/%d")
        rel_dir.mkdir(parents=True, exist_ok=True)
        body_path = rel_dir / f"{sha256}.bin"
        meta_path = rel_dir / f"{sha256}.meta.json"

        if not body_path.exists():
            body_path.write_bytes(response.content)

        meta = {
            "url": response.url,
            "sha256": sha256,
            "encoding": response.encoding,
            "status_code": response.status_code,
            "content_type": response.content_type,
            "etag": response.etag,
            "fetched_at": fetched_at.isoformat(),
            "source_id": source_id,
        }
        if metadata:
            meta.update(metadata)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        return LocalSnapshotRef(
            path=body_path,
            sha256=sha256,
            content_type=response.content_type,
            size_bytes=len(response.content),
            stored_at=fetched_at,
            metadata_path=meta_path,
        )

    def load(self, path: Path | str) -> bytes:
        return Path(path).read_bytes()
