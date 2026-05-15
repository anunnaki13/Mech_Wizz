import { AppShell } from "@/components/layout/AppShell";
import { getPlants } from "@/lib/api";
import type { Plant } from "@/types/plant";

export const dynamic = "force-dynamic";

function formatNumber(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}${suffix}`;
}

export default async function DashboardPage() {
  let plants: Plant[] = [];
  let loadError = false;

  try {
    plants = await getPlants();
  } catch {
    loadError = true;
  }

  const primaryPlant = plants[0];

  return (
    <AppShell>
      <section className="page-header">
        <div>
          <h2>Unit Data Dashboard</h2>
          <p>Live Phase 1 input records for candidate PLN NP carbon-to-fuel pilot units.</p>
        </div>
        <div className="chip-row">
          <span className="chip">Backend API</span>
          <span className="chip">PostgreSQL-ready</span>
        </div>
      </section>

      {loadError ? (
        <div className="notice">Backend data is not reachable. Start the API and run the Tenayan seed command.</div>
      ) : null}

      <section className="grid kpis" aria-label="Unit summary metrics">
        <div className="card">
          <div className="metric-label">Candidate units</div>
          <div className="metric-value">{plants.length}</div>
        </div>
        <div className="card">
          <div className="metric-label">Primary capacity</div>
          <div className="metric-value">{formatNumber(primaryPlant?.capacity_mw, " MW")}</div>
        </div>
        <div className="card">
          <div className="metric-label">Fuel type</div>
          <div className="metric-value">{primaryPlant?.fuel_type ?? "Unknown"}</div>
        </div>
        <div className="card">
          <div className="metric-label">Owner</div>
          <div className="metric-value">{primaryPlant?.owner ?? "Unknown"}</div>
        </div>
      </section>

      <section className="grid two" style={{ marginTop: 16 }}>
        <div className="card">
          <h3>{primaryPlant ? `${primaryPlant.plant_name} ${primaryPlant.unit_name}` : "No unit seeded"}</h3>
          <div className="detail-list">
            <div className="detail-row">
              <span>Location</span>
              <span>{primaryPlant ? `${primaryPlant.city ?? "Unknown"}, ${primaryPlant.province ?? "Unknown"}` : "Unknown"}</span>
            </div>
            <div className="detail-row">
              <span>Capacity factor</span>
              <span>{formatNumber(primaryPlant?.capacity_factor ? primaryPlant.capacity_factor * 100 : null, "%")}</span>
            </div>
            <div className="detail-row">
              <span>Operating days</span>
              <span>{formatNumber(primaryPlant?.operating_days_per_year)}</span>
            </div>
            <div className="detail-row">
              <span>Status</span>
              <span>{primaryPlant?.status ?? "Unknown"}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Data Quality</h3>
          <div className="chip-row">
            <span className="chip">data_status: {primaryPlant?.data_status ?? "unknown"}</span>
            <span className="chip">confidence_level: {primaryPlant?.confidence_level ?? "unknown"}</span>
          </div>
          <p className="muted" style={{ marginTop: 16 }}>
            Simulation insights available after Phase 2
          </p>
        </div>
      </section>
    </AppShell>
  );
}
