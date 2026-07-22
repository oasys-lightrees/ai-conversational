# System Architecture

## Purpose

This document describes the high-level architecture of the AI Conversational Assessment Agent.

The system is designed using a modular architecture where each component has a single responsibility.

---

# High-Level Architecture

```text
                ┌──────────────────────┐
                │      Next.js UI      │
                └──────────┬───────────┘
                           │
                    HTTP / REST API
                           │
                           ▼
                ┌──────────────────────┐
                │       FastAPI        │
                └──────────┬───────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 Chat Service      Assessment Service   Report Service
        │                  │                  │
        └────────────┬─────┴──────────────────┘
                     │
                     ▼
            OpenAI GPT-5.5 API
                     │
                     ▼
              Structured JSON
                     │
                     ▼
              PostgreSQL Database
```

---

# Backend Modules

```text
backend/

├── routers/
│   └── chat.py
│
├── services/
│   ├── chat_service.py
│   ├── extraction_service.py
│   ├── assessment_service.py
│   ├── report_service.py
│   ├── state_service.py
│   └── openai_service.py
│
├── models/
│
├── schemas/
│
├── database/
│
└── main.py
```

---

# Module Responsibilities

## Chat Service

Responsible for:

- Receiving user messages
- Sending responses
- Coordinating the assessment flow

---

## Extraction Service

Responsible for:

- Calling GPT
- Extracting structured data
- Returning validated JSON

Input

User message

Output

Structured assessment fields

---

## Assessment Service

Responsible for:

- Updating assessment data
- Saving assessment progress
- Validating required fields

---

## State Service

Responsible for:

- Tracking current conversation stage
- Identifying missing fields
- Preventing duplicate questions

---

## Report Service

Responsible for:

- Generating the final business assessment
- Producing recommendations
- Returning the final report

---

## OpenAI Service

Responsible for:

- Managing OpenAI API calls
- Prompt selection
- Response parsing
- Error handling

---

# Request Flow

```text
User Message

↓

POST /chat

↓

Chat Service

↓

Extraction Service

↓

OpenAI

↓

Structured JSON

↓

Assessment Service

↓

Update Database

↓

State Service

↓

Determine Next Question

↓

OpenAI

↓

Natural Response

↓

Return to User
```

---

# Database

The system stores:

- Assessment
- Conversation History
- Assessment Progress
- Generated Reports

---

# External Services

- OpenAI GPT-5.5
- PostgreSQL

Future integrations

- WhatsApp
- CRM
- Email
- Property Management System

---

# Design Principles

The architecture follows these principles:

- Single Responsibility Principle
- Modular Services
- Stateless API
- Structured AI Outputs
- Database as Source of Truth
- AI for reasoning, Python for business logic

---

# Future Scalability

Future components may include:

- Authentication
- Dashboard
- Multi-user support
- Analytics
- CRM integration
- WhatsApp integration
- Voice interface