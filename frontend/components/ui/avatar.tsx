import type { ConversationRole } from "@/lib/api";
import { cn } from "@/lib/utils";

/** Small circular avatar distinguishing the assistant (LIA) from the user. */
export function Avatar({
  role,
  className,
}: {
  role: ConversationRole;
  className?: string;
}) {
  const isAssistant = role === "ASSISTANT";
  return (
    <span
      className={cn(
        "inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold",
        isAssistant
          ? "bg-blue-600 text-white"
          : "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-100",
        className,
      )}
    >
      {isAssistant ? "LIA" : "You"}
    </span>
  );
}
