"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import ArticlesCard from "./cards/ArticlesCard";
import NotesCard from "./cards/NotesCard";
import PerformanceCard from "./cards/PerformanceCard";
import PerformanceTrendChart, {
  type TrendPoint,
} from "./cards/PerformanceTrendChart";
import { formatDate, parseToolResult, TOOL_META } from "./lib";

/** Per-item performance lookups — aggregated into one trend chart past this count. */
const PERF_TOOLS = new Set(["get_article_performance", "get_note_performance"]);
const TREND_THRESHOLD = 3;

// AG-UI tool calls are OpenAI-shaped ({ function: { name, arguments } }); some
// CopilotKit paths flatten them to { name, args }. Read whichever is present.
function toolName(toolCall: any): string {
  return toolCall?.function?.name ?? toolCall?.name ?? "";
}

function parseArgs(toolCall: any): any {
  const args = toolCall?.function?.arguments ?? toolCall?.args;
  if (typeof args === "string") {
    try {
      return JSON.parse(args);
    } catch {
      return {};
    }
  }
  return args ?? {};
}

/**
 * Replaces CopilotKit's default per-tool rendering. Everything the agent did
 * is compressed into one collapsed "Steps" accordion; rich cards render below
 * for the tools that have one. Raw tool data is never shown.
 */
export default function ToolCallsView({
  message,
  messages,
}: {
  message: any;
  messages?: any[];
}) {
  const toolCalls: any[] = message?.toolCalls ?? [];

  const steps = toolCalls.map((tc) => {
    const toolMessage = (messages ?? []).find(
      (m) => m.role === "tool" && m.toolCallId === tc.id
    );
    return {
      id: tc.id,
      name: toolName(tc),
      args: parseArgs(tc),
      complete: toolMessage != null,
      result: toolMessage ? parseToolResult(toolMessage.content) : undefined,
    };
  });

  // Map article URL -> { date, title } from any articles result anywhere in the
  // conversation — the performance result carries no date/title, and the article
  // list is usually fetched in an earlier turn (a separate message).
  const articleMeta = new Map<string, { date?: string; title?: string }>();
  let perfCallCount = 0;
  for (const m of messages ?? []) {
    if (m.role === "assistant") {
      for (const tc of m.toolCalls ?? [])
        if (PERF_TOOLS.has(toolName(tc))) perfCallCount += 1;
      continue;
    }
    if (m.role !== "tool") continue;
    const parsed = parseToolResult(m.content);
    for (const a of parsed?.articles ?? []) {
      if (a?.article_link)
        articleMeta.set(a.article_link, {
          date: a.published_at,
          title: a.article_title,
        });
    }
  }
  // When the conversation ends up rendering a comparison chart, the standalone
  // "Latest articles" list was just a precursor to fetch the URLs — hide it.
  const suppressArticleList = perfCallCount > TREND_THRESHOLD;

  const perfSteps = steps.filter((s) => s.complete && PERF_TOOLS.has(s.name));
  const perfPoints: TrendPoint[] = perfSteps.map((step, idx) => {
    const url = step.args?.article_url ?? step.args?.note_url ?? step.args?.url;
    const meta = url ? articleMeta.get(url) : undefined;
    const title =
      meta?.title ?? step.result?.title ?? step.result?.description ?? `Item ${idx + 1}`;
    return {
      name: meta?.date ? formatDate(meta.date) : title.slice(0, 18),
      title,
      reactions: step.result?.reaction_count ?? 0,
      restacks: step.result?.restacks ?? 0,
      comments: step.result?.comment_count ?? step.result?.comments ?? 0,
      _date: meta?.date,
    } as TrendPoint & { _date?: string };
  });
  perfPoints.sort((a: any, b: any) =>
    a._date && b._date ? a._date.localeCompare(b._date) : 0
  );

  const done = steps.filter((s) => s.complete).length;
  const running = done < steps.length;
  // Auto-expand while tools run, auto-collapse once they all finish — unless the
  // user has manually toggled it (then their choice sticks).
  const [open, setOpen] = useState(running);
  const [touched, setTouched] = useState(false);
  useEffect(() => {
    if (!touched) setOpen(running);
  }, [running, touched]);

  if (toolCalls.length === 0) return null;

  return (
    <div className="my-2 max-w-2xl space-y-3">
      <div className="rounded-2xl bg-dark-card border border-white/10 overflow-hidden">
        <button
          onClick={() => {
            setTouched(true);
            setOpen((o) => !o);
          }}
          className="flex w-full items-center justify-between px-4 py-2.5 hover:bg-white/5 transition-colors"
        >
          <span className="flex items-center gap-2 text-sm text-gray-300">
            🔧 Steps{" "}
            <span className="text-gray-500">
              ({running ? `${done}/${steps.length}` : steps.length})
            </span>
          </span>
          <span
            className={`text-gray-500 text-xs transition-transform ${
              open ? "rotate-180" : ""
            }`}
          >
            ▾
          </span>
        </button>

        {running && (
          <div className="h-0.5 bg-white/10">
            <motion.div
              className="h-full bg-gradient-to-r from-neon-pink to-substack-orange"
              initial={{ width: 0 }}
              animate={{ width: `${(done / steps.length) * 100}%` }}
              transition={{ ease: "easeOut" }}
            />
          </div>
        )}

        <AnimatePresence initial={false}>
          {open && (
            <motion.ul
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden px-4 pb-3 space-y-1.5"
            >
              {steps.map((step) => (
                <li
                  key={step.id}
                  className="flex items-center gap-2 text-xs text-gray-400"
                >
                  {step.complete ? (
                    <span className="text-[#00FF88]">✓</span>
                  ) : (
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-substack-orange opacity-75" />
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-substack-orange" />
                    </span>
                  )}
                  <span>{TOOL_META[step.name]?.label ?? step.name}</span>
                </li>
              ))}
            </motion.ul>
          )}
        </AnimatePresence>
      </div>

      {steps.map((step) => {
        if (!step.complete) return null;
        if (step.name === "get_substack_articles")
          return suppressArticleList ? null : (
            <ArticlesCard key={step.id} data={step.result} />
          );
        if (step.name === "get_substack_notes")
          return <NotesCard key={step.id} data={step.result} />;
        return null;
      })}

      {/* Up to 3 specific items → detailed deep-dive cards; more → one trend chart. */}
      {perfSteps.length > TREND_THRESHOLD ? (
        <PerformanceTrendChart points={perfPoints} />
      ) : (
        perfSteps.map((step) => (
          <PerformanceCard
            key={step.id}
            data={step.result}
            articleUrl={step.args?.article_url}
          />
        ))
      )}
    </div>
  );
}
