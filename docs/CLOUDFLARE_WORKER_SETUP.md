# Cloudflare Worker Setup for the Kay Client Demonstration

> Operator Handover Specification for an External Artificial Intelligence (AI)
> Agent.
> Purpose: provision a Cloudflare Worker that holds an OpenRouter credential
> and proxies live Jev and Luna classification calls for the
> `clients/kay/` demonstration subpage.
> Status: Awaiting execution. No infrastructure has been created yet.
> Language: British Professional English (AGENTS.md Policy 15).

---

## 1. Purpose, Scope, and Deliberate Exclusions

### 1.1 What this document is for

1. It is a complete, self-contained set of instructions for an operator or an
   AI agent to create a Cloudflare account, deploy one Worker, store one
   secret, and verify the endpoint end to end.
2. It assumes no prior Cloudflare knowledge and no access to this repository's
   history beyond what is quoted here.
3. It is written to be executed in order. Each step states its own success
   criteria so a partially completed run can be detected and resumed.

### 1.2 What this document is deliberately not for

1. It does not describe how to build the `clients/kay/` static subpage. That
   is a separate task in this repository.
2. It does not authorise moving `heathandcity.com` hosting or Domain Name
   System (DNS) management to Cloudflare. GitHub Pages remains the host of
   record for System A, per `docs/ARCHITECTURE.md` Section 2.1.
3. It does not authorise storing any credential in Git. See Section 3.

### 1.3 The architectural role of Cloudflare

Cloudflare performs exactly one role in this system: it is the server that
GitHub Pages cannot be. The static site cannot execute code, cannot read
environment variables, and cannot hold a secret. The Worker closes that gap
for a single route.

```
Browser --> GitHub Pages --> clients/kay/ page assets   (free, static)

Browser --> Cloudflare Worker --> OPENROUTER_API_KEY       (secret)
                    |
                    +--> https://openrouter.ai/api/v1      (Jev, Luna)
                              |
                    <--+------'  JSON result to the browser
```

The Worker stores nothing between requests. It is stateless, and it exists
only for the duration of a single call.

---

## 2. Cost, Limits, and Plan Suitability

Figures verified against Cloudflare's published pricing, October and November
2026.

### 2.1 Free plan entitlements

| Component | Free plan limit |
| :--- | :--- |
| Price | $0 per month |
| Worker requests | 100,000 per day, account-wide |
| CPU time | 10 milliseconds per invocation |
| Subrequests upstream | 50 per invocation, not billed |
| Static asset requests | Free and unlimited |
| Environment variables | 64 per Worker |
| Secrets | Counted as environment variables |
| Egress bandwidth | No charge |

### 2.2 Paid plan, if required

Workers Paid costs a minimum of $5 USD per month. It lifts CPU time to 30
seconds by default and removes the daily request ceiling.

### 2.3 Why the free plan is sufficient

1. The subpage is set to `noindex` and excluded from `sitemap.xml`, so traffic
   will be low. 100,000 requests per day is roughly 70 per minute sustained.
2. CPU time excludes time spent waiting on `fetch()`. This Worker spends
   almost all of its life waiting for OpenRouter to answer, which is
   wall-clock time, not CPU time. Parsing the reply is well under 1 ms.
3. The upstream call to OpenRouter is a subrequest, and Cloudflare does not
   bill for subrequests.

### 2.4 The cost Cloudflare does not cover

OpenRouter inference is billed separately by OpenRouter at per-model token
rates. Cloudflare being free does not make a classification run free. For a
demonstration of a handful of runs the cost will be small, but it is a real
and recurring charge on the OpenRouter account.

### 2.5 Plan suitability caveat

Cloudflare describes the Free plan as intended for personal or hobby projects
that are not business-critical. It is not explicitly restricted to
non-commercial use. Because this site is engineered for commercial sale to
regulated firms, the operator should decide whether $5 per month for Workers
Paid is the more defensible position once the demonstration becomes
client-facing in earnest. Record that decision in this repository.

---

## 3. Binding Prerequisites Before Any Work Begins

### 3.1 Rotate the exposed OpenRouter credential

**This step is mandatory and must happen first.**

The OpenRouter credential is committed in plaintext in the
`wazzuck/vunderland` repository. It is tracked at `HEAD` as
`keys/openrouter.txt` and appears in five separate commits. It is also
exported into every shell by line 29 of `~/.bashrc`, and the file carries mode
`664`, making it group- and world-readable on the host.

A credential committed in plaintext to version control must be treated as
compromised by default. Do not copy the existing value into Cloudflare.

Required actions, in order:

1. Sign in to https://openrouter.ai and revoke the current key.
2. Issue a fresh key. Keep the scope as narrow as the account allows.
3. Store the new value at `~/vunderland/keys/openrouter.txt`.
4. Set the file mode to `600` so it is readable only by the owner.
   Run `chmod 600 ~/vunderland/keys/openrouter.txt`.
5. Confirm the mode with `stat -c '%a %n' ~/vunderland/keys/openrouter.txt`.
   The expected output is `600`.
6. Do not commit the new key to any repository. Add `keys/` to
   `vunderland/.gitignore` and remove the tracked file from the index with
   `git rm --cached keys/openrouter.txt`. Note that `.gitignore` already
   contains `*.txt`, which has no effect while the file remains tracked.

**Stop and report to the operator if the key cannot be rotated. Do not
proceed to Section 9 with the existing credential.**

### 3.2 Review the remaining tracked credentials

The same repository tracks 29 files under `keys/`, including
`keys/.claude/.credentials.json`, `keys/heathandcity_token.json`,
`keys/opencode/auth.json`, and `keys/mcphub/servers.json`. These are outside
the scope of this task but should be reported to the operator as findings.

### 3.3 Account prerequisites

1. A GitHub account with push access to `wazzuck/heathandcity`.
2. An OpenRouter account with credit, for the inference charges in Section
   2.4.
3. A Cloudflare account. Free tier is acceptable per Section 2.
4. Node.js version 18 or later, to run `wrangler`.
   Check with `node --version`.
5. Confirmation from the operator on the hostname choice in Section 4.

---

## 4. Decision: Which Hostname the Worker Uses

Cloudflare DNS for `heathandcity.com` is currently managed at Spaceship, not
at Cloudflare, according to `STATUS.md` entry 7. This constrains the options.

### 4.1 Option A: `workers.dev` subdomain, no DNS change

1. The Worker answers at a URL such as
   `https://kay-classify.<account>.workers.dev/classify`.
2. No DNS record is created and Spaceship remains untouched.
3. This is the lowest-risk option and the recommended default.

### 4.2 Option B: custom domain `api.heathandcity.com`

1. Requires the `heathandcity.com` zone to be hosted on Cloudflare.
2. Moving a DNS zone is a separate, higher-risk change affecting mail and the
   live site's apex records.
3. Do not choose this option without explicit written operator approval.

**Record which option was chosen, and why, in Section 13.**

---

## 5. Step 1: Create the Cloudflare Account

1. Open https://dash.cloudflare.com/sign-up in a browser.
2. Provide an email address and a password, or use a single sign-on provider.
3. Complete the email verification link.
4. Decline any prompt to add a website or change DNS at this stage. The
   Worker does not require a proxied zone when Option A is chosen.
5. Confirm success by loading https://dash.cloudflare.com and seeing an empty
   account dashboard.

Success criterion: the dashboard loads and shows no active zones or Workers.

---

## 6. Step 2: Install and Authenticate the Command Line Tool

1. Install `wrangler`, the Cloudflare command line tool:

   ```bash
   npm install -g wrangler
   ```

2. Confirm the installation:

   ```bash
   wrangler --version
   ```

3. Record the version in Section 13.

4. Authenticate interactively:

   ```bash
   wrangler login
   ```

   This opens a browser and asks for permission. Approve it for the account
   created in Section 5.

5. Confirm authentication:

   ```bash
   wrangler whoami
   ```

   Success criterion: the output shows your account identifier and no error.

**Dependency record.** `wrangler` is added as a development dependency of this
workflow. Its licence must be confirmed as permissive, MIT or Apache-2.0, and
recorded in Section 13 before the operator runs
`scripts/verify_legal_compliance.py`. If the licence is copyleft, stop and
report under AGENTS.md Policy 4.

---

## 7. Step 3: Create the Worker Project

1. Choose a directory outside this repository, for example:

   ```bash
   mkdir -p ~/kay-worker
   cd ~/kay-worker
   ```

2. Create `wrangler.toml` with the following contents:

   ```toml
   name = "kay-classify"
   main = "src/index.js"
   compatibility_date = "2026-11-13"

   [vars]
   ORIGIN_ALLOWED = "https://heathandcity.com"
   ```

3. Create the source directory:

   ```bash
   mkdir -p src
   ```

4. Do not commit this directory to `wazzuck/heathandcity`. It is
   infrastructure, not site content. Keep it in its own private repository if
   it must be version controlled at all.

Success criterion: `wrangler.toml` exists and parses.

---

## 8. Step 4: Write the Worker Source

Create `src/index.js` with the following contents. This is the complete
implementation; no further code is required.

```javascript
/**
 * Kay demonstration classification proxy.
 *
 * Purpose: accept one classification request from the Heath & City static
 * site, attach the OpenRouter credential held in this Worker's secret
 * store, forward the request, and return the result.
 *
 * Deliberately not here: no storage, no logging of message bodies, no
 * credential ever returned to the caller, no Cross-Origin Resource
 * Sharing (CORS) wildcard.
 *
 * Invariants relied upon:
 * 1. OPENROUTER_API_KEY is injected by Cloudflare at runtime and is never
 *    present in this file, in Git, or in any Hypertext Transfer Protocol
 *    (HTTP) response.
 * 2. Only the origin in ORIGIN_ALLOWED may read the response.
 * 3. Requests are rejected before any upstream call when the origin does
 *    not match, so an unauthorised caller cannot spend OpenRouter credit.
 */

const UPSTREAM = "https://openrouter.ai/api/v1/chat/completions";
const MAX_BODY_BYTES = 65536;

export default {
  async fetch(request, env, ctx) {
    // Step 1: allow only a POST to the single expected route.
    const url = new URL(request.url);
    if (url.pathname !== "/classify") {
      return json({ ok: false, error: "Not found." }, 404);
    }
    if (request.method !== "POST") {
      return json({ ok: false, error: "Method not allowed." }, 405);
    }

    // Step 2: enforce the origin allow-list before doing any paid work.
    const origin = request.headers.get("Origin") || "";
    if (origin !== env.ORIGIN_ALLOWED) {
      return json({ ok: false, error: "Origin rejected." }, 403);
    }

    // Step 3: reject oversized payloads to bound memory and cost.
    const declared = Number(request.headers.get("Content-Length") || 0);
    if (declared > MAX_BODY_BYTES) {
      return json({ ok: false, error: "Payload too large." }, 413);
    }

    // Step 4: read and parse the inbound JSON body.
    let payload;
    try {
      payload = await request.json();
    } catch (err) {
      return json({ ok: false, error: "Invalid JSON payload." }, 400);
    }

    const email = payload && payload.email;
    if (!email || typeof email !== "object") {
      return json({ ok: false, error: "Missing 'email' object." }, 400);
    }

    // Step 5: build the upstream prompt from the submitted email only.
    const glossary = Array.isArray(payload.glossary_override)
      ? payload.glossary_override
      : [];

    const dictionary = glossary
      .map((g) => `${g.term}: ${g.definition}`)
      .join("\n");

    const prompt =
      "You are an email triage assistant for a London market broker.\n" +
      "Return JSON only, with keys: department, confidence, summary.\n" +
      "Registered departments: placement, claims, compliance, internal.\n" +
      "Use this corporate insurance dictionary:\n" +
      (dictionary || "(none supplied)") +
      "\n\nSubject: " +
      String(email.subject || "") +
      "\nFrom: " +
      String(email.sender || "") +
      "\n\nBody:\n" +
      String(email.body || "");

    // Step 6: call OpenRouter with the secret held only by this Worker.
    let upstream;
    try {
      upstream = await fetch(UPSTREAM, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + env.OPENROUTER_API_KEY,
        },
        body: JSON.stringify({
          model: "openai/gpt-luna-latest",
          messages: [{ role: "user", content: prompt }],
          response_format: { type: "json_object" },
        }),
      });
    } catch (err) {
      // Report a generic failure. Do not leak the upstream error text,
      // which may contain request detail.
      return json({ ok: false, error: "Upstream unavailable." }, 502);
    }

    // Step 7: translate the upstream status without forwarding headers.
    if (!upstream.ok) {
      const status = upstream.status === 429 ? 429 : 502;
      return json(
        { ok: false, error: "Classification service error." },
        status
      );
    }

    // Step 8: extract the assistant message and parse it defensively.
    let data;
    try {
      data = await upstream.json();
    } catch (err) {
      return json({ ok: false, error: "Malformed upstream reply." }, 502);
    }

    const text =
      data &&
      data.choices &&
      data.choices[0] &&
      data.choices[0].message &&
      data.choices[0].message.content;

    let parsed = null;
    try {
      parsed = JSON.parse(text);
    } catch (err) {
      parsed = null;
    }

    // Step 9: return a stable shape for the static page to render.
    return json({
      ok: true,
      luna: {
        model: "Luna",
        executive_summary: (parsed && parsed.summary) || String(text || ""),
        department: (parsed && parsed.department) || "internal",
        confidence: (parsed && parsed.confidence) || 0,
      },
    });
  },
};

/**
 * Serialise a response as JSON with an explicit status code.
 *
 * The Access-Control-Allow-Origin header echoes only the single allowed
 * origin, never a wildcard, so credentials cannot be read cross-origin.
 *
 * @param {object} body - The JSON-serialisable response body.
 * @param {number} status - The HTTP status code to send.
 * @returns {Response} A JSON response guarded by the allow-list origin.
 */
function json(body, status) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "https://heathandcity.com",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
```

### 8.1 Narrative walkthrough

1. Steps 1 to 3 reject anything that is not a small, correctly routed POST
   from the approved origin. This happens before any OpenRouter credit can
   be spent, so an unauthorised caller costs nothing.
2. Step 4 parses the body and requires an `email` object, matching the
   payload contract already used by `harness/standalone_classifier/app.js`.
3. Step 5 flattens the glossary into a prompt prefix. This reproduces the
   dynamic prompt injection the Raspberry Pi performs in
   `build_jev_request`.
4. Step 6 is the only place the secret is read. It exists in the Worker's
   runtime environment and nowhere else.
5. Steps 7 and 8 deliberately do not forward upstream error text or headers,
   which prevents internal detail leaking to the browser.
6. Step 9 returns a stable shape. The static page renders this identically
   to a saved result, so the fallback path needs no special handling.

---

## 9. Step 5: Store the Secret and Deploy

### 9.1 Store the secret

```bash
cd ~/kay-worker
wrangler secret put OPENROUTER_API_KEY
```

`wrangler` prompts for the value on standard input. Paste the **rotated**
key from Section 3.1, not the value already committed to `vunderland`.

Success criterion: the command reports `Creating secret OPENROUTER_API_KEY`.
Confirm with:

```bash
wrangler secret list
```

The output must list `OPENROUTER_API_KEY`. It must not print the value.

### 9.2 Deploy

```bash
wrangler deploy
```

Success criterion: the output prints the Worker URL, of the form
`https://kay-classify.<account>.workers.dev`.

### 9.3 Record the deployment

Store the exact Worker URL in Section 13. This is the value the static page
will call.

---

## 10. Step 6: Verify the Endpoint

Run these checks in order. Do not report completion until all pass.

1. **Route rejection.** A GET to the Worker root must return 404:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" \
     "https://kay-classify.<account>.workers.dev/"
   ```

   Expected: `404`.

2. **Origin rejection.** A POST from a disallowed origin must return 403 and
   must not consume OpenRouter credit:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" \
     -X POST "https://kay-classify.<account>.workers.dev/classify" \
     -H "Origin: https://evil.example" \
     -H "Content-Type: application/json" \
     -d '{"email":{"subject":"test","body":"test"}}'
   ```

   Expected: `403`.

3. **Happy path.** A POST from the approved origin must return 200:

   Create the payload file first:

   ```bash
   cat > /tmp/kay-payload.json <<'JSON'
   {
     "email": {
       "sender": "a@b.c",
       "subject": "Renewal order",
       "body": "Please quote on the attached slip."
     },
     "glossary_override": []
   }
   JSON
   ```

   Then POST it:

   ```bash
   curl -s -X POST \
     "https://kay-classify.<account>.workers.dev/classify" \
     -H "Origin: https://heathandcity.com" \
     -H "Content-Type: application/json" \
     --data @/tmp/kay-payload.json
   ```

   Expected: HTTP `200` and a body beginning `{"ok":true,"luna":`.

4. **Secret absence.** Confirm the key is not present in any deployed
   artifact:

   ```bash
   curl -s "https://kay-classify.<account>.workers.dev/classify" \
     | grep -c "sk-or-"
   ```

   Expected: `0`. Also confirm the key never appears in this repository:

   ```bash
   git -C ~/heathandcity grep -c "sk-or-" \
     $(git -C ~/heathandcity rev-list --all)
   ```

   Expected: no matches.

5. **Rate ceiling.** Confirm the free-plan behaviour is understood: exceeding
   100,000 requests in a day returns Cloudflare error 1027 until 00:00
   Coordinated Universal Time (UTC).
   No action is required, but record that this limit exists.

---

## 11. Step 7: Repository and Compliance Actions

These actions are performed in `wazzuck/heathandcity`, not in the Worker
project.

1. Run the licensing and data-boundary gate:

   ```bash
   python scripts/verify_legal_compliance.py
   ```

   All four gates must pass. If a gate fails, stop and report under
   AGENTS.md Policy 4.

2. Run the site verification suite:

   ```bash
   python scripts/verify_site.py
   ```

3. Confirm no credential has entered the tree:

   ```bash
   git status --short
   ```

4. Update `STATUS.md` during close-out, on `main`, recording the decision,
   the chosen hostname option from Section 4, and the OpenRouter licence
   position.

5. If the interface or hosting arrangement changed, update
   `docs/ARCHITECTURE.md` in the same task. Note that
   `docs/ARCHITECTURE.md` is currently modified on the parallel
   `task/revamp-homepage` branch. Re-read it immediately before editing and
   coordinate with that agent to avoid overwriting their work.

### 11.1 Data protection position to record

A live classification transmits message text from the browser to Cloudflare
and then to OpenRouter. That is processing by a third party outside the
on-premises boundary described in `docs/ARCHITECTURE.md` Section 2.2.

The following must be recorded in the repository, not only in chat:

1. Whether the demonstration accepts synthetic scenarios only, or real client
   correspondence.
2. If real correspondence is permitted, the lawful basis, the processor
   arrangement with OpenRouter, and the international transfer safeguard.
3. Confirmation that the `noindex` subpage is not linked from the public
   homepage.

Synthetic scenarios only is the recommended default, and it keeps the
demonstration outside the scope of United Kingdom (UK) General Data
Protection Regulation (UK GDPR) transfer questions entirely.

---

## 12. Rollback

To remove the Worker completely:

```bash
cd ~/kay-worker
wrangler delete kay-classify
```

Then revoke the OpenRouter key at https://openrouter.ai, since the secret
store held it. Finally remove the Worker project directory.

Rollback does not affect `heathandcity.com`, GitHub Pages, or the static
`clients/kay/` subpage, which remain functional with saved results.

---

## 13. Execution Record

Complete this section during and after execution.

| Item | Value |
| :--- | :--- |
| wrangler version | 4.86.0 (MIT OR Apache-2.0) |
| Cloudflare account identifier | `bb26d0a4c5bcf535f66597313ab3c8c7` |
| Hostname option chosen (Section 4) | Option A, `workers.dev` |
| Worker URL | `https://kay-classify.heathandcity.workers.dev` |
| OpenRouter key rotated (Section 3.1) | Deferred by operator decision |
| `wrangler` licence confirmed permissive | Yes, MIT OR Apache-2.0 |
| `verify_legal_compliance.py` result | Gate 1 FAIL, pre-existing |
| `verify_site.py` result | PASS |
| Data protection position recorded | Yes, real correspondence, Section 13.1 |
| Date of execution | 13 November 2026 |

### 13.1 Execution notes

1. **Account and subdomain.** The Cloudflare account was created and
   authorised through the operator's browser. The account had no
   `workers.dev` subdomain, so `heathandcity` was registered with
   `PUT /accounts/{id}/workers/subdomain` before the first deploy.
2. **Model substitution.** The model identifier in Section 8,
   `openai/gpt-luna-latest`, is rejected by OpenRouter with HTTP 400
   ("not a valid model ID"). The deployed Worker uses
   `openai/gpt-6-luna`, the current Luna generation and the cheapest
   Luna tier ($0.10 / $0.50 per million tokens).
3. **Key rotation deferred.** The operator instructed that Section 3.1
   be skipped for now, so the credential previously committed to
   `wazzuck/vunderland` is the value stored in Cloudflare's secret
   store. Rotation remains an open security item, recorded in
   `STATUS.md`.
4. **Certificate delay.** After the first deploy, Transport Layer
   Security (TLS) for the new hostname failed with a handshake error
   for roughly ten minutes while Cloudflare issued the wildcard
   certificate for `*.heathandcity.workers.dev`. No action was
   required; the endpoint then served normally.
5. **Verification results.** All four Section 10 checks pass: 404 on
   the root route, 403 on a disallowed origin, 200 on the happy path
   (department `placement`, confidence 0.96), and zero occurrences of
   `sk-or-` in any response. The repository history grep matches only
   the literal command text in this document, not a credential.
6. **Legal Gate 1 failure (pre-existing).** Gate 1 flags `scipy`,
   `pandas` and `docutils` because the copyleft pattern matches words
   such as "GPL-compatible" inside their BSD licence text, and because
   `practice-vault/venv` does not exist, so the audit runs against the
   host Python environment. This predates this task; a fix is recorded
   as a `Next` item in `STATUS.md`.
7. **Data protection position.** The operator has decided that the
   demonstration accepts real client correspondence. The lawful basis,
   the processor arrangement with OpenRouter, and the international
   transfer safeguard are **not yet defined** and must be recorded
   before real correspondence is used. The `clients/kay/` subpage must
   remain `noindex` and unlinked from the public homepage.

---

## 14. Open Decisions for the Operator

1. Whether to rotate the exposed OpenRouter key before or after the static
   subpage is built. Before is recommended.
2. Whether to adopt the free plan or Workers Paid at $5 per month, given the
   commercial-sale posture of this product.
3. Whether the demonstration accepts synthetic scenarios only, or real
   correspondence under a recorded transfer safeguard.
4. Whether `keys/` should be purged from `vunderland` history, which
   requires a coordinated force-push across all machines.
