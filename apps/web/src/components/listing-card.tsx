"use client";

import type { ListingSummary } from "@tsubo/contracts";
import { Badge, Card } from "@tsubo/ui";
import Link from "next/link";
import { useCurrency } from "@/lib/currency-context";

interface ListingCardProps {
  listing: ListingSummary;
}

export function ListingCard({ listing }: ListingCardProps) {
  const { formatPrice } = useCurrency();

  const location = [listing.municipality_name, listing.prefecture_name]
    .filter(Boolean)
    .join(", ");

  return (
    <Card className="group transition-shadow hover:shadow-md">
      <Link href={`/listing/${listing.slug}`} className="block space-y-3">
        <div className="flex items-start justify-between gap-3">
          <h3 className="font-serif text-lg font-light leading-snug text-stone-900 group-hover:text-stone-700">
            {listing.title}
          </h3>
          <Badge tone={listing.status === "AVAILABLE" ? "success" : "neutral"}>
            {listing.status.replace(/_/g, " ")}
          </Badge>
        </div>

        <p className="text-sm text-stone-500">{location || listing.prefecture_name}</p>

        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 border-t border-stone-100 pt-3">
          <p className="font-serif text-xl text-stone-900">
            {listing.price.display_label ??
              formatPrice(listing.price.amount_jpy, listing.price.amount_usd)}
          </p>
          <p className="font-mono text-xs uppercase tracking-wider text-stone-400">
            {listing.transaction_type.replace(/_/g, " ")} ·{" "}
            {listing.property_type.replace(/_/g, " ")}
          </p>
        </div>

        <div className="flex gap-4 text-xs text-stone-500">
          {listing.floor_area_sqm != null ? (
            <span>{listing.floor_area_sqm} m² floor</span>
          ) : null}
          {listing.land_area_sqm != null ? (
            <span>{listing.land_area_sqm} m² land</span>
          ) : null}
          {listing.built_year != null ? <span>Built {listing.built_year}</span> : null}
        </div>
      </Link>
    </Card>
  );
}
