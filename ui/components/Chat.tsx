"use client";

import {
  CopilotChat,
  useConfigureSuggestions,
} from "@copilotkit/react-core/v2";
import AssistantMessage from "./AssistantMessage";

const PUBLICATION_URL =
  process.env.NEXT_PUBLIC_PUBLICATION_URL ??
  "https://yourpublication.substack.com";

export default function Chat() {
  // Starter prompts shown before the first message
  useConfigureSuggestions(
    {
      suggestions: [
        {
          title: "📰 Analyze my articles",
          message: `Analyze my latest articles from ${PUBLICATION_URL}`,
        },
        {
          title: "📝 Analyze my notes",
          message: `How are my recent notes performing? ${PUBLICATION_URL}`,
        },
        {
          title: "💡 Content ideas",
          message: `Generate content ideas based on my top articles from ${PUBLICATION_URL}`,
        },
      ],
      available: "before-first-message",
    },
    []
  );

  return (
    <CopilotChat
      className="sa-chat dark h-full"
      messageView={{ assistantMessage: AssistantMessage as any }}
      attachments={{
        enabled: true,
        accept: "image/*,application/pdf,text/*,.md",
        maxSize: 10 * 1024 * 1024,
      }}
      labels={{
        chatInputPlaceholder:
          "Ask about your articles, notes, ideas, brand voice…",
      }}
    />
  );
}
