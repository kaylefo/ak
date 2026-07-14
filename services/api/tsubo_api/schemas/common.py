from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str


class FXConvertRequest(BaseModel):
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)


class FXConvertResponse(BaseModel):
    amount: Decimal
    currency: str
    amount_jpy: Decimal
    rate_to_jpy: Decimal
    provider: str


class FXRateResponse(BaseModel):
    base_currency: str
    quote_currency: str
    rate: Decimal
    provider: str
    fetched_at: datetime


class FXProviderHealthResponse(ORMModel):
    provider: str
    status: str
    last_success_at: datetime | None
    last_failure_at: datetime | None
    consecutive_failures: int


class SearchRequest(BaseModel):
    query: str | None = None
    prefecture: str | None = None
    municipality: str | None = None
    property_type: str | None = None
    transaction_type: str | None = None
    min_price_jpy: Decimal | None = None
    max_price_jpy: Decimal | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ListingSummary(ORMModel):
    id: UUID
    source_id: UUID
    status: str
    transaction_type: str
    property_type: str
    price_jpy: Decimal | None
    price_kind: str
    monthly_rent_jpy: Decimal | None
    area_sqm: Decimal | None
    address_ja: str | None
    title_ja: str | None
    last_seen_at: datetime


class ListingDetail(ListingSummary):
    land_area_sqm: Decimal | None
    location_precision: str
    condition_category: str
    address_en: str | None
    title_en: str | None
    description_ja: str | None
    description_en: str | None
    layout: dict[str, Any] | None
    published_at: datetime | None
    administrative_entity_id: UUID | None
    created_at: datetime
    updated_at: datetime


class AdministrativeEntityResponse(ORMModel):
    id: UUID
    entity_type: str
    parent_id: UUID | None
    code: str | None
    canonical_name: str
    canonical_name_en: str | None


class SourceResponse(ORMModel):
    id: UUID
    source_class: str
    name: str
    base_url: str | None
    access_mode: str
    health: str


class SourceJurisdictionResponse(ORMModel):
    id: UUID
    source_id: UUID
    administrative_entity_id: UUID
    coverage_state: str
    notes: str | None


class CoverageAssessmentResponse(ORMModel):
    id: UUID
    administrative_entity_id: UUID
    coverage_state: str
    assessment_date: date
    notes: str | None
    assessed_by: str | None


class AdminStatsResponse(BaseModel):
    listings: int
    sources: int
    jurisdictions: int
    users: int
