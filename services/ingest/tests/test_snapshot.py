"""Tests for snapshot storage."""

from datetime import datetime

import boto3
import pytest
from moto import mock_aws
from tsubo_ingest.context import FetchResponse
from tsubo_ingest.snapshot import SnapshotStore


@mock_aws
def test_snapshot_store_roundtrip() -> None:
    bucket = "tsubo-raw"
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket)

    store = SnapshotStore(bucket=bucket, client=s3)
    response = FetchResponse(
        url="https://example.test/listing/1",
        status_code=200,
        content=b"<html>snapshot</html>",
        content_type="text/html; charset=utf-8",
        encoding="utf-8",
        etag='"etag-1"',
        fetched_at=datetime(2026, 7, 14, 12, 0, 0),
    )

    ref = store.save("lifull_tokyo", response, metadata={"adapter": "lifull_listings"})
    assert ref.bucket == bucket
    assert ref.size_bytes == len(response.content)
    assert ref.sha256

    loaded = store.load(ref.key)
    assert loaded == response.content


@mock_aws
def test_snapshot_store_rejects_not_modified() -> None:
    bucket = "tsubo-raw"
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket)
    store = SnapshotStore(bucket=bucket, client=s3)

    response = FetchResponse(
        url="https://example.test/page",
        status_code=304,
        content=b"",
        content_type=None,
        encoding="utf-8",
        not_modified=True,
    )

    with pytest.raises(ValueError, match="304"):
        store.save("test_source", response)
