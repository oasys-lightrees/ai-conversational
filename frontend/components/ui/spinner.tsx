import { cn } from "@/lib/utils";

/** Indeterminate loading spinner. */
export function Spinner({ className }: { className?: string }) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={cn(
        "inline-block animate-spin rounded-full border-2 border-current border-t-transparent",
        className ?? "h-5 w-5",
      )}
    />
  );
}
