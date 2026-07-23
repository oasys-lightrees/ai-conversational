/** Highlighted executive summary block at the top of the report. */
export function ReportSummary({ summary }: { summary: string | null }) {
  if (!summary) return null;
  return (
    <section className="rounded-xl bg-slate-50 p-5 dark:bg-slate-900">
      <h2 className="mb-2 text-base font-semibold text-slate-900 dark:text-slate-100">
        Ringkasan Eksekutif
      </h2>
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600 dark:text-slate-300">
        {summary}
      </p>
    </section>
  );
}
