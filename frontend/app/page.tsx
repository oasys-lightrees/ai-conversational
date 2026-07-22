// Landing page (route: /). See docs/frontend/05-page-specification.MD.
// Scaffold placeholder — components live under components/.

export default function LandingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-3xl font-bold">AI Conversational Assessment Agent</h1>
      <p className="max-w-md text-center text-slate-600">
        Assess your property business through a natural conversation and receive
        AI-driven recommendations.
      </p>
      <a
        href="/assessment"
        className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white"
      >
        Start Assessment
      </a>
    </main>
  );
}
