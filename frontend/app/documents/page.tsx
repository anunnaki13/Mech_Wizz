import { AppShell } from "@/components/layout/AppShell";

export default function DocumentsPage() {
  return (
    <AppShell>
      <section className="page-header">
        <div>
          <h2>LLM & Document Intelligence</h2>
          <p>This capability is planned for a later phase after deterministic data foundations are in place.</p>
        </div>
      </section>
      <div className="notice">Document intelligence is not available in Phase 1.</div>
    </AppShell>
  );
}
