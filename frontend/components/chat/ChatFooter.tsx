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
    <div className="border-t border-navy/10 py-3">
      <MessageInput onSend={onSend} disabled={disabled} />
    </div>
  );
}
