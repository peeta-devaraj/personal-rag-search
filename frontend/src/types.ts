export interface DocumentOut {
  id: number;
  filename: string;
  filetype: string;
  upload_date: string;
  status: string;
  num_chunks: number;
  error_message: string | null;
}

export interface UploadResultItem {
  document_id: number;
  filename: string;
  status: string;
  error_message: string | null;
}

export interface Citation {
  chunk_id: number;
  document_id: number;
  filename: string;
  page_start: number | null;
  page_end: number | null;
  snippet: string;
  score: number;
}

export type Strategy = "hybrid" | "dense" | "bm25";

export interface AskResponse {
  answer: string;
  citations: Citation[];
  strategy_used: string;
  retrieval_ms: number;
  generation_ms: number;
}

export interface HealthResponse {
  status: string;
  ollama_reachable: boolean;
  model: string;
  embed_model: string;
}

export interface EvalMetrics {
  [metric: string]: number;
}

export interface EvalRunResult {
  run_id: number;
  results: Record<string, EvalMetrics>;
  num_queries: number;
  timestamp: string;
}

export interface EvalRunSummary {
  run_id: number;
  timestamp: string;
  num_queries: number;
  summary_metrics: Record<string, EvalMetrics>;
}
