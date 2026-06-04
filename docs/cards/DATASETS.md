# Datasets

This document inventories every dataset the IntraMind agent ingests or
evaluates against, along with provenance, consent basis, and retention
class. New datasets should be added here as part of the same PR that
introduces them.

## Schema

Every chunk stored in Weaviate carries this provenance metadata
(emitted by the ingestion workflow - see
[`ai-agent/src/workflows/ingestion_workflow.py`](../../ai-agent/src/workflows/ingestion_workflow.py)):

| Field | Type | Meaning |
|---|---|---|
| `source` | string | Original filename or URL |
| `ingested_by` | string | User or service principal that triggered ingestion |
| `ingested_at` | ISO 8601 string | UTC timestamp of ingestion |
| `consent_basis` | string | Legal/ethical basis - see allowed values below |
| `retention_class` | string | Data lifecycle bucket - see allowed values below |
| `pii_findings` | list | PII span metadata (type + offsets, no raw values) |
| `pii_redaction_applied` | bool | True if Presidio actually replaced PII in the chunk |

### Allowed `consent_basis` values

| Value | Meaning |
|---|---|
| `fixture` | Synthetic test corpus committed to the repo - no real data |
| `internal` | Internal company document, employees consented via standard handbook |
| `customer_authorized` | Customer-uploaded with explicit upload consent |
| `public` | Public web content, no consent required |
| `legitimate_interest` | Processed under a documented legitimate interest assessment |

### Allowed `retention_class` values

| Value | Meaning |
|---|---|
| `ephemeral` | Deleted within 24 hours |
| `short_term` | Retained up to 30 days |
| `standard` | Retained up to 1 year |
| `long_term` | Retained up to 7 years (default for compliance documents) |
| `permanent` | Retained indefinitely (governance + audit logs) |

## Inventory

### Eval fixture corpus

| Field | Value |
|---|---|
| Location | `ai-agent/tests/eval/data/corpus/` |
| Files | `q4_2024_earnings.txt`, `acceptable_use_policy.txt`, `onboarding_guide.txt` |
| Size | ~3 KB total |
| Source | Hand-written for this repo |
| Consent basis | `fixture` |
| Retention class | `permanent` |
| PII status | None - synthetic content only, manually verified |
| Used by | `tests/eval/ragas_eval.py` (Step 2), `scripts/drift_report.py` (Step 5) |

### Golden Q&A set

| Field | Value |
|---|---|
| Location | `ai-agent/tests/eval/data/golden_qa.jsonl` |
| Size | 10 entries |
| Source | Hand-written, paired with the fixture corpus |
| Consent basis | `fixture` |
| Retention class | `permanent` |
| PII status | None |
| Used by | Ragas eval driver and threshold tests |

### User-ingested documents

| Field | Value |
|---|---|
| Location | Weaviate collections |
| Source | Customer / employee uploads via `web-ui` or the API Gateway |
| Consent basis | Set per-upload (defaults to `customer_authorized` for widget uploads) |
| Retention class | Set per-collection; default `standard` |
| PII status | Tokenized at ingest by the `redact_pii` node (Step 3). Findings recorded in `pii_findings` metadata. Raw PII never enters Weaviate. |
| Used by | All search and synthesis flows |

## Change log

- Created in Step 6 of the Free RAI Stack rollout.
