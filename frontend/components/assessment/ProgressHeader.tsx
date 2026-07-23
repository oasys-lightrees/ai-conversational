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
    <div className="border-b border-slate-200 py-3 dark:border-slate-800">
      <div className="mb-1.5 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>{stageLabel(stage)}</span>
        <span>{Math.round(completion)}%</span>
      </div>
      <Progress value={completion} />
    </div>
  );
}
