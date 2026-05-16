"use client";

import type { GeoJSONSource, Map, StyleSpecification } from "maplibre-gl";
import { useEffect, useRef } from "react";

import type { UnitOpportunityGeoJSON } from "@/types/scoring";

type OpportunityMapProps = {
  geojson: UnitOpportunityGeoJSON;
  selectedPlantId: string;
  showHeatmap: boolean;
  showMarkers: boolean;
  showLabels: boolean;
  loading: boolean;
  onSelectUnit: (plantId: string) => void;
};

const mapStyle = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "OpenStreetMap",
    },
  },
  layers: [
    {
      id: "background",
      type: "background",
      paint: {
        "background-color": "#07111f",
      },
    },
    {
      id: "osm",
      type: "raster",
      source: "osm",
      paint: {
        "raster-saturation": -0.6,
        "raster-brightness-min": 0.18,
        "raster-brightness-max": 0.72,
        "raster-contrast": 0.15,
      },
    },
  ],
};

const emptyGeoJSON: UnitOpportunityGeoJSON = {
  type: "FeatureCollection",
  features: [],
};

function setLayerVisibility(map: Map, layerId: string, visible: boolean) {
  if (map.getLayer(layerId)) {
    map.setLayoutProperty(layerId, "visibility", visible ? "visible" : "none");
  }
}

export function OpportunityMap({
  geojson,
  loading,
  selectedPlantId,
  showHeatmap,
  showLabels,
  showMarkers,
  onSelectUnit,
}: OpportunityMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const loadedRef = useRef(false);
  const onSelectRef = useRef(onSelectUnit);

  useEffect(() => {
    onSelectRef.current = onSelectUnit;
  }, [onSelectUnit]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return;
    }

    let disposed = false;

    void import("maplibre-gl").then((module) => {
      if (disposed || !containerRef.current || mapRef.current) {
        return;
      }

      const maplibregl = module.default;
      const map = new maplibregl.Map({
        attributionControl: false,
        center: [118, -2.5],
        container: containerRef.current,
        maxZoom: 12,
        minZoom: 3,
        style: mapStyle as StyleSpecification,
        zoom: 4,
      });
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
      map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");

      map.on("load", () => {
        loadedRef.current = true;
        map.addSource("unit-opportunity", {
          type: "geojson",
          data: emptyGeoJSON as never,
        });

        map.addLayer({
          id: "unit-opportunity-heatmap",
          type: "heatmap",
          source: "unit-opportunity",
          maxzoom: 9,
          paint: {
            "heatmap-weight": ["interpolate", ["linear"], ["get", "heatmap_weight"], 0, 0, 1, 1],
            "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 3, 0.7, 7, 1.8],
            "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 3, 18, 7, 45],
            "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 6, 0.85, 9, 0.35],
            "heatmap-color": [
              "interpolate",
              ["linear"],
              ["heatmap-density"],
              0,
              "rgba(0, 24, 64, 0)",
              0.2,
              "rgba(0, 180, 216, 0.45)",
              0.4,
              "rgba(0, 255, 200, 0.55)",
              0.6,
              "rgba(255, 214, 10, 0.65)",
              0.8,
              "rgba(255, 128, 0, 0.75)",
              1,
              "rgba(255, 61, 87, 0.9)",
            ],
          },
        });

        map.addLayer({
          id: "unit-opportunity-circles",
          type: "circle",
          source: "unit-opportunity",
          minzoom: 3,
          paint: {
            "circle-radius": [
              "interpolate",
              ["linear"],
              ["get", "composite_score"],
              0.2,
              6,
              1,
              16,
            ],
            "circle-color": [
              "interpolate",
              ["linear"],
              ["get", "composite_score"],
              0,
              "#1d4ed8",
              0.4,
              "#06b6d4",
              0.6,
              "#facc15",
              0.75,
              "#fb923c",
              1,
              "#f43f5e",
            ],
            "circle-stroke-color": [
              "case",
              ["==", ["get", "site_id"], selectedPlantId || ""],
              "#ffffff",
              "rgba(255,255,255,0.74)",
            ],
            "circle-stroke-width": ["case", ["==", ["get", "site_id"], selectedPlantId || ""], 3, 1.5],
            "circle-opacity": 0.95,
          },
        });

        map.addLayer({
          id: "unit-opportunity-labels",
          type: "symbol",
          source: "unit-opportunity",
          minzoom: 4,
          layout: {
            "text-field": ["concat", "#", ["to-string", ["get", "rank_position"]], " ", ["get", "site_name"]],
            "text-size": 12,
            "text-offset": [0, 1.4],
            "text-anchor": "top",
            "text-allow-overlap": false,
          },
          paint: {
            "text-color": "#e8f2fb",
            "text-halo-color": "#07111f",
            "text-halo-width": 1.2,
          },
        });

        map.on("mouseenter", "unit-opportunity-circles", () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", "unit-opportunity-circles", () => {
          map.getCanvas().style.cursor = "";
        });
        map.on("click", "unit-opportunity-circles", (event) => {
          const feature = event.features?.[0];
          const siteId = feature?.properties?.site_id;
          if (typeof siteId === "string") {
            onSelectRef.current(siteId);
          }
        });
      });

      mapRef.current = map;
    });

    return () => {
      disposed = true;
      mapRef.current?.remove();
      mapRef.current = null;
      loadedRef.current = false;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loadedRef.current) {
      return;
    }
    const source = map.getSource("unit-opportunity") as GeoJSONSource | undefined;
    source?.setData(geojson as never);

    if (geojson.features.length > 0) {
      const coordinates = geojson.features.map((feature) => feature.geometry.coordinates);
      const lngValues = coordinates.map(([lng]) => lng);
      const latValues = coordinates.map(([, lat]) => lat);
      const bounds: [[number, number], [number, number]] = [
        [Math.min(...lngValues), Math.min(...latValues)],
        [Math.max(...lngValues), Math.max(...latValues)],
      ];
      map.fitBounds(bounds, { maxZoom: 8, padding: 70, duration: 700 });
    }
  }, [geojson]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loadedRef.current) {
      return;
    }
    setLayerVisibility(map, "unit-opportunity-heatmap", showHeatmap);
    setLayerVisibility(map, "unit-opportunity-circles", showMarkers);
    setLayerVisibility(map, "unit-opportunity-labels", showLabels);
  }, [showHeatmap, showLabels, showMarkers]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loadedRef.current || !map.getLayer("unit-opportunity-circles")) {
      return;
    }
    map.setPaintProperty("unit-opportunity-circles", "circle-stroke-color", [
      "case",
      ["==", ["get", "site_id"], selectedPlantId || ""],
      "#ffffff",
      "rgba(255,255,255,0.74)",
    ]);
    map.setPaintProperty("unit-opportunity-circles", "circle-stroke-width", [
      "case",
      ["==", ["get", "site_id"], selectedPlantId || ""],
      3,
      1.5,
    ]);
  }, [selectedPlantId]);

  return (
    <section className="map-panel" aria-label="Unit opportunity heatmap">
      <div className="map-panel-header">
        <div>
          <h3>Opportunity Heatmap</h3>
          <span>{geojson.features.length} mapped unit{geojson.features.length === 1 ? "" : "s"}</span>
        </div>
        {loading ? <span className="chip">Loading</span> : <span className="chip">MapLibre</span>}
      </div>
      <div ref={containerRef} className="map-canvas" />
      {geojson.features.length === 0 ? (
        <div className="map-empty-state">No coordinate-ready ranking records.</div>
      ) : null}
    </section>
  );
}
