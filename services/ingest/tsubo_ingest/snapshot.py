"""Snapshot storage for raw fetched content in S3/MinIO."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import boto3
from botocore.client import BaseClient

from tsubo_ingest.context import FetchResponse


@dataclass(frozen=True)
class SnapshotRef:
    """Reference to a stored raw snapshot."""

    bucket: str
    key: str
    sha256: str
    content_type: str | None
    size_bytes: int
    stored_at: datetime


class SnapshotStore:
    """Persist raw fetch responses to S3-compatible object storage."""

    def __init__(
        self,
        *,
        bucket: str = "tsubo-raw",
        prefix: str = "snapshots",
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        client: BaseClient | None = None,
    ) -> None:
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self._client = client or boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def _object_key(self, source_id: str, url: str, fetched_at: datetime) -> str:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        ts = fetched_at.strftime("%Y/%m/%d/%H%M%S")
        return f"{self.prefix}/{source_id}/{ts}_{digest}.bin"

    def save(
        self,
        source_id: str,
        response: FetchResponse,
        *,
        metadata: dict[str, str] | None = None,
    ) -> SnapshotRef:
        if response.not_modified:
            raise ValueError("Cannot snapshot a 304 Not Modified response")

        sha256 = hashlib.sha256(response.content).hexdigest()
        fetched_at = response.fetched_at.replace(tzinfo=UTC)
        key = self._object_key(source_id, response.url, fetched_at)

        extra: dict[str, Any] = {
            "ContentType": response.content_type or "application/octet-stream",
            "Metadata": {
                "url": response.url,
                "sha256": sha256,
                "encoding": response.encoding,
                "status_code": str(response.status_code),
            },
        }
        if metadata:
            extra["Metadata"].update(metadata)
        if response.etag:
            extra["Metadata"]["etag"] = response.etag

        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=response.content,
            **extra,
        )

        return SnapshotRef(
            bucket=self.bucket,
            key=key,
            sha256=sha256,
            content_type=response.content_type,
            size_bytes=len(response.content),
            stored_at=fetched_at,
        )

    def load(self, key: str) -> bytes:
        obj = self._client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()
