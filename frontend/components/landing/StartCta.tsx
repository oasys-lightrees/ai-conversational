"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { clearStoredAssessmentId, getStoredAssessmentId } from "@/lib/session";

/** Primary call-to-action. Offers to resume when an assessment is in progress. */
export function StartCta() {
  const router = useRouter();
  const { t } = useI18n();
  const [hasResume, setHasResume] = useState(false);

  useEffect(() => {
    setHasResume(Boolean(getStoredAssessmentId()));
  }, []);

  const resume = () => router.push("/assessment");
  const startNew = () => {
    clearStoredAssessmentId();
    router.push("/assessment");
  };

  return (
    <div className="flex flex-col items-center gap-3 sm:flex-row">
      <Button onClick={resume} className="px-8 py-3 text-base">
        {hasResume ? t("cta.resume") : t("cta.start")}
      </Button>
      {hasResume && (
        <Button variant="secondary" onClick={startNew}>
          {t("cta.new")}
        </Button>
      )}
    </div>
  );
}
