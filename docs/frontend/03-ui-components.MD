# UI Components

## Purpose

This document defines all reusable UI components for the AI Conversational Assessment Agent.

The application follows Atomic Design principles to maximize reusability, maintainability, and consistency.

---

# Component Hierarchy

```text
Atoms
    │
    ▼
Molecules
    │
    ▼
Organisms
    │
    ▼
Pages
```

---

# 1. Atoms

Small reusable UI elements.

| Component | Description |
|-----------|-------------|
| Button | Primary and secondary actions |
| Input | User text input |
| Textarea | Multi-line input |
| Label | Form labels |
| Badge | Status indicators |
| Avatar | AI/User avatar |
| Icon | Lucide icons |
| Spinner | Loading indicator |
| Progress | Assessment progress bar |
| Separator | Section divider |

---

# 2. Molecules

Combination of multiple atoms.

## Chat Bubble

Displays a single conversation message.

Contains

- Avatar
- Message
- Timestamp

---

## Message Input

Contains

- Text Input
- Send Button

---

## Progress Header

Contains

- Progress Bar
- Completion Percentage
- Current Stage

---

## Typing Indicator

Contains

- Spinner
- "LIA sedang mengetik..."

---

## Recommendation Card

Contains

- Priority Badge
- Recommendation Title
- Description
- Expected Benefit

---

# 3. Organisms

Large reusable sections.

---

## Chat Window

Contains

- Chat Bubble List
- Typing Indicator
- Auto Scroll

---

## Chat Footer

Contains

- Message Input
- Send Button

---

## Assessment Progress

Contains

- Progress Bar
- Current Stage
- Remaining Questions

---

## Report Summary

Contains

- Executive Summary
- AI Readiness
- Overall Score

---

## Recommendation List

Contains

- Recommendation Cards

---

## Property Summary Card

Contains

- Property Type
- Location
- Business Stage
- Total Units

---

# 4. Pages

## Landing Page

Components

- Hero Section
- Start Assessment Button
- Features
- Footer

---

## Assessment Chat Page

Components

- Progress Header
- Chat Window
- Chat Footer

---

## Report Page

Components

- Report Summary
- Property Summary Card
- Recommendation List
- Download Button

---

## Error Page

Components

- Error Message
- Retry Button

---

# Component Structure

```text
components/

ui/
│
├── button.tsx
├── input.tsx
├── badge.tsx
├── progress.tsx
└── ...

assessment/
│
├── ProgressHeader.tsx
├── PropertySummaryCard.tsx
├── RecommendationCard.tsx
└── AssessmentProgress.tsx

chat/
│
├── ChatBubble.tsx
├── ChatWindow.tsx
├── ChatFooter.tsx
├── MessageInput.tsx
├── TypingIndicator.tsx
└── EmptyConversation.tsx

report/
│
├── ReportSummary.tsx
├── RecommendationList.tsx
├── ReportSection.tsx
└── DownloadReportButton.tsx

layout/
│
├── Header.tsx
├── Footer.tsx
└── PageContainer.tsx
```

---

# Component States

## Chat Bubble

- User
- Assistant

---

## Progress Bar

- Not Started
- In Progress
- Completed

---

## Button

- Default
- Hover
- Disabled
- Loading

---

## Recommendation Card

- High Priority
- Medium Priority
- Low Priority

---

# Design Principles

- Components should have a single responsibility.
- Components should be reusable across multiple pages.
- Business logic should not be placed inside UI components.
- Components should receive data through props.
- Components should remain presentation-focused.

---

# Future Components

The following components may be introduced in future versions.

- Voice Recorder
- File Upload
- Image Upload
- PDF Viewer
- Dashboard Charts
- Notification Toasts
- Organization Selector
- Assessment History Table