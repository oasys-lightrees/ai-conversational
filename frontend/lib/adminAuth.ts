// Admin key persistence (shared-key auth). SSR-safe.

const STORAGE_KEY = "adminApiKey";

export function getAdminKey(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(STORAGE_KEY);
}

export function setAdminKey(key: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, key);
}

export function clearAdminKey(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}
