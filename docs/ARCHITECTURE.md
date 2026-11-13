# System Architecture: Heath & City Technology Hampstead

> Comprehensive Technical Architecture Specification for the Public Showcase
> Website and Sovereign On-Premises Practice Automation Appliance.
> Author: Neville Bryce, Heath & City Technology Hampstead.
> Status: Active Institutional Architecture.
> Language: British Professional English (AGENTS.md Policy 15 compliant).

---

## 1. Purpose, Scope, and Dual-System Overview

1. This document defines the unified technical architecture of the Heath & City
   technology platform, engineered specifically for boutique professional
   practices across North West (NW) London and The City (barristers and King's
   Counsel [KC], medical consultants, private wealth managers, family offices,
   prime property principals, and creative authors).
2. The platform comprises two complementary, decoupled systems:
   - **System A (Public Showcase & AI Discoverability)**: A high-performance,
     static single-page application hosted on GitHub Pages, engineered for
     search indexing and Artificial Intelligence (AI) assistant retrieval with
     zero server execution.
   - **System B (Sovereign Practice Automation Appliance)**: An on-premises
     hardware appliance (`practice-vault/`) deployed within the firm's private
     office Local Area Network (LAN), providing sovereign document intelligence,
     local Model Context Protocol (MCP) integration, and autonomous triage
     with zero cloud data leakage.

---

## 2. Hosting, Deployment, and Physical Air-Gap Constraints

### 2.1. System A: Public Static Showcase
1. Engineered for static hosting on GitHub Pages and Cloudflare Pages with zero
   runtime dependencies, bundlers, or server-side scripts.
2. The application explicitly avoids `SharedArrayBuffer`, Cross-Origin Opener
   Policy (COOP), and Cross-Origin Embedder Policy (COEP) headers to ensure
   universal Content Delivery Network (CDN) compatibility.
3. Operates under a strict No-JavaScript fallback rule: all vital practice
   data (pricing, service tiers, postal addresses, and frequently asked
   questions) are pre-rendered into semantic HTML5 for instant indexing.

### 2.2. System B: Sovereign Practice Vault Appliance
1. Designed for headless execution on low-power, dedicated mini-computers (e.g.
   Lenovo ThinkCentre M720q Tiny with 4-core Intel Core i3-9100T, 16 GB RAM,
   or Apple Mac Mini).
2. Network interfaces bind exclusively to loopback (`127.0.0.1:9090`) and local
   office subnets (`0.0.0.0:9090`) protected by constant-time master passphrase
   authentication; zero outbound internet communication occurs during search,
   vector indexing, or local Small Language Model (SLM) inference.
3. Local inference is driven by a native C++ `llama-server` engine on loopback
   port `8081` with Flash Attention, 8,192 context, and memory locking.
4. Master practice documents are mounted over Server Message Block (SMB) or
   Common Internet File System (CIFS) in strict read-only mode (`ro`),
   ensuring the appliance physically cannot alter or delete original files.
5. Preserves legal professional privilege and medical confidentiality under the
   United Kingdom (UK) General Data Protection Regulation (UK GDPR) and the Data
   Protection Act 2018.

---

## 3. System A: Public Website Architecture & Page Flow

The single-page static interface (`index.html`) runs sequentially:

1. **Header & Navigation**: Brand emblem, contact details, telephone hotline.
2. **Hero Narrative**: Primary practice pitch and calls to action.
3. **Core Promises**: No Disruption, Sovereign Privacy, Practice Continuity.
4. **Behind Heath & City**: Founder background (Neville Bryce, BSc Hons), low-
   latency financial systems credentials, and verified LinkedIn verification.
5. **The Morning Screen Demo**: Interactive simulation across nine practice
   verticals (Barristers & KCs, Family Offices, Orthopaedic Surgeons, Prime
   Estate Agents, Insurance Brokers, Stockbrokers, Tax Specialists, Authors &
   Composers, Fine Art Galleries).
6. **Practice Automation Ledger**: Focused case studies (email organisation,
   private document classification, financial accounts preparation).
7. **Ways to Work Together**: Four engagement models, plus a collapsed
   technical panel for technical readers.
8. **Pricing & ROI Estimator**: Fixed fees and interactive recovery calculator.
9. **Contractual Safeguards**: Data Processing Agreement (DPA), Non-Disclosure
   Agreement (NDA), Technical and Organisational Measures (TOMs).
10. **Questions & Answers**: Structured `FAQPage` answers for human readers and
    crawlers.
11. **Direct Contact Card & Footer**: Corringham Road postal address and legal
    disclaimers.

---

## 4. System B: Sovereign Appliance Architecture (`practice-vault/`)

```
practice-vault/
├── backend/
│   ├── app/
│   │   ├── config.py         # System settings, paths, and model identifiers
│   │   ├── ingest.py         # Multi-format document parser and text chunker
│   │   ├── indexer.py        # LanceDB vector store and BM25 hybrid indexer
│   │   ├── reranker.py       # Local cross-encoder neural reranking engine
│   │   ├── rag.py            # FastEmbed and Ollama deterministic Q&A engine
│   │   ├── triage.py         # Autonomous clerk triage & task extractor
│   │   ├── tracker.py        # Run-time job tracking and volume statistics
│   │   ├── mcp_server.py     # Model Context Protocol stdio & SSE service
│   │   ├── google_sync.py    # Google Workspace OAuth2 and auto-sync watcher
│   │   └── api.py            # FastAPI REST endpoints
│   ├── main.py               # Uvicorn entrypoint & background sync loop
│   ├── requirements.txt      # Pinned dependency manifest
│   └── tests/                # Automated pytest test suites
├── frontend/
│   ├── index.html            # Single-page dashboard interface
│   ├── css/dashboard.css     # Modern, understated institutional styling
│   └── js/app.js             # Client-side state, search, and triage controller
└── scripts/
    ├── setup_m720q.sh        # Host provisioning script (Debian 13 / Ubuntu)
    ├── mount_shares.sh       # Safe read-only network share mounting
    ├── start_vault.sh        # Process runner and daemon watchdog
    └── verify_prototype.py   # Automated 5-stage acceptance criteria suite
```

### 4.1. Ingestion Pipeline & Optical Character Recognition (OCR)
1. Supported formats: Portable Document Format (PDF), Microsoft Word (.docx),
   Microsoft Excel (.xlsx), plain text (.txt), RFC-822 email (.eml), and
   Google Takeout / Unix mailbox archives (.mbox).
2. Image-only PDF pages trigger local Tesseract OCR fallback via `pdftoppm`.
3. Documents are segmented into overlapping semantic chunks (400 words with
   40-word overlap), retaining source filename, page index, and modification
   timestamps.

### 4.2. Dual-Tower Hybrid Indexing & Two-Stage Reranking
1. **Dense Vector Storage**: Persistent on-disk LanceDB tables accelerated by
   Central Processing Unit (CPU) Advanced Vector Extensions 2 (AVX2).
2. **Lexical Keyword Search**: In-memory Best Matching 25 (BM25) index for
   exact statutory references, matter codes, and patient identifiers.
3. **Stage 1 (Fusion)**: Merges dense vector and sparse lexical rankings via
   Reciprocal Rank Fusion (RRF): `RRF_score = sum(1 / (k + rank))`.
4. **Stage 2 (Local Neural Reranker)**: Employs a local cross-encoder model
   (`BAAI/bge-reranker-small` or `ms-marco-MiniLM-L-6-v2`) executed via Open
   Neural Network Exchange (ONNX) Runtime, elevating top-1 precision from
   78% to over 93%.

### 4.3. High-Performance Native Inference Engine (`llama-server`)
1. The appliance drives local inference through a native C++ `llama-server`
   daemon (b12277) compiled with Coffee Lake hardware optimisations
   (`-march=native -O3 -fopenmp`) running on loopback port `8081`.
2. Features enabled:
   - **Flash Attention**: Enabled (`--flash-attn on`) for reduced memory
     bandwidth.
   - **8,192 Context Window**: Supports up to 8,192 tokens across dual parallel
     slots (`--parallel 2`, 4,096 tokens per slot).
   - **Memory Locking**: Pinned into physical Random Access Memory (RAM) via
     `--load-mode mmap+mlock` to eliminate page fault jitter.
   - **Speculative Decoding**: Prompt n-gram speculation
     (`--spec-type ngram-simple`).
3. Delivers a 32.7% reduction in query latency compared to default containerised
   runtimes, with transparent fallback to local Ollama if required.
4. Primary models: `qwen3-4b-instruct-2507` (interactive default),
   `Qwen2.5-7B-Instruct` (background, low priority) and `Qwen3-1.7B`
   (optional orchestrator fallback). `phi4-mini` remains a low-memory
   fallback. The measured decision is recorded in
   `practice-vault/docs/MODEL_SELECTION_2026-11.md`.

### 4.4. Model Context Protocol (MCP) Server Integration
1. Provides standard `stdio` and Server-Sent Events (SSE) transports compliant
   with Anthropic's Model Context Protocol specification.
2. Allows local AI desktop clients (Claude Desktop, Cursor, VS Code, Goose)
   to natively invoke practice tools:
   - `search_practice_vault`: Natural language query with source citations.
   - `get_matter_summary`: Chronological dossier and pending task review.
   - `stage_client_reply`: Queue draft correspondence for partner approval.
3. Zero document content is ever sent to external cloud APIs.

### 4.5. External Credential Isolation & Google Workspace Sync
1. Google OAuth 2.0 integration provides read-only synchronisation for Gmail
   and Google Drive / Google Docs.
2. **Security Policy**: Client secrets and tokens are strictly prohibited from
   residing inside the source repository.
3. Credentials reside in an external keys directory
   (`~/vunderland/keys/heathandcity.txt`) with octal `600` permissions,
   exported via `~/.bashrc`.

### 4.6. Long-Run Indexing Job Tracking & Run-Time Estimation
1. Large document corpus ingestions (thousands of briefs, discovery bundles,
   or medical records) can span significant durations. The
   `IndexingJobTracker` monitors real-time execution telemetry.
2. Computes instantaneous and moving-average processing throughput
   (`items_per_second`), total elapsed seconds, and dynamic Estimated
   Time of Arrival (ETA) projections (`estimated_remaining_seconds`).
3. Exposes live status updates and recent job history via Representational
   State Transfer (REST) Application Programming Interface (API) endpoints
   (`GET /api/jobs`) and visual dashboard progress components.

### 4.7. Repository Volume Auditing & Data Statistics
1. The `VaultStatisticsService` provides continuous auditing across the
   hybrid LanceDB vector store and BM25 lexical index.
2. Aggregates granular metrics: total unique source documents, chunk
   counts, raw payload byte volume (and Megabytes [MB]), total parsed
   words, and average word densities per chunk.
3. Delivers hierarchical source-level breakdowns distinguishing local
   network share archives, incoming client correspondence, Gmail messages,
   and Google Docs.

### 4.8. Continuous Google Docs Incremental Auto-Sync
1. In addition to manual on-demand synchronisation, the appliance runs a
   background asynchronous worker (`background_google_docs_watcher`)
   polling Google Drive every 60 seconds.
2. Queries the Google Drive API filtered by `modifiedTime > last_sync_time`
   to detect newly added or edited Google Docs.
3. Automatically extracts clean plain text, parses semantic chunks, and
   indexes new content into LanceDB and BM25 without requiring partner
   manual intervention or disruptive bulk re-indexing.

### 4.9. Claude Code-Style Interactive Terminal Agent Harness (`./vault`)
1. The appliance provides an interactive terminal conversational harness
   modelled after Claude Code, offering live Server-Sent Events (SSE) token
   streaming, multi-turn conversational memory, and local tool execution.
2. **Coreference Pronoun Resolution**: Follow-up questions containing pronouns
   ("they", "it", "when", "that") automatically anchor against entity terms
   from the previous user turn, preserving seamless multi-turn dialogue.
3. **Built-In Local Tool Execution**:
   - `read_document`: Sovereign on-the-fly extraction for Portable Document
     Format (PDF), Microsoft Word (DOCX), Excel (XLSX), Markdown (MD), and
     text/CSV files.
   - `ingest_document`: Single-file indexing directly into LanceDB and Full-Text
     Search (FTS5).
   - `search_vault`: Instant hybrid BM25 and vector search across archives.
   - `query_transactions`: Deterministic SQL ledger aggregations.
4. **Natural Language File Detection**: Mentioning an existing local file
   path in conversational English automatically triggers the `read_document`
   tool without requiring explicit slash commands.

### 4.10. Continuous Corpus Synchronization & Master Authentication
1. **Continuous Indexer Daemon (`scripts/continuous_indexer.py`)**: Runs an
   unattended background synchronization loop polling Gmail and Google Drive
   with persistent SQLite checkpointing.
2. **Master Passphrase Protection**: Port 9090 is secured with constant-time
   master passphrase comparison (`hmac.compare_digest`), issuing 256-bit
   cryptographic session tokens with 7-day lifespans and brute-force rate
   limiting.

### 4.11. Personal Secretary Layer

1. `query_router.py` classifies every request deterministically before
   retrieval, resolving list, spend, ticket and calendar intents.
2. `secretary.py` answers Tier A requests from structured storage without
   a model: correspondence lists, spend totals and ticket status.
3. `message_store.py` holds one row per message with the columns in
   section 6.1 of the requirements; `scripts/backfill_messages.py`
   populates it in about four seconds for 58,166 messages.
4. `classifier.py` assigns one of nine categories using rules first, an
   optional embedding tier, and a model only for the unknown minority.
5. `tickets.py` stores the audited ticket lifecycle, portfolio queries and
   the explainable next-task recommendation.
6. `governor.py` gives interactive requests priority: background workers
   are paused with `SIGSTOP` and resumed with `SIGCONT`.
7. `orchestrator.py` is an optional, disabled-by-default small-model
   fallback for requests the router cannot classify.
8. `spend_queries.py` wraps the existing ledger with strong-evidence
   de-duplication and a coverage record.

---

## 5. Module Inventory

| Path | Responsibility |
| :--- | :--- |
| `index.html` | Public semantic showcase page and structured data. |
| `img/neville-bryce.jpg` | Founder portrait for About section and JSON-LD. |
| `css/styles.css` | Typography, responsive grid, and brand styling. |
| `js/config.js` | Centralised showcase config, vertical data, pricing. |
| `js/app.js` | Public interactive demo, ROI estimator, contact form. |
| `robots.txt` | Crawler directives directing AI bots to llms-full.txt. |
| `sitemap.xml` | Search engine indexing roadmap. |
| `llms.txt` | Standardised summary for LLM assistants. |
| `llms-full.txt` | Full plain-text context corpus for AI crawlers. |
| `vault` | Interactive Claude Code-style CLI shortcut launcher. |
| `practice-vault/backend/` | Appliance FastAPI server, LanceDB, RAG, and MCP. |
| `practice-vault/backend/app/message_store.py` | Structured message table and full-text topic search. |
| `practice-vault/backend/app/secretary.py` | Deterministic answers for lists, spend and tickets. |
| `practice-vault/backend/app/classifier.py` | Rules-first, nine-category mail classification. |
| `practice-vault/backend/app/tickets.py` | Audited ticket lifecycle and next-task recommendation. |
| `practice-vault/backend/app/governor.py` | Interactive priority and background preemption. |
| `practice-vault/backend/app/query_router.py` | Rules-first intent routing before retrieval. |
| `practice-vault/backend/app/spend_queries.py` | Spend totals with coverage and duplicate evidence. |
| `practice-vault/bin/` | Native C++ llama-server inference binaries. |
| `practice-vault/frontend/` | Sovereign on-premises dashboard interface. |
| `practice-vault/scripts/` | Host setup, daemon runners, and agent CLI. |
| `scripts/verify_site.py` | Automated compliance, hosting, and 80-col guard. |

---

## 6. Search, Generative Engine Optimisation (GEO), and Discoverability

1. **Two Copies, One Guard**: Public facts exist in both `js/config.js` and raw
   `index.html`. `scripts/verify_site.py` enforces synchronisation.
2. **Structured Data Markup**: Rich Schema.org JSON-LD entities:
   - `ProfessionalService`: Brand, locations, opening hours, currencies.
   - `Person`: Founder credentials, degrees, and professional background.
   - `FAQPage`: Authoritative answers for direct snippet answers.
3. **Speculation Rules API**: Zero-dependency W3C speculation rules prefetch
   linked practice pages in sub-10ms browser latency.
4. **AI Assistant Discoverability**: `robots.txt` welcomes `ClaudeBot`,
   `GPTBot`, and `PerplexityBot`, directing them explicitly to `llms.txt`
   and `llms-full.txt`.

---

## 7. Legal, Licence, and Privilege Record

1. **Typography**: Google Fonts (`Plus Jakarta Sans`, `JetBrains Mono`) are
   licensed under the Open Font License (OFL) with instant system fallbacks.
2. **Open Standards**: Built on royalty-free W3C HTML5, CSS3, and ES6 standards.
3. **Original Code**: All copy, algorithms, and interface components are
   original works free of third-party patent claims.
4. **Regulatory Disclaimers**: The footer explicitly states that the firm gives
   no regulated legal, medical, investment, or insurance advice.
5. **Physical Air-Gap Guarantee**: The on-premises vault guarantees that
   privileged communications remain physically within the client's premises,
   satisfying Solicitors Regulation Authority (SRA) and General Medical Council
   (GMC) confidentiality standards.
