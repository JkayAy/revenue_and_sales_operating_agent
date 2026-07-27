# Design System — PipelinePilot Dashboard

**Scope:** Rep and manager web app (`apps/dashboard`).

---

## 1. Brand tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--font-sans` | Inter, system-ui | Body, tables |
| `--font-mono` | JetBrains Mono, monospace | IDs, JSON, timestamps |
| `--color-primary` | `#2563EB` | Primary actions |
| `--color-primary-hover` | `#1D4ED8` | Hover |
| `--color-success` | `#059669` | Approved, synced |
| `--color-warning` | `#D97706` | Pending, shadow |
| `--color-danger` | `#DC2626` | Rejected, failed |
| `--color-muted` | `#64748B` | Secondary text |
| `--color-surface` | `#F8FAFC` | Page background |
| `--color-card` | `#FFFFFF` | Cards |
| `--radius-md` | `8px` | Cards, inputs |
| `--shadow-sm` | `0 1px 2px rgb(0 0 0 / 0.06)` | Cards |

Dark mode: optional v1.1 (`--color-surface: #0F172A`).

---

## 2. Typography

| Style | Size / weight |
|-------|----------------|
| Page title | 24px / 600 |
| Section title | 16px / 600 |
| Body | 14px / 400 |
| Caption | 12px / 400 muted |
| KPI value | 28px / 700 |

---

## 3. Components

### Button

- **Primary:** Approve, Save draft  
- **Secondary:** Edit, Back  
- **Ghost:** Reject (with confirm modal)  
- **Destructive:** Kill run (admin)  

Min height 36px; padding 0 14px; focus ring 2px primary.

### Lead table

Columns: Company, Contact, Status, Time in queue, Owner, Updated.  
Row click → detail drawer or `/leads/[id]`.

### Status badge

| Status | Color |
|--------|-------|
| `processing` | warning |
| `awaiting_approval` | primary |
| `approved` | success |
| `rejected` | muted |
| `disqualified` | muted |
| `failed` | danger |

### Agent stepper

Horizontal steps with check/spinner icons; failed step shows error tooltip.

### Source citation chip

Small pill: domain + link icon; max 3 visible + “+N more”.

### KPI stat card

Label, value, delta optional (v1.1).

---

## 4. Layout

- Max content width 1200px  
- Sidebar: Queue, Metrics, Settings (stub)  
- Mobile: stack sidebar into top nav (read-only OK for demo)  

---

## 5. Accessibility

- WCAG AA contrast on primary buttons  
- Focus visible on all interactive elements  
- Status not color-only (icon + label)  
