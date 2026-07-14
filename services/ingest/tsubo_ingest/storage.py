"""Unified snapshot storage with S3 primary and local filesystem fallback."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from tsubo_ingest.context import FetchResponse
from tsubo_ingest.local_storage import LocalSnapshotStore
from tsubo_ingest.snapshot import SnapshotStore


@dataclass(frozen=True)
class StoredSnapshot:
    backend: str
    key: str
    sha256: str
    content_type: str | None
    size_bytes: int
    stored_at: datetime


class HybridSnapshotStore:
    def __init__(self) -> None:
        self._s3: SnapshotStore | None = None
        self._local: LocalSnapshotStore | None = None
        endpoint = os.environ.get("S3_ENDPOINT")
        bucket = os.environ.get("S3_BUCKET", "tsubo-raw")
        local_root = os.environ.get("TSUBO_LOCAL_SNAPSHOT_ROOT", "/workspace/data/snapshots")
        try:
            self._s3 = SnapshotStore(
                bucket=bucket,
                endpoint_url=endpoint,
                access_key=os.environ.get("S3_ACCESS_KEY_ID"),
                secret_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
            )
            self._s3._client.head_bucket(Bucket=bucket)
            self.backend = "s3"
        except Exception:
            self._s3 = None
            self._local = LocalSnapshotStore(local_root)
            self.backend = "local"

    def save(self, source_id: str, response: FetchResponse, **meta: str) -> StoredSnapshot:
        if self._s3 is not None:
            ref = self._s3.save(source_id, response, metadata=meta or None)
            return StoredSnapshot(
                backend="s3",
                key=f"{ref.bucket}/{ref.key}",
                sha256=ref.sha256,
                content_type=ref.content_type,
                size_bytes=ref.size_bytes,
                stored_at=ref.stored_at,
            )
        assert self._local is not None
        ref = self._local.save(source_id, response, metadata=meta or None)
        return StoredSnapshot(
            backend="local",
            key=str(ref.path),
            sha256=ref.sha256,
            content_type=ref.content_type,
            size_bytes=ref.size_bytes,
            stored_at=ref.stored_at,
        )
