# Commercial Sale, Regulatory Governance, and Licensing Compliance Guide

> Practice Vault Commercial Distribution and Regulatory Assurance Specification.
> Applicable to Heath & City Technology commercial deployments for private
> medical practices, King's Counsel (KC) chambers, solicitors, and family
> offices.
> Status: Binding Regulatory Assurance Document.

---

## 1. Executive Summary

Practice Vault is engineered as an on-premises, sovereign cognitive appliance.
When sold or leased to commercial clients—such as private medical consultants,
law firms, and boutique practices—the appliance must satisfy strict United
Kingdom (UK) statutory requirements, regulatory professional codes of conduct,
and commercial intellectual property constraints.

This document records the legal and regulatory compliance architecture of the
system, establishing that:
1. All software components are free from copyleft contamination and are
   commercially distributable under proprietary terms.
2. The system operates strictly within UK General Data Protection Regulation
   (UK GDPR) and Data Protection Act 2018 parameters.
3. Legal Professional Privilege (LPP) is preserved under Solicitors Regulation
   Authority (SRA) and Bar Standards Board (BSB) rules.
4. National Health Service (NHS) Caldicott Principles, the Data Security and
   Protection Toolkit (DSPT), and the Digital Technology Assessment Criteria
   (DTAC) are satisfied for clinical workflows.
5. Audio dictation and multi-party transcription comply with the Investigatory
   Powers Act 2016.

---

## 2. Commercial Open-Source Licensing Audit

To distribute Practice Vault as a proprietary commercial solution without
statutory obligations to publish source code, all dependencies must utilise
permissive open-source licences.

### 2.1 Audited Dependencies and Licences

The complete environment contains 65 packages, all verified permissive:
- **MIT Licence**: FastAPI, Starlette, Pydantic, AnyIO, Uvicorn, LanceDB,
  Sentence-Transformers, PyYAML, Python-Dateutil, Requests, TQDM, Pytest.
- **Apache Licence 2.0**: PyArrow, LXML, Jinja2, Multipart, Google API Client,
  Google Auth, NumPy, Packaging.
- **BSD 2-Clause / 3-Clause**: Faster-Whisper, PyAV, CTranslate2, Click,
  MarkupSafe, Werkzeug, IDNA, Cryptography.
- **ISC Licence**: Certain underlying platform utility libraries.

### 2.2 Copyleft and Contamination Guarantee

- **Zero General Public Licence (GPL)**: No direct or transitive component is
  governed by GPL version 2 or version 3.
- **Zero Affero General Public Licence (AGPL)**: No network-triggered copyleft
  components exist within the appliance stack.
- **Commercial Freedom**: Heath & City Technology retains full intellectual
  property ownership of its custom application code, embeddings pipelines, and
  specialised user interfaces. The system can be sold as a turnkey hardware
  appliance or licensed software package without licensing restriction.

---

## 3. Data Protection and UK GDPR Compliance

### 3.1 Data Controller vs Data Processor Status

When deployed for a client:
- **Client as Data Controller**: The client (e.g. chambers, law firm, or
  private clinic) remains the sole Data Controller under Article 4(7) of the
  UK GDPR. They determine the purposes and means of processing client records.
- **Appliance as Local Tool**: Because Practice Vault operates entirely within
  the client's local premises and infrastructure without transmitting data
  to Heath & City Technology, Heath & City Technology is neither a Data
  Processor nor a recipient of personal data during routine operation.

### 3.2 100% On-Premises Sovereignty

- **Loopback Binding**: The backend web service binds strictly to `127.0.0.1`
  (loopback). It cannot be reached across unauthenticated local area networks
  or the public internet without an intentional reverse proxy.
- **Zero Cloud Leakage**: No telemetry, analytics, embeddings queries, or
  generative prompts leave the host machine. All Large Language Model (LLM)
  inference is performed locally by Ollama running open-weight weights
  (`qwen3.5:4b` or `qwen2.5:3b`) on local CPU or GPU hardware.
- **Externalised Data Directories**: Client data, indices, vector tables, and
  extracted plain text reside in a dedicated path
  (`/home/neville/practice-vault-data/`) isolated entirely from Git source
  control, preventing accidental commits or upstream remote leakage.

---

## 4. Legal Professional Privilege (LPP) and Confidentiality

Confidentiality is an absolute professional duty under SRA Principle 2 and BSB
Core Duty 6. Legal Professional Privilege encompasses both Legal Advice
Privilege (LAP) and Litigation Privilege (LP).

### 4.1 Threat from Third-Party Cloud AI

Transmitting unredacted client instructions, witness statements, or counsel
opinions to commercial third-party cloud Application Programming Interfaces
(APIs)—such as OpenAI, Anthropic, or Google Cloud—creates severe legal risks:
1. Potential waiver of privilege if confidentiality is compromised under
   unilateral provider terms of service.
2. Cross-border data transfers violating Chapter V of the UK GDPR.
3. Retention of client secrets in external server logs or retraining corpora.

### 4.2 Practice Vault Immunity

Practice Vault eliminates these risks:
- Complete physical containment ensures client privilege is never waived.
- Deterministic cross-encoder re-ranking and explicit zero-hallucination
  refusal gates guarantee that if a matter is unrecorded, the model returns an
  explicit refusal rather than fabricating advice.
- Direct statutory, contract, or email citations accompany every synthesized
  finding, providing an unbroken audit trail for court submission.

---

## 5. NHS Caldicott Principles and Clinical Information Governance

For medical practices, independent consulting doctors, and surgical suites,
Practice Vault conforms to the eight Caldicott Principles:

1. **Principle 1 (Justify the purpose)**: Data indexing is restricted to
   direct practice management, clinical scheduling, and fee reconciliation.
2. **Principle 2 (Use confidential information only when necessary)**: Only
   documents explicitly placed within the vault directory are indexed.
3. **Principle 3 (Use the minimum necessary)**: Retrieval-Augmented Generation
   (RAG) extracts only relevant text passages (chunks) for a query.
4. **Principle 4 (Strict access control)**: Local filesystem permissions
   govern access to the underlying SQLite and LanceDB vector stores.
5. **Principle 5 (Duty of awareness)**: System audit logs record all search,
   synthesis, and document indexing operations.
6. **Principle 6 (Understand and comply with the law)**: Zero cross-border
   data movement ensures adherence to the Data Protection Act 2018.
7. **Principle 7 (Duty to share for care)**: Clinical summaries and attendance
   notes can be exported locally for multidisciplinary team consultations.
8. **Principle 8 (Inform patients of choices)**: Clear audit trails support
   Subject Access Requests (SARs) and patient transparency.

---

## 6. Audio Dictation, Call Recording, and Interception Law

Practice Vault includes an audio dictation and multi-speaker transcription
engine powered by Faster-Whisper and acoustic feature clustering.

### 6.1 Investigatory Powers Act 2016

Section 3 of the Investigatory Powers Act 2016 prohibits intentional
interception of telecommunications without lawful authority or consent:
- **Explicit Consent**: Where calls or multi-party conferences are recorded,
  all participants must give explicit informed consent prior to recording.
- **Statutory Notice**: The Practice Vault user interface displays a prominent
  consent warning:
  *"Statutory Notice: Under the Investigatory Powers Act 2016, recording
  third-party communications requires explicit participant consent."*
- **Telecommunications Regulations 2000**: For business practices recording
  client instructions to establish facts or ensure regulatory compliance,
  all reasonable efforts must be made to inform callers in advance.

### 6.2 Attendance Note Synthesis

Transcribed speech turns can be labelled with identified speaker roles
(e.g. "William McAdam (Counsel)" or "Dr Julian Ross (Consultant Surgeon)").
The generated attendance note is stamped with:
- Date, time, and session duration.
- Key discussion points and agreed actions.
- Explicit participant roster.
- Statutory confidentiality notice.

---

## 7. Automated Continuous Verification

Compliance is not treated as an afterthought; it is enforced programmatically
via an automated verification gate:
```bash
python3 scripts/verify_legal_compliance.py
```
This script audits:
1. Every installed Python distribution against a copyleft exclusion filter.
2. Configuration files for loopback binding and data directory separation.
3. RAG engine source files for refusal guards and citation enforcement.
4. Compliance documentation and statutory consent disclosures.

Passing this gate is a mandatory prerequisite for any release, deployment, or
commercial client hand-over.
