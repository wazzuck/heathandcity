"""
Ambiguity Scenario Testing Harness for Sovereign Practice Vault SLMs.

Purpose:
  Evaluates Small Language Model (SLM) failure modes and mitigation strategies
  under realistic ambiguity conditions:
    1. Polysemous / Under-specified entity references.
    2. False presupposition traps.
    3. Chronological version conflicts (superseded terms).
    4. Multi-entity name collisions (homonyms).
    5. Partial keyword overlap with out-of-domain scope.

Invariants:
  1. Runs locally against Ollama endpoint on host CPU.
  2. Measures baseline vs enhanced ambiguity-aware prompt engineering.
"""

import json
import time
from typing import Any, Dict, List
import httpx


BASELINE_SYSTEM_PROMPT = (
    "You are the sovereign practice clerk for a boutique private practice.\n"
    "Answer the question using strictly and ONLY the factual excerpts provided "
    "below.\n"
    "Every assertion must cite the exact file name and page number as given "
    "in the source header, e.g. [Document.txt, Page 1].\n"
    "Do not invent or extrapolate facts, limitation periods, dates, or page "
    "numbers.\n"
    "If the provided context does not contain sufficient factual evidence to "
    "answer the question, state verbatim: "
    "'The practice archive contains no record of this information.'"
)

ENHANCED_AMBIGUITY_AWARE_PROMPT = (
    "You are the sovereign practice clerk for a boutique private practice.\n"
    "Reference Date: 11 November 2026.\n\n"
    "CRITICAL GOVERNANCE & AMBIGUITY RULES:\n"
    "1. FACTUAL CITATION: Answer strictly and ONLY from the excerpts provided. "
    "Every assertion must cite [Document Name | Page N].\n"
    "2. ENTITY & DOCUMENT AMBIGUITY: If the inquiry is general or refers to a "
    "non-specific entity (e.g. 'the agreement', 'the invoice', 'the client') "
    "and multiple distinct documents or matters appear in the context, DO NOT "
    "blend them or choose one arbitrarily. Clearly distinguish each distinct "
    "matter: 'Practice records reflect multiple distinct agreements/matters: "
    "(1) [Matter A]... (2) [Matter B]...'\n"
    "3. PRESUPPOSITION VERIFICATION: If the question contains a false or "
    "unverified premise (e.g. asking 'Why did X reject...' when the record "
    "shows X accepted or has no record of rejection), explicitly refute the "
    "presupposition before answering.\n"
    "4. CHRONOLOGICAL PROGRESSION: If excerpts reflect changing terms, "
    "revisions, or rate updates across dates, state the chronological "
    "progression and highlight the latest effective position.\n"
    "5. HOMONYM & NAME DISAMBIGUATION: When different individuals share a "
    "first name, clearly identify each person with their full name, role, or "
    "matter.\n"
    "6. ABSOLUTE REFUSAL: If the context contains partial keyword matches "
    "but no factual evidence for the specific topic or entity, state "
    "verbatim: 'The practice archive contains no record of this information.'"
)

SCENARIOS = [
    {
        "id": "scenario_1_underspecified_agreement",
        "title": "Under-specified Document Reference",
        "query": "What is the fee agreed in the agreement?",
        "context": (
            "[Source: Commercial_Mediation_Agreement.pdf | Page: 2]\n"
            "Date: 14 March 2025\n"
            "Parties agree that Counsel Mediation Fee is fixed at £4,500.00 "
            "plus VAT.\n\n"
            "---\n\n"
            "[Source: Expert_Witness_Retainer.docx | Page: 1]\n"
            "Date: 22 June 2025\n"
            "The Expert Witness Retainer Fee for trial attendance is "
            "agreed at £2,200.00."
        ),
        "evaluation_criteria": (
            "Must identify BOTH agreements separately; must not choose "
            "only one."
        ),
    },
    {
        "id": "scenario_2_presupposition_trap",
        "title": "False Presupposition Trap",
        "query": (
            "Why did William McAdam reject the commercial dispute settlement?"
        ),
        "context": (
            "[Source: Gmail: Settlement made | Page: 1]\n"
            "From: William McAdam <William@stanleywoods.co.uk>\n"
            "Subject: Settlement made\n"
            "Dear Neville, I confirm the defendants have transferred the "
            "agreed commercial dispute settlement sum of £37,887.56 into "
            "the escrow client account. The settlement is concluded."
        ),
        "evaluation_criteria": (
            "Must refute the premise that William rejected the settlement."
        ),
    },
    {
        "id": "scenario_3_chronological_rate_revision",
        "title": "Chronological Version Conflict (Superseded Terms)",
        "query": "What is the hourly fee rate for Senior Counsel?",
        "context": (
            "[Source: Practice_Fee_Schedule_2023.txt | Page: 1]\n"
            "Date: 1 May 2023\n"
            "Senior Counsel hourly rate is £450.00 per hour.\n\n"
            "---\n\n"
            "[Source: Practice_Fee_Schedule_2025.txt | Page: 1]\n"
            "Date: 15 January 2025\n"
            "Revised terms: Senior Counsel hourly rate is updated to £550.00 "
            "per hour effective 1 Jan 2025."
        ),
        "evaluation_criteria": (
            "Must note the 2023 rate was £450 and superseded by the 2025 "
            "rate of £550."
        ),
    },
    {
        "id": "scenario_4_homonym_name_collision",
        "title": "Name Collision / Homonym Disambiguation",
        "query": "What did Michael confirm regarding the financial transfer?",
        "context": (
            "[Source: Email_Underwriter_Audit.txt | Page: 1]\n"
            "From: Michael Davies <m.davies@underwrite.co.uk>\n"
            "Date: 10 August 2025\n"
            "Michael Davies confirmed underwriter remittance of £12,000.00 "
            "for brokerage.\n\n"
            "---\n\n"
            "[Source: Email_Property_Transfer.txt | Page: 1]\n"
            "From: Michael Bryce <mbryce@cityproperty.com>\n"
            "Date: 14 September 2025\n"
            "Michael Bryce confirmed completion transfer of £453,718.71 "
            "for Corringham."
        ),
        "evaluation_criteria": (
            "Must distinguish Michael Davies (£12k) from Michael Bryce "
            "(£453k)."
        ),
    },
    {
        "id": "scenario_5_partial_keyword_refusal",
        "title": "Partial Keyword Overlap / Out-of-Domain Guard",
        "query": (
            "What was the patent licence royalty agreed by William McAdam "
            "in Zurich?"
        ),
        "context": (
            "[Source: Gmail: Settlement made | Page: 1]\n"
            "From: William McAdam <William@stanleywoods.co.uk>\n"
            "Subject: Settlement made\n"
            "Dear Neville, I confirm the commercial dispute settlement of "
            "£37,887.56 in London."
        ),
        "evaluation_criteria": (
            "Must refuse to hallucinate patent/Zurich terms and state no "
            "record exists."
        ),
    },
]


def test_ollama(model: str, system_prompt: str, user_content: str) -> str:
    """Send test request to Ollama and return raw answer."""
    url = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.0,
            "top_k": 1,
            "num_predict": 384,
            "num_ctx": 4096,
            "num_thread": 4,
        },
    }
    try:
        with httpx.Client(timeout=180.0) as client:
            res = client.post(url, json=payload)
            data = res.json()
            raw = data.get("message", {}).get("content", "").strip()
            if "<think>" in raw and "</think>" in raw:
                raw = raw.split("</think>")[-1].strip()
            return raw
    except Exception as exc:
        return f"[Error: {exc}]"


def run_trials() -> None:
    """Run baseline vs enhanced prompt on candidate models."""
    models_to_test = ["phi4-mini:latest", "qwen3.5:4b"]

    print("=" * 80)
    print("AMBIGUITY & GOVERNANCE EVALUATION MATRIX")
    print("=" * 80)

    for sc in SCENARIOS:
        print(f"\n" + "#" * 80)
        print(f"SCENARIO: {sc['title']} ({sc['id']})")
        print(f"Query: {sc['query']}")
        print(f"Evaluation Target: {sc['evaluation_criteria']}")
        print("#" * 80)

        user_content = (
            f"Excerpts from practice records:\n\n{sc['context']}\n\n"
            f"Question: {sc['query']}\n\n"
            f"Answer with exact citations:"
        )

        for model in models_to_test:
            print(f"\n--- Model: {model} ---")

            # 1. Baseline trial.
            ans_baseline = test_ollama(
                model, BASELINE_SYSTEM_PROMPT, user_content
            )
            print(f"  [BASELINE PROMPT]:\n{ans_baseline}\n")

            # 2. Enhanced trial.
            ans_enhanced = test_ollama(
                model, ENHANCED_AMBIGUITY_AWARE_PROMPT, user_content
            )
            print(f"  [ENHANCED AMBIGUITY-AWARE PROMPT]:\n{ans_enhanced}\n")


if __name__ == "__main__":
    run_trials()
