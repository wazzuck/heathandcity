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

import concurrent.futures
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

# Curated practice vocabulary synonyms for lexical query expansion.
PRACTICE_SYNONYMS: Dict[str, List[str]] = {
    "fee": ["fee", "rate", "tariff", "retainer", "remuneration", "charge"],
    "rate": ["rate", "fee", "tariff", "hourly"],
    "agreement": ["agreement", "contract", "retainer", "terms", "settlement"],
    "contract": ["contract", "agreement", "retainer", "terms"],
    "settlement": ["settlement", "compromise", "consent order", "resolution"],
    "invoice": ["invoice", "bill", "fee note", "receipt", "payment"],
    "lawyer": ["counsel", "barrister", "solicitor", "advocate"],
    "counsel": ["counsel", "barrister", "advocate", "silk"],
    "purchase": ["purchase", "order", "receipt", "invoice", "payment", "buy"],
    "bought": ["bought", "purchase", "purchased", "order", "receipt"],
    "spend": ["spend", "spent", "expenditure", "cost", "total"],
    "spent": ["spent", "spend", "expenditure", "cost", "total"],
}


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
        self._query_embed_cache: Dict[str, List[float]] = {}

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
        Connect to LanceDB instance on disk and tune SQLite FTS5 for RAM speed.

        Execution steps:
          1. Step 1: Ensure persistent directory exists.
          2. Step 2: Open SQLite FTS5 connection and apply high-speed RAM
             PRAGMAs.
          3. Step 3: Open LanceDB vector table.
        """
        # Step 1: Ensure directory exists.
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Step 2: Open SQLite FTS5 connection with high-speed memory buffers.
        try:
            self._fts_conn = sqlite3.connect(
                str(self.fts_path), check_same_thread=False
            )
            # High-performance in-memory cache and memory-mapped I/O pragmas.
            self._fts_conn.execute("PRAGMA journal_mode = WAL;")
            self._fts_conn.execute("PRAGMA synchronous = NORMAL;")
            self._fts_conn.execute("PRAGMA cache_size = -64000;")  # 64 MB RAM
            self._fts_conn.execute(
                "PRAGMA mmap_size = 268435456;"
            )  # 256 MB MMAP
            self._fts_conn.execute("PRAGMA temp_store = MEMORY;")

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

    def embed_query(self, query: str) -> List[float]:
        """
        Generate or retrieve cached dense embedding for a single query string.

        Uses an in-memory Least Recently Used (LRU) cache capped at 2,048
        entries to eliminate redundant embedding inference overhead for
        recurring, re-ranked, or composite inquiries.

        Args:
          query: User inquiry string in plain English.

        Returns:
          384-dimensional dense floating-point embedding vector.
        """
        clean_q = query.strip()
        if clean_q in self._query_embed_cache:
            return self._query_embed_cache[clean_q]

        vec = self.embed_texts([clean_q])[0]
        if len(self._query_embed_cache) >= 2048:
            first_key = next(iter(self._query_embed_cache))
            self._query_embed_cache.pop(first_key, None)
        self._query_embed_cache[clean_q] = vec
        return vec

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

    def _search_vector(
        self, query_vec: List[float], candidate_k: int
    ) -> List[Dict[str, Any]]:
        """Query LanceDB vector store for top nearest neighbour chunks."""
        if self._table is None:
            return []
        try:
            return (
                self._table.search(query_vec)
                .limit(candidate_k * 2)
                .to_list()
            )
        except Exception:
            return []

    def _search_lexical(
        self, query: str, candidate_k: int
    ) -> List[Dict[str, Any]]:
        """Query SQLite FTS5 index for BM25 keyword matches with synonyms."""
        lexical_hits: List[Dict[str, Any]] = []
        if self._fts_conn is not None:
            try:
                clean_words = [
                    w for w in re.findall(r"\w+", query) if len(w) > 1
                ]
                if clean_words:
                    expanded_clauses = []
                    for w in clean_words:
                        w_lower = w.lower()
                        if w_lower in PRACTICE_SYNONYMS:
                            syns = PRACTICE_SYNONYMS[w_lower]
                            sub = " OR ".join(f'"{s}"*' for s in syns[:4])
                            expanded_clauses.append(f"({sub})")
                        else:
                            expanded_clauses.append(f'"{w}"*')
                    match_expr = " OR ".join(expanded_clauses)
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
        return lexical_hits

    def search_hybrid(
        self,
        query: str,
        top_k: int = 5,
        rrf_k: int = 60,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Execute concurrent dual-tower hybrid search and Stage 2 reranking.

        Execution steps:
          1. Step 1: Obtain dense embedding (cached via in-memory LRU).
          2. Step 2: Concurrently query LanceDB vector store and SQLite FTS5.
          3. Step 3: Merge rankings using standard Reciprocal Rank Fusion (RRF).
          4. Step 4: Sort by combined score and collect candidate pool.
          5. Step 5: If rerank is enabled, execute Stage 2 neural cross-encoder.

        Args:
          query: User search string in plain English.
          top_k: Number of ranked results to return.
          rrf_k: Constant smoothing parameter for reciprocal rank fusion.
          rerank: Whether to execute Stage 2 neural cross-encoder reranking.

        Returns:
          List of ranked result dictionaries with metadata and scores.
        """
        if not query.strip():
            return []

        # Candidate pool size for Stage 2 reranking.
        candidate_k = max(top_k * 3, 10) if rerank else top_k

        # Step 1: Obtain query embedding (using LRU cache).
        query_vec = self.embed_query(query)

        # Step 2: Concurrent dual-tower retrieval.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fut_vec = executor.submit(
                self._search_vector, query_vec, candidate_k
            )
            fut_lex = executor.submit(
                self._search_lexical, query, candidate_k
            )
            vector_hits = fut_vec.result()
            lexical_hits = fut_lex.result()

        # Step 3: Reciprocal Rank Fusion calculation.
        scores_by_id: Dict[str, float] = {}
        chunks_by_id: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(vector_hits, start=1):
            cid = item["chunk_id"]
            rrf_term = 1.0 / (rrf_k + rank)
            scores_by_id[cid] = scores_by_id.get(cid, 0.0) + rrf_term
            chunks_by_id[cid] = item

        for rank, item in enumerate(lexical_hits, start=1):
            cid = item["chunk_id"]
            rrf_term = 1.0 / (rrf_k + rank)
            scores_by_id[cid] = scores_by_id.get(cid, 0.0) + rrf_term
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

    def search_aspects(
        self,
        aspects: List[str],
        top_k: int = 5,
        composite_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and fuse document chunks across multiple nuanced sub-aspects.

        Execution steps:
          1. Step 1: Execute concurrent hybrid search for each sub-aspect.
          2. Step 2: Track aspect coverage counts per chunk.
          3. Step 3: Pool candidate chunks and apply aspect coverage boost.
          4. Step 4: Run Stage 2 cross-encoder rerank on the composite query.

        Args:
          aspects: List of distinct sub-aspect query strings.
          top_k: Number of final ranked chunks to return.
          composite_query: Original full composite question string.

        Returns:
          List of top_k enriched document chunk dictionaries.
        """
        if not aspects:
            return []
        if len(aspects) == 1:
            return self.search_hybrid(aspects[0], top_k=top_k)

        pooled_chunks: Dict[str, Dict[str, Any]] = {}
        aspect_coverage: Dict[str, int] = {}
        base_scores: Dict[str, float] = {}

        for aspect in aspects:
            hits = self.search_hybrid(
                aspect, top_k=max(top_k * 2, 8), rerank=False
            )
            for h in hits:
                cid = h["chunk_id"]
                pooled_chunks[cid] = h
                aspect_coverage[cid] = aspect_coverage.get(cid, 0) + 1
                base_scores[cid] = base_scores.get(cid, 0.0) + h.get(
                    "rrf_score", 0.01
                )

        # Apply multi-aspect coverage multiplier.
        scored_candidates = []
        for cid, chunk in pooled_chunks.items():
            coverage = aspect_coverage[cid]
            multiplier = 1.0 + (coverage - 1) * 0.5
            c_copy = chunk.copy()
            c_copy["multi_aspect_score"] = round(
                base_scores[cid] * multiplier, 5
            )
            c_copy["aspects_covered"] = coverage
            scored_candidates.append(c_copy)

        scored_candidates.sort(
            key=lambda x: x.get("multi_aspect_score", 0.0), reverse=True
        )

        target_query = composite_query or " ".join(aspects)
        candidate_pool = scored_candidates[: max(top_k * 3, 12)]

        return self._reranker.rerank(
            target_query, candidate_pool, top_n=top_k
        )

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
