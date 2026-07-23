import { Avatar } from "@/components/ui/avatar";
import { Spinner } from "@/components/ui/spinner";

/** Shown while awaiting the assistant's reply. */
export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <Avatar role="ASSISTANT" />
      <div className="inline-flex items-center gap-2 rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-500 dark:bg-slate-800 dark:text-slate-400">
        <Spinner className="h-4 w-4" />
        LIA sedang mengetik...
      </div>
    </div>
  );
}
