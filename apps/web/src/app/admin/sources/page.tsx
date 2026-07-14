import { PageHeader } from "@tsubo/ui";

export default function AdminSourcesPage() {
  return (
    <>
      <PageHeader
        title="Source administration"
        subtitle="Monitor parser health, trigger syncs, and manage source metadata."
      />
      <p className="text-sm text-stone-500">
        Source sync controls and parser drift alerts will appear here once the ingest pipeline
        is connected.
      </p>
    </>
  );
}
