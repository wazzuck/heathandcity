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
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from .audio import AudioDiarisationEngine
from .config import settings
from .google_sync import GoogleWorkspaceSyncService
from .indexer import HybridIndexEngine
from .ingest import DocumentChunk, DocumentIngestionPipeline
from .rag import RAGEngine
from .tracker import job_tracker, stats_service
from .transactions import TransactionStore
from .triage import InboxTriageEngine, TriageResult

router = APIRouter(prefix="/api")

# Shared service singletons.
ingest_pipeline = DocumentIngestionPipeline()
index_engine = HybridIndexEngine()
tx_store = TransactionStore()
rag_engine = RAGEngine(indexer=index_engine, tx_store=tx_store)
triage_engine = InboxTriageEngine()
google_service = GoogleWorkspaceSyncService()
audio_engine = AudioDiarisationEngine()

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
    top_k: int = Field(
        default=5, ge=1, le=20, description="Context chunk count."
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model override tag.",
    )


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


class SpeakerTagRequest(BaseModel):
    """Payload to tag speaker cluster IDs with names and roles."""

    dictation_id: str
    tags: Dict[str, Dict[str, str]]


class AttendanceNoteRequest(BaseModel):
    """Payload to generate formal chambers attendance note."""

    dictation_id: str
    matter_title: str = "Client Conference"


class IndexNoteRequest(BaseModel):
    """Payload to index synthesised attendance note into vault."""

    dictation_id: str
    matter_title: str = "Client Conference"


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
    resp = rag_engine.query(
        payload.query,
        top_k=payload.top_k,
        model_override=payload.model,
    )
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
    Ingest files from disk into vector and lexical indexes with job logging.
    """
    scan_dir = (
        settings.sample_docs_dir
        if payload.folder_path is None
        else settings.data_dir / payload.folder_path
    )
    job = job_tracker.create_job(source_type="local_files", total_items=1)
    try:
        chunks = ingest_pipeline.scan_directory(scan_dir)
        job.update_progress(
            processed_items=len(chunks),
            chunks_generated=len(chunks),
            total_items=len(chunks) or 1,
        )
        indexed_count = index_engine.index_chunks(chunks)
        job_tracker.finish_job(job.job_id, chunks_indexed=indexed_count)

        # Recalculate repository statistics.
        all_chunks = index_engine.get_all_chunks()
        stats_service.calculate_statistics(all_chunks, index_engine.count())

        return {
            "status": "success",
            "job_id": job.job_id,
            "scan_directory": str(scan_dir),
            "chunks_extracted": len(chunks),
            "chunks_indexed": indexed_count,
            "total_index_count": index_engine.count(),
        }
    except Exception as err:
        job_tracker.fail_job(job.job_id, str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/stats")
def get_vault_statistics() -> Dict[str, Any]:
    """
    Return comprehensive metrics of all data volume tracked across the vault.
    Uses cached metrics to avoid deserialising vector chunks on every poll.
    """
    cached = stats_service.get_latest_statistics()
    if cached and cached.get("total_chunks_indexed", 0) > 0:
        return cached
    all_chunks = index_engine.get_all_chunks()
    return stats_service.calculate_statistics(all_chunks, index_engine.count())


@router.get("/jobs")
def get_indexing_jobs() -> Dict[str, Any]:
    """
    Return active indexing jobs with ETA calculations and historical runs.
    """
    return {
        "active_jobs": job_tracker.get_active_jobs(),
        "history": job_tracker.get_history(limit=15),
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
    google_service.save_client_credentials(
        payload.client_id, payload.client_secret
    )
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
def handle_google_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
):
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
def sync_gmail(
    max_messages: int = 100,
    use_checkpoint: bool = True,
) -> Dict[str, Any]:
    """
    Synchronise messages from Gmail using checkpointed pagination sweeps.
    """
    job = job_tracker.create_job(source_type="gmail", total_items=max_messages)
    try:
        existing_ids = index_engine.get_indexed_ids()

        def on_progress(proc: int, total: int, gen: int) -> None:
            job.update_progress(
                processed_items=proc,
                total_items=total or max_messages,
                chunks_generated=gen,
            )

        chunks = google_service.fetch_and_parse_gmails(
            max_messages=max_messages,
            use_checkpoint=use_checkpoint,
            existing_chunk_ids=existing_ids,
            progress_callback=on_progress,
        )
        indexed = index_engine.index_chunks(chunks)
        job_tracker.finish_job(job.job_id, chunks_indexed=indexed)

        # Update stats incrementally without heap deserialisation.
        stats_service.update_incremental(chunks, index_engine.count())

        # Extract transactions from newly indexed correspondence into ledger.
        for c in chunks:
            subj_m = re.search(r"Subject:\s*(.+)", c.text)
            subj = subj_m.group(1).strip() if subj_m else c.file_name
            from_m = re.search(r"From:\s*(.+)", c.text)
            sender = from_m.group(1).strip() if from_m else ""
            date_m = re.search(r"Date:\s*(.+)", c.text)
            date_h = date_m.group(1).strip() if date_m else ""
            tx = tx_store.extract_from_email(
                chunk_id=c.chunk_id,
                subject=subj,
                sender=sender,
                date_header=date_h,
                text=c.text,
            )
            if tx:
                tx_store.insert_transaction(tx)

        return {
            "status": "success",
            "job_id": job.job_id,
            "messages_fetched": len(chunks),
            "chunks_indexed": indexed,
            "total_vault_volume": index_engine.count(),
        }
    except Exception as err:
        job_tracker.fail_job(job.job_id, str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/google/sync-docs")
def sync_google_docs(max_files: Optional[int] = None) -> Dict[str, Any]:
    """
    Synchronise Google Docs from Google Drive across entire corpus.
    """
    job = job_tracker.create_job(source_type="google_docs", total_items=191)
    try:
        existing_ids = index_engine.get_indexed_ids()

        def on_progress(proc: int, total: int, gen: int) -> None:
            job.update_progress(
                processed_items=proc,
                total_items=total or 191,
                chunks_generated=gen,
            )

        chunks = google_service.fetch_and_parse_google_docs(
            max_files=max_files,
            existing_chunk_ids=existing_ids,
            progress_callback=on_progress,
        )
        indexed = index_engine.index_chunks(chunks)
        job_tracker.finish_job(job.job_id, chunks_indexed=indexed)

        # Update stats incrementally without heap deserialisation.
        stats_service.update_incremental(chunks, index_engine.count())

        # Extract transactions from newly indexed correspondence into ledger.
        for c in chunks:
            subj_m = re.search(r"Subject:\s*(.+)", c.text)
            subj = subj_m.group(1).strip() if subj_m else c.file_name
            from_m = re.search(r"From:\s*(.+)", c.text)
            sender = from_m.group(1).strip() if from_m else ""
            date_m = re.search(r"Date:\s*(.+)", c.text)
            date_h = date_m.group(1).strip() if date_m else ""
            tx = tx_store.extract_from_email(
                chunk_id=c.chunk_id,
                subject=subj,
                sender=sender,
                date_header=date_h,
                text=c.text,
            )
            if tx:
                tx_store.insert_transaction(tx)

        return {
            "status": "success",
            "job_id": job.job_id,
            "docs_fetched": len(chunks),
            "chunks_indexed": indexed,
            "total_vault_volume": index_engine.count(),
        }
    except Exception as err:
        job_tracker.fail_job(job.job_id, str(err))
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/google/sync-state")
def get_google_sync_state() -> Dict[str, Any]:
    """
    Return incremental Google Docs synchronisation state and timestamps.
    """
    return google_service.get_sync_state()


@router.post("/google/auto-sync")
def trigger_google_auto_sync() -> Dict[str, Any]:
    """
    Detect newly added or modified Google Docs and automatically index them.
    """
    job = job_tracker.create_job(
        source_type="google_docs_incremental", total_items=10
    )
    try:
        new_chunks = google_service.detect_and_sync_new_docs(max_files=50)
        indexed = 0
        if new_chunks:
            indexed = index_engine.index_chunks(new_chunks)
            job.update_progress(
                processed_items=len(new_chunks),
                chunks_generated=len(new_chunks),
                total_items=len(new_chunks),
            )
            job_tracker.finish_job(job.job_id, chunks_indexed=indexed)
            all_chunks = index_engine.get_all_chunks()
            stats_service.calculate_statistics(all_chunks, index_engine.count())
        else:
            job_tracker.finish_job(job.job_id, chunks_indexed=0)

        state = google_service.get_sync_state()
        return {
            "status": "success",
            "job_id": job.job_id,
            "new_docs_detected": len(new_chunks),
            "chunks_indexed": indexed,
            "last_doc_sync": state.get("last_doc_sync"),
            "total_vault_volume": index_engine.count(),
        }
    except Exception as err:
        job_tracker.fail_job(job.job_id, str(err))
        raise HTTPException(status_code=500, detail=str(err))


# ==============================================================================
# Sovereign Audio Dictation & Speaker Diarisation Endpoints
# ==============================================================================


@router.post("/audio/transcribe")
async def transcribe_audio_upload(
    file: UploadFile = File(...),
    max_speakers: int = Form(default=4),
) -> Dict[str, Any]:
    """
    Upload and transcribe audio recording with local speaker diarisation.

    Execution steps:
      1. Step 1: Save uploaded recording stream to external storage.
      2. Step 2: Execute Faster-Whisper transcription and speaker clustering.
      3. Step 3: Return structured speech turns with timestamp ranges.
    """
    dictation_dir = settings.data_dir / "dictations" / "uploads"
    dictation_dir.mkdir(parents=True, exist_ok=True)
    temp_file = dictation_dir / f"upload_{file.filename}"

    content = await file.read()
    temp_file.write_bytes(content)

    try:
        res = audio_engine.transcribe_audio_file(
            temp_file, max_speakers=max_speakers
        )
        return res
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/audio/tag")
def tag_audio_speakers(payload: SpeakerTagRequest) -> Dict[str, Any]:
    """
    Assign human identity names and institutional roles to speaker cluster IDs.
    """
    try:
        return audio_engine.tag_speakers(
            dictation_id=payload.dictation_id,
            tag_mapping=payload.tags,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dictation not found.")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/audio/attendance-note")
def generate_chambers_note(payload: AttendanceNoteRequest) -> Dict[str, Any]:
    """
    Generate formal Chambers Attendance Note or Clinical Consultation note.
    """
    try:
        note_text = audio_engine.generate_attendance_note(
            dictation_id=payload.dictation_id,
            matter_title=payload.matter_title,
        )
        return {
            "dictation_id": payload.dictation_id,
            "matter_title": payload.matter_title,
            "attendance_note": note_text,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dictation not found.")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/audio/index-to-vault")
def index_audio_note_to_vault(payload: IndexNoteRequest) -> Dict[str, Any]:
    """
    Index synthesised attendance note directly into sovereign Practice Vault.
    """
    try:
        note_text = audio_engine.generate_attendance_note(
            dictation_id=payload.dictation_id,
            matter_title=payload.matter_title,
        )
        chunk = DocumentChunk(
            chunk_id=f"audio#{payload.dictation_id}#p1#c0",
            source_path=f"audio://{payload.dictation_id}",
            file_name=f"Attendance Note: {payload.matter_title}",
            page_number=1,
            section_heading="Conference Attendance Note",
            text=note_text,
            modified_at=datetime.now(timezone.utc).isoformat(),
        )
        indexed = index_engine.index_chunks([chunk])
        stats_service.update_incremental([chunk], index_engine.count())
        return {
            "status": "success",
            "message": "Attendance note indexed into Practice Vault.",
            "chunk_id": chunk.chunk_id,
            "chunks_indexed": indexed,
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


# ==============================================================================
# Transaction Ledger & Deterministic Accounting Endpoints
# ==============================================================================


@router.get("/transactions/summary")
def get_transaction_summary() -> Dict[str, Any]:
    """
    Return cumulative financial overview, year-by-year totals, and top vendors.
    """
    res = tx_store.query_transactions(limit=10)
    # Extract distinct year metrics.
    with tx_store._get_connection() as conn:
        year_rows = conn.execute(
            """
            SELECT year, count(*), COALESCE(sum(amount_minor), 0)
            FROM transactions
            GROUP BY year
            ORDER BY year DESC;
            """
        ).fetchall()
        years = [
            {
                "year": r[0],
                "count": r[1],
                "total_minor": r[2],
                "total_display": f"£{r[2] / 100.0:,.2f}",
            }
            for r in year_rows
        ]

    return {
        "count": res.get("count", 0),
        "total_display": res.get("total_display", "£0.00"),
        "top_merchants": res.get("merchant_breakdown", []),
        "year_summary": years,
    }


@router.get("/transactions/ledger")
def get_transaction_ledger(
    year: Optional[int] = None,
    merchant: Optional[str] = None,
    limit: int = 100,
    format: str = "json",
) -> Any:
    """
    Query individual transaction rows with optional CSV export format.
    """
    res = tx_store.query_transactions(year=year, merchant=merchant, limit=limit)
    if format.lower() == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Date", "Year", "Month", "Merchant",
            "Description", "Amount", "Currency", "Subject"
        ])
        for t in res.get("transactions", []):
            writer.writerow([
                t.get("id"),
                t.get("transaction_date"),
                t.get("year"),
                t.get("month"),
                t.get("merchant"),
                t.get("item_description"),
                t.get("amount_display"),
                t.get("currency"),
                t.get("subject"),
            ])
        csv_bytes = output.getvalue().encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=practice_ledger_{year or 'all'}.csv"
                )
            },
        )

    return res
