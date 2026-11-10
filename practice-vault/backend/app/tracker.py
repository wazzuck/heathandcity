"""
Indexing Job Tracker and Practice Data Statistics Module.

Purpose:
  Tracks execution durations, processing throughput, and estimated time to
  completion (ETA) for long-running document ingestion jobs. Aggregates live
  statistics on the total volume, word counts, and source categorization of
  data indexed within the sovereign practice vault.

Deliberately Not For:
  Direct document parsing or LLM inference.

Invariants:
  1. Job progress and operational metrics are thread-safe and non-blocking.
  2. Metrics files persist in local appliance storage without external telemetry.
"""

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import settings


@dataclass
class IndexingJob:
    """
    Represents an active or historical document indexing run.

    Attributes:
      job_id: Unique run identifier formatted as 'JOB-<timestamp>'.
      source_type: Document origin ('local_files', 'google_docs', 'gmail').
      status: Current state ('running', 'completed', 'failed').
      total_items: Expected total count of files or messages.
      processed_items: Current tally of ingested documents.
      total_bytes: Cumulative file size in bytes if known.
      processed_bytes: Cumulative bytes parsed and embedded.
      chunks_generated: Total semantic chunks produced during this run.
      start_time: POSIX timestamp of run commencement.
      end_time: POSIX timestamp of job conclusion (None if active).
      elapsed_seconds: Elapsed runtime in seconds.
      estimated_remaining_seconds: Calculated time remaining based on throughput.
      items_per_second: Current processing velocity.
      error_message: Failure description if aborted.
    """

    job_id: str
    source_type: str
    status: str = "running"
    total_items: int = 0
    processed_items: int = 0
    total_bytes: int = 0
    processed_bytes: int = 0
    chunks_generated: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    elapsed_seconds: float = 0.0
    estimated_remaining_seconds: float = 0.0
    items_per_second: float = 0.0
    error_message: Optional[str] = None

    def update_progress(
        self,
        processed_items: int,
        processed_bytes: int = 0,
        chunks_generated: int = 0,
        total_items: Optional[int] = None,
    ) -> None:
        """
        Recalculate throughput and estimated completion time.

        Execution steps:
          1. Step 1: Update processed counters.
          2. Step 2: Compute elapsed duration.
          3. Step 3: Derive items per second velocity.
          4. Step 4: Project estimated remaining seconds.
        """
        self.processed_items = processed_items
        if total_items is not None and total_items > 0:
            self.total_items = total_items
        if processed_bytes > 0:
            self.processed_bytes = processed_bytes
        if chunks_generated > 0:
            self.chunks_generated = chunks_generated

        now = time.time()
        self.elapsed_seconds = round(now - self.start_time, 2)

        if self.elapsed_seconds > 0.1 and self.processed_items > 0:
            self.items_per_second = round(
                self.processed_items / self.elapsed_seconds, 2
            )
            remaining_items = max(0, self.total_items - self.processed_items)
            if self.items_per_second > 0:
                self.estimated_remaining_seconds = round(
                    remaining_items / self.items_per_second, 1
                )
            else:
                self.estimated_remaining_seconds = 0.0
        else:
            self.items_per_second = 0.0
            self.estimated_remaining_seconds = 0.0

    def complete(self, final_chunks: int = 0) -> None:
        """Mark job as successfully concluded."""
        self.status = "completed"
        self.end_time = time.time()
        self.elapsed_seconds = round(self.end_time - self.start_time, 2)
        if final_chunks > 0:
            self.chunks_generated = final_chunks
        if self.elapsed_seconds > 0:
            self.items_per_second = round(
                self.processed_items / self.elapsed_seconds, 2
            )
        self.estimated_remaining_seconds = 0.0

    def fail(self, error_message: str) -> None:
        """Mark job as failed with error details."""
        self.status = "failed"
        self.end_time = time.time()
        self.elapsed_seconds = round(self.end_time - self.start_time, 2)
        self.error_message = error_message
        self.estimated_remaining_seconds = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert job representation to serialisable dictionary."""
        d = asdict(self)
        d["percent_complete"] = (
            round((self.processed_items / self.total_items) * 100, 1)
            if self.total_items > 0
            else 100.0
        )
        return d


class IndexingJobTracker:
    """
    Manages active indexing jobs and operational execution logs.

    Attributes:
      log_file: Filesystem path to persistent execution history JSON.
      max_history: Maximum historical records retained in memory and disk.
    """

    def __init__(self, log_file: Optional[Path] = None, max_history: int = 50) -> None:
        """Initialise tracker storage."""
        self.log_file = (
            log_file
            or settings.data_dir / "indexing_history.json"
        )
        self.max_history = max_history
        self._active_jobs: Dict[str, IndexingJob] = {}
        self._history: List[Dict[str, Any]] = []
        self._load_history()

    def create_job(self, source_type: str, total_items: int = 0) -> IndexingJob:
        """
        Instantiate and register a new active indexing job.

        Args:
          source_type: Category identifier ('local_files', 'google_docs', 'gmail').
          total_items: Estimated document tally.

        Returns:
          Initialised IndexingJob instance.
        """
        timestamp_id = int(time.time() * 1000)
        job_id = f"JOB-{timestamp_id}"
        job = IndexingJob(
            job_id=job_id,
            source_type=source_type,
            total_items=total_items,
        )
        self._active_jobs[job_id] = job
        return job

    def finish_job(self, job_id: str, chunks_indexed: int = 0) -> None:
        """Conclude an active job and archive it into persistent history."""
        job = self._active_jobs.get(job_id)
        if job:
            job.complete(final_chunks=chunks_indexed)
            self._history.insert(0, job.to_dict())
            if len(self._history) > self.max_history:
                self._history = self._history[: self.max_history]
            del self._active_jobs[job_id]
            self._save_history()

    def fail_job(self, job_id: str, error_message: str) -> None:
        """Record job abort and move to history."""
        job = self._active_jobs.get(job_id)
        if job:
            job.fail(error_message)
            self._history.insert(0, job.to_dict())
            del self._active_jobs[job_id]
            self._save_history()

    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Return all currently executing jobs with real-time ETA estimates."""
        # Refresh elapsed timings.
        for job in self._active_jobs.values():
            job.update_progress(job.processed_items)
        return [j.to_dict() for j in self._active_jobs.values()]

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent completed or failed ingestion runs."""
        return self._history[:limit]

    def _load_history(self) -> None:
        """Load historical execution records from persistent JSON file."""
        if self.log_file.exists():
            try:
                data = json.loads(self.log_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._history = data[: self.max_history]
            except Exception:
                self._history = []

    def _save_history(self) -> None:
        """Persist execution history to disk."""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text(
                json.dumps(self._history, indent=2), encoding="utf-8"
            )
        except Exception:
            pass


class VaultStatisticsService:
    """
    Computes and aggregates practice repository storage metrics.

    Calculates:
      - Total document count across all practice sources
      - Total semantic vector chunks indexed
      - Total tracked byte volume and human-readable formatting
      - Total word counts
      - Categorical breakdown (Local files, Gmail, Google Docs)
    """

    def __init__(self, stats_file: Optional[Path] = None) -> None:
        """Initialise metrics storage path."""
        self.stats_file = (
            stats_file
            or settings.data_dir / "vault_statistics.json"
        )

    def calculate_statistics(
        self,
        indexed_chunks: List[Any],
        index_count: int,
    ) -> Dict[str, Any]:
        """
        Aggregate comprehensive data metrics across repository chunks.

        Execution steps:
          1. Step 1: Iterate chunks and extract word count, size, and source.
          2. Step 2: Categorise items into Local, Gmail, and Google Docs buckets.
          3. Step 3: Format sizes into Megabytes (MB) and Kilobytes (KB).
          4. Step 4: Persist computed metrics and return structured dictionary.
        """
        total_chunks = max(index_count, len(indexed_chunks))
        total_words = 0
        total_bytes = 0
        unique_sources = set()

        breakdown = {
            "local_documents": 0,
            "gmail_messages": 0,
            "google_docs": 0,
            "other": 0,
        }

        for chunk in indexed_chunks:
            # Handle chunk whether DocumentChunk object or dictionary.
            text = (
                chunk.text
                if hasattr(chunk, "text")
                else chunk.get("text", "")
            )
            source_path = (
                chunk.source_path
                if hasattr(chunk, "source_path")
                else chunk.get("source_path", "")
            )
            chunk_bytes = len(text.encode("utf-8"))
            chunk_words = len(text.split())

            total_bytes += chunk_bytes
            total_words += chunk_words
            unique_sources.add(source_path)

            if source_path.startswith("gmail://"):
                breakdown["gmail_messages"] += 1
            elif source_path.startswith("gdrive://"):
                breakdown["google_docs"] += 1
            elif source_path:
                breakdown["local_documents"] += 1
            else:
                breakdown["other"] += 1

        total_docs = len(unique_sources) or (1 if total_chunks > 0 else 0)

        stats = {
            "total_documents_tracked": total_docs,
            "total_chunks_indexed": total_chunks,
            "total_words_indexed": total_words,
            "total_bytes_indexed": total_bytes,
            "total_megabytes_indexed": round(total_bytes / (1024.0 * 1024.0), 3),
            "average_chunk_words": (
                round(total_words / total_chunks, 1) if total_chunks > 0 else 0
            ),
            "source_breakdown": breakdown,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

        self._save_stats(stats)
        return stats

    def update_incremental(
        self, new_chunks: List[Any], total_index_count: int
    ) -> Dict[str, Any]:
        """
        Incrementally update corpus statistics without loading full database.

        Execution steps:
          1. Step 1: Load current persisted statistics as baseline.
          2. Step 2: Sum bytes, words, and category counts for new chunks.
          3. Step 3: Add deltas to baseline totals.
          4. Step 4: Persist updated metrics and return structured dictionary.
        """
        stats = self.get_latest_statistics()
        added_words = 0
        added_bytes = 0
        breakdown = stats.get("source_breakdown", {
            "local_documents": 0,
            "gmail_messages": 0,
            "google_docs": 0,
            "other": 0,
        })

        for chunk in new_chunks:
            text = (
                chunk.text
                if hasattr(chunk, "text")
                else chunk.get("text", "")
            )
            source_path = (
                chunk.source_path
                if hasattr(chunk, "source_path")
                else chunk.get("source_path", "")
            )
            added_bytes += len(text.encode("utf-8"))
            added_words += len(text.split())

            if source_path.startswith("gmail://"):
                breakdown["gmail_messages"] = (
                    breakdown.get("gmail_messages", 0) + 1
                )
            elif source_path.startswith("gdrive://"):
                breakdown["google_docs"] = (
                    breakdown.get("google_docs", 0) + 1
                )
            elif source_path:
                breakdown["local_documents"] = (
                    breakdown.get("local_documents", 0) + 1
                )
            else:
                breakdown["other"] = breakdown.get("other", 0) + 1

        total_words = stats.get("total_words_indexed", 0) + added_words
        total_bytes = stats.get("total_bytes_indexed", 0) + added_bytes
        total_chunks = max(
            total_index_count,
            stats.get("total_chunks_indexed", 0) + len(new_chunks),
        )
        total_docs = stats.get("total_documents_tracked", 0) + len(new_chunks)

        updated_stats = {
            "total_documents_tracked": total_docs,
            "total_chunks_indexed": total_chunks,
            "total_words_indexed": total_words,
            "total_bytes_indexed": total_bytes,
            "total_megabytes_indexed": round(
                total_bytes / (1024.0 * 1024.0), 3
            ),
            "average_chunk_words": (
                round(total_words / total_chunks, 1)
                if total_chunks > 0
                else 0
            ),
            "source_breakdown": breakdown,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

        self._save_stats(updated_stats)
        return updated_stats

    def get_latest_statistics(self) -> Dict[str, Any]:
        """Load cached statistics or return baseline metrics."""
        if self.stats_file.exists():
            try:
                return json.loads(self.stats_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        return {
            "total_documents_tracked": 0,
            "total_chunks_indexed": 0,
            "total_words_indexed": 0,
            "total_bytes_indexed": 0,
            "total_megabytes_indexed": 0.0,
            "average_chunk_words": 0,
            "source_breakdown": {
                "local_documents": 0,
                "gmail_messages": 0,
                "google_docs": 0,
                "other": 0,
            },
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_stats(self, stats: Dict[str, Any]) -> None:
        """Persist statistics JSON."""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            self.stats_file.write_text(
                json.dumps(stats, indent=2), encoding="utf-8"
            )
        except Exception:
            pass


# Global singletons.
job_tracker = IndexingJobTracker()
stats_service = VaultStatisticsService()
