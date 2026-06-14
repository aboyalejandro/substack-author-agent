/**
 * MCP tool results can arrive as a JSON string, an object, or an MCP
 * content array ([{type: "text", text: "{...}"}]). Normalize to an object.
 */
export function parseToolResult(result: unknown): any {
  if (result == null) return null;

  if (typeof result === "string") {
    try {
      return parseToolResult(JSON.parse(result));
    } catch {
      return { text: result };
    }
  }

  if (Array.isArray(result)) {
    const textItem = result.find(
      (item) => item?.type === "text" && typeof item.text === "string"
    );
    if (textItem) return parseToolResult(textItem.text);
  }

  if (typeof result === "object") {
    const obj = result as Record<string, unknown>;
    if (Array.isArray(obj.content)) return parseToolResult(obj.content);
    return obj;
  }

  return { text: String(result) };
}

export function formatDate(value?: string): string {
  if (!value) return "";
  const date = new Date(value.replace(" ", "T"));
  if (isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function totalReactions(reactions?: Record<string, number>): number {
  if (!reactions) return 0;
  return Object.values(reactions).reduce((sum, n) => sum + n, 0);
}

/** Shared recharts styling so every card chart looks identical. */
export const CHART_AXIS = {
  stroke: "#6b7280",
  fontSize: 11,
  tickLine: false,
  axisLine: false,
} as const;

export const CHART_Y_AXIS = {
  ...CHART_AXIS,
  allowDecimals: false,
  width: 28,
} as const;

export const CHART_TOOLTIP = {
  cursor: { fill: "rgba(255,255,255,0.05)" },
  contentStyle: {
    background: "#1A1A1A",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 12,
    color: "#fff",
  },
} as const;

/**
 * Single source of truth for the present-progressive label shown in the Steps
 * accordion while each MCP tool runs.
 */
export const TOOL_META: Record<string, { label: string }> = {
  get_substack_articles: { label: "Fetching articles" },
  get_article_performance: { label: "Pulling article metrics" },
  get_substack_notes: { label: "Fetching notes" },
  get_article_content: { label: "Reading article" },
  get_article_comments: { label: "Reading article comments" },
  get_note_comments: { label: "Reading note comments" },
  get_note_performance: { label: "Pulling note metrics" },
  search_articles: { label: "Searching articles" },
  get_cover_image: { label: "Fetching cover image" },
};
