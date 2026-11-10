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
import re
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import httpx
import lxml.html

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
        self.sync_state_file = settings.data_dir / "google_sync_state.json"

    def get_sync_state(self) -> Dict[str, Any]:
        """Load persistent Google synchronization timestamps and statistics."""
        if self.sync_state_file.exists():
            try:
                return json.loads(self.sync_state_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "last_doc_sync": None,
            "last_gmail_sync": None,
            "total_synced_docs": 0,
            "auto_sync_enabled": True,
            "poll_interval_seconds": 60,
        }

    def save_sync_state(self, state: Dict[str, Any]) -> None:
        """Persist synchronization timestamps to disk."""
        try:
            self.sync_state_file.parent.mkdir(parents=True, exist_ok=True)
            self.sync_state_file.write_text(
                json.dumps(state, indent=2), encoding="utf-8"
            )
        except Exception:
            pass

    def get_client_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Retrieve Google Client ID and Client Secret.

        Execution steps:
          1. Step 1: Check persistent client_config_file if present.
          2. Step 2: Check environment variables or application settings.
          3. Step 3: Check external key file at ~/vunderland/keys/heathandcity.txt.
        """
        client_id = None
        client_secret = None

        # Step 1: Check persistent client_config_file.
        if self.client_config_file.exists():
            try:
                data = json.loads(self.client_config_file.read_text(encoding="utf-8"))
                client_id = data.get("client_id")
                client_secret = data.get("client_secret")
            except Exception:
                pass

        # Step 2: Check environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET).
        if not client_id or not client_secret:
            client_id = client_id or (
                settings.google_client_id or os.environ.get("GOOGLE_CLIENT_ID")
            )
            client_secret = client_secret or (
                settings.google_client_secret
                or os.environ.get("GOOGLE_CLIENT_SECRET")
            )

        # Step 3: Check external key storage in ~/vunderland/keys/heathandcity.txt
        if not client_id or not client_secret:
            ext_key_file = Path.home() / "vunderland" / "keys" / "heathandcity.txt"
            if ext_key_file.exists():
                try:
                    for line in ext_key_file.read_text(encoding="utf-8").splitlines():
                        clean_line = line.strip()
                        if clean_line.startswith("export "):
                            clean_line = clean_line[7:].strip()
                        if "=" in clean_line:
                            k, v = clean_line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k == "GOOGLE_CLIENT_ID" and not client_id:
                                client_id = v
                            elif k == "GOOGLE_CLIENT_SECRET" and not client_secret:
                                client_secret = v
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
            self._save_tokens_to_disk(tokens)
            return tokens

    def _save_tokens_to_disk(self, tokens: Dict[str, Any]) -> None:
        """
        Persist OAuth2 tokens to disk, preserving external symlinks.

        Args:
          tokens: Token payload dictionary.
        """
        target_path = self.credentials_file.resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(tokens, indent=2), encoding="utf-8")

    def refresh_access_token(self) -> str:
        """
        Refresh Google OAuth2 access token using stored refresh_token.

        Execution steps:
          1. Step 1: Retrieve stored tokens from disk.
          2. Step 2: Validate presence of refresh_token.
          3. Step 3: Fetch client ID and client secret.
          4. Step 4: POST grant_type=refresh_token to GOOGLE_TOKEN_URL.
          5. Step 5: Merge and save updated tokens to disk.
          6. Step 6: Return refreshed access token.

        Returns:
          Fresh access token string.

        Raises:
          RuntimeError: If refresh token is missing or Google returns an error.
        """
        tokens = self.get_token()
        if not tokens or "refresh_token" not in tokens:
            raise RuntimeError(
                "Cannot refresh token: No refresh_token found in credentials."
            )

        client_id, client_secret = self.get_client_credentials()
        if not client_id or not client_secret:
            raise RuntimeError(
                "Cannot refresh token: Client ID or Secret is not configured."
            )

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": tokens["refresh_token"],
            "grant_type": "refresh_token",
        }

        with httpx.Client(timeout=30.0) as client:
            res = client.post(self.GOOGLE_TOKEN_URL, data=payload)
            if res.status_code != 200:
                raise RuntimeError(
                    f"Google token refresh failed ({res.status_code}): {res.text}"
                )
            new_data = res.json()
            tokens.update(new_data)
            tokens["refreshed_at"] = datetime.now(timezone.utc).isoformat()
            self._save_tokens_to_disk(tokens)
            return str(tokens["access_token"])

    def get_valid_access_token(self, force_refresh: bool = False) -> str:
        """
        Return an active access token, refreshing if requested or missing.

        Args:
          force_refresh: Whether to proactively refresh via OAuth endpoint.

        Returns:
          Valid access token string.
        """
        if force_refresh:
            return self.refresh_access_token()

        token = self.get_token()
        if not token or "access_token" not in token:
            raise RuntimeError("Google account is not authenticated.")

        return str(token["access_token"])

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
        target = self.credentials_file.resolve()
        if target.exists():
            target.unlink()
            if self.credentials_file.is_symlink():
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

    def fetch_and_parse_gmails(
        self,
        max_messages: int = 50,
        page_token: Optional[str] = None,
        use_checkpoint: bool = False,
        existing_chunk_ids: Optional[Any] = None,
        progress_callback: Optional[Any] = None,
    ) -> List[DocumentChunk]:
        """
        Synchronise messages from Gmail and convert to DocumentChunks.

        Execution steps:
          1. Step 1: Verify valid access token (auto-refreshing if expired).
          2. Step 2: Retrieve message IDs using pagination tokens.
          3. Step 3: Filter out message IDs already indexed.
          4. Step 4: Fetch detailed headers and body for unindexed messages.
          5. Step 5: Checkpoint next_page_token and update sync state.
        """
        access_token = self.get_valid_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        chunks: List[DocumentChunk] = []

        curr_token = page_token
        if use_checkpoint and curr_token is None:
            state = self.get_sync_state()
            curr_token = state.get("gmail_next_page_token")

        messages: List[Dict[str, Any]] = []
        next_token: Optional[str] = None

        with httpx.Client(timeout=40.0) as client:
            while len(messages) < max_messages:
                batch_limit = min(max_messages - len(messages), 100)
                url = f"{self.GMAIL_API_BASE}/messages?maxResults={batch_limit}"
                if curr_token:
                    url += f"&pageToken={curr_token}"

                list_res = client.get(url, headers=headers)
                if list_res.status_code == 401:
                    access_token = self.refresh_access_token()
                    headers = {"Authorization": f"Bearer {access_token}"}
                    list_res = client.get(url, headers=headers)
                elif list_res.status_code in (403, 429):
                    # Google API per-minute quota exceeded; back off 35 seconds.
                    time.sleep(35.0)
                    list_res = client.get(url, headers=headers)

                if list_res.status_code != 200:
                    raise RuntimeError(
                        f"Gmail list query failed: {list_res.text}"
                    )

                data = list_res.json()
                batch_msgs = data.get("messages", [])
                messages.extend(batch_msgs)
                next_token = data.get("nextPageToken")
                curr_token = next_token
                if not curr_token or not batch_msgs:
                    break

            # Filter out messages already indexed.
            messages_to_fetch = [
                m for m in messages
                if not existing_chunk_ids
                or f"gmail#{m.get('id')}#p1#c0" not in existing_chunk_ids
            ]

            total_to_process = len(messages_to_fetch)
            for idx, msg_meta in enumerate(messages_to_fetch, start=1):
                msg_id = msg_meta.get("id")
                msg_res = client.get(
                    f"{self.GMAIL_API_BASE}/messages/{msg_id}?format=full",
                    headers=headers,
                )
                if msg_res.status_code == 401:
                    access_token = self.refresh_access_token()
                    headers = {"Authorization": f"Bearer {access_token}"}
                    msg_res = client.get(
                        f"{self.GMAIL_API_BASE}/messages/{msg_id}?format=full",
                        headers=headers,
                    )
                elif msg_res.status_code in (403, 429):
                    # Google API per-minute quota exceeded; back off 35 seconds.
                    time.sleep(35.0)
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

                body_text = self._extract_gmail_body(
                    msg_data.get("payload", {})
                )
                if not body_text:
                    body_text = msg_data.get("snippet", "")

                # Parse internalDate (epoch milliseconds) into ISO UTC string.
                internal_date_ms = msg_data.get("internalDate")
                source_iso = None
                if internal_date_ms:
                    try:
                        source_iso = datetime.fromtimestamp(
                            int(internal_date_ms) / 1000.0, tz=timezone.utc
                        ).isoformat()
                    except Exception:
                        pass
                if not source_iso:
                    source_iso = datetime.now(timezone.utc).isoformat()

                header_prefix = (
                    f"Subject: {subject}\nFrom: {sender}\nDate: {date_str}\n\n"
                )

                words = body_text.split()
                if len(words) <= 400:
                    chunk = DocumentChunk(
                        chunk_id=f"gmail#{msg_id}#p1#c0",
                        source_path=f"gmail://{msg_id}",
                        file_name=f"Gmail: {subject[:40]}",
                        page_number=1,
                        section_heading=f"Email from {sender}",
                        text=header_prefix + body_text,
                        modified_at=source_iso,
                    )
                    chunks.append(chunk)
                else:
                    # Segment multi-page or lengthy correspondence (400 words).
                    step_size = 350
                    c_idx = 0
                    for w_start in range(0, len(words), step_size):
                        window = words[w_start : w_start + 400]
                        segment_text = " ".join(window)
                        chunk = DocumentChunk(
                            chunk_id=f"gmail#{msg_id}#p1#c{c_idx}",
                            source_path=f"gmail://{msg_id}",
                            file_name=f"Gmail: {subject[:40]}",
                            page_number=1,
                            section_heading=(
                                f"Email from {sender} (Part {c_idx + 1})"
                            ),
                            text=header_prefix + segment_text,
                            modified_at=source_iso,
                        )
                        chunks.append(chunk)
                        c_idx += 1
                        if w_start + 400 >= len(words):
                            break

                if progress_callback:
                    try:
                        progress_callback(idx, total_to_process, len(chunks))
                    except Exception:
                        pass

        # Update persistent sync timestamp.
        state = self.get_sync_state()
        state["last_gmail_sync"] = datetime.now(timezone.utc).isoformat()
        state["total_synced_gmails"] = (
            state.get("total_synced_gmails", 0) + len(chunks)
        )
        state["gmail_next_page_token"] = next_token
        self.save_sync_state(state)

        return chunks

    def fetch_and_parse_google_docs(
        self,
        max_files: Optional[int] = None,
        existing_chunk_ids: Optional[Any] = None,
        progress_callback: Optional[Any] = None,
    ) -> List[DocumentChunk]:
        """
        Synchronise Google Docs from Google Drive and convert to DocumentChunks.

        Execution steps:
          1. Step 1: Query Google Drive API using pagination tokens to collect
             matching Google Docs metadata across entire corpus.
          2. Step 2: Filter out documents whose chunk_ids already reside in
             the vault index to minimise redundant export latency.
          3. Step 3: Export each unindexed document as plain text.
          4. Step 4: Segment text into DocumentChunks preserving file metadata.
          5. Step 5: Update persistent sync timestamps and totals.
        """
        access_token = self.get_valid_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        chunks: List[DocumentChunk] = []

        query = (
            "mimeType='application/vnd.google-apps.document' and trashed=false"
        )
        files: List[Dict[str, Any]] = []
        page_token: Optional[str] = None

        with httpx.Client(timeout=40.0) as client:
            # Step 1: Collect document records across pages.
            while True:
                page_size = (
                    min(max_files - len(files), 100) if max_files else 100
                )
                if page_size <= 0:
                    break
                url = (
                    f"{self.DRIVE_API_BASE}/files?q={urllib.parse.quote(query)}"
                    f"&pageSize={page_size}"
                    f"&fields=nextPageToken,files(id,name,modifiedTime)"
                )
                if page_token:
                    url += f"&pageToken={page_token}"

                list_res = client.get(url, headers=headers)
                if list_res.status_code == 401:
                    access_token = self.refresh_access_token()
                    headers = {"Authorization": f"Bearer {access_token}"}
                    list_res = client.get(url, headers=headers)

                if list_res.status_code != 200:
                    raise RuntimeError(
                        f"Google Drive query failed: {list_res.text}"
                    )

                data = list_res.json()
                batch_files = data.get("files", [])
                files.extend(batch_files)
                page_token = data.get("nextPageToken")
                if not page_token or (max_files and len(files) >= max_files):
                    break

            # Step 2: Filter out documents already indexed.
            files_to_export = [
                f for f in files
                if not existing_chunk_ids
                or f"gdoc#{f.get('id')}#p1#c0" not in existing_chunk_ids
            ]

            total_to_process = len(files_to_export)
            for idx, f in enumerate(files_to_export, start=1):
                file_id = f.get("id")
                file_name = f.get("name", "Untitled Doc")
                modified_time = f.get(
                    "modifiedTime", datetime.now(timezone.utc).isoformat()
                )

                export_res = client.get(
                    f"{self.DRIVE_API_BASE}/files/{file_id}/export?mimeType=text/plain",
                    headers=headers,
                )
                if export_res.status_code == 401:
                    access_token = self.refresh_access_token()
                    headers = {"Authorization": f"Bearer {access_token}"}
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

                if progress_callback:
                    try:
                        progress_callback(idx, total_to_process, len(chunks))
                    except Exception:
                        pass

        # Update persistent sync timestamp.
        state = self.get_sync_state()
        state["last_doc_sync"] = datetime.now(timezone.utc).isoformat()
        state["total_synced_docs"] = (
            state.get("total_synced_docs", 0) + len(chunks)
        )
        self.save_sync_state(state)

        return chunks

    def detect_and_sync_new_docs(self, max_files: int = 50) -> List[DocumentChunk]:
        """
        Detect and ingest newly added or modified Google Docs since last sync.

        Execution steps:
          1. Step 1: Read last_doc_sync timestamp from state.
          2. Step 2: Build Drive query filtering by modifiedTime > last_sync.
          3. Step 3: Fetch, export, and segment newly detected documents.
          4. Step 4: Advance last_doc_sync timestamp to current UTC time.

        Args:
          max_files: Maximum new documents processed per cycle.

        Returns:
          List of DocumentChunk instances for newly added or modified docs.
        """
        token = self.get_token()
        if not token or "access_token" not in token:
            return []

        state = self.get_sync_state()
        last_sync = state.get("last_doc_sync")

        # If no previous sync timestamp exists, fall back to initial sync.
        if not last_sync:
            return self.fetch_and_parse_google_docs(max_files=max_files)

        access_token = self.get_valid_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        chunks: List[DocumentChunk] = []

        query = (
            f"mimeType='application/vnd.google-apps.document' and "
            f"trashed=false and modifiedTime > '{last_sync}'"
        )

        with httpx.Client(timeout=40.0) as client:
            list_res = client.get(
                f"{self.DRIVE_API_BASE}/files?q={urllib.parse.quote(query)}"
                f"&pageSize={max_files}&fields=files(id,name,modifiedTime)",
                headers=headers,
            )
            if list_res.status_code == 401:
                access_token = self.refresh_access_token()
                headers = {"Authorization": f"Bearer {access_token}"}
                list_res = client.get(
                    f"{self.DRIVE_API_BASE}/files?q={urllib.parse.quote(query)}"
                    f"&pageSize={max_files}&fields=files(id,name,modifiedTime)",
                    headers=headers,
                )

            if list_res.status_code != 200:
                return []

            files = list_res.json().get("files", [])
            for f in files:
                file_id = f.get("id")
                file_name = f.get("name", "Untitled Doc")
                modified_time = f.get("modifiedTime", datetime.now(timezone.utc).isoformat())

                export_res = client.get(
                    f"{self.DRIVE_API_BASE}/files/{file_id}/export?mimeType=text/plain",
                    headers=headers,
                )
                if export_res.status_code == 401:
                    access_token = self.refresh_access_token()
                    headers = {"Authorization": f"Bearer {access_token}"}
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

        # Advance state timestamp.
        state["last_doc_sync"] = datetime.now(timezone.utc).isoformat()
        state["total_synced_docs"] = state.get("total_synced_docs", 0) + len(chunks)
        self.save_sync_state(state)

        return chunks

    def _extract_gmail_body(self, payload: Dict[str, Any]) -> str:
        """
        Recursively extract message text from a Gmail MIME payload.

        Prefers plain text parts; falls back to Hypertext Markup Language (HTML)
        sanitisation via lxml when plain text is absent or empty.

        Execution steps:
          1. Step 1: Traverse MIME tree and collect text/plain and text/html
             encoded segments.
          2. Step 2: Return concatenated plain text if available.
          3. Step 3: Parse and strip HTML trees if only markup was provided.
        """
        text_plain_parts: List[str] = []
        text_html_parts: List[str] = []

        def _traverse(part: Dict[str, Any]) -> None:
            mime = part.get("mimeType", "")
            raw_data = part.get("body", {}).get("data", "")
            if raw_data:
                try:
                    decoded = base64.urlsafe_b64decode(
                        raw_data.encode("ASCII")
                    ).decode("utf-8", errors="replace")
                    if mime == "text/plain":
                        text_plain_parts.append(decoded)
                    elif mime == "text/html":
                        text_html_parts.append(decoded)
                except Exception:
                    pass
            for subpart in part.get("parts", []):
                _traverse(subpart)

        _traverse(payload)

        # Step 2: Prefer text/plain if non-empty.
        plain_combined = "\n".join(text_plain_parts).strip()
        if plain_combined:
            return plain_combined

        # Step 3: Parse HTML if text/plain was absent.
        if text_html_parts:
            html_raw = "\n".join(text_html_parts)
            try:
                doc = lxml.html.fromstring(html_raw)
                for elem in doc.xpath(
                    "//script | //style | //head | //meta"
                ):
                    elem.drop_tree()
                for elem in doc.xpath(
                    "//p | //div | //tr | //h1 | //h2 | //h3 | //h4 | //br | //li"
                ):
                    elem.tail = (elem.tail or "") + "\n"
                extracted = doc.text_content()
                lines = [
                    line.strip()
                    for line in extracted.splitlines()
                    if line.strip()
                ]
                return "\n".join(lines)
            except Exception:
                cleaned = re.sub(r"<[^>]+>", " ", html_raw)
                return " ".join(cleaned.split())

        return ""
