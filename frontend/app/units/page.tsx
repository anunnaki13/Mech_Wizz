import { AppShell } from "@/components/layout/AppShell";
import { UnitList } from "@/components/units/UnitList";
import { getPlants } from "@/lib/api";
import type { Plant } from "@/types/plant";

export const dynamic = "force-dynamic";

export default async function UnitsPage() {
  let plants: Plant[] = [];
  let loadError = false;

  try {
    plants = await getPlants();
  } catch {
    loadError = true;
  }

  return (
    <AppShell>
      <section className="page-header">
        <div>
          <h2>Units</h2>
          <p>Candidate power generation units with Phase 1 data quality markers.</p>
        </div>
      </section>
      {loadError ? <div className="notice">Backend data is not reachable.</div> : <UnitList plants={plants} />}
    </AppShell>
  );
}
