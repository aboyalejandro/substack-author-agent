"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import CardShell from "./CardShell";
import { CHART_AXIS, CHART_TOOLTIP, CHART_Y_AXIS } from "../lib";

export interface TrendPoint {
  name: string; // x label (publish date, or title fallback)
  title: string; // shown in tooltip
  reactions: number;
  restacks: number;
  comments: number;
}

const SERIES = [
  { key: "reactions", label: "Reactions", color: "#FF006E" },
  { key: "restacks", label: "Restacks", color: "#FF6719" },
  { key: "comments", label: "Comments", color: "#0066FF" },
] as const;

/**
 * One grouped-bar chart for >3 articles/notes: x = publish date, each article a
 * group of 3 colored bars (the metrics). Replaces a stack of per-item cards and
 * gives a clear per-article breakdown of all three metrics at a glance.
 */
export default function PerformanceTrendChart({
  points,
}: {
  points: TrendPoint[];
}) {
  if (points.length === 0) return <></>;

  return (
    <CardShell>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-black text-lg gradient-text">
          📊 Performance comparison
        </h3>
        <span className="text-xs text-gray-400">{points.length} items</span>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 mb-2">
        {SERIES.map((s) => (
          <span key={s.key} className="flex items-center gap-1.5 text-[11px] text-gray-400">
            <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
            {s.label}
          </span>
        ))}
      </div>

      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={points} margin={{ top: 4, right: 8, bottom: 16, left: 0 }} barCategoryGap="20%">
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis
              dataKey="name"
              {...CHART_AXIS}
              interval={0}
              angle={-35}
              textAnchor="end"
              height={48}
              tickMargin={8}
            />
            <YAxis {...CHART_Y_AXIS} />
            <Tooltip
              {...CHART_TOOLTIP}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              labelFormatter={(_, payload) =>
                payload?.[0]?.payload?.title ?? ""
              }
            />
            {SERIES.map((s) => (
              <Bar
                key={s.key}
                dataKey={s.key}
                fill={s.color}
                radius={[3, 3, 0, 0]}
                name={s.label}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Which article each x-point is (the chart x-axis is the publish date). */}
      <ul className="mt-3 space-y-1 border-t border-white/10 pt-2">
        {points.map((p, i) => (
          <li key={i} className="flex gap-2 text-[11px] text-gray-400">
            <span className="shrink-0 font-black text-white/40 w-14">{p.name}</span>
            <span className="truncate text-gray-300">{p.title}</span>
          </li>
        ))}
      </ul>
    </CardShell>
  );
}
