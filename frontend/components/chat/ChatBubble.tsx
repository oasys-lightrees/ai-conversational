import type { ReactNode } from "react";

import type { ConversationRole } from "@/lib/api";
import { Avatar } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

/** A single conversation message with its avatar. */
export function ChatBubble({
  role,
  children,
}: {
  role: ConversationRole;
  children: ReactNode;
}) {
  const isUser = role === "USER";
  return (
    <div className={cn("flex items-start gap-3", isUser && "flex-row-reverse")}>
      <Avatar role={role} />
      <div
        className={cn(
          "max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
          isUser
            ? "bg-blue-600 text-white"
            : "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-100",
        )}
      >
        {children}
      </div>
    </div>
  );
}
