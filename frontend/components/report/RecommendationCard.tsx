import type { Recommendation, RecommendationPriority } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const PRIORITY_LABEL: Record<RecommendationPriority, string> = {
  HIGH: "Prioritas Tinggi",
  MEDIUM: "Prioritas Sedang",
  LOW: "Prioritas Rendah",
};

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-800">
      <div className="mb-2 flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{rec.title}</h3>
        <Badge priority={rec.priority}>{PRIORITY_LABEL[rec.priority]}</Badge>
      </div>
      {rec.description && (
        <p className="text-sm text-slate-600 dark:text-slate-300">{rec.description}</p>
      )}
      {rec.estimated_impact && (
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
          Dampak: {rec.estimated_impact}
        </p>
      )}
    </div>
  );
}
