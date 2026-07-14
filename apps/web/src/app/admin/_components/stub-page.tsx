import { PageHeader } from "@tsubo/ui";

export default function AdminStubPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <>
      <PageHeader title={title} subtitle={description} />
      <p className="text-sm text-stone-500">This admin section is a stub awaiting implementation.</p>
    </>
  );
}
