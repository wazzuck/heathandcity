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
1. **Operating System:** Linux (Ubuntu 24.04 LTS Server or Debian 12),
   configured for headless, silent execution.
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
