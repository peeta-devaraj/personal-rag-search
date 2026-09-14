import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, BarChart3, History, ListChecks, Loader2, PlayCircle, Sparkles, Target, Trophy } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { getGenerateQaSetStatus, listEvalRuns, runEval, startGenerateQaSet } from "../api/client";
import Card from "../components/Card";
import MetricsChart from "../components/MetricsChart";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import type { EvalRunResult, EvalRunSummary } from "../types";
import { cn } from "../lib/utils";

const STRATEGY_LABELS: Record<string, string> = { bm25: "BM25", dense: "Dense", hybrid: "Hybrid + Rerank" };

function bestStrategy(results: Record<string, Record<string, number>>): { name: string; mrr: number } | null {
  const entries = Object.entries(results);
  if (entries.length === 0) return null;
  return entries
    .map(([name, m]) => ({ name, mrr: m.MRR ?? 0 }))
    .sort((a, b) => b.mrr - a.mrr)[0];
}

export default function EvalDashboardPage() {
  const [genStatus, setGenStatus] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [running, setRunning] = useState(false);
  const [current, setCurrent] = useState<EvalRunResult | null>(null);
  const [history, setHistory] = useState<EvalRunSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  const refreshHistory = () => {
    listEvalRuns()
      .then((r) => setHistory(r.runs))
      .catch(() => {});
  };

  useEffect(() => {
    refreshHistory();
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  const generateGoldSet = async () => {
    setError(null);
    setGenerating(true);
    setGenStatus("Starting...");
    try {
      const { job_id } = await startGenerateQaSet(100, false);
      pollRef.current = window.setInterval(async () => {
        const status = await getGenerateQaSetStatus(job_id);
        if (status.status === "done") {
          setGenStatus(`Generated ${status.generated_count} eval questions`);
          setGenerating(false);
          if (pollRef.current) window.clearInterval(pollRef.current);
        } else if (status.status === "failed") {
          setError(status.error || "Generation failed");
          setGenerating(false);
          if (pollRef.current) window.clearInterval(pollRef.current);
        } else {
          setGenStatus(status.status === "running" ? "Generating questions from your chunks..." : "Queued...");
        }
      }, 1500);
    } catch (e) {
      setError((e as Error).message);
      setGenerating(false);
    }
  };

  const runComparison = async () => {
    setRunning(true);
    setError(null);
    try {
      const result = await runEval([1, 3, 5, 10]);
      setCurrent(result);
      refreshHistory();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning(false);
    }
  };

  const best = current ? bestStrategy(current.results) : null;

  return (
    <>
      <PageHeader
        eyebrow="Evaluation"
        title="Retrieval eval dashboard"
        subtitle="Compares BM25-only, dense-only, and hybrid+rerank retrieval on a synthetic gold set generated from your own corpus — one auto-generated question per chunk."
      />

      <Card className="mb-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button onClick={generateGoldSet} disabled={generating} className="btn-secondary">
            {generating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
            1. Generate QA gold set
          </button>
          <button onClick={runComparison} disabled={running} className="btn-primary">
            {running ? <Loader2 size={14} className="animate-spin" /> : <PlayCircle size={14} />}
            2. Run Evaluation
          </button>
          {running && (
            <span className="text-[12.5px] text-zinc-500">
              Running BM25/dense/hybrid over your full corpus with cross-encoder reranking &mdash; can take a
              minute or two on larger libraries.
            </span>
          )}
          <AnimatePresence>
            {genStatus && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-[12.5px] text-zinc-500"
              >
                {genStatus}
              </motion.span>
            )}
          </AnimatePresence>
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

      <AnimatePresence>
        {current && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mb-6 grid grid-cols-3 gap-4"
          >
            <StatCard icon={ListChecks} label="Gold queries" value={String(current.num_queries)} />
            <StatCard
              icon={Trophy}
              label="Best strategy"
              value={best ? STRATEGY_LABELS[best.name] ?? best.name : "-"}
              hint={best ? `MRR ${best.mrr.toFixed(3)}` : undefined}
              delay={0.05}
            />
            <StatCard
              icon={Target}
              label="Hybrid nDCG@5"
              value={current.results.hybrid?.["nDCG@5"]?.toFixed(3) ?? "-"}
              delay={0.1}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {current && (
        <Card className="mb-6" delay={0.1}>
          <div className="mb-4 flex items-center gap-2 text-[13px] font-semibold text-zinc-200">
            <BarChart3 size={14} className="text-indigo-400" />
            Run #{current.run_id} results
          </div>
          <MetricsChart results={current.results} />

          <div className="mt-5 overflow-x-auto">
            <table className="w-full border-collapse text-[12.5px]">
              <thead>
                <tr className="border-b border-white/[0.06] text-left text-zinc-500">
                  <th className="pb-2 pr-4 font-medium">Metric</th>
                  {Object.keys(current.results).map((s) => (
                    <th key={s} className="pb-2 pr-4 font-medium">
                      {STRATEGY_LABELS[s] ?? s}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.keys(Object.values(current.results)[0] || {}).map((metric) => {
                  const values = Object.keys(current.results).map((s) => current.results[s][metric]);
                  const maxVal = Math.max(...values);
                  return (
                    <tr key={metric} className="border-b border-white/[0.03] text-zinc-400">
                      <td className="py-1.5 pr-4 font-medium text-zinc-300">{metric}</td>
                      {Object.keys(current.results).map((s) => (
                        <td
                          key={s}
                          className={cn(
                            "py-1.5 pr-4 tabular-nums",
                            current.results[s][metric] === maxVal && maxVal > 0 && "font-semibold text-emerald-400",
                          )}
                        >
                          {current.results[s][metric]}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Card delay={0.15}>
        <div className="mb-3 flex items-center gap-2 text-[13px] font-semibold text-zinc-200">
          <History size={14} className="text-zinc-500" />
          Run history
        </div>
        {history.length === 0 ? (
          <p className="py-6 text-center text-[13px] text-zinc-500">No eval runs yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-[12.5px]">
              <thead>
                <tr className="border-b border-white/[0.06] text-left text-zinc-500">
                  <th className="pb-2 pr-4 font-medium">Run</th>
                  <th className="pb-2 pr-4 font-medium">Timestamp</th>
                  <th className="pb-2 pr-4 font-medium">Queries</th>
                  <th className="pb-2 pr-4 font-medium">Hybrid nDCG@5</th>
                </tr>
              </thead>
              <tbody>
                {history.map((r) => (
                  <tr key={r.run_id} className="border-b border-white/[0.03] text-zinc-400 last:border-0">
                    <td className="py-1.5 pr-4 font-medium text-zinc-300">#{r.run_id}</td>
                    <td className="py-1.5 pr-4">{new Date(r.timestamp + "Z").toLocaleString()}</td>
                    <td className="py-1.5 pr-4 tabular-nums">{r.num_queries}</td>
                    <td className="py-1.5 pr-4 tabular-nums">{r.summary_metrics.hybrid?.["nDCG@5"] ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  );
}
