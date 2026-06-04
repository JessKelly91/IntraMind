# IntraMind Documentation

This directory contains detailed documentation for the IntraMind platform.

## 📚 Documentation Index

### Core Documentation

- **[DOCKER_SETUP.md](./DOCKER_SETUP.md)** - Complete Docker Compose setup guide
  - Prerequisites and installation
  - Step-by-step quick start
  - Service details and configuration
  - Troubleshooting common issues
  - Development workflows

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design
  - Microservices overview
  - Communication flows
  - Technology stack
  - Deployment patterns

- **[PROJECT_ROADMAP.md](./PROJECT_ROADMAP.md)** - Development progress and plans
  - Current status and completed phases
  - In-progress work
  - Future roadmap
  - Architecture decisions

### Responsible AI

The Free RAI Stack ships six free, open-source capabilities. See
[`ai-agent/README.md`](../ai-agent/README.md#-responsible-ai) for the
end-to-end overview.

- **Model and Dataset Cards** - [`cards/`](./cards/)
  - [`MODEL_CARD_router.md`](./cards/MODEL_CARD_router.md) - query router (Llama 3.2 3B)
  - [`MODEL_CARD_synthesizer.md`](./cards/MODEL_CARD_synthesizer.md) - response synthesizer (Anthropic / OpenAI / Ollama)
  - [`MODEL_CARD_embedder.md`](./cards/MODEL_CARD_embedder.md) - embedder (`all-MiniLM-L6-v2` via `text2vec-transformers`)
  - [`MODEL_CARD_safety.md`](./cards/MODEL_CARD_safety.md) - output safety (Llama Guard 3)
  - [`DATASETS.md`](./cards/DATASETS.md) - inventory + provenance schema for ingested corpora
- **Drift reports** - [`drift/`](./drift/) (auto-PR weekly via `.github/workflows/drift-report.yml`)
- **PII policy** - redact-on-ingest with stable tokenized pseudonyms (see the AI Agent README for full rationale)
- **Output safety policy** - hard-block flagged outputs and substitute a templated fallback (see `MODEL_CARD_safety.md`)

### Internal Notes

- **SETUP_SUMMARY.md** *(gitignored)* - Development notes for Phase 5.1 testing
  - Local file only, not committed to git
  - Testing checklist and validation steps
  - Can be deleted after Phase 5.1 is complete

## 🔗 Quick Links

- [Main README](../README.md) - Platform overview and quick start
- [Vector DB Service Docs](../vector-db-service/README.md)
- [API Gateway Docs](../api-gateway/README.md)
- [AI Agent Docs](../ai-agent/README.md)

## 🚀 Getting Started

New to IntraMind? Start here:

1. Read the [Main README](../README.md) for an overview
2. Follow the [DOCKER_SETUP.md](./DOCKER_SETUP.md) guide to get running
3. Explore the [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system design

## 📝 Contributing to Documentation

When updating documentation:
- Keep links relative (use `./` and `../`)
- Update cross-references when moving files
- Maintain consistent formatting and structure
- Test all links after changes

---

**Last Updated**: November 5, 2025

