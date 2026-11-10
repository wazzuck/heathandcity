"""
System Configuration Module for Heath & City Practice Vault.

Purpose:
  Centralises path resolution, network interface bindings, Small Language
  Model (SLM) identifiers, and embedding parameters for the on-premises
  appliance.

Deliberately Not For:
  Handling runtime state, processing raw document contents, or making
  network requests.

Invariants:
  1. Default Hypertext Transfer Protocol (HTTP) server binds exclusively
     to loopback (127.0.0.1) or local interface, never to public interfaces.
  2. All directory paths resolve to absolute filesystem locations.
"""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class SystemSettings(BaseModel):
    """
    Strongly typed settings container for the Practice Vault appliance.

    Attributes:
      app_name: Formal system title rendered on the dashboard and logs.
      host: Local network address bound by the web server.
      port: Transmission Control Protocol (TCP) port for HTTP traffic.
      ollama_base_url: Loopback endpoint of the local Ollama daemon.
      llm_model: Quantised local reasoning model tag.
      embed_model: Local vector embedding model identifier.
      data_dir: Absolute root path for persistent appliance storage.
      lancedb_dir: Path to on-disk LanceDB database tables.
      sample_docs_dir: Directory containing practice files for ingestion.
      inbox_staging_dir: Directory staging incoming emails and memos.
      static_dir: Directory serving frontend assets (HTML, CSS, JS).
    """

    app_name: str = Field(
        default="Heath & City Practice Vault",
        description="Institutional service title.",
    )
    host: str = Field(
        default="127.0.0.1",
        description="Local loopback network interface.",
    )
    port: int = Field(
        default=8080,
        description="Default HTTP listening port.",
    )
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        description="Local Ollama daemon endpoint.",
    )
    llm_model: str = Field(
        default="qwen3.5:4b",
        description="Primary 4-bit quantised local instruction model.",
    )
    embed_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="Default local CPU vector embedding model.",
    )
    data_dir: Path = Field(
        default_factory=lambda: (
            Path("/home/neville/practice-vault-data")
            if Path("/home/neville/practice-vault-data").exists()
            else Path(__file__).resolve().parent.parent.parent / "data"
        ),
        description="Persistent external data root directory.",
    )
    lancedb_dir: Path = Field(
        default_factory=lambda: (
            Path("/home/neville/practice-vault-data/lancedb")
            if Path("/home/neville/practice-vault-data").exists()
            else Path(__file__).resolve().parent.parent.parent
            / "data"
            / "lancedb"
        ),
        description="LanceDB persistent storage directory.",
    )
    sample_docs_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
        / "data"
        / "sample_docs",
        description="Directory holding mock sample practice documentation.",
    )
    inbox_staging_dir: Path = Field(
        default_factory=lambda: (
            Path("/home/neville/practice-vault-data/inbox_staging")
            if Path("/home/neville/practice-vault-data").exists()
            else Path(__file__).resolve().parent.parent.parent
            / "data"
            / "inbox_staging"
        ),
        description="Staging inbox for email triage.",
    )
    static_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
        / "frontend",
        description="Directory serving static frontend files.",
    )
    google_client_id: Optional[str] = Field(
        default=None,
        description="Google OAuth2 Client ID.",
    )
    google_client_secret: Optional[str] = Field(
        default=None,
        description="Google OAuth2 Client Secret.",
    )
    google_redirect_uri: str = Field(
        default="http://127.0.0.1:8080/api/google/callback",
        description="Authorised Google OAuth2 redirect URI.",
    )
    google_credentials_file: Path = Field(
        default_factory=lambda: (
            Path("/home/neville/vunderland/keys/heathandcity_token.json")
            if Path("/home/neville/vunderland/keys/heathandcity_token.json").exists()
            else Path(__file__).resolve().parent.parent.parent
            / "data"
            / "google_credentials.json"
        ),
        description="Local on-disk Google OAuth2 token storage.",
    )
    google_client_config_file: Path = Field(
        default_factory=lambda: (
            Path("/home/neville/practice-vault-data/google_client_config.json")
            if Path("/home/neville/practice-vault-data").exists()
            else Path(__file__).resolve().parent.parent.parent
            / "data"
            / "google_client_config.json"
        ),
        description="Local on-disk Google OAuth2 client secrets storage.",
    )

    def ensure_directories(self) -> None:
        """
        Verify that all mandatory filesystem directories exist on disk.

        Execution steps:
          1. Step 1: Ensure persistent data root exists.
          2. Step 2: Ensure LanceDB vector database directory exists.
          3. Step 3: Ensure sample practice documents directory exists.
          4. Step 4: Ensure inbox staging folder exists.
        """
        # Step 1: Ensure persistent data root exists.
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Step 2: Ensure LanceDB vector database directory exists.
        self.lancedb_dir.mkdir(parents=True, exist_ok=True)

        # Step 3: Ensure sample practice documents directory exists.
        self.sample_docs_dir.mkdir(parents=True, exist_ok=True)

        # Step 4: Ensure inbox staging folder exists.
        self.inbox_staging_dir.mkdir(parents=True, exist_ok=True)


# Global singleton instance used across application modules.
settings = SystemSettings()
settings.ensure_directories()
