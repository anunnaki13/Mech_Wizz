import Link from "next/link";

const navItems = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Map", href: "/dashboard/map" },
  { label: "Shortlist", href: "/shortlist" },
  { label: "Units", href: "/units" },
  { label: "Scenarios", href: "/scenarios" },
  { label: "Investor", href: "/investor" },
  { label: "Pre-FEED", href: "/prefeed" },
  { label: "Sensitivity", href: "/sensitivity" },
  { label: "Documents", href: "/documents" },
  { label: "Settings", href: "/settings" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">MW</div>
          <div className="brand-name">MECH WIZ AI Digital Twin</div>
          <div className="brand-subtitle">PLN NP feasibility cockpit</div>
        </div>
        <nav className="nav" aria-label="Primary">
          {navItems.map((item) => (
            <Link href={item.href} key={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <h1>MECH WIZ Decision Cockpit</h1>
            <span>Strategy, simulation, and data quality</span>
          </div>
          <span>Pre-feasibility workspace</span>
        </header>
        <div className="content">{children}</div>
      </main>
    </div>
  );
}
