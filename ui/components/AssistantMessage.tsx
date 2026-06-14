"use client";

import {
  CopilotChatAssistantMessage,
  useAgent,
} from "@copilotkit/react-core/v2";
import FollowUpChips from "./FollowUpChips";
import ToolCallsView from "./ToolCallsView";

const hidden = () => null;

/**
 * Custom assistant-message slot. The agent emits several assistant messages per
 * turn (preamble + post-tool text), so the toolbar and follow-ups are shown
 * only on the last one, once the run is idle. Read-aloud and thumbs are hidden
 * — copy is the only action we keep.
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
        readAloudButton={hidden}
        thumbsUpButton={hidden}
        thumbsDownButton={hidden}
        toolbarVisible={showExtras}
      />
      {showExtras && (
        <FollowUpChips key={props.message.id} messages={messages} />
      )}
    </>
  );
}
