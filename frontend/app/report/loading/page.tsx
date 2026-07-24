"use client";

// Generating-report page (route: /report/loading?assessment_id=...).
// See docs/frontend/05-page-specification.MD — Page 3.

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { ApiError, api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useI18n } from "@/lib/i18n";

function GeneratingReport() {
  const router = useRouter();
  const { t } = useI18n();
  const assessmentId = useSearchParams().get("assessment_id");
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false);

  const generate = async () => {
    if (!assessmentId) {
      setError(t("loading.notFound"));
      return;
    }
    setError(null);
    try {
      const res = await api.generateReport(assessmentId);
      router.replace(`/report/${res.report_id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("loading.error"));
    }
  };

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void generate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <p className="text-sm text-red-600">{error}</p>
        <Button onClick={generate}>{t("loading.retry")}</Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <Spinner className="h-8 w-8 text-gold" />
      <h1 className="text-xl font-semibold">{t("loading.title")}</h1>
      <p className="text-navy/60">{t("loading.message")}</p>
    </div>
  );
}

export default function ReportLoadingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <Suspense fallback={<Spinner className="h-8 w-8 text-gold" />}>
        <GeneratingReport />
      </Suspense>
    </main>
  );
}
