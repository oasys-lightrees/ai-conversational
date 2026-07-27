import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/** Small status/label chip. */
export function Badge({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full bg-navy/10 px-2.5 py-0.5 text-xs font-medium text-navy",
        className,
      )}
    >
      {children}
    </span>
  );
}
