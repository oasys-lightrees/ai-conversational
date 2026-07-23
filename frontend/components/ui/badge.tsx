import type { ReactNode } from "react";

import type { RecommendationPriority } from "@/lib/api";
import { cn } from "@/lib/utils";

const PRIORITY_STYLES: Record<RecommendationPriority, string> = {
  HIGH: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  MEDIUM: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  LOW: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
};

/** Status/priority chip. Pass `priority` for the priority color scheme. */
export function Badge({
  children,
  priority,
  className,
}: {
  children: ReactNode;
  priority?: RecommendationPriority;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        priority
          ? PRIORITY_STYLES[priority]
          : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
        className,
      )}
    >
      {children}
    </span>
  );
}
