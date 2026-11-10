"""
Unit Tests for Google Workspace Synchronization Service.

Verifies client credential persistence, authorization URL construction,
and disconnection logic.
"""

from pathlib import Path
from app.google_sync import GoogleWorkspaceSyncService


def test_google_credentials_save_and_url(tmp_path: Path):
    """Verify that credentials save to disk and generate valid OAuth URLs."""
    service = GoogleWorkspaceSyncService()
    service.client_config_file = tmp_path / "google_client_config.json"
    service.credentials_file = tmp_path / "google_credentials.json"

    # Save credentials.
    service.save_client_credentials(
        client_id="test-client-id-12345.apps.googleusercontent.com",
        client_secret="test-client-secret-9988",
    )

    client_id, client_secret = service.get_client_credentials()
    assert client_id == "test-client-id-12345.apps.googleusercontent.com"
    assert client_secret == "test-client-secret-9988"

    # Generate authorization URL.
    auth_url = service.generate_authorization_url()
    assert "https://accounts.google.com/o/oauth2/v2/auth" in auth_url
    assert "test-client-id-12345.apps.googleusercontent.com" in auth_url
    assert "gmail.readonly" in auth_url
    assert "drive.readonly" in auth_url

    # Check status when not connected.
    status = service.get_connection_status()
    assert status["is_configured"] is True
    assert status["is_connected"] is False


def test_google_disconnect(tmp_path: Path):
    """Verify that disconnecting purges stored token files."""
    service = GoogleWorkspaceSyncService()
    cred_file = tmp_path / "google_credentials.json"
    cred_file.write_text('{"access_token": "mock-token"}', encoding="utf-8")
    service.credentials_file = cred_file

    assert service.get_token() is not None
    assert service.disconnect() is True
    assert service.get_token() is None


def test_external_key_file_reading(tmp_path: Path, monkeypatch):
    """Verify that credentials are read from ~/vunderland/keys/heathandcity.txt."""
    service = GoogleWorkspaceSyncService()
    # Ensure no environment variables or local json interfere.
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    service.client_config_file = tmp_path / "nonexistent.json"

    # Mock Path.home() to return tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    keys_dir = tmp_path / "vunderland" / "keys"
    keys_dir.mkdir(parents=True)
    key_file = keys_dir / "heathandcity.txt"
    key_file.write_text(
        'export GOOGLE_CLIENT_ID="ext-id.apps.googleusercontent.com"\n'
        'export GOOGLE_CLIENT_SECRET="ext-secret-12345"\n',
        encoding="utf-8",
    )

    cid, csecret = service.get_client_credentials()
    assert cid == "ext-id.apps.googleusercontent.com"
    assert csecret == "ext-secret-12345"
