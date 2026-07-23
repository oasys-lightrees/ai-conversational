// Helpers for reading and presenting the loosely-typed assessment_data map.

import type { AssessmentData } from "@/lib/api";

/** "BOARDING_HOUSE" -> "Boarding House". Returns "-" for non-strings. */
export function humanizeEnum(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) return "-";
  return value
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function getString(data: AssessmentData, key: string): string | null {
  const value = data[key];
  return typeof value === "string" && value.trim() ? value : null;
}

export function getNumber(data: AssessmentData, key: string): number | null {
  const value = data[key];
  return typeof value === "number" ? value : null;
}
