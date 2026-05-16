"use client";

import type { GeoJSONSource, Map, StyleSpecification } from "maplibre-gl";
import { useEffect, useRef } from "react";

import type {
  EconomicZoneGeoJSON,
  ExportCorridorGeoJSON,
  PortGeoJSON,
  UnitOpportunityGeoJSON,
} from "@/types/scoring";

type OpportunityMapProps = {
  geojson: UnitOpportunityGeoJSON;
  portsGeoJSON: PortGeoJSON;
  economicZonesGeoJSON: EconomicZoneGeoJSON;
  exportCorridorsGeoJSON: ExportCorridorGeoJSON;
  selectedPlantId: string;
  showHeatmap: boolean;
  showMarkers: boolean;
  showLabels: boolean;
  showEconomicZones: boolean;
  showPorts: boolean;
  showExportCorridors: boolean;
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

const emptyPortGeoJSON: PortGeoJSON = {
  type: "FeatureCollection",
  features: [],
};

const emptyEconomicZoneGeoJSON: EconomicZoneGeoJSON = {
  type: "FeatureCollection",
  features: [],
};

const emptyExportCorridorGeoJSON: ExportCorridorGeoJSON = {
  type: "FeatureCollection",
  features: [],
};

function setLayerVisibility(map: Map, layerId: string, visible: boolean) {
  if (map.getLayer(layerId)) {
    map.setLayoutProperty(layerId, "visibility", visible ? "visible" : "none");
  }
}

function escapeHtml(value: unknown) {
  return String(value ?? "Not available")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatPopupNumber(value: unknown, suffix = "") {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "Not available";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 1, notation: "compact" })}${suffix}`;
}

function popupHtml(title: unknown, rows: Array<[string, unknown]>, note?: string) {
  const contentRows = rows
    .map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`)
    .join("");
  return `
    <div class="map-popup">
      <h4>${escapeHtml(title)}</h4>
      ${contentRows}
      ${note ? `<p>${escapeHtml(note)}</p>` : ""}
    </div>
  `;
}

function fitToUnitBounds(map: Map, geojson: UnitOpportunityGeoJSON) {
  if (geojson.features.length === 0) {
    return;
  }
  const coordinates = geojson.features.map((feature) => feature.geometry.coordinates);
  const lngValues = coordinates.map(([lng]) => lng);
  const latValues = coordinates.map(([, lat]) => lat);
  const bounds: [[number, number], [number, number]] = [
    [Math.min(...lngValues), Math.min(...latValues)],
    [Math.max(...lngValues), Math.max(...latValues)],
  ];
  map.fitBounds(bounds, { maxZoom: 8, padding: 70, duration: 700 });
}

export function OpportunityMap({
  economicZonesGeoJSON,
  exportCorridorsGeoJSON,
  geojson,
  loading,
  portsGeoJSON,
  selectedPlantId,
  showEconomicZones,
  showExportCorridors,
  showHeatmap,
  showLabels,
  showMarkers,
  showPorts,
  onSelectUnit,
}: OpportunityMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const loadedRef = useRef(false);
  const onSelectRef = useRef(onSelectUnit);
  const geojsonRef = useRef<UnitOpportunityGeoJSON>(geojson);
  const portsRef = useRef<PortGeoJSON>(portsGeoJSON);
  const zonesRef = useRef<EconomicZoneGeoJSON>(economicZonesGeoJSON);
  const corridorsRef = useRef<ExportCorridorGeoJSON>(exportCorridorsGeoJSON);

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
        map.addSource("economic-zones", {
          type: "geojson",
          data: emptyEconomicZoneGeoJSON as never,
        });
        map.addSource("export-corridors", {
          type: "geojson",
          data: emptyExportCorridorGeoJSON as never,
        });
        map.addSource("unit-opportunity", {
          type: "geojson",
          data: emptyGeoJSON as never,
        });
        map.addSource("ports", {
          type: "geojson",
          data: emptyPortGeoJSON as never,
        });

        map.addLayer({
          id: "economic-zones-fill",
          type: "circle",
          source: "economic-zones",
          paint: {
            "circle-radius": [
              "interpolate",
              ["linear"],
              ["get", "zone_radius"],
              20,
              20,
              100,
              92,
            ],
            "circle-color": [
              "match",
              ["get", "economic_label"],
              "highest",
              "#ff3d57",
              "high",
              "#ff9f1c",
              "medium",
              "#ffd166",
              "#06d6a0",
            ],
            "circle-opacity": ["interpolate", ["linear"], ["zoom"], 3, 0.34, 8, 0.16],
            "circle-blur": 0.25,
            "circle-stroke-color": "rgba(255,255,255,0.22)",
            "circle-stroke-width": 1,
          },
        });

        map.addLayer({
          id: "economic-zones-core",
          type: "circle",
          source: "economic-zones",
          paint: {
            "circle-radius": [
              "interpolate",
              ["linear"],
              ["get", "economic_score"],
              0.25,
              4,
              1,
              13,
            ],
            "circle-color": [
              "interpolate",
              ["linear"],
              ["get", "economic_score"],
              0.2,
              "#0ea5a3",
              0.55,
              "#f6c85f",
              0.75,
              "#fb923c",
              1,
              "#f43f5e",
            ],
            "circle-stroke-color": "#fff7ed",
            "circle-stroke-width": 1.4,
            "circle-opacity": 0.95,
          },
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
          id: "export-corridors",
          type: "line",
          source: "export-corridors",
          paint: {
            "line-color": [
              "interpolate",
              ["linear"],
              ["get", "economic_score"],
              0.35,
              "#38bdf8",
              0.65,
              "#f6c85f",
              1,
              "#ff3d57",
            ],
            "line-width": [
              "interpolate",
              ["linear"],
              ["get", "economic_score"],
              0.35,
              1.8,
              1,
              4.4,
            ],
            "line-opacity": 0.82,
            "line-dasharray": [1.2, 1.1],
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
          id: "ports-circles",
          type: "circle",
          source: "ports",
          paint: {
            "circle-radius": [
              "case",
              ["==", ["get", "is_export_target"], true],
              9,
              [
                "interpolate",
                ["linear"],
                ["get", "readiness_score"],
                0.25,
                3,
                1,
                7,
              ],
            ],
            "circle-color": [
              "case",
              ["==", ["get", "country_name"], "Singapore"],
              "#f97316",
              [
                "interpolate",
                ["linear"],
                ["get", "readiness_score"],
                0.3,
                "#475569",
                0.6,
                "#38bdf8",
                0.85,
                "#22c55e",
              ],
            ],
            "circle-stroke-color": "#e8f2fb",
            "circle-stroke-width": ["case", ["==", ["get", "is_export_target"], true], 2.2, 1],
            "circle-opacity": 0.92,
          },
        });

        map.addLayer({
          id: "economic-zones-labels",
          type: "symbol",
          source: "economic-zones",
          minzoom: 4,
          layout: {
            "text-field": ["concat", ["get", "nearest_port_name"], " ", ["get", "economic_label"]],
            "text-size": 11,
            "text-offset": [0, -1.8],
            "text-anchor": "bottom",
            "text-allow-overlap": false,
          },
          paint: {
            "text-color": "#fff7ed",
            "text-halo-color": "#07111f",
            "text-halo-width": 1.2,
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

        map.addLayer({
          id: "ports-labels",
          type: "symbol",
          source: "ports",
          minzoom: 5,
          layout: {
            "text-field": ["get", "port_name"],
            "text-size": 10.5,
            "text-offset": [0, 1.1],
            "text-anchor": "top",
            "text-allow-overlap": false,
          },
          paint: {
            "text-color": "#dbeafe",
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
          const properties = feature?.properties as Record<string, unknown> | undefined;
          const coordinates = feature?.geometry.type === "Point" ? (feature.geometry.coordinates as [number, number]) : null;
          if (properties && coordinates) {
            new maplibregl.Popup({ closeButton: true, closeOnClick: true, maxWidth: "320px" })
              .setLngLat(coordinates)
              .setHTML(
                popupHtml(`${properties.site_name} ${properties.unit_name}`, [
                  ["Economic value", properties.economic_value_label],
                  ["Methanol", formatPopupNumber(properties.methanol_tpy, " t/y")],
                  ["Nearest port", properties.nearest_port_name],
                  ["Port distance", formatPopupNumber(properties.nearest_port_distance_km, " km")],
                  ["Port readiness", properties.nearest_port_readiness_label],
                  ["Confidence", properties.data_confidence_label],
                ]),
              )
              .addTo(map);
          }
        });

        map.on("click", "economic-zones-core", (event) => {
          const feature = event.features?.[0];
          const properties = feature?.properties as Record<string, unknown> | undefined;
          const coordinates = feature?.geometry.type === "Point" ? (feature.geometry.coordinates as [number, number]) : null;
          if (!properties || !coordinates) {
            return;
          }
          new maplibregl.Popup({ closeButton: true, closeOnClick: true, maxWidth: "340px" })
            .setLngLat(coordinates)
            .setHTML(
              popupHtml(properties.zone_name, [
                ["Economic tier", properties.economic_label],
                ["Units", properties.unit_count],
                ["Methanol", formatPopupNumber(properties.methanol_tpy, " t/y")],
                ["CO2", formatPopupNumber(properties.co2_tpy, " t/y")],
                ["Nearest port", properties.nearest_port_name],
                ["Avg port distance", formatPopupNumber(properties.average_port_distance_km, " km")],
                ["Top unit", properties.top_unit],
              ]),
            )
            .addTo(map);
        });

        map.on("click", "ports-circles", (event) => {
          const feature = event.features?.[0];
          const properties = feature?.properties as Record<string, unknown> | undefined;
          const coordinates = feature?.geometry.type === "Point" ? (feature.geometry.coordinates as [number, number]) : null;
          if (!properties || !coordinates) {
            return;
          }
          new maplibregl.Popup({ closeButton: true, closeOnClick: true, maxWidth: "320px" })
            .setLngLat(coordinates)
            .setHTML(
              popupHtml(properties.port_name, [
                ["Country", properties.country_name],
                ["Readiness", properties.readiness_label],
                ["Max depth", formatPopupNumber(properties.max_depth_m, " m")],
                ["Harbor size", properties.harbor_size],
                ["Liquid bulk", properties.has_liquid_bulk],
                ["First entry", properties.first_port_of_entry],
              ]),
            )
            .addTo(map);
        });

        map.on("click", "export-corridors", (event) => {
          const feature = event.features?.[0];
          const properties = feature?.properties as Record<string, unknown> | undefined;
          if (!properties) {
            return;
          }
          new maplibregl.Popup({ closeButton: true, closeOnClick: true, maxWidth: "360px" })
            .setLngLat(event.lngLat)
            .setHTML(
              popupHtml(`${properties.source_port_name} to ${properties.target_port_name}`, [
                ["Zone", properties.zone_name],
                ["Methanol", formatPopupNumber(properties.methanol_tpy, " t/y")],
                ["Indicative distance", formatPopupNumber(properties.indicative_sea_distance_km, " km")],
                ["Route type", "Screening proxy"],
                ["Demand note", properties.demand_reference],
              ]),
            )
            .addTo(map);
        });

        for (const layerId of ["economic-zones-core", "ports-circles", "export-corridors"]) {
          map.on("mouseenter", layerId, () => {
            map.getCanvas().style.cursor = "pointer";
          });
          map.on("mouseleave", layerId, () => {
            map.getCanvas().style.cursor = "";
          });
        }

        (map.getSource("unit-opportunity") as GeoJSONSource | undefined)?.setData(geojsonRef.current as never);
        (map.getSource("ports") as GeoJSONSource | undefined)?.setData(portsRef.current as never);
        (map.getSource("economic-zones") as GeoJSONSource | undefined)?.setData(zonesRef.current as never);
        (map.getSource("export-corridors") as GeoJSONSource | undefined)?.setData(corridorsRef.current as never);
        fitToUnitBounds(map, geojsonRef.current);
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
    geojsonRef.current = geojson;
    portsRef.current = portsGeoJSON;
    zonesRef.current = economicZonesGeoJSON;
    corridorsRef.current = exportCorridorsGeoJSON;

    const map = mapRef.current;
    if (!map || !loadedRef.current) {
      return;
    }
    const source = map.getSource("unit-opportunity") as GeoJSONSource | undefined;
    source?.setData(geojson as never);
    (map.getSource("ports") as GeoJSONSource | undefined)?.setData(portsGeoJSON as never);
    (map.getSource("economic-zones") as GeoJSONSource | undefined)?.setData(economicZonesGeoJSON as never);
    (map.getSource("export-corridors") as GeoJSONSource | undefined)?.setData(exportCorridorsGeoJSON as never);

    fitToUnitBounds(map, geojson);
  }, [economicZonesGeoJSON, exportCorridorsGeoJSON, geojson, portsGeoJSON]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loadedRef.current) {
      return;
    }
    setLayerVisibility(map, "unit-opportunity-heatmap", showHeatmap);
    setLayerVisibility(map, "unit-opportunity-circles", showMarkers);
    setLayerVisibility(map, "unit-opportunity-labels", showLabels);
    setLayerVisibility(map, "economic-zones-fill", showEconomicZones);
    setLayerVisibility(map, "economic-zones-core", showEconomicZones);
    setLayerVisibility(map, "economic-zones-labels", showEconomicZones && showLabels);
    setLayerVisibility(map, "ports-circles", showPorts);
    setLayerVisibility(map, "ports-labels", showPorts && showLabels);
    setLayerVisibility(map, "export-corridors", showExportCorridors);
  }, [showEconomicZones, showExportCorridors, showHeatmap, showLabels, showMarkers, showPorts]);

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
    <section className="map-panel" aria-label="Port-aware unit opportunity map">
      <div className="map-panel-header">
        <div>
          <h3>Port-Aware Opportunity Map</h3>
          <span>
            {geojson.features.length} unit{geojson.features.length === 1 ? "" : "s"} ·{" "}
            {economicZonesGeoJSON.features.length} economic area
            {economicZonesGeoJSON.features.length === 1 ? "" : "s"} · {portsGeoJSON.features.length} WPI ports
          </span>
        </div>
        {loading ? <span className="chip">Loading</span> : <span className="chip">GEM + WPI</span>}
      </div>
      <div ref={containerRef} className="map-canvas" />
      <div className="map-legend" aria-label="Map legend">
        <span>
          <i className="legend-zone" />
          Economic area
        </span>
        <span>
          <i className="legend-port" />
          WPI port
        </span>
        <span>
          <i className="legend-route" />
          SG export proxy
        </span>
        <span>
          <i className="legend-unit" />
          Unit
        </span>
      </div>
      {geojson.features.length === 0 ? (
        <div className="map-empty-state">No coordinate-ready ranking records.</div>
      ) : null}
    </section>
  );
}
