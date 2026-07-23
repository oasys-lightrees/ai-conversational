"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage } from "@/hooks/useAssessment";
import { useI18n } from "@/lib/i18n";
import { ChatBubble } from "./ChatBubble";
import { TypingIndicator } from "./TypingIndicator";

/** Scrollable conversation list with auto-scroll to the latest message. */
export function ChatWindow({
  messages,
  typing,
}: {
  messages: ChatMessage[];
  typing: boolean;
}) {
  const endRef = useRef<HTMLDivElement>(null);
  const { t } = useI18n();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="flex-1 space-y-4 overflow-y-auto py-4">
      {/* LIA's opening line (UI copy; not persisted). */}
      <ChatBubble role="ASSISTANT">{t("chat.greeting")}</ChatBubble>
      {messages.map((m) => (
        <ChatBubble key={m.id} role={m.role}>
          {m.content}
        </ChatBubble>
      ))}
      {typing && <TypingIndicator />}
      <div ref={endRef} />
    </div>
  );
}
