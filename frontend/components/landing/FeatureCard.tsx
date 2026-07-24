import type { LucideIcon } from "lucide-react";

export function FeatureCard({
  icon: Icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl bg-ink p-5 text-left text-white">
      <Icon className="mb-3 h-6 w-6 text-gold" aria-hidden />
      <h3 className="mb-1 text-sm font-semibold text-white">{title}</h3>
      <p className="text-sm text-white/70">{description}</p>
    </div>
  );
}
