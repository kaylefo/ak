"use client";

import { Suspense } from "react";
import { Container, PageHeader, Stat } from "@tsubo/ui";
import { SearchFilters } from "@/components/search-filters";
import { FxDisclosure } from "@/components/fx-disclosure";
import { useCoverageSummary, useFxRate } from "@/lib/queries";
import Link from "next/link";

export default function HomePage() {
  const { data: coverage, isLoading: coverageLoading } = useCoverageSummary();
  const { data: fx, isLoading: fxLoading } = useFxRate();

  return (
    <Container className="py-12">
      <PageHeader
        eyebrow="Japan vacant property registry"
        title="Find space with precision"
        subtitle="Search municipal listings, regional banks, and public asset programs. Coverage and exchange rates disclosed at every step."
      />

      <div className="mb-10 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Suspense fallback={<p className="text-sm text-stone-500">Loading filters…</p>}>
            <SearchFilters />
          </Suspense>
        </div>
        <FxDisclosure rate={fx ?? null} isLoading={fxLoading} />
      </div>

      <section aria-labelledby="coverage-heading" className="mb-12">
        <h2
          id="coverage-heading"
          className="mb-6 font-mono text-xs uppercase tracking-[0.2em] text-stone-500"
        >
          Coverage summary
        </h2>
        {coverageLoading ? (
          <p className="text-sm text-stone-500">Loading coverage data…</p>
        ) : coverage ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Listings" value={coverage.total_listings.toLocaleString()} />
            <Stat
              label="Sources"
              value={coverage.total_sources.toLocaleString()}
              hint={`${coverage.direct_active_count} direct active`}
            />
            <Stat
              label="Prefectures"
              value={coverage.prefectures_covered}
            />
            <Stat
              label="Municipalities"
              value={coverage.municipalities_covered.toLocaleString()}
            />
          </div>
        ) : (
          <p className="text-sm text-stone-500">
            Coverage data unavailable.{" "}
            <Link href="/coverage" className="underline underline-offset-2">
              View coverage map
            </Link>
          </p>
        )}
      </section>

      <nav className="grid gap-4 border-t border-stone-200 pt-8 sm:grid-cols-3">
        {[
          { href: "/map", label: "Map view", desc: "Spatial coverage across prefectures" },
          { href: "/sources", label: "Source registry", desc: "Municipal and regional feeds" },
          { href: "/methodology", label: "Methodology", desc: "How listings are classified" },
        ].map(({ href, label, desc }) => (
          <Link
            key={href}
            href={href}
            className="rounded-sm border border-stone-200 bg-white p-5 transition-colors hover:border-stone-300"
          >
            <p className="font-serif text-lg text-stone-900">{label}</p>
            <p className="mt-1 text-sm text-stone-500">{desc}</p>
          </Link>
        ))}
      </nav>
    </Container>
  );
}
