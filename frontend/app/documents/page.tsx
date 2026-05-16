import { AppShell } from "@/components/layout/AppShell";
import { DocumentWorkspace } from "@/components/documents/DocumentWorkspace";

export const dynamic = "force-dynamic";

export default function DocumentsPage() {
  return (
    <AppShell>
      <DocumentWorkspace />
    </AppShell>
  );
}
