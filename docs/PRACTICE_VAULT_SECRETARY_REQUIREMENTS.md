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
8. `transactions.db` holds 2,284 extracted transactions across 290
   merchants, of which 818 are Amazon. Amounts appear in three
   currencies: GBP 2,196, EUR 22, USD 66.
9. No transaction has a negative amount, so refunds are not yet
   represented.
10. Amazon coverage is uneven: no rows in 2019 or 2020, and 35 rows for
    2025 against 182 for 2024. A total presented without this caveat
    would be misleading.
11. At least 217 same-day, same-merchant, same-amount groups exist,
    consistent with an order confirmation and a dispatch notice
    describing one purchase.

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

### FR-18. Spending and quantitative questions

1. Answer questions such as "how much did I spend on Amazon last year",
   "what did I spend with PayPal in the last six months", and "compare
   Amazon spend in 2024 and 2025".
2. Decompose the question into merchant or counterparty, date range,
   currency, inclusions (refunds, shipping, gift cards), and grouping
   (year, month or merchant).
3. If the date range is ambiguous, clarify before computing. "Last
   year" must be resolved to a calendar year, a United Kingdom (UK)
   tax year, or a rolling twelve months. The clarification offers the
   options, states the default, and waits.
4. Run the calculation as deterministic SQL. The model may parse the
   question and phrase the answer; it must not perform arithmetic.
5. Every answer states: the total, the currency, the number of receipts
   counted, the date range used, the coverage caveat, and the largest
   contributing receipts with their message identifiers.
6. Never sum across currencies. Never present a total as complete when
   the archive has gaps.
7. Acceptance: exact agreement with an independent SQL oracle on 20
   queries; a clarification issued on 100 per cent of ambiguous ranges;
   every answer carries a coverage statement; 95th percentile latency
   at or below two seconds after clarification.
8. Simulation group: `spend`.

### FR-19. Clarification protocol

1. Ask a clarifying question when an ambiguity would change the answer
   materially, or when an action is irreversible.
2. Ask at most one question, offering two or three concrete options and
   a stated default. Never ask for information already supplied.
3. Accept "you decide" and apply the default, naming it in the answer.
4. Do not clarify where the request is already unambiguous; a Tier A
   query with an explicit range must answer immediately.
5. Acceptance: no more than one question per turn; zero unnecessary
   clarifications across 20 unambiguous prompts; every clarification
   records the ambiguity it resolved.
6. Simulation group: `clarify`.

### FR-20. Ticket creation

1. Create a ticket from a message, a document, a calendar event, or an
   explicit instruction.
2. Fields: identifier, title, matter, requester, priority, due date,
   status, owner, source link, created time.
3. Deduplicate against open tickets by matter, normalised subject and
   counterparty within 14 days. If a match exists, propose a link
   instead of creating a second ticket.
4. Acceptance: 30 seeded messages create the expected ticket or link;
   a re-run creates no duplicates; every ticket cites a source.
5. Simulation group: `ticket-create`.

### FR-21. Ticket lifecycle

1. States: new, triaged, in progress, waiting on client, waiting on
   third party, blocked, done, cancelled.
2. Transitions are explicit and audited. Closing requires a completion
   note and a link back to the source.
3. Reopening preserves history rather than erasing it.
4. Acceptance: the state machine rejects illegal transitions; 100 per
   cent of transitions are audited; a close without a note is refused.
5. Simulation group: `ticket-lifecycle`.

### FR-22. Ticket queries and portfolio views

1. Answer "what is open", "what is overdue", "what is waiting on me",
   "what did I close this week", "what is the status of <matter>",
   "what is due tomorrow", and "who is blocking".
2. Tier A from SQL, under two seconds.
3. Acceptance: exact agreement on 25 queries; every answer lists
   identifier, title, status and due date.
4. Simulation group: `ticket-query`.

### FR-23. Next-task recommendation

1. Recommend the next task with a deterministic, stored score built
   from deadline proximity, client importance, matter value, age,
   dependency, effort and operator pinning.
2. Show the top three, each with the reason for its position. The
   recommendation must be explainable from stored fields alone.
3. Acceptance: agreement with a manual ranking on 10 scenarios, at
   least 80 per cent for the first choice and 100 per cent containment
   in the top three.
4. Simulation group: `ticket-recommend`.

### FR-24. Ticket hygiene

1. Detect tickets with no activity beyond a threshold, blocked tickets
   whose dependency has cleared, and probable duplicates.
2. Propose an action; never close or merge automatically.
3. Acceptance: 15 known cases, recall at least 0.90 and precision at
   least 0.85.
4. Simulation group: `ticket-hygiene`.

### FR-25. Administrative extraction

1. Extract deadlines, invoices and amounts, renewal dates, travel
   bookings, deliveries, subscriptions, appointments, reference
   numbers and requested actions.
2. Each extraction proposes a ticket or a calendar entry; it never
   makes a silent commitment.
3. Acceptance: 40 seeded messages across eight types, extraction F1 at
   least 0.85; zero tickets created without a source.
4. Simulation group: `admin-extract`.

### FR-26. Routine correspondence

1. Draft acknowledgements, holding replies, chasers, thank-you notes,
   appointment confirmations and document cover notes.
2. Never send. Stage for approval.
3. Acceptance: rubric at least 4 of 5 on 20 drafts; no fabricated
   facts; British Professional English throughout.
4. Simulation group: `draft-admin`.

### FR-27. Meeting preparation

1. One page per meeting: attendees and last contact, open tickets,
   relevant documents, recent messages, and three suggested questions.
2. Acceptance: 10 meetings; every item cites a source; generation
   within 90 seconds.
3. Simulation group: `meeting-prep`.

### FR-28. Weekly review

1. Produce, every Friday or on request: closed, opened, overdue and
   stale tickets, the week ahead, and one recommendation.
2. Acceptance: figures match SQL; under two seconds from cache; names
   the three most at-risk items.
3. Simulation group: `weekly`.

### FR-29. Matter lifecycle

1. Maintain checklists for opening, active, closing and archived
   matters. Checklist items become ticket templates.
2. Acceptance: checklist completeness; no item closes without
   evidence.
3. Simulation group: `matter-lifecycle`.

### FR-30. Risk and compliance flags

1. Flag phishing, suspicious payment requests, complaints, data
   subject requests, regulatory deadlines, possible privilege issues
   and conflict-check names.
2. Flags are advisory, cite the trigger text, and never state a legal
   conclusion.
3. Acceptance: 30 seeded cases, recall at least 0.90, false-positive
   rate at most 0.10; zero automated legal conclusions.
4. Simulation group: `risk-flags`.

### FR-31. Personal administration

1. Maintain reminders for renewals, appointments, travel and personal
   deadlines, linked to their source.
2. Acceptance: 20 prompts, correct date and entity, no duplicate
   reminders.
3. Simulation group: `personal-admin`.

### FR-32. Interactive priority and preemption

1. Every user-facing request holds an interactive lease for its whole
   duration, including streamed responses.
2. While any interactive lease is held, background work must not consume
   Central Processing Unit (CPU) time. Cooperative workers check the
   governor before each batch; registered background processes are paused
   with `SIGSTOP` and resumed with `SIGCONT`.
3. Background work resumes only after an idle grace period, configurable
   and defaulting to three seconds, so a burst of quick questions does not
   thrash the scheduler.
4. A background task interrupted by an interactive request must resume
   from a checkpoint, never from the beginning.
5. Acceptance: no interactive request waits on a background batch; a
   paused worker resumes and completes; no work is lost across a pause.
6. Simulation group: `governor`.

### FR-33. Model roles and orchestration

1. Models are assigned to explicit roles: `interactive` answers the user,
   `background` performs slow classification and summarisation, and
   `orchestrator` resolves an ambiguous request into a capability.
2. The deterministic router runs first. The orchestrator model is used
   only when the router returns `unknown`, and its budget is capped so it
   cannot breach the interactive latency tier.
3. Background models run at low process priority and reduced thread count,
   and never share a server slot with the interactive model.
4. A model may be loaded or unloaded by the governor, but an unload may
   never happen while an interactive lease is held.
5. Acceptance: role assignment is declared in configuration; the
   orchestrator is measurably optional; a background model swap never
   delays an interactive request.
6. Simulation group: `orchestrator`.

### FR-34. Deployment profession pack

1. Each appliance serves exactly one practice and selects exactly one
   profession pack.
2. A pack supplies domain vocabulary, analytical directives, entity
   patterns and representative evaluation questions.
3. Selection is stored on the appliance and takes effect without a
   restart or an environment edit.
4. A known domain term is expanded deterministically, without a model, in
   under 50 milliseconds. An unknown term falls through to retrieval.
5. A pack is data only: it may not change a permission, a route, a
   network call or an outbound action.
6. Acceptance: five of five evaluation prompts return a non-empty answer;
   extraction passes a twenty-message spot check; the verified interaction
   catalogue and the full test suite still pass.
7. Simulation group: `profession`.

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

### NFR-11. Stack review and change mandate

1. Review the technology stack before and after the build against
   measured performance, not fashion.
2. The review covers at least: inference engine and build flags, model
   choice and quantisation, embedding model, reranker, index
   technology, job scheduling, and dependency licences.
3. Every proposed change states the measured baseline, the expected
   gain, the cost, the risk, and the effect on offline operation.
4. A change is adopted only when it passes the regression suite and a
   benchmark on this host. No cloud dependency may enter the runtime
   path.
5. Decisions are committed as a dated record under `docs/`, including
   rejected options and the reason for rejection.
6. Acceptance: gate G12. Each proposal is reproducible from a script
   in `scripts/benchmarks/`.

### NFR-12. Resource isolation

1. Interactive requests take priority over every background task.
2. Background work uses at most half the processor threads and the lowest
   scheduling priority, and is paused while an interactive lease is held.
3. A paused background task resumes from its checkpoint and loses no
   completed work.
4. The appliance remains usable when the provider quota is exhausted:
   Tier A and offline capabilities continue, and background work pauses.
5. A quota check runs at most every five minutes and never blocks an
   interactive request.

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
4. `duplicate_of` is set only when two rows share the same normalised
   sender, the same normalised subject, a timestamp within 48 hours and
   an identical body hash. Metadata alone is insufficient: 402 groups
   share sender, subject and second but carry different bodies, so a
   metadata-only rule would wrongly merge distinct messages.

### 6.2. Calendar mirror

1. Existing `calendar_events.db` is the read model.
2. A separate `calendar_sandbox.db` is used for simulations. The two
   must never be the same file.

### 6.3. Matters and tasks

1. Delivered: `matters` and `matter_events`. The registry holds the name,
   client, reference, state and timestamps; events are append-only.
2. Tickets are the task record, and `ticket_links` links them to messages
   and documents. A separate `tasks` table was not needed.
3. `matter_summaries` remains future work for the nightly per-matter
   summary.

### 6.4. Glossary

1. Table: `glossary(term, definition, synonyms, matter_tags,
   updated_utc)`.
2. Operator edits win over inferred entries.

### 6.5. Trace

1. One JavaScript Object Notation (JSON) line per request:
   `request_id`, `timestamp`, `prompt`, `route`, `tier`, `timings`,
   `model`, `tokens_in`, `tokens_out`, `sources`, `action_proposed`,
   `outcome`.

### 6.6. Transaction and receipt store

1. `transactions.db` already holds `transaction_date`, `year`, `month`,
   `merchant`, `item_description`, `amount_minor`, `currency`,
   `amount_display`, `source_message_id`, `subject` and `confidence`.
2. Aggregation must run on `amount_minor`, never on the display string,
   and must filter to one currency before summing.
3. Duplicate suppression must run before aggregation. At least 217
   same-day, same-merchant, same-amount groups exist, consistent with
   an order confirmation and a dispatch notice describing one purchase.
4. Refunds must be stored as negative amounts, or in a separate table
   linked to the original purchase. Neither exists today, so a spend
   answer must say that refunds are not deducted.
5. Every aggregated answer must include a coverage record: earliest and
   latest receipt found, count by year, and any year with no receipts.
6. A receipt is admissible as evidence only when `source_message_id`
   resolves to a message in the `messages` table.

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
8. G8: spend totals match the oracle exactly on 20 queries, every
   ambiguous range triggers a clarification, and every answer states
   coverage, currency and refund treatment.
9. G9: ticket creation, lifecycle and queries pass 30, 20 and 25
   scenarios respectively.
10. G10: top-three recommendation containment is 100 per cent, and
    first-choice agreement is at least 80 per cent.
11. G11: administrative extraction F1 is at least 0.85.
12. G12: the stack review is committed with measured baselines and a
    written decision for every proposed change.
13. G13: with a background batch running, interactive p95 is no more than
    1.2 times the idle p95, and the batch resumes without losing work.
14. G14: the orchestrator is disabled by default; when enabled, it stays
   within the interactive latency tier on the routing suite.

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
| WP-9 Spend queries | B | FR-18, FR-19, G8 |
| WP-10 Stack review | Reviewer | G12 |
| WP-11 Governor and quota | Integrator | G13, G14 |

Files owned:

1. WP-0: `simulation/`.
2. WP-1: `message_store.py`, `backfill_messages.py`.
3. WP-2: `query_router.py`, `temporal_filter.py`.
4. WP-3: `classifier.py`, `triage.py`.
5. WP-4: `calendar_engine.py`, `invitations.py`.
6. WP-5: `tickets.py`.
7. WP-6: `glossary.py`, `contacts.py`, `documents.py`.
8. WP-7: `rag.py`, `api.py`, `config.py`.
9. WP-8: `docs/`, review notes.
10. WP-9: `transactions.py`, `spend_queries.py`.
11. WP-10: `docs/STACK_REVIEW_2026-11.md`,
    `scripts/benchmarks/`.
12. WP-11: `governor.py`, `orchestrator.py`,
    `scripts/governorctl.py`, `scripts/quota_watch.py`,
    `scripts/start_background_model.sh`.

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
6. **Default meaning of "last year".** Calendar year (1 January to
   31 December) or UK tax year (6 April to 5 April)? The clarification
   protocol asks when the answer is ambiguous, but a stored default
   removes a turn from routine spend questions.
7. **Refund treatment.** Should a refund reduce the spend in the year
   of purchase or in the year of refund?

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
| Spend on Amazon last year, with clarification | FR-18, FR-19 |
| Create and manage tickets | FR-20, FR-21 |
| Status of tickets and matters | FR-13, FR-22 |
| Close out completed work | FR-21, FR-29 |
| Recommend the next task | FR-23 |
| Admin and routine correspondence | FR-25, FR-26, FR-31 |
| Examine and change the stack | NFR-11, WP-10 |
| Use the hardware fully without delaying the user | FR-32, FR-33, |
| | NFR-12, WP-11 |
| Internet when unsure | FR-14 |
| Fast simple answers | FR-1, FR-2, FR-13, NFR-1 |

---

## Appendix A. Secretary task catalogue

This catalogue defines the intent taxonomy the router must cover. Each
line is a task the secretary should recognise, even where the required
action is only to draft or to propose.

### A.1. Inbox and correspondence

1. Show recent, unread or flagged messages.
2. Show messages from a named person or organisation.
3. Show messages about a matter, project or property.
4. Show messages with attachments or invitations.
5. Summarise a long thread.
6. Summarise everything received today.
7. Find the last message from or to a person.
8. Find a message by approximate date and topic.
9. Find an attachment by name or type.
10. Draft a reply to a thread.
11. Draft a new message from facts in the archive.
12. Draft a holding reply or acknowledgement.
13. Draft a chase for an unanswered message.
14. Draft a thank-you or confirmation note.
15. Rewrite a draft in a different register.
16. Translate a technical passage into plain English.
17. Extract the action list from a message.
18. Detect the requested response date in a message.
19. Compare two messages or two versions of a thread.
20. Identify who said what in a thread.

### A.2. Calendar and scheduling

1. Show today's or this week's commitments.
2. Show the next meeting and its preparation.
3. Find a free slot of a given length.
4. Check whether a proposed time clashes.
5. Propose three alternative times.
6. Accept, decline or tentatively accept an invitation.
7. Create, move or cancel an event.
8. Add travel time around a meeting.
9. Detect back-to-back or over-running days.
10. Summarise a meeting from the invitation and related mail.
11. Prepare a briefing note for a meeting.
12. List invitations awaiting a response.

### A.3. Tickets, matters and work management

1. Create a ticket from an email.
2. Create a ticket from a document or a verbal instruction.
3. Link an email to an existing ticket.
4. Merge duplicate tickets.
5. Change a ticket's priority, owner or due date.
6. Move a ticket through its lifecycle.
7. Close a ticket with a completion note.
8. Reopen a closed ticket.
9. List open, overdue or blocked tickets.
10. List tickets waiting on the operator.
11. List tickets waiting on a client or third party.
12. Show the status of a matter.
13. Show everything due tomorrow or this week.
14. Show what was closed this week.
15. Recommend the next task.
16. Explain why a task is ranked where it is.
17. Detect stale tickets.
18. Detect tickets whose blocker has cleared.
19. Detect probable duplicate tickets.
20. Produce a matter close-out checklist.
21. Produce a weekly review.
22. Estimate effort for a task.
23. Record time or effort against a ticket.
24. Reassign a ticket between matters.
25. Archive a completed matter.

### A.4. Documents and knowledge

1. Find a document by name, date or content.
2. Summarise a document in five bullets.
3. Compare two versions of a document.
4. Extract obligations or deadlines from an agreement.
5. Extract parties and defined terms.
6. File a document to a matter.
7. Draft a covering note for a document.
8. Produce an index for a bundle.
9. Find the governing law or jurisdiction clause.
10. Find a signature page or execution date.
11. Explain a term using the glossary.
12. Add or edit a glossary entry.

### A.5. Finance and receipts

1. Total spend with a merchant over a period.
2. Compare spend across two periods.
3. List the largest receipts in a period.
4. Find a receipt for a specific purchase.
5. List recurring subscriptions and renewal dates.
6. Detect a price increase on a subscription.
7. Match a receipt to a transaction.
8. List invoices awaiting payment.
9. Draft a payment reminder.
10. Categorise transactions by matter.
11. Report spend against a matter budget.
12. Flag a duplicate charge.
13. Flag an unusual or unexpected payment.

### A.6. Contacts and relationships

1. Identify a person and their organisation.
2. Show the last contact with a person.
3. Show all correspondence with an organisation.
4. Detect a change of role, address or telephone number.
5. List people not contacted for a long period.
6. Prepare a relationship summary before a meeting.
7. Detect a possible conflict of interest.
8. Correct or merge a contact record.

### A.7. Risk, compliance and security

1. Flag a suspected phishing message.
2. Flag a suspicious payment or bank-detail change.
3. Detect a complaint or a threat of one.
4. Detect a data subject request.
5. Detect a regulatory or statutory deadline.
6. Flag a possible privilege issue.
7. Flag confidential material sent to the wrong recipient.
8. Detect a possible conflict of interest.
9. Record a compliance decision.
10. Produce an audit trail for a matter.

### A.8. Reporting and planning

1. Produce the morning brief.
2. Produce the end-of-day summary.
3. Produce the weekly review.
4. Produce the monthly practice report.
5. Report on response times.
6. Report on overdue work by client.
7. Report on work in progress by matter.
8. Identify the three most at-risk items.
9. Forecast the week ahead.
10. Recommend what to delegate or defer.

### A.9. Personal administration

1. Remind about a renewal or expiry.
2. Remind about an appointment.
3. Remind about a travel booking.
4. Track a delivery.
5. Record a personal deadline.
6. List personal tasks for the day.
7. Find a booking confirmation.
8. Summarise a trip.
9. Cancel or change a booking.
10. Keep a personal note or fact.

---

## Appendix B. Implementation status

Recorded 13 November 2026 after the first build and live activation.

### B.1. Delivered

1. Correspondence lists, unread, invitations and topics:
   `message_store.py` and `secretary.py`; 58,203 rows, newest-20 p95
   0.96 ms, live unread results.
2. Deterministic routing and clarification: `query_router.py`; 64 tests,
   including the "recent emails" regression and the "last year" menu.
3. Spend totals: `spend_queries.py`; £2,637.61 for Amazon 2024 across
   182 receipts, with coverage and refund caveats.
4. Classification: `classifier.py`; 58,166 messages in 12.8 s, 84.3 per
   cent assigned, 15.7 per cent unknown.
5. Ticket lifecycle and recommendation: `tickets.py`; 51 tests and gate
   G9 in the simulation.
6. Matter registry and status by matter: `matters.py`; 19 tests and a
   live "no matter recorded" answer.
7. Calendar reading for today, tomorrow, this week and next week:
   `rag.py` and `calendar_engine.py`; live next-week commitment shown.
8. Interactive priority and quota pause: `governor.py` and
   `quota_watch.py`; `SIGSTOP` verified with a real process.
9. Model residency: `model_manager.py`; background 7B started on demand
   and evicted with its page cache dropped.
10. Gmail metadata: `gmail_metadata.py`; over 30,000 messages enriched
    with threads, labels and recipients.
11. Offline simulation: `simulation/`; 7 of 7 scenarios pass gates G1,
    G2, G3, G8 and G9.
12. Licence: MPL-2.0 accepted for `certifi`, full text shipped, gate
    amended and passing.
13. Exact-answer cache: `answer_cache.py`; a repeated 105.65-second
    answer served in 0.02 seconds, invalidated by any ingest.
14. Forward Gmail sync: `scripts/sync_gmail_new.py` and the
    continuous indexer; 66 new messages fetched through a seven-day query.
15. Deep-task queue: `deep_tasks.py` and `deep_worker.py`; a 14B cited
    summary completed while the 4B stayed resident.
16. Behavioural learning: `learning.py`; interaction log, feedback,
    style profile and nightly cache warming.
17. Monthly spend and the verified interaction catalogue, with its
    executable checker.
18. Deployment profession packs: `professions.py`, `scripts/profession.py`
    and `GET/POST /api/profession`. Four packs ship; the measured IT
    support case is in `practice-vault/docs/IT_SUPPORT_TEST_CASE.md`.
19. Colibri overnight path: `colibri.py` and
    `deep_worker.py --engine colibri`. A grounded 35B summary with six
    citations completed at about 0.8 tokens per second, then the engine
    stopped and returned its memory.
20. Overnight workflow: `deep_digest.py`, the secretary's
    **"what did you do overnight"** answer, and the nightly Markdown
    digest. The before/after analysis is in
    `practice-vault/docs/BEFORE_AFTER_2026-11-13.md`.
21. Calendar sync caller: `scripts/sync_calendar.py` upserts Google events
    into `calendar_events.db` and records `last_calendar_sync`. Live use
    waits for the Google Calendar API to be enabled.

### B.2. Partial

1. Fact answers and drafting: the streaming path and Qwen3-4B are live,
   but gates G5 and G6 have no scored run yet.
2. Invitations: 50 are listed from the classifier's category, but
   accept/decline and clash write-back wait for calendar write access and
   a working calendar sync.
3. Web look-up and offline persistence: the existing enrichment module is
   present but was not re-tested in this build.
4. Contacts and relationship memory: the existing engines are present but
   were not re-tested in this build.
5. Mixed-currency spend: the engine refuses a total that spans currencies
   rather than presenting a per-currency breakdown.

### B.3. Not built

1. Calendar writing, blocked by the read-only OAuth scope.
2. Attachment indexing and filtering.
3. A user-facing thread view, although `thread_id` is now populated.
