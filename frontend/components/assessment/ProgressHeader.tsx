"use client";

import { Progress } from "@/components/ui/progress";
import { useI18n } from "@/lib/i18n";

/** Sticky header showing the current stage and completion percentage. */
export function ProgressHeader({
  completion,
  stage,
}: {
  completion: number;
  stage: string | null;
}) {
  const { t } = useI18n();
  const key = stage ? `stage.${stage}` : "stage.default";
  const translated = t(key);
  // Fall back to the raw code if the stage is unknown to the dictionary.
  const label = translated === key && stage ? stage : translated;

  return (
    <div className="border-b border-navy/10 py-3">
      <div className="mb-1.5 flex items-center justify-between text-xs text-navy/60">
        <span>{label}</span>
        <span>{Math.round(completion)}%</span>
      </div>
      <Progress value={completion} />
    </div>
  );
}
