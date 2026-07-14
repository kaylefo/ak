import { Suspense } from "react";
import { SearchPageClient } from "./search-client";

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="px-6 py-12 text-sm text-stone-500">Loading search…</div>}>
      <SearchPageClient />
    </Suspense>
  );
}
