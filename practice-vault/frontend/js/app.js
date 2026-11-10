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
  pollStatus();
  loadTasks();
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
 * Escape HTML special characters for safe browser rendering.
 */
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
