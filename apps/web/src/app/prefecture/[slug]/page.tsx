"use client";

import { Badge, Container, EmptyState, PageHeader, Stat } from "@tsubo/ui";
import { usePrefecture } from "@/lib/queries";
import Link from "next/link";
import { use } from "react";

export default function PrefecturePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const { data, isLoading, isError } = usePrefecture(slug);

  return (
    <Container className="py-12">
      {isLoading ? (
        <p className="text-sm text-stone-500">Loading prefecture…</p>
      ) : isError || !data ? (
        <EmptyState title="Prefecture not found" description={`No prefecture "${slug}".`} />
      ) : (
        <>
          <PageHeader
            eyebrow="Prefecture"
            title={data.name}
            subtitle={`${data.name_ja} · ${data.region}`}
          />

          <div className="mb-8">
            <Badge tone="info">{data.coverage_state.replace(/_/g, " ")}</Badge>
          </div>

          <div className="mb-10 grid gap-6 sm:grid-cols-3">
            <Stat label="Listings" value={data.listing_count.toLocaleString()} />
            <Stat label="Municipalities" value={data.municipality_count} />
            <Stat label="Region" value={data.region} />
          </div>

          <Link
            href={`/search?prefecture=${data.slug}`}
            className="text-sm text-stone-600 underline-offset-2 hover:underline"
          >
            Search listings in {data.name} →
          </Link>
        </>
      )}
    </Container>
  );
}
