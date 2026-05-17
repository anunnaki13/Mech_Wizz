import Link from "next/link";
import { ArrowRight, ClipboardCheck, FileSearch, Gauge, Target } from "lucide-react";

const workflowSteps = [
  {
    title: "Baca jawaban bisnis",
    module: "Pilot Decision",
    href: "/pilot-decision",
    cta: "Open Pilot Decision",
    icon: Target,
    body: "Lihat kandidat pilot yang direkomendasikan, status gate, blocker, dan action plan.",
  },
  {
    title: "Tutup bukti yang kurang",
    module: "Evidence",
    href: "/evidence",
    cta: "Update Evidence",
    icon: FileSearch,
    body: "Ubah status bukti dari missing/requested menjadi received atau verified setelah ada data pendukung.",
  },
  {
    title: "Bawa ke komite",
    module: "Validation Pack",
    href: "/validation-pack",
    cta: "Open Pack",
    icon: ClipboardCheck,
    body: "Review Top 3, checklist evidence, no-go trigger, pertanyaan komite, dan memo PDF.",
  },
  {
    title: "Jika perlu cek detail",
    module: "Map & Analysis",
    href: "/dashboard/map",
    cta: "Open Map",
    icon: Gauge,
    body: "Gunakan peta, shortlist, sensitivity, dan investor case sebagai drill-down, bukan langkah pertama.",
  },
];

export function WorkflowGuide() {
  return (
    <section className="card workflow-guide" aria-label="Guided operator workflow">
      <div className="section-title-row">
        <div>
          <h3>Alur Operasi Yang Disarankan</h3>
          <p>Mulai dari keputusan pilot, lalu tutup bukti yang membuat kandidat belum siap.</p>
        </div>
        <Link className="section-link" href="/pilot-decision" prefetch={false}>
          Mulai <ArrowRight size={14} aria-hidden="true" />
        </Link>
      </div>
      <div className="workflow-step-grid">
        {workflowSteps.map((step, index) => {
          const Icon = step.icon;
          return (
            <article className="workflow-step-card" key={step.module}>
              <div className="workflow-step-index">{index + 1}</div>
              <Icon size={18} aria-hidden="true" />
              <span>{step.module}</span>
              <strong>{step.title}</strong>
              <p>{step.body}</p>
              <Link href={step.href} prefetch={false}>
                {step.cta} <ArrowRight size={13} aria-hidden="true" />
              </Link>
            </article>
          );
        })}
      </div>
    </section>
  );
}
