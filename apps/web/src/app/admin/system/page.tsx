"use client";

import { Badge, PageHeader } from "@tsubo/ui";
import { useSystemHealth } from "@/lib/queries";

export default function AdminSystemPage() {
  const { data, isLoading, isError } = useSystemHealth();

  return (
    <>
      <PageHeader
        title="System health"
        subtitle="API, worker, and search infrastructure status."
      />

      {isLoading ? (
        <p className="text-sm text-stone-500">Checking system health…</p>
      ) : isError || !data ? (
        <p className="text-sm text-stone-500">Health endpoint unavailable.</p>
      ) : (
        <dl className="space-y-4">
          {(
            [
              ["API", data.api_status],
              ["Worker", data.worker_status],
              ["OpenSearch", data.opensearch_status],
            ] as const
          ).map(([label, status]) => (
            <div
              key={label}
              className="flex items-center justify-between border-b border-stone-100 pb-3"
            >
              <dt className="text-sm text-stone-700">{label}</dt>
              <dd>
                <Badge tone={status === "healthy" ? "success" : "warning"}>
                  {status}
                </Badge>
              </dd>
            </div>
          ))}
          <div className="flex items-center justify-between pt-2 text-sm text-stone-500">
            <span>Version</span>
            <span className="font-mono">{data.version}</span>
          </div>
          {data.last_ingest_at ? (
            <div className="flex items-center justify-between text-sm text-stone-500">
              <span>Last ingest</span>
              <span className="font-mono">{data.last_ingest_at}</span>
            </div>
          ) : null}
        </dl>
      )}
    </>
  );
}
