import { EvidenceWorkspace } from "@/components/validation/EvidenceWorkspace";
import { AppShell } from "@/components/layout/AppShell";
import { getEvidenceWorkspace } from "@/lib/api";
import type { ValidationEvidenceWorkspace } from "@/types/validation-evidence";

export const dynamic = "force-dynamic";

export default async function EvidencePage() {
  let workspace: ValidationEvidenceWorkspace | null = null;
  let loadError = false;

  try {
    workspace = await getEvidenceWorkspace({ scheme: "align", limit: 3 });
  } catch {
    loadError = true;
  }

  return (
    <AppShell>
      <EvidenceWorkspace initialWorkspace={workspace} initialLoadError={loadError} />
    </AppShell>
  );
}
