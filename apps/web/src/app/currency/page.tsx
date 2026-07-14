"use client";

import { Container, PageHeader, Section } from "@tsubo/ui";
import { FxDisclosure } from "@/components/fx-disclosure";
import { useFxRate } from "@/lib/queries";

export default function CurrencyPage() {
  const { data: fx, isLoading } = useFxRate();

  return (
    <Container narrow className="py-12">
      <PageHeader
        eyebrow="Display conversion"
        title="Currency"
        subtitle="Exchange rates used for USD display. Source prices remain in their original denomination."
      />

      <FxDisclosure rate={fx ?? null} isLoading={isLoading} className="mb-10" />

      <Section title="Policy">
        <div className="space-y-4 text-sm leading-relaxed text-stone-700">
          <p>
            Tsubo displays prices in either Japanese yen or US dollars based on your preference.
            The conversion rate is fetched from the configured provider and cached with a stale
            indicator when the effective date exceeds 24 hours.
          </p>
          <p>
            Negotiable, undisclosed, and zero-price listings show their source label rather than
            a converted amount. Auction reserve prices and minimum bids are labeled accordingly.
          </p>
        </div>
      </Section>
    </Container>
  );
}
