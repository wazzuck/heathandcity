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
from pydantic import BaseModel, Field

from .config import settings
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

# In-memory staging queue for active practice tasks.
active_triage_store: List[TriageResult] = []


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
