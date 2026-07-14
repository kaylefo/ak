from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from tsubo_api.config import Settings
from tsubo_api.errors import ValidationError
from tsubo_api.services.search import SearchService


@pytest.fixture
def search_settings() -> Settings:
    return Settings(
        APP_ENV="test",
        OPENSEARCH_URL="http://localhost:9200",
        OPENSEARCH_INDEX_LISTINGS="test_listings",
    )


@pytest.fixture
def search_service(search_settings: Settings) -> SearchService:
    return SearchService(search_settings)


@pytest.mark.asyncio
async def test_search_listings_validation(search_service: SearchService):
    with pytest.raises(ValidationError):
        await search_service.search_listings(page=0)

    with pytest.raises(ValidationError):
        await search_service.search_listings(page_size=200)


@pytest.mark.asyncio
async def test_search_listings_success(search_service: SearchService):
    mock_client = AsyncMock()
    mock_client.search.return_value = {
        "hits": {
            "total": {"value": 1},
            "hits": [
                {
                    "_id": "abc",
                    "_score": 1.5,
                    "_source": {"id": "abc", "title_ja": "Test Listing", "price_jpy": 1000000},
                }
            ],
        }
    }
    search_service._client = mock_client

    result = await search_service.search_listings(
        query="test",
        min_price_jpy=Decimal("500000"),
        page=1,
        page_size=10,
    )

    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["title_ja"] == "Test Listing"
    mock_client.search.assert_awaited_once()
