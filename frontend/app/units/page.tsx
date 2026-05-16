import { AppShell } from "@/components/layout/AppShell";
import { UnitWorkspace } from "@/components/units/UnitWorkspace";
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
      <UnitWorkspace initialPlants={plants} initialLoadError={loadError} />
    </AppShell>
  );
}
