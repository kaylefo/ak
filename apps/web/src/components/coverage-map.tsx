"use client";

import { useEffect, useRef } from "react";
import "maplibre-gl/dist/maplibre-gl.css";

interface CoverageMapProps {
  className?: string;
  center?: [number, number];
  zoom?: number;
}

export function CoverageMap({
  className,
  center = [138.0, 36.5],
  zoom = 4.5,
}: CoverageMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import("maplibre-gl").Map | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    let cancelled = false;

    async function initMap() {
      const maplibregl = await import("maplibre-gl");
      if (cancelled || !containerRef.current) return;

      const map = new maplibregl.Map({
        container: containerRef.current,
        style: {
          version: 8,
          sources: {
            osm: {
              type: "raster",
              tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
              tileSize: 256,
              attribution: "© OpenStreetMap contributors",
            },
          },
          layers: [
            {
              id: "osm",
              type: "raster",
              source: "osm",
            },
          ],
        },
        center,
        zoom,
      });

      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
      mapRef.current = map;
    }

    void initMap();

    return () => {
      cancelled = true;
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [center, zoom]);

  return (
    <div className={className}>
      <div
        ref={containerRef}
        className="h-full min-h-[320px] w-full rounded-sm border border-stone-200"
        role="img"
        aria-label="Coverage map of Japan"
      />
      <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.15em] text-stone-400">
        Coverage overlay — placeholder
      </p>
    </div>
  );
}
