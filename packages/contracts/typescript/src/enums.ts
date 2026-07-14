export type EntityType =
  | "country"
  | "convenience_region"
  | "prefecture"
  | "hokkaido_subprefecture"
  | "county_district"
  | "municipality"
  | "tokyo_special_ward"
  | "designated_city_ward"
  | "town_aza"
  | "island"
  | "remote_island_grouping"
  | "administrative_reference";

export type CoverageState =
  | "DIRECT_ACTIVE"
  | "DIRECT_ZERO_INVENTORY"
  | "DIRECT_REGISTRATION_REQUIRED"
  | "DIRECT_PAPER_ONLY"
  | "DIRECT_DISCONTINUED"
  | "PREFECTURAL_ONLY"
  | "REGIONAL_ONLY"
  | "NATIONAL_BANK_ONLY"
  | "PUBLIC_ASSET_ONLY"
  | "DISCOVERED_UNPARSED"
  | "SOURCE_BROKEN"
  | "SOURCE_BLOCKED"
  | "SOURCE_MISSING"
  | "UNDER_REVIEW"
  | "NOT_APPLICABLE"
  | "ADMINISTRATIVE_REFERENCE_ONLY";

export type SourceClass =
  | "NATIONAL_GOVERNMENT"
  | "NATIONWIDE_AKIYA_BANK"
  | "PREFECTURAL_REGIONAL"
  | "MUNICIPAL_DIRECT"
  | "GENERAL_HOME_SEARCH"
  | "PUBLIC_ASSET"
  | "SUPPORTING_DATA";

export type AccessMode =
  | "PUBLIC_API"
  | "PUBLIC_JSON"
  | "PUBLIC_CSV"
  | "PUBLIC_XML"
  | "PUBLIC_RSS"
  | "PUBLIC_HTML"
  | "PUBLIC_JAVASCRIPT_APP"
  | "PUBLIC_PDF"
  | "PUBLIC_SPREADSHEET"
  | "PUBLIC_IMAGE_DOCUMENT"
  | "MANUAL_IMPORT"
  | "REGISTRATION_REQUIRED"
  | "PAPER_ONLY"
  | "DISABLED";

export type SourceHealth =
  | "HEALTHY"
  | "DEGRADED"
  | "STALE"
  | "PARSER_DRIFT"
  | "RATE_LIMITED"
  | "TEMPORARILY_UNAVAILABLE"
  | "BLOCKED"
  | "DISABLED"
  | "UNKNOWN";

export type ListingStatus =
  | "ACTIVE"
  | "NEW"
  | "AVAILABLE"
  | "APPLICATION_OPEN"
  | "UNDER_NEGOTIATION"
  | "APPLICATION_PENDING"
  | "RESERVED"
  | "APPLICATION_CLOSED"
  | "SOLD"
  | "RENTED"
  | "TRANSFERRED"
  | "WITHDRAWN"
  | "EXPIRED"
  | "REMOVED_FROM_SOURCE"
  | "SOURCE_UNAVAILABLE"
  | "STATUS_UNKNOWN";

export type TransactionType =
  | "sale"
  | "rent"
  | "lease"
  | "rent_to_own"
  | "transfer"
  | "free_transfer"
  | "auction"
  | "tender"
  | "trial_residence"
  | "negotiation"
  | "unknown";

export type PriceKind =
  | "FIXED"
  | "NEGOTIABLE"
  | "ZERO_PRICE"
  | "FREE_TRANSFER"
  | "MINIMUM_BID"
  | "RESERVE_PRICE"
  | "MONTHLY_RENT"
  | "ANNUAL_RENT"
  | "UNDISCLOSED"
  | "PENDING"
  | "UNKNOWN";

export type PropertyType =
  | "detached_house"
  | "row_house"
  | "condominium"
  | "apartment_unit"
  | "apartment_building"
  | "kominka"
  | "farmhouse"
  | "house_with_farmland"
  | "mixed_residential_commercial"
  | "shop_with_residence"
  | "vacant_land"
  | "residential_lot"
  | "agricultural_land"
  | "forest"
  | "warehouse"
  | "factory"
  | "office"
  | "lodging"
  | "public_building"
  | "former_school"
  | "trial_residence"
  | "other"
  | "unknown";

export type LocationPrecision =
  | "EXACT_BUILDING"
  | "EXACT_PARCEL"
  | "STREET_BLOCK"
  | "TOWN_AZA"
  | "POSTCODE"
  | "MUNICIPALITY"
  | "PREFECTURE"
  | "SOURCE_MAP_ONLY"
  | "WITHHELD"
  | "UNKNOWN";

export type ConditionCategory =
  | "immediately_habitable"
  | "minor_repair"
  | "substantial_repair"
  | "major_rehabilitation"
  | "demolition_required"
  | "structure_only"
  | "not_inspected"
  | "unknown";

export type CurrencyCode = "USD" | "JPY";
