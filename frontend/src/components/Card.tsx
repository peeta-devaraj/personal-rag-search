import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "../lib/utils";

export default function Card({
  children,
  className,
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: "easeOut" }}
      className={cn("glass-card rounded-xl p-5", className)}
    >
      {children}
    </motion.div>
  );
}
