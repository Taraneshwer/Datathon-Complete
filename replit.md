# Crime Intelligence & Analytical Platform (CIPA)

Karnataka State Police / State Crime Records Bureau — a senior-product-designer-caliber intelligence platform for law enforcement analysts. 11 integrated modules with shared navigation, cross-module state, and a consistent mock data layer.

## Run & Operate

- `npm --workspace artifacts/crime-intel run dev` — run the frontend (auto-started via workflow)
- `npm --workspace artifacts/api-server run dev` — run the API server (auto-started via workflow)
- `npm run typecheck` — full typecheck across all packages
- `npm run build` — typecheck + build all packages
- `npm --workspace lib/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec

## Stack

- npm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React + Vite, Tailwind CSS (token-based design system), wouter routing, framer-motion
- Maps: react-leaflet + leaflet.heat (CartoDB Positron light tiles)
- Graph: react-force-graph-2d (light theme, hex colors in canvas — CSS vars don't resolve in canvas context)
- Charts: recharts (light theme tokens explicitly set)
- API: Express 5
- Codegen: Orval (OpenAPI → React Query hooks + Zod schemas)

## Where things live

- `artifacts/crime-intel/src/` — frontend React app
  - `src/context/IntelContext.tsx` — shared cross-module state (selectedDistrictId, selectedCaseId, selectedPatternId, timeOfDayFilter)
  - `src/mockData/` — single shared mock dataset (districts, cases, suspects, victims, hotspots, graph nodes/edges, patterns, alerts, evidence, timelines)
  - `src/api/` — fetch layer (swap real endpoints here, no component changes needed)
  - `src/pages/` — one file per module route
  - `src/components/` — shared components (CaseIdLink, Skeleton, Motion, StatusPill)
- `artifacts/api-server/src/` — Express API server
  - `src/mockData.ts` — canonical Karnataka mock data (8 districts, 14 cases, 12 suspects, 8 victims, 30 hotspots, 18 graph nodes, 6 patterns, 10 alerts…)
  - `src/routes/` — one file per domain (districts, cases, suspects, graph, patterns, analytics, alerts, evidence, bias, trust)
- `lib/api-spec/openapi.yaml` — OpenAPI contract (source of truth)
- `lib/api-client-react/src/generated/` — generated React Query hooks (do not hand-edit)
- `lib/api-zod/src/generated/` — generated Zod schemas (do not hand-edit)

## Architecture decisions

- **Light theme only** — no dark mode. react-force-graph-2d uses explicit hex values (not CSS vars) in canvas drawing callbacks — CSS custom properties don't resolve in canvas `fillStyle`/`strokeStyle`.
- **Single mock dataset** — `artifacts/api-server/src/mockData.ts` is the canonical source. All IDs (case IDs, suspect IDs, district IDs) are consistent across every module. The frontend's `src/api/` fetch layer wraps the API client hooks so swapping in real endpoints requires zero component changes.
- **Cross-module IntelContext** — selecting a district on the Hotspot Map propagates to the Knowledge Graph, Dashboard, and Pattern Matching via a single React context. The 300ms highlight pulse makes the causality visible.
- **OpenAPI-first** — spec gates codegen which gates the frontend. All API shapes are defined in `lib/api-spec/openapi.yaml`. After spec changes, run codegen before touching component code.
- **Canvas colors = hex** — any third-party library rendering to a canvas (react-force-graph-2d) must receive resolved hex values, not CSS variable strings.

## Product — 11 Modules

### INTELLIGENCE
- **Analytics Dashboard** (`/dashboard`) — recharts trend line + historical average, anomaly stat cards, risk forecast strip, active cases table
- **Hotspot Map** (`/hotspot-map`) — react-leaflet CartoDB Positron, leaflet.heat, time-of-day scrubber, district drill-down, anomaly pulse animation (the only sustained animation in the product), blind-spot overlay
- **Pattern Matching** (`/patterns`) — MO cluster card grid, confidence scores (IBM Plex Mono), frequency sparklines, cross-filters Knowledge Graph
- **Early Warning** (`/early-warning`) — chronological alert feed, severity filter, risk forecast

### INVESTIGATION
- **Knowledge Graph** (`/knowledge-graph`) — react-force-graph-2d, 4 node types (suspect/victim/location/case), edge labels on hover, crime replay time scrubber, slide-in detail panel
- **Case Evidence & Timeline** (`/cases/:id`) — reached by clicking any case ID anywhere; vertical hairline timeline, evidence chips with confidence badges
- **Investigative Agent** (`/agent`) — Tier 3 static; chat-style panel, "Firewall active" badge
- **Blind-Spot Discovery** — overlay toggle on Hotspot Map, –accent-warning shading, plain-language "why flagged" tooltip

### TRUST & OVERSIGHT
- **Identity & Access** (`/trust`) — architecture diagram (Officer Login → DID Verification → Encrypted Record → Ledger Anchor), access log table
- **Bias Audit** (`/bias-audit`) — recharts bar chart, disparity callout with –accent-warning border, clinical tone

## User preferences

_Populate as needed._

## Gotchas

- **react-force-graph-2d canvas colors**: always use resolved hex values (e.g. `#1F3A5C`), never `var(--accent-focus)`. CSS variables don't parse in canvas rendering context.
- **Orval body schema naming**: component names must not match `<OperationIdPascal>Body` — causes TS2308 collision in `lib/api-zod`. Use entity-shaped names (`NoteInput`, not `CreateNoteBody`).
- **Codegen collision with path+query params**: if an operation has both path params and query params, Orval can generate `<OperationIdPascal>Params` in both `generated/api.ts` and `generated/types/`, causing TS2308. Collapse to query-param-only operations when possible.
- After each OpenAPI spec change, re-run codegen: `npm --workspace lib/api-spec run codegen`.
- API server uses esbuild (CJS bundle), not `tsc --emit`. Route handler functions must use `: void` return type or consistent return patterns to avoid TS7030.

## Pointers

- See the workspace package manifests for structure, TypeScript setup, and package details
- Canvas token values are defined in `artifacts/crime-intel/src/pages/KnowledgeGraph.tsx` → `TOKEN` const
- Mock data canonical source: `artifacts/api-server/src/mockData.ts`
