"use client";

import { PageHeader } from "@tsubo/ui";
import { FxDisclosure } from "@/components/fx-disclosure";
import { useFxRate } from "@/lib/queries";

export default function AdminFxPage() {
  const { data: fx, isLoading } = useFxRate();

  return (
    <>
      <PageHeader
        title="FX administration"
        subtitle="Current exchange rate configuration and provider settings."
      />
      <FxDisclosure rate={fx ?? null} isLoading={isLoading} className="mb-6 max-w-md" />
      <p className="text-sm text-stone-500">
        Provider override and manual rate entry will be available in a future release.
      </p>
    </>
  );
}
