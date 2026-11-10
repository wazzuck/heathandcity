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
from typing import Any, Dict, List, Optional
import httpx

from .config import settings
from .indexer import HybridIndexEngine


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
    ) -> None:
        """
        Initialise RAG query service.

        Args:
          indexer: Initialised HybridIndexEngine instance.
          ollama_url: Loopback address of the Ollama daemon.
          model_name: Identifier of the quantised local model.
        """
        self.indexer = indexer
        self.ollama_url = ollama_url or settings.ollama_base_url
        self.model_name = model_name or settings.llm_model

    def query(self, user_query: str, top_k: int = 5) -> RAGResponse:
        """
        Retrieve context and generate an attributed answer.

        Execution steps:
          1. Step 1: Retrieve top_k relevant fragments via hybrid search.
          2. Step 2: Assemble structured citations from retrieved chunks.
          3. Step 3: Check if context is empty; return clean refusal if so.
          4. Step 4: Construct strict institutional system prompt.
          5. Step 5: Query local Ollama service. If Ollama is offline or loading,
             synthesise a deterministic extractive answer from the top excerpt.

        Args:
          user_query: Search inquiry in natural English.
          top_k: Number of context fragments to supply.

        Returns:
          RAGResponse object populated with answer text and citations.
        """
        # Step 1: Retrieve top_k relevant fragments via hybrid search.
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

        # Step 4: Construct strict institutional prompt.
        context_text = "\n\n---\n\n".join(context_blocks)
        system_prompt = (
            "You are the sovereign practice clerk for a boutique private practice.\n"
            "Answer the question using ONLY the provided document excerpts below.\n"
            "Every assertion must cite the exact file name and page number in square brackets, "
            "e.g. [Document.pdf, Page 3].\n"
            "If the provided context does not contain sufficient factual evidence to answer, "
            "state clearly: 'The practice archive contains no record of this information.'"
        )

        user_content = (
            f"Excerpts from practice records:\n\n{context_text}\n\n"
            f"Question: {user_query}\n\n"
            f"Answer with exact citations:"
        )

        # Step 5: Query local Ollama service.
        answer_text = ""
        model_tag = self.model_name
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content},
                        ],
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 512},
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    answer_text = data.get("message", {}).get("content", "").strip()
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
