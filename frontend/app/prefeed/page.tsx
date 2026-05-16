import { AppShell } from "@/components/layout/AppShell";
import { PreFeedWorkspace } from "@/components/prefeed/PreFeedWorkspace";

export const dynamic = "force-dynamic";

export default function PreFeedPage() {
  return (
    <AppShell>
      <PreFeedWorkspace />
    </AppShell>
  );
}
