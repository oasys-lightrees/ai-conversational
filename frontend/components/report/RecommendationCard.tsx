"use client";

import type { Recommendation } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  const { t } = useI18n();
  return (
    <div className="rounded-xl bg-ink p-4 text-white">
      <div className="mb-2 flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">{rec.title}</h3>
        <Badge priority={rec.priority}>{t(`priority.${rec.priority}`)}</Badge>
      </div>
      {rec.description && <p className="text-sm text-white/75">{rec.description}</p>}
      {rec.estimated_impact && (
        <p className="mt-2 text-xs text-gold">
          {t("report.impact")}: {rec.estimated_impact}
        </p>
      )}
    </div>
  );
}
