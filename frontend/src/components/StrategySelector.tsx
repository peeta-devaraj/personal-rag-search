import { motion } from "framer-motion";
import { Combine, Hash, Sparkles } from "lucide-react";
import type { Strategy } from "../types";
import { cn } from "../lib/utils";

const OPTIONS: { value: Strategy; label: string; icon: typeof Combine }[] = [
  { value: "hybrid", label: "Hybrid + Rerank", icon: Combine },
  { value: "dense", label: "Dense", icon: Sparkles },
  { value: "bm25", label: "BM25", icon: Hash },
];

export default function StrategySelector({
  value,
  onChange,
}: {
  value: Strategy;
  onChange: (s: Strategy) => void;
}) {
  return (
    <div className="inline-flex items-center gap-0.5 rounded-lg bg-white/[0.03] p-1 ring-1 ring-white/[0.06]">
      {OPTIONS.map((opt) => {
        const active = opt.value === value;
        const Icon = opt.icon;
        return (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            className="relative rounded-md px-3 py-1.5 text-[12.5px] font-medium transition-colors"
          >
            {active && (
              <motion.div
                layoutId="strategy-pill"
                className="absolute inset-0 rounded-md bg-white/[0.08] ring-1 ring-inset ring-white/10"
                transition={{ type: "spring", stiffness: 500, damping: 40 }}
              />
            )}
            <span className={cn("relative flex items-center gap-1.5", active ? "text-white" : "text-zinc-500 hover:text-zinc-300")}>
              <Icon size={12.5} />
              {opt.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
