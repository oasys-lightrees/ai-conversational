// Typed API client for the backend REST API.
// Types mirror the backend Pydantic schemas exactly (backend/schemas/*).
// This module is the single source of truth for the frontend<->backend
// contract — keep it in lockstep with the backend.

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

// --- Enums (mirror backend/models/enums.py) ---------------------------------

export type AssessmentStatus = "IN_PROGRESS" | "COMPLETED" | "ABANDONED";
export type ConversationRole = "USER" | "ASSISTANT";
export type RecommendationPriority = "LOW" | "MEDIUM" | "HIGH";

// --- Response shapes (mirror backend/schemas/*) -----------------------------

export interface StartAssessmentResponse {
  assessment_id: string;
  status: AssessmentStatus;
  message: string;
}

export interface ChatResponse {
  reply: string;
  completion_percentage: number;
  next_stage: string | null;
}

/** Collected assessment fields. Values are enums-as-strings, numbers, booleans,
 *  or arrays depending on the field; flattened branch fields appear here too. */
export type AssessmentData = Record<string, unknown>;

export interface AssessmentResponse {
  assessment_id: string;
  status: AssessmentStatus;
  completion_percentage: number;
  assessment_data: AssessmentData;
}

export interface ConversationMessage {
  role: ConversationRole;
  message: string;
}

export interface TemplateSummary {
  id: string;
  name: string;
  description: string | null;
  language: string;
  is_default: boolean;
}

export interface Recommendation {
  title: string;
  description: string | null;
  priority: RecommendationPriority;
  estimated_impact: string | null;
}

export interface ReportResponse {
  report_id: string;
  assessment_id: string;
  executive_summary: string | null;
  business_analysis: string | null;
  operational_analysis: string | null;
  technology_analysis: string | null;
  ai_readiness: string | null;
  recommendations_summary: string | null;
  next_steps: string | null;
  recommendations: Recommendation[];
}

// --- Request plumbing -------------------------------------------------------

/** Error carrying the HTTP status and the backend's `detail` message. */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError(0, "Network error. Please check your connection.");
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body?.detail === "string") {
        detail = body.detail;
      } else if (body?.detail != null) {
        detail = JSON.stringify(body.detail);
      }
    } catch {
      // non-JSON error body; keep the default message
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

// --- Endpoints (mirror docs/08-api-design.MD) -------------------------------

export const api = {
  getTemplates: () => request<TemplateSummary[]>("/templates"),

  startAssessment: (templateId?: string) =>
    request<StartAssessmentResponse>("/assessment/start", {
      method: "POST",
      body: JSON.stringify(templateId ? { template_id: templateId } : {}),
    }),

  chat: (assessmentId: string, message: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ assessment_id: assessmentId, message }),
    }),

  getAssessment: (assessmentId: string) =>
    request<AssessmentResponse>(`/assessment/${assessmentId}`),

  deleteAssessment: (assessmentId: string) =>
    request<void>(`/assessment/${assessmentId}`, { method: "DELETE" }),

  getConversation: (assessmentId: string) =>
    request<ConversationMessage[]>(`/conversation/${assessmentId}`),
};
