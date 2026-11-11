"""
Unit Tests for Retrieval-Augmented Generation (RAG) and Deterministic Q&A.

Verifies citation attribution and zero-hallucination safeguards.
"""

from pathlib import Path
from app.indexer import HybridIndexEngine
from app.ingest import DocumentChunk
from app.rag import RAGEngine


def test_rag_deterministic_attribution(tmp_path: Path):
    """Verify that RAG responses cite the source document name and page."""
    engine = HybridIndexEngine(db_path=tmp_path / "lancedb_rag_test")

    chunk = DocumentChunk(
        chunk_id="chambers_memo.txt#p1#c0",
        source_path="/tmp/chambers_memo.txt",
        file_name="chambers_memo.txt",
        page_number=1,
        section_heading="Limitation Periods",
        text=(
            "The statutory deadline for HMRC filing under Section 98A is "
            "31 January 2025."
        ),
        modified_at="2026-11-10T00:00:00Z",
    )
    engine.index_chunks([chunk])

    rag = RAGEngine(indexer=engine)
    response = rag.query("What is the statutory deadline for HMRC filing?")

    assert response.query == "What is the statutory deadline for HMRC filing?"
    assert len(response.citations) > 0
    assert response.citations[0].file_name == "chambers_memo.txt"
    assert response.citations[0].page_number == 1
    assert (
        "chambers_memo.txt" in response.answer
        or "31 January 2025" in response.answer
    )


def test_rag_zero_hallucination_refusal(tmp_path: Path):
    """Verify queries against empty archive return explicit refusal."""
    empty_engine = HybridIndexEngine(db_path=tmp_path / "lancedb_empty")
    rag = RAGEngine(indexer=empty_engine)

    response = rag.query("What is the nuclear launch code?")
    assert "no record of this information" in response.answer.lower()
    assert len(response.citations) == 0


def test_rag_query_decomposition(tmp_path: Path):
    """Verify decomposition of compound and nuanced inquiries."""
    engine = HybridIndexEngine(db_path=tmp_path / "lancedb_decomp_test")
    rag = RAGEngine(indexer=engine)

    compound_q = (
        "What is our hourly fee with counsel and what happens if a trial "
        "is adjourned?"
    )
    aspects = rag._decompose_query(compound_q)
    assert len(aspects) == 2
    assert "hourly fee with counsel" in aspects[0].lower()
    assert "trial is adjourned" in aspects[1].lower()

    atomic_q = "What is the filing deadline?"
    assert len(rag._decompose_query(atomic_q)) == 1
