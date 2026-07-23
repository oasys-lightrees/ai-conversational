import type { Recommendation, RecommendationPriority } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const PRIORITY_LABEL: Record<RecommendationPriority, string> = {
  HIGH: "Prioritas Tinggi",
  MEDIUM: "Prioritas Sedang",
  LOW: "Prioritas Rendah",
};

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="rounded-xl bg-ink p-4 text-white">
      <div className="mb-2 flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">{rec.title}</h3>
        <Badge priority={rec.priority}>{PRIORITY_LABEL[rec.priority]}</Badge>
      </div>
      {rec.description && <p className="text-sm text-white/75">{rec.description}</p>}
      {rec.estimated_impact && (
        <p className="mt-2 text-xs text-gold">Dampak: {rec.estimated_impact}</p>
      )}
    </div>
  );
}
