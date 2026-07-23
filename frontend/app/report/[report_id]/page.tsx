"use client";

// Assessment report page (route: /report/[report_id]).
// See docs/frontend/05-page-specification.MD — Page 4.

import { useParams, useRouter } from "next/navigation";

import { PropertySummaryCard } from "@/components/assessment/PropertySummaryCard";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { PageContainer } from "@/components/layout/PageContainer";
import { DownloadReportButton } from "@/components/report/DownloadReportButton";
import { RecommendationList } from "@/components/report/RecommendationList";
import { ReportSection } from "@/components/report/ReportSection";
import { ReportSummary } from "@/components/report/ReportSummary";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useReport } from "@/hooks/useReport";
import { clearStoredAssessmentId } from "@/lib/session";

export default function ReportPage() {
  const { report_id } = useParams<{ report_id: string }>();
  const router = useRouter();
  const { report, assessment, status, error, reload } = useReport(report_id);

  const startNew = () => {
    clearStoredAssessmentId();
    router.push("/assessment");
  };

  if (status === "loading") {
    return (
      <main className="flex min-h-screen items-center justify-center gap-3 text-slate-500">
        <Spinner />
        <span>Memuat laporan...</span>
      </main>
    );
  }

  if (status === "error" || !report) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
        <p className="text-sm text-red-600 dark:text-red-400">
          {error ?? "Laporan tidak ditemukan."}
        </p>
        <Button onClick={reload}>Coba lagi</Button>
      </main>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 py-8">
        <PageContainer className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <h1 className="text-2xl font-bold">Laporan Asesmen</h1>
            <DownloadReportButton />
          </div>

          {assessment && <PropertySummaryCard data={assessment.assessment_data} />}

          <ReportSummary summary={report.executive_summary} />
          <ReportSection title="Analisis Bisnis" body={report.business_analysis} />
          <ReportSection title="Analisis Operasional" body={report.operational_analysis} />
          <ReportSection title="Analisis Teknologi" body={report.technology_analysis} />
          <ReportSection title="Kesiapan AI" body={report.ai_readiness} />

          <RecommendationList items={report.recommendations} />

          <ReportSection title="Ringkasan Rekomendasi" body={report.recommendations_summary} />
          <ReportSection title="Langkah Berikutnya" body={report.next_steps} />

          <div className="pt-2">
            <Button variant="secondary" onClick={startNew}>
              Mulai Asesmen Baru
            </Button>
          </div>
        </PageContainer>
      </main>
      <Footer />
    </div>
  );
}
