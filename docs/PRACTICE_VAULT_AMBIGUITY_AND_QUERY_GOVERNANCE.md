# Practice Vault: Ambiguity Resolution & Query Governance

Status: Living Document  
Date: November 2026  
Audience: Senior Partners, Practice Managers, Information Officers  
Scope: Natural Language Ambiguity, Homonym Collisions, Version Conflicts,  
       Presupposition Refutation, and Retrieval-Augmented Generation (RAG)

---

## 1. Executive Summary

When legal counsel, King's Counsel (KC), medical consultants, or practice
principals query private practice archives through Small Language Models
(SLMs), inquiries frequently exhibit semantic ambiguity. Unlike public web
search, where inexact phrasing returns generic pages, private practice queries
carry severe liability implications. A system that answers an under-specified
question by arbitrarily guessing a single agreement, or that tacitly accepts a
false premise embedded in a partner's question, risks professional negligence.

This document catalogues the five primary failure modes of natural language
query ambiguity observed in practice vaults, presents empirical evaluation
results across local reasoning models (`phi4-mini:latest` and `qwen3.5:4b`),
and specifies the governance architecture implemented within the Heath & City
Practice Vault core engine.

---

## 2. Taxonomy of Practice Query Ambiguity

Through exhaustive stress testing against sovereign practice records, five
distinct categories of query ambiguity were identified:

```
+--------------------------------------------------------------------------+
|                  PRACTICE QUERY AMBIGUITY TAXONOMY                       |
+--------------------------------------------------------------------------+
| 1. Under-specified Reference    | "What is the fee in the agreement?"    |
|    (Multiple active agreements) | Risk: Arbitrary selection of one matter|
+---------------------------------+----------------------------------------+
| 2. False Presupposition Trap    | "Why did McAdam reject the settlement?"|
|    (Contradicted premise)       | Risk: Hallucinating fabricated reasons |
+---------------------------------+----------------------------------------+
| 3. Chronological Conflict       | "What is the hourly fee rate?"         |
|    (Superseded contract terms)  | Risk: Citing outdated historical rate  |
+---------------------------------+----------------------------------------+
| 4. Homonym / Name Collision     | "What did Michael confirm?"            |
|    (Multiple distinct entities) | Risk: Conflating separate actors/sums  |
+---------------------------------+----------------------------------------+
| 5. Partial Keyword Overlap      | "What patent royalty in Zurich?"       |
|    (Out-of-domain scope probe)  | Risk: Extrapolating unsupported terms  |
+--------------------------------------------------------------------------+
```

### 2.1 Under-specified Document Reference
A client or fee-earner inquires about "the contract", "the agreement", or
"the invoice" when the archive contains multiple distinct commercial
instruments across separate matters.
- **Defect Pattern:** The model arbitrarily selects whichever document
  ranked highest in vector similarity, concealing the existence of other
  agreements from counsel.
- **Required Behaviour:** The model must identify every distinct instrument
  and enumerate each matter separately with its respective citations.

### 2.2 False Presupposition Trap
An inquiry embeds an inaccurate or unproven factual assertion within its
premise (for example, "Why did X reject the settlement?", when contemporaneous
correspondence confirms X accepted and executed the settlement).
- **Defect Pattern:** The language model assumes the user's premise is valid
  and hallucinates speculative reasons or justifications.
- **Required Behaviour:** The model must identify the contradiction,
  explicitly refute the false presupposition, and cite the factual record.

### 2.3 Chronological Version Conflict
A fee structure, engagement retainer, or practice policy has been amended
across successive years (for example, a 2023 hourly fee schedule superseded
by a 2025 schedule).
- **Defect Pattern:** The model quotes the historical rate without noting that
  it has been superseded, or merges terms from different versions.
- **Required Behaviour:** The model must delineate the terms chronologically
  and explicitly declare the latest effective position.

### 2.4 Homonym and Name Collision
A query refers to an individual by first name or common surname where multiple
parties exist in practice records (for example, Michael Davies, underwriter,
versus Michael Bryce, property transfer agent).
- **Defect Pattern:** The model conflates the two individuals or reports only
  one transaction whilst omitting the second.
- **Required Behaviour:** The model must isolate both entities, specify their
  full names and institutional roles, and present both records clearly.

### 2.5 Partial Keyword Overlap and Out-of-Domain Guards
A query contains an authentic entity name (for example, William McAdam)
combined with fictitious or unrecorded terms (for example, a patent licence in
Zurich).
- **Defect Pattern:** The model attempts to synthesise an answer from adjacent
  context or hallucinates Swiss legal arrangements.
- **Required Behaviour:** The model must explicitly state that no record exists
  regarding the unverified terms, whilst confirming the verified factual
  matters on record.

---

## 3. Empirical Model Evaluation Matrix

We conducted rigorous automated trials using the evaluation harness in
`practice-vault/scripts/test_ambiguity_scenarios.py` on the on-premises
sovereign appliance (Intel Core i3-9100T, 15.5 GiB Random Access Memory (RAM)).

Trials evaluated two leading compact SLMs under two prompting regimes:
1. **Baseline Prompt:** Standard institutional attribution instructions.
2. **Enhanced Ambiguity-Aware Prompt:** Multi-directive governance framework
   enforcing enumeration of multiple matters, chronological tracking, and
   presupposition refutation.

### 3.1 Comparative Benchmark Results

| Scenario & Evaluated Model | Baseline Outcome | Enhanced Outcome |
| :--- | :--- | :--- |
| **1. Under-specified Reference** | | |
| - `phi4-mini:latest` | Refusal ("no record") | Refusal ("no record") |
| - `qwen3.5:4b` | Merged 2 fee quotes | Delineated 2 matters |
| **2. False Presupposition** | | |
| - `phi4-mini:latest` | Refusal ("no record") | Refusal ("no record") |
| - `qwen3.5:4b` | Refusal ("no record") | Refuted false premise |
| **3. Chronological Conflict** | | |
| - `phi4-mini:latest` | Refusal ("no record") | Refusal ("no record") |
| - `qwen3.5:4b` | Quoted both rates | Delineated rates + latest |
| **4. Homonym Collision** | | |
| - `phi4-mini:latest` | Omitted 2nd person | Extracted both records |
| - `qwen3.5:4b` | Extracted both | Delineated Matter A and B |
| **5. Partial Keyword Guard** | | |
| - `phi4-mini:latest` | Refusal ("no record") | Refusal ("no record") |
| - `qwen3.5:4b` | Refusal ("no record") | Refused fiction, kept facts |

### 3.2 Key Findings & Model Characteristics
1. **`phi4-mini:latest` Guardrail Sensitivity:** Microsoft Phi-4 Mini displays
   an exceptionally strict safety filter. When document headings or query terms
   do not align with near-verbatim lexical exactness, it defaults to a clean
   refusal ("The practice archive contains no record of this information").
   Whilst this guarantees zero hallucination, it can result in false-negative
   refusals on under-specified queries.
2. **`qwen3.5:4b` Semantic Disambiguation Superiority:** Alibaba Qwen 3.5 4B
   demonstrated world-class governance compliance under the enhanced prompt:
   - Accurately dissected multiple agreements into distinct numbered matters.
   - Articulated explicit logical refutations against false presuppositions.
   - Identified the superseded historical rate and computed the "Latest
     Effective Position".
   - Disambiguated homonyms with institutional clarity.

---

## 4. Production Implementation

To permanently institutionalise these protections across the appliance, the
following architectural enhancements were integrated into the core engine:

### 4.1 Enhanced Institutional System Prompt
The production Retrieval-Augmented Generation (RAG) module in
`practice-vault/backend/app/rag.py` has been updated with five binding
governance directives:

1. **Citation Discipline:** Mandatory document and page citations formatted
   as `[Document.pdf \| Page: 1]`.
2. **Multiple Matters Enumeration:** Mandatory separation and labelling of
   distinct legal or financial instruments.
3. **Chronology & Superseded Terms:** Explicit ordering of historical terms
   and declaration of current standing.
4. **Presupposition Verification:** Pre-emptive refutation of contradictory
   assumptions embedded in partner questions.
5. **Zero-Extrapolation Refusal:** Strict fallback to verbatim institutional
   refusal when facts are absent.

### 4.2 Dynamic Reference Date Injection
All prompts now dynamically inject the sovereign Central Processing Unit (CPU)
wall-clock reference date:
```text
Reference Date: 11 November 2026
```
This enables local models to evaluate temporal concepts ("last year",
"recent update", "effective as of current date") without reliance on external
network synchronisation.

### 4.3 High-Throughput Memory Optimisation
To prevent event loop contention during continuous background ingestion sweeps,
the statistics engine was upgraded:
- Replaced 54,000-chunk in-memory Python deserialisation with direct SQLite
  Full-Text Search (FTS5) aggregate calculations (reducing startup latency
  from 45 seconds to 0.05 seconds).
- Background document detection and vector indexing routines now run inside
  worker threads (`asyncio.to_thread`), ensuring uninterrupted Hypertext
  Transfer Protocol (HTTP) responsiveness.

---

## 5. Ongoing Monitoring & Continuous Ingestion

The continuous ingestion daemon (`continuous_indexer.py`) and post-indexing
orchestrator (`run_post_index_evaluation.py`) remain active on the host:
- Current corpus scale: **54,984 indexed chunks** across **54,698 Gmail
  messages** and **268 Google Docs** (22.5 million verified words).
- Transaction ledger: **1,995 itemised financial records** (£2,003,593.53)
  resolving in 0.02 seconds.
- All correspondence remains strictly confined to external local storage
  at `/home/neville/practice-vault-data/` outside Git revision control.
