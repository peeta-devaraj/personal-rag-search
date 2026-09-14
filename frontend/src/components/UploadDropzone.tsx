import { motion } from "framer-motion";
import { Loader2, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { cn } from "../lib/utils";

interface Props {
  onFiles: (files: File[]) => void;
  disabled?: boolean;
}

export default function UploadDropzone({ onFiles, disabled }: Props) {
  const [active, setActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <motion.div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setActive(true);
      }}
      onDragLeave={() => setActive(false)}
      onDrop={(e) => {
        e.preventDefault();
        setActive(false);
        if (disabled) return;
        onFiles(Array.from(e.dataTransfer.files));
      }}
      animate={{ scale: active ? 1.01 : 1 }}
      transition={{ duration: 0.15 }}
      className={cn(
        "group relative flex cursor-pointer flex-col items-center justify-center gap-3 overflow-hidden rounded-xl border border-dashed px-6 py-12 text-center transition-colors duration-200",
        disabled
          ? "cursor-not-allowed border-white/10 bg-white/[0.02]"
          : active
            ? "border-indigo-400/60 bg-indigo-500/[0.06]"
            : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.03]",
      )}
    >
      <div
        className={cn(
          "absolute inset-0 bg-brand-gradient-soft opacity-0 transition-opacity duration-300",
          active && "opacity-100",
        )}
      />
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.txt,.md"
        style={{ display: "none" }}
        onChange={(e) => {
          if (e.target.files) onFiles(Array.from(e.target.files));
          e.target.value = "";
        }}
      />
      <div
        className={cn(
          "relative flex h-11 w-11 items-center justify-center rounded-full border transition-colors",
          active ? "border-indigo-400/40 bg-indigo-500/10" : "border-white/10 bg-white/[0.04]",
        )}
      >
        {disabled ? (
          <Loader2 size={18} className="animate-spin text-indigo-300" />
        ) : (
          <UploadCloud size={18} className={active ? "text-indigo-300" : "text-zinc-400"} />
        )}
      </div>
      <div className="relative">
        <p className="text-[13.5px] font-medium text-zinc-200">
          {disabled ? "Processing your documents..." : "Drop files here, or click to browse"}
        </p>
        <p className="mt-1 text-[12px] text-zinc-500">PDF, TXT, or MD &middot; chunked and embedded automatically</p>
      </div>
    </motion.div>
  );
}
