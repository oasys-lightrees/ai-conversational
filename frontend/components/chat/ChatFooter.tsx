import { MessageInput } from "./MessageInput";

/** Sticky composer at the bottom of the chat page. */
export function ChatFooter({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="border-t border-slate-200 py-3 dark:border-slate-800">
      <MessageInput onSend={onSend} disabled={disabled} />
    </div>
  );
}
