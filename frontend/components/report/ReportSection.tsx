/** A titled narrative section. Renders nothing when the body is empty. */
export function ReportSection({ title, body }: { title: string; body: string | null }) {
  if (!body) return null;
  return (
    <section className="space-y-1.5">
      <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
      <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600 dark:text-slate-300">
        {body}
      </p>
    </section>
  );
}
