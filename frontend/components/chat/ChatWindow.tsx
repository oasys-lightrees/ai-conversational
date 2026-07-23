"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage } from "@/hooks/useAssessment";
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

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="flex-1 space-y-4 overflow-y-auto py-4">
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
