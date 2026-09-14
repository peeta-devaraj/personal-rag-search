# Personal RAG Search

A fully local semantic search + Q&A tool over your own notes, lecture PDFs, or papers — a small-scale
Retrieval-Augmented Generation (RAG) system, but grounded in real Information Retrieval mechanics rather
than a thin wrapper around an LLM API.

Upload your documents, ask questions in natural language, and get answers with inline citations back to
the exact passage they came from. Everything runs on your machine: embeddings via `sentence-transformers`,
generation via a local [Ollama](https://ollama.com) model, retrieval via ChromaDB + BM25. No cloud API
keys, no cost, works offline.

## Why this isn't just a LangChain demo

The retrieval pipeline is the point of the project, not an afterthought:

- **Hybrid retrieval**: dense (embedding cosine similarity) and sparse (BM25) retrieval run independently
  and are combined with **Reciprocal Rank Fusion (RRF)**, since the two scoring scales aren't comparable.
- **Cross-encoder re-ranking**: the fused candidate set is re-scored by a cross-encoder
  (`cross-encoder/ms-marco-MiniLM-L-6-v2`), which jointly encodes (query, passage) pairs for higher
  precision than the bi-encoder similarity used for initial retrieval.
- **A real evaluation harness**: since there's no query log for a personal corpus, the app auto-generates
  a synthetic labeled eval set (one question per chunk, written by the local LLM) and reports
  **Precision@k, Recall@k, MRR, and nDCG@k** comparing BM25-only vs dense-only vs hybrid+rerank — on
  *your own documents*, not a public benchmark.

## Architecture

```
┌─────────────┐   upload    ┌──────────────────┐
│   React     │ ──────────▶ │  FastAPI backend │
│  (Vite+TS)  │ ◀────────── │                  │
└─────────────┘   ask/eval  └──────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
             ┌───────────┐  ┌───────────┐  ┌────────────┐
             │  SQLite   │  │ ChromaDB  │  │  rank_bm25 │
             │ (docs,    │  │ (dense    │  │ (sparse    │
             │  chunks,  │  │  vectors) │  │  index)    │
             │  eval)    │  │           │  │            │
             └───────────┘  └───────────┘  └────────────┘
                                   │              │
                                   └──────┬───────┘
                                          ▼
                              Reciprocal Rank Fusion
                                          ▼
                              Cross-encoder re-rank
                                          ▼
                                Ollama (local LLM)
                                          ▼
                              Answer + citations
```

## Retrieval pipeline in detail

1. **Ingestion** (`app/ingestion/`): PDF/txt/md → text per page (PyMuPDF) → sentence-aware chunking with
   overlap, targeting ~300 tokens/chunk with ~50 tokens of overlap carried between chunks so context isn't
   lost at boundaries.
2. **Indexing** (`app/retrieval/indexing.py`): each chunk is embedded with `BAAI/bge-small-en-v1.5` and
   upserted into a persistent ChromaDB collection; the BM25 index is rebuilt from all chunks (cheap at
   personal-corpus scale).
3. **Retrieval** (`app/retrieval/hybrid.py`): a query is embedded (with BGE's required query-side
   instruction prefix) and searched against both the vector store and BM25 index, each returning their
   top ~20 candidates. The two ranked lists are fused with RRF (`k=60`), and the fused top candidates are
   re-scored by the cross-encoder before the final top-k is selected.
4. **Generation** (`app/generation/qa.py`): the top-k passages are stuffed into a prompt instructing the
   model to answer only from the provided passages and cite them inline (`[1]`, `[2]`, ...).

## Evaluation methodology

Since a personal corpus has no real query history to evaluate against, the eval harness builds a
**synthetic gold set**: for each indexed chunk, the local LLM is prompted to write one question that
chunk uniquely and directly answers. `(question, source_chunk_id)` becomes a gold pair — the chunk is
known-relevant by construction.

For each gold question, three retrieval strategies are run (BM25-only, dense-only, hybrid+rerank) and
scored against the known-relevant chunk using standard IR metrics (`app/eval/metrics.py`):

- **Precision@k / Recall@k** — hit-rate based, since each query has exactly one relevant chunk
- **MRR** — mean reciprocal rank of the relevant chunk across all gold queries
- **nDCG@k** — implemented generically (supports graded relevance) even though this gold set is binary

Results are persisted per run (`eval_runs` table) with model/config metadata, so you can compare
before/after when tuning chunk size, RRF parameters, or swapping models.

**Known limitation, stated explicitly rather than hidden:** synthetic questions generated from a passage
tend to be lexically close to that passage's own wording, which can inflate BM25's apparent performance
relative to how it would do against real, more loosely-worded user queries. Treat the eval numbers as a
tool for *comparing retrieval strategies against each other on your corpus*, not as an absolute benchmark.
The comparison is only meaningful with a reasonably sized corpus — on the 7-document bundled sample
corpus, an example run scored `MRR: bm25=0.929, dense=1.0, hybrid=1.0` (one gold question paraphrased its
source chunk enough that a purely lexical match fell to rank 2, while both embedding-based strategies
still ranked it first). With only a handful of chunks this gap is small; load your own larger, more
topically overlapping corpus to see the strategies differentiate further.

## Setup

### Prerequisites

- Python 3.11+, Node.js 18+
- [Ollama](https://ollama.com) installed, with `ollama serve` running
- An instruct-capable model pulled, e.g. `ollama pull llama3.1:8b-instruct-q4_K_M` (any modern
  instruct model works — see `backend/.env.example` to configure which one)

### Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt   # Windows; use venv/bin/pip on macOS/Linux
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
copy .env.example .env    # edit OLLAMA_MODEL if needed
./venv/Scripts/python -m app.seed_corpus          # loads the bundled sample corpus
./venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

The first request that touches embeddings/reranking will download the corresponding model from
Hugging Face (a few hundred MB total) — this only happens once.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api/*` to `http://localhost:8000`.

### Verifying it works

1. **Library** — the bundled sample corpus (a handful of short IR/ML notes on BM25, PageRank,
   transformers, embeddings, evaluation metrics, inverted indexes, and query expansion) should already be
   listed with status `ready` if you ran the seed script. Upload your own PDFs/notes here too.
2. **Ask** — ask a question, e.g. *"What role does the damping factor play in PageRank?"* and confirm the
   answer cites the right passage. Try switching the strategy dropdown between Hybrid/Dense/BM25 to see
   retrieval differ (an exact-keyword query favors BM25; a paraphrase favors dense).
3. **Eval Dashboard** — click "Generate QA gold set", then "Run Evaluation" to see the metrics comparison
   chart across strategies.

## Project layout

```
backend/app/
  ingestion/    loader.py, chunker.py, pipeline.py       — file → text → chunks → persisted
  retrieval/    embeddings.py, vector_store.py,
                bm25_index.py, fusion.py, reranker.py,
                hybrid.py, retrieve.py                    — the core IR pipeline
  generation/   ollama_client.py, prompt_templates.py,
                qa.py                                     — retrieval-augmented answer generation
  eval/         generate_qa_pairs.py, metrics.py,
                runner.py, storage.py                      — the evaluation harness
  api/          routes_documents.py, routes_ask.py,
                routes_eval.py, routes_health.py           — FastAPI routes
frontend/src/
  pages/        LibraryPage, AskPage, EvalDashboardPage
  components/   Layout, PageHeader, Card, UploadDropzone, DocumentList,
                StatusBadge, StrategySelector, ChatMessage, ThinkingIndicator,
                CitationCard, MetricsChart, StatCard
```

## Frontend stack

Vite + React + TypeScript, styled with Tailwind CSS (dark theme, glass-panel cards, a brand gradient
accent), [Lucide](https://lucide.dev) icons, and [Framer Motion](https://www.framer.com/motion/) for the
micro-interactions — page transitions, the sliding nav/strategy-selector active pill, animated citation
accordions, and the "thinking" indicator while waiting on the local LLM.

## Tests

```bash
cd backend
./venv/Scripts/python -m pytest tests/ -v
```

Covers the pure-logic pieces that are easy to get subtly wrong: IR metric implementations
(`tests/test_metrics.py`) and RRF fusion (`tests/test_fusion.py`).
