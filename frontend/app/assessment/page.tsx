"use client";

// Assessment chat page (route: /assessment).
// See docs/frontend/05-page-specification.MD — Page 2.

import { Check } from "lucide-react";
import { useRouter } from "next/navigation";

import { ProgressHeader } from "@/components/assessment/ProgressHeader";
import { ChatFooter } from "@/components/chat/ChatFooter";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { Spinner } from "@/components/ui/spinner";
import { useAssessment } from "@/hooks/useAssessment";
import { useI18n } from "@/lib/i18n";
import { clearStoredAssessmentId } from "@/lib/session";

export default function AssessmentPage() {
  const { t } = useI18n();
  const router = useRouter();
  const { messages, completion, stage, phase, error, sendMessage } = useAssessment();

  const startNew = () => {
    clearStoredAssessmentId();
    router.push("/");
  };

  if (phase === "loading") {
    return (
      <main className="flex min-h-screen items-center justify-center gap-3 text-navy/60">
        <Spinner />
        <span>{t("assessment.loading")}</span>
      </main>
    );
  }

  // Completed: a dedicated done screen instead of the chat.
  if (phase === "complete") {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8 text-center">
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-gold text-navy">
          <Check className="h-8 w-8" strokeWidth={3} />
        </span>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-navy">{t("done.title")}</h1>
          <p className="max-w-md text-navy/70">{t("done.message")}</p>
        </div>
        <Button onClick={startNew} className="px-8 py-3 text-base">
          {t("assessment.startNew")}
        </Button>
      </main>
    );
  }

  return (
    <main className="flex h-[100dvh] flex-col">
      <PageContainer className="flex h-full flex-col">
        <div className="flex items-center justify-end pt-2">
          <LanguageToggle />
        </div>
        <ProgressHeader completion={completion} stage={stage} />
        <ChatWindow messages={messages} typing={phase === "sending"} />
        {error && (
          <div
            role="alert"
            className="mb-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </div>
        )}
        <ChatFooter onSend={sendMessage} disabled={phase === "sending"} />
      </PageContainer>
    </main>
  );
}
