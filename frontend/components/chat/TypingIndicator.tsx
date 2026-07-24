"use client";

import { Avatar } from "@/components/ui/avatar";
import { Spinner } from "@/components/ui/spinner";
import { useI18n } from "@/lib/i18n";

/** Shown while awaiting the assistant's reply. */
export function TypingIndicator() {
  const { t } = useI18n();
  return (
    <div className="flex items-start gap-3">
      <Avatar role="ASSISTANT" />
      <div className="inline-flex items-center gap-2 rounded-2xl bg-navy/5 px-4 py-2.5 text-sm text-navy/60">
        <Spinner className="h-4 w-4" />
        {t("chat.typing")}
      </div>
    </div>
  );
}
