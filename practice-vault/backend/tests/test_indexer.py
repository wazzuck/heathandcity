"""
Unit Tests for Hybrid Indexing Engine.

Verifies LanceDB persistent storage, BM25 keyword matching, and RRF ranking.
"""

from pathlib import Path
from app.indexer import HybridIndexEngine
from app.ingest import DocumentChunk


def test_indexing_and_hybrid_search(tmp_path: Path):
    """Verify that chunks are indexed and retrieved accurately by keywords."""
    engine = HybridIndexEngine(db_path=tmp_path / "lancedb_test")

    chunk1 = DocumentChunk(
        chunk_id="doc1#p1#c0",
        source_path="/tmp/doc1.txt",
        file_name="doc1.txt",
        page_number=1,
        section_heading="Trusts",
        text="The statutory deadline for HMRC filing is 31 January 2025.",
        modified_at="2026-11-10T00:00:00Z",
    )
    chunk2 = DocumentChunk(
        chunk_id="doc2#p1#c0",
        source_path="/tmp/doc2.txt",
        file_name="doc2.txt",
        page_number=1,
        section_heading="Clinical",
        text="Patient received a titrated dosage of Pregabalin 75 mg twice daily.",
        modified_at="2026-11-10T00:00:00Z",
    )

    indexed_count = engine.index_chunks([chunk1, chunk2])
    assert indexed_count == 2
    assert engine.count() >= 2

    # Query for trust deadline.
    results = engine.search_hybrid("statutory HMRC deadline", top_k=2)
    assert len(results) > 0
    top_hit = results[0]
    assert "doc1.txt" == top_hit["file_name"]
    assert "31 January 2025" in top_hit["text"]
    assert "rrf_score" in top_hit

    # Query for clinical dosage.
    clinical_results = engine.search_hybrid("Pregabalin dosage", top_k=2)
    assert len(clinical_results) > 0
    assert "doc2.txt" == clinical_results[0]["file_name"]
