"use client";

import type { FxRate } from "@tsubo/contracts";
import { Badge, cn } from "@tsubo/ui";

interface FxDisclosureProps {
  rate: FxRate | null;
  isLoading?: boolean;
  className?: string;
}

export function FxDisclosure({ rate, isLoading, className }: FxDisclosureProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          "rounded-sm border border-stone-200 bg-white px-4 py-3",
          className,
        )}
        aria-busy="true"
      >
        <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-stone-400">
          Exchange rate
        </p>
        <p className="mt-1 text-sm text-stone-500">Loading…</p>
      </div>
    );
  }

  if (!rate) {
    return (
      <div
        className={cn(
          "rounded-sm border border-stone-200 bg-white px-4 py-3",
          className,
        )}
      >
        <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-stone-400">
          Exchange rate
        </p>
        <p className="mt-1 text-sm text-stone-500">Rate unavailable</p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "rounded-sm border border-stone-200 bg-white px-4 py-3",
        className,
      )}
      aria-label="Foreign exchange disclosure"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-stone-400">
            Exchange rate
          </p>
          <p className="mt-1 font-serif text-lg text-stone-900">
            1 USD = {rate.rate.toLocaleString("en-US", { minimumFractionDigits: 2 })} JPY
          </p>
        </div>
        {rate.is_stale ? <Badge tone="warning">Stale</Badge> : null}
      </div>
      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-stone-500">
        <div>
          <dt className="inline font-mono uppercase tracking-wider">Effective</dt>
          <dd className="inline before:content-[':_']">{rate.effective_date}</dd>
        </div>
        <div>
          <dt className="inline font-mono uppercase tracking-wider">Provider</dt>
          <dd className="inline before:content-[':_']">{rate.provider}</dd>
        </div>
      </dl>
    </div>
  );
}
