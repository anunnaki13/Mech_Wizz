import { AppShell } from "@/components/layout/AppShell";
import { SensitivityWorkspace } from "@/components/sensitivity/SensitivityWorkspace";

export const dynamic = "force-dynamic";

export default function SensitivityPage() {
  return (
    <AppShell>
      <SensitivityWorkspace />
    </AppShell>
  );
}
