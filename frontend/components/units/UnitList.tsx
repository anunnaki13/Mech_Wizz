import Link from "next/link";

import type { Plant } from "@/types/plant";

function formatNumber(value: number | null, suffix = "") {
  if (value === null) {
    return "Unknown";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}${suffix}`;
}

export function UnitList({ plants }: { plants: Plant[] }) {
  if (plants.length === 0) {
    return <div className="notice">No units are available. Run the Tenayan seed command.</div>;
  }

  return (
    <div className="unit-list">
      {plants.map((plant) => (
        <article className="unit-row" key={plant.id}>
          <div>
            <strong>{plant.plant_name}</strong>
            <span className="muted">{plant.unit_name}</span>
          </div>
          <div>
            <span className="metric-label">Location</span>
            <div>{[plant.city, plant.province].filter(Boolean).join(", ") || "Unknown"}</div>
          </div>
          <div>
            <span className="metric-label">Capacity</span>
            <div>{formatNumber(plant.capacity_mw, " MW")}</div>
          </div>
          <div>
            <span className="metric-label">Fuel</span>
            <div>{plant.fuel_type ?? "Unknown"}</div>
          </div>
          <div>
            <span className="metric-label">Status</span>
            <div>{plant.status ?? "Unknown"}</div>
          </div>
          <div className="inline-actions">
            <span className="chip">{plant.data_status}</span>
            <span className="chip">confidence_level: {plant.confidence_level}</span>
            <Link className="button" href={`/units/${plant.id}`}>
              Open
            </Link>
          </div>
        </article>
      ))}
    </div>
  );
}
