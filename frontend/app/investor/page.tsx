import { AppShell } from "@/components/layout/AppShell";
import { InvestorDashboard } from "@/components/investor/InvestorDashboard";

export const dynamic = "force-dynamic";

export default function InvestorPage() {
  return (
    <AppShell>
      <InvestorDashboard />
    </AppShell>
  );
}
