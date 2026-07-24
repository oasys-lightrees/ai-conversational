import type { ReactNode } from "react";

import type { RecommendationPriority } from "@/lib/api";
import { cn } from "@/lib/utils";

// Priority chips render on the dark (ink) recommendation cards, so they use
// light-on-dark treatments within the navy/gold/white palette.
const PRIORITY_STYLES: Record<RecommendationPriority, string> = {
  HIGH: "bg-gold text-navy",
  MEDIUM: "bg-white/15 text-white",
  LOW: "border border-white/30 text-white/70",
};

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
        priority ? PRIORITY_STYLES[priority] : "bg-white/10 text-white",
        className,
      )}
    >
      {children}
    </span>
  );
}
