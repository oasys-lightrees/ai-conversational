// Typed API client scaffold for the backend REST API.
// Endpoints mirror docs/08-api-design.MD. Implementations are stubs.

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface StartAssessmentResponse {
  assessment_id: string;
  status: string;
  message: string;
}

export interface ChatResponse {
  reply: string;
  completion_percentage: number;
  next_stage: string | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  startAssessment: () =>
    request<StartAssessmentResponse>("/assessment/start", { method: "POST" }),

  chat: (assessmentId: string, message: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ assessment_id: assessmentId, message }),
    }),

  getAssessment: (assessmentId: string) =>
    request(`/assessment/${assessmentId}`),

  getConversation: (assessmentId: string) =>
    request(`/conversation/${assessmentId}`),

  generateReport: (assessmentId: string) =>
    request("/report/generate", {
      method: "POST",
      body: JSON.stringify({ assessment_id: assessmentId }),
    }),

  getReport: (reportId: string) => request(`/report/${reportId}`),
};
