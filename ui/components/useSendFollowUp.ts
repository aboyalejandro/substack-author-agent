"use client";

import { useAgent, useCopilotKit } from "@copilotkit/react-core/v2";
import { randomUUID } from "@copilotkit/shared";
import { useCallback } from "react";

/**
 * Returns a `send(text)` that drops a user message into the conversation and
 * runs the agent — used by interactive cards (chart drilldowns, row actions)
 * to drive a follow-up turn without the user typing.
 */
export function useSendFollowUp() {
  const { agent } = useAgent();
  const { copilotkit } = useCopilotKit();

  return useCallback(
    async (text: string) => {
      if (!agent) return;
      agent.addMessage({ id: randomUUID(), role: "user", content: text });
      await copilotkit.runAgent({ agent });
    },
    [agent, copilotkit]
  );
}
