# Model Card: Query Router

## Overview

| Field | Value |
|---|---|
| Model name | Llama 3.2 3B Instruct |
| Provider | Meta, served locally via Ollama |
| Role in IntraMind | Query complexity router (simple vs complex) and lightweight classification tasks |
| Where it runs | Local Ollama process - no data leaves the deployment |
| Code | `ai-agent/src/utils/llm.py` (`get_router_llm`), used in `workflows/search_workflow.py::classify_query` |
| Cost | $0 (local inference) |

## Intended Use

- Classify each user query as `simple` (one search call) or `complex` (multi-query expansion + synthesis).
- Designed for low latency and low cost so it can run on every request.

## Out-of-Scope Use

- Final user-facing answers. Never used as a synthesizer.
- Any task that requires reasoning over retrieved context - use the synthesizer model instead.
- Safety classification - that is delegated to Llama Guard in the `safety_check` node.

## Inputs and Outputs

- Input: the user query, plus a small system prompt that defines the
  classification schema.
- Output: a one-token / one-word verdict that the workflow parses into
  `simple` or `complex`.

## Training Data

Trained by Meta on a broad open-web mix. IntraMind does not fine-tune this
model. See Meta's official model card for details.

## Performance

Tracked end-to-end via the `rag-evals` CI job (Ragas
`context_precision` / `context_recall` are sensitive to router mistakes
because picking the wrong branch leads to under-retrieval). Threshold is
warning-only today; flip `RAGAS_ENFORCE_THRESHOLDS=true` to gate PRs.

## Risks and Limitations

- Misclassification can downgrade a complex query to a single search,
  reducing recall. Captured by `context_recall` in evals.
- Local inference quality depends on the host machine; very small hosts
  may quantize away accuracy.

## Governance

- Versioned via the Ollama tag (`llama3.2:3b`).
- Replaceable via `settings.router_llm_provider` + `settings.router_llm_model`.
- All calls produce OTEL spans visible in Phoenix when tracing is enabled.
