import { cn } from "@/lib/utils";

/** Assessment progress bar. `value` is a 0–100 percentage. */
export function Progress({ value, className }: { value: number; className?: string }) {
  const clamped = Math.max(0, Math.min(100, Math.round(value)));
  return (
    <div
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
      className={cn(
        "h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700",
        className,
      )}
    >
      <div
        className="h-full rounded-full bg-blue-600 transition-all duration-500 ease-out"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
