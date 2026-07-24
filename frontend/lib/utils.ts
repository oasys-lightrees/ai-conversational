// Small helpers shared across the UI.

/** Join truthy class names (a tiny, dependency-free `clsx`). */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}
