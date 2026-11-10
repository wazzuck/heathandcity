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
  brandName: "Heath & City Technology Hampstead",
  brandMonogram: "H·C",
  brandStatusBadge: "STATE-OF-THE-ART TECHNOLOGY FOR SMALL PRIVATE PRACTICES",
  brandTagline:
    "Quiet, private systems for small London practices",
  principalRole: "Principal Systems & Sovereign Data Architect",
  experienceYears: 17,
  primaryPostcodes: "NW3 · NW6 · NW8 · NW11 · N6 · The City",
  neighbourhoods: [
    "Hampstead (NW3)",
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
  officeAddress:
    "Corringham Court, Corringham Road, London NW11 7BY",
  officeLocation: "Hampstead, London NW3 (visits by appointment)",
  immediateSupportSite: "https://itoldyouso.tech",
  immediateSupportLabel: "itoldyouso.tech"
});

/**
 * Step 2: Define VERTICAL_DEMOS.
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

  estate: {
    id: "estate",
    tabLabel: "Estate Agents",
    badge: "PRIME RESIDENTIAL & COMMERCIAL · NW3 / NW8 / W1",
    headline: "Prime Estate Agents & Property Advisors",
    summary:
      "Accelerate sales progression, cross-check anti-money laundering " +
      "paperwork, and keep tenancy compliance audits in order.",
    stats: [
      { label: "Sales Progression Files", value: "24 Matters", tone: "gold" },
      { label: "AML & Source of Funds Gaps", value: "3 Incomplete", tone: "amber" },
      { label: "Tenancy Safety Certificates", value: "100% In Order", tone: "emerald" }
    ],
    digestTime: "08:15 daily pipeline update · On-premises vault",
    queueItems: [
      {
        priority: "SALES PROGRESSION CHASER",
        client: "Hampstead Village detached residence (£4.2m, illustrative)",
        matter: "Draft contract pack and management replies stalled with seller's solicitor",
        status: "Enquiries unanswered for 11 days; polite escalation drafted for approval",
        timer: "Stalled 11 days",
        sourceRef: "Solicitor_Thread · Enquiries_List.pdf"
      },
      {
        priority: "AML & SOURCE OF FUNDS",
        client: "Purchaser, St John's Wood penthouse (illustrative)",
        matter: "Anti-Money Laundering (AML) and source of wealth verification",
        status: "Bank statement received; overseas trust deed still outstanding",
        timer: "Deposit ready, awaiting deed",
        sourceRef: "Client_AML_Checklist.xlsx"
      },
      {
        priority: "TENANCY STATUTORY COMPLIANCE",
        client: "Belsize Park portfolio (18 managed units, illustrative)",
        matter: "Annual Gas Safety (CP12) and Electrical Installation (EICR) renewals",
        status: "Two certificates expiring in 30 days; contractor booking emails drafted",
        timer: "Expiring in 28 days",
        sourceRef: "Tenancy_Compliance_Register.xlsx"
      }
    ],
    guarantee:
      "We track compliance dates, summarise conveyancing correspondence, " +
      "and draft chasers. We never communicate with buyers, vendors, or " +
      "solicitors without your explicit instruction."
  },

  insurance: {
    id: "insurance",
    tabLabel: "Insurance Brokers",
    badge: "COMMERCIAL & PRIVATE BROKERAGE · NW3 / EC3",
    headline: "Commercial & Private Client Insurance Brokers",
    summary:
      "Track renewal dates 90 days out, catch changes in underwriter " +
      "policy wording, and chase missing client schedules automatically.",
    stats: [
      { label: "Renewals Under Review", value: "12 Policies", tone: "gold" },
      { label: "Wording Alterations Flagged", value: "2 Clauses", tone: "amber" },
      { label: "Data Sent to Public Cloud", value: "None", tone: "emerald" }
    ],
    digestTime: "08:00 daily summary · Stays on your machine",
    queueItems: [
      {
        priority: "RENEWAL · 6 DAYS",
        client: "Commercial property portfolio (illustrative)",
        matter: "Annual policy renewal with underwriter's amended wording",
        status: "Wording received; two changed warranty clauses flagged for review",
        timer: "Renewal in 6 days",
        sourceRef: "Outlook thread · Endorsement PDF, Clause 14.2"
      },
      {
        priority: "VALUATION CHASER",
        client: "Private client, fine art schedule (illustrative)",
        matter: "Independent valuation needed before Lloyd's syndicate binds risk",
        status: "Polite chaser drafted for your approval to send to client PA",
        timer: "Waiting 4 days",
        sourceRef: "Attachment: Valuation_Schedule.pdf"
      },
      {
        priority: "CLAIMS CORRESPONDENCE",
        client: "Water ingress claim, Hampstead residential block (illustrative)",
        matter: "Loss adjuster report cross-checked against original policy excess",
        status: "Coverage confirmed; £250 excess verified against policy terms",
        timer: "Reviewed 08:14 today",
        sourceRef: "Loss_Adjuster_Report_Final.pdf · Page 4"
      }
    ],
    guarantee:
      "We organise paperwork, track renewal dates, and prepare draft " +
      "chasers. We do not provide regulated insurance advice, and no " +
      "message leaves your office without your approval."
  },

  stockbrokers: {
    id: "stockbrokers",
    tabLabel: "Stockbrokers & Wealth",
    badge: "WEALTH MANAGEMENT & BROKING · THE CITY / MAYFAIR",
    headline: "Stockbrokers, Investment Managers & Family Wealth",
    summary:
      "Contract notes matched against custodian feeds, corporate actions " +
      "tracked, and cash reconciliations verified quietly on-site.",
    stats: [
      { label: "Contract Notes Matched", value: "142 Notes", tone: "gold" },
      { label: "Custodian Breaks", value: "0 Breaks", tone: "emerald" },
      { label: "Corporate Actions Approaching", value: "1 Action", tone: "amber" }
    ],
    digestTime: "07:45 morning reconciliation · Local installation",
    queueItems: [
      {
        priority: "CONTRACT NOTE MATCHING",
        client: "Institutional execution and custody feeds (illustrative)",
        matter: "Previous business day equity and fixed-income settlement match",
        status: "All 142 contract notes verified against custodian broker logs",
        timer: "Completed 07:45 today",
        sourceRef: "Custodian_Feed_Matched.csv"
      },
      {
        priority: "CORPORATE ACTION · 48 HOURS",
        client: "Discretionary portfolio holdings (illustrative)",
        matter: "Rights issue election notification across 28 client sub-accounts",
        status: "Summary memo prepared showing election options and client cash balances",
        timer: "Election deadline in 2 days",
        sourceRef: "Corporate_Action_Circular.pdf · Page 2"
      },
      {
        priority: "SUITABILITY FILE CHECK",
        client: "Mandate renewal: offshore trust account (illustrative)",
        matter: "Annual risk profile and wealth verification review",
        status: "All documentation complete; compliance sign-off pack drafted",
        timer: "Waiting for partner review",
        sourceRef: "Mandate_Annual_Review.docx"
      }
    ],
    guarantee:
      "Our software operates entirely within your walls on dedicated local " +
      "hardware. We do not handle funds or give investment advice; the " +
      "system automates documentation and reconciliation."
  },

  composers: {
    id: "composers",
    tabLabel: "Composers & Music",
    badge: "COMPOSERS & MUSIC PUBLISHING · NW3 / NW6",
    headline: "Composers, Songwriters & Music Publishers",
    summary:
      "Royalty statements are checked against your own records, and every " +
      "commission deadline stays visible.",
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
 * Step 3: Define PRICING_STEPS.
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
      "A private machine in your office, or a private UK data vault",
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
