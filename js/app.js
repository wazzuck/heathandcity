/**
 * ============================================================================
 * FILE: js/app.js
 * ============================================================================
 *
 * PURPOSE:
 * Primary User Interface (UI) controller for the Hampstead and North West (NW)
 * London consulting showcase website. Coordinates brand token injection, the
 * Three-Dimensional (3D) Web Graphics Processing Unit (WebGPU) and Three.js
 * scene switcher, the four-vertical "One Clean Daily Screen" simulator,
 * senior readability controls, and the interactive value calculator.
 *
 * WHAT THIS FILE IS NOT FOR:
 * - Does not contain raw shader code (delegated to js/gpu-scene.js).
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
  SCENE_MODES,
  VERTICAL_DEMOS,
  SPECIALIST_ROLES,
  PRICING_STEPS
} from "./config.js";
import { GPUSceneController } from "./gpu-scene.js";

/**
 * Step 1: Define calculator multipliers for the Practice Recovery Estimator.
 * Maps each vertical identifier to hourly value and annual leakage rate.
 * Units: hourlyRateGbp in Pounds Sterling (£/hour); leakageFactor as a
 * dimensionless fraction of fee volume recovered or protected.
 * Consumed by: updateCalculator().
 */
const CALCULATOR_PROFILES = Object.freeze({
  insurance: {
    label: "Boutique Insurance / Mortgage Brokerage",
    hourlyRateGbp: 185,
    leakageFactor: 0.035,
    efficiencyGain: 0.72,
    note:
      "Reflects automated renewal retention, underwriter chaser tracking, " +
      "and elimination of manual Outlook thread forwarding."
  },
  medical: {
    label: "Senior Medical Consultant / Medico-Legal Practice",
    hourlyRateGbp: 550,
    leakageFactor: 0.065,
    efficiencyGain: 0.78,
    note:
      "Reflects automated 2,000-page PDF bundle chronology extraction plus " +
      "recovery of under-reimbursed Bupa, AXA, and Vitality procedures."
  },
  legal: {
    label: "King's Counsel (KC) / Arbitrator / Boutique Law Partner",
    hourlyRateGbp: 600,
    leakageFactor: 0.04,
    efficiencyGain: 0.75,
    note:
      "Reflects instant 20-year private precedent retrieval and automated " +
      "financial disclosure discrepancy detection across PDF bundles."
  },
  family_office: {
    label: "Family Office / Multi-SPV Property Principal",
    hourlyRateGbp: 420,
    leakageFactor: 0.045,
    efficiencyGain: 0.8,
    note:
      "Reflects multi-bank PDF statement normalisation and 90/60/30-day " +
      "commercial lease-break, rent review, and compliance protection."
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
 * Step 3: Render the four Specialist Roles cards from SPECIALIST_ROLES.
 */
function renderSpecialistRoles() {
  const container = document.getElementById("specialist-roles-grid");
  if (!container) {
    return;
  }
  container.innerHTML = "";

  SPECIALIST_ROLES.forEach((item) => {
    const card = document.createElement("article");
    card.className = "role-card";
    card.innerHTML = `
      <div class="role-card__header">
        <span class="role-card__number">ROLE ${item.number}</span>
        <span class="role-card__tag">${item.architectureTag}</span>
      </div>
      <h3 class="role-card__title">${item.role}</h3>
      <p class="role-card__best-for">
        <strong>Designed for:</strong> ${item.bestFor}
      </p>
      <blockquote class="role-card__pitch">"${item.pitch}"</blockquote>
    `;
    container.appendChild(card);
  });
}

/**
 * Step 4: Render the Three-Step Pricing Architecture cards from PRICING_STEPS.
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
 * Step 5: Render the selected vertical inside the interactive "One Clean Daily
 * Screen" simulator and synchronise the 3D GPU showcase mode.
 *
 * @param {string} verticalId - Key in VERTICAL_DEMOS.
 * @param {GPUSceneController} [gpuController] - Active 3D controller instance.
 * @param {boolean} [syncScene=true] - Whether to switch the 3D scene mode.
 */
function selectVerticalDemo(verticalId, gpuController, syncScene = true) {
  const demo = VERTICAL_DEMOS[verticalId];
  if (!demo) {
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

  // 5. Optionally synchronise the 3D GPU showcase mode.
  if (syncScene && gpuController && demo.sceneMode) {
    activateSceneModeUI(demo.sceneMode, gpuController);
  }
}

/**
 * Step 6: Update the 3D Multi-Scene Showcase UI panel and notify the
 * GPUSceneController when the visitor switches between "lattice", "vault",
 * and "telemetry".
 *
 * @param {string} modeId - Scene identifier ("lattice", "vault", "telemetry").
 * @param {GPUSceneController} gpuController - Active 3D controller instance.
 */
function activateSceneModeUI(modeId, gpuController) {
  const mode = SCENE_MODES[modeId];
  if (!mode) {
    return;
  }

  // 1. Highlight the active scene mode button.
  document.querySelectorAll("[data-scene-mode]").forEach((btn) => {
    const active = btn.getAttribute("data-scene-mode") === modeId;
    btn.classList.toggle("is-active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });

  // 2. Update the overlay caption and technical telemetry readout.
  const titleEl = document.getElementById("scene-caption-title");
  const subEl = document.getElementById("scene-caption-subtitle");
  const noteEl = document.getElementById("scene-caption-note");
  const pipeEl = document.getElementById("telemetry-pipeline");
  const speedEl = document.getElementById("telemetry-throughput");
  const egressEl = document.getElementById("telemetry-egress");

  if (titleEl) titleEl.textContent = mode.title;
  if (subEl) subEl.textContent = mode.subtitle;
  if (noteEl) noteEl.textContent = mode.technicalNote;
  if (pipeEl) pipeEl.textContent = mode.metrics.pipeline;
  if (speedEl) speedEl.textContent = mode.metrics.throughput;
  if (egressEl) egressEl.textContent = mode.metrics.egress;

  // 3. Synchronise the Entropy-to-Order slider value.
  const slider = document.getElementById("order-slider");
  const sliderVal = document.getElementById("order-slider-value");
  const pct = Math.round(mode.defaultOrder * 100);
  if (slider) {
    slider.value = String(pct);
  }
  if (sliderVal) {
    sliderVal.textContent = `${pct}% Order`;
  }

  // 4. Instruct the GPU controller to transition smoothly to the new topology.
  if (gpuController) {
    gpuController.setMode(modeId, true);
  }
}

/**
 * Step 7: Initialise the Senior Readability & Comfort controls (Large Type
 * A/A+ toggle and High-Contrast Warm Parchment / Sovereign Vault Dark toggle).
 */
function initReadabilityControls() {
  const fontBtn = document.getElementById("toggle-font-size");
  const themeBtn = document.getElementById("toggle-theme-mode");

  // 1. Restore saved preferences from localStorage if available.
  try {
    if (localStorage.getItem("hc_large_type") === "1") {
      document.documentElement.classList.add("large-type");
      if (fontBtn) fontBtn.setAttribute("aria-pressed", "true");
    }
    if (localStorage.getItem("hc_theme") === "parchment") {
      document.documentElement.setAttribute("data-theme", "parchment");
      if (themeBtn) {
        themeBtn.setAttribute("aria-pressed", "true");
        themeBtn.textContent = "Theme: Warm Paper";
      }
    }
  } catch (_err) {
    // Ignore storage errors in private browsing modes.
  }

  // 2. Bind Large Type (A / A+) button.
  if (fontBtn) {
    fontBtn.addEventListener("click", () => {
      const enabled = document.documentElement.classList.toggle("large-type");
      fontBtn.setAttribute("aria-pressed", enabled ? "true" : "false");
      fontBtn.textContent = enabled ? "Text Size: A+ (Large)" : "Text Size: A / A+";
      try {
        localStorage.setItem("hc_large_type", enabled ? "1" : "0");
      } catch (_err) {
        // Ignore storage errors.
      }
    });
  }

  // 3. Bind Theme Mode (Sovereign Night vs Warm Parchment Day) button.
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const nextTheme = current === "parchment" ? "vault" : "parchment";
      if (nextTheme === "parchment") {
        document.documentElement.setAttribute("data-theme", "parchment");
        themeBtn.setAttribute("aria-pressed", "true");
        themeBtn.textContent = "Theme: Warm Paper";
      } else {
        document.documentElement.removeAttribute("data-theme");
        themeBtn.setAttribute("aria-pressed", "false");
        themeBtn.textContent = "Theme: Vault Dark";
      }
      try {
        localStorage.setItem("hc_theme", nextTheme);
      } catch (_err) {
        // Ignore storage errors.
      }
    });
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
      CALCULATOR_PROFILES.insurance;
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
      "Step 1 Read-Only Inbox & Workflow Audit (£750–£1,500)";

    const subject = `Private Consultation (${postcode}) — ${practice}`;
    const body = [
      `Dear Principal Architect (${SITE_CONFIG.brandName}),`,
      "",
      `I would like to arrange a discreet 20-minute coffee or on-site discussion in ${postcode}.`,
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
async function bootstrapApp() {
  // 1. Inject centralised brand tokens across the page.
  applyBrandConfig();

  // 2. Render dynamic Specialist Roles and Pricing Step cards.
  renderSpecialistRoles();
  renderPricingSteps();

  // 3. Initialise readability and theme controls.
  initReadabilityControls();

  // 4. Initialise the GPU 3D visual centrepiece controller.
  const canvas = document.getElementById("gpu-centrepiece-canvas");
  const engineBadge = document.getElementById("gpu-engine-badge");
  const fpsBadge = document.getElementById("gpu-fps-badge");
  const pauseBtn = document.getElementById("gpu-pause-btn");

  const gpuController = new GPUSceneController({
    canvas,
    onStatusChange: (status) => {
      if (engineBadge) {
        engineBadge.textContent = status.tierLabel;
      }
      if (fpsBadge) {
        fpsBadge.textContent = status.isPaused
          ? "STATIC MODE"
          : `${status.fps} FPS · ZERO COOP/COEP`;
      }
      if (pauseBtn) {
        pauseBtn.textContent = status.isPaused
          ? "Resume 3D Motion"
          : "Pause 3D Motion";
        pauseBtn.setAttribute(
          "aria-pressed",
          status.isPaused ? "true" : "false"
        );
      }
    }
  });

  await gpuController.init();

  // 5. Bind Multi-Scene Showcase mode buttons.
  document.querySelectorAll("[data-scene-mode]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modeId = btn.getAttribute("data-scene-mode");
      activateSceneModeUI(modeId, gpuController);
    });
  });

  // 6. Bind the live Entropy-to-Order slider and quick preset buttons.
  const orderSlider = document.getElementById("order-slider");
  const orderSliderVal = document.getElementById("order-slider-value");
  if (orderSlider) {
    orderSlider.addEventListener("input", () => {
      const pct = Number(orderSlider.value) || 0;
      if (orderSliderVal) {
        orderSliderVal.textContent = `${pct}% Order`;
      }
      gpuController.setOrderRatio(pct / 100.0);
    });
  }

  const chaosBtn = document.getElementById("btn-simulate-chaos");
  if (chaosBtn) {
    chaosBtn.addEventListener("click", () => {
      if (orderSlider) orderSlider.value = "8";
      if (orderSliderVal) orderSliderVal.textContent = "8% Order (Inbox Chaos)";
      gpuController.setOrderRatio(0.08);
      gpuController.triggerPulse();
    });
  }

  const orderBtn = document.getElementById("btn-simulate-order");
  if (orderBtn) {
    orderBtn.addEventListener("click", () => {
      if (orderSlider) orderSlider.value = "96";
      if (orderSliderVal) {
        orderSliderVal.textContent = "96% Order (Reconciled Ledger)";
      }
      gpuController.setOrderRatio(0.96);
      gpuController.triggerPulse();
    });
  }

  const pulseBtn = document.getElementById("btn-trigger-pulse");
  if (pulseBtn) {
    pulseBtn.addEventListener("click", () => {
      gpuController.triggerPulse();
    });
  }

  if (pauseBtn) {
    pauseBtn.addEventListener("click", () => {
      gpuController.toggleRunning();
    });
  }

  // 7. Bind the four-vertical "One Clean Daily Screen" tabs.
  document.querySelectorAll("[data-vertical-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const vId = btn.getAttribute("data-vertical-tab");
      selectVerticalDemo(vId, gpuController, true);
    });
  });

  // 8. Set initial scene and vertical states.
  activateSceneModeUI("lattice", gpuController);
  selectVerticalDemo("insurance", gpuController, false);

  // 9. Initialise the ROI calculator and consultation form builder.
  initRecoveryCalculator();
  initConsultationBuilder();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrapApp);
} else {
  bootstrapApp();
}
