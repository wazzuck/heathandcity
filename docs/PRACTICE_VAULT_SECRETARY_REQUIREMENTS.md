# Practice Vault Personal Secretary: Requirements and Simulation
# Specification

> Status: proposed; awaiting operator approval.
> Date: 2026-11-13.
> Companion to `docs/PRACTICE_VAULT_SECRETARY_FEASIBILITY_HANDOVER.md`.
> Language: British Professional English (AGENTS.md Policy 15).
> Line width: 80 columns.

---

## 1. Purpose and scope

1. This document converts the feasibility handover into a buildable,
   testable requirement set for a personal secretary running on the
   on-premises Practice Vault appliance.
2. It exists so that several agents can work in parallel without sharing
   files, and so that every claim about the secretary can be checked by
   simulation rather than by opinion.
3. The secretary is a deterministic practice system with a language
   model at the edges. It is not a chat interface bolted onto a search
   box.

### 1.1. What "simulation" means in this document

1. A simulation runs the secretary against a frozen snapshot of the
   real Gmail and Google Drive corpus held on this host.
2. Every outbound action is intercepted. No email is sent, no calendar
   event is created, moved or cancelled, and no file is deleted or
   relabelled.
3. Each scenario produces four artefacts: the user-visible answer, the
   execution trace, the sources used, and a pass or fail against a
   stated oracle.
4. A run is reproducible: the same snapshot, scenario and seed produce
   the same result.

### 1.2. Out of scope

1. Sending email without explicit human approval.
2. Deleting, archiving or labelling live Gmail during a simulation.
3. Legal, medical, tax or investment advice.
4. Multi-user access control. This is a single-operator appliance.
5. Mobile clients and voice input.

---

## 2. Actors, data and constraints

### 2.1. Actors

1. **Operator**: the single human user. Senior principal of a boutique
   practice. Approves any externally visible action.
2. **Secretary**: the system in this document. Answers, classifies,
   drafts, proposes and reports.
3. **Simulation harness**: drives scenarios, intercepts actions, records
   traces and scores results.
4. **Background worker**: runs overnight, never interactive.

### 2.2. Corpus facts (measured 2026-11-13)

1. 69,173 chunks in `practice_fts.db`.
2. 58,166 distinct Gmail message identifiers, spanning 2004-09-22 to
   2026-11-11T10:59:39Z.
3. 268 Google Docs; 20 local documents; 26.6 million words.
4. Every Gmail chunk begins with `Subject:`, `From:` and `Date:`
   headers, so message identifier, sender, date and subject can be
   backfilled from the full-text index without calling Google.
5. Recipients, thread identifier, labels, read state and attachment
   metadata are **not** stored and require Gmail metadata calls.
6. At least 41.1 per cent of messages come from plainly automated
   senders: job alerts 12.3 per cent, newsletters 10.4 per cent,
   platform notifications 10.0 per cent, retail receipts 8.4 per cent.
   The remainder, 58.9 per cent, is unclassified.
7. Gmail synchronisation stopped on 2026-11-11T12:37 while Google Docs
   synchronisation continued to 2026-11-13T13:51.

### 2.3. Host constraints

1. Intel Core i3-9100T, four cores, 16 GB RAM, Intel UHD Graphics 630,
   no discrete Graphics Processing Unit (GPU).
2. Local inference: about 47 prompt tokens per second and 10 generated
   tokens per second with Phi-4-mini on four threads.
3. Consequence: five-second answers are reachable only from Structured
   Query Language (SQL) or pre-computed results, never from a model
   reading email text.

### 2.4. Legal and policy constraints

1. Zero copyleft contamination; permissive licences only.
2. United Kingdom (UK) General Data Protection Regulation (GDPR)
   compliance, Legal Professional Privilege, and National Health
   Service (NHS) Caldicott Principles.
3. `scripts/verify_legal_compliance.py` must pass on every change.
4. Every online capability requires an offline counterpart
   (AGENTS.md Policy 16).
5. No message content leaves the host at any point.

---

## 3. Definitions

1. **Message**: one Gmail message, identified by its Gmail identifier.
   A message may occupy several chunks.
2. **Thread**: an ordered set of messages sharing a Gmail thread
   identifier. Not yet available locally.
3. **Matter**: a unit of practice work, for example a conveyance or a
   probate estate. Matters are operator-defined.
4. **Tier A**: answers served from SQL or a pre-computed cache.
5. **Tier B**: answers served from retrieval plus a short model call.
6. **Tier C**: answers served from retrieval plus a long model call.
7. **Dry run**: execution in which every external side effect is
   recorded and suppressed.
8. **Forbidden action**: any send, delete, relabel, or calendar write
   during a dry run.

---

## 4. Functional requirements

Each requirement states the behaviour, the acceptance criterion, and
the simulation group that proves it.

### FR-1. Morning brief

1. On request, produce one screen containing: unread count, messages
   received since the last brief, invitations awaiting a response,
   tasks due today, tasks overdue, and calendar commitments today.
2. Acceptance: every figure is traceable to a SQL query or a stored
   summary; the screen renders in under two seconds at Tier A; no model
   call is made.
3. Simulation group: `brief`.

### FR-2. List, filter and count

1. Understand and answer: "recent", "latest", "unread", "today",
   "this week", "from <person>", "about <matter>", "with attachments",
   "invitations", "between <date> and <date>", and explicit months,
   quarters and years.
2. Results are de-duplicated by message, ordered newest first, and
   labelled by category. A newsletter must never be presented as
   personal correspondence without its label.
3. Acceptance: at least 95 per cent exact agreement with a SQL oracle
   across 40 scenarios; 95th percentile latency at or below two
   seconds; zero model calls on the hot path.
4. Simulation group: `list`.

### FR-3. Classification and prioritisation

1. Assign every message one category: personal, client or matter,
   newsletter, job alert, platform notification, receipt or
   transaction, invitation, or spam and phishing.
2. Prioritise into urgent, routine and low, with a stated reason.
3. Decision order: header and sender rules, then an embedding
   classifier, then the language model for ambiguous cases only.
4. Acceptance: at least 0.90 macro F1 on a hand-labelled set of 500
   messages; newsletter precision at least 0.95; every result records
   which tier decided it and with what confidence.
5. Simulation group: `classify`.

### FR-4. Thread reconstruction

1. Group messages into conversations, newest first, with participants
   and subject normalisation (removing `Re:` and `Fwd:` prefixes).
2. Acceptance: for 20 sampled threads, grouping matches the Gmail
   thread identifier exactly; no message appears in two threads.
3. Simulation group: `threads`.

### FR-5. Invitations and responses

1. Detect meeting invitations, extract organiser, start, end, location,
   attendees and current response status.
2. Check for clashes against the calendar mirror.
3. Propose accept, decline or tentative with a one-line reason, and
   wait for operator approval.
4. Acceptance: correct extraction on 30 sampled invitations; clash
   detection agrees with a manual check on 20 cases; zero writes during
   a dry run.
5. Simulation group: `invitations`.

### FR-6. Calendar reading and clash detection

1. Answer "what is on today", "what is on this week", "when am I free
   for an hour on Thursday", and "does this clash".
2. Acceptance: day and week listings match the local mirror exactly;
   free-slot proposals respect working hours and existing commitments.
3. Simulation group: `calendar-read`.

### FR-7. Calendar writing (decision-gated)

1. Create, move and cancel events, but only after explicit operator
   confirmation and only when a write scope has been approved.
2. **This requirement is blocked** until the operator decides whether
   to break the current read-only OAuth policy. See section 9.
3. Acceptance when unblocked: every write is previewed, confirmed, then
   verified by reading the event back.
4. Simulation group: `calendar-write` (suspended).

### FR-8. Fact finding with citations

1. Answer questions whose evidence lies in messages or documents, for
   example "what did we agree about the completion date".
2. Every factual sentence carries a citation to a message identifier or
   document path. If evidence is insufficient, the secretary says so
   and names what is missing.
3. Acceptance: citation validity at least 0.98; unsupported-claim rate
   at most 0.02 on 30 scenarios; 95th percentile latency at or below
   90 seconds.
4. Simulation group: `facts`.

### FR-9. Multi-turn discussion

1. Maintain context across turns, resolve pronouns against the previous
   turn, and never lose the active matter.
2. Acceptance: 10 scripted three-turn conversations complete without
   topic drift; the third answer remains correctly anchored.
3. Simulation group: `discussion`.

### FR-10. Drafting

1. Draft replies and new messages from retrieved facts, in British
   Professional English, in the operator's register: understated,
   precise, never effusive.
2. The draft must list the sources used and must not introduce a fact
   absent from them.
3. Acceptance: rubric score at least 4 of 5 on 20 drafts across five
   matter types; zero fabricated facts; no draft is sent.
4. Simulation group: `draft`.

### FR-11. Follow-ups and deadlines

1. Detect when a sent message has had no reply for a configurable
   period, and when a message states a deadline.
2. Produce a chase list and a deadline list, each linked to the source
   message.
3. Acceptance: on 20 known cases, recall at least 0.90 and precision at
   least 0.85.
4. Simulation group: `followups`.

### FR-12. Glossary and practice profile

1. Maintain an operator-editable table of terms, definitions,
   synonyms and matter tags, covering legal, medical and property
   vocabulary.
2. Use it for query expansion and prompt context. It may clarify
   language but must never override retrieved evidence.
3. Acceptance: 25 jargon queries improve retrieval hit rate against a
   no-glossary baseline; no glossary entry can introduce a fact.
4. Simulation group: `glossary`.

### FR-13. Matters, tasks and status

1. Maintain matters, tasks, links between tasks and messages, and a
   status for each.
2. Answer "what is the status of <matter>" from a nightly summary in
   under two seconds, and from live data in under 90 seconds.
3. Acceptance: status answers agree with a manual audit on 15 matters;
   every task traces to a source message or is marked manual.
4. Simulation group: `crm`.

### FR-14. Internet look-up with offline persistence

1. Use the internet only on an explicit trigger, for example a named
   statute, a company number, or an unfamiliar term.
2. Persist every result locally with source, retrieval time and a
   confidence note, so the same question is answered offline next time.
3. Acceptance: with the network disabled, every previously researched
   question still answers from the local store; no automatic browsing
   occurs without a trigger.
4. Simulation group: `web`.

### FR-15. Document search and summarisation

1. Find and summarise Google Docs and local documents, and compare two
   versions of a document.
2. Acceptance: retrieval matches a manual list on 20 documents; a
   summary names the document and date and stays within five bullets.
3. Simulation group: `documents`.

### FR-16. Contacts and relationship memory

1. Maintain a record of people, organisations, roles and last contact,
   derived from message headers and corrected by the operator.
2. Answer "who is <person>", "when did we last speak", and "what do we
   know about <organisation>".
3. Acceptance: 20 identity questions answered correctly, with the
   source message cited; operator corrections override inference
   permanently.
4. Simulation group: `contacts`.

### FR-17. Audit, trace and consent

1. Every request records: route chosen, tier, timings, model used,
   tokens consumed, sources returned, and whether an external action
   was proposed.
2. Every proposed external action requires a confirmation token. A dry
   run records the proposal and discards the token.
3. Acceptance: 100 per cent of simulated requests produce a complete
   trace; zero forbidden actions across the entire suite.
4. Simulation group: `audit`.

---

## 5. Non-functional requirements

### NFR-1. Latency tiers

1. Tier A, 95th percentile at or below 2 seconds.
2. Tier B, 95th percentile at or below 90 seconds.
3. Tier C, 95th percentile at or below 180 seconds, streamed.

### NFR-2. Determinism

1. Temperature zero, fixed seed, fixed snapshot.
2. Two runs of the same scenario produce identical classifications and
   identical source sets.

### NFR-3. Privacy

1. No content, prompt or embedding leaves the host.
2. Logs record identifiers and lengths, never bodies.

### NFR-4. Safety

1. Dry run is the default. External writes require both a flag and a
   confirmation token.
2. A failed confirmation aborts the action and records it.

### NFR-5. Offline first

1. Tier A and Tier B work with the network disabled.
2. Cached web results are dated and re-checked only on request.

### NFR-6. Resumability

1. The background worker checkpoints after every batch and resumes
   without duplicating work.

### NFR-7. Observability

1. One trace record per request, in a single append-only store.
2. A daily summary of routes, timings and failures.

### NFR-8. Legal

1. `scripts/verify_legal_compliance.py` passes.
2. No copyleft dependency is introduced.

### NFR-9. Documentation

1. Every new module carries a file header and step-by-step embedded
   documentation at 80 columns, per AGENTS.md Policy 13.

### NFR-10. Compatibility

1. The existing `./vault` command-line interface and dashboard continue
   to work throughout.

---

## 6. Data contracts

### 6.1. `messages` table

1. Columns: `message_id` (primary key), `thread_id`, `date_utc`,
   `sender_name`, `sender_address`, `recipients`, `subject`, `labels`,
   `category`, `category_confidence`, `category_source`,
   `has_invitation`, `duplicate_of`, `first_seen_utc`.
2. Backfill from the full-text index supplies `message_id`,
   `date_utc`, `sender_address`, `sender_name` and `subject`.
3. Gmail metadata calls supply `thread_id`, `recipients`, `labels` and
   read state.
4. `duplicate_of` is set only when two rows share a normalised subject,
   sender and date within 48 hours.

### 6.2. Calendar mirror

1. Existing `calendar_events.db` is the read model.
2. A separate `calendar_sandbox.db` is used for simulations. The two
   must never be the same file.

### 6.3. Matters and tasks

1. Tables: `matters`, `tasks`, `task_message_links`, `matter_summaries`.
2. `matter_summaries` is written only by the nightly worker and carries
   a generation timestamp.

### 6.4. Glossary

1. Table: `glossary(term, definition, synonyms, matter_tags,
   updated_utc)`.
2. Operator edits win over inferred entries.

### 6.5. Trace

1. One JavaScript Object Notation (JSON) line per request:
   `request_id`, `timestamp`, `prompt`, `route`, `tier`, `timings`,
   `model`, `tokens_in`, `tokens_out`, `sources`, `action_proposed`,
   `outcome`.

---

## 7. Simulation protocol

### 7.1. Snapshot

1. Copy the full-text index, the calendar mirror and the statistics
   file into a read-only directory with a manifest and checksum.
2. The harness records the manifest hash in every result file.
3. Simulations never write to the live data directory.

### 7.2. Scenario format

1. One YAML file per scenario group under `simulation/scenarios/`.
2. Fields: `id`, `capability`, `prompt`, `setup`, `oracle`,
   `expected_path`, `timeout_seconds`, `forbidden_actions`.
3. Oracle types: `sql_order`, `exact_set`, `golden_label`,
   `rubric`, `citation_check`, `manual_audit`.

### 7.3. Ground truth

1. List queries: an independent SQL query written by the harness, not
   by the code under test.
2. Classification: 500 messages labelled by hand, stratified by
   category and year, stored as a versioned file.
3. Drafts: a five-point rubric applied blind by a reviewer model and
   spot-checked by the operator.
4. Facts: citation validity and unsupported-claim counting.

### 7.4. Metrics

1. Correctness, path accuracy, latency at the 50th and 95th
   percentiles, tokens and cost, refusal correctness, citation
   validity, and forbidden-action count.

### 7.5. Gates

1. G1: zero forbidden actions.
2. G2: Tier A at or below 2 seconds, Tier B at or below 90 seconds,
   Tier C at or below 180 seconds, all at the 95th percentile.
3. G3: list correctness at least 0.95.
4. G4: classification macro F1 at least 0.90.
5. G5: citation validity at least 0.98.
6. G6: draft rubric at least 4 of 5 with zero fabricated facts.
7. G7: offline run passes every Tier A and Tier B scenario.

### 7.6. Artefacts

1. `simulation/results/summary.md`: gate table and headline numbers.
2. `simulation/results/results.json`: one record per run.
3. `simulation/results/transcripts/`: the answers as the operator would
   see them.
4. `simulation/results/failures.md`: every failure with a reproduction
   command.

---

## 8. Work packages and file ownership

Each package names one writer. Shared files have a single owner: the
integrator.

| Package | Owner | Gate |
| :--- | :--- | :--- |
| WP-0 Snapshot and harness | A | G1, G7 |
| WP-1 Message store | A | FR-2 |
| WP-2 Query router | B | FR-2, G3 |
| WP-3 Classifier | B | FR-3, G4 |
| WP-4 Calendar and invitations | C | FR-5, FR-6 |
| WP-5 Matters and tasks | C | FR-13 |
| WP-6 Glossary, contacts, documents | Bulk | FR-12, FR-15, FR-16 |
| WP-7 Integration | Integrator | all |
| WP-8 Audit and review | Reviewer | FR-17 |

Files owned:

1. WP-0: `simulation/`.
2. WP-1: `message_store.py`, `backfill_messages.py`.
3. WP-2: `query_router.py`, `temporal_filter.py`.
4. WP-3: `classifier.py`, `triage.py`.
5. WP-4: `calendar_engine.py`, `invitations.py`.
6. WP-5: `crm.py`.
7. WP-6: `glossary.py`, `contacts.py`, `documents.py`.
8. WP-7: `rag.py`, `api.py`, `config.py`.
9. WP-8: `docs/`, review notes.

Rules:

1. A package may create new files freely and may modify only the files
   it owns.
2. A package that needs a change in a shared file writes a patch note
   instead of editing it.
3. The integrator applies patch notes in one pass, after the lanes have
   finished.
4. Tests live beside the module they test and are owned by the same
   package.

---

## 9. Open decisions for the operator

1. **Calendar write scope.** Reading is available today; writing is
   not. Granting it breaks the read-only OAuth policy and needs a fresh
   consent. Decide before FR-7 can be built.
2. **Sending.** Should the secretary ever send without approval, for
   example routine acknowledgements? This document assumes no.
3. **Retention.** How long should drafted replies and traces be kept?
4. **Matter taxonomy.** Which matter types should seed the system?
5. **Label policy.** May the secretary apply Gmail labels, or only
   propose them?

---

## 10. Traceability

| Operator request | Requirement |
| :--- | :--- |
| Recent emails answered correctly | FR-2 |
| Classify emails | FR-3 |
| Invitations and responses | FR-5 |
| Read and edit calendar | FR-6, FR-7 |
| Discuss, find facts, draft | FR-8, FR-9, FR-10 |
| Jargon knowledge base | FR-12 |
| Tasks and status | FR-11, FR-13 |
| Internet when unsure | FR-14 |
| Fast simple answers | FR-1, FR-2, FR-13, NFR-1 |
