/**
 * ============================================================================
 * FILE: js/app.js
 * ============================================================================
 *
 * PURPOSE:
 * Primary User Interface (UI) controller for the Hampstead and North West (NW)
 * London private practice website. Coordinates brand token injection, the
 * four-practice "A typical morning" demo, the interactive return estimator,
 * and the enquiry form builder.
 *
 * WHAT THIS FILE IS NOT FOR:
 * - Does not transmit user inputs to any external analytics or cloud server.
 *
 * INVARIANTS:
 * 1. All brand strings are populated from SITE_CONFIG in js/config.js.
 * 2. Every interactive control is keyboard accessible and updates Accessible
 *    Rich Internet Applications (ARIA) attributes synchronously.
 * 3. Customer-facing strings use British English conventions throughout.
 * ============================================================================
 */

import {
  SITE_CONFIG,
  VERTICAL_DEMOS,
  PRICING_STEPS
} from "./config.js?v=20261110d";

/**
 * Step 1: Define calculator multipliers for the Practice Recovery Estimator.
 * Maps each vertical identifier to hourly value and annual leakage rate.
 * Units: hourlyRateGbp in Pounds Sterling (£/hour); leakageFactor as a
 * dimensionless fraction of fee volume recovered or protected.
 * Consumed by: updateCalculator().
 */
const CALCULATOR_PROFILES = Object.freeze({
  legal: {
    label: "Barrister / King's Counsel",
    hourlyRateGbp: 600,
    leakageFactor: 0.04,
    efficiencyGain: 0.75,
    note:
      "Assumes faster precedent searches and fewer disclosure checks done by " +
      "hand. Use your own hourly rate to refine the estimate."
  },
  "family-office": {
    label: "Family Office / Private Trustee",
    hourlyRateGbp: 450,
    leakageFactor: 0.05,
    efficiencyGain: 0.76,
    note:
      "Assumes instant capital call tracking, faster trust reconciliations, " +
      "and reduced manual filing across multiple entities."
  },
  estate: {
    label: "Prime Estate Agent / Surveyor",
    hourlyRateGbp: 220,
    leakageFactor: 0.045,
    efficiencyGain: 0.7,
    note:
      "Assumes faster sales progression, fewer stalled solicitor replies, " +
      "and automated tracking of anti-money laundering paperwork."
  },
  insurance: {
    label: "Commercial Insurance Broker",
    hourlyRateGbp: 250,
    leakageFactor: 0.035,
    efficiencyGain: 0.72,
    note:
      "Assumes fewer missed renewals, fewer manual chasers, and less time " +
      "spent cross-checking underwriter policy wordings."
  },
  stockbrokers: {
    label: "Stockbroker / Wealth Manager",
    hourlyRateGbp: 350,
    leakageFactor: 0.04,
    efficiencyGain: 0.75,
    note:
      "Assumes instant contract note matching, zero custodian breaks, " +
      "and early notification of corporate actions."
  },
  accountants: {
    label: "Chartered Accountant / Tax Adviser",
    hourlyRateGbp: 280,
    leakageFactor: 0.04,
    efficiencyGain: 0.74,
    note:
      "Assumes automated chasing of missing client vouchers, faster " +
      "statutory cross-checks, and fewer deadline scrambles."
  },
  "it-support": {
    label: "IT Support Engineer / MSP",
    hourlyRateGbp: 150,
    leakageFactor: 0.05,
    efficiencyGain: 0.7,
    note:
      "Assumes faster ticket triage, fewer missed licence renewals, and " +
      "less time reconstructing an incident from email threads."
  },
  talent: {
    label: "Author, Composer or Creative Talent",
    hourlyRateGbp: 200,
    leakageFactor: 0.045,
    efficiencyGain: 0.72,
    note:
      "Assumes faster royalty statement reconciliations, automated tracking " +
      "of residuals, and fewer missed delivery deadlines."
  },
  galleries: {
    label: "Commercial Art Gallery or Dealer",
    hourlyRateGbp: 240,
    leakageFactor: 0.045,
    efficiencyGain: 0.7,
    note:
      "Assumes faster consignment reconciliations, automated tracking of " +
      "provenance files, and fewer missed artist resale deadlines."
  },
  medical: {
    label: "Surgeon / Consultant",
    hourlyRateGbp: 550,
    leakageFactor: 0.065,
    efficiencyGain: 0.78,
    note:
      "Assumes long bundles are read on-site and possible insurer " +
      "underpayments are flagged for recovery."
  }
});

/**
 * Step 2: Populate all Document Object Model (DOM) nodes carrying data-brand
 * attributes from SITE_CONFIG so the provisional To Be Confirmed (TBC) brand
 * can be updated in one place.
 */
function applyBrandConfig() {
  // 1. Map data attribute keys to SITE_CONFIG values.
  const bindings = {
    "brand-name": SITE_CONFIG.brandName,
    "brand-monogram": SITE_CONFIG.brandMonogram,
    "brand-badge": SITE_CONFIG.brandStatusBadge,
    "brand-tagline": SITE_CONFIG.brandTagline,
    "brand-role": SITE_CONFIG.principalRole,
    "brand-postcodes": SITE_CONFIG.primaryPostcodes,
    "brand-email": SITE_CONFIG.contactEmail,
    "brand-phone": SITE_CONFIG.contactPhoneDisplay,
    "brand-location": SITE_CONFIG.officeLocation,
    "brand-address": SITE_CONFIG.officeAddress,
    "brand-support-label": SITE_CONFIG.immediateSupportLabel
  };

  // 2. Write textContent into every matching element.
  Object.entries(bindings).forEach(([key, value]) => {
    const elements = document.querySelectorAll(`[data-${key}]`);
    elements.forEach((el) => {
      el.textContent = value;
    });
  });

  // 3. Update mailto and tel hyperlinks.
  document.querySelectorAll("[data-brand-email-link]").forEach((el) => {
    el.setAttribute(
      "href",
      `mailto:${SITE_CONFIG.contactEmail}?subject=` +
        encodeURIComponent(
          `Private Consultation Enquiry — ${SITE_CONFIG.brandName}`
        )
    );
  });

  document.querySelectorAll("[data-brand-phone-link]").forEach((el) => {
    el.setAttribute("href", `tel:${SITE_CONFIG.contactPhoneHref}`);
  });

  document.querySelectorAll("[data-brand-support-link]").forEach((el) => {
    el.setAttribute("href", SITE_CONFIG.immediateSupportSite);
  });

  // 4. Populate the neighbourhood coverage pills if container exists.
  const hoodContainer = document.getElementById("neighbourhood-pills");
  if (hoodContainer) {
    hoodContainer.innerHTML = "";
    SITE_CONFIG.neighbourhoods.forEach((name) => {
      const span = document.createElement("span");
      span.className = "postcode-pill";
      span.textContent = name;
      hoodContainer.appendChild(span);
    });
  }
}

/**
 * Step 3: Render the Three-Step Pricing Architecture cards from PRICING_STEPS.
 */
function renderPricingSteps() {
  const container = document.getElementById("pricing-steps-grid");
  if (!container) {
    return;
  }
  container.innerHTML = "";

  PRICING_STEPS.forEach((tier) => {
    const article = document.createElement("article");
    article.className =
      "pricing-card" + (tier.featured ? " pricing-card--featured" : "");

    const listHtml = tier.deliverables
      .map((d) => `<li class="pricing-card__item">${d}</li>`)
      .join("");

    article.innerHTML = `
      <div class="pricing-card__step">${tier.step}</div>
      <h3 class="pricing-card__title">${tier.title}</h3>
      <div class="pricing-card__price-row">
        <span class="pricing-card__price">${tier.price}</span>
        <span class="pricing-card__duration">${tier.duration}</span>
      </div>
      <p class="pricing-card__desc">${tier.description}</p>
      <ul class="pricing-card__list">${listHtml}</ul>
    `;
    container.appendChild(article);
  });
}

/**
 * Step 5: Render the selected practice type inside the "A typical morning"
 * demo panel.
 *
 * @param {string} verticalId - Key in VERTICAL_DEMOS.
 */
function selectVerticalDemo(verticalId) {
  const demo = VERTICAL_DEMOS[verticalId];
  if (!demo) {
    console.warn("Unknown vertical demo ID:", verticalId);
    return;
  }

  // 1. Update tab button active states and ARIA attributes.
  document.querySelectorAll("[data-vertical-tab]").forEach((btn) => {
    const isMatch = btn.getAttribute("data-vertical-tab") === verticalId;
    btn.classList.toggle("is-active", isMatch);
    btn.setAttribute("aria-selected", isMatch ? "true" : "false");
  });

  // 2. Populate header metadata inside the simulated daily screen.
  const badgeEl = document.getElementById("demo-screen-badge");
  const titleEl = document.getElementById("demo-screen-title");
  const summaryEl = document.getElementById("demo-screen-summary");
  const digestEl = document.getElementById("demo-screen-digest");
  const guaranteeEl = document.getElementById("demo-screen-guarantee");

  if (badgeEl) badgeEl.textContent = demo.badge;
  if (titleEl) titleEl.textContent = demo.headline;
  if (summaryEl) summaryEl.textContent = demo.summary;
  if (digestEl) digestEl.textContent = demo.digestTime;
  if (guaranteeEl) guaranteeEl.textContent = demo.guarantee;

  // 3. Populate top-level key performance indicators.
  const statsContainer = document.getElementById("demo-screen-stats");
  if (statsContainer) {
    statsContainer.innerHTML = demo.stats
      .map(
        (stat) => `
        <div class="screen-stat screen-stat--${stat.tone}">
          <span class="screen-stat__label">${stat.label}</span>
          <strong class="screen-stat__value">${stat.value}</strong>
        </div>
      `
      )
      .join("");
  }

  // 4. Populate the simulated priority queue items.
  const queueContainer = document.getElementById("demo-screen-queue");
  if (queueContainer) {
    queueContainer.innerHTML = demo.queueItems
      .map(
        (item) => `
        <div class="queue-row">
          <div class="queue-row__meta">
            <span class="queue-row__priority">${item.priority}</span>
            <span class="queue-row__timer">${item.timer}</span>
          </div>
          <div class="queue-row__main">
            <h4 class="queue-row__client">${item.client}</h4>
            <p class="queue-row__matter">${item.matter}</p>
          </div>
          <div class="queue-row__footer">
            <span class="queue-row__status">${item.status}</span>
            <code class="queue-row__ref">${item.sourceRef}</code>
          </div>
        </div>
      `
      )
      .join("");
  }

}

/**
 * Step 8: Initialise the interactive Practice Time & Revenue Recovery
 * Calculator so principals can quantify their Return on Investment (ROI).
 */
function initRecoveryCalculator() {
  const verticalSelect = document.getElementById("calc-vertical");
  const hoursInput = document.getElementById("calc-hours");
  const hoursDisplay = document.getElementById("calc-hours-display");
  const revenueInput = document.getElementById("calc-revenue");
  const revenueDisplay = document.getElementById("calc-revenue-display");

  const outHours = document.getElementById("calc-result-hours");
  const outValue = document.getElementById("calc-result-value");
  const outNote = document.getElementById("calc-result-note");

  if (!verticalSelect || !hoursInput || !revenueInput) {
    return;
  }

  function updateCalculator() {
    const profile =
      CALCULATOR_PROFILES[verticalSelect.value] ||
      CALCULATOR_PROFILES.legal;
    const weeklyHours = Number(hoursInput.value) || 10;
    const annualRevenueMillions = Number(revenueInput.value) || 1.2;

    if (hoursDisplay) {
      hoursDisplay.textContent = `${weeklyHours} hrs / week`;
    }
    if (revenueDisplay) {
      revenueDisplay.textContent = `£${annualRevenueMillions.toFixed(1)}m / yr`;
    }

    // 1. Compute annual hours reclaimed (48 working weeks per year).
    const annualHoursSaved = Math.round(
      weeklyHours * 48 * profile.efficiencyGain
    );

    // 2. Compute combined value of principal time saved + fee leakage/renewal
    //    protection, capped conservatively for credibility.
    const timeValueGbp = annualHoursSaved * profile.hourlyRateGbp;
    const protectedRevenueGbp =
      annualRevenueMillions * 1000000 * profile.leakageFactor * 0.45;
    const totalAnnualBenefit = Math.round(
      (timeValueGbp + protectedRevenueGbp) / 500
    ) * 500;

    if (outHours) {
      outHours.textContent = `${annualHoursSaved.toLocaleString("en-GB")} hrs / year`;
    }
    if (outValue) {
      outValue.textContent = `£${totalAnnualBenefit.toLocaleString("en-GB")} / year`;
    }
    if (outNote) {
      outNote.textContent = profile.note;
    }
  }

  verticalSelect.addEventListener("change", updateCalculator);
  hoursInput.addEventListener("input", updateCalculator);
  revenueInput.addEventListener("input", updateCalculator);
  updateCalculator();
}

/**
 * Step 9: Initialise the Private Hampstead Consultation & Audit Enquiry form.
 * Generates a formatted, zero-cloud local email or clipboard brief.
 */
function initConsultationBuilder() {
  const form = document.getElementById("audit-enquiry-form");
  const statusEl = document.getElementById("enquiry-status-message");
  const copyBtn = document.getElementById("copy-enquiry-btn");

  if (!form) {
    return;
  }

  function buildMessagePayload() {
    const name =
      (document.getElementById("enquiry-name") || {}).value ||
      "Senior Principal";
    const practice =
      (document.getElementById("enquiry-practice") || {}).value ||
      "NW London Practice";
    const postcode =
      (document.getElementById("enquiry-postcode") || {}).value || "NW3";
    const bottleneck =
      (document.getElementById("enquiry-bottleneck") || {}).value ||
      "Step 1: Two-week trial on my own documents (£750–£1,500)";

    const subject = `Private Consultation (${postcode}) — ${practice}`;
    const body = [
      `Hello ${SITE_CONFIG.brandName},`,
      "",
      `I would like to arrange a short, discreet coffee or on-site discussion in ${postcode}.`,
      "",
      `Principal / Partner: ${name}`,
      `Practice / Chambers: ${practice}`,
      `Primary Interest: ${bottleneck}`,
      "",
      "Kind regards,",
      name
    ].join("\n");

    return { subject, body };
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const { subject, body } = buildMessagePayload();
    const mailtoUrl =
      `mailto:${SITE_CONFIG.contactEmail}?subject=` +
      encodeURIComponent(subject) +
      `&body=` +
      encodeURIComponent(body);

    if (statusEl) {
      statusEl.textContent =
        "Opening your local email client with a pre-addressed private note " +
        "(zero data sent to any web server).";
    }
    window.location.href = mailtoUrl;
  });

  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const { subject, body } = buildMessagePayload();
      const fullText = `To: ${SITE_CONFIG.contactEmail}\nSubject: ${subject}\n\n${body}`;
      try {
        await navigator.clipboard.writeText(fullText);
        if (statusEl) {
          statusEl.textContent =
            "Enquiry details copied to your clipboard. Send at your convenience.";
        }
      } catch (_err) {
        if (statusEl) {
          statusEl.textContent = `Direct email: ${SITE_CONFIG.contactEmail}`;
        }
      }
    });
  }
}

/**
 * Step 10: Bootstrap the application once the DOM is ready.
 */
function bootstrapApp() {
  // 1. Inject centralised brand tokens across the page.
  applyBrandConfig();

  // 2. Render dynamic Pricing Step cards.
  renderPricingSteps();

  // 3. Bind the four-practice "A typical morning" tabs.
  document.querySelectorAll("[data-vertical-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const vId = btn.getAttribute("data-vertical-tab");
      selectVerticalDemo(vId);
    });
  });

  // 4. Show the default practice type.
  selectVerticalDemo("legal");

  // 5. Initialise the return estimator and consultation form builder.
  initRecoveryCalculator();
  initConsultationBuilder();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrapApp);
} else {
  bootstrapApp();
}
