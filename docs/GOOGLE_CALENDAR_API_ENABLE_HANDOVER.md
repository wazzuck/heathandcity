# Enabling the Google Calendar API: Browser Agent Handover

> Purpose: let a browser-capable Artificial Intelligence (AI) agent enable
> the Google Calendar API for the Practice Vault appliance. This is one
> console change. It does not require re-consent, a new token, a new scope
> or a code change.
> Date: 13 November 2026.
> Status: completed 14 November 2026 at 03:16 UTC. The API is enabled, a
> Calendar read succeeds, and 558 events from seven calendars were
> imported into the local diary at 03:42 UTC. Findings and results are
> in Section 10.
> Language: British Professional English (AGENTS.md Policy 15).
> Line width: 80 columns.

---

## 1. Objective

Enable the Google Calendar API in the Google Cloud project that owns the
appliance's OAuth client, then prove that a Calendar read succeeds.

The appliance already holds a durable refresh token with the
`https://www.googleapis.com/auth/calendar.readonly` scope. Gmail and Drive
calls succeed with that token. Calendar calls fail only because the API
itself is disabled in the project.

## 2. Current state, measured on 13 November 2026

1. Token file written at 20:24:34 UTC with no seven-day expiry.
2. Scopes present: Gmail read-only, Drive read-only, Calendar read-only,
   profile, email and `openid`.
3. `GET /api/google/status` returns `is_connected: true`.
4. Gmail profile call: HTTP 200. Drive `about` call: HTTP 200.
5. Calendar list call: **HTTP 403**. Google returns:

   ```text
   "reason": "accessNotConfigured"
   "status": "PERMISSION_DENIED"
   "details": [{
     "reason": "SERVICE_DISABLED",
     "metadata": {
       "service": "calendar-json.googleapis.com",
       "containerInfo": "840262346134"
     }
   }]
   ```

6. Project number in the error: `840262346134`. The earlier OAuth
   execution report calls the project `marketcalc`. Confirm that both
   names refer to the same project before enabling anything. If the
   console shows a different project, stop and report.

## 3. The single change

### Step 1: Open the API page

Open this exact address in the browser:

```text
https://console.cloud.google.com/apis/library/calendar-json.googleapis.com?project=840262346134
```

The shorter link that Google itself returned is also valid:

```text
https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=840262346134
```

### Step 2: Confirm the project

1. Check the project selector at the top of the page.
2. It must show the project that owns the OAuth client used by the
   appliance, identified by number `840262346134` and named `marketcalc`
   in the earlier report.
3. If it shows any other project, stop. Do not enable the API in the
   wrong project.

### Step 3: Enable the API

1. If the page shows **Enable**, click it and confirm.
2. If the page already shows **Manage**, the API is already enabled. Stop
   and report that finding; the cause of the 403 is then elsewhere.
3. Do not enable any other API on this page or in this project.

### Step 4: Wait for propagation

1. Wait at least two minutes.
2. Google sometimes takes up to ten minutes to propagate an enablement.
3. Do not repeat the click while waiting. Do not change any other setting.

## 4. Guardrails

1. Never print, copy or transmit the client secret, access token or
   refresh token.
2. Do not change the OAuth scopes. The appliance depends on all five.
3. Do not create, delete or rotate any credential, key or consent screen.
4. Do not change the authorised redirect Uniform Resource Identifier
   (URI), the branding, or the publishing status.
5. Do not submit a verification, Cloud Application Security Assessment
   (CASA) or security-assessment request.
6. Do not enable billing, add a service account or create an API key.
7. Make one change at a time, then report the visible result in text.
8. If the console asks for a password, a one-time code, an administrator
   approval or an organisation policy exception, stop and hand control
   back to the operator.

## 5. Verification

### Step 1: Confirm in the console

The API dashboard must show that the API is enabled, with a **Manage**
button and no warning banner.

### Step 2: Confirm from the appliance

Run this command on the appliance host. It refreshes the access token and
prints only the status and the number of calendars; it never prints a
token.

```bash
cd ~/practice-vault
./venv/bin/python - <<'EOF'
import sys
sys.path.insert(0, "backend")
import httpx
from app.google_sync import GoogleWorkspaceSyncService

service = GoogleWorkspaceSyncService()
service.refresh_access_token()
token = service.get_valid_access_token()
response = httpx.get(
    "https://www.googleapis.com/calendar/v3/users/me/calendarList",
    headers={"Authorization": f"Bearer {token}"},
    timeout=30,
)
print("HTTP", response.status_code)
body = response.json()
if response.status_code == 200:
    print("calendars:", len(body.get("items", [])))
else:
    error = body.get("error", {})
    print("status:", error.get("status"))
    reasons = error.get("errors") or [{}]
    print("reason:", reasons[0].get("reason"))
EOF
```

Expected before the change:

```text
HTTP 403
status: PERMISSION_DENIED
reason: accessNotConfigured
```

Expected after the change:

```text
HTTP 200
calendars: 1
```

A count of one or more is success. An empty list with HTTP 200 also
proves access, but report it because it means the account has no visible
calendar.

### Step 3: Confirm the appliance can read events

```bash
cd ~/practice-vault
./venv/bin/python - <<'EOF'
import sys
from datetime import datetime, timezone
sys.path.insert(0, "backend")
from app.google_sync import GoogleWorkspaceSyncService

service = GoogleWorkspaceSyncService()
events = service.fetch_calendar_events(
    time_min=datetime(2026, 1, 1, tzinfo=timezone.utc),
    time_max=datetime(2027, 1, 1, tzinfo=timezone.utc),
    max_results=5,
)
print("events:", len(events))
for event in events:
    print(event["start"], "|", event["summary"][:60])
```

Success is `events: 0` or more with no warning in
`~/practice-vault-data/vault-server.log` about a Calendar status.

## 6. Troubleshooting

1. **403 `accessNotConfigured`.** The API is still off, or the wrong
   project is selected. Recheck project `840262346134` and wait ten
   minutes.
2. **403 `insufficientPermissions`.** The token lacks the Calendar scope.
   Stop. Do not re-consent. Report to the operator.
3. **401 `invalid_request`.** The access token expired and the refresh
   failed. Run the refresh command again; if it still fails, stop.
4. **429.** Quota or rate limit. Wait and retry once; do not loop.
5. **The console asks for verification.** A restricted-scope review.
   Stop and report; never submit.

## 7. What this does not fix

Enabling the API restores **access**. It does not, by itself, refresh the
diary.

1. `GoogleWorkspaceSyncService.fetch_calendar_events()` exists. On the
   appliance host it now has a caller, `scripts/sync_calendar.py`, but
   that script is not part of this developer checkout.
2. There is no scheduled calendar sync, and no `last_calendar_sync` key in
   `google_sync_state.json`. The local `calendar_events` table still
   holds one manual entry, the Chambers Advisory Conference on
   19 November 2026, with source `manual_diary`.
3. Confirmed on 14 November 2026: `calendar_events.db` holds exactly one
   row, and its source is `manual_diary`.

The caller now exists on the appliance, but the remaining engineering
change is a nightly step that runs it and records a sync timestamp.
Until then, enabling the API lets an operator read the calendar on
demand but does not update the diary automatically.

## 8. Success criteria

1. The console shows the Google Calendar API enabled for project
   `840262346134`.
2. The calendar list call returns HTTP 200.
3. The appliance's event fetch returns without a Calendar warning.
4. No credential, scope, redirect URI or consent setting changed.
5. The report names the project, the time of the change, and the
   verification output, with no token value.

## 9. Report back

1. Project name and number shown in the console.
2. Whether the button said **Enable** or **Manage**.
3. The calendar list HTTP status and calendar count.
4. The appliance event count.
5. Any console warning, administrator prompt or propagation delay.
6. Anything that required operator intervention.

Record the result in `STATUS.md` and in
`docs/GOOGLE_OAUTH_BROWSER_AGENT_HANDOVER.md`. A stale status file is a
defect.

---

## 10. Execution report: findings and results (14 November 2026)

### 10.1 Outcome at a glance

| Success criterion (Section 8) | Result |
| --- | --- |
| Console shows the API enabled | Met: Status **Enabled**, no warning |
| Calendar list returns HTTP 200 | Met: 7 calendars |
| Event fetch without a Calendar warning | Met: 5 events |
| No credential, scope, redirect URI or consent change | Met |
| Report names project, time and output, no token | Met: this section |

### 10.2 What was done

1. Opened the API page named in Section 3 for project `840262346134`.
2. Confirmed that the project selector read `marketcalc` and that the
   home link carried the same number. Both names refer to one project.
3. Found an **Enable** button, so the API was off, as reported.
4. Clicked **Enable** once at 2026-11-14T03:16:18Z. The console moved to
   the API/Service details page.
5. Read Status **Enabled** with a **Disable API** button and no warning
   banner.
6. Waited about four minutes, then ran the Section 5 checks on the
   appliance host.

### 10.3 Verification output

Calendar list, with no token printed:

```text
HTTP 200
calendars: 7
```

Event fetch for 2026:

```text
events: 5
```

No Calendar warning was written to
`~/practice-vault-data/vault-server.log`.

### 10.4 Findings

1. **The API was the only blocker.** The same durable token that failed
   with `SERVICE_DISABLED` returned HTTP 200 once the API was enabled.
   No re-consent, new scope or new token was needed.
2. **The expected count was wrong.** Section 5 predicted one calendar.
   The account exposes seven, including shared calendars, so a count of
   seven is success, not a defect.
3. **The developer container is not the appliance.** Its token is older
   and lacks `calendar.readonly`, so the same check returned
   `403 insufficientPermissions` there. The durable token lives on the
   appliance host (`86.27.171.186`), and all verification ran there with
   `~/practice-vault/venv/bin/python`.
4. **The diary is unchanged.** `calendar_events.db` still holds one row,
   the manual entry with source `manual_diary`. Enabling the API did not
   import Google events, as Section 7 predicted.
5. **No side effects were seen.** No warning banner, administrator
   prompt, organisation policy exception or verification request
   appeared.

### 10.5 Repository record and checks

1. `STATUS.md` entry 63 records the change; KF-01 is resolved and KF-02
   remains open.
2. `docs/GOOGLE_OAUTH_BROWSER_AGENT_HANDOVER.md` now points here.
3. Committed as `2d22058` and pushed to `origin/main`.
4. `scripts/verify_site.py` fails on pre-existing wide lines in
   `docs/ARCHITECTURE.md`. `scripts/verify_legal_compliance.py` fails
   Gate 1 on its known licence false positives. This change is
   documentation only, and neither failure is caused by it.

### 10.6 Closed on 14 November 2026

1. **KF-02:** `scripts/sync_calendar.py` ran at 03:42 UTC and imported
   558 events from seven calendars, including the shared and holiday
   calendars, with source `google_calendar`; `last_calendar_sync` is now
   present in `google_sync_state.json`.
2. The nightly maintenance calls the sync and tolerates a failed request.
3. The manual Chambers Advisory Conference entry was preserved.
4. The primary calendar's repeated all-day task reminders are imported;
   the diary labels them separately from timed commitments.
