import { motion } from "framer-motion";
import type { ReactNode } from "react";

export default function PageHeader({
  eyebrow,
  title,
  subtitle,
  action,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="mb-8 flex items-start justify-between gap-6"
    >
      <div>
        {eyebrow && (
          <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-indigo-400/80">
            {eyebrow}
          </div>
        )}
        <h1 className="text-2xl font-bold tracking-tight text-zinc-50">{title}</h1>
        {subtitle && <p className="mt-2 max-w-xl text-[13.5px] leading-relaxed text-zinc-400">{subtitle}</p>}
      </div>
      {action}
    </motion.div>
  );
}
