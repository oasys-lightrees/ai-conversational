"use client";

import { useI18n } from "@/lib/i18n";

/** Highlighted executive summary block at the top of the report. */
export function ReportSummary({ summary }: { summary: string | null }) {
  const { t } = useI18n();
  if (!summary) return null;
  return (
    <section className="rounded-xl bg-ink p-5 text-white">
      <h2 className="mb-2 text-base font-semibold text-white">{t("report.summary")}</h2>
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-white/75">{summary}</p>
    </section>
  );
}
