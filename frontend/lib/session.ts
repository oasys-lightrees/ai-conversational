// Assessment id persistence (Decision D-F1).
// The active assessment id is stored in localStorage so a returning user can
// resume, and passed via the URL where a page needs it (e.g. /report/loading).
// All accessors are SSR-safe (no-op / null on the server).

const STORAGE_KEY = "assessmentId";

export function getStoredAssessmentId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(STORAGE_KEY);
}

export function setStoredAssessmentId(id: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, id);
}

export function clearStoredAssessmentId(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}
