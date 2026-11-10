# Technical Specification: Sovereign Practice Automation Appliance

> Product and Technical Architecture Specification for the Heath & City
> On-Premises Office Automation and Private Document Intelligence System.
> Author: Neville Bryce, Heath & City Technology Hampstead.
> Status: Working Specification.
> Language: British Professional English (AGENTS.md Policy 15 compliant).

---

## 1. Executive Summary & Product Vision

1. The Heath & City Automation Appliance is a self-contained, sovereign
   hardware and software system deployed directly within the client's office
   (or private sovereign UK data vault).
2. It acts as an autonomous digital assistant ("Automated Practice Clerk")
   for boutique professional practices (barristers, medical consultants,
   family offices, prime estate agents, brokers, accountants, and creative
   studios).
3. The design philosophy is **Zero Operational Disruption**:
   - The client never changes their existing daily software (Outlook, Word,
     Excel).
   - The appliance reads data via read-only local network shares and read-only
     email synchronization.
   - Zero confidential client, patient, or financial records are ever
     transmitted to third-party public cloud Application Programming
     Interfaces (APIs).
   - All processing executes locally on dedicated hardware with 100% United
     Kingdom (UK) General Data Protection Regulation (GDPR) compliance.

---

## 2. Core Feature Set

### 2.1. Sovereign Semantic Search & Document Intelligence
1. **Multi-Format Ingestion:** Continuously indexes twenty years of historical
   and live practice documents: Portable Document Format (PDF), scanned
   bundles (via local Optical Character Recognition [OCR]), Microsoft Word
   (.docx), Excel (.xlsx), and email archives (.pst, .ost, .msg).
2. **Deterministic Citations:** Answers and search results link directly to the
   primary source document, volume, and exact page or paragraph number. Zero
   hallucination tolerance for professional liability protection.
3. **Natural Language Question Answering:** Principals can query their entire
   practice archive in plain English (e.g. *"What specific dosage did I
   prescribe to patient X in June 2023?"* or *"What did we advise regarding the
   offshore trust variation in 2019?"*).

### 2.2. Automated Practice Clerk & Inbox Triage
1. **Background Intake:** Connects to Microsoft 365 or Internet Message Access
   Protocol (IMAP) on a read-only schedule.
2. **Automated Triage & Extraction:**
   - Extracts incoming tasks, hearing dates, and transaction deadlines.
   - Categorises urgency and flags conflicting diary commitments.
   - Identifies financial amounts, fee notes, and billing remittances.
3. **Pre-Drafted Responses:** For routine enquiries (e.g. fee quotes,
   document requests, hearing availability), the system drafts a polite
   response in the principal's personal style, staging it in an "Awaiting
   Approval" queue. Nothing is ever sent without explicit human sign-off.

### 2.3. Bespoke Zero-Bloat Customer Relationship Management (CRM)
1. **Matter-Centric Architecture:** Unlike bloated enterprise CRMs, the system
   organises around active matters, clients, and deadlines.
2. **Autonomous Entity Association:** Incoming emails and documents are
   automatically attached to the correct client or matter record without manual
   filing.
3. **Practice Continuity ("The Shared Brain"):** If a key partner, practice
   manager, or personal assistant is away, any authorised team member can view
   the complete chronological status and outstanding tasks for any matter in
   under sixty seconds.

### 2.4. Advanced Value-Add Capabilities
1. **Automated Chronology Generation:** For complex litigation bundles or
   medico-legal files, automatically generates a dated chronological event table
   cross-referencing every event to its source PDF page.
2. **Financial Reconciliation & Leakage Detection:** Cross-checks invoiced
   amounts against incoming insurance remittances, underwriter commissions, or
   royalty statements, flagging underpayments and missing fees automatically.
3. **Local Audio Dictation Transcription:** Ingests voice memos from phones or
   dictaphones, transcribes them privately via local Whisper models, and formats
   them into formal client letters using the practice's Word template.
4. **Statutory & Limitation Deadline Guard:** Proactively tracks court filing
   dates, Companies House filings, statutory tenancy renewals (CP12/EICR), and
   limitation periods, escalating approaching deadlines before they become
   emergencies.

---

## 3. Systems & Hardware Architecture

### 3.1. Hardware Footprint
1. **Development & Prototype Testbed:**
   - Hardware: Lenovo ThinkCentre M720q Tiny (1-litre chassis).
   - Processor: Intel Core i3-9100T (4 cores, 3.10-3.70 GHz) with Advanced
     Vector Extensions 2 (AVX2) instruction set.
   - Memory: 16 GB DDR4 Random Access Memory (RAM).
   - Storage: 240 GB Non-Volatile Memory Express (NVMe) Solid State Drive.
   - Power: 35W low-power, whisper-quiet operation.
2. **Production Appliance Options:**
   - Option A: Lenovo ThinkCentre / HP EliteDesk Mini PC (Intel 12th/13th Gen,
     32 GB RAM, 1 TB NVMe SSD). Approximate cost: £450 - £650.
   - Option B: Apple Mac Mini (M4 chip with Unified Memory, 16 GB - 24 GB RAM,
     512 GB SSD). Approximate cost: £599 - £799.

### 3.2. Software Stack
1. **Operating System:** Linux (Debian 13 [Trixie], with Ubuntu 24.04 LTS also
   supported), configured for silent execution with persistent service uptime.
2. **Document Ingestion & OCR:**
   - Text extractors: `pypdf`, `pdfplumber`, `python-docx`, `openpyxl`.
   - Local OCR: `Tesseract OCR` or `ocrmypdf` for scanned document bundles.
3. **Embedding & Vector Storage Engine:**
   - Embedding Model: `bge-small-en-v1.5` or `nomic-embed-text` executed via
     ONNX Runtime (FastEmbed) utilising CPU AVX2 instructions.
   - Vector Store: `LanceDB` (serverless, disk-based vector storage) or
     `sqlite-vec` (SQLite vector search extension).
   - Search Architecture: Hybrid Two-Tower neural search combined with Best
     Matching 25 (BM25) keyword search for deterministic legal term matching.
4. **Local Large Language Model (LLM) Inference:**
   - Inference Engine: `llama.cpp` server or `Ollama` daemon.
   - Primary Models: Quantized (Q4_K_M / Q5_K_M) 4-bit models:
     - `Llama-3.2-3B-Instruct`: Fast daily summaries and matter triage.
     - `Qwen-2.5-7B-Instruct`: Complex document analysis and reasoning.
     - `Whisper-small` / `Whisper-base`: Local audio dictation transcription.
5. **Application Layer & User Interface:**
   - Backend API: Python `FastAPI` serving local Hypertext Transfer Protocol
     (HTTP) endpoints.
   - Frontend UI: Single-page responsive web dashboard (vanilla ES6 JavaScript,
     HTML5, and CSS3) accessible across local office browser at
     `http://practice-vault.local:8080`.

---

## 4. Security, Governance & Privilege Protection

1. **Physical Air-Gap Capability:** The system operates autonomously on the
   local office Local Area Network (LAN) without requiring an outbound internet
   connection for processing.
2. **Read-Only Data Access:** Client documents are mounted via read-only Server
   Message Block (SMB) network shares, ensuring the appliance physically
   cannot modify or delete master practice files.
3. **Legal Privilege Guarantee:** Zero client or patient records are
   transmitted outside the physical walls of the practice, preserving legal
   professional privilege and medical confidentiality under the UK Data
   Protection Act 2018.

---

## 5. Implementation Blueprint & AI Build Instructions

### 5.1. Overview & Build Objectives
This section serves as an operational instruction manual for an AI coding
agent (or human systems engineer) implementing the prototype on a dedicated
Lenovo ThinkCentre M720q Tiny (or equivalent Linux mini-personal computer).
The objective is to produce a fully functioning, self-contained prototype
within a single working session, adhering to the Zero Operational Disruption
architecture.

### 5.2. Target System Directory Structure
The prototype application codebase shall reside in `/opt/practice-vault/` (or
the developer's local user directory during prototyping) with the following
layout:

```
practice-vault/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py             # System paths, model names, port bindings
│   │   ├── ingest.py             # File parsers (PDF, DOCX, XLSX, MSG/PST)
│   │   ├── indexer.py            # LanceDB vector store and BM25 indexer
│   │   ├── rag.py                # FastEmbed and Ollama RAG query engine
│   │   ├── triage.py             # Autonomous inbox triage & task extractor
│   │   └── api.py                # FastAPI endpoints for search and clerk
│   ├── main.py                   # Uvicorn entrypoint (binds to 127.0.0.1:8080)
│   ├── requirements.txt          # Python package manifest with pinned vers
│   └── tests/
│       ├── test_ingest.py        # Ingestion test suite
│       ├── test_indexer.py       # Vector storage and retrieval tests
│       └── test_rag.py           # End-to-end question answering tests
├── frontend/
│   ├── index.html                # Sovereign single-page web dashboard
│   ├── css/
│   │   └── dashboard.css         # Modern, understated practice styling
│   └── js/
│       └── app.js                # Search, task list, and triage interface
├── scripts/
│   ├── setup_m720q.sh            # Automated OS package and model installer
│   ├── mount_shares.sh           # Safe read-only CIFS/SMB share mounting
│   ├── start_vault.sh            # Production process runner and watchdog
│   └── verify_prototype.py       # Automated smoke test verifying all layers
├── data/
│   ├── sample_docs/              # Mock legal, medical, and financial files
│   ├── lancedb/                  # Local on-disk vector database files
│   └── inbox_staging/            # Incoming mock emails and attachments
└── README.md                     # Operational runbook and usage instructions
```

### 5.3. System Prerequisites & Setup Script
The prototype setup script (`scripts/setup_m720q.sh`) automates host operating
system configuration on Debian 13 (Trixie) and Ubuntu 24.04 LTS:

1. **System Packages:**
   Install required system packages, including compiler toolchains, Optical
   Character Recognition (OCR) engines, and Server Message Block (SMB) client
   utilities:
   ```bash
   sudo apt-get update
   sudo apt-get install -y \
     python3-pip python3-venv \
     tesseract-ocr tesseract-ocr-eng \
     cifs-utils poppler-utils curl git
   ```

2. **Ollama LLM Engine:**
   Install Ollama and pull the recommended 4-bit quantized Small Language
   Models (SLMs):
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2:3b-instruct-q4_K_M
   ollama pull nomic-embed-text
   ```

3. **Python Virtual Environment & Dependencies:**
   Create an isolated environment and install the verified Python manifest:
   ```bash
   python3 -m venv /opt/practice-vault/venv
   source /opt/practice-vault/venv/bin/activate
   pip install --upgrade pip
   pip install \
     fastapi==0.115.0 \
     uvicorn==0.31.0 \
     lancedb==0.13.0 \
     fastembed==0.3.6 \
     pypdf==5.0.0 \
     pdfplumber==0.11.4 \
     python-docx==1.1.2 \
     openpyxl==3.1.5 \
     rank-bm25==0.2.2 \
     pydantic==2.9.2 \
     httpx==0.27.2 \
     pytest==8.3.3
   ```

### 5.4. Phased Implementation Milestones
The building AI agent should implement and verify the system in five strict,
sequential milestones:

#### Milestone 1: Hardware & Inference Sanity Verification
1. Verify CPU Advanced Vector Extensions 2 (AVX2) instructions:
   `grep -o 'avx2' /proc/cpuinfo | head -n 1`.
2. Confirm Ollama daemon responds to local Hypertext Transfer Protocol (HTTP)
   requests on port 11434.
3. Execute a smoke script validating that `llama3.2:3b-instruct-q4_K_M` delivers
   local inference at greater than 10 tokens per second while consuming under
   3.0 Gigabytes (GB) of Random Access Memory (RAM).

#### Milestone 2: Document Ingestion Pipeline
File: `backend/app/ingest.py`
1. Implement pure-Python extractors for Portable Document Format (PDF),
   Microsoft Word (.docx), Microsoft Excel (.xlsx), and plain text.
2. Implement recursive folder traversal scanning specified directories.
3. For scanned PDFs containing image-only pages, trigger local Tesseract OCR
   as a graceful fallback.
4. Implement semantic text chunking (500 tokens per chunk with 50-token
   overlap) preserving source document metadata (file path, modification date,
   page number, and detected section heading).

#### Milestone 3: Vector Indexing & Hybrid Search
File: `backend/app/indexer.py`
1. Integrate `fastembed` with `bge-small-en-v1.5` for local CPU embedding
   vectorisation.
2. Initialise a persistent on-disk LanceDB table storing embedding vectors and
   chunk metadata.
3. Initialise an in-memory Best Matching 25 (BM25) index for exact keyword
   matching (crucial for exact case references, patient IDs, or statute codes).
4. Implement reciprocal rank fusion (RRF) combining vector similarity scores
   with BM25 lexical scores to deliver high-precision hybrid search results.

#### Milestone 4: Retrieval-Augmented Generation & Practice Clerk
Files: `backend/app/rag.py` and `backend/app/triage.py`
1. **Deterministic Q&A Engine:** Given a natural language query, retrieve the
   top 5 relevant chunks, construct a strict citation prompt, and query the
   local 3B model via Ollama. Enforce mandatory document citations: if the
   evidence is absent from the provided context, the model must explicitly state
   that the information is not found in practice records.
2. **Autonomous Inbox & Task Triage:** Given incoming email text or document
   memoranda, prompt the local model to extract structured JSON containing:
   - Priority categorisation (Urgent, Routine, Low).
   - Actionable tasks with inferred due dates.
   - Identified entities (client name, matter reference, monetary sums).
   - Pre-drafted polite reply staged for partner approval.

#### Milestone 5: Web Dashboard & Local Application Programming Interface (API)
Files: `backend/main.py` and `frontend/`
1. Implement FastAPI endpoints:
   - `GET /api/status`: Health check, indexed document count, and memory usage.
   - `POST /api/search`: Hybrid search returning ranked snippets and citations.
   - `POST /api/query`: Full Retrieval-Augmented Generation (RAG) question
     answering with source attribution.
   - `GET /api/tasks`: Active task list grouped by matter and urgency.
   - `POST /api/triage`: Manual or automated document/email intake processing.
2. Build an elegant, lightweight single-page web dashboard using vanilla ES6
   JavaScript and semantic HTML5:
   - Search bar with live deterministic citations and file links.
   - Practice Clerk tab displaying pending action items and draft replies.
   - Practice Overview tab displaying indexed document volumes and status.
   - Clean, professional aesthetic suitable for senior partners and KCs.

### 5.5. Copy-Paste Master Build Prompt for AI Coding Agent
To instruct another AI coding agent (e.g. running in an isolated shell on the
ThinkCentre M720q) to build the complete prototype, supply the following prompt:

```text
You are an expert systems engineer tasked with implementing the sovereign
practice automation prototype described in docs/PRODUCT_SPECIFICATION.md on
this Lenovo ThinkCentre M720q (Intel i3-9100T, 16GB RAM, Debian 13 Trixie).

Follow these binding engineering instructions:
1. Adhere strictly to British Professional English for all code comments,
   User Interface (UI) strings, docstrings, and documentation.
2. Execute the phased milestones in order:
   - Step 1: Run scripts/setup_m720q.sh (or execute equivalent commands) to
     verify Ollama, install Python dependencies, and download 3B models.
   - Step 2: Implement backend/app/ingest.py to parse PDF, DOCX, XLSX, and TXT
     files with chunking (500 tokens, 50-token overlap) and metadata.
   - Step 3: Implement backend/app/indexer.py using FastEmbed and LanceDB,
     supplemented with BM25 hybrid ranking.
   - Step 4: Implement backend/app/rag.py and backend/app/triage.py for
     deterministic question answering with exact citations and structured
     task extraction.
   - Step 5: Implement backend/app/api.py and backend/main.py with FastAPI,
     serving the static single-page dashboard from frontend/.
3. Ensure the entire system runs locally on port 8080 without external cloud
   dependencies.
4. Create sample test documents in data/sample_docs/ representing a boutique
   legal, medical, or accounting practice.
5. Provide automated test verification in backend/tests/ proving that:
   - Document chunks are indexed into LanceDB.
   - Hybrid search returns accurate citations.
   - The RAG endpoint answers questions with precise source attribution.
   - Memory usage remains strictly below 4.0 GB RAM under load.
Proceed step-by-step, verifying each component as you build.
```

### 5.6. Verification & Acceptance Criteria
The prototype is considered complete and accepted when the automated test
script (`python3 scripts/verify_prototype.py`) demonstrates:
1. **Cold Start & Resource Budget:** System boots in under ten seconds and
   idles at less than 1.5 GB RAM total memory consumption.
2. **Deterministic Ingestion:** Parses and indexes a test batch of 50 complex
   PDF, DOCX, and XLSX documents in under two minutes using CPU AVX2.
3. **Exact Citations:** 100% of generated answers cite the specific document
   filename and page number from which the factual answer was derived.
4. **Zero Cloud Leakage:** All network calls remain on 127.0.0.1 and local
   subnet; zero outbound public internet packets are transmitted during search
   or inference.
5. **Human-in-the-Loop Safeguard:** Triage engine stages draft communications
   in an approval queue; no automated outbound communication is transmitted.
