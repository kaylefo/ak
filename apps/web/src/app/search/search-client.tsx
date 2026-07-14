"use client";

import { Container, EmptyState, PageHeader } from "@tsubo/ui";
import { SearchFilters } from "@/components/search-filters";
import { ListingCard } from "@/components/listing-card";
import { useListings } from "@/lib/queries";
import { useSearchParams } from "next/navigation";

export function SearchPageClient() {
  const searchParams = useSearchParams();
  const params = Object.fromEntries(searchParams.entries());
  const hasFilters = Object.keys(params).length > 0;
  const { data, isLoading, isError } = useListings(params);

  return (
    <Container className="py-12">
      <PageHeader
        eyebrow="Registry search"
        title="Listings"
        subtitle="Filter by prefecture, transaction type, and property class."
      />

      <div className="mb-8">
        <SearchFilters initial={params} />
      </div>

      {!hasFilters ? (
        <EmptyState
          title="Set filters to search"
          description="Enter keywords or select a prefecture to query the registry."
        />
      ) : isLoading ? (
        <p className="text-sm text-stone-500">Searching…</p>
      ) : isError ? (
        <EmptyState
          title="Search unavailable"
          description="The API could not be reached. Ensure NEXT_PUBLIC_API_URL is configured."
        />
      ) : data && data.items.length > 0 ? (
        <div className="space-y-6">
          <p className="font-mono text-xs text-stone-500">
            {data.total.toLocaleString()} results
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            {data.items.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        </div>
      ) : (
        <EmptyState title="No listings found" description="Try broadening your filters." />
      )}
    </Container>
  );
}
