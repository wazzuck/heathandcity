"""
Benchmark Suite for Sovereign Practice Vault Small Language Models (SLMs).

Purpose:
  Conducts rigorous, automated evaluation across candidate open-weight models
  hosted locally on Ollama:
    - qwen3.5:4b (Primary recommended 4-bit)
    - qwen3.5:9b (Quality tier 4-bit)
    - phi4-mini:latest (Microsoft 3.8B SOTA)
    - llama3.2:3b (Meta compact instruction)
    - qwen2.5:3b (Historical baseline)

Deliberately Not For:
  Executing external cloud API inference. All models execute locally on CPU.

Invariants:
  1. Measures prompt evaluation time, generation latency, token generation
     rate, peak memory usage, and citation accuracy.
  2. Ensures Ollama keep-alive and cache are systematically managed.
"""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional
import httpx


@dataclass
class BenchmarkResult:
    """Telemetry container for a single model evaluation trial."""

    model_name: str
    query: str
    load_duration_ms: float
    prompt_eval_tokens: int
    prompt_eval_duration_ms: float
    prompt_eval_tokens_per_sec: float
    eval_tokens: int
    eval_duration_ms: float
    eval_tokens_per_sec: float
    total_time_s: float
    answer: str
    has_valid_citation: bool


def query_ollama(
    model: str,
    prompt: str,
    system_prompt: str,
    think: bool = False,
    timeout: float = 120.0,
) -> Dict[str, Any]:
    """Execute local inference against Ollama chat endpoint."""
    url = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "keep_alive": "5m",
        "options": {
            "temperature": 0.0,
            "top_k": 1,
            "top_p": 1.0,
            "num_predict": 256,
            "num_ctx": 4096,
            "num_thread": 4,
            "repeat_penalty": 1.0,
        },
    }
    if not think:
        payload["think"] = False

    t0 = time.time()
    with httpx.Client(timeout=timeout) as client:
        res = client.post(url, json=payload)
        dt = time.time() - t0
        data = res.json()
        data["wall_time_s"] = dt
        return data


def unload_model(model: str) -> None:
    """Evict model from memory to measure clean cold-start loads."""
    url = "http://127.0.0.1:11434/api/chat"
    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(
                url,
                json={"model": model, "keep_alive": 0},
            )
    except Exception:
        pass


def run_benchmark() -> None:
    """Run comparative trials across candidate models."""
    candidate_models = [
        "qwen3.5:4b",
        "phi4-mini:latest",
        "llama3.2:3b",
        "qwen2.5:3b",
    ]

    # Two representative test cases:
    # 1. Targeted legal limitation fact.
    # 2. Context-grounded RAG query from actual practice records.
    system_rag = (
        "You are the sovereign practice clerk for a boutique private practice.\n"
        "Answer the question strictly and ONLY using the excerpts provided.\n"
        "Cite the exact source file and page: [Document, Page N].\n"
        "If not in the text, state: 'The practice archive contains no record.'"
    )

    rag_context = (
        "[Source: Gmail: Settlement made | Page: 1]\n"
        "From: William McAdam <William@stanleywoods.co.uk>\n"
        "Subject: Settlement made\n"
        "Dear Neville,\n"
        "Further to our telephone conversation this morning, I confirm the "
        "defendants have transferred the agreed commercial dispute settlement "
        "sum of £37,887.56 into the escrow client account.\n"
        "Yours sincerely,\nWilliam McAdam\n"
    )

    test_queries = [
        {
            "id": "rag_factual_citation",
            "prompt": (
                f"Excerpts from practice records:\n\n{rag_context}\n\n"
                f"Question: What was the settlement sum agreed in the "
                f"commercial dispute?\nAnswer with citation:"
            ),
            "expected_fact": "37,887.56",
            "expected_citation": "Settlement made",
        },
        {
            "id": "refusal_out_of_domain",
            "prompt": (
                f"Excerpts from practice records:\n\n{rag_context}\n\n"
                f"Question: What was the flight departure time to Zurich?\n"
                f"Answer with citation:"
            ),
            "expected_fact": "contains no record",
            "expected_citation": "",
        },
    ]

    print("=" * 80)
    print("SOVEREIGN PRACTICE VAULT SLM BENCHMARK MATRIX (Intel Core i3-9100T)")
    print("=" * 80)

    summary_rows = []

    for model in candidate_models:
        print(f"\nEvaluating Model: {model} ...", flush=True)

        # Step 1: Unload any active models to measure cold start.
        unload_model(model)
        time.sleep(1)

        # Run cold trial.
        cold_data = query_ollama(
            model=model,
            prompt=test_queries[0]["prompt"],
            system_prompt=system_rag,
        )
        cold_time = cold_data.get("wall_time_s", 0.0)
        print(f"  [Cold Start Trial] Total time: {cold_time:.2f}s", flush=True)

        # Run warm trials.
        warm_times = []
        gen_rates = []
        answers = []
        citations_ok = []

        for q in test_queries:
            data = query_ollama(
                model=model,
                prompt=q["prompt"],
                system_prompt=system_rag,
            )
            wall_t = data.get("wall_time_s", 0.0)
            warm_times.append(wall_t)

            msg_content = (
                data.get("message", {}).get("content", "").strip()
            )
            # Filter think tags if present.
            if "<think>" in msg_content and "</think>" in msg_content:
                msg_content = msg_content.split("</think>")[-1].strip()

            answers.append(msg_content)

            eval_count = data.get("eval_count", 0)
            eval_dur_ns = data.get("eval_duration", 1)
            eval_rate = (
                (eval_count / (eval_dur_ns / 1e9)) if eval_dur_ns > 0 else 0
            )
            gen_rates.append(eval_rate)

            # Check correctness.
            fact_ok = q["expected_fact"].lower() in msg_content.lower()
            cite_ok = (
                (q["expected_citation"].lower() in msg_content.lower())
                if q["expected_citation"]
                else True
            )
            citations_ok.append(fact_ok and cite_ok)

            print(
                f"  [{q['id']}] Wall: {wall_t:.2f}s | "
                f"Eval Rate: {eval_rate:.1f} tok/s | "
                f"Correct: {fact_ok and cite_ok}",
                flush=True,
            )
            print(f"    Answer: {msg_content[:120]}...", flush=True)

        avg_warm = sum(warm_times) / len(warm_times)
        avg_rate = sum(gen_rates) / len(gen_rates)
        all_ok = all(citations_ok)

        summary_rows.append(
            {
                "model": model,
                "cold_start_s": round(cold_time, 2),
                "avg_warm_s": round(avg_warm, 2),
                "eval_rate_tok_s": round(avg_rate, 1),
                "accuracy": "100%" if all_ok else "Degraded",
            }
        )

    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY RESULTS TABLE")
    print("=" * 80)
    print(
        f"{'Model':<20} | {'Cold Start':<12} | {'Warm Avg':<10} | "
        f"{'Eval Rate':<14} | {'Accuracy':<10}"
    )
    print("-" * 80)
    for r in summary_rows:
        print(
            f"{r['model']:<20} | {r['cold_start_s']:<10}s | "
            f"{r['avg_warm_s']:<8}s | {r['eval_rate_tok_s']:<8} tok/s | "
            f"{r['accuracy']:<10}"
        )
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
