"use client";

import { Badge, Container, DataTable, EmptyState, PageHeader } from "@tsubo/ui";
import Link from "next/link";
import { useSources } from "@/lib/queries";

export default function SourcesPage() {
  const { data, isLoading, isError } = useSources();

  return (
    <Container className="py-12">
      <PageHeader
        eyebrow="Data provenance"
        title="Sources"
        subtitle="Municipal portals, akiya banks, and public asset programs feeding the registry."
      />

      {isLoading ? (
        <p className="text-sm text-stone-500">Loading sources…</p>
      ) : isError ? (
        <EmptyState title="Sources unavailable" description="API connection failed." />
      ) : data && data.length > 0 ? (
        <DataTable
          headers={["Name", "Class", "Health", "Listings", ""]}
          rows={data.map((source) => [
            <Link
              key={source.slug}
              href={`/source/${source.slug}`}
              className="font-medium text-stone-800 hover:underline"
            >
              {source.name}
            </Link>,
            <Badge key={`class-${source.slug}`}>{source.source_class.replace(/_/g, " ")}</Badge>,
            <Badge
              key={`health-${source.slug}`}
              tone={source.health === "HEALTHY" ? "success" : "warning"}
            >
              {source.health}
            </Badge>,
            source.listing_count.toLocaleString(),
            <Link
              key={`link-${source.slug}`}
              href={`/source/${source.slug}`}
              className="text-sm text-stone-500 hover:text-stone-800"
            >
              View →
            </Link>,
          ])}
        />
      ) : (
        <EmptyState title="No sources indexed" />
      )}
    </Container>
  );
}
