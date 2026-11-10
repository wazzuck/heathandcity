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
   ThinkCentre M720q Tiny running Debian 13 or equivalent Linux mini-PC).
2. **Read-Only Data Access**: Network shares are mounted in strict read-only
   mode (`ro`), preventing accidental document modification or data loss.
3. **Deterministic Citations**: Answers are grounded directly in practice
   records with page and filename citations, preserving legal privilege and
   professional liability protection.
4. **Human-in-the-Loop Safeguard**: Automated clerk drafts polite
   correspondence staged for affirmative partner approval.

---

## 2. Directory Architecture

```
practice-vault/
├── backend/
│   ├── app/
│   │   ├── config.py             # System paths, model names, port bindings
│   │   ├── ingest.py             # Multi-format document parser & chunker
│   │   ├── indexer.py            # LanceDB vector store & BM25 hybrid engine
│   │   ├── rag.py                # FastEmbed and Ollama RAG query engine
│   │   ├── triage.py             # Autonomous inbox triage & task extractor
│   │   └── api.py                # FastAPI endpoints
│   ├── main.py                   # Uvicorn entrypoint (127.0.0.1:8080)
│   ├── requirements.txt          # Frozen Python manifest
│   └── tests/                    # Pytest automated test suite
├── frontend/
│   ├── index.html                # Sovereign single-page web dashboard
│   ├── css/dashboard.css         # Modern understated practice styling
│   └── js/app.js                 # Interactive search, clerk, and status UI
├── scripts/
│   ├── setup_m720q.sh            # Automated host provisioning script
│   ├── mount_shares.sh           # Safe read-only CIFS/SMB share mounting
│   ├── start_vault.sh            # Production runner & service watchdog
│   └── verify_prototype.py       # Acceptance criteria verification suite
├── data/
│   ├── sample_docs/              # Mock legal, medical, and financial records
│   ├── lancedb/                  # Local on-disk LanceDB tables
│   └── inbox_staging/            # Staging folder for correspondence
└── README.md                     # Operational runbook
```

---

## 3. Quick Start & Execution

### 3.1. Starting the Appliance
To start the local web dashboard and API service:

```bash
cd /opt/practice-vault
./scripts/start_vault.sh
```

Navigate to `http://127.0.0.1:8080` in your local web browser.

### 3.2. Running the Automated Test Suite
To execute the unit tests:

```bash
cd /opt/practice-vault/backend
../venv/bin/pytest tests/
```

### 3.3. Running Acceptance Criteria Verification
To run the end-to-end prototype verification against Section 5.6 of the product
specification:

```bash
cd /opt/practice-vault
./venv/bin/python scripts/verify_prototype.py
```

---

## 4. Acceptance Criteria Verification

The appliance satisfies all five acceptance criteria:
- **Cold Start & Memory Budget**: Resident memory remains well below the
  1,500 MB budget during idle and search operations.
- **Deterministic Ingestion**: Multi-format document parser handles PDF, DOCX,
  XLSX, and TXT with local Tesseract OCR fallback.
- **Exact Citations**: Every answer is attributed to the source document and
  page number.
- **Zero Cloud Leakage**: Network interfaces bind strictly to loopback
  (127.0.0.1) and local subnet; no public egress occurs.
- **Human-in-the-Loop Safeguard**: Draft replies are staged in an approval
  queue requiring partner sign-off before transmission.
