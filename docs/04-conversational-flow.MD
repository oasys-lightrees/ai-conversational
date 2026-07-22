# Prompt Design

## Purpose

This document defines how the Large Language Model (LLM) is used throughout the assessment process.

Instead of relying on a single prompt, the system separates responsibilities into multiple specialized prompts.

This approach improves maintainability, consistency, and debugging.

---

# Prompt Architecture

```text
                User Message
                     │
                     ▼
          Information Extraction
                     │
                     ▼
          Assessment State Update
                     │
                     ▼
         Missing Field Detection
                     │
                     ▼
       Next Question Generation
                     │
                     ▼
             AI Response
                     │
                     ▼
           Report Generation
```

---

# Prompt 1 — Information Extraction

## Objective

Extract structured business information from the user's response.

## Input

- User message
- Current assessment state

## Output

Structured JSON

Example

User

> Saya punya villa di Bali dengan 12 kamar.

Output

```json
{
  "property_type": "Villa",
  "location": "Bali",
  "total_units": 12
}
```

Responsibilities

- Extract multiple fields
- Ignore conversational filler
- Normalize values
- Never invent missing information

---

# Prompt 2 — Missing Field Detection

## Objective

Determine which required fields are still incomplete.

Input

Current assessment JSON

Output

```json
{
    "missing_fields": [
        "occupancy_rate",
        "staff_count"
    ]
}
```

Responsibilities

- Validate required fields
- Ignore optional fields
- Detect incomplete assessment

---

# Prompt 3 — Next Question Generator

## Objective

Generate the most appropriate follow-up question.

Input

- Assessment State
- Missing Fields
- Conversation History

Output

Natural Indonesian question.

Example

> Saat ini rata-rata tingkat hunian properti Anda sekitar berapa persen?

Responsibilities

- Ask only one question
- Avoid duplicate questions
- Keep conversation natural
- Adapt to previous answers

---

# Prompt 4 — Report Generator

## Objective

Generate the final assessment report.

Input

Completed assessment.

Output

Business report containing

- Executive Summary
- Current Situation
- Key Challenges
- AI Readiness
- Recommended Solutions
- Expected Benefits
- Next Steps

---

# Prompt Flow

```text
User Message

↓

Information Extraction

↓

Update Assessment

↓

Missing Field Detection

↓

Question Generation

↓

Response

↓

Repeat

↓

Assessment Complete

↓

Report Generation
```

---

# Prompt Design Principles

## 1.

Never assume missing information.

---

## 2.

Extract as many fields as possible from one response.

---

## 3.

Ask one follow-up question at a time.

---

## 4.

Keep responses conversational.

---

## 5.

Never ask for completed information.

---

# Language

The AI communicates entirely in Bahasa Indonesia.

Internal field names remain in English.

Example

Conversation

> Berapa jumlah kamar yang tersedia?

Database

```json
{
    "total_units": 12
}
```

---

# Structured Output

Whenever possible, the LLM should return structured JSON instead of free text.

Benefits

- Easier validation
- Easier debugging
- Direct database integration
- Lower hallucination risk