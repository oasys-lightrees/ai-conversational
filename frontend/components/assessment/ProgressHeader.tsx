import { Progress } from "@/components/ui/progress";
import { stageLabel } from "@/lib/stages";

/** Sticky header showing the current stage and completion percentage. */
export function ProgressHeader({
  completion,
  stage,
}: {
  completion: number;
  stage: string | null;
}) {
  return (
    <div className="border-b border-navy/10 py-3">
      <div className="mb-1.5 flex items-center justify-between text-xs text-navy/60">
        <span>{stageLabel(stage)}</span>
        <span>{Math.round(completion)}%</span>
      </div>
      <Progress value={completion} />
    </div>
  );
}
