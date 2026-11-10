"""
Google Workspace OAuth2 Authentication and Document Ingestion Module.

Purpose:
  Provides on-premises OAuth2 authorization, token exchange, and read-only
  synchronisation for Google Mail (Gmail) and Google Docs via Google APIs.
  Converts fetched correspondence and documents into indexed DocumentChunk
  instances without transmitting data to any third-party intermediate service.

Deliberately Not For:
  Writing to, modifying, or deleting messages or files on Google Workspace.
  All access scopes are strictly read-only.

Invariants:
  1. Stored tokens remain exclusively in local persistent storage.
  2. Data ingestion executes directly between the client host and Google
     endpoints via Hypertext Transfer Protocol Secure (HTTPS).
"""

import base64
import json
import os
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import httpx

from .config import settings
from .ingest import DocumentChunk


class GoogleWorkspaceSyncService:
    """
    Coordinates Google OAuth2 authentication, Gmail intake, and Google Docs sync.

    Attributes:
      credentials_file: Filesystem path to stored OAuth token JSON.
      client_config_file: Filesystem path to client ID and secret JSON.
    """

    GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
    DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    def __init__(self) -> None:
        """Initialise configuration paths."""
        self.credentials_file = settings.google_credentials_file
        self.client_config_file = settings.google_client_config_file

    def get_client_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Retrieve Google Client ID and Client Secret from file or settings.

        Execution steps:
          1. Step 1: Check environment or settings defaults.
          2. Step 2: If absent, read from persistent client_config_file.
        """
        client_id = settings.google_client_id or os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = settings.google_client_secret or os.environ.get(
            "GOOGLE_CLIENT_SECRET"
        )

        if not client_id or not client_secret:
            if self.client_config_file.exists():
                try:
                    data = json.loads(self.client_config_file.read_text(encoding="utf-8"))
                    client_id = data.get("client_id")
                    client_secret = data.get("client_secret")
                except Exception:
                    pass

        return client_id, client_secret

    def save_client_credentials(self, client_id: str, client_secret: str) -> None:
        """Persist Google OAuth credentials entered by the user."""
        self.client_config_file.parent.mkdir(parents=True, exist_ok=True)
        self.client_config_file.write_text(
            json.dumps({"client_id": client_id.strip(), "client_secret": client_secret.strip()}),
            encoding="utf-8",
        )

    def generate_authorization_url(self) -> str:
        """
        Construct Google OAuth2 authorization URL for user browser login.

        Execution steps:
          1. Step 1: Retrieve client credentials.
          2. Step 2: Build query parameters requesting read-only scopes.
          3. Step 3: Return formatted authorization endpoint link.
        """
        client_id, _ = self.get_client_credentials()
        if not client_id:
            raise ValueError(
                "Google Client ID is not configured. Please supply client credentials."
            )

        params = {
            "client_id": client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.GOOGLE_AUTH_BASE}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange one-time authorization code for permanent access/refresh tokens.

        Execution steps:
          1. Step 1: Form POST request to Google token endpoint.
          2. Step 2: Fetch user profile to identify connected email address.
          3. Step 3: Persist tokens locally to credentials_file.
        """
        client_id, client_secret = self.get_client_credentials()
        if not client_id or not client_secret:
            raise ValueError("Google Client ID or Secret is not configured.")

        payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }

        with httpx.Client(timeout=30.0) as client:
            token_res = client.post(self.GOOGLE_TOKEN_URL, data=payload)
            if token_res.status_code != 200:
                raise RuntimeError(
                    f"Google token exchange failed ({token_res.status_code}): {token_res.text}"
                )
            tokens = token_res.json()

            # Step 2: Fetch user profile.
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            profile_res = client.get(self.GOOGLE_USERINFO_URL, headers=headers)
            profile_email = ""
            if profile_res.status_code == 200:
                profile_email = profile_res.json().get("email", "")

            tokens["connected_email"] = profile_email
            tokens["connected_at"] = datetime.now(timezone.utc).isoformat()

            # Step 3: Persist tokens locally.
            self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
            self.credentials_file.write_text(json.dumps(tokens), encoding="utf-8")
            return tokens

    def get_token(self) -> Optional[Dict[str, Any]]:
        """Load stored OAuth2 token credentials if available."""
        if not self.credentials_file.exists():
            return None
        try:
            return json.loads(self.credentials_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def disconnect(self) -> bool:
        """Remove stored OAuth2 tokens to disconnect Google account."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()
            return True
        return False

    def get_connection_status(self) -> Dict[str, Any]:
        """Return connected account state and email."""
        client_id, _ = self.get_client_credentials()
        token = self.get_token()

        return {
            "is_configured": bool(client_id),
            "is_connected": bool(token and "access_token" in token),
            "connected_email": token.get("connected_email") if token else None,
            "connected_at": token.get("connected_at") if token else None,
        }

    def fetch_and_parse_gmails(self, max_messages: int = 50) -> List[DocumentChunk]:
        """
        Synchronise messages from Gmail and convert to DocumentChunks.

        Execution steps:
          1. Step 1: Verify valid access token.
          2. Step 2: List recent messages via Gmail REST API.
          3. Step 3: For each message ID, fetch detailed body and headers.
          4. Step 4: Construct DocumentChunk instance for each email.
        """
        token = self.get_token()
        if not token or "access_token" not in token:
            raise RuntimeError("Google account is not authenticated.")

        headers = {"Authorization": f"Bearer {token['access_token']}"}
        chunks: List[DocumentChunk] = []

        with httpx.Client(timeout=40.0) as client:
            list_res = client.get(
                f"{self.GMAIL_API_BASE}/messages?maxResults={max_messages}",
                headers=headers,
            )
            if list_res.status_code != 200:
                raise RuntimeError(f"Gmail list query failed: {list_res.text}")

            messages = list_res.json().get("messages", [])

            for msg_meta in messages:
                msg_id = msg_meta.get("id")
                msg_res = client.get(
                    f"{self.GMAIL_API_BASE}/messages/{msg_id}?format=full",
                    headers=headers,
                )
                if msg_res.status_code != 200:
                    continue

                msg_data = msg_res.json()
                headers_list = msg_data.get("payload", {}).get("headers", [])

                subject = "Untitled Email"
                sender = "Unknown Sender"
                date_str = ""
                for h in headers_list:
                    name = h.get("name", "").lower()
                    if name == "subject":
                        subject = h.get("value", "")
                    elif name == "from":
                        sender = h.get("value", "")
                    elif name == "date":
                        date_str = h.get("value", "")

                body_text = self._extract_gmail_body(msg_data.get("payload", {}))
                if not body_text:
                    body_text = msg_data.get("snippet", "")

                full_content = (
                    f"Subject: {subject}\nFrom: {sender}\nDate: {date_str}\n\n"
                    f"{body_text}"
                )

                chunk = DocumentChunk(
                    chunk_id=f"gmail#{msg_id}#p1#c0",
                    source_path=f"gmail://{msg_id}",
                    file_name=f"Gmail: {subject[:40]}",
                    page_number=1,
                    section_heading=f"Email from {sender}",
                    text=full_content,
                    modified_at=datetime.now(timezone.utc).isoformat(),
                )
                chunks.append(chunk)

        return chunks

    def fetch_and_parse_google_docs(self, max_files: int = 30) -> List[DocumentChunk]:
        """
        Synchronise Google Docs from Google Drive and convert to DocumentChunks.

        Execution steps:
          1. Step 1: Query Google Drive API for Google Docs documents.
          2. Step 2: Export each document as plain text.
          3. Step 3: Segment text into DocumentChunks preserving file metadata.
        """
        token = self.get_token()
        if not token or "access_token" not in token:
            raise RuntimeError("Google account is not authenticated.")

        headers = {"Authorization": f"Bearer {token['access_token']}"}
        chunks: List[DocumentChunk] = []

        query = "mimeType='application/vnd.google-apps.document' and trashed=false"
        with httpx.Client(timeout=40.0) as client:
            list_res = client.get(
                f"{self.DRIVE_API_BASE}/files?q={urllib.parse.quote(query)}&pageSize={max_files}&fields=files(id,name,modifiedTime)",
                headers=headers,
            )
            if list_res.status_code != 200:
                raise RuntimeError(f"Google Drive query failed: {list_res.text}")

            files = list_res.json().get("files", [])

            for f in files:
                file_id = f.get("id")
                file_name = f.get("name", "Untitled Doc")
                modified_time = f.get("modifiedTime", datetime.now(timezone.utc).isoformat())

                export_res = client.get(
                    f"{self.DRIVE_API_BASE}/files/{file_id}/export?mimeType=text/plain",
                    headers=headers,
                )
                if export_res.status_code != 200:
                    continue

                doc_text = export_res.text.strip()
                if not doc_text:
                    continue

                chunk = DocumentChunk(
                    chunk_id=f"gdoc#{file_id}#p1#c0",
                    source_path=f"gdrive://{file_id}",
                    file_name=f"Google Doc: {file_name}",
                    page_number=1,
                    section_heading=file_name,
                    text=doc_text,
                    modified_at=modified_time,
                )
                chunks.append(chunk)

        return chunks

    def _extract_gmail_body(self, payload: Dict[str, Any]) -> str:
        """Recursively extract plain text body parts from Gmail MIME payload."""
        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data", "")

        if mime_type == "text/plain" and body_data:
            try:
                decoded = base64.urlsafe_b64decode(body_data.encode("ASCII"))
                return decoded.decode("utf-8", errors="replace")
            except Exception:
                return ""

        parts = payload.get("parts", [])
        extracted = []
        for p in parts:
            text = self._extract_gmail_body(p)
            if text:
                extracted.append(text)

        return "\n".join(extracted)
