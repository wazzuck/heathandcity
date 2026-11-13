# Project Status: Hampstead & North West London Consulting

## 1. Done

1. Committed repository governance (`AGENTS.md`), local strategy brief
   (`hampstead_local_consulting_strategy.md`), and founder background notes
   (`neville_background.txt`).
2. Built the static, single-page showcase website (`index.html`,
   `css/styles.css`, `js/config.js`, `js/gpu-scene.js`, `js/app.js`) ready for
   GitHub Pages and Cloudflare Pages with zero reliance on `SharedArrayBuffer`,
   Cross-Origin Opener Policy (COOP), or Cross-Origin Embedder Policy (COEP)
   headers.
3. Implemented the Multi-Scene Interactive Three-Dimensional (3D) visual
   centrepiece using Web Graphics Processing Unit (WebGPU) hardware probing,
   Three.js Web Graphics Library (WebGL) custom shaders, a self-contained
   Two-Dimensional (2D) Canvas 3D fallback, and reduced-motion support.
4. Added interactive "One Clean Daily Screen" simulations for North West (NW)
   London verticals (Insurance Brokers, Surgeons/Medico-Legal, King's Counsel
   and Law Partners, and Family Offices/Property Principals), a Return on
   Investment (ROI) estimator, and senior readability controls (`A+` text size
   and Warm Paper theme).
5. Recorded architecture and legal/licence compliance in `docs/ARCHITECTURE.md`
   and verified all checks via `scripts/verify_site.py`.
6. Configured production domain `heathandcity.com` (`CNAME`), synchronised
   repository remotes to `wazzuck/heathandcity`, and updated package metadata.
7. Configured Spaceship Domain Name System (DNS) apex A records and www CNAME
   record; confirmed live HTTPS serving on `https://heathandcity.com`.
8. Constructed a complete 63-page offline-first restoration mock-up and
   cold-calling acquisition playbook for The Southgate Surgery
   (`clients/southgatesurgery/`) following the Silicon Practice provider
   collapse, covering all clinical rosters, opening hours, patient care
   pathways, and National Health Service (NHS) Design System assets.
9. Authored the comprehensive NHS client acquisition, legal, UK GDPR, Caldicott
   Principles, DSPT, and DTAC compliance guide in
   `docs/NHS_CLIENT_ACQUISITION_AND_COMPLIANCE_GUIDE.md`.
10. Compiled The Southgate Surgery leadership, ownership, and stakeholder
    contact intelligence dossier in
    `clients/southgatesurgery/PRACTICE_STAKEHOLDER_AND_CONTACT_DOSSIER.md`.
11. Updated the principal contact telephone number to `+44 20 4520 9114` in
    the centralised brand configuration and the static contact fallback.
12. Rewrote the landing page for time-poor principals: barristers, insurance
    and stock brokers, composers, and surgeons. Plain-English hero, three
    promises, four-practice demo, fixed-fee pricing, and a collapsed technical
    panel (`index.html`, `css/styles.css`, `js/config.js`, `js/app.js`).
13. Removed the animated Three.js and WebGPU visual, its engine module
    (`js/gpu-scene.js`), the `three` dependency, and the matching checks in
    `scripts/verify_site.py`. The page is now static text and layout only.
14. Shortened the hero label to "TECHNOLOGY FOR PRIVATE PRACTICES"
    (`js/config.js`, `index.html`).
15. Reworded the hero label to "STATE-OF-THE-ART TECHNOLOGY FOR SMALL
    PRIVATE PRACTICES" (`js/config.js`, `index.html`).
16. Renamed the brand to "Heath & City Technology" in the header, footer,
    page title and README (`js/config.js`, `index.html`, `README.md`).
17. Replaced the header "Book a coffee" button with the telephone number
    (`index.html`).
18. Header button now reads "Book an in-person coffee" with the telephone
    number (`index.html`).
19. Search and AI-assistant visibility (phases 1 and 2): static HTML for
    JavaScript-built content, FAQ, structured data, canonical and Open
    Graph tags, `robots.txt`, `sitemap.xml`, `llms.txt`, and verifier
    checks.
20. Added About the Founder section with portrait image
    (`img/neville-bryce.jpg`), verified 17+ years low-latency financial
    systems background from LinkedIn, credibility chips, and Schema.org
    `Person` JSON-LD entity.
21. Redesigned desktop layout: widened container to 92% (1600px cap) and
    added root scroll-padding-top clearance for the sticky header.
22. Refined opening hero & brand identity:
    - Updated primary headline to "Your information automated. Your time back."
    - Refined sales pitch copy with 50% larger typography.
    - Streamlined hero by moving coffee booking button to About section and
      removing practice standard card and secondary demo button.
    - Symmetrical vertical spacing above and below hero copy.
    - Replaced 'Promise 01-03' card headers with 'No Disruption', 'Privacy',
      and 'Continuity'.
    - Integrated labyrinth & seedling brand logo into header and browser
      favicon.
23. Refined brand emblem artwork and framing:
    - Removed tight inner labyrinth wall to open central sanctuary courtyard.
    - Enlarged golden leaf by 1.85x with anti-aliased smooth contours.
    - Made upper golden maze wall continuous and anchored stem flush to base.
    - Framed header emblem as crisp 56px square with 1px black rim border.
24. Added high-impact practice automations section & polished copy:
    - Added "If you have the data, we can build it" section with a vertical
      stack of three focused practice use cases (shared inbox matter tracking,
      100% private offline AI, and automated fee reconciliation).
    - Removed all orange pill badges across the entire site for cleaner visual
      hierarchy.
    - Retitled About section to "The Person Behind Heath & City" with a clean,
      grounded name label.
25. Refined layout alignment, section themes, typography, and copy:
    - Removed jump links from sticky top header banner.
    - Left-aligned opening hero narrative with 1600px main container.
    - Replaced "Hampstead Village" with "Hampstead" across all copy and configs.
    - Implemented alternating section background colours (light and darker)
      from top to bottom.
    - Added crisp 1px black borders around practice automation example cards.
    - Added business postal address (Flat 25, Corringham Court, Corringham
      Road, London NW11 7BY) to Direct contact card, footer, and configs.
    - Widened hero subtitle measure to 86ch for a clean two-line flow.
    - Updated hero pitch to "We work with you in person to quietly automate
      what makes sense..."
    - Updated practice automation card copy and retitled to "Email organisation
      and task tracking".
    - Added founder BSc (Hons) Software Engineering credential and redesigned
      all four founder credentials from cards into a vertical hairline ledger.
    - Standardised "City-Grade" chip and eliminated Americanisms ("rigor" ->
      "rigour", "catalog" -> "catalogue").
    - Enforced British English in AGENTS.md and automated check in
      verify_site.py.
26. Refined practice automations copy, section headers, and founder typography:
    - Retitled Card 2 to "Private document classification" with human-centred
      copy.
    - Retitled Card 3 to "Preparation of financial accounts" with grounded
      copy.
    - Set single-line gap above "A few examples of automation:" in styles.css.
    - Shortened about heading to "Behind Heath & City".
    - Updated founder credential chips to "BofA" and "SOTA Computing".
    - Increased founder name ("Neville Bryce") font size by 50% to 1.425rem.
27. Refined card hierarchy, terminology dictionaries, address, and credentials:
    - Retitled Card 2 to "Private document management" and moved to top of
      stack.
    - Highlighted custom practice dictionaries for nuanced terminology.
    - Removed "bespoke" from use-cases footer note.
    - Simplified address to "Corringham Court, Corringham Road" (removed
      Flat 25) across index.html, js/config.js, llms.txt, and llms-full.txt.
    - Removed redundant "Base" line from direct contact card and LLM specs.
    - Updated founder credential chips to "Algorithmic Trading & High
      Performance Computing" and standardised Title Case across all chips.
28. Added governance section, rebrand, and founder/header refinements:
    - Added "Contractual safeguards & the small print" section (Data
      Processing Agreement, Non-Disclosure Agreement, Technical and
      Organisational Measures, right to independent scrutiny).
    - Renamed the company to "Heath & City Technology Hampstead" across
      the page, metadata, config, robots.txt and llms files.
    - Reworded the founder bio in plain language and removed
      "ultra-low-latency"; edited card and footer-note copy.
    - Styled the LinkedIn button in LinkedIn blue; aligned and equalised
      the founder action buttons.
    - Aligned the header logo with the page content edge.
    - Direct line button now pulses between white and the section
      background colour (stops for reduced-motion readers).

29. Streamlined page architecture, expanded vertical suite & appliance spec:
    - Standardised "private UK data vault" across index.html, js/config.js,
      llms-full.txt, and local strategy documentation.
    - Refined core promise cards: removed redundant uppercase badges, reworded
      continuity card to support team without singling out PAs, and bolded
      "nothing to train anyone on".
    - Replaced button gradients with solid brand gold and removed header phone
      button background colour oscillation.
    - Removed redundant Section 6 (services-by-vertical) and Section 7
      (specialist-roles) to create a lean 9-section infomercial flow.
    - Separated Insurance Brokers and Stockbrokers, and expanded The Morning
      Screen to 9 distinct practices in a balanced 3x3 desktop grid:
      Barristers & KCs, Family Offices, Surgeons, Estate Agents, Insurance
      Brokers, Stockbrokers, Accountants & Tax, Authors & Composers & Talent,
      and Art Galleries & Fine Art.
    - Updated ROI Practice Recovery Estimator and Contact Form dropdowns to
      support all 9 practice verticals.
    - Added module cache-busting query parameters to ensure fresh browser asset
      hydration.
    - Codified AI Discoverability & LLM Sync Policy into AGENTS.md rule 4.
    - Synchronised llms.txt, llms-full.txt, and Schema.org JSON-LD structured
      data across all 9 target practices.
    - Authored comprehensive on-premises appliance technical architecture
      specification in docs/PRODUCT_SPECIFICATION.md.
    - Added Section 5 (Implementation Blueprint & AI Build Instructions)
      to docs/PRODUCT_SPECIFICATION.md, providing target directory structure,
      prerequisites setup script, five phased build milestones, automated test
      criteria, and copy-paste AI master build prompt for the Lenovo
      ThinkCentre M720q Tiny prototype.

30. Implemented sovereign practice automation prototype (practice-vault/):
    - Provisioned host prerequisites (Tesseract OCR, Poppler, CIFS, Ollama).
    - Pulled local models (llama3.2:3b and nomic-embed-text) via Ollama.
    - Built multi-format document parser (backend/app/ingest.py) supporting
      PDF, DOCX, XLSX, and TXT with local OCR fallback and chunking.
    - Implemented LanceDB vector indexing with BM25 Reciprocal Rank Fusion
      (backend/app/indexer.py) and verified CPU AVX2 acceleration.
    - Built deterministic RAG question answering engine (backend/app/rag.py)
      enforcing strict source and page citations with refusal guards.
    - Created autonomous correspondence triage clerk (backend/app/triage.py)
      staging pre-drafted replies in a mandatory human-approval queue.
    - Built REST API endpoints and single-page dashboard (frontend/) in pure
      ES6 JavaScript and CSS with zero external content delivery network calls.
    - Created test suites (backend/tests/) and acceptance criteria verification
      script (scripts/verify_prototype.py), passing all 5 acceptance checks.
    - Configured production runners, share mounting scripts, and operational
      runbook (practice-vault/README.md).

31. Added Google Workspace OAuth2 login & synchronization (practice-vault/):
    - Implemented Google Workspace OAuth2 service in backend/app/google_sync.py
      with read-only access scopes for Gmail and Google Drive / Docs.
    - Added RESTful endpoints in backend/app/api.py for login authorization,
      callback token exchange, status inspection, and live synchronization.
    - Added RFC-822 .eml and Google Takeout .mbox format parsers to
      backend/app/ingest.py.
    - Built 'Google Login & Workspace' dashboard tab in frontend/ with live
      connection status, client credential setup, and sync triggers.
    - Expanded automated unit test suite (backend/tests/test_google_sync.py),
      passing all 7 unit checks cleanly.

32. Provisioned Google Cloud OAuth 2.0 credentials for the Practice Vault
    appliance (operational task, no repository changes):
    - Enabled the Gmail API and the Google Drive API in Cloud project
      `marketcalc`.
    - Created the Google Auth Platform configuration (app name "Heath & City
      Practice Vault", External user type, testing mode) with the
      `gmail.readonly` and `drive.readonly` scopes and the operator account
      registered as a test user.
    - Created the Web application OAuth client "Practice Vault Local Web
      Client" with authorised redirect URI
      `http://127.0.0.1:8080/api/google/callback`.
    - Stored the Client ID and Client Secret outside the repository at
      `~/vunderland/keys/heathandcity.txt` (mode 600), sourced from `~/.bashrc`.
    - Redirected the appliance token store outside the repository by symlink,
      so no key material exists in any tracked or untracked repository file.
    - Verified `GET /api/google/status` returns `is_configured: true` and
      `is_connected: true`, and `GET /api/google/auth-url` returns a valid
      Google authorisation URL.

33. Configured host Debian 13 (Trixie) environment for Practice Vault:
    - Updated documentation (`docs/PRODUCT_SPECIFICATION.md`,
      `practice-vault/README.md`, `practice-vault/scripts/setup_m720q.sh`) to
      designate Debian 13 (Trixie) as the tested host Operating System (OS).
    - Configured systemd logind and sleep drop-ins
      (`/etc/systemd/logind.conf.d/zz-always-on.conf` and
      `/etc/systemd/sleep.conf.d/zz-always-on.conf`) and masked sleep/suspend
      targets to enforce always-on continuous operation without sleep or
      hibernation.
    - Preserved graphical login session (`graphical.target` via LightDM).
    - Verified dynamic Central Processing Unit (CPU) scaling under Intel
      Hardware P-States (HWP) and enabled dynamic boost: turbo boost
      activates up to 3.4-3.7 GHz across all cores during vector embedding
      and Artificial Intelligence (AI) inference, returning immediately to
      sub-1.6 GHz power-efficient idle when waiting for requests.
    - Fixed test isolation in `practice-vault/backend/app/google_sync.py` and
      verified full unit test and acceptance criteria suites.

34. Conducted full-repository API key and secret security audit:
    - Scanned working tree, untracked files, and Git commit history across 13
      secret regex classes (Google API keys, OAuth secrets, OpenAI, Anthropic,
      AWS, GitHub tokens, Slack tokens, Stripe keys, and private key blocks).
    - Neutralised legacy third-party Google Maps browser key embedded in the
      Southgate Surgery offline restoration mock-up.
    - Verified zero active API keys or credentials exist within the working
      tree or repository.
    - Verified that Google Workspace OAuth credentials remain strictly isolated
      in external storage at ~/vunderland/keys/heathandcity.txt.

35. Updated unified system architecture specification (`docs/ARCHITECTURE.md`):
    - Restructured into a decoupled dual-system architecture: System A (Public
      Showcase & AI Discoverability) and System B (Sovereign Practice Vault
      Appliance).
    - Codified Model Context Protocol (MCP) server integration (`stdio` and SSE)
      enabling Claude Desktop, Cursor, and IDE assistants to query private
      practice records securely.
    - Added multi-model local Small Language Model (SLM) routing
      (`llama3.2:3b`, `qwen2.5:3b`, `deepseek-r1:1.5b`) for specialised JSON
      extraction and step-by-step statutory limitation audits.
    - Added Stage 2 local neural cross-encoder reranking specification (ONNX
      Runtime) to elevate top-1 retrieval precision from 78% to over 93%.
    - Codified Speculation Rules API and targeted crawler routing directives.
    - Verified all 80-column line limits and British English rules.

36. Implemented Indexing Job Tracker, Volume Auditing & Google Docs Auto-Sync:
    - Built `IndexingJobTracker` (`backend/app/tracker.py`) tracking elapsed
      run-times, processing velocity (items/sec), and dynamic Estimated Time
      of Arrival (ETA) projections with persistent job history.
    - Built `VaultStatisticsService` (`backend/app/tracker.py`) calculating
      total tracked documents, indexed chunks, byte and megabyte volumes,
      word counts, and source breakdown.
    - Implemented background asynchronous watcher
      (`background_google_docs_watcher` in `backend/main.py`) polling Google
      Drive every 60 seconds with incremental ingestion of new/modified docs.
    - Updated dashboard User Interface (UI) (`frontend/index.html`,
      `css/dashboard.css`, `js/app.js`) with live statistics cards, active job
      progress bar, ETA timer, and manual auto-sync trigger.
    - Documented all features in `docs/ARCHITECTURE.md` (Sections 4.6-4.8).
    - Verified all 11 pytest checks and 5/5 prototype acceptance suite stages.

37. Evaluated Small Language Model (SLM) scaling and provisioned Qwen 3:
    - Conducted Central Processing Unit (CPU) latency and token throughput
      benchmarks across Qwen 2.5 (3B and 7B) and Llama 3.2 (3B), validating
      11.2 tok/s on 3B versus 4.5 tok/s on 7B.
    - Confirmed architectural decoupling of vector and lexical indexes from
      model inference: swapping base models requires zero re-indexing of
      the accumulated vault corpus (19,991 chunks / 9.2 million words).
    - Initiated local Ollama provisioning of `qwen3:latest` (5.2 GB)
      as the recommended next-generation reasoning candidate.
    - Codified model operational routing: Qwen 2.5 (3B) / Qwen 3 (4B) for
      interactive low-latency conversational queries (<3.5s response) and
      Qwen 2.5 (7B) / Qwen 3 (8B) for complex multi-document legal synthesis.

38. Built Sovereign Command-Line Interface (CLI) and Terminal REPL (`./vault`):
    - Implemented `practice-vault/scripts/vault_cli.py` and root launcher
      `./vault` supporting interactive terminal REPL and direct scriptable
      queries.
    - Added sub-second hybrid search mode (`./vault -s <query>`) returning
      ranked matches with cross-encoder neural scores in 0.02-0.8s.
    - Added plain-English Retrieval-Augmented Generation (RAG) query mode
      (`./vault "<question>"`) generating synthesised answers with verified
      source citations and execution telemetry.
    - Added appliance status inspection (`./vault --status`) and Google
      Workspace synchronisation inspection (`./vault --sync`).
    - Integrated interactive Read-Eval-Print Loop (REPL) with command history,
      on-the-fly model switching (`/model <tag>`), and ANSI styling.
    - Increased backend HTTP client timeout to 180s in `backend/app/rag.py`
      and enabled dynamic model overrides in `backend/app/api.py`.

39. Provisioned and Benchmarked Qwen 3 (4B) Reasoning Model (`qwen3:4b`):
    - Downloaded and verified `qwen3:4b` (2.5 GB, 4.0B parameters, 262k
      context) into local Ollama runtime.
    - Benchmarked raw token generation velocity at 9.42 tokens/sec on host
      quad-core CPU.
    - Identified architectural thinking behaviour: Qwen 3 natively emits
      chain-of-thought tokens (`<think> ... </think>`) before producing
      final syntheses.
    - Validated live Retrieval-Augmented Generation (RAG) execution via
      `./vault -m qwen3:4b -k 1`, returning factual summary with source
      citations in 71.8 seconds.
    - Confirmed operational recommendation: `qwen2.5:3b` remains optimal
      for low-latency interactive conversational search (~24-28s on CPU),
      while `qwen3:4b` is available for deep legal deliberation.

40. Advanced Corpus Ingestion to 42,700 Chunks:
    - Ingested historical Gmail messages in persistent batches, expanding
      corpus to 42,442+ documents and 42,700 chunks across LanceDB and
      SQLite FTS5.
    - Checkpointed sync state safely preserved in external appliance storage
      (`~/practice-vault-data/google_sync_state.json`).

41. Provisioned and Benchmarked SOTA Small Language Models (SLMs):
    - Researched latest open-weight models in the 3B-9B class; downloaded and
      verified `qwen3.5:4b` (3.3 GB), `qwen3.5:9b` (6.6 GB), and
      `phi4-mini:latest` (2.5 GB, Microsoft 3.8B SOTA) into local Ollama.
    - Deployed Ollama systemd override (`override.conf`) restricting concurrency
      to 1 model, setting 8192 context, 4 CPU threads, and 5-minute keep-alive.
    - Automated comparative benchmark matrix across candidates on host quad-core
      CPU: `phi4-mini:latest` delivered 2.05s warm latency (11.2 tok/s, 100%
      citation compliance); `qwen3.5:4b` with `think: false` delivered 4.70s
      warm latency (9.1 tok/s, 100% citation compliance).

42. Built Path B Structured Transaction Pipeline (`transactions.py`):
    - Offloaded exhaustive multi-document financial inquiries from SLMs to
      deterministic SQLite queries, eliminating arithmetic hallucinations.
    - Scanned indexed email database and extracted 1,607 verified transactions
      into `~/practice-vault-data/transactions.db` (£696,344.78 ledger spend).
    - Answering aggregation inquiries ("What did I buy last year?") in 0.02s
      with exact figures (108 orders, £2,160.34, merchant breakdown, itemised
      table, email citations), and "What did I buy from Amazon?" (725 orders,
      £15,255.52).

43. Hardened Ingestion Pipeline & Reduced Memory Footprint:
    - Upgraded `google_sync.py` to extract HTML email bodies using `lxml.html`,
      parse true email dates via `internalDate` into ISO8601 UTC strings, and
      chunk long emails (>400 words) with sliding windows and preserved headers.
    - Added automatic 35-second backoff and retry on Google API HTTP 403 / 429
      per-minute quota limits.
    - Replaced in-memory vector table deserialisation in `indexer.py` and
      `tracker.py` with direct SQLite FTS5 queries and incremental stat updates;
      backend memory RSS reduced to 586 MB.
    - All 15 unit tests passing in `practice-vault/backend/tests/`.

44. Launched Overnight Continuous Ingestion Daemon:
    - Initiated background indexer daemon (`scripts/continuous_indexer.py`)
      running continuously with controlled 12-second inter-batch pauses to
      ingest remaining historical Gmail messages to complete mailbox archive.
    - Corpus expanded to 55,171+ chunks across 54,885+ Gmail messages and 268
      Google Docs (22.55 million words, 232.5 MB storage).

45. Designed Ambiguity Testing Harness & Institutional Query Governance:
    - Catalogued 5 primary semantic ambiguity failure modes: under-specified
      references, false presuppositions, chronological version conflicts,
      homonym name collisions, and partial keyword scope traps.
    - Built comprehensive evaluation harness in
      `practice-vault/scripts/test_ambiguity_scenarios.py`.
    - Proved `qwen3.5:4b` under enhanced prompt achieved 5/5 flawless results
      (enumerated multiple distinct matters, refuted contradictory premises,
      isolated superseded rates, disambiguated homonyms, and guarded domain).
    - Integrated Enhanced Institutional Ambiguity-Aware prompt directives and
      dynamic reference date injection into production `rag.py`.
    - Optimised `main.py` startup using `asyncio.to_thread` and persistent
      statistics caching, maintaining sub-700 MB RSS memory usage.
    - Authored exhaustive architecture report in
      `docs/PRACTICE_VAULT_AMBIGUITY_AND_QUERY_GOVERNANCE.md`.
    - All 15 unit tests pass cleanly.

46. Commercial Open-Source Licensing & Legal Compliance Audit Suite:
    - Built automated legal audit suite (`scripts/verify_legal_compliance.py`)
      verifying zero copyleft contamination across all 65 installed packages,
      United Kingdom General Data Protection Regulation (UK GDPR) 127.0.0.1
      loopback isolation, zero cloud AI egress, and National Health Service
      (NHS) Caldicott Principles compliance.
    - Added binding compliance gate to `AGENTS.md` (Policy 4 and Section 9.5).
    - Authored comprehensive commercial sale and regulatory governance guide in
      `docs/COMMERCIAL_SALE_AND_REGULATORY_COMPLIANCE.md`.
    - Unit test `test_legal_compliance.py` passing in test suite.

47. Sovereign Audio Dictation, Speaker Diarisation & Person Tagging:
    - Integrated Faster-Whisper (`tiny.en` int8 on CPU) with Silero Voice
      Activity Detection (VAD) for fast local audio transcription.
    - Implemented multi-speaker acoustic feature clustering (Spectral Centroid,
      Root Mean Square energy, Zero-Crossing Rate) in
      `practice-vault/backend/app/audio.py` for CPU-efficient speaker turn
      separation.
    - Implemented person tagging API and UI allowing users to map speaker IDs
      to human roles (e.g. Counsel, Medical Consultant, Client).
    - Added automated Attendance Note synthesis and direct vault indexing.
    - Complies with Investigatory Powers Act 2016 statutory recording consent
      requirements.

48. Financial Ledger Exploration Dashboard & Structured Audit:
    - Added dedicated Expenditure & Ledger Audit view (`tab-ledger`) in
      `practice-vault/frontend/` with macro key performance metrics, annual
      spend filters (2021-2026), interactive merchant search, and CSV export.
    - Added REST endpoints `GET /api/transactions/summary` and `GET
      /api/transactions/ledger` in `practice-vault/backend/app/api.py`.

49. Advanced SOTA RAG Optimisations & Complete Test Suite:
    - Added Neural Cross-Encoder Refusal Gate (Corrective RAG) in `rag.py`
      achieving ~30ms instant refusal for out-of-domain queries.
    - Added Anthropic-style Contextual Retrieval header prepending in
      `ingest.py`.
    - Added legal and accounting synonym expansion in `indexer.py` SQLite FTS5.
    - Expanded test suite to 19 unit tests across
      `practice-vault/backend/tests/` (all 19 passing).

50. Sovereign Performance Tuning & In-Memory Retrieval Optimisation:
    - Configured SQLite Full-Text Search 5 (FTS5) with high-performance RAM
      PRAGMAs (64 MB page cache, 256 MB memory-mapped I/O, write-ahead logging).
    - Added in-memory Least Recently Used (LRU) query embedding cache (2,048
      entries) eliminating redundant inference for repeated searches.
    - Implemented concurrent dual-tower retrieval in `search_hybrid()`
      dispatching LanceDB vector search and SQLite FTS5 in parallel threads
      using `ThreadPoolExecutor(max_workers=2)`, halving retrieval latency.
    - Pre-warmed Ollama SLM in memory with 24-hour residency
      (`keep_alive: "24h"`, `num_thread: 4`, `num_predict: 512`), eliminating
      cold-load latency.

51. Advanced Nuance Handling, Aspect Decomposition & Interface Enhancements:
    - Implemented sub-aspect query decomposition in `_decompose_query()` and
      multi-aspect candidate fusion in `search_aspects()` with coverage bonuses.
    - Added multi-year financial variance comparison (`compare_years()` and
      `format_comparison_response()`) resolving comparative ledger inquiries.
    - Added deterministic merchant exclusions (`exclude_merchant`) and monetary
      threshold filters (`min_amount`, `max_amount`) for complex constraints.
    - Enhanced frontend Document Intelligence UI (`tab-search`): formatted
      Markdown table and list rendering, Nuanced Query Starters chips, query
      latency and attribution badge, and keyboard shortcuts (`Ctrl+Enter`, `/`,
      `Esc`).
    - Expanded test suite to 22 unit tests across
      `practice-vault/backend/tests/` (all 22 passing).

52. Configured Social Preview Metadata & Confirmed Multi-Domain SSL:
    - Added `og:image` and `twitter:image` tags in `index.html` referencing
      the brand emblem (`https://heathandcity.com/img/logo-square.png`).
    - Confirmed automated GitHub Pages multi-domain Transport Layer Security
      (TLS) certificate active across both `heathandcity.com` (HTTP/2 200) and
      `www.heathandcity.com` (HTTP/2 301 canonical redirect).

53. Native C++ Inference Engine & Real-Time Streaming Migration:
    - Compiled native upstream `llama-server` (b12277) targeting Coffee Lake
      AVX2/FMA/F16C (`-march=native -O3 -fopenmp`) and deployed to `bin/`.
    - Configured native runner (`scripts/start_llama_server.sh`) on loopback
      port 8081 with Flash Attention, 8,192 context window, `--parallel 2`
      execution slots, mmap+mlock memory pinning, and prompt n-gram
      speculative decoding.
    - Integrated real-time Server-Sent Events (SSE) token streaming via
      `POST /api/query/stream`, context compression (`_prune_context`),
      Hypothetical Document Embeddings (`_apply_hyde`), and GBNF
      grammar-constrained JSON decoding.

54. 100% Practice Correspondence Archive Ingestion:
    - Fully ingested 68,685 Gmail messages and 268 Google Docs into
      quarantined LanceDB and SQLite FTS5 storage (`practice-vault-data/`).
    - Total indexed volume reached 69,163 chunks with sub-second retrieval.
    - Reconciled 2,337 practice financial transaction records (£2,055,080.74).

55. Claude Code-Style Interactive Conversational Agent CLI (`./vault`):
    - Upgraded terminal interface into an interactive conversational agent
      modelled after Claude Code.
    - Renders user badges (`● You`), assistant headers (`╭─ Practice Clerk`),
      tool status cards, and source citation summaries using Rich.
    - Added multi-turn conversation dialogue history and automatic coreference
      pronoun resolution for retrieval.
    - Added root `./vault` executable delegating to local authenticated
      appliance daemon.

56. Built-In Local Tool Execution Engine:
    - Integrated `read_document`: parses external PDF, Word (DOCX), Excel
      (XLSX), Markdown (MD), and text/CSV on the fly without pre-indexing.
    - Integrated `ingest_document`: indexes single external documents into
      LanceDB and SQLite FTS5.
    - Integrated `search_vault` and `query_transactions`.
    - Added natural language file reference detection: mentioning an existing
      document path in conversational English triggers the tool automatically.
    - Test suite expanded to 30 unit tests (all 30 passing).
    - 4-gate commercial regulatory auditor verified (all 4 gates passing).

57. Executive Interface Usability, Ambiguity & Longitudinal Tracker:
    - Formulated comprehensive executive interface architecture tailored for
      time-poor, non-technical HNW principals, King's Counsel, and surgeons
      (`practice-vault/docs/EXECUTIVE_CLI_AND_INTERACTION_CATALOG_PLAN.md`).
    - Established persistent longitudinal testing framework and defect log
      (`practice-vault/docs/REAL_WORLD_USER_INTERACTION_TRACKER.md`) tracking
      response tightness, proactive ambiguity handling, and active memory.
    - Initialised 25-interaction catalog with initial baseline tests passed
      (clinical fact retrieval, coreference anchoring, document parsing,
      negative refusal).
58. Exported Cloudflare Worker setup handover for the Kay demonstration:
    - Authored `docs/CLOUDFLARE_WORKER_SETUP.md`, a self-contained
      specification for an external Artificial Intelligence (AI) agent to
      provision the proxy that protects the OpenRouter credential.
    - Recorded that the key cannot be held by GitHub Pages, because System A
      has zero server execution, and that a private repository cannot serve a
      credential at request time.
    - Documented the Worker as the sole role: store the secret, accept one
      route, forward to OpenRouter, return a stable JSON shape.
    - Verified free-plan limits against Cloudflare pricing (October and
      November 2026): 100,000 requests per day, 10 milliseconds Central
      Processing Unit (CPU) time per invocation, subrequests unbilled.
    - Recorded that OpenRouter inference remains chargeable separately, and
      that the free plan is described as unsuited to business-critical use.
    - Made rotation of the plaintext OpenRouter credential a binding
      prerequisite, with the key found tracked at `HEAD` in `wazzuck/vunderland`
      across five commits at mode `664`.
    - Included a complete origin-allow-listed Worker, its narrative
      walkthrough, endpoint verification commands, rollback, and an
      execution record table for completion during deployment.
    - Reported 29 further credential files tracked under `keys/` in the same
      repository as findings for the operator.
    - Verified `scripts/verify_site.py` and `scripts/verify_legal_compliance.py`
      both pass, and confirmed the embedded Worker source parses under
      `node --check`.

59. Provisioned and deployed the Kay classification Cloudflare Worker
    (operational task, Worker kept outside this repository at
    `~/kay-worker`):
    - Installed `wrangler` 4.86.0 (MIT OR Apache-2.0, permissive) and
      authorised it through the operator's browser; recorded Cloudflare
      account `bb26d0a4c5bcf535f66597313ab3c8c7`.
    - Chose hostname Option A (`workers.dev`) per `STATUS.md` entry 7
      (DNS remains at Spaceship); registered the account subdomain
      `heathandcity` through the Cloudflare Representational State
      Transfer (REST) API.
    - Deployed Worker `kay-classify` at
      `https://kay-classify.heathandcity.workers.dev` with the
      origin-allow-listed source from `docs/CLOUDFLARE_WORKER_SETUP.md`
      Section 8, storing `OPENROUTER_API_KEY` only in Cloudflare's
      secret store.
    - Substituted model `openai/gpt-6-luna` because the specification's
      `openai/gpt-luna-latest` is rejected by OpenRouter (HTTP 400).
    - Verified all four endpoint checks (404 root, 403 disallowed
      origin, 200 happy path returning department `placement` at 0.96
      confidence, zero `sk-or-` occurrences in any response).
    - Recorded execution details and deviations in
      `docs/CLOUDFLARE_WORKER_SETUP.md` Section 13.
    - Decisions recorded: free plan retained; demonstration accepts
      real client correspondence, with lawful basis, processor
      arrangement and international transfer safeguard still to be
      defined; OpenRouter key rotation deferred by operator decision.

60. Published the Kay demonstration on the website, identical to the
    Kay project's own demo (`harness/standalone_classifier`):
    - Copied `index.html`, `style.css` and `app.js` verbatim into
      `clients/kay/`; `style.css` is byte-identical to the Kay
      project, and `app.js` differs only by a Worker base-URL
      constant plus the two fetch paths it prefixes.
    - Extended the Worker with the two routes the demo calls:
      `GET /api/classifier/data` (14 buckets, 77-term glossary and
      12 scenario emails, exported from the Kay project by a
      regeneration script rather than hand-copied) and
      `POST /api/classifier/classify` (dual Jev and Luna pipeline).
    - Ported the classification half of `kayharness/classifier.py`
      to JavaScript in `~/kay-worker/src/pipeline.js`: identical
      prompts, scoring rules and deterministic fallbacks. Verified
      by running the Python original and the port side by side on
      the default scenario with live calls disabled: the outputs are
      canonically identical.
    - Verified live dual classification through OpenRouter: Jev
      `typesafe/jev-1.14` returned `risk` at 0.77 (High) and Luna
      (alias `~openai/gpt-luna-latest`, served by `gpt-6-luna`)
      returned a full briefing with 13 recognised terms.
    - Kept the page `noindex,nofollow`, excluded from `sitemap.xml`,
      and deliberately unlinked from `index.html`, `robots.txt` and
      the `llms*` files.
    - Retained the client-side access gate (user `kay`) comparing a
      SHA-256 digest rather than plaintext, and the credential link
      form (`#<user>:<password>`) whose fragment is never sent to
      the server and is stripped from the address bar on arrival.
      Recorded that static hosting cannot authenticate, so this is
      a soft gate, not a security boundary.
    - Fixed a defect in the specification's Worker: it answered the
      Cross-Origin Resource Sharing (CORS) preflight `OPTIONS`
      request with 405, which would have blocked every browser
      request. The Worker now answers preflights with 204 for the
      approved origin and 403 for any other.
    - Verified the handover's Section 10 checks still pass (404
      root, 403 foreign origin, 200 legacy `/classify`, zero
      `sk-or-` occurrences), plus 80-column wrapping, `node --check`
      on every script, and British Professional English spelling.

61. Built and verified the Practice Vault personal secretary on branch
    merged into `master` (350 tests):
    - Requirements, 31 functional requirements, a 100-task catalogue and
      simulation gates in `docs/PRACTICE_VAULT_SECRETARY_REQUIREMENTS.md`.
    - Structured message store: 58,166 messages backfilled in 4.2 s;
      newest-20 query p95 0.96 ms; topic search through the full-text
      index with relevance ranking.
    - Deterministic router and secretary path: list, spend, ticket and
      clarification questions answered before retrieval, fixing the
      original "recent emails" defect.
    - Rules-first classifier: 58,166 messages in 12.8 s, 84.3 per cent
      assigned; an optional overnight model pass covers the unknown
      minority.
    - Ticket engine with an audited lifecycle, portfolio queries, hygiene
      proposals and an explainable next-task recommendation.
    - Interactive-priority governor: background workers are paused with
      `SIGSTOP` and resumed with `SIGCONT`; verified with a real process.
    - Quota watcher every five minutes, pausing background work below
      five per cent remaining.
    - Offline simulation harness: 7/7 scenarios pass gates G1, G2, G3, G8
      and G9 at p95 107 ms.
    - Model bake-off and adoption: Qwen3-4B interactive, Qwen2.5-7B
      background, Qwen3-1.7B optional orchestrator; Phi-4-mini retained
      as the low-memory fallback.
    - MPL-2.0 accepted for `certifi`; the full licence text ships at
      `licences/MPL-2.0.txt`, and the legal gate now reports it.

---

## 2. Next

1. **Standing Activity: Real-World Usability & Interaction Testing**:
   - Iteratively execute and verify catalog interactions against live archives.
   - Refine response tightness to direct bottom-line conclusions
     (maximum 3 bullets).
   - Implement proactive disambiguation router presenting 2–3 numbered choices.
   - Implement 4-stage Active Practice Memory for permanent self-correction.
2. Deploy appliance hardware image to production Lenovo ThinkCentre M720q
   appliances for commercial partner trials.
3. Optional: Add client-specific keyword synonym dictionaries for specialised
   chambers and clinical practices.
4. Visibility phase 3 (one page per profession) awaits a decision.
5. Visibility phase 4 (off-page): Google Business Profile, Search Console,
   Bing Webmaster Tools, LinkedIn, directories, and real testimonials.
6. Fix Legal Gate 1 false positives in `scripts/verify_legal_compliance.py`:
   match SPDX licence identifiers or classifiers instead of free text, and
   provision `practice-vault/venv` so the audit runs against the appliance
   environment rather than the host Python installation.
7. Rotate the OpenRouter credential (deferred operator decision) and
   update the secret stored by Worker `kay-classify`; also report the 29
   credential files tracked under `keys/` in `wazzuck/vunderland`.
8. Define and record the lawful basis, the OpenRouter processor
   arrangement, and the international transfer safeguard required before
   the Kay demonstration handles real client correspondence.
9. Publish the Google OAuth consent screen to production before
   17 November 2026, or re-consent weekly; the refresh token expires then.
10. Restart the Practice Vault service to load the merged
    interactive-priority code and the Qwen3-4B interactive model.
11. Rotate the local OpenCode service password, which was printed into a
    session transcript during diagnostics.

---

## 3. Blocked

1. Legal Gate 1 of `scripts/verify_legal_compliance.py` fails on three
   pre-existing false positives (`scipy`, `pandas`, `docutils`). The
   operator has deferred the fix to a `Next` item; sale-readiness checks
   remain blocked until the gate passes cleanly.
2. Decide the appliance network binding: it listens on `0.0.0.0:9090` and
   the log records requests from public addresses. Bind loopback,
   firewall port 9090 to the local subnet, or require a Virtual Private
   Network.
