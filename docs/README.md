# IntraMind Documentation

This directory contains the public documentation for the IntraMind platform. It is organized so GitHub visitors see the polished overview and setup material first, with maintainer/process docs kept lower on the page.

## 📚 Documentation Index

### Public Core Docs

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

- **[API_REFERENCE.md](./API_REFERENCE.md)** - API details for Gateway, Vector Service, Prompt Registry, and AI Agent
  - REST and gRPC usage examples
  - Prompt Registry auth, seed, label, eval, audit, and history endpoints
  - Development auth and production recommendations

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Local deployment, production caveats, health checks, and operational notes

- **[USER_GUIDE.md](./USER_GUIDE.md)** - End-to-end user scenarios and feature walkthroughs

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

## 🔗 Quick Links

- [Main README](../README.md) - Platform overview and quick start
- [Vector DB Service Docs](../vector-db-service/README.md)
- [API Gateway Docs](../api-gateway/README.md)
- [AI Agent Docs](../ai-agent/README.md)
- [Prompt Registry Docs](../prompt-registry/README.md)
- [Web UI Docs](../web-ui/README.md)

## Maintainer Docs

These docs are public, but they are aimed at contributors and maintainers rather than first-time users:

- [Submodule Guide](./SUBMODULE_GUIDE.md)
- [Platform Integration Tests](../tests/integration/README.md)
- [GitHub Workflows](../.github/WORKFLOWS.md)
- [AI Agent Workflows](../ai-agent/docs/WORKFLOWS.md)
- [AI Agent Observability](../ai-agent/docs/OBSERVABILITY.md)
- [AI Agent Conversation Memory](../ai-agent/docs/CONVERSATION_MEMORY.md)
- [API Gateway Usage Guide](../api-gateway/docs/api-usage-guide.md)
- [API Gateway Metadata Schema](../api-gateway/docs/metadata-schema.md)

## Archived History

Historical phase notes and stale narrative snapshots are archived below their owning service when they are useful for project history but not current public guidance:

- [Web UI Phase History](../web-ui/docs/archive/PHASE_HISTORY.md)
- [AI Agent Portfolio Writeup Archive Note](../ai-agent/docs/archive/PORTFOLIO_WRITEUP.md)

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

**Last Updated**: June 15, 2026

