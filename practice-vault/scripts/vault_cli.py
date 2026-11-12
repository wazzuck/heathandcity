#!/usr/bin/env python3
"""
==============================================================================
FILE: practice-vault/scripts/vault_cli.py
==============================================================================

PURPOSE:
Interactive Command-Line Interface (CLI) and scriptable utility for the Heath
& City Practice Vault sovereign document intelligence appliance. Allows
partners and operators to query, search, inspect status, and monitor
synchronisation directly from their terminal.

WHAT THIS FILE IS DELIBERATELY NOT FOR:
- Does not run heavy model weights in its own process; delegates to the local
  asynchronous backend Hypertext Transfer Protocol (HTTP) daemon.
- Does not expose any external network sockets or bypass local loopback
  security boundaries.

INVARIANTS:
1. Connects exclusively to the local loopback service interface
   (http://127.0.0.1:8080) to preserve zero data leakage.
2. Formats all console output with British Professional English conventions.
3. Degrades gracefully with actionable diagnostic guidance when the backend
   daemon is offline.
==============================================================================
"""

import argparse
import json
import os
from pathlib import Path
import readline
import sys
import time
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request

# Default backend server Uniform Resource Locator (URL) on local loopback.
DEFAULT_VAULT_URL = "http://127.0.0.1:8080"

# ANSI Terminal Colour Escapes for formatted console presentation.
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_DIM = "\033[2m"
COLOR_CYAN = "\033[36m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_MAGENTA = "\033[35m"


def supports_color() -> bool:
    """
    Check whether the active terminal environment supports ANSI colour codes.

    Returns:
        bool: True if stdout is an interactive terminal and colour is enabled.
    """
    if os.environ.get("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def style(text: str, color_code: str) -> str:
    """
    Wrap text in an ANSI terminal escape sequence when colour is supported.

    Args:
        text (str): Input string to stylise.
        color_code (str): ANSI escape sequence.

    Returns:
        str: Styled string or raw text if colour is disabled.
    """
    if supports_color():
        return f"{color_code}{text}{COLOR_RESET}"
    return text


# GNU Readline non-printing escape sequence delimiters.
RL_PROMPT_START = "\001"
RL_PROMPT_END = "\002"


def rl_style(text: str, color_code: str) -> str:
    """
    Format prompt text with ANSI escape codes shielded for GNU Readline.

    Non-printing terminal escape sequences inside an input() prompt must be
    enclosed within RL_PROMPT_START_IGNORE (\\001) and RL_PROMPT_END_IGNORE
    (\\002) delimiters. This enables GNU Readline to calculate the true visual
    character width of the prompt. Consequently, pressing the Backspace key
    cannot delete past the prompt boundary or misalign the cursor.

    Args:
        text: Prompt label or symbol to format.
        color_code: ANSI escape sequence code (e.g. COLOR_CYAN).

    Returns:
        Formatted prompt string with non-printing sequences shielded.
    """
    if supports_color():
        return (
            f"{RL_PROMPT_START}{color_code}{RL_PROMPT_END}"
            f"{text}"
            f"{RL_PROMPT_START}{COLOR_RESET}{RL_PROMPT_END}"
        )
    return text


class VaultClient:
    """
    HTTP client communicating with the local Practice Vault backend daemon.

    Attributes:
        base_url (str): Root loopback endpoint of the running appliance.
        timeout (float): Network request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_VAULT_URL,
        timeout: float = 180.0,
    ) -> None:
        """
        Initialise the Practice Vault client instance.

        Args:
            base_url (str): Local API root address.
            timeout (float): Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a JSON POST request against the local backend daemon.

        Args:
            endpoint (str): API route path.
            payload (Dict[str, Any]): Dictionary serialized as JSON.

        Returns:
            Dict[str, Any]: Parsed JSON response from the server.
        """
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as err:
            raise ConnectionError(
                f"Unable to reach Practice Vault daemon at {self.base_url}.\n"
                f"Please verify the backend server is active (reason: {err})."
            ) from err

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """
        Perform a JSON GET request against the local backend daemon.

        Args:
            endpoint (str): API route path.

        Returns:
            Dict[str, Any]: Parsed JSON response from the server.
        """
        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as err:
            raise ConnectionError(
                f"Unable to reach Practice Vault daemon at {self.base_url}.\n"
                f"Please verify the backend server is active (reason: {err})."
            ) from err

    def get_status(self) -> Dict[str, Any]:
        """Retrieve operational telemetry and memory utilisation."""
        return self._get("/api/status")

    def get_sync_status(self) -> Dict[str, Any]:
        """Retrieve Google Workspace synchronisation progress and state."""
        return self._get("/api/google/status")

    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Execute sub-second hybrid lexical and vector search.

        Args:
            query (str): Natural language search terms.
            top_k (int): Maximum number of ranked results.

        Returns:
            Dict[str, Any]: Ranked hits with metadata and snippets.
        """
        return self._post("/api/search", {"query": query, "top_k": top_k})

    def ask(
        self,
        query: str,
        top_k: int = 3,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute full Retrieval-Augmented Generation (RAG) query.

        Args:
            query (str): Plain-English question for practice records.
            top_k (int): Number of context chunks retrieved for synthesis.
            model (Optional[str]): Quantised local reasoning model tag.

        Returns:
            Dict[str, Any]: Synthesised answer with verified source citations.
        """
        payload: Dict[str, Any] = {"query": query, "top_k": top_k}
        if model:
            payload["model"] = model
        return self._post("/api/query", payload)


def format_status(data: Dict[str, Any]) -> str:
    """
    Format status telemetry into an executive summary block.

    Args:
        data (Dict[str, Any]): Raw status dictionary from API.

    Returns:
        str: Formatted human-readable status overview.
    """
    lines = [
        style("=== Heath & City Practice Vault Status ===", COLOR_BOLD),
        f"  Appliance Health   : {style(data.get('status', 'unknown'), COLOR_GREEN)}",
        f"  Indexed Chunks     : {style(str(data.get('indexed_chunks_count', 0)), COLOR_CYAN)}",
        f"  Memory Footprint   : {data.get('memory_rss_mb', 0):.2f} MB RSS",
        f"  Active Model       : {style(str(data.get('llm_model', 'none')), COLOR_YELLOW)}",
        f"  Embedding Engine   : {data.get('embed_model', 'none')}",
    ]
    return "\n".join(lines)


def format_sync(data: Dict[str, Any]) -> str:
    """
    Format Google Workspace synchronisation status into an overview.

    Args:
        data (Dict[str, Any]): Raw sync dictionary from API.

    Returns:
        str: Formatted synchronisation status summary.
    """
    gmail_state = data.get("gmail_sync", {})
    docs_state = data.get("docs_sync", {})
    lines = [
        style("=== Google Workspace Synchronisation ===", COLOR_BOLD),
        f"  Configured Status  : {data.get('configured', False)}",
        f"  Authenticated      : {data.get('authenticated', False)}",
        f"  Gmail Messages     : {gmail_state.get('total_messages_indexed', 0)} indexed",
        f"  Gmail In-Progress  : {gmail_state.get('in_progress', False)}",
        f"  Google Docs Chunks : {docs_state.get('total_chunks_indexed', 0)} indexed",
        f"  Docs In-Progress   : {docs_state.get('in_progress', False)}",
    ]
    return "\n".join(lines)


def format_search_results(data: Dict[str, Any]) -> str:
    """
    Format hybrid search results into clear ranked cards.

    Args:
        data (Dict[str, Any]): Search response containing results list.

    Returns:
        str: Formatted terminal output for search hits.
    """
    results = data.get("results", [])
    if not results:
        return style("No matching documents found in practice archive.", COLOR_YELLOW)

    out = [style(f"Found {len(results)} matching records:", COLOR_BOLD)]
    for idx, hit in enumerate(results, start=1):
        file_name = hit.get("file_name", "Untitled Record")
        page = hit.get("page_number", 1)
        score = (
            hit.get("rerank_score")
            or hit.get("score")
            or hit.get("rrf_score", 0.0)
        )
        heading = hit.get("section_heading", "General")
        raw_snippet = hit.get("snippet") or hit.get("text", "")
        snippet = " ".join(raw_snippet.strip().replace("\r", " ").split())
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."

        out.append(
            f"\n  {style(f'[{idx}]', COLOR_CYAN)} {style(file_name, COLOR_BOLD)} "
            f"(Page {page}) — {style(f'Score: {score:.3f}', COLOR_DIM)}"
        )
        out.append(f"      {style('Section:', COLOR_DIM)} {heading}")
        out.append(f"      {style('Snippet:', COLOR_DIM)} {snippet}")
    return "\n".join(out)


def format_qa_response(data: Dict[str, Any], elapsed_sec: float) -> str:
    """
    Format a RAG question answering response with citations and telemetry.

    Args:
        data (Dict[str, Any]): Response containing answer and citations.
        elapsed_sec (float): Total round-trip execution latency in seconds.

    Returns:
        str: Formatted terminal response block.
    """
    answer = data.get("answer", "No answer generated.").strip()
    model = data.get("model_used", "unknown")
    citations = data.get("citations", [])

    out = [
        style("=== Synthesised Answer ===", COLOR_BOLD),
        f"{answer}\n",
        style("=== Source Citations ===", COLOR_BOLD),
    ]
    if citations:
        for idx, cite in enumerate(citations, start=1):
            file_name = cite.get("file_name", "Unknown File")
            page = cite.get("page_number", 1)
            heading = cite.get("section_heading", "")
            out.append(
                f"  [{idx}] {style(file_name, COLOR_GREEN)} (Page {page})"
                f"{f' — {heading}' if heading else ''}"
            )
    else:
        out.append("  (No direct citations returned)")

    out.append(
        f"\n{style('Telemetry:', COLOR_DIM)} "
        f"Latency: {elapsed_sec:.2f}s | Model: {model} | Chunks: {len(citations)}"
    )
    return "\n".join(out)


def run_repl(client: VaultClient, default_model: Optional[str] = None) -> None:
    """
    Run an interactive Read-Eval-Print Loop (REPL) session for the user.

    Args:
        client (VaultClient): Initialised appliance API client.
        default_model (Optional[str]): Selected reasoning model override.
    """
    current_model = default_model
    print(style("=" * 68, COLOR_CYAN))
    print(style("  Heath & City Practice Vault — Sovereign Terminal Interface", COLOR_BOLD))
    print(style("=" * 68, COLOR_CYAN))
    print("Type plain questions to interrogate practice archives with citations.")
    print("Available commands:")
    print("  /search <terms>   : Sub-second hybrid search across all records")
    print("  /model <tag>      : Switch active SLM (e.g. qwen2.5:3b, qwen2.5:7b)")
    print("  /status           : Inspect RAM footprint and chunk statistics")
    print("  /sync             : Check Google Drive & Gmail indexing state")
    print("  /help             : Show this guidance message")
    print("  /exit, /quit      : Terminate session\n")

    # Initialise history storage.
    history_file = Path.home() / ".practice_vault_history"
    try:
        if history_file.is_file():
            readline.read_history_file(str(history_file))
    except Exception:
        pass

    while True:
        try:
            model_tag = f" [{current_model}]" if current_model else ""
            prompt = (
                f"{rl_style('vault', COLOR_CYAN)}"
                f"{rl_style(model_tag, COLOR_DIM)}> "
            )
            user_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Practice Vault session.")
            break

        if not user_input:
            continue

        if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
            print("Exiting Practice Vault session.")
            break

        if user_input.lower() in ["/help", "help", "?"]:
            print("\nCommands:")
            print("  /search <terms>   : Fast hybrid vector & lexical search")
            print("  /model <tag>      : Set reasoning model override")
            print("  /status           : View appliance operational metrics")
            print("  /sync             : View mailbox and Drive sync status")
            print("  /exit             : Quit session\n")
            continue

        if user_input.lower() == "/status":
            try:
                data = client.get_status()
                print("\n" + format_status(data) + "\n")
            except Exception as e:
                print(style(f"\nError: {e}\n", COLOR_RED))
            continue

        if user_input.lower() == "/sync":
            try:
                data = client.get_sync_status()
                print("\n" + format_sync(data) + "\n")
            except Exception as e:
                print(style(f"\nError: {e}\n", COLOR_RED))
            continue

        if user_input.startswith("/model"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                current_model = parts[1].strip()
                print(f"Active reasoning model set to: {style(current_model, COLOR_YELLOW)}\n")
            else:
                current_model = None
                print("Active reasoning model reset to server default.\n")
            continue

        if user_input.startswith("/search"):
            query_terms = user_input[7:].strip()
            if not query_terms:
                print(style("Please provide search terms: /search <terms>", COLOR_YELLOW))
                continue
            try:
                t0 = time.time()
                res = client.search(query_terms, top_k=5)
                elapsed = time.time() - t0
                print("\n" + format_search_results(res))
                print(style(f"\nSearch completed in {elapsed:.3f}s\n", COLOR_DIM))
            except Exception as e:
                print(style(f"\nError executing search: {e}\n", COLOR_RED))
            continue

        # Default behaviour: full question answering RAG query.
        print(style("\nInterrogating practice records (synthesising)...", COLOR_DIM))
        try:
            t0 = time.time()
            resp = client.ask(user_input, top_k=3, model=current_model)
            elapsed = time.time() - t0
            print("\n" + format_qa_response(resp, elapsed) + "\n")
        except Exception as e:
            print(style(f"\nError processing query: {e}\n", COLOR_RED))

    # Persist command history.
    try:
        readline.write_history_file(str(history_file))
    except Exception:
        pass


def main() -> int:
    """
    Main entry point for the Command-Line Interface (CLI).

    Returns:
        int: Exit status code (0 for success, non-zero for error).
    """
    parser = argparse.ArgumentParser(
        description=(
            "Heath & City Practice Vault — Sovereign Terminal Interface. "
            "Execute plain-English queries, perform instant hybrid searches, "
            "and inspect local appliance telemetry."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Optional plain-English question to execute immediately.",
    )
    parser.add_argument(
        "-s",
        "--search",
        action="store_true",
        help="Execute sub-second hybrid search instead of full synthesis.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display operational health and memory metrics.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Display Google Drive and Gmail synchronisation telemetry.",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help="Quantised local reasoning model tag override (e.g. qwen2.5:3b).",
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=3,
        help="Number of context chunks to retrieve (default: 3).",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default=DEFAULT_VAULT_URL,
        help=f"Base backend daemon endpoint (default: {DEFAULT_VAULT_URL}).",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Start interactive Read-Eval-Print Loop (REPL) console.",
    )

    args = parser.parse_args()
    client = VaultClient(base_url=args.url)

    # 1. Status command flag.
    if args.status:
        try:
            status_data = client.get_status()
            print(format_status(status_data))
            return 0
        except Exception as exc:
            print(style(f"Status check failed: {exc}", COLOR_RED), file=sys.stderr)
            return 1

    # 2. Sync telemetry flag.
    if args.sync:
        try:
            sync_data = client.get_sync_status()
            print(format_sync(sync_data))
            return 0
        except Exception as exc:
            print(style(f"Sync check failed: {exc}", COLOR_RED), file=sys.stderr)
            return 1

    # 3. Direct command execution.
    if args.query:
        if args.search:
            try:
                t0 = time.time()
                res = client.search(args.query, top_k=args.top_k)
                elapsed = time.time() - t0
                print(format_search_results(res))
                print(style(f"\nCompleted in {elapsed:.3f}s", COLOR_DIM))
                return 0
            except Exception as exc:
                print(style(f"Search failed: {exc}", COLOR_RED), file=sys.stderr)
                return 1
        else:
            try:
                t0 = time.time()
                res = client.ask(args.query, top_k=args.top_k, model=args.model)
                elapsed = time.time() - t0
                print(format_qa_response(res, elapsed))
                return 0
            except Exception as exc:
                print(style(f"Query failed: {exc}", COLOR_RED), file=sys.stderr)
                return 1

    # 4. Default: Interactive REPL.
    run_repl(client, default_model=args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
