"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

/** Shared gradient-border + dark backdrop wrapper used by every result card. */
export default function CardShell({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="gradient-border my-3 max-w-2xl"
    >
      <div className="rounded-2xl bg-dark-card p-4">{children}</div>
    </motion.div>
  );
}
