from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from tsubo_api.dependencies import get_search_service
from tsubo_api.schemas.common import PaginatedResponse, SearchRequest
from tsubo_api.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


async def _run_search(
    search_service: SearchService,
    *,
    query: str | None,
    prefecture: str | None,
    municipality: str | None,
    property_type: str | None,
    transaction_type: str | None,
    min_price_jpy: Decimal | None,
    max_price_jpy: Decimal | None,
    page: int,
    page_size: int,
) -> PaginatedResponse:
    result = await search_service.search_listings(
        query=query,
        prefecture=prefecture,
        municipality=municipality,
        property_type=property_type,
        transaction_type=transaction_type,
        min_price_jpy=min_price_jpy,
        max_price_jpy=max_price_jpy,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(**result)


@router.post("", response_model=PaginatedResponse)
async def search_listings(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> PaginatedResponse:
    return await _run_search(
        search_service,
        query=request.query,
        prefecture=request.prefecture,
        municipality=request.municipality,
        property_type=request.property_type,
        transaction_type=request.transaction_type,
        min_price_jpy=request.min_price_jpy,
        max_price_jpy=request.max_price_jpy,
        page=request.page,
        page_size=request.page_size,
    )


@router.get("", response_model=PaginatedResponse)
async def search_listings_get(
    query: str | None = Query(None),
    prefecture: str | None = Query(None),
    municipality: str | None = Query(None),
    property_type: str | None = Query(None),
    transaction_type: str | None = Query(None),
    min_price_jpy: Decimal | None = Query(None),
    max_price_jpy: Decimal | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
) -> PaginatedResponse:
    return await _run_search(
        search_service,
        query=query,
        prefecture=prefecture,
        municipality=municipality,
        property_type=property_type,
        transaction_type=transaction_type,
        min_price_jpy=min_price_jpy,
        max_price_jpy=max_price_jpy,
        page=page,
        page_size=page_size,
    )
