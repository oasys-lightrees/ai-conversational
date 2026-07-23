# Admin Dashboard — Design & Plan

## Purpose

Give operators a UI to **manage pipeline templates**, **browse assessments and
reports**, and **see basic analytics** — plus the **authentication** the app
currently lacks. The dashboard is the home for the template CRUD deferred in
`docs/11` and for operational visibility into the pipeline.

Grounded in the existing entities: `AssessmentTemplate`, `Assessment` (+ status,
`template_id`, `config_snapshot`, `completion_percentage`), `AssessmentData`,
`Conversation`, `Report`, `Recommendation`.

---

## Feature areas

### 1. Template management (highest value — realizes deferred CRUD)
- List templates (name, language, default flag, usage count).
- Create / edit / clone / delete; set the default; toggle language, knowledge,
  and style.
- **Field builder** — the complex part: add/remove/reorder `FieldSpec`s, set
  type, enum options, `required` / `required_when` (branch logic), and section.
- Validate on save (unique field names, enum options for enum types,
  `required_when` referencing real fields) — reject with 422.

### 2. Assessments browser
- Paginated list with filters: status (`IN_PROGRESS`/`COMPLETED`/`ABANDONED`),
  template, date range; columns for completion %, stage, created/completed.
- Detail view: collected data (`assessment_data`), full conversation transcript,
  and the generated report + recommendations.
- Actions: delete / mark abandoned; regenerate report.

### 3. Analytics (all computable from the current schema)
- Funnel: started → completed → report generated; completion rate.
- Counts by status; completion-% distribution; assessments over time.
- Breakdowns: by `property_type`, `business_stage`, per-template.
- Aggregates from JSONB: top `pain_points`, `business_goals`; recommendations by
  priority; time-to-complete (`completed_at − created_at`).

### 4. Authentication (prerequisite — none exists today)
The public assessment flow stays open; **only `/admin/**` and `/api/v1/admin/**`
are protected.** Auth model is an open decision (see below).

---

## Backend API (`/api/v1/admin/*`, auth-gated)

**Templates (CRUD — completes `docs/11`)**
- `GET /admin/templates` · `POST /admin/templates` · `GET/PUT/DELETE /admin/templates/{id}`
- `POST /admin/templates/{id}/clone` · `POST /admin/templates/{id}/default`

**Assessments**
- `GET /admin/assessments?status=&template_id=&page=&page_size=` (paginated)
- `GET /admin/assessments/{id}` (data + conversation + report in one payload)
- `DELETE /admin/assessments/{id}`

**Metrics**
- `GET /admin/metrics` (aggregate counts, funnel, breakdowns)

**Auth**
- `POST /admin/login` (if credential-based) or a token check middleware.

The public `GET /templates` / `GET /templates/{id}` stay for the assessment
flow; admin CRUD is additive.

---

## Frontend (`/admin` route group in the existing Next app)

```text
app/admin/
  layout.tsx            # sidebar nav + auth guard
  page.tsx              # overview / metrics
  templates/page.tsx    # list
  templates/new/page.tsx
  templates/[id]/page.tsx   # edit + field builder
  assessments/page.tsx      # list + filters
  assessments/[id]/page.tsx # detail (data + transcript + report)
  login/page.tsx
components/admin/
  Sidebar, MetricCard, TemplateForm, FieldBuilder, AssessmentTable, ...
lib/adminApi.ts          # typed admin client (sends auth header)
```

Reuses the existing atoms/brand palette; charts can start as simple stat cards +
bars (no new chart dep needed for v1).

---

## Auth options (decision required)

| Option | What | Trade-off |
|--------|------|-----------|
| **A. Shared admin key** | `ADMIN_API_KEY` env; UI stores it, sends `Authorization: Bearer`; middleware checks | Simplest; no user table; fine for a single operator. No per-user audit. |
| **B. Admin user + JWT** | `AdminUser` table (hashed password), `POST /admin/login` issues a JWT | Real login, multiple users, revocable; more infra (hashing, token lib, expiry). |
| **C. Basic auth** | env username/password via HTTP Basic | Trivial; browser-native prompt; weakest UX/security. |

Recommendation: **A** for a fast, credible v1 (one operator), with **B** as the
upgrade path when multiple admins/audit are needed.

---

## Phase plan

| Phase | Deliverable | Exit criteria |
|-------|-------------|---------------|
| **A0** | Auth: chosen model + `/admin/**` gating (backend middleware + frontend guard) | unauthenticated admin calls → 401; login flow works |
| **A1** | Template CRUD API + validation | create/edit/clone/delete/default; 422 on invalid config |
| **A2** | Template management UI (list + form + **field builder**) | operator builds/edits a template end-to-end; it appears in `/assessment/start` |
| **A3** | Assessments browser (list + filters + detail) | view data, transcript, report for any assessment |
| **A4** | Metrics endpoint + overview page | funnel + breakdowns render from live data |

Each phase: backend tests (auth gating, CRUD validation, metrics math) + a
browser check of the UI.

---

## Risks & open questions

- **R1 — Editing a template vs snapshots.** Assessments snapshot config at start
  (`docs/11`), so editing a template does **not** change in-flight assessments —
  correct, but the UI should show that (e.g. "used by N assessments; edits apply
  to new ones only"). Consider template versioning later.
- **R2 — Deleting a template** referenced by assessments (`template_id` FK).
  Options: block delete if referenced, soft-delete (`is_active=false`), or null
  the FK. Proposal: soft-delete/deactivate.
- **R3 — Field builder validation** is the riskiest UI; mirror the backend
  validation client-side and always re-validate server-side.
- **R4 — Metrics cost.** Aggregates over JSONB (`pain_points`, etc.) are fine at
  MVP volume; add indexes/materialization only if needed.
- **Open:** auth model (A/B/C)? Is v1 scope **template management only**, or the
  full set (templates + assessments + metrics)?
