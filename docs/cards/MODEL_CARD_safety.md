# Model Card: Output Safety (Llama Guard 3)

## Overview

| Field | Value |
|---|---|
| Model name | `llama-guard3` |
| Provider | Meta, served locally via Ollama |
| Role in IntraMind | Final safety screen on every synthesized response before it is returned to the user |
| Where it runs | Local Ollama process |
| Code | `ai-agent/src/utils/safety.py` + the `safety_check` and `handle_unsafe_response` nodes in `workflows/search_workflow.py` |
| Cost | $0 (local inference) |

## Intended Use

- Classify each candidate response as `safe` or `unsafe` per Meta's
  Llama Guard taxonomy (S1 - S13 categories such as "Violent Crimes",
  "Privacy", "Specialized Advice", etc.).
- Drive the **hard-block** policy: when the verdict is `unsafe`, the
  agent discards the original response and citations and returns
  `settings.safety_fallback_message` instead. The flagged text is
  **never** returned to the user.

## Out-of-Scope Use

- Input-side moderation. Today only outputs are screened. Adding an
  input-side guard would be a separate node.
- Adjudication of policy violations beyond Llama Guard's built-in
  taxonomy (e.g. company-specific data classification policies).

## Inputs and Outputs

- Input: the user prompt and the candidate assistant response.
- Output: a single token (`safe` / `unsafe`) plus, on `unsafe`, a list
  of category codes parsed by `_parse_llama_guard_output`.

## Performance

- Failure mode "false positive (over-block)" is preferred over "false
  negative (leak)" - the parser **fails closed** on malformed verdicts
  (treats them as unsafe).
- When Ollama or the model is unavailable, `classify_output` returns
  `is_safe=True` with the category `CLASSIFIER_UNAVAILABLE` so dev
  environments and CI without Ollama don't accidentally block all
  traffic. Production deployments should monitor this category and
  alert on it.

## Risks and Limitations

- Llama Guard reflects Meta's safety taxonomy; it is not a substitute
  for a domain-specific compliance review.
- The model can over-block in edge cases (e.g. legitimate medical or
  legal questions classified as "Specialized Advice"). The fallback
  message intentionally mentions that the user can "rephrase or contact
  your administrator" so over-blocks are recoverable.

## Governance

- Every block produces metrics (`safety_flags_total` and per-category
  counters in `utils/metrics.py`) and an OTEL span attribute
  (`safety.flagged=true`, `safety.categories=...`) visible in Phoenix.
- The fallback message text is configurable via
  `settings.safety_fallback_message` for localization.
- Llama Guard tag is pinned via `settings.safety_guard_model`.
