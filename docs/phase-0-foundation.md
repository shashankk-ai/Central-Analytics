# Phase 0 — Foundation: completion record

## What was built

**Frontend** (`frontend/`) — React 18 + TypeScript + Vite, Tailwind CSS v4, shadcn/ui,
Framer Motion, Recharts, TanStack Query, Zustand, date-fns, react-router-dom.

- App shell: sidebar navigation (Overview + 5 pillars), header, glassmorphism
  background layer (`components/layout/`)
- Global filter bar: time period (presets + custom range), business vertical,
  product, supplier, customer — all wired to a Zustand store (`store/filterStore.ts`),
  persists across navigation (`components/filters/`)
- Drill-down panel state scaffolding (`store/drillDownStore.ts`) — breadcrumb
  path tracking, ready for Level 0 → 1 → 2 wiring once a pillar has live data
- Indian number formatting utilities (₹ Cr/L, days, %, direction arrows)
  (`lib/format.ts`)
- Design tokens matching the Scimplify brand palette (teal/navy/gold, status
  green/amber/red, glass surfaces) in light and dark mode (`index.css`)
- Overview page showing all 5 pillars with phase/status badges
- Placeholder pages for each pillar pending their data source specification

**Backend** (`backend/`) — Python + FastAPI, httpx, pandas, pydantic,
python-dotenv, APScheduler.

- `app/connectors/zoho.py` — Zoho Analytics OAuth 2.0 (refresh-token grant)
  connector: token exchange/caching, workspace connection verification,
  generic view-data fetch. Surfaces the exact HTTP error and fix on failure.
- `app/models/payment_terms.py` — Payment Terms Master lookup + unknown-term
  detection, plus `suggest_payable_days()` implementing the two parsing rules
  from the brief (standard "Net N" terms, two-step "X/Y Net Z" terms with the
  configurable early-pay rate, default 0.35)
- `app/calculators/ccc.py` — DPO / DSO / DIO / CCC calculation engine,
  implemented exactly to the formulas in the build brief
- `app/api/health.py` — `GET /health/zoho` connection check
- `app/api/filters.py` — `GET /filters/options` (returns empty until Phase 1
  data sources are wired)
- `config/settings.py` — typed settings loaded from `.env`

## Calculation audit

The CCC engine is unit-tested against hand-computed figures (`backend/tests/test_ccc_calculator.py`),
all passing:

| Test | Formula | Inputs | Expected | Result |
|---|---|---|---|---|
| Standard term | `payable_days = N` from "Net N" | "Net 30" | 30 | ✅ 30 |
| Two-step term | `0.35×discount_days + 0.65×base_days` | "2/10 Net 30" | 23.0 | ✅ 23.0 |
| DPO | `SUM(value×days)/SUM(value)`, unknown terms excluded + flagged | PO value ₹1L@Net30, ₹3L@Net60, ₹0.5L@Net90(unknown) | 52.5 days, 1 unknown term (₹50,000 affected) | ✅ 52.5 / ✅ flagged |
| DSO | `SUM(value×days_outstanding)/SUM(value)`, uncollected → as-of date | ₹2L collected in 30d, ₹1L uncollected at 50d | 36.67 days | ✅ 36.67 |
| DIO | `inventory / (COGS/days_in_period)` | ₹9L inventory, ₹27L COGS, 90-day period | 30 days | ✅ 30 |
| CCC | `DIO + DSO − DPO` | 30 + 36.67 − 52.5 | 14.17 days | ✅ 14.17 |

No live data has been connected yet — these figures are synthetic, chosen to
make the formula mechanics easy to verify by hand. Real DPO/DSO/DIO/CCC
numbers will only appear once the Phase 1 datasets below are wired in.

## Data quality issues found

None yet — no live Zoho Analytics connection has been established. The
`GET /health/zoho` endpoint currently returns:

```json
{"connected": false, "error": "Missing Zoho OAuth credentials. Set ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET and ZOHO_REFRESH_TOKEN in backend/.env (see backend/.env.example)."}
```

This is expected until `.env` is populated.

## What is intentionally NOT built yet

- Zoho OAuth credentials / `.env` values (waiting on you)
- Wiring the connector to actual PO / AR / inventory datasets — column names
  are unknown, so no calculation runs against real data yet
- Drill-down panel UI (Level 1/2 breakdowns) — needs live data to decompose
- Payment Terms Master data source and its add/edit UI
- The Overview Matrix (Phase 5) — design received (`scimplify_overview_matrix_v2_2.html`)
  but per the build brief this is built last, once all 4 pillars have live data

## Validate and confirm

Please review the app shell (screenshots below) and the calculation audit
above, then confirm before Phase 1 (CCC) data wiring begins.
