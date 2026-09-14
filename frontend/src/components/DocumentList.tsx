import { AnimatePresence, motion } from "framer-motion";
import { FileText, Inbox, Trash2 } from "lucide-react";
import type { DocumentOut } from "../types";
import StatusBadge from "./StatusBadge";

interface Props {
  documents: DocumentOut[];
  onDelete: (id: number) => void;
}

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso + "Z").getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function DocumentList({ documents, onDelete }: Props) {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-14 text-center">
        <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white/[0.04] ring-1 ring-white/10">
          <Inbox size={18} className="text-zinc-500" />
        </div>
        <p className="text-[13px] text-zinc-500">No documents indexed yet. Upload something above to get started.</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-white/[0.05]">
      <AnimatePresence initial={false}>
        {documents.map((d) => (
          <motion.div
            key={d.id}
            layout
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="group flex items-center gap-3.5 px-1 py-3.5"
          >
            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-white/[0.04] ring-1 ring-white/[0.06]">
              <FileText size={15} className="text-zinc-400" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-[13.5px] font-medium text-zinc-200">{d.filename}</div>
              <div className="mt-0.5 flex items-center gap-2 text-[11.5px] text-zinc-500">
                <span className="uppercase">{d.filetype}</span>
                <span>&middot;</span>
                <span>{d.num_chunks} chunks</span>
                <span>&middot;</span>
                <span>{timeAgo(d.upload_date)}</span>
                {d.error_message && <span className="text-rose-400">&middot; {d.error_message}</span>}
              </div>
            </div>
            <StatusBadge status={d.status} />
            <button
              onClick={() => onDelete(d.id)}
              className="rounded-md p-2 text-zinc-600 opacity-0 transition-all hover:bg-rose-500/10 hover:text-rose-400 group-hover:opacity-100"
              aria-label={`Delete ${d.filename}`}
            >
              <Trash2 size={14} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
