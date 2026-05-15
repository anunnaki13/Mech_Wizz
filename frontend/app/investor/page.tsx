import { AppShell } from "@/components/layout/AppShell";

export default function InvestorPage() {
  return (
    <AppShell>
      <section className="page-header">
        <div>
          <h2>Investor Case & Data Quality</h2>
          <p>This capability is planned for a later phase. Phase 1 only exposes source data quality markers.</p>
        </div>
      </section>
      <div className="notice">Investor case outputs are not available in Phase 1.</div>
    </AppShell>
  );
}
