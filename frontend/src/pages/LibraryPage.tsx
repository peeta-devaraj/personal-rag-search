import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, FileStack } from "lucide-react";
import { useEffect, useState } from "react";
import { deleteDocument, listDocuments, uploadDocuments } from "../api/client";
import Card from "../components/Card";
import DocumentList from "../components/DocumentList";
import PageHeader from "../components/PageHeader";
import UploadDropzone from "../components/UploadDropzone";
import type { DocumentOut } from "../types";

export default function LibraryPage() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    listDocuments()
      .then((r) => setDocuments(r.documents))
      .catch((e) => setError(e.message));
  };

  useEffect(refresh, []);

  const handleFiles = async (files: File[]) => {
    setUploading(true);
    setError(null);
    try {
      const result = await uploadDocuments(files);
      const failed = result.uploaded.filter((u) => u.status === "failed" || u.status === "rejected");
      if (failed.length > 0) {
        setError(failed.map((f) => `${f.filename}: ${f.error_message}`).join("; "));
      }
      refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    setDocuments((prev) => prev.filter((d) => d.id !== id));
    await deleteDocument(id);
    refresh();
  };

  const totalChunks = documents.reduce((sum, d) => sum + d.num_chunks, 0);

  return (
    <>
      <PageHeader
        eyebrow="Library"
        title="Your documents"
        subtitle="Upload notes, lecture PDFs, or papers. Each file is chunked, embedded, and indexed for both semantic and keyword search."
      />

      <Card className="mb-5">
        <UploadDropzone onFiles={handleFiles} disabled={uploading} />
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 flex items-start gap-2 overflow-hidden rounded-lg bg-rose-500/10 px-3.5 py-2.5 text-[12.5px] text-rose-300 ring-1 ring-rose-500/20"
            >
              <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      <Card delay={0.05}>
        <div className="mb-1 flex items-center justify-between">
          <div className="flex items-center gap-2 text-[13px] font-medium text-zinc-300">
            <FileStack size={14} className="text-zinc-500" />
            {documents.length} document{documents.length !== 1 ? "s" : ""}
          </div>
          <div className="text-[12px] text-zinc-500">{totalChunks} chunks indexed</div>
        </div>
        <DocumentList documents={documents} onDelete={handleDelete} />
      </Card>
    </>
  );
}
