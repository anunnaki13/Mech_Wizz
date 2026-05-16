import { AppShell } from "@/components/layout/AppShell";
import { ScenarioWorkspace } from "@/components/scenarios/ScenarioWorkspace";

export const dynamic = "force-dynamic";

export default function ScenariosPage() {
  return (
    <AppShell>
      <section className="page-header">
        <div>
          <h2>Scenario Simulation Engine</h2>
          <p>Business scenario and financial assumption workspace for PLN NP carbon-to-fuel pilots.</p>
        </div>
      </section>
      <ScenarioWorkspace />
    </AppShell>
  );
}
