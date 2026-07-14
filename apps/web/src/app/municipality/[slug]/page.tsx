"use client";

import { Badge, Container, EmptyState, PageHeader, Stat } from "@tsubo/ui";
import { useMunicipality } from "@/lib/queries";
import Link from "next/link";
import { use } from "react";

export default function MunicipalityPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const { data, isLoading, isError } = useMunicipality(slug);

  return (
    <Container className="py-12">
      {isLoading ? (
        <p className="text-sm text-stone-500">Loading municipality…</p>
      ) : isError || !data ? (
        <EmptyState title="Municipality not found" description={`No municipality "${slug}".`} />
      ) : (
        <>
          <PageHeader
            eyebrow="Municipality"
            title={data.name}
            subtitle={`${data.name_ja} · ${data.prefecture_name}`}
          />

          <div className="mb-8">
            <Badge tone="info">{data.coverage_state.replace(/_/g, " ")}</Badge>
          </div>

          <div className="mb-10 grid gap-6 sm:grid-cols-2">
            <Stat label="Listings" value={data.listing_count.toLocaleString()} />
            <Stat label="Prefecture" value={data.prefecture_name} />
          </div>

          <div className="flex gap-4 text-sm">
            <Link
              href={`/prefecture/${data.prefecture_slug}`}
              className="text-stone-600 underline-offset-2 hover:underline"
            >
              View prefecture →
            </Link>
            <Link
              href={`/search?municipality=${data.slug}`}
              className="text-stone-600 underline-offset-2 hover:underline"
            >
              Search listings →
            </Link>
          </div>
        </>
      )}
    </Container>
  );
}
