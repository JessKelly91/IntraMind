# IntraMind

> AI-powered intelligent search platform for enterprise internal documents — with built-in Responsible AI tooling.

IntraMind is a microservices-based platform that enables semantic search across your organization's internal knowledge base. It supports multiple file types (PDF, Word, PowerPoint, images, plain text), ships an embeddable chat widget for any website, and includes a fully open-source Responsible AI stack (tracing, RAG evaluations, PII redaction, output safety, drift monitoring, and governance docs) — all running locally with **$0 of monthly SaaS cost**.

## 🏗️ Architecture

IntraMind follows a microservices architecture with independent, deployable services managed via Git submodules:

```
IntraMind/
├── vector-db-service/   # Vector database service (Python + gRPC + Weaviate)
├── api-gateway/         # REST API gateway (ASP.NET Core 8.0)
├── ai-agent/            # AI agent orchestration (LangGraph + LangChain)
└── web-ui/              # Embeddable chat widget (Preact + FastAPI)
```

```
┌─────────────────────┐
│   Host Website      │  Embed via <script> tag
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Web UI Widget      │  Preact + TypeScript (Shadow DOM)
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│  Web UI Backend     │  FastAPI (port 8001)
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│  AI Agent           │  LangGraph workflows
└──────────┬──────────┘  (search + ingestion + safety)
           │ HTTP/REST
           ▼
┌─────────────────────┐
│  API Gateway        │  ASP.NET Core 8.0 (port 5000)
└──────────┬──────────┘
           │ gRPC
           ▼
┌─────────────────────┐
│  Vector Service     │  Python gRPC (port 50052)
└──────────┬──────────┘
           │
           ▼
   [Weaviate + text2vec-transformers]

       ⤷ all services emit OTEL spans to → Phoenix (port 6006)
```

### Current Services

- **vector-db-service** ([Repository](https://github.com/JessKelly91/intramind-vector-db-service))
  - gRPC microservice wrapping Weaviate
  - All 11 RPCs (CRUD + batch + collections + search + health)
  - Python + gRPC + Weaviate client
- **api-gateway** ([Repository](https://github.com/JessKelly91/intramind-api-gateway))
  - ASP.NET Core 8.0 REST API
  - Proxies to gRPC Vector Service via shared `VectorDB.Contracts` NuGet package
  - Swagger, FluentValidation, Serilog, Kubernetes-style liveness/readiness probes
- **ai-agent** ([Repository](https://github.com/JessKelly91/intramind-ai-agent))
  - LangGraph search and ingestion workflows
  - Multimodal ingestion (PDF, DOCX, PPTX, images, plain text)
  - Conversation memory via LangGraph SQLite checkpointing
  - Query classification (router LLM) → simple vs complex search → grounded synthesis
  - **Responsible AI nodes:** PII redaction on ingest, Llama Guard output safety check
  - OpenTelemetry tracing to Phoenix (every node, every LLM call, every retrieval)
  - CLI with streaming, conversation management, and metrics
- **web-ui** ([Repository](https://github.com/JessKelly91/intramind-web-ui))
  - Preact + TypeScript embeddable chat widget (~30 KB gzipped, Shadow-DOM isolated)
  - FastAPI backend that proxies to the AI Agent
  - Document upload, collection management, demo site

## 🛡️ Responsible AI

A fully free, open-source RAI stack is wired into the platform. All LLM judges and classifiers run on local Ollama, so the running cost is **$0**:

| Capability | Tool | Where it lives |
|---|---|---|
| Distributed tracing | [Phoenix](https://github.com/Arize-ai/phoenix) | `phoenix` container in `docker-compose.yml`; instrumentation in `ai-agent` and `web-ui` |
| RAG evaluations (CI) | [Ragas](https://github.com/explodinggradients/ragas) with Ollama judge | `ai-agent/tests/eval/` + `rag-evals` job in `.github/workflows/ci.yml` |
| PII redaction | [Microsoft Presidio](https://github.com/microsoft/presidio) | `redact_pii` node in the ingestion workflow (redact-on-ingest, tokenized pseudonyms) |
| Output safety | Llama Guard 3 via Ollama | `safety_check` node in the search workflow (hard-block + templated fallback) |
| Drift monitoring | [Evidently AI](https://github.com/evidentlyai/evidently) | `ai-agent/scripts/drift_report.py` + weekly `.github/workflows/drift-report.yml` |
| Governance docs | Model + dataset cards | [`docs/cards/`](./docs/cards/) |

See [`docs/cards/`](./docs/cards/) for model cards, [`ai-agent/README.md`](./ai-agent/README.md#-responsible-ai) for the full RAI overview, and [`docs/drift/`](./docs/drift/) for the latest drift reports.

## 🚀 Getting Started

### Prerequisites

- **Git**
- **Docker & Docker Compose**
- **Python 3.11+** (3.12 verified; some tooling — e.g. spaCy — does not yet support 3.13)
- **Node.js 18+** (only required if you want to build the web-ui widget)
- **[Ollama](https://ollama.ai/)** for local LLM inference

### Installation Steps

#### 1. Clone with Submodules

```bash
git clone --recurse-submodules https://github.com/JessKelly91/IntraMind.git
cd IntraMind

# Or if you already cloned without --recurse-submodules:
git submodule update --init --recursive
```

#### 2. Install Ollama models (one-time)

```bash
# Required for routing + synthesis
ollama pull llama3.2:3b

# Required for the Responsible AI stack
ollama pull llama3.1:8b      # Ragas judge (Step 2)
ollama pull llama-guard3     # Output safety classifier (Step 4)

# Start the daemon (keep running in the background)
ollama serve
```

#### 3. Start the IntraMind platform

```bash
# Brings up Weaviate, t2v-transformers, Vector Service, API Gateway, and Phoenix
docker compose up -d

# Verify all services are healthy
docker compose ps

# Tail logs (optional)
docker compose logs -f api-gateway
```

**Services will be available at:**

| Service | URL |
|---|---|
| Weaviate | http://localhost:8080 |
| Vector Service (gRPC) | localhost:50052 |
| API Gateway (REST) | http://localhost:5000 |
| API Gateway Swagger | http://localhost:5000/swagger |
| Phoenix tracing UI | http://localhost:6006 |

#### 4. Run the AI Agent CLI

```bash
cd ai-agent

# First-time setup
pip install -r requirements.txt
python -m spacy download en_core_web_lg   # required for Presidio PII redaction

# Configure environment
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY or OPENAI_API_KEY (optional - Ollama works too).
# Set ENABLE_TRACING=true to start emitting spans to Phoenix.

# Interactive search
python -m src.cli.main search

# Single-shot search
python -m src.cli.main search -q "your search query"
```

#### 5. (Optional) Run the Web UI

See [`web-ui/README.md`](./web-ui/README.md) for detailed instructions. Quick start:

```bash
cd web-ui/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# In another shell, build the widget
cd web-ui/widget
npm install
npm run dev
```

### Quick Health Check

```bash
curl http://localhost:8080/v1/.well-known/ready    # Weaviate
curl http://localhost:5000/health                  # API Gateway
curl http://localhost:6006/                        # Phoenix UI

cd ai-agent
python -m src.cli.main search -q "test"            # End-to-end smoke
```

### Stopping Services

```bash
docker compose down            # Stop containers
docker compose down -v         # Stop and remove all volumes (clean slate)
```

## 🔄 Working with Submodules

```bash
# Update all submodules to their latest tracked commit
git submodule update --remote

# Pull latest main + submodules together
git pull --recurse-submodules

# Make changes inside a submodule
cd ai-agent
git checkout main
git pull
# ...edit, commit, push as normal...
cd ..
git add ai-agent
git commit -m "Bump ai-agent to latest"
git push
```

See [`docs/SUBMODULE_GUIDE.md`](./docs/SUBMODULE_GUIDE.md) for the full submodule workflow.

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| Vector storage | Weaviate, text2vec-transformers (`all-MiniLM-L6-v2`, free local embeddings) |
| Vector service | Python, gRPC, Protocol Buffers |
| API Gateway | ASP.NET Core 8.0, Grpc.Net.Client, Serilog, FluentValidation, Swagger |
| AI Agent | Python, LangGraph, LangChain, langchain-ollama, httpx, Click, Rich |
| Web UI widget | Preact, TypeScript, Vite (Shadow-DOM-isolated, ~30 KB gzipped) |
| Web UI backend | FastAPI, Uvicorn |
| LLM providers | Ollama (router + judge + safety), Anthropic / OpenAI / Ollama (synthesis) |
| Responsible AI | Phoenix (OpenInference), Ragas, Microsoft Presidio, Llama Guard 3, Evidently AI |
| Observability | OpenTelemetry, FastAPI + HTTPX + LangChain instrumentors |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions (validate + lint + build + integration + RAG evals + weekly drift) |

## 🎯 Roadmap

### Completed
- [x] **Phase 1** — Weaviate + free local vectorization
- [x] **Phase 2** — gRPC vector service (all 11 RPCs, full CRUD, batch, search, health)
- [x] **Phase 3** — REST API Gateway (ASP.NET Core, Swagger, validation, health checks)
- [x] **Phase 4** — AI Agent (LangGraph workflows, multimodal ingestion, conversation memory, CLI)
- [x] **Phase 5** — Platform integration (Docker Compose, integration tests, CI pipeline)
- [x] **Phase 6** — Web UI (embeddable Preact widget + FastAPI backend + demo site)
- [x] **Phase 7** — Responsible AI (Phoenix tracing, Ragas evals, Presidio PII redaction, Llama Guard safety, Evidently drift, model + dataset cards)

### Up next
- [ ] Authentication & multi-tenancy hardening of the web-ui backend
- [ ] Retrieval quality optimization (currently measured by Ragas; improvements to be driven by the metrics)
- [ ] Flip the Ragas threshold gate from warning-only to enforcing once a baseline is established
- [ ] User acceptance testing on a real corpus

See [`docs/PROJECT_ROADMAP.md`](./docs/PROJECT_ROADMAP.md) for the full phase-by-phase breakdown.

## 🧪 Testing

### Unit tests (per submodule)
Run inside the relevant submodule (`ai-agent/`, `api-gateway/`, `vector-db-service/`, `web-ui/`).

For example, the AI Agent ships **112+ unit tests** plus **16 Responsible AI tests** (PII redaction + safety guard parsing + workflow hard-block):

```bash
cd ai-agent
pytest tests/ -v
```

### Platform integration tests
Located in [`tests/integration/`](./tests/integration/):

```bash
cd tests
pip install -r requirements.txt
pytest integration/ -v
# Expected: ~34 passed, ~6 skipped in CI mode (no vectorizer)
```

**CI mode:** [`docker-compose.ci.yml`](./docker-compose.ci.yml) runs without the 8 GB text2vec-transformers model, trading semantic-search coverage for ~5 minutes of CI runtime. Semantic-search tests skip themselves automatically.

### RAG evaluations (Ragas)
Every PR gets a warning-only RAG-quality report (faithfulness, answer relevancy, context precision, context recall) using a local Ollama judge. See the `rag-evals` job in [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) and [`ai-agent/tests/eval/`](./ai-agent/tests/eval/).

### Weekly drift report
[`.github/workflows/drift-report.yml`](./.github/workflows/drift-report.yml) runs every Monday and opens a PR with a fresh Evidently HTML report under [`docs/drift/`](./docs/drift/).

## 📚 Documentation

### Getting Started
- **[User Guide](./docs/USER_GUIDE.md)** — End-to-end usage scenarios
- **[Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)** — Local and production deployment
- **[Docker Setup Guide](./docs/DOCKER_SETUP.md)** — Compose setup and troubleshooting

### Developer Resources
- **[API Reference](./docs/API_REFERENCE.md)** — Complete API documentation for all services
- **[Architecture Overview](./docs/ARCHITECTURE.md)** — System design and component details
- **[Submodule Guide](./docs/SUBMODULE_GUIDE.md)** — Working with Git submodules
- **[Integration Tests](./tests/integration/README.md)** — Platform-wide integration testing

### Responsible AI
- **[Model + Dataset Cards](./docs/cards/)** — Router, synthesizer, embedder, safety; dataset provenance schema
- **[Drift Reports](./docs/drift/)** — Weekly auto-generated Evidently reports
- **[AI Agent RAI overview](./ai-agent/README.md#-responsible-ai)** — End-to-end stack walkthrough

### CI/CD
- **[GitHub Workflows](./.github/WORKFLOWS.md)** — CI/CD pipeline documentation
- **[CI Compose Configuration](./docker-compose.ci.yml)** — Optimized CI environment

### Project Management
- **[Project Roadmap](./docs/PROJECT_ROADMAP.md)** — Development progress and plans
- **[Production Improvements](./docs/PRODUCTION_IMPROVEMENTS.md)** — NuGet package implementation
- **[NuGet Implementation](./docs/NUGET_IMPLEMENTATION.md)** — Contract packaging details

### Service-Specific Documentation
- [Vector DB Service](./vector-db-service/README.md)
- [API Gateway](./api-gateway/README.md)
- [AI Agent](./ai-agent/README.md)
- [Web UI](./web-ui/README.md)

## 🤝 Contributing

1. Clone the repository with submodules.
2. Create a feature branch.
3. Make your changes (commit + push inside the relevant submodule first, then bump the submodule reference in the main repo).
4. Open a pull request — the CI pipeline will run lint, build, integration tests, and the warning-only Ragas eval.

## 📄 License

See individual service repositories for licensing information.

---

**Built with** ❤️ **for enterprise knowledge management**
