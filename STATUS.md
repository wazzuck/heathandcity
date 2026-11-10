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

---

## 2. Next

1. Visibility phase 3 (one page per profession) awaits a decision.
2. Visibility phase 4 (off-page): Google Business Profile, Search Console,
   Bing Webmaster Tools, LinkedIn, directories, and real testimonials.
3. Add a bespoke social preview Open Graph image (`og:image`).
4. Allow GitHub to finish issuing the multi-domain certificate expansion for
   `www.heathandcity.com` (automated background job).

---

## 3. Blocked

1. None.
