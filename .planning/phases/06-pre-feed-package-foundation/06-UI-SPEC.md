---
phase: 6
slug: pre-feed-package-foundation
status: approved
shadcn_initialized: false
preset: none
created: 2026-05-16
---

# Phase 6 - UI Design Contract

> Visual and interaction contract for the `/prefeed` package foundation workspace.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | project-native React components |
| Icon library | lucide-react, only where icons improve tool/button scanability |
| Font | Arial, Helvetica, sans-serif |

---

## Spacing Scale

Declared values must stay aligned to the existing CSS scale.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Inline metadata gaps and icon/text gaps |
| sm | 8px | Compact field gaps, table cell secondary text |
| md | 16px | Form groups, card inner gaps |
| lg | 24px | Panel padding and workspace row gaps |
| xl | 32px | Major grid gaps |
| 2xl | 48px | Page-level vertical spacing only if needed |

Exceptions: none.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 12px | 700 | 1.35 |
| Panel heading | 16px | 700 | 1.35 |
| Page heading | 28px | 700 | 1.2 |
| Metric value | 24px | 700 | 1.2 |

Typography rules:

- Do not scale font size with viewport width.
- Letter spacing remains `0`.
- Use compact headings inside panels; reserve page-scale text for the page title only.
- Long package names, filenames, and source organizations must wrap instead of overflowing.

---

## Color

Use existing CSS custom properties unless a new semantic status color is required.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#07111f` / `var(--bg)` | Page background |
| Secondary (30%) | `#11243a` / `var(--panel)` | Panels, cards, controls |
| Soft surface | `#162b43` / `var(--panel-soft)` | Nested form rows, active table rows |
| Border | `#25435d` / `var(--border)` | Panel, input, and table boundaries |
| Text | `#e8f2fb` / `var(--text)` | Primary text |
| Muted | `#93a9bb` / `var(--muted)` | Supporting metadata |
| Accent | `#18c7c8` / `var(--cyan)` | Primary CTA, active package, selected document link |
| Positive | `#7ddf96` / `var(--green)` | Validated/high-confidence status only |
| Warning | `#f6c85f` / `var(--amber)` | Missing data, low-confidence, review-needed status |
| Destructive | `#ef6b6b` | Archive/destructive confirmation only |

Accent reserved for: primary save action, selected package row, active linked document, and critical focus rings. Do not use accent on every interactive element.

---

## Layout Contract

`/prefeed` must be an operational workspace, not a landing page.

Required layout:

1. Page header with title `Pre-FEED Package Foundation`, concise subtitle, and status notice area.
2. Top control band with plant selector, scenario selector, and package selector/create action.
3. Main two-column desktop layout:
   - Left/main column: package metadata form and linked documents table.
   - Right column: package confidence/gap summary and selected package details.
4. Mobile layout collapses to one column in this order: controls, package metadata, linked documents, warnings/detail.

Sizing:

- Control band should use CSS grid with responsive tracks and stable min widths.
- Tables should be horizontally contained by their panel and may scroll inside the panel if needed.
- No card-inside-card composition. Use panels as siblings.

---

## Required Components And States

### Package Controls

- Plant selector: populated from existing plant API.
- Scenario selector: populated from selected plant scenarios; optional package may exist without scenario.
- Package selector: shows package name, version, status, and confidence.
- Primary CTA: `Save Package`.
- Secondary CTA: `New Package`.
- Destructive/soft state action: `Archive Package`.

### Package Metadata Form

Fields:

- package_name
- package_status
- owner_name
- source_organization
- received_date
- version_label
- data_status
- confidence_level
- notes

Field behavior:

- Required fields must be visibly marked via label text or validation state, not by placeholder alone.
- Empty optional values render as `Not provided`.
- Save errors show backend detail when available.

### Linked Documents

Table columns:

- Document
- Role
- Extraction
- Uploaded
- Action

Document role options:

- vendor_proposal
- epc_estimate
- offtake_document
- mrv_document
- permit_document
- internal_note

Empty state heading: `No documents linked`
Empty state body: `Link uploaded documents from the repository to make this package auditable.`

### Package Warnings

Show rule-based warnings as a compact list with impact/priority labels.

Required warning examples:

- Missing owner
- Missing source organization
- Missing received date
- Missing version label
- No vendor proposal linked
- Low package confidence

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Page title | Pre-FEED Package Foundation |
| Page subtitle | Track package source, confidence, documents, and readiness before detailed costing. |
| Primary CTA | Save Package |
| Secondary CTA | New Package |
| Archive action | Archive Package |
| Empty package heading | No package selected |
| Empty package body | Create a Pre-FEED package for the selected plant and scenario. |
| Empty document heading | No documents linked |
| Empty document body | Link uploaded documents from the repository to make this package auditable. |
| Error state | Package data could not be loaded. Check the backend service and try again. |
| Destructive confirmation | Archive Package: this keeps history but removes the package from active selection. |

---

## Interaction Contract

- Loading state: disable save/archive/link actions and show a concise status message.
- Create flow: `New Package` clears package form while retaining selected plant/scenario.
- Save flow: successful save refreshes package list and selects the saved package.
- Archive flow: archive is a status update; archived package remains accessible only if backend returns archived records.
- Document link flow: user selects an existing document and assigns a role before saving the link.
- Package warnings refresh after save and after document link changes.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registry | none | blocked unless separately approved |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-05-16
