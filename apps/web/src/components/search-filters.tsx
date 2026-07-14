"use client";

import type { SearchFilters as SearchFiltersType } from "@tsubo/contracts";
import { Button, Card } from "@tsubo/ui";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useState } from "react";

const TRANSACTION_TYPES = [
  { value: "", label: "Any transaction" },
  { value: "sale", label: "Sale" },
  { value: "rent", label: "Rent" },
  { value: "free_transfer", label: "Free transfer" },
  { value: "auction", label: "Auction" },
] as const;

const PROPERTY_TYPES = [
  { value: "", label: "Any property" },
  { value: "detached_house", label: "Detached house" },
  { value: "kominka", label: "Kominka" },
  { value: "vacant_land", label: "Vacant land" },
  { value: "apartment_unit", label: "Apartment" },
] as const;

export function SearchFilters({ initial }: { initial?: SearchFiltersType }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [q, setQ] = useState(initial?.q ?? searchParams.get("q") ?? "");
  const [prefecture, setPrefecture] = useState(
    initial?.prefecture ?? searchParams.get("prefecture") ?? "",
  );
  const [transactionType, setTransactionType] = useState(
    initial?.transaction_type ?? searchParams.get("transaction_type") ?? "",
  );
  const [propertyType, setPropertyType] = useState(
    initial?.property_type ?? searchParams.get("property_type") ?? "",
  );

  const applyFilters = useCallback(() => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (prefecture) params.set("prefecture", prefecture);
    if (transactionType) params.set("transaction_type", transactionType);
    if (propertyType) params.set("property_type", propertyType);
    const qs = params.toString();
    router.push(`/search${qs ? `?${qs}` : ""}`);
  }, [q, prefecture, transactionType, propertyType, router]);

  return (
    <Card variant="outline" className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <label className="block sm:col-span-2">
          <span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.15em] text-stone-500">
            Keywords
          </span>
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Prefecture, municipality, feature…"
            className="w-full rounded-sm border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 placeholder:text-stone-400 focus:border-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-500"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.15em] text-stone-500">
            Prefecture
          </span>
          <input
            type="text"
            value={prefecture}
            onChange={(e) => setPrefecture(e.target.value)}
            placeholder="e.g. nagano"
            className="w-full rounded-sm border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 placeholder:text-stone-400 focus:border-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-500"
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.15em] text-stone-500">
            Transaction
          </span>
          <select
            value={transactionType}
            onChange={(e) => setTransactionType(e.target.value)}
            className="w-full rounded-sm border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 focus:border-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-500"
          >
            {TRANSACTION_TYPES.map(({ value, label }) => (
              <option key={value || "any"} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>

        <label className="block sm:col-span-2">
          <span className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.15em] text-stone-500">
            Property type
          </span>
          <select
            value={propertyType}
            onChange={(e) => setPropertyType(e.target.value)}
            className="w-full rounded-sm border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 focus:border-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-500"
          >
            {PROPERTY_TYPES.map(({ value, label }) => (
              <option key={value || "any"} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="flex justify-end">
        <Button type="button" onClick={applyFilters}>
          Apply filters
        </Button>
      </div>
    </Card>
  );
}
