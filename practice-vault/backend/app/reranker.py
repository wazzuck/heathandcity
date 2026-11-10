"""
Local Cross-Encoder Neural Reranking Engine.

Purpose:
  Provides Stage 2 neural cross-encoder reranking over hybrid search candidate
  results retrieved from LanceDB vector store and Best Matching 25 (BM25)
  lexical index. Reranks top document candidates to elevate retrieval accuracy
  and eliminate irrelevant citations before Small Language Model (SLM)
  generation.

Deliberately Not For:
  Direct document parsing, vector indexing, or external network egress.
  Model runs fully on-premises via local Open Neural Network Exchange (ONNX)
  runtime.

Invariants:
  1. Reranking executes entirely on local Central Processing Unit (CPU)
     without cloud communication.
  2. Candidate ordering preserves input structures while injecting calibrated
     cross-encoder neural relevance scores.
"""

from typing import Any, Dict, List, Optional

try:
    from fastembed.rerank.cross_encoder import TextCrossEncoder
except ImportError:
    TextCrossEncoder = None


class NeuralReranker:
    """
    Local cross-encoder neural reranking service.

    Attributes:
      model_name: Identifier of the quantised ONNX cross-encoder model.
    """

    DEFAULT_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"

    def __init__(self, model_name: Optional[str] = None) -> None:
        """
        Initialise neural reranker.

        Args:
          model_name: Hugging Face or ONNX model tag.
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self._encoder: Any = None

    def _get_encoder(self) -> Any:
        """Lazy load the TextCrossEncoder model instance."""
        if self._encoder is None and TextCrossEncoder is not None:
            try:
                self._encoder = TextCrossEncoder(model_name=self.model_name)
            except Exception:
                self._encoder = None
        return self._encoder

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_n: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidate documents against a query with calibrated thresholding.

        Execution steps:
          1. Step 1: Validate query and candidates; return early if empty.
          2. Step 2: Attempt neural scoring via ONNX cross-encoder.
          3. Step 3: If cross-encoder is unavailable, return candidates
             sorted by existing Reciprocal Rank Fusion (RRF) scores.
          4. Step 4: Sort candidates descending by neural relevance score.
          5. Step 5: Filter candidates by min_score threshold if specified,
             retaining at least top result if initial list was non-empty.
          6. Step 6: Truncate to top_n if specified and return.

        Args:
          query: Search query in natural English.
          candidates: List of chunk dictionaries containing 'text'.
          top_n: Maximum candidate count to retain after reranking.
          min_score: Calibrated minimum neural cross-encoder relevance score.

        Returns:
          List of reranked candidate dictionaries with 'rerank_score'.
        """
        if not candidates or not query.strip():
            return candidates

        encoder = self._get_encoder()
        if encoder is None:
            # Fallback: maintain input order if neural encoder unavailable.
            return candidates[:top_n] if top_n else candidates

        doc_texts = [c.get("text", "") for c in candidates]
        try:
            scores = list(encoder.rerank(query, doc_texts))
            scored_candidates = []
            for item, score in zip(candidates, scores):
                c_copy = item.copy()
                c_copy["rerank_score"] = float(score)
                scored_candidates.append(c_copy)

            # Sort descending by neural score.
            scored_candidates.sort(
                key=lambda x: x.get("rerank_score", -999.0),
                reverse=True,
            )

            # Step 5: Filter by calibrated minimum score threshold.
            if min_score is not None:
                filtered = [
                    c for c in scored_candidates
                    if c.get("rerank_score", -999.0) >= min_score
                ]
                # Retain the top result if all fell below threshold.
                scored_candidates = (
                    filtered if filtered else scored_candidates[:1]
                )

            return (
                scored_candidates[:top_n] if top_n else scored_candidates
            )
        except Exception:
            return candidates[:top_n] if top_n else candidates
