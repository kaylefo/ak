"""HTTP client with SSRF protection, conditional requests, and encoding detection."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlparse

import chardet
import httpx

from tsubo_ingest.context import FetchResponse

_PRIVATE_NETWORKS = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
)

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "metadata.google.internal",
        "metadata",
    }
)

_CHARSET_RE = re.compile(r"charset=([^\s;\"']+)", re.IGNORECASE)


class SSRFError(ValueError):
    """Raised when a URL targets a disallowed host or network."""


@dataclass
class ConditionalState:
    """Stored conditional request headers for a URL."""

    etag: str | None = None
    last_modified: datetime | None = None


def _is_private_ip(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return any(addr in network for network in _PRIVATE_NETWORKS)


def validate_url(url: str) -> None:
    """Reject URLs that could be used for SSRF attacks."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SSRFError(f"Unsupported scheme: {parsed.scheme!r}")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL missing hostname")

    if hostname.lower() in _BLOCKED_HOSTNAMES:
        raise SSRFError(f"Blocked hostname: {hostname}")

    try:
        addr = ipaddress.ip_address(hostname)
        if _is_private_ip(addr):
            raise SSRFError(f"Blocked private/reserved IP: {hostname}")
        return
    except ValueError:
        pass

    try:
        infos = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise SSRFError(f"Cannot resolve hostname: {hostname}") from exc

    for info in infos:
        ip_str = info[4][0]
        addr = ipaddress.ip_address(ip_str)
        if _is_private_ip(addr):
            raise SSRFError(f"Hostname {hostname} resolves to blocked IP: {ip_str}")


def detect_encoding(content: bytes, content_type: str | None) -> str:
    """Detect response encoding from headers and byte content."""
    if content_type:
        match = _CHARSET_RE.search(content_type)
        if match:
            return match.group(1).strip().lower()

    if content.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"

    detected = chardet.detect(content)
    encoding = detected.get("encoding")
    if encoding:
        return encoding.lower()

    return "utf-8"


def _parse_last_modified(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None


class SafeHttpClient:
    """HTTP client that enforces SSRF checks and supports conditional GET."""

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        user_agent: str = "TsuboIngest/1.0 (+https://tsubo.example)",
        client: httpx.Client | None = None,
    ) -> None:
        self._timeout = timeout
        self._user_agent = user_agent
        self._client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self._conditional: dict[str, ConditionalState] = {}

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SafeHttpClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        use_conditional: bool = True,
    ) -> FetchResponse:
        validate_url(url)

        request_headers = {"User-Agent": self._user_agent}
        if headers:
            request_headers.update(headers)

        if use_conditional and url in self._conditional:
            state = self._conditional[url]
            if state.etag:
                request_headers["If-None-Match"] = state.etag
            if state.last_modified:
                request_headers["If-Modified-Since"] = state.last_modified.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )

        response = self._client.get(url, headers=request_headers)
        content_type = response.headers.get("content-type")
        etag = response.headers.get("etag")
        last_modified = _parse_last_modified(response.headers.get("last-modified"))

        if response.status_code == 304:
            prior = self._conditional.get(url)
            return FetchResponse(
                url=url,
                status_code=304,
                content=b"",
                content_type=content_type,
                encoding="utf-8",
                etag=prior.etag if prior else etag,
                last_modified=prior.last_modified if prior else last_modified,
                not_modified=True,
            )

        content = response.content
        encoding = detect_encoding(content, content_type)

        self._conditional[url] = ConditionalState(etag=etag, last_modified=last_modified)

        return FetchResponse(
            url=url,
            status_code=response.status_code,
            content=content,
            content_type=content_type,
            encoding=encoding,
            etag=etag,
            last_modified=last_modified,
        )
