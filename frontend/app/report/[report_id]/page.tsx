// Assessment report page (route: /report/[report_id]).
// See docs/frontend/05-page-specification.MD — Page 4.

export default function ReportPage({
  params,
}: {
  params: { report_id: string };
}) {
  return (
    <main className="flex min-h-screen flex-col gap-4 p-8">
      <h1 className="text-2xl font-bold">Assessment Report</h1>
      <p className="text-slate-600">Report ID: {params.report_id}</p>
    </main>
  );
}
