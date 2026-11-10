# Autonomous Agent Instructions: Google OAuth 2.0 Credentials Setup

> Operational instruction manual for an Artificial Intelligence (AI) agent or
> automated browser operator tasked with provisioning Google Cloud OAuth 2.0
> credentials for the Heath & City Practice Vault appliance.
> Target Environment: Google Cloud Console and local Practice Vault host.
> Language: British Professional English (AGENTS.md Policy 15 compliant).

---

## 1. Objective and System Context

You are tasked with provisioning an Open Authorization 2.0 (OAuth 2.0) Client ID
and Client Secret from the Google Cloud Console, and registering them with the
local Heath & City Practice Vault running at `http://127.0.0.1:8080`.

The appliance requires read-only access to Google Mail (Gmail) and Google Drive
to enable autonomous practice clerk intake and private document indexing into
on-premises vector storage.

---

## 2. Binding Operational Parameters

| Parameter | Required Value | Notes |
| :--- | :--- | :--- |
| **Application Type** | `Web application` | Mandatory for OAuth 2.0 callback flow. |
| **Application Name** | `Heath & City Practice Vault` | Identifies client on consent screen. |
| **Authorised Redirect URI** | `http://127.0.0.1:8080/api/google/callback` | Exact match required by Google. |
| **Required Scope 1** | `https://www.googleapis.com/auth/gmail.readonly` | Read-only inbox intake. |
| **Required Scope 2** | `https://www.googleapis.com/auth/drive.readonly` | Read-only Google Docs export. |
| **User Type** | `External` (or `Internal` for Workspace) | Testing mode supported. |

---

## 3. Step-by-Step Procedure for the AI Agent

### Step 1: Enable Mandatory Google APIs
1. Navigate to or execute Google Cloud CLI / Browser navigation to:
   - Gmail API:
     `https://console.cloud.google.com/apis/library/gmail.googleapis.com`
   - Click **"Enable"** (or execute: `gcloud services enable gmail.googleapis.com`).
2. Navigate to:
   - Google Drive API:
     `https://console.cloud.google.com/apis/library/drive.googleapis.com`
   - Click **"Enable"** (or execute: `gcloud services enable drive.googleapis.com`).

### Step 2: Configure OAuth Consent Screen
1. Navigate to:
   `https://console.cloud.google.com/apis/credentials/consent`
2. Select **External** (if using personal `@gmail.com`) or **Internal** (if on a
   Google Workspace domain), then click **Create**.
3. Under **App Information**:
   - App name: `Heath & City Practice Vault`
   - User support email: Select current authenticated operator account.
   - Developer contact information: Enter operator email.
4. Under **Scopes**:
   - Click **"Add or Remove Scopes"**.
   - Select `https://www.googleapis.com/auth/gmail.readonly`.
   - Select `https://www.googleapis.com/auth/drive.readonly`.
   - Click **Update**.
5. Under **Test Users** (if User Type is External):
   - Add the target user's Gmail address to allow authentication while in testing
     mode.
   - Click **Save and Continue**.

### Step 3: Create OAuth 2.0 Client ID & Extract Secret
1. Navigate to:
   `https://console.cloud.google.com/apis/credentials`
2. Click **"+ Create Credentials"** &rarr; Select **"OAuth client ID"**.
3. Select **Application type**: `Web application`.
4. Name: `Practice Vault Local Web Client`.
5. Under **Authorised redirect URIs**, click **"+ Add URI"** and enter:
   `http://127.0.0.1:8080/api/google/callback`
6. Click **Create**.
7. In the resulting modal:
   - Copy the **Client ID** (format: `[digits]-[hash].apps.googleusercontent.com`).
   - Copy the **Client secret** (format: `GOCSPX-[alphanumeric-secret]`).
   - If modal closes, click on the client name in the table to view and copy the
     Client secret on the right sidebar.

### Step 4: Inject Credentials into Practice Vault
Register the acquired credentials using either the REST API or filesystem:

#### Method A: Via Local REST Endpoint (Preferred)
Execute an HTTP POST request to the local vault daemon:
```bash
curl -X POST http://127.0.0.1:8080/api/google/configure \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "PASTE_CLIENT_ID_HERE",
    "client_secret": "PASTE_CLIENT_SECRET_HERE"
  }'
```

#### Method B: Direct Filesystem Injection
Write the JSON payload directly to:
`/home/neville/heathandcity/practice-vault/data/google_client_config.json`
```json
{
  "client_id": "PASTE_CLIENT_ID_HERE",
  "client_secret": "PASTE_CLIENT_SECRET_HERE"
}
```

---

## 4. Verification and Acceptance Checks

The agent must confirm successful configuration by executing:
1. `curl -s http://127.0.0.1:8080/api/google/status`
   - Must return: `{"is_configured": true, ...}`.
2. `curl -s http://127.0.0.1:8080/api/google/auth-url`
   - Must return a valid Google accounts login URL containing the registered
     Client ID and redirect URI.
3. Prompt operator or open browser to complete one-time Google consent.
