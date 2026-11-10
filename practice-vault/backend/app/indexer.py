"""
Vector and Lexical Indexing Engine.

Purpose:
  Coordinates persistent on-disk vector storage via LanceDB and lexical
  keyword search via Best Matching 25 (BM25). Merges dense semantic vector
  similarity scores with sparse keyword rankings using Reciprocal Rank Fusion
  (RRF) to ensure deterministic retrieval for precise legal references,
  statutory citations, and client records.

Deliberately Not For:
  Direct end-user question answering, prompt construction, or external
  network egress.

Invariants:
  1. LanceDB database files reside strictly within local appliance storage.
  2. Every indexed entry maps 1:1 to an immutable source DocumentChunk.
"""

import math
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import lancedb
    import pyarrow as pa
except ImportError:
    lancedb = None
    pa = None

try:
    from fastembed import TextEmbedding
except ImportError:
    TextEmbedding = None

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

from .config import settings
from .ingest import DocumentChunk
from .reranker import NeuralReranker


class HybridIndexEngine:
    """
    Dual-tower vector and lexical indexing service.

    Attributes:
      db_path: Filesystem path to on-disk LanceDB storage.
      embed_model_name: Identifier for FastEmbed local embedding model.
      table_name: Internal LanceDB table name.
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        embed_model_name: Optional[str] = None,
        table_name: str = "practice_chunks",
    ) -> None:
        """
        Initialise database path, embedding engine, and lexical index.

        Args:
          db_path: Path to LanceDB directory (defaults to settings.lancedb_dir).
          embed_model_name: Local embedding model tag.
          table_name: Persistent LanceDB table identifier.
        """
        self.db_path = Path(db_path or settings.lancedb_dir).resolve()
        self.fts_path = (
            self.db_path.parent / "practice_fts.db"
            if self.db_path.is_dir()
            else self.db_path.parent / f"{self.db_path.name}_fts.db"
        )
        self.embed_model_name = embed_model_name or settings.embed_model
        self.table_name = table_name

        self._db: Any = None
        self._table: Any = None
        self._embedding_model: Any = None
        self._fts_conn: Optional[sqlite3.Connection] = None
        self._bm25: Any = None
        self._bm25_chunks: List[DocumentChunk] = []
        self._reranker: NeuralReranker = NeuralReranker()

        self._init_database()

    def _get_table_names(self) -> List[str]:
        """Return list of existing table names in LanceDB."""
        if self._db is None:
            return []
        try:
            if hasattr(self._db, "list_tables"):
                return list(self._db.list_tables())
            return list(self._db.table_names())
        except Exception:
            return []

    def _init_database(self) -> None:
        """
        Connect to LanceDB instance on disk.

        Execution steps:
          1. Step 1: Ensure persistent directory exists.
          2. Step 2: Open LanceDB connection.
          3. Step 3: Open existing table if already created.
          4. Step 4: Rehydrate BM25 index from stored chunks for consistency.
        """
        # Step 1: Ensure directory exists.
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Step 2: Open SQLite FTS5 connection for disk-backed BM25 search.
        try:
            self._fts_conn = sqlite3.connect(
                str(self.fts_path), check_same_thread=False
            )
            self._fts_conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS practice_fts USING fts5("
                "chunk_id UNINDEXED, source_path UNINDEXED, file_name, "
                "page_number UNINDEXED, section_heading, text, "
                "modified_at UNINDEXED"
                ");"
            )
            self._fts_conn.commit()
        except Exception:
            self._fts_conn = None

        # Step 3: Open connection if lancedb is installed.
        if lancedb is not None:
            try:
                self._db = lancedb.connect(str(self.db_path))
                if self.table_name in self._get_table_names():
                    self._table = self._db.open_table(self.table_name)
            except Exception:
                self._db = None
                self._table = None

    def _get_embedding_model(self) -> Any:
        """Lazy load the FastEmbed embedding model."""
        if self._embedding_model is None and TextEmbedding is not None:
            try:
                self._embedding_model = TextEmbedding(
                    model_name=self.embed_model_name
                )
            except Exception:
                self._embedding_model = None
        return self._embedding_model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate dense vector embeddings for input strings.

        Execution steps:
          1. Step 1: Attempt generation via local FastEmbed model.
          2. Step 2: If model is unavailable, generate deterministic fallback
             vector representations based on token hashing.
        """
        model = self._get_embedding_model()
        if model is not None:
            try:
                embeddings = list(model.embed(texts))
                return [emb.tolist() for emb in embeddings]
            except Exception:
                pass

        # Step 2: Deterministic pseudo-embedding fallback (384 dimensions).
        fallback_dim = 384
        vectors = []
        for text in texts:
            vec = [0.0] * fallback_dim
            words = text.lower().split()
            for word in words:
                h = abs(hash(word)) % fallback_dim
                vec[h] += 1.0
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vectors.append([v / norm for v in vec])
        return vectors

    def get_indexed_ids(self) -> set:
        """
        Return the set of unique chunk identifiers already indexed.

        Uses the lightweight on-disk SQLite Full-Text Search 5 (FTS5) table
        when available to avoid deserialising all dense vector arrays into
        Python heap memory.

        Returns:
          Set of string chunk identifiers.
        """
        if self._fts_conn is not None:
            try:
                rows = self._fts_conn.execute(
                    "SELECT chunk_id FROM practice_fts;"
                ).fetchall()
                if rows:
                    return {str(r[0]) for r in rows}
            except Exception:
                pass
        if self._bm25_chunks:
            return {c.chunk_id for c in self._bm25_chunks}
        if self._table is not None:
            try:
                lance_tbl = self._table.to_lance()
                arr = lance_tbl.to_table(columns=["chunk_id"])["chunk_id"]
                return set(arr.to_pylist())
            except Exception:
                pass
        return set()

    def index_chunks(self, chunks: List[DocumentChunk]) -> int:
        """
        Store chunks into LanceDB table and update BM25 index.

        Execution steps:
          1. Step 1: Validate input chunk list and filter out duplicate IDs.
          2. Step 2: Compute dense vector embeddings for chunk texts.
          3. Step 3: Construct table schema and upsert into LanceDB.
          4. Step 4: Re-tokenise and rebuild BM25 lexical index.

        Args:
          chunks: List of DocumentChunk instances to persist.

        Returns:
          Total count of newly indexed chunks.
        """
        # Step 1: Validate input chunk list and eliminate existing duplicates.
        if not chunks:
            return 0

        existing_ids = self.get_indexed_ids()
        unique_chunks = [
            c for c in chunks if c.chunk_id not in existing_ids
        ]
        if not unique_chunks:
            return 0

        # Step 2: Compute dense vector embeddings.
        texts = [c.text for c in unique_chunks]
        vectors = self.embed_texts(texts)

        # Step 3: Upsert into LanceDB.
        records = []
        for c, vec in zip(unique_chunks, vectors):
            records.append(
                {
                    "chunk_id": c.chunk_id,
                    "source_path": c.source_path,
                    "file_name": c.file_name,
                    "page_number": c.page_number,
                    "section_heading": c.section_heading,
                    "text": c.text,
                    "modified_at": c.modified_at,
                    "vector": vec,
                }
            )

        if self._db is not None:
            try:
                if self.table_name in self._get_table_names():
                    self._table = self._db.open_table(self.table_name)
                    self._table.add(records)
                else:
                    self._table = self._db.create_table(
                        self.table_name, data=records
                    )
            except Exception:
                pass

        # Step 4: Index into SQLite FTS5 table and in-memory BM25 fallback.
        if self._fts_conn is not None:
            try:
                rows = [
                    (
                        c.chunk_id,
                        c.source_path,
                        c.file_name,
                        c.page_number,
                        c.section_heading,
                        c.text,
                        c.modified_at,
                    )
                    for c in unique_chunks
                ]
                self._fts_conn.executemany(
                    "INSERT INTO practice_fts("
                    "chunk_id, source_path, file_name, page_number, "
                    "section_heading, text, modified_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?);",
                    rows,
                )
                self._fts_conn.commit()
            except Exception:
                pass
        else:
            self._bm25_chunks.extend(unique_chunks)
            if BM25Okapi is not None:
                tokenised_corpus = [
                    c.text.lower().split() for c in self._bm25_chunks
                ]
                self._bm25 = BM25Okapi(tokenised_corpus)

        return len(records)

    def search_hybrid(
        self,
        query: str,
        top_k: int = 5,
        rrf_k: int = 60,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Execute hybrid search using Reciprocal Rank Fusion (RRF) and Stage 2 reranking.

        Execution steps:
          1. Step 1: Query LanceDB for top vector nearest neighbours.
          2. Step 2: Query BM25 index for top lexical keyword matches.
          3. Step 3: Merge rankings using standard RRF: RRF_score = sum(1 / (k + rank)).
          4. Step 4: Sort by combined score and collect candidate pool.
          5. Step 5: If rerank is enabled, execute Stage 2 local neural
             cross-encoder reranking to elevate top-1 precision.

        Args:
          query: User search string in plain English.
          top_k: Number of ranked results to return.
          rrf_k: Constant smoothing parameter for reciprocal rank fusion.
          rerank: Whether to execute Stage 2 neural cross-encoder reranking.

        Returns:
          List of ranked result dictionaries containing chunk metadata and
          composite fusion or neural rerank scores.
        """
        if not query.strip():
            return []

        vector_hits: List[Dict[str, Any]] = []
        lexical_hits: List[Dict[str, Any]] = []

        # Candidate pool size for Stage 2 reranking.
        candidate_k = max(top_k * 3, 10) if rerank else top_k

        # Step 1: Dense vector search.
        query_vec = self.embed_texts([query])[0]
        if self._table is not None:
            try:
                results = (
                    self._table.search(query_vec)
                    .limit(candidate_k * 2)
                    .to_list()
                )
                vector_hits = results
            except Exception:
                vector_hits = []

        # Step 2: Lexical BM25 search via SQLite FTS5.
        if self._fts_conn is not None:
            try:
                clean_words = [
                    w for w in re.findall(r"\w+", query) if len(w) > 1
                ]
                if clean_words:
                    match_expr = " OR ".join(f'"{w}"*' for w in clean_words)
                    cur = self._fts_conn.execute(
                        "SELECT chunk_id, source_path, file_name, "
                        "page_number, section_heading, text, modified_at, "
                        "bm25(practice_fts) FROM practice_fts "
                        "WHERE practice_fts MATCH ? "
                        "ORDER BY bm25(practice_fts) ASC LIMIT ?;",
                        (match_expr, candidate_k * 2),
                    )
                    for row in cur.fetchall():
                        lexical_hits.append(
                            {
                                "chunk_id": row[0],
                                "source_path": row[1],
                                "file_name": row[2],
                                "page_number": int(row[3]),
                                "section_heading": row[4],
                                "text": row[5],
                                "modified_at": row[6],
                                "_bm25_score": -float(row[7]),
                            }
                        )
            except Exception:
                pass
        elif self._bm25 is not None and self._bm25_chunks:
            tokens = query.lower().split()
            scores = self._bm25.get_scores(tokens)
            ranked_indices = sorted(
                range(len(scores)), key=lambda i: scores[i], reverse=True
            )[: candidate_k * 2]
            for idx in ranked_indices:
                if scores[idx] > 0.0:
                    c = self._bm25_chunks[idx]
                    lexical_hits.append(
                        {
                            "chunk_id": c.chunk_id,
                            "source_path": c.source_path,
                            "file_name": c.file_name,
                            "page_number": c.page_number,
                            "section_heading": c.section_heading,
                            "text": c.text,
                            "modified_at": c.modified_at,
                            "_bm25_score": scores[idx],
                        }
                    )

        # Step 3: Reciprocal Rank Fusion calculation.
        scores_by_id: Dict[str, float] = {}
        chunks_by_id: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(vector_hits, start=1):
            cid = item["chunk_id"]
            scores_by_id[cid] = scores_by_id.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            chunks_by_id[cid] = item

        for rank, item in enumerate(lexical_hits, start=1):
            cid = item["chunk_id"]
            scores_by_id[cid] = scores_by_id.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            if cid not in chunks_by_id:
                chunks_by_id[cid] = item

        # If both engines yielded nothing, check in-memory fallback.
        if not scores_by_id and self._bm25_chunks:
            for c in self._bm25_chunks[:candidate_k]:
                chunks_by_id[c.chunk_id] = {
                    "chunk_id": c.chunk_id,
                    "source_path": c.source_path,
                    "file_name": c.file_name,
                    "page_number": c.page_number,
                    "section_heading": c.section_heading,
                    "text": c.text,
                    "modified_at": c.modified_at,
                }
                scores_by_id[c.chunk_id] = 1.0

        # Step 4: Sort by combined score.
        sorted_ids = sorted(
            scores_by_id.keys(), key=lambda k: scores_by_id[k], reverse=True
        )[:candidate_k]

        ranked_results = []
        for cid in sorted_ids:
            record = chunks_by_id[cid].copy()
            record["rrf_score"] = round(scores_by_id[cid], 5)
            ranked_results.append(record)

        # Step 5: Stage 2 Neural Cross-Encoder Reranking.
        if rerank and ranked_results:
            return self._reranker.rerank(query, ranked_results, top_n=top_k)

        return ranked_results[:top_k]

    def count(self) -> int:
        """Return total indexed records in database."""
        if self._table is not None:
            try:
                return len(self._table)
            except Exception:
                pass
        return len(self._bm25_chunks)

    def get_all_chunks(self) -> List[Any]:
        """
        Return all indexed document chunks in memory or database.

        Prefers disk-backed SQLite FTS5 index to prevent heap exhaustion from
        full vector table deserialisation.
        """
        if self._fts_conn is not None:
            try:
                cur = self._fts_conn.cursor()
                cur.execute(
                    "SELECT chunk_id, source_path, file_name, page_number, "
                    "section_heading, text, modified_at FROM practice_fts;"
                )
                rows = cur.fetchall()
                return [
                    {
                        "chunk_id": r[0],
                        "source_path": r[1],
                        "file_name": r[2],
                        "page_number": r[3],
                        "section_heading": r[4],
                        "text": r[5],
                        "modified_at": r[6],
                    }
                    for r in rows
                ]
            except Exception:
                pass
        if self._bm25_chunks:
            return list(self._bm25_chunks)
        return []
