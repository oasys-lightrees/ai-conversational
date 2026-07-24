"use client";

import type { Recommendation } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { RecommendationCard } from "./RecommendationCard";

export function RecommendationList({ items }: { items: Recommendation[] }) {
  const { t } = useI18n();
  if (items.length === 0) return null;
  return (
    <section className="space-y-3">
      <h2 className="text-sm font-semibold text-navy">{t("report.reco")}</h2>
      <div className="space-y-3">
        {items.map((rec, index) => (
          <RecommendationCard key={`${rec.title}-${index}`} rec={rec} />
        ))}
      </div>
    </section>
  );
}
