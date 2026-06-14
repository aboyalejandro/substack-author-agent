"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import CardShell from "./CardShell";
import { useSendFollowUp } from "../useSendFollowUp";
import { formatDate } from "../lib";

const PREVIEW_COUNT = 5;

interface Article {
  article_title: string;
  article_link: string;
  subtitle?: string;
  published_at?: string;
  word_count?: number;
  post_type?: string;
  cover_image?: string;
}

export default function ArticlesCard({ data }: { data: any }) {
  const [expanded, setExpanded] = useState(false);
  const send = useSendFollowUp();
  const articles: Article[] = data?.articles ?? [];
  if (articles.length === 0) return <></>;

  const visible = expanded ? articles : articles.slice(0, PREVIEW_COUNT);
  const hidden = articles.length - visible.length;

  return (
    <CardShell>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-black text-lg gradient-text">📰 Latest articles</h3>
        <span className="text-xs text-gray-400">
          {articles.length} of {data?.total_articles_found ?? articles.length}
        </span>
      </div>
      <div className="space-y-2.5">
        {visible.map((article, idx) => (
          <motion.div
            key={article.article_link ?? idx}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + idx * 0.08 }}
            className="group flex gap-3 bg-white/5 hover:bg-white/10 transition-colors rounded-xl p-3"
          >
            {article.cover_image && (
              <img
                src={article.cover_image}
                alt=""
                className="w-14 h-20 object-cover rounded-lg shrink-0"
              />
            )}
            <div className="min-w-0 flex-1">
              <a
                href={article.article_link}
                target="_blank"
                rel="noopener noreferrer"
                className="font-bold text-sm text-white leading-tight hover:underline"
              >
                {article.article_title}
              </a>
              {article.subtitle && (
                <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                  {article.subtitle}
                </p>
              )}
              <div className="flex items-center gap-3 mt-2 text-[11px] text-gray-500">
                <span>{formatDate(article.published_at)}</span>
                {article.word_count != null && (
                  <span>✍️ {article.word_count.toLocaleString()} words</span>
                )}
                {article.post_type && <span>{article.post_type}</span>}
                <button
                  onClick={() =>
                    send(
                      `Show me the performance for "${article.article_title}": ${article.article_link}`
                    )
                  }
                  className="ml-auto text-substack-orange opacity-0 group-hover:opacity-100 transition-opacity hover:underline"
                >
                  📊 Performance
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      {(hidden > 0 || expanded) && articles.length > PREVIEW_COUNT && (
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
