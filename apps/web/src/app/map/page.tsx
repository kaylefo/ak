"use client";

import { Container, PageHeader } from "@tsubo/ui";
import { CoverageMap } from "@/components/coverage-map";

export default function MapPage() {
  return (
    <Container className="py-12">
      <PageHeader
        eyebrow="Spatial index"
        title="Coverage map"
        subtitle="Geographic distribution of registry coverage. Overlay data pending API integration."
      />
      <CoverageMap className="h-[60vh]" />
    </Container>
  );
}
