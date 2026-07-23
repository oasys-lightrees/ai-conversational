"use client";

// 404 page (route: *). See docs/frontend/05-page-specification.MD — Page 5.

import Link from "next/link";

import { useI18n } from "@/lib/i18n";

export default function NotFound() {
  const { t } = useI18n();
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-2xl font-bold">404</h1>
      <p className="text-navy/60">{t("notfound.message")}</p>
      <Link href="/" className="text-navy underline">
        {t("notfound.back")}
      </Link>
    </main>
  );
}
