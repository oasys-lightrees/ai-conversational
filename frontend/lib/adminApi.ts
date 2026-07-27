// Typed admin API client. Sends the shared admin key as a bearer token.

import { ApiError } from "@/lib/api";
import { getAdminKey } from "@/lib/adminAuth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

// --- Types (mirror backend/schemas) -----------------------------------------

export type FieldType = "string" | "integer" | "decimal" | "boolean" | "list" | "enum";

export interface FieldSpec {
  name: string;
  label?: string;
  description?: string;
  type: FieldType;
  enum_options?: string[];
  aliases?: string[];
  required?: boolean;
  required_when?: Record<string, string[]> | null;
  section?: string;
}

export interface PipelineConfig {
  knowledge: string;
  style: string;
  language: "id" | "en";
  fields: FieldSpec[];
}

export interface TemplateSummary {
  id: string;
  name: string;
  description: string | null;
  language: string;
  is_default: boolean;
}

export interface TemplateDetail {
  id: string;
  name: string;
  description: string | null;
  is_default: boolean;
  config: PipelineConfig;
}

export interface TemplateWrite {
  name: string;
  description: string | null;
  is_default: boolean;
  config: PipelineConfig;
}

export interface AssessmentListItem {
  assessment_id: string;
  status: string;
  completion_percentage: number;
  template_id: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface PaginatedAssessments {
  items: AssessmentListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdminConversationMessage {
  role: "USER" | "ASSISTANT";
  message: string;
}

export interface AssessmentDetail {
  assessment_id: string;
  status: string;
  completion_percentage: number;
  template_id: string | null;
  created_at: string;
  completed_at: string | null;
  assessment_data: Record<string, unknown>;
  conversation: AdminConversationMessage[];
}

export interface NamedCount {
  key: string;
  count: number;
}

export interface Metrics {
  total_assessments: number;
  by_status: Record<string, number>;
  completion_rate: number;
  average_completion: number;
  by_property_type: NamedCount[];
  by_business_stage: NamedCount[];
}

// --- Request plumbing --------------------------------------------------------

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const key = getAdminKey();
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/admin${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(key ? { Authorization: `Bearer ${key}` } : {}),
      },
      ...init,
    });
  } catch {
    throw new ApiError(0, "Network error. Please check your connection.");
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body?.detail === "string") detail = body.detail;
      else if (body?.detail != null) detail = JSON.stringify(body.detail);
    } catch {
      /* keep default */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const adminApi = {
  metrics: () => request<Metrics>("/metrics"),

  listTemplates: () => request<TemplateSummary[]>("/templates"),
  getTemplate: (id: string) => request<TemplateDetail>(`/templates/${id}`),
  createTemplate: (body: TemplateWrite) =>
    request<TemplateDetail>("/templates", { method: "POST", body: JSON.stringify(body) }),
  updateTemplate: (id: string, body: TemplateWrite) =>
    request<TemplateDetail>(`/templates/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteTemplate: (id: string) =>
    request<void>(`/templates/${id}`, { method: "DELETE" }),
  cloneTemplate: (id: string) =>
    request<TemplateDetail>(`/templates/${id}/clone`, { method: "POST" }),
  setDefaultTemplate: (id: string) =>
    request<TemplateDetail>(`/templates/${id}/default`, { method: "POST" }),

  listAssessments: (params: { status?: string; page?: number } = {}) => {
    const q = new URLSearchParams();
    if (params.status) q.set("status", params.status);
    if (params.page) q.set("page", String(params.page));
    const suffix = q.toString() ? `?${q}` : "";
    return request<PaginatedAssessments>(`/assessments${suffix}`);
  },
  getAssessment: (id: string) => request<AssessmentDetail>(`/assessments/${id}`),
  deleteAssessment: (id: string) =>
    request<void>(`/assessments/${id}`, { method: "DELETE" }),
};
