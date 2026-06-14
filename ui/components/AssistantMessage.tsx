"use client";

import {
  CopilotChatAssistantMessage,
  useAgent,
} from "@copilotkit/react-core/v2";
import FollowUpChips from "./FollowUpChips";
import ToolCallsView from "./ToolCallsView";

/** Read the assistant message aloud via the browser's speech synthesis. */
function readAloud(message: any) {
  const text = (message?.content ?? "").trim();
  if (!text || typeof window === "undefined" || !window.speechSynthesis) return;
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    return;
  }
  window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
}

const noop = () => {};

/**
 * Custom assistant-message slot. The agent emits several assistant messages per
 * turn (preamble + post-tool text), so the toolbar and follow-ups are shown
 * only on the last one, once the run is idle.
 */
export default function AssistantMessage(props: any) {
  const { agent } = useAgent();
  const messages: any[] = (agent as any)?.messages ?? [];
  const running = !!(agent as any)?.isRunning;

  const lastAssistantId = [...messages]
    .reverse()
    .find((m) => m.role === "assistant" && m.content)?.id;
  const isLast = !!props.message?.id && props.message.id === lastAssistantId;
  const showExtras = isLast && !running;

  return (
    <>
      <CopilotChatAssistantMessage
        {...props}
        toolCallsView={ToolCallsView}
        markdownRenderer={{ controls: { code: false, table: false } }}
        onReadAloud={readAloud}
        onThumbsUp={noop}
        onThumbsDown={noop}
        toolbarVisible={showExtras}
      />
      {showExtras && (
        <FollowUpChips key={props.message.id} messages={messages} />
      )}
    </>
  );
}
