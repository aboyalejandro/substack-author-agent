"use client";

import {
  CopilotChat,
  useConfigureSuggestions,
} from "@copilotkit/react-core/v2";
import { useCallback } from "react";
import ToolCallsView from "./ToolCallsView";

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

  // Dynamic follow-up actions generated after every assistant message
  useConfigureSuggestions(
    {
      instructions:
        "Suggest the most relevant next content-strategy actions based on the conversation so far: drilling into a specific article's performance, comparing notes vs articles, extracting brand voice, generating content ideas, or reviewing cover images. Keep each suggestion short and actionable.",
      minSuggestions: 2,
      maxSuggestions: 3,
      available: "after-first-message",
    },
    []
  );

  // Read the assistant message aloud via the browser's speech synthesis.
  const onReadAloud = useCallback((message: any) => {
    const text = (message?.content ?? "").trim();
    if (!text || typeof window === "undefined" || !window.speechSynthesis) return;
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      return;
    }
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  }, []);

  const onThumbsUp = useCallback(() => {}, []);
  const onThumbsDown = useCallback(() => {}, []);

  return (
    <CopilotChat
      className="sa-chat dark h-full"
      messageView={{
        assistantMessage: {
          toolCallsView: ToolCallsView,
          onReadAloud,
          onThumbsUp,
          onThumbsDown,
        },
      }}
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
