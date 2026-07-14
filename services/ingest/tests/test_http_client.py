"""Tests for SafeHttpClient SSRF protection and encoding detection."""


import httpx
import pytest
from tsubo_ingest.http_client import SafeHttpClient, SSRFError, detect_encoding, validate_url


def test_validate_url_blocks_localhost() -> None:
    with pytest.raises(SSRFError):
        validate_url("http://localhost/admin")


def test_validate_url_blocks_private_ip() -> None:
    with pytest.raises(SSRFError):
        validate_url("http://192.168.1.1/internal")


def test_detect_encoding_utf8_bom() -> None:
    assert detect_encoding(b"\xef\xbb\xbfhello", None) == "utf-8-sig"


def test_detect_encoding_from_header() -> None:
    assert detect_encoding(b"test", "text/html; charset=shift_jis") == "shift_jis"


def test_conditional_request_uses_etag() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            headers={"ETag": '"abc123"', "Last-Modified": "Mon, 14 Jul 2025 00:00:00 GMT"},
            content=b"<html>first</html>",
        )
    )
    client = httpx.Client(transport=transport)
    safe = SafeHttpClient(client=client)

    first = safe.get("https://example.com/page", use_conditional=False)
    assert first.etag == '"abc123"'
    assert first.content == b"<html>first</html>"

    transport = httpx.MockTransport(
        lambda request: (
            httpx.Response(304)
            if request.headers.get("If-None-Match") == '"abc123"'
            else httpx.Response(200, content=b"<html>changed</html>")
        )
    )
    safe._client = httpx.Client(transport=transport)
    second = safe.get("https://example.com/page")
    assert second.not_modified is True
    assert second.status_code == 304

    safe.close()
