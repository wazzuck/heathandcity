# Practice Vault Personal Secretary: Feasibility Handover

> Assessment Handover for an External Artificial Intelligence (AI) Agent.
> Purpose: transfer a completed feasibility assessment of turning the
> on-premises Practice Vault into a personal secretary, so that another
> agent can interpret, challenge or act on it without this conversation.
> Assessed: 2026-11-13. Status: research only; no code was changed.
> Language: British Professional English (AGENTS.md Policy 15).

---

## 1. How to read this document

1. Section 2 states the operator's request verbatim in summary form.
2. Section 3 lists facts, each tagged with its evidence class:
   - `[MEASURED]` observed on the host during the assessment;
   - `[REPO]` read from a file in the repository or data directory;
   - `[ESTIMATE]` derived by arithmetic or from public benchmarks.
3. Section 4 gives the findings; section 5 the verdict per feature.
4. Section 6 gives the recommended architecture and ordered next steps.
5. Section 7 lists open questions and known uncertainties. Treat any
   `[ESTIMATE]` as a hypothesis to re-measure before relying on it.

---

## 2. The operator's request

The operator wants the local Large Language Model (LLM) server to act as
a personal secretary that can:

1. answer "show me my recent emails" correctly (it currently returns
   emails over 12 years old);
2. classify emails;
3. read meeting invitations and prompt the user to accept or decline;
4. read and edit the calendar;
5. discuss emails, find facts in them, and draft new emails from those
   facts;
6. use a user-maintained knowledge base of jargon (for example legal
   vocabulary);
7. track tasks in a Customer Relationship Management (CRM) system, link
   emails to tasks, and give status updates on request;
8. use the internet when unsure;
9. prepare in the background for as long as it likes, but respond in
   about 5 seconds to simple questions and a few minutes to complex ones.

The operator asked: is this too ambitious for the hardware and for the
current state of offline AI?

---

## 3. Facts

### 3.1. Host hardware

1. `[MEASURED]` Lenovo ThinkCentre M720q; Intel Core i3-9100T, 4 cores,
   4 threads, 35 W, Advanced Vector Extensions 2 (AVX2), no AVX-512.
2. `[MEASURED]` Memory: 16 GB as 2 x 8 GB DDR4, rated 2667 MT/s,
   configured at 2400 MT/s. About 9 GB available at assessment time.
3. `[MEASURED]` Graphics: Intel UHD Graphics 630 only; no discrete
   Graphics Processing Unit (GPU).
4. `[MEASURED]` Storage: 222 GB NVMe Solid State Drive (SSD), 132 GB
   free.

### 3.2. Inference stack

1. `[MEASURED]` Running process:
   `/home/neville/practice-vault/bin/llama-server` with model
   `phi4-mini.gguf` (Phi-4-mini, 3.8 billion parameters, 2.4 GB file),
   `-c 8192 -t 4 --parallel 2 --flash-attn on`, quantised key-value
   cache (`q8_0`), `--spec-type ngram-simple`, port 8081.
2. `[REPO]` `~/llm-benchmark/head_to_head_results.json`:
   prompt processing about 47 tokens per second; generation about
   10 tokens per second; 238-token prompt with 36-token answer took
   8.6 seconds wall time.
3. `[REPO]` `~/practice-vault/docs/LLM_SERVER_COMPARISON_AND_BENCHMARK_
   REPORT.md` section 3.3: Vulkan offload to the UHD 630 was slower
   (about 16.8 prompt and 5.5 generation tokens per second).
4. `[REPO]` Ollama is installed (`/usr/local/bin/ollama`) as a fallback,
   disabled unless `START_OLLAMA_FALLBACK=1`.

### 3.3. Data and application

1. `[REPO]` Application code: `~/practice-vault/backend/app/`
   (about 13,000 lines of Python). Relevant modules: `rag.py`,
   `temporal_filter.py`, `triage.py`, `calendar_engine.py`,
   `tracker.py`, `fact_engine.py`, `relationship_engine.py`,
   `web_enrichment.py`, `google_sync.py`, `ambiguity_router.py`.
2. `[REPO]` Data directory: `~/practice-vault-data/`. Key stores:
   `practice_fts.db` (SQLite full-text index, 441 MB), `lancedb/`
   (vector index, 269 MB), `calendar_events.db`, `people_entities.db`,
   `established_facts.db`, `transactions.db`.
3. `[REPO]` `vault_statistics.json`: 69,173 chunks; 68,885 Gmail
   messages; 268 Google Docs; 20 local documents; 26.6 million words.
4. `[MEASURED]` `practice_fts` schema: `chunk_id, source_path,
   file_name, page_number, section_heading, text, modified_at`. There is
   no structured email table (no sender, recipients, thread ID, labels,
   read state or attachment fields as columns).
5. `[MEASURED]` `modified_at` holds the email date: range 2004-09-22 to
   2026-11-11T10:59:39Z.
6. `[MEASURED]` The three newest rows are the same TabbFORUM newsletter
   chunk, so there are duplicates and no newsletter filtering.
7. `[MEASURED]` The newest email is dated 2026-11-11, two days before
   the assessment, so synchronisation has probably stalled. Cause not
   investigated.

---

## 4. Findings

### 4.1. Root cause of the "recent emails" defect (software, not hardware)

1. `[REPO]` `TemporalRangeParser.extract_date_range` in
   `temporal_filter.py` recognises explicit months, quarters, years,
   "last/this month" and "last/this year". It does not recognise
   "recent", "latest", "new", "today's", "this week" or "unread".
2. `[REPO]` In `rag.py` (around lines 1132 and 1688), date filtering is
   applied only after retrieval, and only when a date range was parsed.
3. Therefore "show me my recent emails" falls through to lexical and
   semantic search, which ranks by textual similarity to the words
   "recent emails", not by date.
4. The correct execution is a structured query, for example
   `ORDER BY modified_at DESC LIMIT 20`, de-duplicated by message. It
   needs no LLM and completes in milliseconds.

### 4.2. Latency arithmetic (the deciding constraint)

All figures `[ESTIMATE]`, derived from the measured 47 and 10 tokens per
second. A token is roughly three quarters of an English word.

| Scenario                               | Tokens in / out | Time      |
|----------------------------------------|-----------------|-----------|
| Bare question, no email context        | 150 / 30        | about 6 s |
| Answer from 5 retrieved emails         | 2,500 / 150     | about 68 s|
| Classify one email                     | 400 / 10        | about 9 s |
| Classify full archive, one pass        | 27.5 M / small  | about 7 d |
| Classify last 12 months (about 5,000)  | 2 M / small     | about 12 h|

Conclusion: an answer that requires the model to read email text cannot
meet a 5-second target on this host. Model or flag changes give at most
about a two-fold gain. Five seconds is reachable only for answers served
from Structured Query Language (SQL) queries or from pre-computed
results.

### 4.3. Capability of small offline models (as of November 2026)

1. Good at: classification, extraction into fixed fields, short
   summaries, rewording, and narrow instructions under a JSON grammar.
2. Weak at: multi-document reasoning, autonomous multi-step tool use,
   recognising their own uncertainty, and polished long-form drafting.
3. Credible offline assistants therefore use deterministic software and
   indexes for the work, the model as a language layer, and heavy
   pre-computation.

---

## 5. Verdict per requested feature (current host)

`Yes` = feasible now; `Partial` = feasible with stated limits;
`No` = not realistic on this hardware.

| # | Feature                         | Verdict | Required approach          |
|---|---------------------------------|---------|----------------------------|
| 1 | Recent / unread / from-X email  | Yes     | Structured table plus SQL; |
|   |                                 |         | no LLM; under 1 s          |
| 2 | Classify emails                 | Yes     | Header and sender rules,   |
|   |                                 |         | embedding classifier; LLM  |
|   |                                 |         | on new mail overnight      |
| 3 | Invitations: accept or decline  | Yes     | Parse iCalendar parts; SQL |
|   |                                 |         | clash check                |
| 4 | Read and edit calendar          | Yes     | Google Calendar API plus   |
|   |                                 |         | local mirror               |
| 5 | Find facts in emails            | Partial | Search instant; written    |
|   |                                 |         | answer 30-90 s             |
| 5 | Discuss emails, draft replies   | Partial | 1-3 min; short, routine    |
|   |                                 |         | replies only               |
| 6 | Jargon knowledge base           | Yes     | Glossary table for prompts |
|   |                                 |         | and search synonyms        |
| 7 | CRM tasks linked to emails      | Yes     | Ordinary relational tables |
| 7 | Status update on a task         | Partial | Instant if summarised      |
|   |                                 |         | nightly; slow on demand    |
| 8 | Internet look-up when unsure    | Partial | Explicit trigger rules;    |
|   |                                 |         | persist results offline    |
|   |                                 |         | (AGENTS.md Policy 16)      |
| - | Free-form "do everything" agent | No      | Use scripted workflows     |

Overall: not too ambitious in scope; too ambitious if the LLM is
expected to do retrieval and reasoning itself at interactive speed.

---

## 6. Recommended architecture and next steps

### 6.1. Principle

Software does the work; the model only handles language.

1. A fast intent router classifies each request. Rules come first; a
   grammar-constrained LLM call is the fallback.
2. List, filter and count requests go to SQL (under 2 seconds).
3. Status and summary requests read pre-computed nightly summaries
   (under 2 seconds).
4. Fact-finding, discussion and drafting go to retrieval plus a streamed
   LLM answer (30 seconds to 3 minutes), with visible progress.
5. An overnight worker classifies, de-duplicates, extracts invitations,
   links emails to CRM matters, and refreshes summaries.

### 6.2. Ordered next steps (highest value first)

1. Investigate and repair the stalled Gmail synchronisation.
2. Add a structured `messages` table: message ID, thread ID, date,
   sender, recipients, subject, labels, category, has-invitation,
   duplicate-of. Backfill from existing ingested data where possible.
3. Add rules-first routing for "recent", "latest", "unread", "today",
   "this week", "from <person>", "invitations". Extend
   `temporal_filter.py` and the router; do not build a parallel parser
   (AGENTS.md Policy 9).
4. Two-tier classification: rules for newsletters and notifications;
   an embedding-based classifier for the remainder; LLM only for the
   last 90 days and new arrivals.
5. Invitation handling with accept, decline or tentative, clash
   detection, and write-back through the Calendar API.
6. User-editable glossary and practice profile table.
7. Nightly per-matter status summaries in the CRM tracker.
8. Interface: stream tokens, show retrieval progress, and state the
   expected wait on slow paths.
9. Only after steps 1-8, benchmark candidate models (for example
   Qwen3-4B-Instruct-2507 or the Qwen3.5 4B class against Phi-4-mini)
   on the router and extraction tasks.

### 6.3. Hardware options (all `[ESTIMATE]`; benchmark before buying)

| Option                               | Cost        | Expected effect     |
|--------------------------------------|-------------|---------------------|
| Keep host, re-architect              | £0          | Look-ups under 2 s; |
|                                      |             | drafts 1-3 min      |
| RAM to 32 GB                         | about £60   | Larger Mixture-of-  |
|                                      |             | Experts model (e.g. |
|                                      |             | Qwen3-30B-A3B);     |
|                                      |             | smarter, not faster |
| Apple Mac mini M4, 24 GB or more     | about £800  | 5-10x prompt speed  |
| Mini PC, Ryzen AI or 780M/890M, 64 GB| £500-900    | 3-6x prompt speed   |
| Desktop with 16 GB or more GPU       | £900-1,500  | 20-50x prompt speed |

---

## 7. Open questions and uncertainties

1. Why synchronisation stopped on 2026-11-11 (not investigated).
2. What share of the archive is newsletters or notifications (assumed
   to be the majority; not measured).
3. Whether existing `triage.py`, `calendar_engine.py` and `tracker.py`
   already cover parts of steps 4-7; they were listed but not reviewed
   in depth. Read them before designing new code.
4. All new-hardware speed figures come from public benchmarks, not from
   this workload.
5. Model comparison claims in section 6.2 step 9 are based on public
   reports and have not been tested on this host.
6. Any new dependency or feature must pass
   `scripts/verify_legal_compliance.py` and have an offline counterpart
   (AGENTS.md Policies 4 and 16).
