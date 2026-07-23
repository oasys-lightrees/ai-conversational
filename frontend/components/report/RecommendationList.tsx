import type { Recommendation } from "@/lib/api";
import { RecommendationCard } from "./RecommendationCard";

export function RecommendationList({ items }: { items: Recommendation[] }) {
  if (items.length === 0) return null;
  return (
    <section className="space-y-3">
      <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Rekomendasi</h2>
      <div className="space-y-3">
        {items.map((rec, index) => (
          <RecommendationCard key={`${rec.title}-${index}`} rec={rec} />
        ))}
      </div>
    </section>
  );
}
