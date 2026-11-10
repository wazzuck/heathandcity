/**
 * Sovereign Practice Vault - Frontend Application Controller.
 *
 * Coordinates user interactions across Document Intelligence, Practice Clerk
 * triage, and system archive administration. Zero third-party dependencies.
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSearch();
  initTriage();
  initArchive();
  initGoogleWorkspace();
  pollStatus();
  loadTasks();
  pollStatistics();
  pollJobs();
  pollGoogleSyncState();

  // Polling intervals for real-time status and telemetry.
  setInterval(pollStatus, 5000);
  setInterval(pollJobs, 2000);
  setInterval(pollStatistics, 5000);
  setInterval(pollGoogleSyncState, 5000);
});

/**
 * Configure tabbed navigation behaviour.
 */
function initTabs() {
  const navButtons = document.querySelectorAll(".nav-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      navButtons.forEach((b) => b.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

/**
 * Configure Document Intelligence query and search handlers.
 */
function initSearch() {
  const form = document.getElementById("search-form");
  const queryInput = document.getElementById("query-input");
  const btnSearchOnly = document.getElementById("btn-search-only");

  const answerContainer = document.getElementById("answer-container");
  const answerText = document.getElementById("answer-text");
  const citationsList = document.getElementById("citations-list");

  const resultsContainer = document.getElementById("search-results-container");
  const resultsList = document.getElementById("results-list");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    answerContainer.style.display = "block";
    resultsContainer.style.display = "none";
    answerText.textContent = "Synthesising deterministic answer from practice records...";
    citationsList.innerHTML = "";

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query, top_k: 5 }),
      });
      const data = await res.json();

      answerText.textContent = data.answer || "No response received.";
      citationsList.innerHTML = "";

      if (data.citations && data.citations.length > 0) {
        data.citations.forEach((c) => {
          const card = document.createElement("div");
          card.className = "citation-card";
          card.innerHTML = `
            <div class="citation-source">${escapeHtml(c.file_name)} (Page ${c.page_number})</div>
            <div class="citation-snippet">&ldquo;${escapeHtml(c.snippet)}&rdquo;</div>
          `;
          citationsList.appendChild(card);
        });
      } else {
        citationsList.innerHTML = "<p class='empty-state'>No specific citations required.</p>";
      }
    } catch (err) {
      answerText.textContent = `Error querying practice vault: ${err.message}`;
    }
  });

  btnSearchOnly.addEventListener("click", async () => {
    const query = queryInput.value.trim();
    if (!query) return;

    answerContainer.style.display = "none";
    resultsContainer.style.display = "block";
    resultsList.innerHTML = "<p class='empty-state'>Executing hybrid search across vault...</p>";

    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query, top_k: 8 }),
      });
      const data = await res.json();

      resultsList.innerHTML = "";
      if (data.results && data.results.length > 0) {
        data.results.forEach((r) => {
          const card = document.createElement("div");
          card.className = "citation-card";
          card.style.marginBottom = "0.75rem";
          card.innerHTML = `
            <div class="citation-source">${escapeHtml(r.file_name)} &bull; Page ${r.page_number} (RRF Score: ${r.rrf_score})</div>
            <div class="citation-snippet" style="font-style: normal; color: var(--text-main); margin-top: 0.35rem;">
              ${escapeHtml(r.text)}
            </div>
          `;
          resultsList.appendChild(card);
        });
      } else {
        resultsList.innerHTML = "<p class='empty-state'>No matching document records found.</p>";
      }
    } catch (err) {
      resultsList.innerHTML = `<p class='empty-state'>Search error: ${err.message}</p>`;
    }
  });
}

/**
 * Configure Practice Clerk triage submission.
 */
function initTriage() {
  const form = document.getElementById("triage-form");
  const subjectInput = document.getElementById("triage-subject");
  const senderInput = document.getElementById("triage-sender");
  const textInput = document.getElementById("triage-text");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const subject = subjectInput.value.trim();
    const sender = senderInput.value.trim();
    const rawText = textInput.value.trim();

    if (!subject || !rawText) return;

    try {
      const res = await fetch("/api/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: subject,
          sender: sender || "client@internal",
          raw_text: rawText,
        }),
      });

      if (res.ok) {
        form.reset();
        await loadTasks();
        await pollStatus();
      }
    } catch (err) {
      alert(`Error processing correspondence: ${err.message}`);
    }
  });
}

/**
 * Load and render active tasks and staged draft replies.
 */
async function loadTasks() {
  const tasksList = document.getElementById("tasks-list");
  try {
    const res = await fetch("/api/tasks");
    const data = await res.json();

    if (!data.tasks || data.tasks.length === 0) {
      tasksList.innerHTML = "<p class='empty-state'>No pending tasks staged. Process correspondence above.</p>";
      return;
    }

    tasksList.innerHTML = "";
    data.tasks.forEach((t) => {
      const item = document.createElement("div");
      item.className = "task-item";
      const urgencyClass = t.urgency.toLowerCase() === "urgent" ? "urgency-urgent" : "urgency-routine";

      item.innerHTML = `
        <div class="task-header">
          <div class="task-title">${escapeHtml(t.task_description)}</div>
          <span class="urgency-badge ${urgencyClass}">${escapeHtml(t.urgency)}</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">
          Matter: <strong>${escapeHtml(t.matter_reference)}</strong> &bull; Target: <strong>${escapeHtml(t.due_date)}</strong> &bull; Origin: ${escapeHtml(t.sender)}
        </div>
        <div class="draft-box">
          <div style="font-weight: 600; color: var(--gold-accent); margin-bottom: 0.25rem;">Staged Draft Response (Human Sign-off Required):</div>
          ${escapeHtml(t.draft_reply)}
        </div>
        <div class="task-actions">
          <button class="btn-primary" onclick="approveTask('${escapeHtml(t.intake_id)}')">Approve &amp; Finalise</button>
        </div>
      `;
      tasksList.appendChild(item);
    });
  } catch (err) {
    tasksList.innerHTML = `<p class='empty-state'>Failed to load tasks: ${err.message}</p>`;
  }
}

/**
 * Handle affirmative sign-off for staged draft replies.
 */
function approveTask(intakeId) {
  alert(`Matter action [${intakeId}] approved by principal. Staged for secure transmission.`);
}

/**
 * Configure archive ingestion controls and health updates.
 */
function initArchive() {
  const btnIngest = document.getElementById("btn-trigger-ingest");
  const btnRefresh = document.getElementById("btn-refresh-status");
  const feedback = document.getElementById("ingest-feedback");

  btnIngest.addEventListener("click", async () => {
    btnIngest.disabled = true;
    feedback.innerHTML = "<p class='stat-badge'>Scanning on-premises repository...</p>";
    try {
      const res = await fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      feedback.innerHTML = `
        <p style="color: var(--status-green); font-size: 0.9rem;">
          Ingestion completed: ${data.chunks_indexed} new chunks indexed. Total vault volume: ${data.total_index_count} chunks.
        </p>
      `;
      await pollStatus();
    } catch (err) {
      feedback.innerHTML = `<p style="color: var(--status-red);">Ingest failed: ${err.message}</p>`;
    } finally {
      btnIngest.disabled = false;
    }
  });

  btnRefresh.addEventListener("click", pollStatus);
}

/**
 * Poll system health and update metrics badges.
 */
async function pollStatus() {
  const statusDot = document.getElementById("status-dot");
  const statusText = document.getElementById("status-text");
  const memoryBadge = document.getElementById("memory-badge");
  const chunksBadge = document.getElementById("chunks-badge");

  try {
    const res = await fetch("/api/status");
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();

    statusDot.className = "status-dot healthy";
    statusText.textContent = "System Active";
    memoryBadge.textContent = `RAM: ${data.memory_rss_mb} MB`;
    chunksBadge.textContent = `Chunks: ${data.indexed_chunks_count}`;
  } catch (err) {
    statusDot.className = "status-dot";
    statusDot.style.backgroundColor = "var(--status-amber)";
    statusText.textContent = "Connecting...";
  }
}

/**
 * Format duration in seconds into human-readable British English string.
 */
function formatSeconds(sec) {
  if (sec === null || sec === undefined || isNaN(sec)) return "Calculating...";
  const s = Math.round(sec);
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return `${m}m ${rem}s`;
}

/**
 * Poll indexing jobs and update runtime progress and ETA metrics.
 */
async function pollJobs() {
  const badge = document.getElementById("job-status-badge");
  const container = document.getElementById("active-job-container");
  const descEl = document.getElementById("active-job-desc");
  const percentEl = document.getElementById("active-job-percent");
  const fillEl = document.getElementById("active-job-progress-fill");
  const currentLabelEl = document.getElementById("active-job-current-label");
  const processedEl = document.getElementById("job-processed-metric");
  const elapsedEl = document.getElementById("job-elapsed-metric");
  const remainingEl = document.getElementById("job-remaining-metric");
  const throughputEl = document.getElementById("job-throughput-metric");
  const recentContainer = document.getElementById("recent-jobs-container");

  try {
    const res = await fetch("/api/jobs");
    if (!res.ok) return;
    const data = await res.json();

    const job = data.active_job;
    if (job) {
      if (badge) {
        badge.textContent = `Status: In Progress (${job.status})`;
        badge.style.color = "var(--gold-accent)";
      }
      if (container) container.style.display = "block";
      if (descEl) descEl.textContent = job.description || "Indexing practice records...";
      if (percentEl) percentEl.textContent = `${job.percent_complete}%`;
      if (fillEl) fillEl.style.width = `${job.percent_complete}%`;
      if (currentLabelEl) {
        currentLabelEl.textContent = job.current_item_label
          ? `Current: ${job.current_item_label}`
          : "Processing records...";
      }
      if (processedEl) processedEl.textContent = `${job.processed_items} / ${job.total_items}`;
      if (elapsedEl) elapsedEl.textContent = formatSeconds(job.elapsed_seconds);
      if (remainingEl) remainingEl.textContent = formatSeconds(job.estimated_remaining_seconds);
      if (throughputEl) throughputEl.textContent = `${job.items_per_second.toFixed(2)} items/s`;
    } else {
      if (badge) {
        badge.textContent = "Status: Idle";
        badge.style.color = "var(--text-muted)";
      }
      if (container) container.style.display = "none";
    }

    if (recentContainer && Array.isArray(data.recent_jobs)) {
      if (data.recent_jobs.length === 0) {
        recentContainer.innerHTML = "<p class='empty-state' style='padding: 0.5rem;'>No recent indexing jobs recorded.</p>";
      } else {
        recentContainer.innerHTML = data.recent_jobs.map((rj) => {
          const finishedAt = rj.finished_at ? new Date(rj.finished_at * 1000).toLocaleTimeString() : "--";
          const dur = rj.elapsed_seconds ? `${rj.elapsed_seconds.toFixed(1)}s` : "--";
          const statusCol = rj.status === "completed" ? "var(--status-green)" : "var(--status-red)";
          return `<div style="padding: 0.25rem 0; border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between;">
            <span>[${escapeHtml(rj.job_type)}] ${escapeHtml(rj.description)} &mdash; ${rj.processed_items} items (${dur})</span>
            <span style="color: ${statusCol}; font-weight: 600;">${rj.status} at ${finishedAt}</span>
          </div>`;
        }).join("");
      }
    }
  } catch (err) {
    // Graceful error silence for background polling.
  }
}

/**
 * Poll practice repository volume and data statistics.
 */
async function pollStatistics() {
  const totalDocsEl = document.getElementById("stats-total-docs");
  const totalChunksEl = document.getElementById("stats-total-chunks");
  const totalVolEl = document.getElementById("stats-total-volume");
  const totalWordsEl = document.getElementById("stats-total-words");
  const tableBody = document.getElementById("stats-sources-body");

  try {
    const res = await fetch("/api/stats");
    if (!res.ok) return;
    const stats = await res.json();

    if (totalDocsEl) totalDocsEl.textContent = stats.total_documents.toLocaleString();
    if (totalChunksEl) totalChunksEl.textContent = stats.total_chunks.toLocaleString();
    if (totalVolEl) totalVolEl.textContent = `${stats.total_megabytes.toFixed(2)} MB`;
    if (totalWordsEl) totalWordsEl.textContent = stats.total_words.toLocaleString();

    if (tableBody) {
      const sources = Object.entries(stats.sources_breakdown || {});
      if (sources.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No documents indexed yet.</td></tr>`;
      } else {
        tableBody.innerHTML = sources.map(([sourceName, s]) => {
          return `<tr>
            <td style="color: var(--text-main); font-weight: 500;">${escapeHtml(sourceName)}</td>
            <td>${s.documents.toLocaleString()}</td>
            <td>${s.chunks.toLocaleString()}</td>
            <td>${s.megabytes.toFixed(3)} MB</td>
            <td>${s.words.toLocaleString()}</td>
          </tr>`;
        }).join("");
      }
    }
  } catch (err) {
    // Graceful error silence for background polling.
  }
}

/**
 * Poll Google Workspace auto-sync status state.
 */
async function pollGoogleSyncState() {
  const statusEl = document.getElementById("auto-sync-status-details");
  if (!statusEl) return;

  try {
    const res = await fetch("/api/google/sync-state");
    if (!res.ok) return;
    const state = await res.json();

    if (state.last_synced_iso) {
      const dt = new Date(state.last_synced_iso);
      statusEl.textContent = `Last check: ${dt.toLocaleTimeString()} (${state.tracked_google_docs_count} docs registered, poll interval: ${state.poll_interval_seconds}s)`;
    } else {
      statusEl.textContent = `Auto-sync active (${state.poll_interval_seconds}s interval). Awaiting initial sync run.`;
    }
  } catch (err) {
    // Graceful error silence for background polling.
  }
}

/**
 * Configure Google Workspace OAuth2 login, token state, and synchronization.
 */
function initGoogleWorkspace() {
  const statusHeading = document.getElementById("google-status-heading");
  const statusSub = document.getElementById("google-status-sub");
  const statusDot = document.getElementById("google-dot");
  const authActions = document.getElementById("google-auth-actions");
  const syncControls = document.getElementById("google-sync-controls");
  const feedback = document.getElementById("google-sync-feedback");
  const btnLogin = document.getElementById("btn-google-login");
  const btnSyncGmail = document.getElementById("btn-sync-gmail");
  const btnSyncDocs = document.getElementById("btn-sync-docs");
  const configForm = document.getElementById("google-config-form");
  const clientIdInput = document.getElementById("google-client-id");
  const clientSecretInput = document.getElementById("google-client-secret");
  const configDetails = document.getElementById("google-config-details");

  // Check URL query parameters for return from OAuth callback.
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("google_auth") === "success") {
    alert("Google Workspace account connected successfully. You can now synchronise Gmail and Google Docs.");
    window.history.replaceState({}, document.title, window.location.pathname);
  } else if (urlParams.get("google_error")) {
    alert(`Google Authentication Failed: ${urlParams.get("google_error")}`);
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  // Check connection status.
  async function refreshGoogleStatus() {
    try {
      const res = await fetch("/api/google/status");
      const data = await res.json();

      if (data.is_connected) {
        statusDot.style.backgroundColor = "var(--status-green)";
        statusHeading.textContent = `Connected: ${data.connected_email || "Google Account"}`;
        statusSub.textContent = `Authorised for Gmail and Google Docs (Last sync: ${new Date(data.connected_at).toLocaleTimeString()})`;
        authActions.innerHTML = `
          <button type="button" class="btn-secondary" id="btn-google-disconnect">
            Disconnect Account
          </button>
        `;
        syncControls.style.display = "grid";

        document.getElementById("btn-google-disconnect").addEventListener("click", async () => {
          if (confirm("Disconnect this Google account? Stored tokens will be removed locally.")) {
            await fetch("/api/google/disconnect", { method: "POST" });
            await refreshGoogleStatus();
          }
        });
      } else {
        statusDot.style.backgroundColor = "var(--status-amber)";
        statusHeading.textContent = "Google Account Not Connected";
        statusSub.textContent = data.is_configured
          ? "Client credentials configured. Ready for partner sign-in."
          : "Configure OAuth2 Client ID & Secret below, then click Sign in with Google.";
        authActions.innerHTML = `
          <button type="button" class="btn-primary" id="btn-google-login">
            Sign in with Google
          </button>
        `;
        syncControls.style.display = "none";
        document.getElementById("btn-google-login").addEventListener("click", triggerGoogleLogin);
      }
    } catch (err) {
      statusHeading.textContent = "Unable to inspect Google status";
    }
  }

  async function triggerGoogleLogin() {
    try {
      const res = await fetch("/api/google/auth-url");
      const data = await res.json();
      if (res.ok && data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        configDetails.open = true;
        alert(data.detail || "Please configure your Google Client ID and Secret first.");
      }
    } catch (err) {
      alert(`Login initiation error: ${err.message}`);
    }
  }

  if (btnLogin) {
    btnLogin.addEventListener("click", triggerGoogleLogin);
  }

  // Handle saving client credentials.
  if (configForm) {
    configForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const clientId = clientIdInput.value.trim();
      const clientSecret = clientSecretInput.value.trim();

      if (!clientId || !clientSecret) return;

      try {
        const res = await fetch("/api/google/configure", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ client_id: clientId, client_secret: clientSecret }),
        });
        const data = await res.json();
        alert(data.message || "Credentials saved.");
        configDetails.open = false;
        await refreshGoogleStatus();
      } catch (err) {
        alert(`Failed to save credentials: ${err.message}`);
      }
    });
  }

  // Sync Gmail.
  if (btnSyncGmail) {
    btnSyncGmail.addEventListener("click", async () => {
      btnSyncGmail.disabled = true;
      feedback.style.display = "block";
      feedback.innerHTML = "<p class='stat-badge'>Synchronising Gmail messages via Google API...</p>";

      try {
        const res = await fetch("/api/google/sync-gmail", { method: "POST" });
        const data = await res.json();

        if (res.ok) {
          feedback.innerHTML = `
            <div class="log-box" style="border-left: 3px solid var(--status-green);">
              [SUCCESS] Gmail Synchronisation Complete.
              Messages processed: ${data.messages_fetched}
              Chunks indexed into LanceDB &amp; BM25: ${data.chunks_indexed}
              Total vault repository count: ${data.total_vault_volume} chunks.
            </div>
          `;
          await pollStatus();
        } else {
          feedback.innerHTML = `<div class="log-box" style="color: var(--status-red);">[ERROR] ${data.detail || "Sync failed"}</div>`;
        }
      } catch (err) {
        feedback.innerHTML = `<div class="log-box" style="color: var(--status-red);">[ERROR] ${err.message}</div>`;
      } finally {
        btnSyncGmail.disabled = false;
      }
    });
  }

  // Sync Google Docs.
  if (btnSyncDocs) {
    btnSyncDocs.addEventListener("click", async () => {
      btnSyncDocs.disabled = true;
      feedback.style.display = "block";
      feedback.innerHTML = "<p class='stat-badge'>Scanning and synchronising Google Docs...</p>";

      try {
        const res = await fetch("/api/google/sync-docs", { method: "POST" });
        const data = await res.json();

        if (res.ok) {
          feedback.innerHTML = `
            <div class="log-box" style="border-left: 3px solid var(--status-green);">
              [SUCCESS] Google Docs Synchronisation Complete.
              Documents fetched: ${data.docs_fetched}
              Chunks indexed into LanceDB &amp; BM25: ${data.chunks_indexed}
              Total vault repository count: ${data.total_vault_volume} chunks.
            </div>
          `;
          await pollStatus();
        } else {
          feedback.innerHTML = `<div class="log-box" style="color: var(--status-red);">[ERROR] ${data.detail || "Sync failed"}</div>`;
        }
      } catch (err) {
        feedback.innerHTML = `<div class="log-box" style="color: var(--status-red);">[ERROR] ${err.message}</div>`;
      } finally {
        btnSyncDocs.disabled = false;
      }
    });
  }

  // Incremental Auto-Sync Trigger Now.
  const btnAutoSyncNow = document.getElementById("btn-auto-sync-now");
  if (btnAutoSyncNow) {
    btnAutoSyncNow.addEventListener("click", async () => {
      btnAutoSyncNow.disabled = true;
      feedback.style.display = "block";
      feedback.innerHTML = "<p class='stat-badge'>Checking Google Drive for newly added or modified documents...</p>";

      try {
        const res = await fetch("/api/google/auto-sync", { method: "POST" });
        const data = await res.json();

        if (res.ok) {
          feedback.innerHTML = `
            <div class="log-box" style="border-left: 3px solid var(--status-green);">
              [SUCCESS] Incremental Check Complete.
              ${data.message}
              Newly indexed chunks: ${data.new_chunks_indexed}
              Total vault volume: ${data.total_vault_volume} chunks.
            </div>
          `;
          await pollGoogleSyncState();
          await pollStatistics();
          await pollStatus();
        } else {
          feedback.innerHTML = `<div class="log-box" style="color: var(--status-red);">[ERROR] ${data.detail || "Auto-sync check failed"}</div>`;
        }
      } catch (err) {
        feedback.innerHTML = `<div class="log-box" style="color: var(--status-red);">[ERROR] ${err.message}</div>`;
      } finally {
        btnAutoSyncNow.disabled = false;
      }
    });
  }

  refreshGoogleStatus();
}

/**
 * Escape HTML special characters for safe browser rendering.
 */
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
