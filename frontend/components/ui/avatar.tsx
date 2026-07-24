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
        isAssistant ? "bg-navy text-gold" : "bg-gold text-navy",
        className,
      )}
    >
      {isAssistant ? "LIA" : "You"}
    </span>
  );
}
