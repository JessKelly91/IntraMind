# Model Card: Synthesizer

## Overview

| Field | Value |
|---|---|
| Model name(s) | Configurable: Anthropic Claude (Sonnet/Haiku family), OpenAI GPT (4o-mini and similar), or local Llama 3.x via Ollama |
| Role in IntraMind | Generates the final natural-language response from retrieved chunks (the "primary LLM") |
| Where it runs | Provider API or local Ollama, depending on `settings.primary_llm_provider` |
| Code | `ai-agent/src/utils/llm.py` (`get_primary_llm`), used in `workflows/search_workflow.py::synthesize_results` |
| Cost | $0 with the Ollama variant; metered with Anthropic/OpenAI |

## Intended Use

- Compose user-facing answers grounded in the retrieved chunks.
- Cite source chunk IDs in the returned `citations` list.

## Out-of-Scope Use

- Final adjudication of safety. That is enforced by Llama Guard in the
  `safety_check` node, which **hard-blocks** unsafe outputs and replaces
  them with `settings.safety_fallback_message`. The synthesizer is not the
  last line of defense.
- Operations that require side effects (tool use, write APIs). The
  synthesizer is read-only and produces text only.

## Inputs and Outputs

- Input: the user query, the (already PII-redacted) retrieved chunks, and
  a system prompt that mandates citation + grounding.
- Output: a Markdown response and a list of cited chunk IDs.

## Training Data

Provider-managed. IntraMind does not fine-tune. Refer to the provider's
own model card for training-data details.

## Performance

- Faithfulness, answer relevancy, context precision, and context recall
  scores from Ragas are reported on every PR by the `rag-evals` CI job.
- Tracing in Phoenix shows per-call latency and token counts.

## Risks and Limitations

- Hallucination is the primary risk. Mitigated by:
    1. Grounded prompt that requires citation from retrieved chunks.
    2. Ragas faithfulness metric in CI.
    3. Output safety screen before the response leaves the agent.
- The PII redactor (Step 3) replaces real PII with stable tokens (e.g.
  `<PERSON_1>`). The synthesizer therefore never sees raw PII; downstream
  responses also won't contain raw PII unless the user provides it in the
  prompt itself.
- Provider-hosted variants send query + retrieved chunks to a third
  party. If your data contract forbids that, configure the Ollama variant
  via `settings.primary_llm_provider="ollama"`.

## Governance

- Tracked via OTEL spans in Phoenix (Step 1).
- Hard safety gate enforced by Llama Guard (Step 4).
- Provider can be swapped without code changes via env vars.
