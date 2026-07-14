"use client";

import type { ListingDetail } from "@tsubo/contracts";
import { Badge, Card, Section } from "@tsubo/ui";
import { useCurrency } from "@/lib/currency-context";

interface ListingDetailViewProps {
  listing: ListingDetail;
}

export function ListingDetailView({ listing }: ListingDetailViewProps) {
  return (
    <article className="space-y-8">
      <ListingHeader listing={listing} />
      <ListingPricing listing={listing} />
      <ListingLocation listing={listing} />
      <ListingDescription listing={listing} />
      <ListingSource listing={listing} />
    </article>
  );
}

function ListingHeader({ listing }: { listing: ListingDetail }) {
  return (
    <header>
      <div className="mb-3 flex flex-wrap gap-2">
        <Badge>{listing.property_type.replace(/_/g, " ")}</Badge>
        <Badge tone="info">{listing.transaction_type.replace(/_/g, " ")}</Badge>
        <Badge tone={listing.status === "AVAILABLE" ? "success" : "neutral"}>
          {listing.status.replace(/_/g, " ")}
        </Badge>
      </div>
      <h1 className="font-serif text-3xl font-light tracking-tight text-stone-900">
        {listing.title}
      </h1>
      {listing.title_ja ? (
        <p className="mt-2 text-sm text-stone-500">{listing.title_ja}</p>
      ) : null}
    </header>
  );
}

function ListingPricing({ listing }: { listing: ListingDetail }) {
  const { formatPrice } = useCurrency();

  return (
    <Section title="Pricing">
      <Card variant="muted">
        <p className="font-serif text-3xl font-light text-stone-900">
          {listing.price.display_label ??
            formatPrice(listing.price.amount_jpy, listing.price.amount_usd)}
        </p>
        <p className="mt-1 font-mono text-xs uppercase tracking-wider text-stone-500">
          {listing.price.price_kind.replace(/_/g, " ")}
        </p>
      </Card>
    </Section>
  );
}

function ListingLocation({ listing }: { listing: ListingDetail }) {
  return (
    <Section title="Location">
      <Card variant="outline" className="space-y-2 text-sm">
        {listing.address_display ? (
          <p className="text-stone-800">{listing.address_display}</p>
        ) : null}
        {listing.address_ja ? (
          <p className="text-stone-500">{listing.address_ja}</p>
        ) : null}
        <dl className="grid grid-cols-2 gap-3 pt-2 text-xs text-stone-500">
          <div>
            <dt className="font-mono uppercase tracking-wider">Prefecture</dt>
            <dd className="mt-0.5 text-stone-700">{listing.prefecture_name}</dd>
          </div>
          {listing.municipality_name ? (
            <div>
              <dt className="font-mono uppercase tracking-wider">Municipality</dt>
              <dd className="mt-0.5 text-stone-700">{listing.municipality_name}</dd>
            </div>
          ) : null}
          <div>
            <dt className="font-mono uppercase tracking-wider">Precision</dt>
            <dd className="mt-0.5 text-stone-700">
              {listing.location_precision.replace(/_/g, " ")}
            </dd>
          </div>
        </dl>
      </Card>
    </Section>
  );
}

function ListingDescription({ listing }: { listing: ListingDetail }) {
  if (!listing.description && !listing.description_ja) return null;

  return (
    <Section title="Description">
      <div className="prose-sm max-w-none space-y-3 text-sm leading-relaxed text-stone-700">
        {listing.description ? <p>{listing.description}</p> : null}
        {listing.description_ja ? (
          <p className="text-stone-500">{listing.description_ja}</p>
        ) : null}
      </div>
    </Section>
  );
}

function ListingSource({ listing }: { listing: ListingDetail }) {
  return (
    <Section title="Source">
      <Card variant="outline" className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-stone-800">{listing.source_name}</p>
          <p className="mt-0.5 font-mono text-xs text-stone-500">
            Coverage: {listing.coverage_state.replace(/_/g, " ")}
          </p>
        </div>
        {listing.source_url ? (
          <a
            href={listing.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 text-sm text-stone-600 underline-offset-2 hover:text-stone-900 hover:underline"
          >
            View original
          </a>
        ) : null}
      </Card>
    </Section>
  );
}
