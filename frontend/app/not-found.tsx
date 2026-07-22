// 404 page (route: *). See docs/frontend/05-page-specification.MD — Page 5.

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-2xl font-bold">404</h1>
      <p className="text-slate-600">Halaman tidak ditemukan.</p>
      <a href="/" className="text-blue-600 underline">
        Kembali ke beranda
      </a>
    </main>
  );
}
