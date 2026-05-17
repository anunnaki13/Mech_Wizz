"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navGroups = [
  {
    label: "Decision",
    description: "Jawaban utama",
    items: [
      { label: "Dashboard", href: "/dashboard" },
      { label: "Pilot Decision", href: "/pilot-decision" },
      { label: "Evidence", href: "/evidence" },
      { label: "Validation Pack", href: "/validation-pack" },
    ],
  },
  {
    label: "Analysis",
    description: "Peta dan ekonomi",
    items: [
      { label: "Map", href: "/dashboard/map" },
      { label: "Shortlist", href: "/shortlist" },
      { label: "Sensitivity", href: "/sensitivity" },
      { label: "Investor", href: "/investor" },
    ],
  },
  {
    label: "Data & Admin",
    description: "Input lanjutan",
    items: [
      { label: "Units", href: "/units" },
      { label: "Scenarios", href: "/scenarios" },
      { label: "Pre-FEED", href: "/prefeed" },
      { label: "Documents", href: "/documents" },
      { label: "Settings", href: "/settings" },
    ],
  },
];

const workflowLinks = [
  { label: "1 Pilot Decision", href: "/pilot-decision" },
  { label: "2 Evidence", href: "/evidence" },
  { label: "3 Validation Pack", href: "/validation-pack" },
];

function isActivePath(pathname: string, href: string) {
  if (href === "/dashboard") {
    return pathname === "/dashboard" || pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">MW</div>
          <div className="brand-name">MECH WIZ AI Digital Twin</div>
          <div className="brand-subtitle">PLN NP feasibility cockpit</div>
        </div>
        <nav className="nav" aria-label="Primary">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              <div className="nav-group-title">
                <strong>{group.label}</strong>
                <span>{group.description}</span>
              </div>
              <div className="nav-group-links">
                {group.items.map((item) => {
                  const active = isActivePath(pathname, item.href);
                  return (
                    <Link
                      aria-current={active ? "page" : undefined}
                      className={active ? "active" : undefined}
                      href={item.href}
                      key={item.href}
                      prefetch={false}
                    >
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <h1>MECH WIZ Decision Cockpit</h1>
            <span>Alur utama: keputusan pilot, bukti, lalu validation pack</span>
          </div>
          <div className="topbar-flow" aria-label="Main workflow">
            {workflowLinks.map((item) => (
              <Link href={item.href} key={item.href} prefetch={false}>
                {item.label}
              </Link>
            ))}
          </div>
        </header>
        <div className="content">{children}</div>
      </main>
    </div>
  );
}
