"use client";

import { useCallback, useEffect, useState } from "react";

import { api, type AssessmentResponse, type ReportResponse } from "@/lib/api";

type Status = "loading" | "ready" | "error";

export interface UseReport {
  report: ReportResponse | null;
  assessment: AssessmentResponse | null;
  status: Status;
  error: string | null;
  reload: () => void;
}

export function useReport(reportId: string): UseReport {
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  const [status, setStatus] = useState<Status>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);
    try {
      const rep = await api.getReport(reportId);
      setReport(rep);
      // The property summary is best-effort — a failure here shouldn't block
      // the report itself.
      try {
        setAssessment(await api.getAssessment(rep.assessment_id));
      } catch {
        setAssessment(null);
      }
      setStatus("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal memuat laporan.");
      setStatus("error");
    }
  }, [reportId]);

  useEffect(() => {
    void load();
  }, [load]);

  return { report, assessment, status, error, reload: load };
}
