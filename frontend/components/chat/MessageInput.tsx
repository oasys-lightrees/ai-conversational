"use client";

import { useState, type KeyboardEvent } from "react";
import { Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

/** Text input with a send button. Enter sends; Shift+Enter inserts a newline. */
export function MessageInput({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [value, setValue] = useState("");

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="flex items-end gap-2">
      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        rows={1}
        placeholder="Ketik pesan Anda..."
        disabled={disabled}
        className="max-h-32 min-h-[44px]"
      />
      <Button
        onClick={submit}
        disabled={disabled || !value.trim()}
        aria-label="Kirim pesan"
        className="h-11 shrink-0 px-4"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
