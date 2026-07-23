"use client";

// Assessment chat page (route: /assessment).
// See docs/frontend/05-page-specification.MD — Page 2.

import { ProgressHeader } from "@/components/assessment/ProgressHeader";
import { ChatFooter } from "@/components/chat/ChatFooter";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { PageContainer } from "@/components/layout/PageContainer";
import { Spinner } from "@/components/ui/spinner";
import { useAssessment } from "@/hooks/useAssessment";

export default function AssessmentPage() {
  const { messages, completion, stage, phase, error, sendMessage } = useAssessment();

  if (phase === "loading") {
    return (
      <main className="flex min-h-screen items-center justify-center gap-3 text-slate-500">
        <Spinner />
        <span>Memuat asesmen...</span>
      </main>
    );
  }

  return (
    <main className="flex h-screen flex-col">
      <PageContainer className="flex h-full flex-col">
        <ProgressHeader completion={completion} stage={stage} />
        <ChatWindow messages={messages} typing={phase === "sending"} />
        {error && (
          <div
            role="alert"
            className="mb-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300"
          >
            {error}
          </div>
        )}
        <ChatFooter
          onSend={sendMessage}
          disabled={phase === "sending" || phase === "complete"}
        />
      </PageContainer>
    </main>
  );
}
