# API Reference

All endpoints are served under `/api/v1`. Request/response bodies are JSON.
Types mirror `backend/schemas/`. Interactive docs are available at `/docs`.

**Auth:** public endpoints need none. Admin endpoints (`/admin/**`) require
`Authorization: Bearer <ADMIN_API_KEY>`; see
[`docs/14-configuration-and-operations.MD`](14-configuration-and-operations.MD).

---

## Health

### `GET /health`
Liveness probe. → `200 {"status": "ok"}`

---

## Assessment

### `POST /assessment/start`
Create a new assessment. Body is optional.

Request:
```json
{ "template_id": "uuid | null" }
```
- `template_id` omitted/null → the default template (or the built-in default
  config if none is seeded).

Response `201`:
```json
{ "assessment_id": "uuid", "status": "IN_PROGRESS", "message": "Assessment started." }
```
`404` if `template_id` is unknown.

### `GET /assessment/{assessment_id}`
Collected data so far.

Response `200`:
```json
{
  "assessment_id": "uuid",
  "status": "IN_PROGRESS | COMPLETED | ABANDONED",
  "completion_percentage": 0,
  "assessment_data": { "property_type": "VILLA", "occupancy_rate": 55.0 }
}
```
`assessment_data` is a flat map (enum values as strings, numbers as numbers,
dynamic/branch fields flattened in). `404` if unknown.

### `DELETE /assessment/{assessment_id}`
Hard-delete (cascades to data, conversation, report). → `204`; `404` if unknown.

---

## Chat

### `POST /chat`
Process one conversation turn using the assessment's snapshotted config.

Request:
```json
{ "assessment_id": "uuid", "message": "Saya punya villa di Bali" }
```
Response `200`:
```json
{ "reply": "Apa tahap bisnis properti Anda?", "completion_percentage": 67, "next_stage": "BUSINESS_STAGE" }
```
`next_stage` is a stage code (`PROPERTY_PROFILE`, `BUSINESS_STAGE`, `BRANCH`,
`OPERATIONS`, `TECHNOLOGY`, `PAIN_POINTS`, `GOALS`, `COMPLETE`). When the
required set is complete, the reply is a closing message and `next_stage` is
`COMPLETE`. `404` if the assessment is unknown.

> On model failure the turn degrades gracefully: extraction failure asks the
> user to rephrase (data untouched); question-generation failure keeps the
> extracted data and returns a generic reply.

---

## Conversation

### `GET /conversation/{assessment_id}`
Ordered transcript. → `200`:
```json
[ { "role": "USER", "message": "..." }, { "role": "ASSISTANT", "message": "..." } ]
```
`404` if the assessment is unknown.

---

## Report

### `POST /report/generate`
Generate (or regenerate — idempotent) the report for a `COMPLETED` assessment.

Request: `{ "assessment_id": "uuid" }`
Response `201`: `{ "report_id": "uuid", "status": "GENERATED" }`
`404` unknown assessment · `409` assessment not completed.

### `GET /report/{report_id}`
Response `200`:
```json
{
  "report_id": "uuid",
  "assessment_id": "uuid",
  "executive_summary": "...",
  "business_analysis": "...",
  "operational_analysis": "...",
  "technology_analysis": "...",
  "ai_readiness": "...",
  "recommendations_summary": "...",
  "next_steps": "...",
  "recommendations": [
    { "title": "AI Receptionist", "description": "...", "priority": "HIGH", "estimated_impact": "..." }
  ]
}
```
`assessment_id` lets the report page fetch the property summary. `404` if unknown.

---

## Templates (public)

Used by the landing-page template picker.

### `GET /templates`
→ `200` list of `{ id, name, description, language, is_default }`.

### `GET /templates/{template_id}`
→ `200` `{ id, name, description, is_default, config }` where `config` is a
`PipelineConfig` (see below). `404` if unknown.

---

## Admin (`/admin/**`, Bearer auth)

All routes require the admin bearer token: `401` on missing/wrong token, `503`
when `ADMIN_API_KEY` is unset (admin disabled).

### Templates

- `GET /admin/templates` → list of summaries.
- `POST /admin/templates` → create. Body: `TemplateWrite` (below). `201`;
  `422` invalid config; `409` duplicate name.
- `GET /admin/templates/{id}` → full detail (`404` unknown).
- `PUT /admin/templates/{id}` → update (`200`; `404`/`422`/`409`).
- `DELETE /admin/templates/{id}` → `204`; `404` unknown; `409` if referenced by
  assessments.
- `POST /admin/templates/{id}/clone` → `201` new copy.
- `POST /admin/templates/{id}/default` → `200` set as the default.

`TemplateWrite`:
```json
{ "name": "…", "description": "… | null", "is_default": false, "config": { PipelineConfig } }
```

### Assessments

- `GET /admin/assessments?status=&template_id=&page=1&page_size=20` → paginated:
  ```json
  { "items": [ { "assessment_id", "status", "completion_percentage", "template_id", "created_at", "completed_at" } ],
    "total": 0, "page": 1, "page_size": 20 }
  ```
- `GET /admin/assessments/{id}` → detail: assessment fields + `assessment_data`
  + `conversation` + `report` (or null). `404` if unknown.
- `DELETE /admin/assessments/{id}` → `204`; `404` if unknown.

### Metrics

- `GET /admin/metrics` →
  ```json
  {
    "total_assessments": 0,
    "by_status": { "IN_PROGRESS": 0, "COMPLETED": 0, "ABANDONED": 0 },
    "reports_generated": 0,
    "completion_rate": 0.0,
    "average_completion": 0.0,
    "by_property_type": [ { "key": "VILLA", "count": 0 } ],
    "by_business_stage": [ { "key": "UNDERPERFORMING", "count": 0 } ],
    "recommendations_by_priority": { "HIGH": 0, "MEDIUM": 0, "LOW": 0 }
  }
  ```

---

## `PipelineConfig` shape

```json
{
  "knowledge": "domain context injected into prompts",
  "style": "LIA's persona/tone",
  "language": "id | en",
  "fields": [
    {
      "name": "property_type",
      "label": "Jenis Properti",
      "description": "extraction hint",
      "type": "string | integer | decimal | boolean | list | enum",
      "enum_options": ["VILLA", "HOTEL"],
      "aliases": ["location"],
      "required": true,
      "required_when": { "business_stage": ["UNDERPERFORMING"] },
      "section": "PROPERTY_PROFILE"
    }
  ]
}
```

Storage is hybrid: a field whose `name` matches an `AssessmentData` column is
stored there (typed); everything else goes to the dynamic JSON area. See
[`docs/11-pipeline-config.MD`](11-pipeline-config.MD).
