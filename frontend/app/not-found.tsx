// 404 page (route: *). See docs/frontend/05-page-specification.MD — Page 5.

import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-2xl font-bold">404</h1>
      <p className="text-navy/60">Halaman tidak ditemukan.</p>
      <Link href="/" className="text-navy underline">
        Kembali ke beranda
      </Link>
    </main>
  );
}
