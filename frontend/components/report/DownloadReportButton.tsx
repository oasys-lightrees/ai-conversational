"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

/** Triggers the browser print dialog (print-to-PDF). */
export function DownloadReportButton() {
  const { t } = useI18n();
  return (
    <Button variant="secondary" onClick={() => window.print()}>
      <Download className="h-4 w-4" />
      {t("report.download")}
    </Button>
  );
}
