"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Container, cn } from "@tsubo/ui";
import type { ReactNode } from "react";

const ADMIN_NAV: {
  href: string;
  label: string;
  exact?: boolean;
  stub?: boolean;
}[] = [
  { href: "/admin", label: "Overview", exact: true },
  { href: "/admin/coverage", label: "Coverage" },
  { href: "/admin/sources", label: "Sources" },
  { href: "/admin/fx", label: "FX" },
  { href: "/admin/system", label: "System" },
  { href: "/admin/listings", label: "Listings", stub: true },
  { href: "/admin/ingest", label: "Ingest", stub: true },
  { href: "/admin/parsers", label: "Parsers", stub: true },
  { href: "/admin/users", label: "Users", stub: true },
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-[calc(100vh-4rem)] border-t border-stone-200 bg-stone-100/50">
      <Container className="py-8">
        <div className="mb-8 flex items-baseline justify-between">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-stone-500">
              Administration
            </p>
            <h1 className="mt-1 font-serif text-2xl font-light text-stone-900">
              Control panel
            </h1>
          </div>
          <Link href="/" className="text-sm text-stone-500 hover:text-stone-800">
            ← Public site
          </Link>
        </div>

        <div className="flex flex-col gap-8 lg:flex-row">
          <nav
            className="flex shrink-0 flex-row flex-wrap gap-1 lg:w-48 lg:flex-col"
            aria-label="Admin navigation"
          >
            {ADMIN_NAV.map(({ href, label, exact, stub }) => {
              const active = exact
                ? pathname === href
                : pathname === href || pathname.startsWith(`${href}/`);
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "rounded-sm px-3 py-2 text-sm transition-colors",
                    active
                      ? "bg-white text-stone-900 shadow-sm"
                      : "text-stone-600 hover:bg-white/60 hover:text-stone-900",
                  )}
                >
                  {label}
                  {stub ? (
                    <span className="ml-1.5 font-mono text-[9px] uppercase text-stone-400">
                      stub
                    </span>
                  ) : null}
                </Link>
              );
            })}
          </nav>

          <div className="min-w-0 flex-1 rounded-sm border border-stone-200 bg-white p-6 shadow-sm">
            {children}
          </div>
        </div>
      </Container>
    </div>
  );
}
