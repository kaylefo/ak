import { Container, PageHeader, Section } from "@tsubo/ui";

export default function MethodologyPage() {
  return (
    <Container narrow className="py-12">
      <PageHeader
        eyebrow="Classification"
        title="Methodology"
        subtitle="How Tsubo normalizes listings from heterogeneous municipal and regional sources."
      />

      <div className="space-y-10 text-sm leading-relaxed text-stone-700">
        <Section title="Coverage states">
          <p>
            Each administrative unit receives a coverage state reflecting the highest-quality
            data source available: direct municipal feeds, prefectural portals, regional akiya
            banks, or public asset programs. States such as{" "}
            <code className="font-mono text-xs">DIRECT_ACTIVE</code> indicate live inventory;
            <code className="font-mono text-xs"> PREFECTURAL_ONLY</code> indicates listings
            reachable only through prefecture-level aggregation.
          </p>
        </Section>

        <Section title="Listing normalization">
          <p>
            Raw source records are parsed into a canonical schema: transaction type, price kind,
            property class, condition category, and location precision. Machine translation is
            flagged when applied; human-reviewed translations take precedence.
          </p>
        </Section>

        <Section title="Location precision">
          <p>
            Coordinates are stored with an explicit precision level—from exact parcel to
            municipality centroid. Listings with withheld locations remain searchable by
            administrative unit but are excluded from map views requiring sub-municipal accuracy.
          </p>
        </Section>

        <Section title="Currency conversion">
          <p>
            USD equivalents are computed from the disclosed daily rate on the currency page.
            Original JPY amounts from sources are never altered; conversions are display-only.
          </p>
        </Section>
      </div>
    </Container>
  );
}
