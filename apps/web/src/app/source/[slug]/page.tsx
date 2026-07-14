"use client";

import { Badge, Card, Container, EmptyState, PageHeader, Section } from "@tsubo/ui";
import { useSource } from "@/lib/queries";
import { use } from "react";

export default function SourcePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const { data, isLoading, isError } = useSource(slug);

  return (
    <Container narrow className="py-12">
      {isLoading ? (
        <p className="text-sm text-stone-500">Loading source…</p>
      ) : isError || !data ? (
        <EmptyState title="Source not found" description={`No source with slug "${slug}".`} />
      ) : (
        <>
          <PageHeader
            eyebrow="Source detail"
            title={data.name}
            subtitle={data.description ?? undefined}
          />

          <div className="mb-6 flex flex-wrap gap-2">
            <Badge>{data.source_class.replace(/_/g, " ")}</Badge>
            <Badge tone={data.health === "HEALTHY" ? "success" : "warning"}>
              {data.health}
            </Badge>
            <Badge tone="info">{data.coverage_state.replace(/_/g, " ")}</Badge>
          </div>

          <Section title="Metrics">
            <Card variant="muted" className="grid gap-4 sm:grid-cols-3">
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-stone-500">
                  Listings
                </p>
                <p className="mt-1 font-serif text-2xl">{data.listing_count}</p>
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-stone-500">
                  Municipalities
                </p>
                <p className="mt-1 font-serif text-2xl">{data.municipality_count}</p>
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-stone-500">
                  Access
                </p>
                <p className="mt-1 text-sm text-stone-700">
                  {data.access_mode.replace(/_/g, " ")}
                </p>
              </div>
            </Card>
          </Section>

          {data.homepage_url ? (
            <a
              href={data.homepage_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-stone-600 underline-offset-2 hover:underline"
            >
              Visit source website →
            </a>
          ) : null}
        </>
      )}
    </Container>
  );
}
