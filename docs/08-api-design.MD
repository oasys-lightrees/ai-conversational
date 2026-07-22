# API Design

## Purpose

This document defines the REST API endpoints for the AI Conversational Assessment Agent.

The API is designed around business workflows rather than database CRUD operations.

---

# API Overview

```text
Frontend (Next.js)

        │

        ▼

     FastAPI

        │

        ▼

Business Services

        │

        ▼

OpenAI + PostgreSQL
```

---

# Assessment Flow

```text
Start Assessment

↓

Chat

↓

Chat

↓

Chat

↓

Assessment Complete

↓

Generate Report

↓

View Report
```

---

# Endpoints

## 1. Start Assessment

Creates a new assessment session.

### Endpoint

```http
POST /api/v1/assessment/start
```

### Request

```json
{}
```

### Response

```json
{
    "assessment_id": "uuid",
    "status": "IN_PROGRESS",
    "message": "Halo, saya LIA..."
}
```

---

## 2. Continue Conversation

Processes one conversation turn.

### Endpoint

```http
POST /api/v1/chat
```

### Request

```json
{
    "assessment_id": "uuid",
    "message": "Saya memiliki villa di Bali dengan 12 kamar."
}
```

### Response

```json
{
    "reply": "Baik, saya memahami bahwa Anda memiliki villa dengan 12 kamar. Saat ini bagaimana tingkat hunian properti tersebut?",
    "completion_percentage": 20,
    "next_stage": "business_performance"
}
```

---

## 3. Get Assessment

Returns all assessment data collected so far.

### Endpoint

```http
GET /api/v1/assessment/{assessment_id}
```

### Response

```json
{
    "assessment_id": "...",
    "status": "IN_PROGRESS",
    "completion_percentage": 45,
    "assessment_data": {}
}
```

---

## 4. Get Conversation History

Returns previous conversation.

### Endpoint

```http
GET /api/v1/conversation/{assessment_id}
```

### Response

```json
[
    {
        "role": "assistant",
        "message": "Halo..."
    },
    {
        "role": "user",
        "message": "Saya memiliki villa..."
    }
]
```

---

## 5. Generate Report

Generates the final assessment report.

Normally this endpoint is only called when all required fields have been completed.

### Endpoint

```http
POST /api/v1/report/generate
```

### Request

```json
{
    "assessment_id": "uuid"
}
```

### Response

```json
{
    "report_id": "uuid",
    "status": "GENERATED"
}
```

---

## 6. Get Report

Returns the generated assessment report.

### Endpoint

```http
GET /api/v1/report/{report_id}
```

### Response

```json
{
    "executive_summary": "...",
    "business_analysis": "...",
    "recommendations": []
}
```

---

## 7. Delete Assessment (Optional)

Deletes or archives an assessment.

### Endpoint

```http
DELETE /api/v1/assessment/{assessment_id}
```

---

# Response Format

Every API response follows the same structure.

```json
{
    "success": true,
    "message": "",
    "data": {}
}
```

Example

```json
{
    "success": true,
    "message": "Assessment updated successfully.",
    "data": {
        "completion_percentage": 60
    }
}
```

---

# Error Response

```json
{
    "success": false,
    "message": "Assessment not found.",
    "errors": []
}
```

---

# HTTP Status Codes

| Status | Description |
|----------|-------------|
| 200 | Success |
| 201 | Resource Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

# Authentication

MVP

Authentication is not implemented.

Future versions may use:

- JWT
- OAuth
- Clerk
- Auth0

---

# Future Endpoints

Possible future APIs include:

```http
POST /api/v1/upload

POST /api/v1/voice

POST /api/v1/recommendation/regenerate

GET /api/v1/dashboard

GET /api/v1/statistics

POST /api/v1/organization
```

---

# API Workflow

```text
Frontend

↓

POST /assessment/start

↓

Receive Assessment ID

↓

POST /chat

↓

FastAPI

↓

OpenAI Extraction

↓

Update Database

↓

Generate Next Question

↓

Return Response

↓

Repeat

↓

POST /report/generate

↓

GET /report/{id}

↓

Display Report
```

---

# API Design Principles

The API follows these principles:

- Business-oriented endpoints
- Stateless requests
- Consistent response format
- UUID-based resources
- Separation of concerns
- Backend manages assessment state
- Frontend remains presentation-focused