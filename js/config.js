/**
 * ============================================================================
 * FILE: js/config.js
 * ============================================================================
 *
 * PURPOSE:
 * Centralised configuration, brand identity tokens, interactive simulation
 * presets, and plain-English domain data for the Hampstead and North West (NW)
 * London private technology showcase website. The audience is time-poor
 * professional principals: barristers and King's Counsel (KC), insurance and
 * stock brokers, composers and music publishers, and surgeons and senior
 * consultants.
 *
 * WHAT THIS FILE IS NOT FOR:
 * - This file does not perform Document Object Model (DOM) manipulation.
 * - This file does not execute Web Graphics Processing Unit (WebGPU) or Web
 *   Graphics Library (WebGL) rendering calls.
 * - This file does not store any confidential client, patient or personal
 *   data. Every client name, figure and reference below is invented for
 *   illustration.
 *
 * INVARIANTS:
 * 1. Every exported constant is immutable and serialisable.
 * 2. Brand identity strings live exclusively in SITE_CONFIG so that changing
 *    the provisional To Be Confirmed (TBC) practice name updates the entire
 *    User Interface (UI) from a single location.
 * 3. Copy is written in plain British English. Sentences are short, and each
 *    acronym is expanded at its first use on the page.
 * ============================================================================
 */

/**
 * Step 1: Define SITE_CONFIG.
 * Holds the provisional brand identity, geographic coverage across North West
 * London postcodes, founder credentials, and contact endpoints.
 * Consumers: js/app.js (populates [data-brand-*] nodes in index.html).
 */
export const SITE_CONFIG = Object.freeze({
  // Provisional brand name (marked TBC for effortless future replacement).
  brandName: "Heath & City Computer Systems Advisory",
  brandMonogram: "H·C",
  brandStatusBadge: "HAMPSTEAD NW3 · TECHNOLOGY FOR PRIVATE PRACTICES",
  brandTagline:
    "Quiet, private systems for small London practices",
  principalRole: "Principal Systems & Sovereign Data Architect",
  experienceYears: 17,
  primaryPostcodes: "NW3 · NW6 · NW8 · NW11 · N6 · The City",
  neighbourhoods: [
    "Hampstead Village (NW3)",
    "Belsize Park (NW3)",
    "St John's Wood (NW8)",
    "West Hampstead (NW6)",
    "Swiss Cottage (NW3)",
    "Highgate (N6)",
    "Hampstead Garden Suburb (NW11)",
    "Golders Green (NW11)",
    "The City of London"
  ],
  contactEmail: "contactus@heathandcity.com",
  contactPhoneDisplay: "020 4520 9114",
  contactPhoneHref: "02045209114",
  officeLocation: "Hampstead Village, London NW3 (visits by appointment)",
  immediateSupportSite: "https://itoldyouso.tech",
  immediateSupportLabel: "itoldyouso.tech"
});

/**
 * Step 2: Define SCENE_MODES.
 * Configures the three interactive Three-Dimensional (3D) GPU visual
 * centrepiece modes. The copy is deliberately plain: the visitor is a busy
 * professional, not an engineer. The technical wording is kept in
 * technicalNote for the reader who wants it.
 *
 * Fields and units:
 * - id: Unique string key consumed by the GPU scene controller.
 * - number: Display ordinal ("01", "02", "03").
 * - title: Human-readable scene title, under about six words.
 * - subtitle: One-sentence plain-English explanation of the visual.
 * - technicalNote: Explanation of the underlying architecture represented.
 * - defaultOrder: Initial Entropy-to-Order ratio (float in [0.0, 1.0]).
 * - primaryHex: Primary brass/gold or highlight colour in hexadecimal integer.
 * - secondaryHex: Secondary emerald or slate colour in hexadecimal integer.
 * - accentCss: Cascading Style Sheets (CSS) colour string for UI badges.
 * - metrics: Short telemetry labels displayed in the heads-up overlay.
 *   Consumed by: js/app.js (activateSceneModeUI).
 */
export const SCENE_MODES = Object.freeze({
  lattice: {
    id: "lattice",
    number: "01",
    title: "Order from chaos",
    subtitle:
      "Emails, bundles and statements come in messy and leave sorted by " +
      "client and deadline.",
    technicalNote:
      "Illustrates automated entity extraction (client, matter, deadline, " +
      "urgency) turning unstructured documents into an ordered list.",
    defaultOrder: 0.78,
    primaryHex: 0xd4af6a,
    secondaryHex: 0x34d399,
    accentCss: "#d4af6a",
    metrics: {
      pipeline: "SORTED BY CLIENT & DEADLINE",
      throughput: "2,400 PAGES / MIN ON-SITE",
      egress: "0 BYTES SENT TO PUBLIC CLOUD"
    }
  },
  vault: {
    id: "vault",
    number: "02",
    title: "Your private archive",
    subtitle:
      "Decades of notes, opinions and records, searchable in seconds on a " +
      "machine in your own office.",
    technicalNote:
      "Illustrates Two-Tower neural search combined with keyword indexing, " +
      "running inside a private network with no public cloud involved.",
    defaultOrder: 0.88,
    primaryHex: 0x60a5fa,
    secondaryHex: 0xd4af6a,
    accentCss: "#60a5fa",
    metrics: {
      pipeline: "PRIVATE SEARCH, NO CLOUD",
      throughput: "< 18 MS SEARCH TIME",
      egress: "CONFIDENTIAL · STAYS ON SITE"
    }
  },
  telemetry: {
    id: "telemetry",
    number: "03",
    title: "Money and deadlines in one view",
    subtitle:
      "Statements, royalty reports and key dates matched against each other, " +
      "so nothing is missed.",
    technicalNote:
      "Illustrates ledger reconciliation across bank statements, insurer " +
      "remittances, royalty statements and deadline calendars.",
    defaultOrder: 0.84,
    primaryHex: 0x34d399,
    secondaryHex: 0xd4af6a,
    accentCss: "#34d399",
    metrics: {
      pipeline: "STATEMENTS MATCHED TO LEDGER",
      throughput: "MISMATCHES FLAGGED AUTOMATICALLY",
      egress: "ALERTS AT 90 / 60 / 30 DAYS"
    }
  }
});

/**
 * Step 3: Define VERTICAL_DEMOS.
 * Provides interactive data for the "A typical morning" simulation. Each entry
 * is one practice type. Every name, figure and reference is invented and is
 * labelled as illustrative on the page.
 *
 * Field meanings:
 * - id: Key used by the tab buttons (data-vertical-tab) and by app.js.
 * - tabLabel: Short label shown on the tab button.
 * - badge: Small uppercase label above the headline.
 * - headline: Practice type, shown as the panel title.
 * - summary: One plain sentence describing the benefit.
 * - sceneMode: Scene in SCENE_MODES that is shown alongside this demo.
 * - stats: Three key figures, each with a tone used for colour coding.
 * - digestTime: Label for the daily summary timing.
 * - queueItems: Three rows, each with priority, client, matter, status, timer
 *   and sourceRef (the document the figure was taken from).
 * - guarantee: Reassurance line about human control.
 */
export const VERTICAL_DEMOS = Object.freeze({
  legal: {
    id: "legal",
    tabLabel: "Barristers & KCs",
    badge: "CHAMBERS & PRIVATE PRACTICE · NW3 / WC2",
    headline: "Barristers, King's Counsel & Arbitrators",
    summary:
      "Find any old opinion in seconds, and see disclosure gaps before " +
      "they cost you a hearing.",
    sceneMode: "vault",
    stats: [
      { label: "Opinions Searchable", value: "20 Years", tone: "gold" },
      { label: "Disclosure Gaps Flagged", value: "3 Missing Periods", tone: "amber" },
      { label: "Data Sent to Public Cloud", value: "None", tone: "emerald" }
    ],
    digestTime: "Private system · Stays in your office",
    queueItems: [
      {
        priority: "FIND A PRECEDENT",
        client: "Your archive of opinions and skeleton arguments",
        matter: "Search: 'trust variation, offshore jurisdiction'",
        status: "Six matching opinions found, with paragraph references",
        timer: "Found in 14 milliseconds",
        sourceRef: "Opinion_2014_Example.docx · Para 34"
      },
      {
        priority: "DISCLOSURE CHECK",
        client: "Bundle of 380 bank statements (illustrative case)",
        matter: "Cross-check of statements and transfers",
        status: "A statement period is missing and one transfer is unexplained",
        timer: "Flagged for review today",
        sourceRef: "Disclosure_Bundle_Example.pdf · Page 77"
      },
      {
        priority: "CLIENT ID CHASER",
        client: "New instruction: trust and source-of-wealth documents",
        matter: "Passport and trust deed checks",
        status: "One document still outstanding; a reminder is ready",
        timer: "Reminder waiting for your approval",
        sourceRef: "Client_Checklist_Example.xlsx"
      }
    ],
    guarantee:
      "Nothing is sent to a client, solicitor or court without your say-so. " +
      "The system finds and prepares; you decide."
  },

  brokers: {
    id: "brokers",
    tabLabel: "Insurance & Stock Brokers",
    badge: "BROKERAGE & TRADING PRACTICE · NW3 / NW8",
    headline: "Insurance Brokers & Stock Brokers",
    summary:
      "Renewals and trade records stay on schedule, and your team keeps " +
      "working in Outlook as usual.",
    sceneMode: "lattice",
    stats: [
      { label: "Needs Reply Today", value: "4 Items", tone: "amber" },
      { label: "Waiting on Underwriter", value: "7 Chasers", tone: "gold" },
      { label: "Renewals in 30 Days", value: "Covered", tone: "emerald" }
    ],
    digestTime: "08:00 daily summary to you",
    queueItems: [
      {
        priority: "RENEWAL · 6 DAYS",
        client: "Commercial property client (illustrative)",
        matter: "Policy renewal with the underwriter's amended wording",
        status: "Wording received; two changed clauses flagged for you",
        timer: "Renewal in 6 days",
        sourceRef: "Outlook thread · Endorsement PDF, Clause 11.2"
      },
      {
        priority: "WAITING ON REPLY · 72 HOURS",
        client: "Private client, fine art schedule (illustrative)",
        matter: "Valuation needed before the policy can be bound",
        status: "Polite chaser drafted for your approval",
        timer: "Waiting 3 days",
        sourceRef: "Attachment: Valuation_Schedule.pdf"
      },
      {
        priority: "RECORDS · COMPLETE",
        client: "Trade confirmations for last week (illustrative)",
        matter: "Contract notes matched and filed for retention",
        status: "All trades matched; nothing missing",
        timer: "Completed 08:14",
        sourceRef: "Contract_Notes_Week_Example.csv"
      }
    ],
    guarantee:
      "We organise paperwork and prepare drafts. We do not give regulated " +
      "advice, and no message leaves your office without your approval."
  },

  composers: {
    id: "composers",
    tabLabel: "Composers & Music",
    badge: "COMPOSERS & MUSIC PUBLISHING · NW3 / NW6",
    headline: "Composers, Songwriters & Music Publishers",
    summary:
      "Royalty statements are checked against your own records, and every " +
      "commission deadline stays visible.",
    sceneMode: "telemetry",
    stats: [
      { label: "Statements Matched", value: "18 Reports", tone: "gold" },
      { label: "Unmatched Works", value: "2 To Review", tone: "amber" },
      { label: "Commission Deadlines", value: "On Track", tone: "emerald" }
    ],
    digestTime: "Monthly royalty review · Weekly deadline list",
    queueItems: [
      {
        priority: "ROYALTY STATEMENT",
        client: "Collection-society statement (illustrative)",
        matter: "Matched against your works list and writer splits",
        status: "Fourteen works matched; two titles need a closer look",
        timer: "Reviewed this morning",
        sourceRef: "Statement_Example_Q3.pdf · Page 2"
      },
      {
        priority: "COMMISSION DUE · 9 DAYS",
        client: "Film score commission (illustrative)",
        matter: "Stems, cue sheet and final invoice",
        status: "Stems delivered; cue sheet still outstanding",
        timer: "Due in 9 days",
        sourceRef: "Commission_Brief_Example.docx"
      },
      {
        priority: "SPLIT AGREEMENT",
        client: "Co-writing agreement (illustrative)",
        matter: "Writer shares and publishing terms on file",
        status: "Shares agree with the signed agreement",
        timer: "Filed and verified",
        sourceRef: "Co_Write_Agreement_Example.pdf · Schedule 1"
      }
    ],
    guarantee:
      "Your catalogue, splits and contracts stay on your own private " +
      "system. We flag differences for you to check; we never change a " +
      "royalty figure on your behalf."
  },

  medical: {
    id: "medical",
    tabLabel: "Surgeons & Consultants",
    badge: "CONSULTANT PRACTICE · HARLEY ST / NW3",
    headline: "Surgeons, Consultants & Expert Witnesses",
    summary:
      "Long medical bundles become a dated chronology, and underpaid " +
      "private procedures are flagged for recovery.",
    sceneMode: "vault",
    stats: [
      { label: "Bundle Read On-Site", value: "2,140 Pages", tone: "gold" },
      { label: "Weekend Hours Saved", value: "12.5 Hours", tone: "emerald" },
      { label: "Possible Underpayment", value: "£4,850", tone: "amber" }
    ],
    digestTime: "100% on-premises · Nothing leaves your study",
    queueItems: [
      {
        priority: "CHRONOLOGY READY",
        client: "Medico-legal bundle (illustrative case)",
        matter: "2,140 pages of records, dated and in order",
        status: "148 events listed, each linked to its page number",
        timer: "Ready in 11 minutes",
        sourceRef: "Bundle_Vol1_to_4.pdf · Pages 14, 89, 412"
      },
      {
        priority: "UNDERPAYMENT ALERT",
        client: "Private theatre list against insurer payment (illustrative)",
        matter: "Three procedures paid below the agreed amount",
        status: "A code mismatch between invoice and remittance is flagged",
        timer: "£1,920 claim draft ready",
        sourceRef: "Remittance_Example.pdf vs Theatre_List_Example.xlsx"
      },
      {
        priority: "VOICE NOTE",
        client: "Post-clinic dictation (four patients, illustrative)",
        matter: "Referral letters and insurer requests",
        status: "Four draft letters prepared in your usual format",
        timer: "Waiting for your sign-off",
        sourceRef: "Dictation_Example.wav → draft Word files"
      }
    ],
    guarantee:
      "Patient records are read on dedicated, encrypted hardware in your " +
      "study or clinic. No patient data is uploaded to public cloud AI."
  }
});

/**
 * Step 4: Define SPECIALIST_ROLES.
 * Four ways of working together, written as short plain-English summaries.
 * Fields:
 * - number: Two-digit display ordinal.
 * - role: Short title, shown as the card heading.
 * - bestFor: Who the role suits, shown as "Designed for".
 * - summary: One or two sentences explaining what it does.
 * - architectureTag: Two short keywords shown as a badge on the card.
 */
export const SPECIALIST_ROLES = Object.freeze([
  {
    number: "01",
    role: "Private search for your records",
    bestFor:
      "Barristers, King's Counsel, surgeons and anyone with decades of files",
    summary:
      "Find any note, opinion or report in seconds. The search runs on a " +
      "machine in your office, so your files never go to a public AI tool.",
    architectureTag: "Private search · On-site machine"
  },
  {
    number: "02",
    role: "Money and paperwork, matched",
    bestFor:
      "Brokers, composers, family offices and anyone reconciling statements",
    summary:
      "Bank statements, remittances and royalty reports are checked against " +
      "your own records, and differences are flagged for you to decide.",
    architectureTag: "Reconciliation · Statement matching"
  },
  {
    number: "03",
    role: "A practice that runs without one person",
    bestFor:
      "Practices where one assistant holds everything in their inbox",
    summary:
      "Key tasks, deadlines and contacts are kept in one shared place, so " +
      "holidays and sick days no longer stall the work.",
    architectureTag: "Shared memory · No change to Outlook"
  },
  {
    number: "04",
    role: "Ongoing local support",
    bestFor:
      "Principals who want one named person, close by, who knows the practice",
    summary:
      "A monthly visit to your office in Hampstead, direct telephone access, " +
      "and quick changes whenever your banks or insurers change formats.",
    architectureTag: "Monthly visit · Priority response"
  }
]);

/**
 * Step 5: Define PRICING_STEPS.
 * Implements the three-step, fixed-fee engagement structure. Prices are
 * quoted in Pounds Sterling (£). Each entry is rendered as one pricing card.
 */
export const PRICING_STEPS = Object.freeze([
  {
    step: "STEP 01 · TRIAL",
    title: "Two-week trial on your own documents",
    price: "£750 – £1,500",
    duration: "10 – 14 days · fixed fee",
    description:
      "We work from a sample of your past emails or documents. Your live " +
      "Outlook or Gmail is not touched, and you see the results on your " +
      "own cases before you commit to anything.",
    deliverables: [
      "A short meeting at your office or over coffee in Hampstead",
      "Read-only work on a sample of your documents",
      "A working summary built from your real cases",
      "A fixed-price plan, with the expected time saving"
    ]
  },
  {
    step: "STEP 02 · SET-UP",
    title: "Full set-up in your office",
    price: "£3,000 – £10,000+",
    duration: "3 – 6 weeks · fixed fee",
    description:
      "We install the system on a machine in your office, or in a private UK " +
      "vault, tailored to your templates, insurers, banks and clients. Your " +
      "team is shown how to use it in short sessions.",
    deliverables: [
      "A private machine in your office, or a private UK vault",
      "Your past documents indexed for search",
      "Rules set up for your own forms, bundles and deadlines",
      "A daily summary, plus short training for your team"
    ],
    featured: true
  },
  {
    step: "STEP 03 · CARE",
    title: "Ongoing local care",
    price: "£350 – £1,200 / month",
    duration: "Ongoing · cancel with notice",
    description:
      "Regular checks, backups and updates, plus a monthly visit so the " +
      "system keeps pace with your practice. You speak to a person, not a " +
      "ticket queue.",
    deliverables: [
      "A monthly visit to your office in NW London",
      "Security checks, backups and updates",
      "Quick changes when banks, insurers or courts change formats",
      "Direct telephone access to your named contact"
    ]
  }
]);
