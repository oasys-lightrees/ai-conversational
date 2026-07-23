"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";

/** Triggers the browser print dialog (print-to-PDF). */
export function DownloadReportButton() {
  return (
    <Button variant="secondary" onClick={() => window.print()}>
      <Download className="h-4 w-4" />
      Unduh PDF
    </Button>
  );
}
