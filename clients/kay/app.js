/**
 * London Market: Standalone Email Classification & Summarisation Demo.
 * Front-end controller using British English.
 *
 * Distinct features:
 * 1. Step-by-step guidance for non-technical operations and broking teams.
 * 2. Lloyd's corporate insurance dictionary directory with integrated
 *    definitions and practical market examples.
 * 3. Fixed directory of 77 standard London market terms and acronyms.
 * 4. Pre-prepared London market demonstration emails with 1-click loading.
 * 5. Automated email triage dashboard (department routing & executive
 *    briefing).
 */

(function () {
  "use strict";

  const STORAGE_KEY_GLOSSARY = "london_market_placement_glossary_v3";

  // Base URL of the Cloudflare Worker that answers this demo's two
  // API routes. The static host executes no code, so the Worker
  // holds the OpenRouter credential and both the dictionary data and
  // the classification run are served from there. Every other line
  // of this controller is unchanged from the Kay project.
  const API_BASE = "https://kay-classify.heathandcity.workers.dev";

  const PRELOADED_RESULTS = {
    jev: {
      model: "Jev System One (Deterministic Decision Engine)",
      mode: "calibrated_decision_model",
      top_bucket: "risk",
      top_bucket_name: "Risk register",
      confidence: 0.9586,
      confidence_tier: "High",
      probabilities: {
        risk: 0.9586,
        placement: 0.0262,
        query: 0.0118,
        compliance: 0.0007,
        submission: 0.0007,
        binding: 0.0005,
        servicing: 0.0004,
        finance: 0.0003,
        claims: 0.0002,
        mga: 0.0002,
        internal: 0.0001,
        review: 0.0001,
        excluded: 0.0001,
        security: 0.0001,
      },
      rationale:
        "Evaluated top placement match as 'Risk register' (risk) with " +
        "95.9% calibrated probability. Decisive signals detected from " +
        "domain phrasing and Lloyd's market conventions.",
    },
    luna: {
      model: "Luna",
      executive_summary:
        "The email outlines a new slip presentation for a global cargo " +
        "open cover placement for BioHealth International PLC, with a " +
        "target inception date of 1st December 2026. The draft MRC slip " +
        "is attached, and the broker is seeking recommendations for " +
        "leading syndicate underwriters for the initial written line.",
      deal_metadata: {
        insured: "BioHealth International PLC",
        class_of_business: "Marine Cargo & Specie",
        limit_or_sum_insured: "USD 25,000,000 any one vessel or conveyance",
        policy_or_risk_reference: "2026/2027 global open cover",
        effective_dates: "1st December 2026",
      },
      jargon_detected: [
        {
          term: "BOR (Broker of Record)",
          category: "Capacity & Placing",
          context: "The RFQ was received under a freshly executed BOR letter.",
        },
        {
          term: "General Average (GA)",
          category: "Claims & Adjustment",
          context:
            "General Average covered under Institute Cargo Clauses (A).",
        },
        {
          term: "Leading Syndicate / Leader",
          category: "Capacity & Placing",
          context:
            "Seeking recommended leading syndicate underwriters for terms.",
        },
        {
          term: "Line Slip Facility",
          category: "Capacity & Placing",
          context:
            "Placement excluded from Line Slip Facility due to parameters.",
        },
        {
          term: "Lloyd's Box",
          category: "Regulatory & Compliance",
          context:
            "Broker queuing at leader's Lloyd's Box in The Room for scratch.",
        },
        {
          term: "Losses Occurring Basis",
          category: "Underwriting Conditions",
          context:
            "Coverage trigger structured on Losses Occurring Basis.",
        },
        {
          term: "MRC (Market Reform Contract)",
          category: "Contract Documentation",
          context:
            "Draft MRC placing slip attached for global open cover.",
        },
        {
          term: "Open Market Risk",
          category: "Capacity & Placing",
          context:
            "Placement mode specified as Open Market Risk via PPL.",
        },
        {
          term: "Policy Schedule",
          category: "Contract Documentation",
          context:
            "Policy Schedule limit specified at USD 25,000,000 per vessel.",
        },
        {
          term: "PPL (Placing Platform Limited)",
          category: "Contract Documentation",
          context:
            "Placement submitted digitally via PPL electronic trading.",
        },
        {
          term: "PPW (Premium Payment Warranty)",
          category: "Underwriting Conditions",
          context: "Settlement terms include a 60-day PPW.",
        },
        {
          term: "RFQ (Request for Quotation / Order to Quote)",
          category: "Capacity & Placing",
          context:
            "Received RFQ under freshly executed BOR authorization.",
        },
        {
          term: "Slip",
          category: "Contract Documentation",
          context:
            "Placing slip presented to Lloyd's market for capacity.",
        },
        {
          term: "Slip Scratch",
          category: "Contract Documentation",
          context:
            "Broker obtaining lead underwriter slip scratch in The Room.",
        },
        {
          term: "Subjectivity",
          category: "Underwriting Conditions",
          context:
            "Continuous calibrated temperature data logger records required.",
        },
        {
          term: "Syndicate",
          category: "Regulatory & Compliance",
          context:
            "Approaching subscribing Lloyd's syndicates for terms.",
        },
        {
          term: "The Room",
          category: "Regulatory & Compliance",
          context:
            "Underwriting presentation at One Lime Street in The Room.",
        },
        {
          term: "Written Line",
          category: "Capacity & Placing",
          context:
            "Seeking lead underwriter agreement for initial written line.",
        },
      ],
      subjectivities_and_warranties: [
        "Continuous calibrated temperature data logger records on active " +
          "pharmaceutical shipments",
      ],
      recommended_actions: [
        "Advise recommended leading syndicate underwriters for the " +
          "initial written line.",
      ],
      classification_suggestion: "Marine Cargo",
      provider: "OpenRouter (local file)",
      mode: "live_ai_gateway",
    },
  };

  const state = {
    glossary: [],
    defaultGlossary: [],
    selectedTermIndex: 0,
    buckets: {},
    sampleEmails: [],
    lastJevResult: PRELOADED_RESULTS.jev,
    lastLunaResult: PRELOADED_RESULTS.luna,
    lastJevPrompt: "",
    lastLunaPrompt: "",
    currentView: "both", // "both", "jev", or "luna"
    activePromptTab: "jev",
    classifiedEmailId: "sample_marine_slip",
    classifiedEmailBody: "",
  };

  const el = {};

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    cacheElements();
    attachListeners();
    await fetchBackendData();
    initGlossary();
    renderDirectory();
    populatePresetDropdown();
    loadPreloadedAnalysis();
  }

  function cacheElements() {
    // Header elements
    el.glossaryHeaderCount = document.getElementById("glossary-header-count");
    el.statusText = document.getElementById("status-text");
    el.btnInspectPrompt = document.getElementById("btn-inspect-prompt");

    // Glossary elements
    el.glossarySearchInput = document.getElementById("glossary-search-input");
    el.glossaryCategoryFilter = document.getElementById(
      "glossary-category-filter"
    );
    el.directoryCountBadge = document.getElementById("directory-count-badge");
    el.glossaryItemsList = document.getElementById("glossary-items-list");
    el.directoryFooterHint = document.getElementById("directory-footer-hint");

    // Email intake elements
    el.presetSelect = document.getElementById("preset-select");
    el.scenarioBadge = document.getElementById("scenario-badge");
    el.inputFrom = document.getElementById("input-from");
    el.inputTo = document.getElementById("input-to");
    el.inputSubject = document.getElementById("input-subject");
    el.inputBody = document.getElementById("input-body");
    el.btnClearForm = document.getElementById("btn-clear-form");

    // Reclassification controls
    el.btnReclassify = document.getElementById("btn-reclassify");
    el.reclassifyBtnText = document.getElementById("reclassify-btn-text");
    el.reclassifySpinner = document.getElementById("reclassify-spinner");

    // Results dashboard elements
    el.toggleViewBoth = document.getElementById("toggle-view-both");
    el.toggleViewJev = document.getElementById("toggle-view-jev");
    el.toggleViewLuna = document.getElementById("toggle-view-luna");
    el.resultsEmptyView = document.getElementById("results-empty-view");
    el.dualResultsContainer = document.getElementById("dual-results-container");
    el.jevCard = document.getElementById("jev-card");
    el.lunaCard = document.getElementById("luna-card");

    // Jev card DOM
    el.jevLeadName = document.getElementById("jev-lead-name");
    el.jevLeadProb = document.getElementById("jev-lead-prob");
    el.jevConfidenceTier = document.getElementById("jev-confidence-tier");
    el.jevRationale = document.getElementById("jev-rationale");
    el.jevDistributionTbody = document.getElementById("jev-distribution-tbody");

    // Luna card DOM
    el.lunaSummaryBody = document.getElementById("luna-summary-body");
    el.lunaMetaInsured = document.getElementById("luna-meta-insured");
    el.lunaMetaCob = document.getElementById("luna-meta-cob");
    el.lunaMetaRef = document.getElementById("luna-meta-ref");
    el.lunaMetaLimit = document.getElementById("luna-meta-limit");
    el.lunaJargonChipsGrid = document.getElementById("luna-jargon-chips-grid");
    el.lunaSubjsList = document.getElementById("luna-subjs-list");
    el.lunaActionsList = document.getElementById("luna-actions-list");

    // Prompt modal DOM
    el.promptModal = document.getElementById("prompt-modal");
    el.btnClosePrompt = document.getElementById("btn-close-prompt");
    el.tabPromptJev = document.getElementById("tab-prompt-jev");
    el.tabPromptLuna = document.getElementById("tab-prompt-luna");
    el.promptContentView = document.getElementById("prompt-content-view");
  }

  function attachListeners() {
    // Glossary toolbar
    el.glossarySearchInput.addEventListener("input", renderDirectory);
    el.glossaryCategoryFilter.addEventListener("change", renderDirectory);

    // Email intake controls
    el.presetSelect.addEventListener("change", onPresetSelect);
    el.btnClearForm.addEventListener("click", clearEmailForm);
    el.inputBody.addEventListener("input", handleEmailBodyInput);
    el.inputBody.addEventListener("paste", handleEmailBodyPaste);
    el.inputBody.addEventListener("change", handleEmailBodyChange);

    // Reclassify button
    if (el.btnReclassify) {
      el.btnReclassify.addEventListener("click", runDualClassification);
    }

    // Quick chips
    document.querySelectorAll(".quick-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        const presetId = btn.getAttribute("data-preset");
        if (presetId) {
          loadPresetById(presetId);
          if (presetId !== state.classifiedEmailId) {
            blankOutClassificationDetails();
          }
        }
      });
    });

    // View switcher toggles
    el.toggleViewBoth.addEventListener("click", () => setResultsView("both"));
    el.toggleViewJev.addEventListener("click", () => setResultsView("jev"));
    el.toggleViewLuna.addEventListener("click", () => setResultsView("luna"));

    // Prompt modal controls (guarded if hidden)
    if (el.btnInspectPrompt) {
      el.btnInspectPrompt.addEventListener("click", showPromptModal);
    }
    el.btnClosePrompt.addEventListener("click", () => {
      el.promptModal.hidden = true;
      el.promptModal.style.display = "none";
    });
    el.promptModal.addEventListener("click", (evt) => {
      if (evt.target === el.promptModal) {
        el.promptModal.hidden = true;
        el.promptModal.style.display = "none";
      }
    });
    el.tabPromptJev.addEventListener("click", () => switchPromptTab("jev"));
    el.tabPromptLuna.addEventListener("click", () => switchPromptTab("luna"));
  }

  async function fetchBackendData() {
    try {
      const resp = await fetch(API_BASE + "/api/classifier/data");
      if (!resp.ok) throw new Error("HTTP error " + resp.status);
      const data = await resp.json();

      state.buckets = data.buckets || {};
      state.defaultGlossary = data.glossary || [];
      state.sampleEmails = (data.sample_emails || []).map((e) => ({
        ...e,
        body: cleanEmailContent(e.body),
      }));
    } catch (err) {
      console.warn(
        "Failed to fetch backend data, using fallback defaults:",
        err
      );
      state.defaultGlossary = [];
      state.sampleEmails = [];
    }
  }

  function initGlossary() {
    // Fixed dictionary of existing items; no additions or removals.
    state.glossary = JSON.parse(JSON.stringify(state.defaultGlossary));
    updateGlossaryCountHeader();
  }

  function updateGlossaryCountHeader() {
    const count = state.glossary.length;
    if (el.glossaryHeaderCount) {
      el.glossaryHeaderCount.textContent = count;
    }
  }

  function getCategoryClass(category) {
    const c = (category || "").toLowerCase();
    if (c.includes("contract")) return "cat-contract";
    if (c.includes("capacity") || c.includes("placing")) return "cat-capacity";
    if (c.includes("underwriting") || c.includes("condition")) {
      return "cat-underwriting";
    }
    if (c.includes("claims") || c.includes("loss")) return "cat-claims";
    if (c.includes("reinsurance") || c.includes("treaty")) {
      return "cat-reinsurance";
    }
    if (c.includes("regulatory") || c.includes("compliance")) {
      return "cat-regulatory";
    }
    if (c.includes("servicing") || c.includes("endorsement")) {
      return "cat-servicing";
    }
    return "cat-contract";
  }

  function getFilteredGlossary() {
    const query = (el.glossarySearchInput.value || "").trim().toLowerCase();
    const catFilter = (el.glossaryCategoryFilter.value || "")
      .trim()
      .toLowerCase();

    return state.glossary
      .map((item, idx) => ({ ...item, originalIndex: idx }))
      .filter((item) => {
        const matchesCat =
          !catFilter || item.category.toLowerCase() === catFilter;
      if (!matchesCat) return false;
      if (!query) return true;
      return (
        item.term.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query) ||
        item.definition.toLowerCase().includes(query) ||
        (item.example && item.example.toLowerCase().includes(query))
      );
    });
  }

  function renderDirectory() {
    const filtered = getFilteredGlossary();
    el.directoryCountBadge.textContent =
      `${filtered.length} of ${state.glossary.length}`;
    el.glossaryItemsList.innerHTML = "";

    if (filtered.length === 0) {
      el.glossaryItemsList.innerHTML =
        '<div style="padding:1.5rem; text-align:center; ' +
        'color:var(--text-muted); font-size:0.85rem;">' +
        'No matching terms found. Adjust your search or filter ' +
        'criteria.</div>';
      return;
    }

    filtered.forEach((item) => {
      const card = document.createElement("div");
      card.className = "glossary-item-card" +
        (item.originalIndex === state.selectedTermIndex ? " active" : "");
      card.setAttribute("role", "option");
      card.setAttribute(
        "aria-selected",
        item.originalIndex === state.selectedTermIndex ? "true" : "false"
      );

      const top = document.createElement("div");
      top.className = "card-top-line";

      const name = document.createElement("span");
      name.className = "card-term-name";
      name.textContent = item.term;

      const catChip = document.createElement("span");
      catChip.className = "cat-chip " + getCategoryClass(item.category);
      catChip.textContent = item.category;

      top.appendChild(name);
      top.appendChild(catChip);

      const defn = document.createElement("div");
      defn.className = "card-defn-snippet";
      defn.textContent = item.definition;

      card.appendChild(top);
      card.appendChild(defn);

      card.addEventListener("click", () =>
        selectTermByIndex(item.originalIndex)
      );
      el.glossaryItemsList.appendChild(card);
    });
  }

  function selectTermByIndex(idx) {
    if (idx < 0 || idx >= state.glossary.length) return;
    state.selectedTermIndex = idx;
    renderDirectoryHighlight();
  }

  function renderDirectoryHighlight() {
    const cards = el.glossaryItemsList.querySelectorAll(
      ".glossary-item-card"
    );
    const filtered = getFilteredGlossary();
    cards.forEach((card, i) => {
      const item = filtered[i];
      if (item && item.originalIndex === state.selectedTermIndex) {
        card.classList.add("active");
        card.setAttribute("aria-selected", "true");
      } else {
        card.classList.remove("active");
        card.setAttribute("aria-selected", "false");
      }
    });
  }

  function cleanEmailContent(text) {
    if (!text) return "";
    let s = String(text);

    // Step 1: Unescape literal newline and tab escape sequences
    s = s
      .replace(/\\r\\n/g, "\n")
      .replace(/\\n/g, "\n")
      .replace(/\\t/g, "  ");

    // Step 2: Convert and strip HTML markup if present
    if (/<(?:p|br|div|table|html|body|h[1-6]|li)\b[^>]*>/i.test(s)) {
      s = s.replace(/<br\s*[\/]?>/gi, "\n");
      s = s.replace(/<\/(?:p|div|tr|li|h[1-6])>/gi, "\n");
      s = s.replace(/<[^>]+>/g, "");
      s = s
        .replace(/&nbsp;/gi, " ")
        .replace(/&amp;/gi, "&")
        .replace(/&lt;/gi, "<")
        .replace(/&gt;/gi, ">")
        .replace(/&quot;/gi, '"')
        .replace(/&#39;/gi, "'");
    }

    // Step 3: Normalise consecutive blank lines
    s = s.replace(/\n{3,}/g, "\n\n").trim();
    return s;
  }

  function handleEmailBodyPaste(evt) {
    const clipboard = evt.clipboardData;
    if (!clipboard) return;

    const html = clipboard.getData("text/html");
    const plain = clipboard.getData("text/plain");

    // Intercept when HTML from email client or escape characters are pasted
    if (html && /<(?:p|br|div|table|body|h[1-6]|li)\b/i.test(html)) {
      evt.preventDefault();
      const cleaned = cleanEmailContent(html);
      insertTextAtCursor(el.inputBody, cleaned);
    } else if (
      plain &&
      (plain.includes("\\n") || /<[a-z][\s\S]*>/i.test(plain))
    ) {
      evt.preventDefault();
      const cleaned = cleanEmailContent(plain);
      insertTextAtCursor(el.inputBody, cleaned);
    }
    blankOutClassificationDetails();
  }

  function handleEmailBodyChange() {
    const val = el.inputBody.value;
    if (val.includes("\\n") || /<(?:p|br|div|table)\b/i.test(val)) {
      el.inputBody.value = cleanEmailContent(val);
    }
    if (el.inputBody.value !== state.classifiedEmailBody) {
      blankOutClassificationDetails();
    }
  }

  function handleEmailBodyInput() {
    if (el.inputBody.value !== state.classifiedEmailBody) {
      blankOutClassificationDetails();
    }
  }

  function blankOutClassificationDetails() {
    state.lastJevResult = null;
    state.lastLunaResult = null;
    state.lastJevPrompt = "";
    state.lastLunaPrompt = "";

    if (el.dualResultsContainer) {
      el.dualResultsContainer.hidden = true;
    }
    if (el.resultsEmptyView) {
      el.resultsEmptyView.hidden = false;
    }
  }

  function insertTextAtCursor(textarea, text) {
    const start = textarea.selectionStart || 0;
    const end = textarea.selectionEnd || 0;
    const current = textarea.value || "";
    textarea.value =
      current.substring(0, start) + text + current.substring(end);
    textarea.selectionStart = textarea.selectionEnd = start + text.length;
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
  }

  /* Pre-prepared Scenarios */
  function populatePresetDropdown() {
    if (state.sampleEmails.length > 0) {
      el.presetSelect.innerHTML =
        '<option value="">-- Choose a Pre-Prepared Example Email --</option>';
      state.sampleEmails.forEach((email, idx) => {
        const opt = document.createElement("option");
        opt.value = email.id;
        opt.textContent = `${idx + 1}. ${email.title}`;
        if (email.id === "sample_marine_slip") {
          opt.selected = true;
        }
        el.presetSelect.appendChild(opt);
      });
      loadPresetById("sample_marine_slip");
    }
  }

  function loadPreloadedAnalysis() {
    state.lastJevResult = PRELOADED_RESULTS.jev;
    state.lastLunaResult = PRELOADED_RESULTS.luna;
    state.lastJevPrompt = PRELOADED_RESULTS.jev.prompt || "";
    state.lastLunaPrompt = PRELOADED_RESULTS.luna.prompt || "";
    state.classifiedEmailId = "sample_marine_slip";
    state.classifiedEmailBody = el.inputBody.value;

    el.resultsEmptyView.hidden = true;
    el.dualResultsContainer.hidden = false;

    renderJevCard(PRELOADED_RESULTS.jev);
    renderLunaCard(PRELOADED_RESULTS.luna);
    setResultsView(state.currentView);
  }

  function onPresetSelect() {
    const id = el.presetSelect.value;
    if (!id) {
      clearEmailForm();
      return;
    }
    loadPresetById(id);
    if (id !== state.classifiedEmailId) {
      blankOutClassificationDetails();
    }
  }

  function loadPresetById(id) {
    const found = state.sampleEmails.find((e) => e.id === id);
    if (found) {
      el.presetSelect.value = found.id;
      el.inputFrom.value = found.sender || "";
      el.inputTo.value = found.recipient || "";
      el.inputSubject.value = found.subject || "";
      el.inputBody.value = cleanEmailContent(found.body || "");
      el.scenarioBadge.textContent = `Scenario: ${found.title}`;
    }
  }

  function clearEmailForm() {
    el.inputFrom.value = "";
    el.inputTo.value = "";
    el.inputSubject.value = "";
    el.inputBody.value = "";
    el.presetSelect.value = "";
    el.scenarioBadge.textContent = "Custom Email Intake";
    blankOutClassificationDetails();
    el.inputFrom.focus();
  }

  /* Dual Model Evaluation */
  async function runDualClassification() {
    const rawBody = el.inputBody.value.trim();
    if (!rawBody) {
      alert("Please select an example email or enter email content.");
      el.inputBody.focus();
      return;
    }

    const body = cleanEmailContent(rawBody);
    el.inputBody.value = body;

    setLoading(true);

    const payload = {
      email: {
        sender: el.inputFrom.value.trim(),
        recipient: el.inputTo.value.trim(),
        subject: el.inputSubject.value.trim(),
        body: body,
      },
      glossary_override: state.glossary,
      model_choice: "both",
    };

    try {
      const resp = await fetch(API_BASE + "/api/classifier/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) throw new Error("HTTP error " + resp.status);
      const data = await resp.json();
      if (!data.ok) throw new Error(data.error || "Email evaluation failed");

      state.lastJevResult = data.jev;
      state.lastLunaResult = data.luna;
      state.lastJevPrompt = data.jev ? data.jev.prompt || "" : "";
      state.lastLunaPrompt = data.luna ? data.luna.prompt || "" : "";
      state.classifiedEmailId = el.presetSelect.value || "custom";
      state.classifiedEmailBody = el.inputBody.value;

      el.resultsEmptyView.hidden = true;
      el.dualResultsContainer.hidden = false;

      if (data.jev) renderJevCard(data.jev);
      if (data.luna) renderLunaCard(data.luna);

      setResultsView(state.currentView);
    } catch (err) {
      alert("Evaluation failed: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  function setLoading(loading) {
    if (el.btnReclassify) {
      el.btnReclassify.disabled = loading;
    }
    if (el.reclassifySpinner) {
      el.reclassifySpinner.hidden = !loading;
    }
    if (el.reclassifyBtnText) {
      el.reclassifyBtnText.textContent = loading
        ? "Reclassifying..."
        : "\u25BA Reclassify";
    }
  }

  function setResultsView(view) {
    state.currentView = view;
    el.toggleViewBoth.className =
      "view-toggle-btn" + (view === "both" ? " active" : "");
    el.toggleViewJev.className =
      "view-toggle-btn" + (view === "jev" ? " active" : "");
    el.toggleViewLuna.className =
      "view-toggle-btn" + (view === "luna" ? " active" : "");

    if (!state.lastJevResult && !state.lastLunaResult) return;

    if (view === "both") {
      el.jevCard.hidden = false;
      el.lunaCard.hidden = false;
    } else if (view === "jev") {
      el.jevCard.hidden = false;
      el.lunaCard.hidden = true;
    } else if (view === "luna") {
      el.jevCard.hidden = true;
      el.lunaCard.hidden = false;
    }
  }

  function renderJevCard(res) {
    const topCode = res.top_bucket;
    const bucketObj = state.buckets[topCode] || {};
    el.jevLeadName.textContent = bucketObj.name || topCode;

    const probVal = res.confidence !== undefined ? res.confidence : 0.0;
    el.jevLeadProb.textContent = `${(probVal * 100).toFixed(1)}%`;
    el.jevConfidenceTier.textContent =
      `Confidence: ${res.confidence_tier || "High"}`;
    el.jevRationale.textContent = res.rationale ||
      "Categorised based on message context and London market terminology.";

    // Render 14-Register Distribution Table
    el.jevDistributionTbody.innerHTML = "";
    const probs = res.probabilities || {};
    const entries = Object.entries(probs).sort((a, b) => b[1] - a[1]);

    entries.forEach(([code, prob]) => {
      const bObj = state.buckets[code] || {};
      const tr = document.createElement("tr");

      const tdName = document.createElement("td");
      tdName.textContent = bObj.name || code;
      if (code === topCode) {
        tdName.style.fontWeight = "700";
        tdName.style.color = "#79c0ff";
      }

      const tdProb = document.createElement("td");
      tdProb.textContent = `${(prob * 100).toFixed(1)}%`;
      tdProb.style.fontFamily = "ui-monospace, monospace";
      if (code === topCode) {
        tdProb.style.fontWeight = "700";
        tdProb.style.color = "var(--ok)";
      }

      const tdMeter = document.createElement("td");
      const track = document.createElement("div");
      track.className = "bar-track";
      const fill = document.createElement("div");
      fill.className = "bar-fill" + (code === topCode ? " lead-fill" : "");
      fill.style.width = `${Math.min(100, Math.max(0, prob * 100))}%`;
      track.appendChild(fill);
      tdMeter.appendChild(track);

      tr.appendChild(tdName);
      tr.appendChild(tdProb);
      tr.appendChild(tdMeter);
      el.jevDistributionTbody.appendChild(tr);
    });
  }

  function renderLunaCard(res) {
    el.lunaSummaryBody.textContent =
      res.executive_summary || "Executive summary generated.";

    const meta = res.deal_metadata || {};
    el.lunaMetaInsured.textContent = meta.insured || "Identified in text";
    el.lunaMetaCob.textContent = meta.class_of_business || "Specialty Lines";
    el.lunaMetaRef.textContent = meta.policy_or_risk_reference || "PL-Pending";
    el.lunaMetaLimit.textContent =
      meta.limit_or_sum_insured ||
      meta.sender_organisation ||
      "Standard Market Line";

    // Jargon Chips
    el.lunaJargonChipsGrid.innerHTML = "";
    const jargonList = res.jargon_detected || [];
    if (jargonList.length === 0) {
      el.lunaJargonChipsGrid.innerHTML =
        '<span style="font-size:0.82rem; color:var(--text-muted);">' +
        'No specialised London market terms identified.</span>';
    } else {
      jargonList.forEach((j) => {
        const chip = document.createElement("span");
        chip.className = "jargon-chip";
        chip.textContent = j.term;
        const catPrefix = j.category ? `[${j.category}] ` : "";
        chip.title = `${catPrefix}${j.definition || j.context || ""}`;
        el.lunaJargonChipsGrid.appendChild(chip);
      });
    }

    // Subjectivities
    el.lunaSubjsList.innerHTML = "";
    const subjs = res.subjectivities_and_warranties || [];
    if (subjs.length === 0) {
      el.lunaSubjsList.innerHTML = "<li>None flagged in message text.</li>";
    } else {
      subjs.forEach((s) => {
        const li = document.createElement("li");
        li.textContent = s;
        el.lunaSubjsList.appendChild(li);
      });
    }

    // Actions
    el.lunaActionsList.innerHTML = "";
    const actions = res.recommended_actions || [];
    if (actions.length === 0) {
      el.lunaActionsList.innerHTML =
        "<li>Awaiting placement triage disposition.</li>";
    } else {
      actions.forEach((a) => {
        const li = document.createElement("li");
        li.textContent = a;
        el.lunaActionsList.appendChild(li);
      });
    }
  }

  /* Prompt Modal */
  function showPromptModal() {
    switchPromptTab(state.activePromptTab || "jev");
    el.promptModal.hidden = false;
    el.promptModal.style.display = "flex";
  }

  function switchPromptTab(tab) {
    state.activePromptTab = tab;
    el.tabPromptJev.className =
      "prompt-tab-btn" + (tab === "jev" ? " active" : "");
    el.tabPromptLuna.className =
      "prompt-tab-btn" + (tab === "luna" ? " active" : "");

    if (tab === "jev") {
      el.promptContentView.textContent =
        state.lastJevPrompt ||
        "Click 'Reclassify' to view active routing instructions.";
    } else {
      el.promptContentView.textContent =
        state.lastLunaPrompt ||
        "Click 'Reclassify' to view active briefing instructions.";
    }
  }
})();
