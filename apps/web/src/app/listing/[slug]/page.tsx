"use client";

import { Container, EmptyState, PageHeader } from "@tsubo/ui";
import { ListingDetailView } from "@/components/listing-detail";
import { useListing } from "@/lib/queries";
import { use } from "react";

export default function ListingPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const { data, isLoading, isError } = useListing(slug);

  return (
    <Container narrow className="py-12">
      {isLoading ? (
        <p className="text-sm text-stone-500">Loading listing…</p>
      ) : isError || !data ? (
        <EmptyState
          title="Listing not found"
          description={`No listing with slug "${slug}" could be loaded.`}
        />
      ) : (
        <>
          <PageHeader eyebrow="Listing" title={data.title} />
          <ListingDetailView listing={data} />
        </>
      )}
    </Container>
  );
}
