"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { CoverageSummary, FxRate, PaginatedResponse, ListingSummary } from "@tsubo/contracts";

export function useFxRate() {
  return useQuery<FxRate>({
    queryKey: ["fx"],
    queryFn: () => api.getFxRate(),
  });
}

export function useCoverageSummary() {
  return useQuery<CoverageSummary>({
    queryKey: ["coverage", "summary"],
    queryFn: () => api.getCoverageSummary(),
  });
}

export function useListings(params: Record<string, string>) {
  return useQuery<PaginatedResponse<ListingSummary>>({
    queryKey: ["listings", params],
    queryFn: () => api.searchListings(params),
    enabled: Object.keys(params).length > 0,
  });
}

export function useListing(slug: string) {
  return useQuery({
    queryKey: ["listing", slug],
    queryFn: () => api.getListing(slug),
    enabled: Boolean(slug),
  });
}

export function useSources() {
  return useQuery({
    queryKey: ["sources"],
    queryFn: () => api.getSources(),
  });
}

export function useSource(slug: string) {
  return useQuery({
    queryKey: ["source", slug],
    queryFn: () => api.getSource(slug),
    enabled: Boolean(slug),
  });
}

export function usePrefecture(slug: string) {
  return useQuery({
    queryKey: ["prefecture", slug],
    queryFn: () => api.getPrefecture(slug),
    enabled: Boolean(slug),
  });
}

export function useMunicipality(slug: string) {
  return useQuery({
    queryKey: ["municipality", slug],
    queryFn: () => api.getMunicipality(slug),
    enabled: Boolean(slug),
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ["admin", "system", "health"],
    queryFn: () => api.getSystemHealth(),
  });
}
