import { AppShell } from "@/components/layout/AppShell";
import { MapDashboard } from "@/components/dashboard/MapDashboard";

export const dynamic = "force-dynamic";

export default function DashboardMapPage() {
  return (
    <AppShell>
      <MapDashboard />
    </AppShell>
  );
}
