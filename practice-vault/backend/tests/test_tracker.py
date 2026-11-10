"""
Unit Tests for Indexing Job Tracker and Repository Statistics Service.

Verifies progress tracking, throughput estimation, time-remaining projections,
and volume metric aggregation.
"""

import time
from pathlib import Path
from app.ingest import DocumentChunk
from app.tracker import IndexingJob, IndexingJobTracker, VaultStatisticsService


def test_indexing_job_eta_and_progress():
    """Verify that job updates calculate velocity and remaining seconds."""
    job = IndexingJob(job_id="TEST-001", source_type="local_files", total_items=100)
    assert job.status == "running"

    # Simulate processing after a short delay.
    job.start_time = time.time() - 10.0  # 10 seconds elapsed
    job.update_progress(processed_items=20, total_items=100)

    assert job.processed_items == 20
    assert job.items_per_second > 0
    # 80 items remaining at ~2 items/sec -> ~40 seconds remaining
    assert job.estimated_remaining_seconds > 0
    assert job.to_dict()["percent_complete"] == 20.0

    job.complete(final_chunks=40)
    assert job.status == "completed"
    assert job.estimated_remaining_seconds == 0.0


def test_job_tracker_lifecycle(tmp_path: Path):
    """Verify job tracker archival into history JSON file."""
    log_file = tmp_path / "test_history.json"
    tracker = IndexingJobTracker(log_file=log_file, max_history=5)

    job = tracker.create_job("google_docs", total_items=10)
    assert len(tracker.get_active_jobs()) == 1

    tracker.finish_job(job.job_id, chunks_indexed=25)
    assert len(tracker.get_active_jobs()) == 0

    history = tracker.get_history()
    assert len(history) == 1
    assert history[0]["job_id"] == job.job_id
    assert history[0]["chunks_generated"] == 25
    assert log_file.exists()


def test_vault_statistics_calculation(tmp_path: Path):
    """Verify volume and word count metrics across document sources."""
    stats_file = tmp_path / "test_stats.json"
    service = VaultStatisticsService(stats_file=stats_file)

    chunks = [
        DocumentChunk(
            chunk_id="c1",
            source_path="/path/to/contract.pdf",
            file_name="contract.pdf",
            page_number=1,
            section_heading="Recitals",
            text="This agreement is executed between Chambers and the Client for legal advisory services.",
            modified_at="2026-11-10T00:00:00Z",
        ),
        DocumentChunk(
            chunk_id="c2",
            source_path="gdrive://file123",
            file_name="Google Doc: Advisory Notes",
            page_number=1,
            section_heading="Notes",
            text="Taxation advice regarding statutory limitation dates.",
            modified_at="2026-11-10T00:00:00Z",
        ),
        DocumentChunk(
            chunk_id="c3",
            source_path="gmail://msg999",
            file_name="Gmail: Hearing Reminder",
            page_number=1,
            section_heading="Email",
            text="Hearing confirmed for tomorrow morning in court room three.",
            modified_at="2026-11-10T00:00:00Z",
        ),
    ]

    stats = service.calculate_statistics(chunks, index_count=3)
    assert stats["total_chunks_indexed"] == 3
    assert stats["total_words_indexed"] > 20
    assert stats["total_bytes_indexed"] > 100
    assert stats["source_breakdown"]["local_documents"] == 1
    assert stats["source_breakdown"]["google_docs"] == 1
    assert stats["source_breakdown"]["gmail_messages"] == 1
    assert stats_file.exists()
