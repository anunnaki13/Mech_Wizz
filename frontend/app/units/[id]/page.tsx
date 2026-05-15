import Link from "next/link";

import { AppShell } from "@/components/layout/AppShell";
import { EmissionTestsSection } from "@/components/units/EmissionTestsSection";
import { getEmissionTests, getPlant } from "@/lib/api";
import type { EmissionTest } from "@/types/emission-test";
import type { Plant } from "@/types/plant";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

function formatNumber(value: number | null | undefined, suffix = "") {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}${suffix}`;
}

export default async function UnitDetailPage({ params }: PageProps) {
  const { id } = await params;
  let plant: Plant | null = null;
  let emissionTests: EmissionTest[] = [];
  let loadError = false;

  try {
    plant = await getPlant(id);
    emissionTests = await getEmissionTests(id);
  } catch {
    loadError = true;
  }

  return (
    <AppShell>
      <section className="page-header">
        <div>
          <h2>{plant ? `${plant.plant_name} ${plant.unit_name}` : "Unit Profile"}</h2>
          <p>Plant identity and stack inputs for Phase 1 unit data management.</p>
        </div>
        <Link className="button" href="/units">
          Units
        </Link>
      </section>

      {loadError || !plant ? (
        <div className="notice">Unit data is not reachable. Confirm the backend is running and the record exists.</div>
      ) : (
        <div className="section-stack">
          <section className="grid kpis">
            <div className="card">
              <div className="metric-label">Capacity</div>
              <div className="metric-value">{formatNumber(plant.capacity_mw, " MW")}</div>
            </div>
            <div className="card">
              <div className="metric-label">Fuel</div>
              <div className="metric-value">{plant.fuel_type ?? "Unknown"}</div>
            </div>
            <div className="card">
              <div className="metric-label">Location</div>
              <div className="metric-value">{plant.city ?? plant.province ?? "Unknown"}</div>
            </div>
            <div className="card">
              <div className="metric-label">Owner</div>
              <div className="metric-value">{plant.owner ?? "Unknown"}</div>
            </div>
          </section>

          <section className="card">
            <h3>Plant Record</h3>
            <div className="chip-row">
              <span className="chip">data_status: {plant.data_status}</span>
              <span className="chip">confidence_level: {plant.confidence_level}</span>
              <span className="chip">status: {plant.status ?? "unknown"}</span>
            </div>
          </section>

          <EmissionTestsSection plantId={plant.id} initialEmissionTests={emissionTests} />
        </div>
      )}
    </AppShell>
  );
}
