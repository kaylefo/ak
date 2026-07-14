import type {
  AccessMode,
  ConditionCategory,
  CoverageState,
  CurrencyCode,
  ListingStatus,
  LocationPrecision,
  PriceKind,
  PropertyType,
  SourceClass,
  SourceHealth,
  TransactionType,
} from "./enums.js";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface MoneyAmount {
  amount_jpy: number | null;
  amount_usd: number | null;
  price_kind: PriceKind;
  display_label: string | null;
}

export interface GeoPoint {
  lat: number;
  lng: number;
}

export interface ListingSummary {
  id: string;
  slug: string;
  title: string;
  title_ja: string | null;
  status: ListingStatus;
  transaction_type: TransactionType;
  property_type: PropertyType;
  condition: ConditionCategory;
  price: MoneyAmount;
  prefecture_slug: string;
  prefecture_name: string;
  municipality_slug: string | null;
  municipality_name: string | null;
  location_precision: LocationPrecision;
  coordinates: GeoPoint | null;
  floor_area_sqm: number | null;
  land_area_sqm: number | null;
  built_year: number | null;
  source_slug: string;
  source_name: string;
  published_at: string | null;
  updated_at: string;
}

export interface ListingDetail extends ListingSummary {
  description: string | null;
  description_ja: string | null;
  address_display: string | null;
  address_ja: string | null;
  images: ListingImage[];
  amenities: string[];
  source_url: string | null;
  coverage_state: CoverageState;
}

export interface ListingImage {
  url: string;
  alt: string | null;
  sort_order: number;
}

export interface SearchFilters {
  q?: string;
  prefecture?: string;
  municipality?: string;
  transaction_type?: TransactionType;
  property_type?: PropertyType;
  min_price_jpy?: number;
  max_price_jpy?: number;
  min_area_sqm?: number;
  max_area_sqm?: number;
  status?: ListingStatus;
  page?: number;
  page_size?: number;
}

export interface SourceSummary {
  id: string;
  slug: string;
  name: string;
  name_ja: string | null;
  source_class: SourceClass;
  access_mode: AccessMode;
  health: SourceHealth;
  coverage_state: CoverageState;
  listing_count: number;
  municipality_count: number;
  last_synced_at: string | null;
  homepage_url: string | null;
}

export interface SourceDetail extends SourceSummary {
  description: string | null;
  prefecture_slug: string | null;
  prefecture_name: string | null;
  municipality_slug: string | null;
  municipality_name: string | null;
  parser_version: string | null;
  notes: string | null;
}

export interface CoverageRegionSummary {
  slug: string;
  name: string;
  name_ja: string | null;
  entity_type: string;
  coverage_state: CoverageState;
  listing_count: number;
  source_count: number;
  child_count: number;
}

export interface CoverageSummary {
  total_listings: number;
  total_sources: number;
  prefectures_covered: number;
  municipalities_covered: number;
  direct_active_count: number;
  last_updated_at: string;
  by_state: Record<CoverageState, number>;
}

export interface FxRate {
  base_currency: CurrencyCode;
  quote_currency: CurrencyCode;
  rate: number;
  effective_date: string;
  provider: string;
  is_stale: boolean;
  fetched_at: string;
}

export interface PrefectureDetail {
  slug: string;
  name: string;
  name_ja: string;
  region: string;
  listing_count: number;
  municipality_count: number;
  coverage_state: CoverageState;
  coordinates: GeoPoint;
}

export interface MunicipalityDetail {
  slug: string;
  name: string;
  name_ja: string;
  prefecture_slug: string;
  prefecture_name: string;
  listing_count: number;
  coverage_state: CoverageState;
  coordinates: GeoPoint | null;
}

export interface CompareEntry {
  listing: ListingSummary;
  added_at: string;
}

export interface SystemHealth {
  api_status: "healthy" | "degraded" | "down";
  worker_status: "healthy" | "degraded" | "down";
  opensearch_status: "healthy" | "degraded" | "down";
  last_ingest_at: string | null;
  version: string;
}
