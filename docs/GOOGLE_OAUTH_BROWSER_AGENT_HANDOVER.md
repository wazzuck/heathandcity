# Google OAuth Restoration: Browser Agent Handover

> Purpose: let a browser-capable Artificial Intelligence (AI) agent restore
> durable Google Workspace authorisation for the Practice Vault appliance.
> Date: 13 November 2026.
> Status: action required before 17 November 2026, 12:19 UTC.
> Language: British Professional English (AGENTS.md Policy 15).
> Line width: 80 columns.

---

## 1. Objective

Restore Gmail, Google Drive and Google Calendar synchronisation so that it
does not stop every seven days. The fix has two parts: publish the OAuth
consent screen to production, then obtain one fresh refresh token.

## 2. Known facts

1. Account: `nevillebryce@gmail.com`, a consumer account, so the OAuth user
   type is **External**.
2. Scopes requested:
   - `https://www.googleapis.com/auth/gmail.readonly` (restricted);
   - `https://www.googleapis.com/auth/drive.readonly`;
   - `https://www.googleapis.com/auth/calendar.readonly`;
   - `userinfo.email` and `userinfo.profile`.
3. Authorised redirect Uniform Resource Identifier (URI):
   `http://127.0.0.1:9090/api/google/callback`.
4. Token file:
   `/home/neville/vunderland/keys/heathandcity_token.json`, symlinked from
   `~/practice-vault-data/google_credentials.json`.
5. Token evidence:
   - `connected_at`: 2026-11-10T12:19:57Z;
   - `refreshed_at`: 2026-11-13T16:58:40Z;
   - `refresh_token_expires_in`: 328,876 seconds at that refresh;
   - inferred refresh-token expiry: 2026-11-17T12:19:56Z.
6. The appliance is currently bound to `127.0.0.1:9090` only, as a
   temporary security measure. The callback must therefore be opened on the
   appliance, or through a Secure Shell (SSH) tunnel.
7. The application programming interface requires the header
   `X-Vault-Password`, whose value is in the server configuration. Do not
   print it, log it or write it into a report.

## 3. Root cause

Google issues a refresh token with a seven-day lifetime to External OAuth
clients whose publishing status is **Testing**. The observed lifetime
matches that rule. Publishing to production removes the seven-day limit;
re-consenting is still required because the existing token keeps its
original expiry.

## 4. What the browser agent must do

### Step 1: Confirm the publishing status

1. Open `https://console.cloud.google.com`.
2. Select the project that owns the OAuth client used by the appliance.
3. Navigate to **APIs & Services → OAuth consent screen**, now also labelled
   **Google Auth Platform → Audience**.
4. Record, verbatim:
   - Publishing status: **Testing** or **In production**.
   - User type: **External** or **Internal**.
5. If the status is already **In production**, stop and report. The cause is
   then elsewhere; do not re-consent blindly.

### Step 2: Publish, only if the status is Testing

1. Click **Publish app** and confirm.
2. If Google asks for scope justification, state: read-only access to
   Gmail, Drive and Calendar for a single-user on-premises appliance; no
   data leaves the host; no third-party access.
3. `gmail.readonly` is a restricted scope. Google may require verification.
   **Do not submit a verification or security-assessment request.** That
   has cost, disclosure and timing consequences and needs the operator's
   decision. If publishing is blocked, stop and report the exact message.
4. Confirm that the authorised redirect URI above is present. Do not add,
   remove or change any other URI.

### Step 3: Re-consent to obtain a new refresh token

1. On the appliance, request the authorisation URL:

```
curl -s -H "X-Vault-Password: ${PRACTICE_VAULT_PASSWORD}" \
  http://127.0.0.1:9090/api/google/auth-url
```

2. Open the returned `auth_url` in the browser.
   - If the browser runs on another machine, tunnel first:
     `ssh -L 9090:127.0.0.1:9090 neville@192.168.0.13`.
3. Approve every requested scope. The callback redirects to
   `/?google_auth=success`.
4. Do not revoke the old token before the new one is confirmed. The old
   token remains valid until its expiry and is the fallback if the new
   consent fails.

### Step 4: Verify the new token

1. Read the token file and check:
   - `connected_at` is today;
   - `refresh_token_expires_in` is absent or far in the future;
   - `refresh_token` is present;
   - no token value is printed in full.
2. Call `GET /api/google/status` with the vault password and confirm
   `is_connected: true` and the correct account.
3. Confirm that `~/practice-vault-data/google_sync_state.json` advances
   `last_gmail_sync` after the next synchronisation cycle.

### Step 5: Resume synchronisation

1. The Gmail indexer is currently disabled on the running service
   (`START_INDEXER=0`). Restart with the indexer enabled once the token is
   confirmed, or run:
   `~/practice-vault/scripts/start_indexer.sh`.
2. The metadata sync may be running separately. It is resumable and needs
   no action beyond a valid token.

## 5. Guardrails

1. Never print, copy or transmit the master password, client secret,
   access token or refresh token.
2. Never delete the Google Cloud project, the OAuth client, or the
   authorised redirect URI.
3. Never change the requested scopes; the appliance depends on all five.
4. Never disable two-step verification or alter account security settings.
5. Never submit a verification, CASA or security-assessment request.
6. Make one change at a time. After each step, report the visible result in
   text or a screenshot.
7. If a page requests a password, one-time code or recovery action, stop
   and hand control back to the operator. Do not attempt to satisfy it.
8. If the console shows an organisation policy or admin restriction, stop
   and report it.

## 6. Success criteria

1. Publishing status is **In production**.
2. A fresh refresh token exists with no seven-day expiry.
3. `/api/google/status` reports connected.
4. `last_gmail_sync` advances.
5. No secret appears in any log or report.

## 7. Rollback

1. If publishing is refused, keep the app in Testing and re-consent weekly.
   Record the next re-consent date.
2. If the new token fails, the old token remains valid until
   2026-11-17T12:19:56Z. Restore the previous token file from backup before
   that time.
3. Do not leave the account disconnected: the archive can still serve
   existing mail, but no new mail arrives.

## 8. Report back

1. Publishing status before and after.
2. Whether verification was requested, and the exact wording if so.
3. New token expiry, or confirmation that it has none.
4. Whether `last_gmail_sync` advanced.
5. Any step that required operator intervention.
