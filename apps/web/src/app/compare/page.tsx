"use client";

import { Container, EmptyState, PageHeader } from "@tsubo/ui";

export default function ComparePage() {
  return (
    <Container className="py-12">
      <PageHeader
        eyebrow="Side by side"
        title="Compare listings"
        subtitle="Select up to four listings to compare price, area, condition, and source coverage."
      />
      <EmptyState
        title="No listings selected"
        description="Add listings from search results or detail pages to begin comparison."
      />
    </Container>
  );
}
