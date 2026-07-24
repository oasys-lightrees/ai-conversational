import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/** Centered, width-constrained page wrapper. */
export function PageContainer({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("mx-auto w-full max-w-3xl px-4", className)}>{children}</div>
  );
}
