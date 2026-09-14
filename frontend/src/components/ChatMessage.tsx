import { motion } from "framer-motion";
import { Clock, Sparkles, User } from "lucide-react";
import { forwardRef } from "react";
import type { AskResponse } from "../types";
import CitationCard from "./CitationCard";

const ChatMessage = forwardRef<HTMLDivElement, { question: string; response: AskResponse }>(
  ({ question, response }, ref) => {
    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="mb-5"
      >
        <div className="mb-3 flex items-start gap-3">
          <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-white/[0.06] ring-1 ring-white/10">
            <User size={12} className="text-zinc-400" />
          </div>
          <p className="pt-0.5 text-[14px] font-medium text-zinc-200">{question}</p>
        </div>

        <div className="flex items-start gap-3">
          <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-brand-gradient">
            <Sparkles size={12} className="text-white" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="glass-card rounded-xl rounded-tl-sm p-4">
              <p className="text-[13.5px] leading-relaxed text-zinc-200">{response.answer}</p>

              {response.citations.length > 0 && (
                <div className="mt-3.5 flex flex-col gap-1.5">
                  {response.citations.map((c, i) => (
                    <CitationCard key={c.chunk_id} citation={c} index={i} />
                  ))}
                </div>
              )}
            </div>
            <div className="mt-2 flex items-center gap-3 px-1 text-[11px] text-zinc-600">
              <span className="rounded bg-white/[0.04] px-1.5 py-0.5 font-medium capitalize text-zinc-500">
                {response.strategy_used}
              </span>
              <span className="flex items-center gap-1">
                <Clock size={10} />
                {response.retrieval_ms.toFixed(0)}ms retrieval &middot; {response.generation_ms.toFixed(0)}ms
                generation
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    );
  },
);
ChatMessage.displayName = "ChatMessage";

export default ChatMessage;
