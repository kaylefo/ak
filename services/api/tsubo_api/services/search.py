from decimal import Decimal
from typing import Any
from uuid import UUID

import structlog
from opensearchpy import NotFoundError as OSNotFoundError
from opensearchpy._async.client import AsyncOpenSearch

from tsubo_api.config import Settings
from tsubo_api.errors import ExternalServiceError, ValidationError

logger = structlog.get_logger(__name__)


class SearchService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: AsyncOpenSearch | None = None

    def _build_client(self) -> AsyncOpenSearch:
        auth = None
        if self.settings.opensearch_username and self.settings.opensearch_password:
            auth = (self.settings.opensearch_username, self.settings.opensearch_password)
        return AsyncOpenSearch(
            hosts=[self.settings.opensearch_url],
            http_auth=auth,
            use_ssl=self.settings.opensearch_url.startswith("https"),
            verify_certs=not self.settings.is_development,
        )

    @property
    def client(self) -> AsyncOpenSearch:
        if self._client is None:
            self._client = self._build_client()
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def search_listings(
        self,
        *,
        query: str | None = None,
        prefecture: str | None = None,
        municipality: str | None = None,
        property_type: str | None = None,
        transaction_type: str | None = None,
        min_price_jpy: Decimal | None = None,
        max_price_jpy: Decimal | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        if page < 1:
            raise ValidationError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValidationError("page_size must be between 1 and 100")

        must: list[dict[str, Any]] = []
        filter_clauses: list[dict[str, Any]] = []

        if query:
            must.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title_ja^3",
                            "title_en^2",
                            "description_ja",
                            "description_en",
                            "address_ja",
                            "address_en",
                        ],
                        "type": "best_fields",
                    }
                }
            )
        if prefecture:
            filter_clauses.append({"term": {"prefecture": prefecture}})
        if municipality:
            filter_clauses.append({"term": {"municipality": municipality}})
        if property_type:
            filter_clauses.append({"term": {"property_type": property_type}})
        if transaction_type:
            filter_clauses.append({"term": {"transaction_type": transaction_type}})
        if min_price_jpy is not None:
            filter_clauses.append({"range": {"price_jpy": {"gte": int(min_price_jpy)}}})
        if max_price_jpy is not None:
            filter_clauses.append({"range": {"price_jpy": {"lte": int(max_price_jpy)}}})

        body: dict[str, Any] = {
            "from": (page - 1) * page_size,
            "size": page_size,
            "query": {
                "bool": {
                    "must": must or [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            },
            "sort": [{"last_seen_at": {"order": "desc"}}],
        }

        try:
            response = await self.client.search(
                index=self.settings.opensearch_index_listings,
                body=body,
            )
        except Exception as exc:
            logger.error("opensearch_search_failed", error=str(exc))
            raise ExternalServiceError("Search service unavailable") from exc

        hits = response.get("hits", {})
        total = hits.get("total", {})
        if isinstance(total, dict):
            total_count = total.get("value", 0)
        else:
            total_count = total

        items = []
        for hit in hits.get("hits", []):
            source = hit.get("_source", {})
            items.append(
                {
                    "id": source.get("id") or hit.get("_id"),
                    "score": hit.get("_score"),
                    **source,
                }
            )

        return {
            "items": items,
            "total": total_count,
            "page": page,
            "page_size": page_size,
        }

    async def get_listing(self, listing_id: UUID) -> dict[str, Any] | None:
        try:
            response = await self.client.get(
                index=self.settings.opensearch_index_listings,
                id=str(listing_id),
            )
        except OSNotFoundError:
            return None
        except Exception as exc:
            logger.error("opensearch_get_failed", listing_id=str(listing_id), error=str(exc))
            raise ExternalServiceError("Search service unavailable") from exc
        return response.get("_source")

    async def index_listing(self, listing_doc: dict[str, Any]) -> None:
        listing_id = listing_doc.get("id")
        if listing_id is None:
            raise ValidationError("listing document requires id")
        try:
            await self.client.index(
                index=self.settings.opensearch_index_listings,
                id=str(listing_id),
                body=listing_doc,
                refresh=False,
            )
        except Exception as exc:
            logger.error("opensearch_index_failed", listing_id=str(listing_id), error=str(exc))
            raise ExternalServiceError("Failed to index listing") from exc
