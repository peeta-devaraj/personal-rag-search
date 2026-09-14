import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

export default function StatCard({
  icon: Icon,
  label,
  value,
  hint,
  delay = 0,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  hint?: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: "easeOut" }}
      className="glass-card rounded-xl p-4"
    >
      <div className="mb-2 flex items-center gap-2 text-[11.5px] font-medium text-zinc-500">
        <Icon size={13} />
        {label}
      </div>
      <div className="text-xl font-bold tracking-tight text-zinc-50">{value}</div>
      {hint && <div className="mt-0.5 text-[11px] text-zinc-500">{hint}</div>}
    </motion.div>
  );
}
