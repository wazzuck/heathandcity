/**
 * ============================================================================
 * FILE: js/config.js
 * ============================================================================
 *
 * PURPOSE:
 * Centralised configuration, brand identity tokens, interactive simulation
 * presets, and domain data for the Hampstead and North West (NW) London
 * private technology consulting showcase website.
 *
 * WHAT THIS FILE IS NOT FOR:
 * - This file does not perform Document Object Model (DOM) manipulation.
 * - This file does not execute Web Graphics Processing Unit (WebGPU) or Web
 *   Graphics Library (WebGL) rendering calls.
 * - This file does not store any confidential client or personal data.
 *
 * INVARIANTS:
 * 1. Every exported constant is immutable and serialisable.
 * 2. Brand identity strings live exclusively in SITE_CONFIG so that changing
 *    the provisional To Be Confirmed (TBC) practice name updates the entire
 *    User Interface (UI) from a single location.
 * 3. All customer-facing copy uses British English spelling and terminology
 *    appropriate for senior (60+) principals.
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
  brandName: "Heath & City Systems Advisory",
  brandMonogram: "H·C",
  brandStatusBadge: "HAMPSTEAD NW3 · PRIVATE PRACTICE",
  brandTagline:
    "City-Grade Engineering & Private Systems for Hampstead Practices",
  principalRole: "Principal Systems & Sovereign Data Architect",
  experienceYears: 17,
  primaryPostcodes: "NW3 · NW6 · NW8 · NW11 · N6",
  neighbourhoods: [
    "Hampstead Village (NW3)",
    "Belsize Park (NW3)",
    "St John's Wood (NW8)",
    "West Hampstead (NW6)",
    "Swiss Cottage (NW3)",
    "Highgate (N6)",
    "Hampstead Garden Suburb (NW11)",
    "Golders Green (NW11)"
  ],
  contactEmail: "principal@heathandcity.co.uk",
  contactPhoneDisplay: "020 7946 0921",
  contactPhoneHref: "+442079460921",
  officeLocation: "Hampstead Village, London NW3 (On-Site Visits by Appointment)",
  immediateSupportSite: "https://itoldyouso.tech",
  immediateSupportLabel: "itoldyouso.tech"
});

/**
 * Step 2: Define SCENE_MODES.
 * Configures the three interactive Three-Dimensional (3D) GPU visual
 * centrepiece modes requested in the brief.
 *
 * Fields and units:
 * - id: Unique string key consumed by the GPU scene controller.
 * - number: Display ordinal ("01", "02", "03").
 * - title: Human-readable scene title.
 * - subtitle: Short executive explanation of the visual metaphor.
 * - technicalNote: Explanation of the underlying architecture represented.
 * - defaultOrder: Initial Entropy-to-Order ratio (float in [0.0, 1.0]).
 * - primaryHex: Primary brass/gold or highlight colour in hexadecimal integer.
 * - secondaryHex: Secondary emerald or slate colour in hexadecimal integer.
 * - accentCss: Cascading Style Sheets (CSS) colour string for UI badges.
 * - metrics: Live telemetry labels displayed in the heads-up overlay.
 */
export const SCENE_MODES = Object.freeze({
  lattice: {
    id: "lattice",
    number: "01",
    title: "Order from Chaos: The Autonomous Inbox Lattice",
    subtitle:
      "Watch unstructured emails, 2,000-page PDF bundles, and insurer " +
      "remittances pass through a normalisation lens into an ordered ledger.",
    technicalNote:
      "Simulates automated entity extraction (Client, Policy, Diagnosis, " +
      "Urgency) converting inbox entropy into a structured state matrix.",
    defaultOrder: 0.78,
    primaryHex: 0xd4af6a,
    secondaryHex: 0x34d399,
    accentCss: "#d4af6a",
    metrics: {
      pipeline: "ENTITY EXTRACTION & STATE CHASER",
      throughput: "2,400 PAGES / MIN LOCAL OCR",
      egress: "0 BYTES EXTERNAL CLOUD EGRESS"
    }
  },
  vault: {
    id: "vault",
    number: "02",
    title: "The Sovereign Vault: Two-Tower Neural Retrieval",
    subtitle:
      "Twenty years of legal precedents, trust deeds, and clinical records " +
      "indexed inside a locked-down Hampstead hardware vault.",
    technicalNote:
      "Visualises Two-Tower neural vector search paired with hybrid keyword " +
      "indexing inside an air-gapped or private United Kingdom (UK) perimeter.",
    defaultOrder: 0.88,
    primaryHex: 0x60a5fa,
    secondaryHex: 0xd4af6a,
    accentCss: "#60a5fa",
    metrics: {
      pipeline: "TWO-TOWER NEURAL + HYBRID INDEX",
      throughput: "< 18 MS ARCHIVE QUERY LATENCY",
      egress: "SRA / BAR / NHS CONFIDENTIALITY LOCKED"
    }
  },
  telemetry: {
    id: "telemetry",
    number: "03",
    title: "City-to-Heath Precision: Portfolio & Fee Telemetry",
    subtitle:
      "Seventeen years of low-latency City market data engineering applied " +
      "to multi-bank PDF statements, rent rolls, and hospital billing.",
    technicalNote:
      "Models continuous cross-document reconciliation across private banks, " +
      "Special Purpose Vehicle (SPV) leases, and medical insurer remittances.",
    defaultOrder: 0.84,
    primaryHex: 0x34d399,
    secondaryHex: 0xd4af6a,
    accentCss: "#34d399",
    metrics: {
      pipeline: "DETERMINISTIC PDF & LEDGER RECONCILIATION",
      throughput: "99.98% DISCREPANCY DETECTION",
      egress: "90 / 60 / 30-DAY COMPLIANCE RADAR"
    }
  }
});

/**
 * Step 3: Define VERTICAL_DEMOS.
 * Provides interactive data for the "One Clean Daily Screen" simulation,
 * demonstrating how the 80/20 Reusable Core Engine adapts to each NW London
 * vertical without forcing principals to abandon Microsoft Outlook or Gmail.
 */
export const VERTICAL_DEMOS = Object.freeze({
  insurance: {
    id: "insurance",
    tabLabel: "Insurance & Mortgage Brokers",
    badge: "BEACHHEAD VERTICAL · NW3 / NW6",
    headline: "Boutique Insurance Brokers & Financial Introducers",
    summary:
      "Eliminates shared-inbox chaos, missed policy renewals, and manual " +
      "underwriter chasing while staff continue using Outlook as normal.",
    sceneMode: "lattice",
    stats: [
      { label: "Needs Reply Today", value: "4 Urgent", tone: "amber" },
      { label: "Waiting on Underwriter", value: "7 Chasers", tone: "gold" },
      { label: "30-Day Renewals Protected", value: "£1.42m GWP", tone: "emerald" }
    ],
    digestTime: "08:00 AM Daily Principal Digest",
    queueItems: [
      {
        priority: "URGENT · TODAY",
        client: "Heathside Estates Ltd (34 Frognal, NW3)",
        matter: "Commercial Block Policy Renewal · Hiscox / Aviva",
        status: "Underwriter endorsement PDF parsed; 2 clauses flagged",
        timer: "Renewal in 6 days",
        sourceRef: "Outlook Thread #4812 · Page 4 Clause 11.2"
      },
      {
        priority: "WAITING ON REPLY · 72H",
        client: "Dr A. Abramson (Belsize Park Gardens)",
        matter: "High-Value Home & Fine Art Schedule Valuation",
        status: "Automated draft chaser prepared for secretary approval",
        timer: "Awaiting surveyor PDF (3 days)",
        sourceRef: "Attachment: Valuation_Schedule_2026.pdf"
      },
      {
        priority: "RECONCILED · COMPLETE",
        client: "Camden Medical Chambers LLP",
        matter: "Professional Indemnity Declaration & Broker Fee",
        status: "Policy bound; commission matched to bank feed",
        timer: "Verified 08:14",
        sourceRef: "Ledger Match #904 · Zero variance"
      }
    ],
    guarantee:
      "The system never sends an email to your clients or underwriters " +
      "behind your back. It prepares the draft and organises the queue so " +
      "you and your staff remain in total control."
  },

  medical: {
    id: "medical",
    tabLabel: "Surgeons & Medico-Legal",
    badge: "ROYAL FREE · WELLINGTON · HARLEY ST",
    headline: "Senior Medical Consultants, Surgeons & Expert Witnesses",
    summary:
      "Turns 2,000-page scanned National Health Service (NHS) medico-legal " +
      "PDF bundles into hyperlinked Word chronologies, and catches every " +
      "unpaid Bupa, AXA, or Vitality procedure.",
    sceneMode: "vault",
    stats: [
      { label: "Bundle Processed Locally", value: "2,140 Pages", tone: "gold" },
      { label: "Weekend Hours Saved", value: "12.5 Hours", tone: "emerald" },
      { label: "Insurer Shortfalls Flagged", value: "£4,850", tone: "amber" }
    ],
    digestTime: "100% On-Premises Private Medical Appliance",
    queueItems: [
      {
        priority: "CHRONOLOGY READY",
        client: "Re: Instructing Solicitors — Clinical Negligence Bundle",
        matter: "2,140-Page Scanned NHS & General Practitioner (GP) Records",
        status: "148 clinical events extracted with exact PDF page links",
        timer: "Processed in 11 mins locally",
        sourceRef: "Bundle_Vol1_to_4.pdf · Pages 14, 89, 412, 1,108"
      },
      {
        priority: "REVENUE LEAKAGE ALERT",
        client: "Wellington Hospital Theatre List vs Remittance Advice",
        matter: "3 Arthroscopic Procedures Under-Reimbursed by Insurer",
        status: "CCSD code mismatch detected between invoice and Bupa PDF",
        timer: "£1,920 recovery draft ready",
        sourceRef: "Remittance_8821.pdf vs Clinic_List_Oct.xlsx"
      },
      {
        priority: "DICTATION PIPELINE",
        client: "Post-Clinic Voice Note (4 Patients · Harley Street)",
        matter: "GP Referral Letters + Pre-Authorisation + Secretary Tasks",
        status: "4 draft letters formatted in consultant template",
        timer: "Awaiting 1-click sign-off",
        sourceRef: "Audio_Memo_1740.wav -> Structured Word Drafts"
      }
    ],
    guarantee:
      "Patient records and medico-legal bundles are processed on dedicated " +
      "encrypted hardware in your study or clinic—zero patient data is ever " +
      "uploaded to public cloud AI services."
  },

  legal: {
    id: "legal",
    tabLabel: "KCs, Arbitrators & Law Partners",
    badge: "CHAMBERS & BOUTIQUE PARTNERS · NW3 / WC2",
    headline: "King's Counsel, Arbitrators, Mediators & Boutique Law Firms",
    summary:
      "Search 20 years of opinions, skeleton arguments, and trust structures " +
      "in seconds on a private 'Second Brain' appliance, and detect financial " +
      "disclosure discrepancies across hundreds of bank statements.",
    sceneMode: "vault",
    stats: [
      { label: "Archive Indexed Privately", value: "22 Years", tone: "gold" },
      { label: "Disclosure Gaps Detected", value: "3 Missing Ranges", tone: "amber" },
      { label: "Public Cloud Data Exposure", value: "0.0%", tone: "emerald" }
    ],
    digestTime: "Air-Gapped Linux / GPU Sovereign Vault",
    queueItems: [
      {
        priority: "PRECEDENT RETRIEVAL",
        client: "20-Year Personal Archive (Opinions, Clauses & Skeletons)",
        matter: "Query: 'Offshore discretionary trust variation jurisdiction'",
        status: "6 exact historical opinions retrieved with paragraph citations",
        timer: "Query time: 14 milliseconds",
        sourceRef: "Chambers_Archive_2014_Opinion_19.docx · Para 34"
      },
      {
        priority: "DISCLOSURE ANOMALY",
        client: "Ancillary Relief / High-Net-Worth Matrimonial Bundle",
        matter: "380 PDF Bank Statements & Company Accounts Cross-Check",
        status: "Missing statement period (14 Mar – 30 Apr) & unlinked transfer",
        timer: "£185,000 transfer flagged",
        sourceRef: "Disclosure_Tab_19_JuliusBaer.pdf · Page 77"
      },
      {
        priority: "KYC / AML ONBOARDING",
        client: "Hampstead Conveyancing & Private Client Trust Matter",
        matter: "Source-of-Wealth Declaration & Certified Passport Expiry",
        status: "1 document outstanding from family office accountant",
        timer: "Polite reminder queued",
        sourceRef: "Solicitors Regulation Authority (SRA) Compliance Log #312"
      }
    ],
    guarantee:
      "Engineered to satisfy Bar Standards Board and Solicitors Regulation " +
      "Authority (SRA) confidentiality duties: all neural indexing runs on " +
      "your private hardware under your physical key."
  },

  family_office: {
    id: "family_office",
    tabLabel: "Family Offices & Property Principals",
    badge: "MULTI-SPV PORTFOLIOS · NW3 / NW8",
    headline: "Family Offices, Boutique Financiers & Property Principals",
    summary:
      "Applies City financial message normalisation to aggregate multi-bank " +
      "PDF capital calls and protect multi-SPV property portfolios against " +
      "silent lease-break, rent review, and compliance losses.",
    sceneMode: "telemetry",
    stats: [
      { label: "Private Bank & Fund PDFs", value: "18 Feeds Normalised", tone: "gold" },
      { label: "SPV Properties Monitored", value: "64 Units / 9 SPVs", tone: "emerald" },
      { label: "90-Day Compliance Horizon", value: "2 Action Items", tone: "amber" }
    ],
    digestTime: "Automated Master Ledger & Compliance Radar",
    queueItems: [
      {
        priority: "CAPITAL CALL & NAV PARSED",
        client: "Private Bank & Syndicate Consolidated Reporting",
        matter: "Coutts, UBS & Private Equity Capital Call PDF Extraction",
        status: "Figures validated and mapped directly to Master Excel Workbook",
        timer: "Reconciled 07:45 AM",
        sourceRef: "Fund_IV_Drawdown_Notice.pdf -> Master_NAV_2026.xlsx"
      },
      {
        priority: "90-DAY RENT REVIEW WINDOW",
        client: "SPV 4: Fitzjohn's Holdings Ltd (Commercial Ground Floor)",
        matter: "Upward-Only Rent Review Notice Window Closing",
        status: "Managing agent PDF statement cross-checked against lease clause",
        timer: "62 days remaining · High Value",
        sourceRef: "Lease_2021_Fitzjohns.pdf · Schedule 3"
      },
      {
        priority: "STATUTORY CERTIFICATE RADAR",
        client: "SPV 2: Belsize Residential Portfolio (14 Flats)",
        matter: "Gas Safety, Electrical (EICR) & Energy (EPC) Renewal Tracker",
        status: "2 flats require Gas Safety renewal within 45 days",
        timer: "Contractor quote matched",
        sourceRef: "Managing_Agent_Oct_Pack.pdf · Unit 4B & 9A"
      }
    ],
    guarantee:
      "Replaces days of manual copy-pasting from private bank PDFs and " +
      "managing agent statements with deterministic validation rules built " +
      "on 17 years of City market data engineering."
  }
});

/**
 * Step 4: Define SPECIALIST_ROLES.
 * Captures the four high-status positioning pillars from Section 3 of the
 * strategy brief.
 */
export const SPECIALIST_ROLES = Object.freeze([
  {
    number: "01",
    role: "Private AI & Sovereign Data Architect",
    bestFor:
      "King's Counsel, Arbitrators, Boutique Law Firms, Private Surgeons, " +
      "Psychiatrists & Family Offices",
    pitch:
      "You want modern search to find a clause across 20 years of files or " +
      "summarise a 2,000-page bundle in seconds—but legally and " +
      "reputationally, you cannot upload confidential client or patient data " +
      "into public cloud tools. We install locked-down search and document " +
      "appliances on dedicated hardware right in your Hampstead office or " +
      "private UK vault where zero data ever leaves your control.",
    architectureTag: "Two-Tower Neural Search · Local Linux/GPU Appliance"
  },
  {
    number: "02",
    role: "Financial & Document Data Normalisation Engineer",
    bestFor:
      "Family Offices, Multi-SPV Property Principals, Insurance Brokers & " +
      "Wealth/Tax Advisors",
    pitch:
      "Built on 17 years in the City of London engineering ultra-low-latency " +
      "systems that extract and map complex exchange data. Today, we build " +
      "automated pipelines for North West London principals that read " +
      "incoming PDF statements, rent rolls, insurer remittances, and emails—" +
      "turning messy paperwork into a single reconciled ledger.",
    architectureTag: "Deterministic PDF Extraction · Ledger Reconciliation"
  },
  {
    number: "03",
    role: "Practice Continuity & Workflow Engineer",
    bestFor:
      "Established Practice Owners (60+), Medical Consultants, Chartered " +
      "Surveyors & Principals Facing 'Single-PA Fragility'",
    pitch:
      "If your trusted Personal Assistant (PA), medical secretary, or office " +
      "manager took a month off tomorrow, would your practice still run " +
      "smoothly? We turn chaotic shared inboxes and fragile spreadsheets " +
      "into a quiet Digital Filing Clerk—giving you complete visibility over " +
      "every client, task, and unpaid fee in 10 minutes a day.",
    architectureTag: "Zero Change to Outlook/Gmail · Institutional Memory"
  },
  {
    number: "04",
    role: "Fractional CTO & Private Technologist",
    bestFor:
      "Ongoing Retainer Care for Wealthy Principals, Chambers & Boutique " +
      "Practices Across NW3, NW6, NW8, NW11 & N6",
    pitch:
      "Large institutions have an internal engineering department keeping " +
      "their systems automated, backed up, and cyber-secure. For a flat " +
      "monthly retainer, you have your own private Chief Technology Officer " +
      "(CTO) five minutes down the road in Hampstead—maintaining your " +
      "systems, protecting family and firm data, and refining workflows.",
    architectureTag: "In-Person Hampstead Check-Ins · Priority Local Response"
  }
]);

/**
 * Step 5: Define PRICING_STEPS.
 * Implements the three-step engagement and pricing architecture from
 * Section 6 of the strategy document.
 */
export const PRICING_STEPS = Object.freeze([
  {
    step: "STEP 01 · PROOF OF VALUE",
    title: "Inbox & Workflow Audit + Working Prototype",
    price: "£750 – £1,500",
    duration: "10 – 14 Days · Fixed Fee",
    description:
      "We ingest a read-only sample of your historical emails or PDF bundles " +
      "with zero disruption to your live Outlook, Gmail, or office routines, " +
      "and demonstrate a working tracker populated with your actual cases.",
    deliverables: [
      "On-site consultation in Hampstead / NW London",
      "Read-only historical sample ingestion (zero live risk)",
      "Working 'One Clean Daily Screen' prototype with your data",
      "Fixed-price blueprint and Return on Investment (ROI) assessment"
    ]
  },
  {
    step: "STEP 02 · BESPOKE DEPLOYMENT",
    title: "Tailored Implementation & Sovereign Hardware Setup",
    price: "£3,000 – £10,000+",
    duration: "3 – 6 Weeks · Turnkey Delivery",
    description:
      "Full deployment of the 80% battle-tested core engine tailored with " +
      "your 20% domain-specific rules, custom Word/Excel templates, " +
      "historical archive indexing, and gentle staff onboarding.",
    deliverables: [
      "Dedicated on-premises quiet hardware box or private UK vault",
      "20-year document & email archive indexing",
      "Custom domain rules (Renewals, Bundles, Leases, or Remittances)",
      "8:00 AM Automated Daily Principal Digest & PA workflow training"
    ],
    featured: true
  },
  {
    step: "STEP 03 · CONTINUITY RETAINER",
    title: "Local Managed Care & Fractional CTO Retainer",
    price: "£350 – £1,200 / month",
    duration: "Ongoing Local Partnership",
    description:
      "Continuous monitoring, encrypted backup verification, insurer or bank " +
      "template updates, and a monthly in-person review at your Hampstead " +
      "office to refine rules and eliminate new administrative bottlenecks.",
    deliverables: [
      "Monthly in-person check-in at your NW London office or study",
      "Hardware, security, and private model maintenance",
      "Immediate adjustments when banks, insurers, or courts change formats",
      "Direct personal telephone access—never an offshore ticket queue"
    ]
  }
]);
