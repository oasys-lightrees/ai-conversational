"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, api, type ConversationRole } from "@/lib/api";
import {
  clearStoredAssessmentId,
  getStoredAssessmentId,
  setStoredAssessmentId,
} from "@/lib/session";

export interface ChatMessage {
  id: string;
  role: ConversationRole;
  content: string;
}

/** Lifecycle of the chat page. */
export type Phase = "loading" | "ready" | "sending" | "error" | "complete";

// LIA's opening line. It's UI copy (the backend has no message on start), so it
// is shown locally and never persisted.
const GREETING =
  "Halo, saya LIA. Saya akan membantu menilai bisnis properti Anda melalui " +
  "percakapan singkat. Untuk memulai, boleh ceritakan tentang properti Anda?";

let counter = 0;
const nextId = () => `m${Date.now()}-${counter++}`;
const greeting = (): ChatMessage => ({ id: "greeting", role: "ASSISTANT", content: GREETING });

function errorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  return "Terjadi kesalahan. Silakan coba lagi.";
}

export interface UseAssessment {
  messages: ChatMessage[];
  completion: number;
  stage: string | null;
  phase: Phase;
  error: string | null;
  sendMessage: (text: string) => void;
}

export function useAssessment(): UseAssessment {
  const router = useRouter();
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [completion, setCompletion] = useState(0);
  const [stage, setStage] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>("loading");
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false);

  useEffect(() => {
    // Guard against double-run in React 18 StrictMode dev.
    if (started.current) return;
    started.current = true;

    async function startFresh() {
      const res = await api.startAssessment();
      setStoredAssessmentId(res.assessment_id);
      setAssessmentId(res.assessment_id);
      setMessages([greeting()]);
      setCompletion(0);
      setPhase("ready");
    }

    async function init() {
      setPhase("loading");
      setError(null);
      const stored = getStoredAssessmentId();
      if (stored) {
        try {
          const [assessment, history] = await Promise.all([
            api.getAssessment(stored),
            api.getConversation(stored),
          ]);
          setAssessmentId(stored);
          setCompletion(assessment.completion_percentage);
          setMessages([
            greeting(),
            ...history.map((m) => ({ id: nextId(), role: m.role, content: m.message })),
          ]);
          setPhase("ready");
          return;
        } catch {
          clearStoredAssessmentId(); // stale/unknown id — fall through to fresh
        }
      }
      try {
        await startFresh();
      } catch (err) {
        setError(errorMessage(err));
        setPhase("error");
      }
    }

    void init();
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || !assessmentId || phase === "sending") return;

      setMessages((prev) => [...prev, { id: nextId(), role: "USER", content: trimmed }]);
      setPhase("sending");
      setError(null);
      try {
        const res = await api.chat(assessmentId, trimmed);
        setMessages((prev) => [
          ...prev,
          { id: nextId(), role: "ASSISTANT", content: res.reply },
        ]);
        setCompletion(res.completion_percentage);
        setStage(res.next_stage);
        if (res.next_stage === "COMPLETE") {
          setPhase("complete");
          router.push(`/report/loading?assessment_id=${assessmentId}`);
        } else {
          setPhase("ready");
        }
      } catch (err) {
        setError(errorMessage(err));
        setPhase("error");
      }
    },
    [assessmentId, phase, router],
  );

  return { messages, completion, stage, phase, error, sendMessage };
}
