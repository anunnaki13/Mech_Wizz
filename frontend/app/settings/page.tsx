import { AppShell } from "@/components/layout/AppShell";

export default function SettingsPage() {
  return (
    <AppShell>
      <section className="page-header">
        <div>
          <h2>Investor Case & Data Quality</h2>
          <p>This settings area is planned for a later phase alongside investor data quality workflows.</p>
        </div>
      </section>
      <div className="notice">Configuration controls are not available in Phase 1.</div>
    </AppShell>
  );
}
