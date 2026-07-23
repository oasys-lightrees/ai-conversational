# Configurable Pipeline — Design & Plan

## Purpose

Today the AI pipeline is hardcoded: the extraction field set lives in
`field_mapping.py`, the required/branch rules in `state_service.py`, and the
prompt "knowledge" and "style" are string constants in `extraction_service.py`,
`chat_service.py`, and `report_service.py`.

This document plans making the pipeline **configuration-driven**, so three
things can be set per assessment without code changes:

- **Knowledge** — domain context injected into the prompts.
- **Style** — LIA's persona/tone (and the report's tone).
- **Data-to-extract** — the field schema: which fields, types, enum options,
  which are required (incl. conditional/branch requirements), and extraction
  hints.

Locked decisions (from review):

- **Storage: hybrid** — keep the existing typed columns for the known core
  fields; add a dynamic JSON area for config-defined *extra* fields.
- **Scope: per-assessment templates (DB)** — named templates; `start` selects
  one and its config is **snapshotted** onto the assessment.
- **Delivery: plan first** (this doc), then implement in phases.

---

## Concepts

```text
AssessmentTemplate (DB, versioned)      PipelineConfig (runtime object)
  name, version, language                 knowledge: str
  knowledge, style          ── snapshot ─▶ style: str
  fields: [FieldSpec]        at /start     language: "id"|"en"
  report_sections: [..]                    fields: [FieldSpec]
  is_active                                report_sections: [..]
        │
        ▼ chosen at start, copied onto:
Assessment.template_id + Assessment.config_snapshot (JSONB)
```

- **`AssessmentTemplate`** — the editable, versioned definition in the DB.
- **`PipelineConfig`** — the plain runtime object the services consume.
- **Snapshot** — at `POST /assessment/start`, the chosen template's config is
  copied onto the assessment (`config_snapshot`). In-flight assessments are
  therefore stable even if the template is later edited; the report uses the
  same snapshot the conversation used.

### `FieldSpec`

```text
FieldSpec
  name           # machine key, e.g. "occupancy_rate"
  label          # human label, e.g. "Tingkat Hunian"
  description    # extraction hint given to the model
  type           # string | integer | decimal | boolean | list | enum
  enum_options   # [str] when type == enum
  required       # bool (always-required)
  required_when  # {field: value} conditional requirement (branch logic)
  section        # grouping / conversation stage
  storage        # DERIVED: "column" if name matches a known ORM column, else "json"
```

`storage` is not authored — it is derived: a field whose `name` matches an
existing `AssessmentData` column is stored there (strong typing preserved);
everything else is stored in the dynamic JSON area.

---

## Hybrid storage model

`AssessmentData` keeps its typed columns for the known hospitality schema.
Two JSON areas hold the rest:

- `branch_data` (exists today) — sparse, stage-specific known fields.
- `extra_data` (new JSONB) — values for template-defined fields that have **no**
  column. Keyed by `FieldSpec.name`; validated/coerced at runtime from the spec.

The flattened `to_state_dict` already merges `branch_data`; it will also merge
`extra_data`, so `StateService` and the prompts see one flat `{field: value}`
map regardless of where a value physically lives.

---

## How config threads through the four stages

Each service is refactored to take a `PipelineConfig` (loaded from the
assessment's `config_snapshot`) instead of module-level constants.

| Stage | Today | Config-driven |
|-------|-------|---------------|
| **Extraction (P1)** | fixed field list + hardcoded system text | prompt built from `knowledge` + `style` + `fields` (labels, descriptions, enum options); allowed-keys filter + coercion derived from `fields` |
| **Mapping** | static `field_mapping` | `FieldMapper(config)` splits extracted dict into typed columns vs `extra_data`, coercing per `FieldSpec.type` |
| **State (P2, rules)** | hardcoded `REQUIRED_ALWAYS` / `BRANCH_REQUIRED` | required + `required_when` read from `fields` |
| **Question gen (P3)** | hardcoded persona text | prompt from `knowledge` + `style` + missing-field labels |
| **Report (P4)** | hardcoded analyst persona | prompt from `knowledge` + `style` + `report_sections` |

`OpenAIService` is unchanged — it stays the single choke point.

---

## Data model & API changes

**Models**
- `AssessmentTemplate` — `id, name, version, language, knowledge, style,
  fields (JSONB), report_sections (JSONB), is_active, created_at`.
- `Assessment` — add `template_id` (FK) and `config_snapshot` (JSONB).
- `AssessmentData` — add `extra_data` (JSONB).

**Schema recreate**: `init_db` uses `create_all`, so dev recreates the schema
(`docker compose down -v && python -m backend.database.init_db`); production
would need an Alembic migration (already flagged in `docs/10`).

**API**
- `GET /api/v1/templates` — list templates (id, name, version, language).
- `GET /api/v1/template/{id}` — full config.
- `POST /api/v1/template` — create/validate a template.
- `POST /api/v1/assessment/start` — accept optional `template_id`; default to
  the active default template.

**Default template** reproduces today's hospitality schema exactly, so with no
`template_id` the behavior is unchanged (backward compatible). This default is
also the regression oracle: the config-driven logic must yield the same fields,
required set, and completion math as the current hardcoded implementation.

---

## Phase plan

Refactor to config-driven **behind a default config first** (no behavior
change), then add DB templates + selection.

| Phase | Deliverable | Exit criteria |
|-------|-------------|---------------|
| **C0** | `PipelineConfig` + `FieldSpec` domain objects; a `DEFAULT_CONFIG` reproducing the current schema | tests assert DEFAULT_CONFIG's fields/required match today's constants |
| **C1** | `FieldMapper(config)` replacing `field_mapping`; add `extra_data`; hybrid split | round-trip tests: column fields → columns, extra fields → extra_data; coercion per type |
| **C2** | `StateService(config)` — required/branch/completion from `fields` | table-driven tests equal today's results under DEFAULT_CONFIG |
| **C3** | Config-built prompts for extraction / question / report | faked-model tests assert prompts contain knowledge, style, and field labels |
| **C4** | `AssessmentTemplate` model + `Assessment.template_id`/`config_snapshot`; seed default; snapshot at start | start snapshots config; services read from snapshot |
| **C5** | Template list/get/create endpoints; `start` accepts `template_id` | API tests; unknown template → 404; invalid template → 422 |
| **C6** | (optional) frontend template picker on the landing/start flow | user can choose a template before starting |

Backend regression suite (the current 67 tests) must stay green throughout,
running against DEFAULT_CONFIG.

---

## Risks & open questions

- **R1 — Report sections.** The `Report` model has fixed columns
  (`executive_summary`, …). If `report_sections` should be fully dynamic, the
  report needs JSON storage too. **Proposal:** keep report columns fixed in
  C0–C5; treat dynamic report sections as a later extension.
- **R2 — Dynamic enums.** Column-backed enums keep the ORM `Enum` types;
  JSON-backed enum fields validate against `FieldSpec.enum_options` and store
  the normalized string. Two coercion paths, one in `FieldMapper`.
- **R3 — Template validation.** `POST /template` must validate: unique field
  names, valid types, `enum_options` present for enum fields, and
  `required_when` referencing a real field. Reject with 422 otherwise.
- **R4 — Snapshot vs live.** Snapshot at start (chosen) keeps in-flight
  assessments stable and makes the report reproducible; the cost is that
  editing a template does not affect running assessments (templates are
  versioned instead).
- **R5 — Language.** `config.language` can drive prompt language, which is what
  makes LIA respond in English end-to-end (the limitation noted for the UI
  language toggle). A template can pin a language.
- **Open:** should `report_sections` be in scope for the first cut (R1)? Should
  templates be editable via API in v1, or seeded-only with CRUD later?
