# Secure AI Insights Assistant

> Multi-agent RAG analytics assistant for internal entertainment data — FictStream.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  React + Vite + Tailwind (port 3000)                            │
│  Chat · Filters · Insights Panel · Charts · Tool Trace          │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────────────────────────────┐
│  FastAPI Gateway  /api/v1  (port 8000)                          │
│  Auth · CORS · Pydantic Validation                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│  LangGraph State Machine                                         │
│                                                                  │
│  Supervisor ──► SQL Agent ──► Analytics Agent ──► Synthesizer   │
│      │                                                  │        │
│      └──────► RAG Agent ────────────────────────────► │        │
│                                                         ▼        │
│                                               Verifier Agent     │
│                                            (adversarial check)   │
└─────────────────────────────────────────────────────────────────┘
         │              │
   PostgreSQL 16    ChromaDB 0.5
   (structured)     (vectors / PDFs)
```

## Key Design Decisions

1. **Multi-agent with typed contracts** — Supervisor emits a `Plan` (intent + evidence requirements + expected shape). Verifier enforces that plan against the final answer. Agents cannot bypass this contract.

2. **Tool-mediated data access** — LLM never executes raw SQL or reads files directly. All access goes through typed, parameterized tool functions in `app/tools/`. This is the security perimeter.

3. **Adversarial Verifier** — separated from the Synthesizer (different system prompt, no shared reasoning). Runs 4 checks: plan satisfaction, citation coverage, entailment, numeric exact-match.

4. **Local embeddings + reranker** — `BAAI/bge-small-en-v1.5` for embeddings, `BAAI/bge-reranker-base` for reranking. No extra vendor dependency, runs on CPU.

5. **PII protection** — viewer emails/names never stored. Viewer dimension tables contain only age group, region, tier, gender (aggregated).

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Groq API key ([get one free](https://console.groq.com))

### 1. Clone and configure
```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
```

### 2. Start everything
```bash
docker compose up --build
```

This will:
- Start PostgreSQL and ChromaDB
- Generate synthetic CSV data
- Generate synthetic PDF documents
- Seed the database
- Ingest PDFs into ChromaDB
- Start the FastAPI backend
- Build and serve the React frontend

### 3. Open the app
- **Frontend**: http://localhost:3000
- **API docs**: http://localhost:8000/docs

### Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start Postgres and Chroma manually (or use Docker):
docker compose up db chroma -d

# Generate data
cd ../data && python generate_csv.py && python generate_pdfs.py

# Seed DB
cd ../backend && python -m app.data.seed

# Ingest PDFs
python -c "from app.data.ingestion import DocumentIngestionService; DocumentIngestionService().ingestAllPdfs()"

# Run server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

**Run tests:**
```bash
cd backend
pytest tests/unit/ -v
```

## Example Questions

| Question | What it exercises |
|----------|-------------------|
| Which titles performed best in 2025? | SQL top-titles tool + bar chart |
| Why is Stellar Run trending recently? | SQL + RAG (campaign report) + analytics momentum |
| Compare Dark Orbit vs Last Kingdom | SQL compareTitles + analytics KPIs |
| Which city had the strongest engagement last month? | SQL regional performance |
| What explains weak comedy performance? | RAG (quarterly report) + SQL genre data |
| What recommendations would you give for leadership? | RAG (all PDFs) + multi-source synthesis |

## Project Structure

```
secure-ai-insights/
├── backend/
│   ├── app/
│   │   ├── agents/          # supervisor, sql, rag, analytics, synthesizer, verifier
│   │   ├── api/routes/      # chat, health, trace endpoints
│   │   ├── data/            # schema, seed, ingestion
│   │   ├── llm/             # groq client, embeddings, reranker
│   │   ├── observability/   # structlog, trace store
│   │   ├── orchestration/   # LangGraph graph + AgentState
│   │   ├── tools/           # sql_tools, vector_tools, analytics_tools
│   │   ├── config.py
│   │   └── main.py
│   └── tests/unit/
├── frontend/
│   └── src/
│       ├── components/      # Chat, Filters, Charts, Insights, ToolTrace
│       ├── api/client.ts
│       ├── hooks/useChat.ts
│       └── types/index.ts
├── data/
│   ├── csv/                 # generated synthetic data
│   ├── pdfs/                # generated synthetic documents
│   ├── generate_csv.py
│   ├── generate_pdfs.py
│   └── SCHEMA.md
├── config.yaml
├── docker-compose.yml
└── .env.example
```

## Configuration

All tuneable parameters live in `config.yaml` (override with env vars):

| Parameter | Default | Notes |
|-----------|---------|-------|
| `retrieval.top_k` | 4 | Chunks returned per RAG query |
| `synthesizer.temperature` | 0.5 | Answer generation creativity |
| `supervisor.temperature` | 0.2 | Routing near-deterministic |
| `verifier.max_retries` | 2 | Hard cap on re-synthesis loops |
| `eval.noise_chunks` | 0 | Set to 2 for noise-robustness eval |

## Security Model

- **No raw SQL** — LLM calls parameterized templates; `run_dynamic_sql` is dev-only and flag-gated with sqlglot AST allowlist (SELECT-only).
- **PII masking** — viewer personal data never passed to LLM; only aggregated dimensions.
- **Prompt injection** — Synthesizer system prompt explicitly treats `<tool_outputs>` as data, not instructions.
- **Tool registry as perimeter** — every data access goes through typed Pydantic-validated tools, not direct DB/file access.
- **Dependency pinning** — all versions pinned in `requirements.txt`; base image is `python:3.11-slim`.

## Assumptions & Tradeoffs

1. **Multi-agent over single-pass pipeline** — adds latency (~2-3 extra LLM calls) but enables the Verifier's contract enforcement. Acceptable for internal correctness-first analytics.
2. **SQLite trace store** — intentionally lightweight; production would use Postgres or Redis.
3. **Synthetic data** — CSVs and PDFs are generated. Schema and content are documented in `data/SCHEMA.md`.
4. **Single dummy user** — no auth in v1. JWT auth is scaffolded in the middleware stub.
5. **LLM-as-judge for entailment** — faster than local NLI; some judge bias accepted. Cross-validate with `cross-encoder/nli-deberta-v3-base` in eval mode.
6. **Chroma over Qdrant** — simpler ops; switch to Qdrant if hybrid BM25+dense retrieval is needed.
