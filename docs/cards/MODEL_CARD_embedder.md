# Model Card: Embedder

## Overview

| Field | Value |
|---|---|
| Model name | `sentence-transformers/all-MiniLM-L6-v2` |
| Provider | Hugging Face, served via Weaviate's `text2vec-transformers` module |
| Role in IntraMind | Produces the dense vectors used for semantic search over ingested chunks |
| Where it runs | Local Docker container `t2v-transformers` (see `docker-compose.yml`) |
| Cost | $0 (local inference) |

## Intended Use

- Embed each chunk produced by the ingestion workflow before storage in
  Weaviate.
- Embed each user query at search time so Weaviate can compute cosine
  similarity against stored vectors.

## Out-of-Scope Use

- Cross-lingual retrieval. The default model is English-centric. Swap to
  a multilingual `sentence-transformers` model if non-English content
  becomes a primary use case.
- Re-ranking. We rely on Weaviate's similarity score directly; if you
  need a cross-encoder re-ranker, add it as a separate model card.

## Inputs and Outputs

- Input: a chunk of redacted text (raw PII has already been replaced
  with stable tokens like `<PERSON_1>`, `<EMAIL_ADDRESS_2>` per the PII
  redaction step).
- Output: a 384-dimensional float vector, persisted in Weaviate.

## Training Data

Trained by the sentence-transformers project on a mix of public NLI /
question-answer corpora. See the official Hugging Face model card.

## Performance

- `context_precision` and `context_recall` from the Ragas eval job are
  the most direct signals of retrieval quality and therefore embedder
  performance.
- The Evidently drift report (Step 5) tracks score-distribution drift on
  a fixed probe set as a leading indicator of corpus drift relative to
  the embedder.

## Risks and Limitations

- Sensitive to typos and unusual capitalization, mitigated somewhat by
  the chunking strategy (overlap + paragraph boundaries).
- Can underperform on highly technical or domain-specific jargon. For
  those domains, consider a domain-tuned `sentence-transformers` model.

## Governance

- Container image pinned via `docker-compose.yml`.
- Vectors carry the same metadata as the source chunk - including
  `pii_findings`, `consent_basis`, `retention_class`, and `ingested_at` -
  so embeddings are governed alongside their text.
