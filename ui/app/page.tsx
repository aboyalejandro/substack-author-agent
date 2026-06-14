"use client";

import { CopilotKitProvider } from "@copilotkit/react-core/v2";
import { motion } from "framer-motion";
import Chat from "@/components/Chat";

export default function Home() {
  return (
    <CopilotKitProvider runtimeUrl="/api/copilotkit">
      <main className="min-h-screen bg-dark-bg text-white relative overflow-hidden flex flex-col">
        {/* Animated neon background (cloned from substackrecapped.com) */}
        <div className="absolute inset-0 opacity-10 pointer-events-none">
          <motion.div
            className="absolute top-20 left-10 w-96 h-96 rounded-full bg-neon-pink blur-3xl"
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute bottom-20 right-10 w-96 h-96 rounded-full bg-neon-blue blur-3xl"
            animate={{ scale: [1.2, 1, 1.2], opacity: [0.5, 0.3, 0.5] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>

        <div className="relative z-10 max-w-4xl w-full mx-auto px-4 py-8 flex flex-col flex-1">
          <motion.header
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-6"
          >
            <h1 className="text-4xl md:text-5xl font-black mb-2 bg-gradient-to-r from-neon-pink via-substack-orange to-neon-blue bg-clip-text text-transparent">
              Substack Author Agent
            </h1>
            <p className="text-gray-400 text-sm md:text-base">
              Your content strategy copilot — articles, notes, ideas & brand
              voice
            </p>
          </motion.header>

          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15 }}
            className="gradient-border flex-1 flex min-h-0"
          >
            <div className="rounded-2xl bg-dark-card w-full overflow-hidden flex flex-col min-h-[70vh]">
              <Chat />
            </div>
          </motion.div>

          <footer className="text-center text-[11px] text-gray-600 mt-4">
            Powered by Agno + CopilotKit (AG-UI) · The Pipe and the Line
          </footer>
        </div>
      </main>
    </CopilotKitProvider>
  );
}
