// Assessment report page (route: /report/[report_id]).
// See docs/frontend/05-page-specification.MD — Page 4.

export default async function ReportPage({
  params,
}: {
  params: Promise<{ report_id: string }>;
}) {
  const { report_id } = await params;
  return (
    <main className="flex min-h-screen flex-col gap-4 p-8">
      <h1 className="text-2xl font-bold">Assessment Report</h1>
      <p className="text-slate-600">Report ID: {report_id}</p>
    </main>
  );
}
