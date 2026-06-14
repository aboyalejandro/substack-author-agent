"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import CardShell from "./CardShell";
import {
  CHART_AXIS,
  CHART_TOOLTIP,
  CHART_Y_AXIS,
  formatDate,
  totalReactions,
} from "../lib";

const PREVIEW_COUNT = 5;

interface Note {
  id: number;
  body: string;
  reactions?: Record<string, number>;
  restacks?: number;
  published_at?: string;
}

export default function NotesCard({ data }: { data: any }) {
  const [expanded, setExpanded] = useState(false);
  const notes: Note[] = data?.notes ?? [];
  if (notes.length === 0) return <></>;

  const visible = expanded ? notes : notes.slice(0, PREVIEW_COUNT);
  const hidden = notes.length - visible.length;

  const chartData = notes.map((note, idx) => ({
    name: `#${idx + 1}`,
    reactions: totalReactions(note.reactions),
    restacks: note.restacks ?? 0,
  }));

  return (
    <CardShell>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-black text-lg gradient-text">📝 Recent notes</h3>
        <span className="text-xs text-gray-400">{notes.length} notes</span>
      </div>

      <div className="h-32 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} barCategoryGap="30%">
            <XAxis dataKey="name" {...CHART_AXIS} />
            <YAxis {...CHART_Y_AXIS} />
            <Tooltip {...CHART_TOOLTIP} />
            <Bar
              dataKey="reactions"
              fill="#FF006E"
              radius={[4, 4, 0, 0]}
              name="Reactions"
            />
            <Bar
              dataKey="restacks"
              fill="#00FF88"
              radius={[4, 4, 0, 0]}
              name="Restacks"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-2">
        {visible.map((note, idx) => (
          <motion.div
            key={note.id ?? idx}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + idx * 0.06 }}
            className="bg-white/5 rounded-xl p-3"
          >
            <div className="flex items-center gap-2 text-[11px] text-gray-500 mb-1">
              <span className="font-black text-white/40">#{idx + 1}</span>
              <span>{formatDate(note.published_at)}</span>
              <span className="ml-auto flex gap-2">
                <span>❤️ {totalReactions(note.reactions)}</span>
                <span>🔄 {note.restacks ?? 0}</span>
              </span>
            </div>
            <p className="text-xs text-gray-300 line-clamp-3 whitespace-pre-line">
              {note.body}
            </p>
          </motion.div>
        ))}
      </div>
      {notes.length > PREVIEW_COUNT && (
        <button
          onClick={() => setExpanded((e) => !e)}
          className="mt-2.5 w-full text-xs text-gray-400 hover:text-white transition-colors py-1.5"
        >
          {expanded ? "Show less" : `See ${hidden} more →`}
        </button>
      )}
    </CardShell>
  );
}
