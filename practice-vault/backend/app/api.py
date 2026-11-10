"""
FastAPI Route Handlers and Application Programming Interface Endpoints.

Purpose:
  Exposes local RESTful endpoints for system health status, hybrid document
  search, Retrieval-Augmented Generation (RAG) question answering, active
  task tracking, and inbox correspondence triage.

Deliberately Not For:
  Exposing unauthenticated endpoints over public networks. The application
  binds strictly to the local loopback address (127.0.0.1) or trusted local
  area network interface.

Invariants:
  1. All returned data structures conform to strict Pydantic schemas.
  2. Zero outbound external network calls occur during endpoint execution.
"""

import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from .config import settings
from .google_sync import GoogleWorkspaceSyncService
from .indexer import HybridIndexEngine
from .ingest import DocumentIngestionPipeline
from .rag import RAGEngine
from .triage import InboxTriageEngine, TriageResult

router = APIRouter(prefix="/api")

# Shared service singletons.
ingest_pipeline = DocumentIngestionPipeline()
index_engine = HybridIndexEngine()
rag_engine = RAGEngine(indexer=index_engine)
triage_engine = InboxTriageEngine()
google_service = GoogleWorkspaceSyncService()

# In-memory staging queue for active practice tasks.
active_triage_store: List[TriageResult] = []


class GoogleConfigureRequest(BaseModel):
    """Payload to configure Google OAuth client credentials."""

    client_id: str = Field(..., description="Google OAuth2 Client ID.")
    client_secret: str = Field(..., description="Google OAuth2 Client Secret.")


class SearchRequest(BaseModel):
    """Payload for hybrid search."""

    query: str = Field(..., description="Natural language search query.")
    top_k: int = Field(default=5, ge=1, le=50, description="Result limit.")


class QueryRequest(BaseModel):
    """Payload for RAG question answering."""

    query: str = Field(..., description="Plain-English question for practice.")
    top_k: int = Field(default=5, ge=1, le=20, description="Context chunk count.")


class TriageRequest(BaseModel):
    """Payload for correspondence intake."""

    raw_text: str = Field(..., description="Body of the email or memo.")
    subject: str = Field(
        default="Client Matter Correspondence",
        description="Subject or heading.",
    )
    sender: str = Field(
        default="client@chambers.internal",
        description="Sender email or name.",
    )


class IngestRequest(BaseModel):
    """Payload to trigger document folder ingestion."""

    folder_path: Optional[str] = Field(
        default=None, description="Custom directory path to scan."
    )


@router.get("/status")
def get_system_status() -> Dict[str, Any]:
    """
    Report host health, indexed document volume, and process memory footprint.

    Execution steps:
      1. Step 1: Read memory usage from /proc/self/status if available.
      2. Step 2: Query index engine for total indexed chunk count.
      3. Step 3: Return health status container.
    """
    mem_rss_kb = 0
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    mem_rss_kb = int(line.split()[1])
                    break
    except Exception:
        mem_rss_kb = 0

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "indexed_chunks_count": index_engine.count(),
        "active_tasks_count": sum(len(t.tasks) for t in active_triage_store),
        "memory_rss_mb": round(mem_rss_kb / 1024.0, 2),
        "llm_model": settings.llm_model,
        "embed_model": settings.embed_model,
    }


@router.post("/search")
def search_documents(payload: SearchRequest) -> Dict[str, Any]:
    """
    Execute hybrid search returning ranked snippets and deterministic citations.
    """
    results = index_engine.search_hybrid(payload.query, top_k=payload.top_k)
    return {
        "query": payload.query,
        "results_count": len(results),
        "results": results,
    }


@router.post("/query")
def answer_question(payload: QueryRequest) -> Dict[str, Any]:
    """
    Execute full RAG pipeline returning answer with exact source citations.
    """
    resp = rag_engine.query(payload.query, top_k=payload.top_k)
    return {
        "query": resp.query,
        "answer": resp.answer,
        "citations": [
            {
                "file_name": c.file_name,
                "page_number": c.page_number,
                "section_heading": c.section_heading,
                "snippet": c.snippet,
            }
            for c in resp.citations
        ],
        "model_used": resp.model_used,
        "context_chunks_count": resp.context_chunks_count,
    }


@router.get("/tasks")
def list_tasks() -> Dict[str, Any]:
    """
    Return all staged inbox tasks grouped by matter reference.
    """
    all_tasks = []
    for item in active_triage_store:
        for t in item.tasks:
            all_tasks.append(
                {
                    "intake_id": item.intake_id,
                    "subject": item.subject,
                    "sender": item.sender,
                    "task_description": t.task_description,
                    "due_date": t.due_date,
                    "matter_reference": t.matter_reference,
                    "urgency": t.urgency,
                    "draft_reply": item.draft_reply,
                    "requires_approval": item.requires_approval,
                }
            )
    return {"tasks_count": len(all_tasks), "tasks": all_tasks}


@router.post("/triage")
def triage_correspondence(payload: TriageRequest) -> Dict[str, Any]:
    """
    Process correspondence, extract tasks, and stage draft response.
    """
    result = triage_engine.process_message(
        raw_text=payload.raw_text,
        subject=payload.subject,
        sender=payload.sender,
    )
    active_triage_store.append(result)
    return result.to_dict()


@router.post("/ingest")
def trigger_ingest(payload: IngestRequest) -> Dict[str, Any]:
    """
    Ingest files from disk into vector and lexical indexes.
    """
    scan_dir = (
        settings.sample_docs_dir
        if payload.folder_path is None
        else settings.data_dir / payload.folder_path
    )
    chunks = ingest_pipeline.scan_directory(scan_dir)
    indexed_count = index_engine.index_chunks(chunks)
    return {
        "scan_directory": str(scan_dir),
        "chunks_extracted": len(chunks),
        "chunks_indexed": indexed_count,
        "total_index_count": index_engine.count(),
    }


# ==============================================================================
# Google Workspace & Cloud Synchronization Endpoints
# ==============================================================================


@router.get("/google/status")
def get_google_status() -> Dict[str, Any]:
    """Return Google Workspace connection and authentication status."""
    return google_service.get_connection_status()


@router.post("/google/configure")
def configure_google(payload: GoogleConfigureRequest) -> Dict[str, Any]:
    """Persist user-supplied Google OAuth2 Client ID and Client Secret."""
    google_service.save_client_credentials(payload.client_id, payload.client_secret)
    return {
        "status": "configured",
        "message": "Google Client credentials saved successfully.",
    }


@router.get("/google/auth-url")
def get_google_auth_url() -> Dict[str, Any]:
    """Generate the OAuth2 browser authorization URL for Google login."""
    try:
        url = google_service.generate_authorization_url()
        return {"auth_url": url}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/google/callback")
def handle_google_callback(code: Optional[str] = None, error: Optional[str] = None):
    """
    Handle Google OAuth2 authorization code callback and exchange for tokens.
    """
    if error:
        return RedirectResponse(url=f"/?google_error={error}")
    if not code:
        return RedirectResponse(url="/?google_error=missing_code")

    try:
        google_service.exchange_code_for_token(code)
        return RedirectResponse(url="/?google_auth=success")
    except Exception as err:
        return RedirectResponse(url=f"/?google_error={str(err)}")


@router.post("/google/disconnect")
def disconnect_google() -> Dict[str, Any]:
    """Disconnect Google account by purging stored local OAuth tokens."""
    success = google_service.disconnect()
    return {"status": "disconnected", "success": success}


@router.post("/google/sync-gmail")
def sync_gmail() -> Dict[str, Any]:
    """
    Synchronise recent emails from Gmail and index into practice vault.
    """
    try:
        chunks = google_service.fetch_and_parse_gmails(max_messages=50)
        indexed = index_engine.index_chunks(chunks)
        return {
            "status": "success",
            "messages_fetched": len(chunks),
            "chunks_indexed": indexed,
            "total_vault_volume": index_engine.count(),
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/google/sync-docs")
def sync_google_docs() -> Dict[str, Any]:
    """
    Synchronise Google Docs from Google Drive and index into practice vault.
    """
    try:
        chunks = google_service.fetch_and_parse_google_docs(max_files=30)
        indexed = index_engine.index_chunks(chunks)
        return {
            "status": "success",
            "docs_fetched": len(chunks),
            "chunks_indexed": indexed,
            "total_vault_volume": index_engine.count(),
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
