# Heath & City Practice Vault: Sovereign Appliance Runbook

> On-premises document intelligence, semantic search, and autonomous clerk
> for boutique private practices across Hampstead and North West London.

---

## 1. Executive Overview

The Heath & City Practice Vault is a sovereign, self-contained hardware and
software appliance engineered to deliver private document intelligence,
statutory deadline tracking, and inbox correspondence triage with zero
operational disruption:

1. **Zero Cloud Leakage**: All vector embeddings, document parsing, and Large
   Language Model (LLM) reasoning execute strictly on local hardware (Lenovo
   ThinkCentre M720q Tiny with 4-core Intel Core i3-9100T, 16 GB RAM, running
   Debian 13 or equivalent Linux mini-PC).
2. **Read-Only Data Access**: Network shares and archives are mounted in
   strict read-only mode (`ro`), preventing accidental document modification
   or data loss.
3. **Deterministic Citations**: Answers are grounded directly in practice
   records with page and filename citations, preserving legal privilege and
   professional liability protection.
4. **Human-in-the-Loop Safeguard**: Automated clerk drafts polite
   correspondence staged for affirmative partner approval.
5. **Interactive Agent Harness**: Includes a Claude Code-style terminal
   interface featuring real-time token streaming, multi-turn memory, pronoun
   coreference resolution, and built-in local tool execution.

---

## 2. Directory Architecture

```
practice-vault/
├── backend/
│   ├── app/
│   │   ├── config.py             # System paths, model names, port bindings
│   │   ├── ingest.py             # Multi-format document parser & chunker
│   │   ├── indexer.py            # LanceDB vector store & BM25 hybrid engine
│   │   ├── rag.py                # FastEmbed and native llama-server engine
│   │   ├── triage.py             # Autonomous inbox triage & task extractor
│   │   └── api.py                # Authenticated FastAPI endpoints
│   ├── main.py                   # Uvicorn entrypoint (0.0.0.0:9090)
│   ├── requirements.txt          # Frozen Python manifest
│   └── tests/                    # Pytest automated test suite (30 tests)
├── bin/
│   └── llama-server              # Native C++ AVX2/FMA/F16C inference engine
├── frontend/
│   ├── index.html                # Sovereign single-page web dashboard
│   ├── css/dashboard.css         # Modern understated practice styling
│   └── js/app.js                 # Interactive search, clerk, and status UI
├── scripts/
│   ├── setup_m720q.sh            # Automated host provisioning script
│   ├── mount_shares.sh           # Safe read-only CIFS/SMB share mounting
│   ├── start_vault.sh            # Production runner & service watchdog
│   ├── start_llama_server.sh     # Native inference runner (port 8081)
│   ├── continuous_indexer.py     # Background Gmail & Drive synchronization
│   ├── vault_cli.py              # Claude Code-style interactive agent CLI
│   └── verify_legal_compliance.py # 4-gate commercial regulatory auditor
├── data/
│   ├── sample_docs/              # Mock legal, medical, and financial records
│   ├── lancedb/                  # Local on-disk LanceDB tables
│   └── inbox_staging/            # Staging folder for correspondence
├── vault                         # Executable shortcut to terminal interface
└── README.md                     # Operational runbook
```

---

## 3. Quick Start & Execution

### 3.1. Starting the Appliance Daemons
The appliance operates via two coordinated background daemons:

1. **Native Inference Daemon (`llama-server`)**:
   Runs on loopback port `8081` with Flash Attention, 8,192 context window,
   `--parallel 2` execution slots, memory locking (`mmap+mlock`), and prompt
   n-gram speculative decoding:
   ```bash
   ./scripts/start_llama_server.sh
   ```

2. **Core Backend Daemon (`api.py`)**:
   Runs on `0.0.0.0:9090` with master passphrase authentication:
   ```bash
   ./scripts/start_vault.sh
   ```

Navigate to `http://127.0.0.1:9090` or `http://<lan-ip>:9090` in any web
browser on the local network.

### 3.2. Master Passphrase Authentication
- **Default Master Passphrase**: `HeathCity2026!` (configurable via the
  `PRACTICE_VAULT_PASSWORD` environment variable).
- **Authentication Lifecycle**: Successful login provisions an HTTP-only
  `vault_session` cookie (or 256-bit Bearer token) valid for 7 days.
- **Lock Terminal**: Clicking "Lock Terminal" in the dashboard header
  immediately revokes the session token.
- **API Access**: Automated scripts authenticate via the `X-Vault-Password`
  header or `Authorization: Bearer <token>`.

---

## 4. Claude Code-Style Interactive Terminal (`./vault`)

The appliance features an interactive conversational agent harness modelled
after Claude Code, providing terminal-based interrogation of practice
records with zero cloud dependencies.

### 4.1. Launching Interactive Session
```bash
./vault
```

### 4.2. Conversational Capabilities
- **Real-Time Token Streaming**: Streams tokens live via Server-Sent Events
  (SSE) from the native C++ inference engine.
- **Multi-Turn Context & Coreference Anchoring**: Retains conversational turns
  across the session. Automatically detects pronouns in follow-up questions
  (e.g., *"When were they sent?"* or *"What did that say?"*) and anchors
  retrieval against entities from prior turns.
- **Rich Terminal Layout**: Renders user query badges (`● You`), assistant
  response headers (`╭─ Practice Clerk`), tool call status panels, and
  tabular source citation summaries.

### 4.3. Built-In Local Tool Execution
The CLI includes built-in sovereign tool executors:

1. **`read_document`**:
   Extracts text and metadata on the fly from Portable Document Format
   (PDF), Microsoft Word (DOCX), Excel (XLSX), Markdown (MD), and text/CSV
   files without requiring pre-indexing.
   - *Natural Language*: Simply mention an existing file path in your prompt:
     ```text
     vault> Can you read /path/to/contract.pdf and check the liability clause?
     ```
   - *Slash Command*:
     ```text
     vault> /read /path/to/contract.pdf Summarise key obligations
     ```
   - *One-Shot CLI Flag*:
     ```bash
     ./vault -r /path/to/contract.pdf "Summarise key obligations"
     ```

2. **`ingest_document`**:
   Parses and indexes a single external file directly into LanceDB vector
   storage and SQLite Full-Text Search (FTS5):
   ```text
   vault> /ingest /path/to/new_brief.docx
   ```
   or via CLI:
   ```bash
   ./vault --ingest /path/to/new_brief.docx
   ```

3. **`search_vault`**:
   Executes sub-second hybrid lexical (FTS5) and dense vector search:
   ```text
   vault> /search Linda cancer diagnosis
   ```

4. **`query_transactions`**:
   Directs natural language financial queries to deterministic Structured
   Query Language (SQL) ledger aggregations:
   ```text
   vault> /fin How much was paid to counsel in 2024?
   ```

5. **Diagnostic Commands**:
   - `/status`: Inspect active Large Language Model (LLM), resident memory,
     and chunk volume.
   - `/sync`: Check Google Drive and Gmail synchronization state.
   - `/reset`: Clear conversational history context.

---

## 5. Verification & Regulatory Compliance

### 5.1. Running the Automated Test Suite
To execute all 30 unit and integration tests:
```bash
cd backend
../venv/bin/pytest tests/
```

### 5.2. Running Legal & Regulatory Compliance Audit
To execute the four-gate commercial regulatory auditor:
```bash
./venv/bin/python scripts/verify_legal_compliance.py
```

The verification script enforces:
- **Gate 1 (Commercial Licensing)**: Audits 100% of Python dependencies for
  permissive commercial licences (MIT, Apache-2.0, BSD) with zero copyleft
  (GPL/AGPL) contamination.
- **Gate 2 (UK GDPR Sovereignty)**: Verifies strictly sovereign on-premises
  network binding and zero external cloud AI API dependencies.
- **Gate 3 (Legal Professional Privilege)**: Confirms mandatory source
  citation enforcement and zero-hallucination refusal guards.
- **Gate 4 (NHS Caldicott Principles)**: Validates compliance with Caldicott
  Principles 1-8, Data Security and Protection Toolkit (DSPT), and Digital
  Technology Assessment Criteria (DTAC) requirements.
