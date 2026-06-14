"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useSendFollowUp } from "./useSendFollowUp";

/**
 * LLM-generated one-click follow-ups, rendered under the last assistant
 * message's toolbar. Mounts (with a fresh key) once per completed turn and
 * fetches from /api/suggestions — Agno can't drive CopilotKit's native
 * suggestion tool, so we generate them ourselves.
 */
export default function FollowUpChips({ messages }: { messages: any[] }) {
  const send = useSendFollowUp();
  const [items, setItems] = useState<string[]>([]);
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    const tail = messages
      .slice(-6)
      .map((m) => ({
        role: m.role,
        content: typeof m.content === "string" ? m.content : "",
      }))
      .filter((m) => m.content);
    if (tail.length === 0) return;

    fetch("/api/suggestions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: tail }),
    })
      .then((r) => r.json())
      .then((d) => setItems(Array.isArray(d?.suggestions) ? d.suggestions : []))
      .catch(() => {});
  }, [messages]);

  if (items.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-wrap gap-2 px-1 pb-1"
    >
      {items.map((s, i) => (
        <button
          key={i}
          onClick={() => send(s)}
          className="rounded-full border border-white/15 bg-white/5 hover:bg-white/10 hover:border-substack-orange/60 transition-colors px-3 py-1.5 text-xs text-gray-200"
        >
          {s}
        </button>
      ))}
    </motion.div>
  );
}
