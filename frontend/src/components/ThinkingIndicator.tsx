import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { forwardRef } from "react";

const ThinkingIndicator = forwardRef<HTMLDivElement>((_props, ref) => {
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="mb-5 flex items-center gap-3"
    >
      <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-brand-gradient">
        <Sparkles size={12} className="text-white" />
      </div>
      <div className="glass-card flex items-center gap-1.5 rounded-xl rounded-tl-sm px-4 py-3.5">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-zinc-400"
            animate={{ opacity: [0.25, 1, 0.25] }}
            transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.15, ease: "easeInOut" }}
          />
        ))}
      </div>
    </motion.div>
  );
});
ThinkingIndicator.displayName = "ThinkingIndicator";

export default ThinkingIndicator;
