import type {
  CoverageRegionSummary,
  CoverageSummary,
  FxRate,
  ListingDetail,
  ListingSummary,
  MunicipalityDetail,
  PaginatedResponse,
  PrefectureDetail,
  SearchFilters,
  SourceDetail,
  SourceSummary,
  SystemHealth,
} from "@tsubo/contracts";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_URL}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
  });

  if (!res.ok) {
    throw new ApiError(`API request failed: ${res.statusText}`, res.status);
  }

  return res.json() as Promise<T>;
}

function toQueryString(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const api = {
  searchListings(filters: SearchFilters = {}): Promise<PaginatedResponse<ListingSummary>> {
    return fetchApi(`/api/v1/listings${toQueryString(filters as Record<string, string | number | undefined>)}`);
  },

  getListing(slug: string): Promise<ListingDetail> {
    return fetchApi(`/api/v1/listings/${slug}`);
  },

  getCoverageSummary(): Promise<CoverageSummary> {
    return fetchApi("/api/v1/coverage/summary");
  },

  getCoverageRegions(): Promise<CoverageRegionSummary[]> {
    return fetchApi("/api/v1/coverage/regions");
  },

  getSources(): Promise<SourceSummary[]> {
    return fetchApi("/api/v1/sources");
  },

  getSource(slug: string): Promise<SourceDetail> {
    return fetchApi(`/api/v1/sources/${slug}`);
  },

  getFxRate(): Promise<FxRate> {
    return fetchApi("/api/v1/fx/current");
  },

  getPrefecture(slug: string): Promise<PrefectureDetail> {
    return fetchApi(`/api/v1/prefectures/${slug}`);
  },

  getMunicipality(slug: string): Promise<MunicipalityDetail> {
    return fetchApi(`/api/v1/municipalities/${slug}`);
  },

  getSystemHealth(): Promise<SystemHealth> {
    return fetchApi("/api/v1/admin/system/health");
  },
};

export { API_URL };
