import { cn } from "../lib/utils";

const STYLES: Record<string, string> = {
  ready: "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20",
  processing: "bg-amber-500/10 text-amber-400 ring-amber-500/20",
  failed: "bg-rose-500/10 text-rose-400 ring-rose-500/20",
  rejected: "bg-rose-500/10 text-rose-400 ring-rose-500/20",
};

const DOT: Record<string, string> = {
  ready: "bg-emerald-400",
  processing: "bg-amber-400 animate-pulse-dot",
  failed: "bg-rose-400",
  rejected: "bg-rose-400",
};

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium capitalize ring-1 ring-inset",
        STYLES[status] ?? "bg-zinc-500/10 text-zinc-400 ring-zinc-500/20",
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", DOT[status] ?? "bg-zinc-400")} />
      {status}
    </span>
  );
}
