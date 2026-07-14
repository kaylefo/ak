"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Container, cn } from "@tsubo/ui";
import { useCurrency } from "@/lib/currency-context";
import type { CurrencyCode } from "@tsubo/contracts";

const NAV_LINKS = [
  { href: "/search", label: "Search" },
  { href: "/map", label: "Map" },
  { href: "/coverage", label: "Coverage" },
  { href: "/sources", label: "Sources" },
  { href: "/methodology", label: "Methodology" },
] as const;

export function Header() {
  const pathname = usePathname();
  const { currency, setCurrency } = useCurrency();

  return (
    <header className="sticky top-0 z-50 border-b border-stone-200 bg-stone-50/90 backdrop-blur-sm">
      <Container>
        <div className="flex h-16 items-center justify-between gap-6">
          <div className="flex items-center gap-10">
            <Link href="/" className="group flex items-baseline gap-2">
              <span className="font-serif text-xl font-light tracking-tight text-stone-900">
                Tsubo
              </span>
              <span className="hidden font-mono text-[10px] uppercase tracking-[0.2em] text-stone-400 sm:inline">
                Registry
              </span>
            </Link>

            <nav className="hidden items-center gap-1 md:flex" aria-label="Main">
              {NAV_LINKS.map(({ href, label }) => {
                const active = pathname === href || pathname.startsWith(`${href}/`);
                return (
                  <Link
                    key={href}
                    href={href}
                    className={cn(
                      "rounded-sm px-3 py-1.5 text-sm transition-colors",
                      active
                        ? "bg-stone-200/60 text-stone-900"
                        : "text-stone-600 hover:bg-stone-100 hover:text-stone-900",
                    )}
                  >
                    {label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <CurrencySwitcher currency={currency} onChange={setCurrency} />
            <Link
              href="/compare"
              className="hidden text-sm text-stone-600 hover:text-stone-900 sm:inline"
            >
              Compare
            </Link>
          </div>
        </div>
      </Container>
    </header>
  );
}

function CurrencySwitcher({
  currency,
  onChange,
}: {
  currency: CurrencyCode;
  onChange: (c: CurrencyCode) => void;
}) {
  return (
    <div
      className="flex rounded-sm border border-stone-300 bg-white p-0.5"
      role="group"
      aria-label="Display currency"
    >
      {(["USD", "JPY"] as const).map((code) => (
        <button
          key={code}
          type="button"
          onClick={() => onChange(code)}
          className={cn(
            "rounded-sm px-2.5 py-1 font-mono text-xs transition-colors",
            currency === code
              ? "bg-stone-900 text-stone-50"
              : "text-stone-600 hover:text-stone-900",
          )}
          aria-pressed={currency === code}
        >
          {code}
        </button>
      ))}
    </div>
  );
}
