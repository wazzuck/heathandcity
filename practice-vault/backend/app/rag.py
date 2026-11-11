"""
Retrieval-Augmented Generation (RAG) and Deterministic Q&A Module.

Purpose:
  Combines retrieved document fragments from the hybrid search index with
  strict prompt engineering for local Small Language Model (SLM) inference.
  Enforces mandatory source document and page citations, with zero
  hallucination tolerance for professional legal and medical liability
  protection.

Deliberately Not For:
  Direct client communication, outbound network calls, or modifying source
  practice archives.

Invariants:
  1. If the provided document excerpts contain no factual answer, the engine
     explicitly returns: "The practice archive contains no record of this
     information."
  2. All network calls are restricted to the local Ollama loopback daemon.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional
import httpx

from .config import settings
from .indexer import HybridIndexEngine
from .transactions import TransactionStore


@dataclass
class Citation:
    """
    Structured attribution link pointing to a source document.

    Attributes:
      file_name: Origin filename (e.g. 'Litigation_Brief.pdf').
      page_number: Source page or worksheet number.
      section_heading: Optional section heading.
      snippet: Extracted supporting text excerpt.
    """

    file_name: str
    page_number: int
    section_heading: str
    snippet: str


@dataclass
class RAGResponse:
    """
    Deterministic answer container with source citations.

    Attributes:
      query: The original question posed.
      answer: Narrative response text.
      citations: List of source Citation objects.
      model_used: Identifier of the local model or engine.
      context_chunks_count: Count of document fragments provided to context.
    """

    query: str
    answer: str
    citations: List[Citation]
    model_used: str
    context_chunks_count: int


class RAGEngine:
    """
    Orchestrates deterministic question answering against practice records.

    Attributes:
      indexer: Hybrid vector and lexical search engine instance.
      ollama_url: Loopback Uniform Resource Locator (URL) for Ollama.
      model_name: Local model identifier (e.g. 'llama3.2:3b-instruct-q4_K_M').
    """

    def __init__(
        self,
        indexer: HybridIndexEngine,
        ollama_url: Optional[str] = None,
        model_name: Optional[str] = None,
        tx_store: Optional[TransactionStore] = None,
    ) -> None:
        """
        Initialise RAG query service.

        Args:
          indexer: Initialised HybridIndexEngine instance.
          ollama_url: Loopback address of the Ollama daemon.
          model_name: Identifier of the quantised local model.
          tx_store: Dedicated deterministic transaction ledger engine.
        """
        self.indexer = indexer
        self.ollama_url = ollama_url or settings.ollama_base_url
        self.model_name = model_name or settings.llm_model
        self.tx_store = tx_store or TransactionStore()

    def _check_aggregation_intent(
        self, user_query: str
    ) -> Optional[RAGResponse]:
        """
        Evaluate whether the query represents a financial aggregation request.

        Implements Path B from the architectural recommendations: routes
        exhaustive queries ("what did I buy last year?", "Amazon purchases")
        to the deterministic SQLite transaction ledger rather than truncating
        across top-k excerpts.

        Args:
          user_query: Search inquiry string.

        Returns:
          RAGResponse populated with ledger tables if matched, else None.
        """
        q_lower = user_query.lower()
        purchase_tokens = [
            "buy", "bought", "purchase", "purchases", "spend", "spent",
            "expenditure", "orders", "receipts", "invoices", "transactions",
        ]
        if not any(token in q_lower for token in purchase_tokens):
            return None

        # Parse target calendar year if referenced.
        target_year: Optional[int] = None
        if "last year" in q_lower:
            target_year = 2025
        elif "this year" in q_lower:
            target_year = 2026
        else:
            year_match = re.search(r"\b(20[12][0-9])\b", q_lower)
            if year_match:
                target_year = int(year_match.group(1))

        # Check for specific merchant or vendor filter.
        target_merchant: Optional[str] = None
        for brand in [
            "amazon", "apple", "uber", "wagamama", "cote", "deliveroo",
            "paypal", "trainline",
        ]:
            if brand in q_lower:
                target_merchant = brand
                break

        res = self.tx_store.query_transactions(
            year=target_year,
            merchant=target_merchant,
            limit=50,
        )
        if res.get("count", 0) == 0:
            return None

        formatted_answer = self.tx_store.format_aggregation_response(
            user_query, res
        )

        citations = []
        for tx in res.get("transactions", [])[:5]:
            citations.append(
                Citation(
                    file_name=tx.get("subject", "Financial Record"),
                    page_number=1,
                    section_heading=f"Merchant: {tx.get('merchant')}",
                    snippet=(
                        f"Date: {tx.get('transaction_date')} | "
                        f"Amount: {tx.get('amount_display')} | "
                        f"Desc: {tx.get('item_description')}"
                    ),
                )
            )

        return RAGResponse(
            query=user_query,
            answer=formatted_answer,
            citations=citations,
            model_used="deterministic-sql-ledger",
            context_chunks_count=res.get("count", 0),
        )

    def query(
        self,
        user_query: str,
        top_k: int = 5,
        model_override: Optional[str] = None,
    ) -> RAGResponse:
        """
        Retrieve context and generate an attributed answer.

        Execution steps:
          1. Step 1: Check Path B aggregation intent (deterministic ledger).
          2. Step 2: Retrieve top_k relevant fragments via hybrid search.
          3. Step 3: Assemble structured citations from retrieved chunks.
          4. Step 4: Check if context is empty; return clean refusal if so.
          5. Step 5: Construct strict institutional system prompt.
          6. Step 6: Query local Ollama service with think=false.
          7. Step 7: Filter internal reasoning tokens and validate response.

        Args:
          user_query: Search inquiry in natural English.
          top_k: Number of context fragments to supply.
          model_override: Optional Small Language Model (SLM) tag override.

        Returns:
          RAGResponse object populated with answer text and citations.
        """
        # Step 1: Check Path B aggregation intent.
        ledger_res = self._check_aggregation_intent(user_query)
        if ledger_res is not None:
            return ledger_res

        # Step 2: Retrieve top_k relevant fragments via hybrid search.
        hits = self.indexer.search_hybrid(user_query, top_k=top_k)

        # Step 2: Assemble structured citations.
        citations: List[Citation] = []
        context_blocks: List[str] = []

        for h in hits:
            citations.append(
                Citation(
                    file_name=h.get("file_name", "Unknown"),
                    page_number=h.get("page_number", 1),
                    section_heading=h.get("section_heading", ""),
                    snippet=h.get("text", "")[:300],
                )
            )
            block = (
                f"[Source: {h.get('file_name')} | Page: {h.get('page_number')}]\n"
                f"{h.get('text')}"
            )
            context_blocks.append(block)

        # Step 3: Check if context is empty.
        if not hits:
            return RAGResponse(
                query=user_query,
                answer=(
                    "The practice archive contains no record of this information."
                ),
                citations=[],
                model_used="deterministic-guard",
                context_chunks_count=0,
            )

        # Step 4: Construct institutional ambiguity-aware prompt.
        context_text = "\n\n---\n\n".join(context_blocks)
        ref_date = datetime.now(timezone.utc).strftime("%d %B %Y")
        system_prompt = (
            "You are the sovereign practice clerk for a boutique private "
            "practice in London.\n"
            f"Reference Date: {ref_date}\n\n"
            "Answer the client inquiry using strictly and ONLY the factual "
            "excerpts provided below.\n\n"
            "GOVERNANCE & AMBIGUITY RESOLUTION DIRECTIVES:\n"
            "1. CITATION DISCIPLINE: Every statement of fact must cite the "
            "exact document title and page number from the header, "
            "e.g. [Document.pdf | Page: 1].\n"
            "2. MULTIPLE MATTERS / AMBIGUITY: If the retrieved excerpts describe "
            "more than one distinct agreement, matter, person, or transaction "
            "matching the query, you MUST NOT arbitrarily pick one. Instead, "
            "explicitly enumerate EACH matter separately (e.g. 'Matter A: ... "
            "[Citation]', 'Matter B: ... [Citation]').\n"
            "3. CHRONOLOGY & SUPERSEDED TERMS: If documents contain conflicting "
            "terms or revisions across different dates (e.g. rate revisions, "
            "contract addenda), specify the terms chronologically by date and "
            "clearly state the latest effective position.\n"
            "4. PRESUPPOSITION CHECK: If the user inquiry contains an "
            "assertion or premise that is directly contradicted by the context "
            "(for example, asking why an event failed when the document states "
            "it succeeded), explicitly refute the false presupposition before "
            "citing the factual position.\n"
            "5. NO EXTRAPOLATION: Do not extrapolate or assume facts not "
            "explicitly stated. If the provided context does not contain factual "
            "evidence to answer the question, respond verbatim: "
            "'The practice archive contains no record of this information.'"
        )

        user_content = (
            f"Excerpts from practice records:\n\n{context_text}\n\n"
            f"Question: {user_query}\n\n"
            f"Answer with exact citations:"
        )

        # Step 5: Query local Ollama service.
        answer_text = ""
        active_model = model_override or self.model_name
        model_tag = active_model
        try:
            with httpx.Client(timeout=180.0) as client:
                res = client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": active_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content},
                        ],
                        "stream": False,
                        "think": False,
                        "keep_alive": "5m",
                        "options": {
                            "temperature": 0.0,
                            "top_k": 1,
                            "top_p": 1.0,
                            "num_predict": 384,
                            "num_ctx": 8192,
                            "num_thread": 4,
                            "repeat_penalty": 1.0,
                        },
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    raw_content = (
                        data.get("message", {}).get("content", "").strip()
                    )
                    # Strip reasoning tags if model emits internal thoughts.
                    if "<think>" in raw_content and "</think>" in raw_content:
                        raw_content = raw_content.split("</think>")[-1].strip()
                    answer_text = raw_content
        except Exception:
            answer_text = ""

        # Step 6: Graceful fallback synthesis if Ollama is not yet active.
        if not answer_text:
            top_hit = hits[0]
            top_file = top_hit.get("file_name", "Practice Archive")
            top_page = top_hit.get("page_number", 1)
            first_sentence = top_hit.get("text", "").split(".")[0].strip()
            answer_text = (
                f"According to practice records: {first_sentence}. "
                f"[{top_file}, Page {top_page}]"
            )
            model_tag = "extractive-fallback"

        return RAGResponse(
            query=user_query,
            answer=answer_text,
            citations=citations,
            model_used=model_tag,
            context_chunks_count=len(hits),
        )
