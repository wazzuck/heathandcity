# Practice Vault Model and Host Recommendations

> Date: 10 November 2026
> Scope: Sovereign Practice Vault appliance on the Heath & City host.
> Status: Assessment and handoff for another Artificial Intelligence (AI)
> coding agent. No existing source file was changed to produce this note.

---

## 1. Purpose

1. This document records the measured host specification, the recommended
   Small Language Model (SLM) for local Retrieval-Augmented Generation
   (RAG), and the optimisations required on this hardware.
2. It also records the pipeline changes needed before natural-language
   questions such as "what did I buy last year?" can be answered reliably.
3. Another agent should treat this as background and acceptance criteria, not
   as permission to alter unrelated files.

---

## 2. Host Specification

| Item | Observed value |
| :--- | :--- |
| Central Processing Unit (CPU) | Intel Core i3-9100T |
| Cores and threads | 4 cores, 4 threads |
| Clock speed | 3.1 GHz base, 3.7 GHz turbo |
| Cache | 6 MB L3 |
| Instruction set | Advanced Vector Extensions 2 (AVX2) and Fused Multiply-Add |
| Extended instructions | No AVX-512 |
| Random Access Memory (RAM) | 15.5 GiB usable |
| Swap | 12 GiB |
| Primary storage | 238 GB Non-Volatile Memory Express (NVMe) flash storage |
| Primary storage free space | 154 GB |
| Secondary storage | 447 GB SATA solid-state drive (SSD) |
| Graphics | Intel UHD 630 integrated graphics processor |
| Graphics memory | Shared system memory |
| Idle temperature | 41-44 degrees Celsius |
| Indexing temperature | 50-52 degrees Celsius |
| Software | Debian 13, Python 3.14.7, Ollama 0.40.16 |
| Current corpus | 42,442 documents, 42,537 chunks, 19.2 million words |
| Current text volume | 202.55 MB |
| Current lexical index | 322 MB SQLite FTS5 database |
| Current appliance data | Approximately 492 MB |

### 2.1. Capacity Assessment

1. The CPU is the limiting factor. It is suitable for 3-4 billion parameter
   models and can run a 9 billion parameter model at reduced speed.
2. A 27 billion parameter model does not fit comfortably once the operating
   system, key-value cache, embedding model, and FastAPI process are included.
3. The integrated graphics processor is not recommended. It shares system
   memory, and Ollama is currently using the CPU.
4. The NVMe SSD has ample free space for the corpus, models, and indexes.
5. The current 8 GB indexing process is a one-off workload. The operator has
   confirmed that indexing and querying will not run concurrently.

---

## 3. Model Recommendation

### 3.1. Primary model

Use **`qwen3.5:4b`** in its Q4_K_M build for normal RAG queries.

1. Size on disk: 3.3-4.0 GB.
2. Context: 256K tokens, although only 8192 should be used for normal RAG.
3. Licence: Apache 2.0.
4. Reported MMLU-Pro: 79.1.
5. Reported GPQA Diamond: 76.2.
6. Strength: the strongest 4B-class model that fits this host.
7. Weakness: it thinks by default, which wastes time on simple RAG answers.

The model must be run with **`think: false`** for normal RAG.

### 3.2. Quality tier

Use **`qwen3.5:9b`** for complex multi-document synthesis, only when answer
quality matters more than response time.

1. Size on disk: 6.6-7.6 GB.
2. Context: 256K tokens.
3. Licence: Apache 2.0.
4. Reported MMLU-Pro: 82.5.
5. Reported GPQA Diamond: 81.7.

### 3.3. Fast fallback

Use **`qwen3:4b-instruct-2507-q4_K_M`** if Qwen3.5 proves unexpectedly slow
on this older CPU.

1. Size on disk: 2.5 GB.
2. Context: 256K tokens.
3. Licence: Apache 2.0.
4. Reported MMLU-Pro: 69.6.
5. Reported GPQA Diamond: 62.0.
6. This is a text-only, non-thinking model, so it avoids the Qwen3.5 vision
   encoder and thinking overhead.

### 3.4. Models to avoid

1. `qwen3.6:27b`: 18-19 GB, does not fit.
2. `qwen3.5:27b`: 17-20 GB, does not fit.
3. `qwen3.8:27b`: approximately 18 GB, does not fit.
4. `qwen3:4b` as a default: capable, but its default thinking behaviour wastes
   tokens unless explicitly disabled.
5. The current default `qwen2.5:3b`: functional, but older and weaker than
   Qwen3.5 4B.

### 3.5. Primary sources

- Qwen3.5-4B model card:
  https://huggingface.co/Qwen/Qwen3.5-4B
- Qwen3.5-9B model card:
  https://huggingface.co/Qwen/Qwen3.5-9B
- Qwen3-4B-Instruct-2507 model card:
  https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507
- Ollama Qwen3.5 library:
  https://ollama.com/library/qwen3.5

---

## 4. Recommended Ollama Configuration

### 4.1. Server-level settings

Use these settings for a single-user appliance:

```text
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_QUEUE=8
OLLAMA_CONTEXT_LENGTH=8192
OLLAMA_KEEP_ALIVE=5m
OLLAMA_KV_CACHE_TYPE=q8_0
```

1. `OLLAMA_MAX_LOADED_MODELS=1` prevents the default three-model CPU cache
   from exhausting 16 GB of RAM.
2. `OLLAMA_NUM_PARALLEL=1` is appropriate for four physical cores and a
   single interactive user.
3. `OLLAMA_CONTEXT_LENGTH=8192` prevents Ollama from allocating an
   unnecessary 256K context.
4. `OLLAMA_KV_CACHE_TYPE=q8_0` halves key-value cache memory with usually
   negligible quality loss.

### 4.2. Per-request settings

Use the following shape for RAG requests:

```json
{
  "model": "qwen3.5:4b",
  "messages": [
    {
      "role": "system",
      "content": "Answer only from the supplied excerpts."
    },
    {
      "role": "user",
      "content": "Question and excerpts"
    }
  ],
  "stream": false,
  "think": false,
  "keep_alive": "5m",
  "options": {
    "temperature": 0,
    "top_k": 1,
    "top_p": 1,
    "num_predict": 384,
    "num_ctx": 8192,
    "num_thread": 4,
    "num_batch": 256,
    "seed": 42,
    "repeat_penalty": 1.0
  }
}
```

### 4.3. Why these settings matter

1. `think: false` avoids Qwen3.5's default hidden reasoning, which caused an
   observed 71.8-second Qwen3 RAG response.
2. `num_ctx: 8192` prevents the current Ollama default of 4096 from
   truncating five 400-word chunks plus the answer.
3. `num_thread: 4` uses all four physical cores.
4. `temperature: 0` and `top_k: 1` make factual answers deterministic.
5. `num_predict: 384` is sufficient for a cited answer.
6. `num_batch: 256` is optional but reduces peak prompt-processing memory.
7. A 256K context must not be used; the key-value cache would consume far too
   much memory.

### 4.4. Ollama documentation

- Thinking control:
  https://docs.ollama.com/capabilities/thinking
- FAQ, concurrency, flash attention, and key-value cache:
  https://docs.ollama.com/faq
- Context length:
  https://docs.ollama.com/context-length

---

## 5. Retrieval Model Recommendations

### 5.1. Embedding model

Keep the current `BAAI/bge-small-en-v1.5` until the one-off indexing job is
complete. Changing it during ingestion would invalidate the existing index.

After indexing, evaluate recall. If it is insufficient, reindex with
**`Qwen/Qwen3-Embedding-0.6B-Q`**:

1. 1024 dimensions.
2. 1.12 GB in the installed FastEmbed 0.9.1 package.
3. 32K context.
4. Apache 2.0 licence.
5. Massive Text Embedding Benchmark (MTEB) English v2 mean: 70.70.
6. MTEB multilingual mean: 64.33.
7. Instruction-aware; queries should use a task instruction.

The installed FastEmbed package lists `Qwen/Qwen3-Embedding-0.6B-Q` as
supported. The published FastEmbed supported-models page appears to lag
behind the installed package.

Do not switch to EmbeddingGemma 300M by default. It is competitive at 300
million parameters, but it is gated under the Gemma licence and has
inconsistent community retrieval results.

A Qwen3 embedding upgrade requires a full re-embed into a new LanceDB table.
It does not require rebuilding the lexical index.

### 5.2. Reranker

Keep `Xenova/ms-marco-MiniLM-L-6-v2` as the default. It is approximately
80 MB and fast on CPU.

If evaluation shows top-1 misses, consider adding
**`Qwen3-Reranker-0.6B`** as an optional quality tier. Its MTEB reranking
score is substantially higher than BGE-reranker-v2-m3, but FastEmbed does not
currently support it. The existing `reranker.py` module would need a
Sentence Transformers CrossEncoder backend and an additional dependency.

### 5.3. Retrieval sources

- Qwen3-Embedding-0.6B:
  https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Qwen3-Reranker-0.6B:
  https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
- FastEmbed supported models:
  https://qdrant.github.io/fastembed/examples/Supported_Models/
- EmbeddingGemma 300M:
  https://huggingface.co/google/embeddinggemma-300m

---

## 6. Critical RAG Gap

The current implementation retrieves only the top five chunks and asks the
model to answer from them. That cannot answer:

> "What did I buy last year?"

A year of purchases cannot fit into five chunks, and a language model must
not be asked to enumerate a year from a truncated sample.

### 6.1. Required two-path design

#### Path A: Normal factual questions

For questions such as "what was the settlement date in this matter?", keep
the existing top-k RAG path.

#### Path B: Exhaustive aggregation questions

For "what did I buy last year?", use a structured path:

1. Parse the date range deterministically. In November 2026, "last year"
   means 1 January 2025 to 31 December 2025 in the Europe/London timezone.
2. Query a structured `transactions` table for that range.
3. If the table does not yet exist, retrieve all candidate emails in the date
   range using metadata, not top-k semantic search.
4. Extract transactions offline into fields such as:
   - date;
   - merchant;
   - item or service;
   - amount in minor units;
   - currency;
   - payment method;
   - source Gmail message identifier;
   - confidence.
5. Deduplicate order confirmations, shipping notices, and receipts.
6. Use Structured Query Language (SQL) for sums and groupings. Do not ask
   the language model to perform arithmetic.
7. Use the language model only to format the answer and narrative summary.
8. Cite each row with date, merchant, subject, and Gmail message identifier.
9. For hundreds of purchases, provide a table or Comma-Separated Values (CSV)
   export plus a short merchant or category summary.

This keeps language-model weaknesses out of the calculation.

---

## 7. Ingestion Issues Affecting Purchase Retrieval

1. **HTML email bodies are ignored.** The Gmail body extractor only reads
   `text/plain`. Most receipt emails are HTML-only or multipart with a
   text/plain stub. Add HTML-to-text extraction using the already-installed
   `lxml` package.
2. **Gmail attachments are not indexed.** Receipts are often PDF
   attachments. Fetch and parse them using the existing PDF, Word, and Excel
   parsers.
3. **Each Gmail becomes one chunk.** A long email thread can exceed the
   embedding model's context and lose detail. Apply the architecture's
   400-word chunking to Gmail content while preserving message metadata.
4. **Gmail dates are not stored reliably.** The current code stores the
   ingestion time in `modified_at`, not the email date. Parse Gmail's
   `internalDate` or `Date` header into a dedicated `source_date` field.
5. **Google Drive sync only covers Google Docs.** The Drive query filters
   to `application/vnd.google-apps.document`. If Drive contains PDF, Word,
   or Excel files, they are not being ingested.
6. **The lexical query ORs every word.** A question such as "what did I buy
   from last year?" becomes a broad OR query across common words. Add
   stopword removal, phrase matching, and date-range filters.
7. **No metadata filters exist.** Add `source_date`, `source_type`, and
   optional `date_from` and `date_to` filters to both LanceDB and the SQLite
   FTS5 query.
8. **Indexing loads the whole table into memory.**
   `get_indexed_ids()` calls `to_arrow().to_pydict()`, which loads vectors and
   text into Python. This explains the 8 GB indexing process. Use a
   projected query such as
   `search().select(["chunk_id"]).limit(...)` instead.

---

## 8. Benchmark Plan

Do not benchmark while the indexer is running. The current process uses
approximately 8 GB of RAM and 64% of the CPU, which invalidates memory and
latency results.

When indexing is complete:

1. Stop the indexing process and confirm memory is released.
2. Pull `qwen3.5:4b`.
3. Warm each candidate model once.
4. Run the same five to ten representative questions three times.
5. Record:
   - model load time;
   - time to first token (TTFT);
   - output tokens per second;
   - total response time;
   - peak Resident Set Size (RSS);
   - answer correctness;
   - citation correctness.
6. Compare `qwen3.5:4b`, `qwen3:4b-instruct-2507-q4_K_M`, and optionally
   `qwen3.5:9b` if the 4B model is inadequate.
7. Build a golden set of 30-50 questions with known answers before comparing
   embedding and reranker configurations.

---

## 9. Recommended Implementation Sequence

1. Finish the current Gmail and Google Drive ingestion with the existing
   embedding model.
2. Stop the indexer and confirm memory is free.
3. Pull `qwen3.5:4b`.
4. Add `think: false`, `num_ctx: 8192`, `num_thread: 4`, and deterministic
   sampling to the RAG request.
5. Run the benchmark against Qwen3-4B-Instruct-2507.
6. Build the structured transaction path before trying to answer exhaustive
   questions.
7. Only then consider Qwen3-Embedding-0.6B-Q and Qwen3-Reranker-0.6B if the
   golden-set recall is insufficient.

---

## 10. Current Repository State

1. No existing source file was changed to produce this document.
2. The working tree already contained uncommitted Practice Vault work before
   this assessment.
3. No pull, edit, or commit was performed against existing files.
4. No tests were run because no source code was changed.
5. Another agent should re-read the target file immediately before editing
   it, because the tree may have moved on.

---

## 11. Open Questions

1. Does "Google Drive documents" include PDF, Word, and Excel files, or only
   Google Docs?
2. Does "last year" mean calendar year 2025 or the trailing twelve months?
3. Should the appliance load both `qwen3.5:4b` and `qwen3.5:9b`, or keep
   only the 4B model until the benchmark is complete?
4. Should the transaction extractor run during one-off ingestion, or only
   when the first aggregation question is asked?
