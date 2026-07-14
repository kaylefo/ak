import { PageHeader, Stat } from "@tsubo/ui";
import Link from "next/link";

export default function AdminPage() {
  return (
    <>
      <PageHeader
        title="Overview"
        subtitle="Registry operations dashboard. Connect to the API for live metrics."
      />

      <div className="mb-8 grid gap-6 sm:grid-cols-3">
        <Stat label="Environment" value={process.env.NODE_ENV ?? "unknown"} />
        <Stat label="API" value={process.env.NEXT_PUBLIC_API_URL ?? "not set"} />
        <Stat label="Version" value="0.1.0" />
      </div>

      <nav className="grid gap-3 sm:grid-cols-2">
        {[
          { href: "/admin/coverage", label: "Manage coverage states" },
          { href: "/admin/sources", label: "Source health & sync" },
          { href: "/admin/fx", label: "Exchange rate configuration" },
          { href: "/admin/system", label: "System health & workers" },
        ].map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className="rounded-sm border border-stone-200 px-4 py-3 text-sm text-stone-700 hover:border-stone-300 hover:bg-stone-50"
          >
            {label} →
          </Link>
        ))}
      </nav>
    </>
  );
}
