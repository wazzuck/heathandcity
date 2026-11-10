"""
Unit Tests for Document Ingestion Pipeline.

Verifies multi-format parsing, text chunking, and source metadata attribution.
"""

from pathlib import Path
from app.ingest import DocumentChunk, DocumentIngestionPipeline


def test_chunking_logic():
    """Verify that text is segmented into target word windows with overlap."""
    pipeline = DocumentIngestionPipeline(
        target_chunk_words=10, chunk_overlap_words=2
    )
    sample_text = (
        "Word one two three four five six seven eight nine ten eleven twelve thirteen."
    )
    chunks = pipeline._chunk_text(sample_text)

    assert len(chunks) >= 2
    assert "one two three" in chunks[0]
    # Check that overlap exists in the second chunk.
    assert "nine ten" in chunks[1]


def test_parse_sample_file(tmp_path: Path):
    """Verify ingestion and metadata capture from a text file."""
    test_file = tmp_path / "test_opinion.txt"
    test_file.write_text(
        "Chambers Opinion: Statutory filing date is 31 January 2025. Fee is £5,000.",
        encoding="utf-8",
    )

    pipeline = DocumentIngestionPipeline(
        target_chunk_words=50, chunk_overlap_words=5
    )
    chunks = pipeline.parse_file(test_file)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.file_name == "test_opinion.txt"
    assert chunk.page_number == 1
    assert "31 January 2025" in chunk.text
    assert chunk.word_count > 5
