"use client";

import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import CardShell from "./CardShell";
import { useSendFollowUp } from "../useSendFollowUp";
import { CHART_AXIS, CHART_TOOLTIP, CHART_Y_AXIS } from "../lib";

export default function PerformanceCard({
  data,
  articleUrl,
}: {
  data: any;
  articleUrl?: string;
}) {
  const send = useSendFollowUp();
  const ref = data?.title ?? articleUrl ?? "this article";
  const drill = (metric: string) =>
    send(
      `Dig into the ${metric.toLowerCase()} for "${ref}" — what's driving it and how does it compare to my other articles?`
    );
  const metrics = [
    { name: "Reactions", value: data?.reaction_count ?? 0, emoji: "❤️", color: "#FF006E" },
    { name: "Restacks", value: data?.restacks ?? 0, emoji: "🔄", color: "#FF6719" },
    {
      name: "Comments",
      value: data?.comment_count ?? data?.comments ?? 0,
      emoji: "💬",
      color: "#0066FF",
    },
  ];

  return (
    <CardShell>
      <div className="flex items-start gap-3 mb-3">
        {data?.cover_image && (
          <img
            src={data.cover_image}
            alt=""
            className="w-12 h-16 object-cover rounded-lg shrink-0"
          />
        )}
        <div className="min-w-0">
          <h3 className="font-black text-lg gradient-text">
            📊 Article performance
          </h3>
          {(data?.description || articleUrl) && (
            <p className="text-xs text-gray-400 mt-1 line-clamp-2">
              {data?.description ?? articleUrl}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-4">
        {metrics.map((metric, idx) => (
          <motion.button
            key={metric.name}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + idx * 0.08 }}
            onClick={() => drill(metric.name)}
            title={`Drill into ${metric.name}`}
            className="bg-white/5 hover:bg-white/10 rounded-xl p-3 text-center transition-colors cursor-pointer"
          >
            <div className="text-xl">{metric.emoji}</div>
            <div className="text-2xl font-black" style={{ color: metric.color }}>
              {metric.value.toLocaleString()}
            </div>
            <div className="text-[11px] text-gray-400">{metric.name}</div>
          </motion.button>
        ))}
      </div>

      <div className="h-36">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={metrics} barCategoryGap="25%">
            <XAxis dataKey="name" {...CHART_AXIS} />
            <YAxis {...CHART_Y_AXIS} />
            <Tooltip {...CHART_TOOLTIP} />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {metrics.map((metric) => (
                <Cell key={metric.name} fill={metric.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </CardShell>
  );
}
