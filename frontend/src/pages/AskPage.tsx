import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, MessageSquareText, Send } from "lucide-react";
import { useState } from "react";
import { askQuestion } from "../api/client";
import Card from "../components/Card";
import ChatMessage from "../components/ChatMessage";
import PageHeader from "../components/PageHeader";
import StrategySelector from "../components/StrategySelector";
import ThinkingIndicator from "../components/ThinkingIndicator";
import type { AskResponse, Strategy } from "../types";

interface Turn {
  question: string;
  response: AskResponse;
}

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [strategy, setStrategy] = useState<Strategy>("hybrid");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);

  const submit = async () => {
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    const q = question;
    setQuestion("");
    try {
      const response = await askQuestion(q, strategy);
      setTurns((prev) => [{ question: q, response }, ...prev]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Ask"
        title="Ask your documents"
        subtitle="Answers are grounded in your library and cited back to the exact passage they came from."
      />

      <Card className="mb-6">
        <div className="mb-3 flex items-center justify-between">
          <StrategySelector value={strategy} onChange={setStrategy} />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            className="input-base"
            placeholder="Ask something about your notes..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />
          <button onClick={submit} disabled={loading || !question.trim()} className="btn-primary flex-shrink-0 px-3.5">
            <Send size={15} />
          </button>
        </div>
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

      <AnimatePresence mode="popLayout">{loading && <ThinkingIndicator key="thinking" />}</AnimatePresence>

      {turns.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white/[0.04] ring-1 ring-white/10">
            <MessageSquareText size={18} className="text-zinc-500" />
          </div>
          <p className="max-w-xs text-[13px] text-zinc-500">
            Upload documents in the Library, then ask a question grounded in them.
          </p>
        </div>
      )}

      <AnimatePresence mode="popLayout">
        {turns.map((t, i) => (
          <ChatMessage key={turns.length - i} question={t.question} response={t.response} />
        ))}
      </AnimatePresence>
    </>
  );
}
