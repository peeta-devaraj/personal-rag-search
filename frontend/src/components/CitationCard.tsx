import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, FileText } from "lucide-react";
import { useState } from "react";
import type { Citation } from "../types";
import { cn } from "../lib/utils";

export default function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const [open, setOpen] = useState(false);

  const pages =
    citation.page_start && citation.page_end
      ? citation.page_start === citation.page_end
        ? `p. ${citation.page_start}`
        : `pp. ${citation.page_start}-${citation.page_end}`
      : null;

  return (
    <div className="overflow-hidden rounded-lg border border-white/[0.06] bg-white/[0.02]">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2.5 px-3 py-2 text-left transition-colors hover:bg-white/[0.03]"
      >
        <span className="flex h-4.5 w-4.5 flex-shrink-0 items-center justify-center rounded bg-indigo-500/15 text-[10px] font-semibold text-indigo-300">
          {index + 1}
        </span>
        <FileText size={12} className="flex-shrink-0 text-zinc-500" />
        <span className="min-w-0 flex-1 truncate text-[12.5px] font-medium text-zinc-300">{citation.filename}</span>
        {pages && <span className="flex-shrink-0 text-[11px] text-zinc-500">{pages}</span>}
        <span className="flex-shrink-0 text-[11px] tabular-nums text-zinc-600">{citation.score.toFixed(2)}</span>
        <ChevronDown
          size={13}
          className={cn("flex-shrink-0 text-zinc-600 transition-transform duration-200", open && "rotate-180")}
        />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            <p className="border-t border-white/[0.06] px-3.5 py-3 text-[12.5px] leading-relaxed text-zinc-400">
              {citation.snippet}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
