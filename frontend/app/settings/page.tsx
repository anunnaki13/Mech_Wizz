import { AppShell } from "@/components/layout/AppShell";
import { SettingsWorkspace } from "@/components/settings/SettingsWorkspace";

export const dynamic = "force-dynamic";

export default function SettingsPage() {
  return (
    <AppShell>
      <SettingsWorkspace />
    </AppShell>
  );
}
