# Page Specification

## Purpose

This document defines every page of the AI Conversational Assessment Agent, including its purpose, route, components, user interactions, API integrations, and navigation.

---

# Application Flow

```text
Landing
    │
    ▼
Assessment Chat
    │
    ▼
Generating Report
    │
    ▼
Assessment Report
```

---

# Page 1 — Landing Page

## Route

```
/
```

## Purpose

Introduce the AI Conversational Assessment Agent and encourage users to begin an assessment.

---

## Components

- Navbar
- Hero Section
- Feature Cards
- Start Assessment Button
- Footer

---

## User Actions

- Click "Start Assessment"

---

## API Calls

None

---

## Navigation

```
Landing

↓

Assessment Chat
```

---

## Loading State

None

---

## Error State

None

---

# Page 2 — Assessment Chat

## Route

```
/assessment
```

## Purpose

Conduct the AI-powered business assessment through natural conversation.

---

## Components

- Progress Header
- Conversation Window
- Typing Indicator
- Message Input
- Send Button

---

## API Calls

### Start Assessment

```
POST /api/v1/assessment/start
```

### Continue Conversation

```
POST /api/v1/chat
```

### Load Assessment

```
GET /api/v1/assessment/{id}
```

---

## User Actions

- Send Message
- Continue Assessment
- Leave Page
- Resume Assessment

---

## Success State

Assessment completed.

↓

Navigate to Report Generation.

---

## Loading State

Display

- Typing Indicator
- Disabled Input

---

## Error State

Display

- Retry Button
- Error Message

---

## Navigation

```
Landing

↓

Assessment Chat

↓

Generating Report
```

---

# Page 3 — Generating Report

## Route

```
/report/loading
```

## Purpose

Inform the user that the AI is analyzing the collected information and preparing recommendations.

---

## Components

- Loading Animation
- Progress Indicator
- Status Message

Example

> LIA sedang menganalisis hasil asesmen Anda...

---

## API Calls

```
POST /api/v1/report/generate
```

---

## Success State

Navigate automatically to

```
/report/{id}
```

---

## Error State

Display Retry Button.

---

# Page 4 — Assessment Report

## Route

```
/report/{report_id}
```

## Purpose

Display the AI-generated business assessment report.

---

## Components

- Property Summary
- Business Analysis
- AI Readiness Score
- Recommendation Cards
- Next Steps
- Download Button

---

## API Calls

```
GET /api/v1/report/{report_id}
```

---

## User Actions

- View Report
- Download Report (Future)
- Start New Assessment

---

## Success State

Report displayed successfully.

---

## Error State

Display

- Report Not Found
- Retry Button

---

# Page 5 — 404 Page

## Route

```
*
```

## Purpose

Handle invalid routes.

---

## Components

- Illustration
- Error Message
- Back Home Button

---

# Navigation Map

```text
Landing
    │
    ▼
Assessment Chat
    │
    ▼
Generating Report
    │
    ▼
Assessment Report
```

---

# Shared Layout

The following components are reused across multiple pages.

- Navbar
- Footer
- Container
- Loading Spinner
- Error Dialog
- Progress Bar

---

# Responsive Behaviour

## Mobile

- Full-screen chat
- Sticky message input
- Collapsible progress header

---

## Tablet

- Larger chat area
- Fixed progress bar

---

## Desktop

- Centered layout
- Wider report cards
- Larger conversation window

---

# Future Pages

These pages are outside the MVP.

- Login
- Dashboard
- Assessment History
- Organization Management
- User Profile
- Settings
- Analytics Dashboard
- Admin Panel

---

# Design Principles

- One primary action per page.
- Keep navigation simple.
- Always display assessment progress.
- Minimize user distraction.
- Provide immediate feedback after every interaction.
- Ensure all pages remain responsive and accessible.