import type {
  AskResponse,
  DocumentOut,
  EvalRunResult,
  EvalRunSummary,
  HealthResponse,
  Strategy,
  UploadResultItem,
} from "../types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return request("/health");
}

export function listDocuments(): Promise<{ documents: DocumentOut[] }> {
  return request("/documents");
}

export async function uploadDocuments(files: File[]): Promise<{ uploaded: UploadResultItem[] }> {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  const res = await fetch(`${BASE}/documents/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Upload failed: ${res.status}`);
  }
  return res.json();
}

export function deleteDocument(id: number): Promise<{ deleted: boolean }> {
  return request(`/documents/${id}`, { method: "DELETE" });
}

export function askQuestion(question: string, strategy: Strategy, top_k = 5): Promise<AskResponse> {
  return request("/ask", {
    method: "POST",
    body: JSON.stringify({ question, strategy, top_k }),
  });
}

export function startGenerateQaSet(
  sample_size: number,
  force_regenerate: boolean,
): Promise<{ job_id: string; status: string }> {
  return request("/eval/generate-qa-set", {
    method: "POST",
    body: JSON.stringify({ sample_size, force_regenerate }),
  });
}

export function getGenerateQaSetStatus(
  jobId: string,
): Promise<{ job_id: string; status: string; generated_count?: number; error?: string }> {
  return request(`/eval/generate-qa-set/status/${jobId}`);
}

export function runEval(k_values: number[]): Promise<EvalRunResult> {
  return request("/eval/run", {
    method: "POST",
    body: JSON.stringify({ k_values }),
  });
}

export function listEvalRuns(): Promise<{ runs: EvalRunSummary[] }> {
  return request("/eval/runs");
}
