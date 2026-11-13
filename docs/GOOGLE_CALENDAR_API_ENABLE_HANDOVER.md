# Enabling the Google Calendar API: Browser Agent Handover

> Purpose: let a browser-capable Artificial Intelligence (AI) agent enable
> the Google Calendar API for the Practice Vault appliance. This is one
> console change. It does not require re-consent, a new token, a new scope
> or a code change.
> Date: 13 November 2026.
> Status: action required. The OAuth token is valid; only the API is off.
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

1. `GoogleWorkspaceSyncService.fetch_calendar_events()` exists but has no
   caller in the current codebase.
2. There is no scheduled calendar sync, and no `last_calendar_sync` key in
   `google_sync_state.json`.
3. The local `calendar_events` table currently holds one manual entry,
   the Chambers Advisory Conference on 19 November 2026, with source
   `manual_diary`.

A separate engineering change is required: a calendar sync script that
upserts Google events with source `google_calendar`, a nightly step that
calls it, and a recorded sync timestamp. Record that as a known failure
until it is built and tested. Until then, enabling the API lets an
operator read the calendar on demand but does not update the diary
automatically.

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
