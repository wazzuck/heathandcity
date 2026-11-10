"""
Autonomous Inbox Triage and Task Extraction Module.

Purpose:
  Analyses incoming practice correspondence (emails, letters, and client
  memoranda), categorising urgency, identifying deadlines, extracting
  actionable tasks, identifying monetary sums, and composing pre-drafted
  institutional replies staged in an approval queue.

Deliberately Not For:
  Directly sending outbound emails or modifying client mailboxes without
  explicit human authorisation.

Invariants:
  1. Human-in-the-loop safeguard: every generated draft reply requires
     affirmative partner sign-off before transmission.
  2. Data processing remains 100% on-premises.
"""

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from .config import settings


@dataclass
class TriageTask:
    """
    Actionable task derived from correspondence.

    Attributes:
      task_description: Plain-English summary of the required action.
      due_date: Inferred deadline (ISO format or descriptive string).
      matter_reference: Associated matter or client identifier.
      urgency: Priority rating (Urgent, Routine, or Low).
    """

    task_description: str
    due_date: str
    matter_reference: str
    urgency: str


@dataclass
class TriageResult:
    """
    Structured outcome of correspondence analysis.

    Attributes:
      intake_id: Unique identifier for tracking.
      subject: Subject line or heading of the message.
      sender: Sender email address or entity name.
      received_at: Timestamp of intake.
      priority: Overall priority rating (Urgent, Routine, or Low).
      matter_reference: Inferred matter or client reference code.
      identified_monetary_sums: List of financial figures extracted.
      tasks: Extracted actionable items.
      draft_reply: Pre-drafted institutional response awaiting partner sign-off.
      requires_approval: Affirmative flag enforcing partner sign-off.
    """

    intake_id: str
    subject: str
    sender: str
    received_at: str
    priority: str
    matter_reference: str
    identified_monetary_sums: List[str]
    tasks: List[TriageTask]
    draft_reply: str
    requires_approval: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert triage instance to dictionary representation."""
        return asdict(self)


class InboxTriageEngine:
    """
    Coordinates extraction of structured tasks and staging of draft replies.

    Attributes:
      ollama_url: Local loopback address for the inference daemon.
      model_name: Identifier for the local model.
    """

    def __init__(
        self,
        ollama_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """
        Initialise triage engine.

        Args:
          ollama_url: Loopback Uniform Resource Locator (URL) for Ollama.
          model_name: Model identifier for structured extraction.
        """
        self.ollama_url = ollama_url or settings.ollama_base_url
        self.model_name = model_name or settings.llm_model

    def process_message(
        self,
        raw_text: str,
        subject: str = "Client Correspondence",
        sender: str = "client@example.co.uk",
    ) -> TriageResult:
        """
        Process incoming text into structured triage metadata.

        Execution steps:
          1. Step 1: Assign intake timestamp and unique intake identifier.
          2. Step 2: Attempt extraction via local LLM structured prompt.
          3. Step 3: If LLM is unreachable, apply rule-based heuristics to
             detect deadlines, financial sums, and draft a professional reply.
          4. Step 4: Assemble and return TriageResult.

        Args:
          raw_text: Body text of the incoming message.
          subject: Email subject or memo title.
          sender: Sender address or entity name.

        Returns:
          TriageResult populated with categorised tasks and draft response.
        """
        intake_id = f"INT-{int(datetime.now(timezone.utc).timestamp())}"
        received_at = datetime.now(timezone.utc).isoformat()

        # Step 2: Attempt extraction via Ollama.
        llm_result = self._query_llm_triage(raw_text, subject, sender)
        if llm_result:
            llm_result.intake_id = intake_id
            llm_result.received_at = received_at
            return llm_result

        # Step 3: Rule-based heuristic fallback.
        return self._heuristic_fallback(
            intake_id, received_at, raw_text, subject, sender
        )

    def _query_llm_triage(
        self, raw_text: str, subject: str, sender: str
    ) -> Optional[TriageResult]:
        """Query Ollama with a strict JSON instruction schema."""
        prompt = (
            "You are an automated clerk for a senior professional practice. "
            "Analyze the correspondence below and return valid JSON with keys: "
            "'priority' ('Urgent', 'Routine', or 'Low'), 'matter_reference' (string), "
            "'monetary_sums' (list of strings), 'tasks' (list of objects with "
            "'task_description', 'due_date', 'matter_reference', 'urgency'), and "
            "'draft_reply' (formal, polite British English response staged for partner sign-off).\n\n"
            f"Subject: {subject}\n"
            f"Sender: {sender}\n"
            f"Body:\n{raw_text}\n\n"
            "Return JSON only:"
        )

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0.1},
                    },
                )
                if res.status_code == 200:
                    data = json.loads(res.json().get("response", "{}"))
                    tasks = [
                        TriageTask(
                            task_description=t.get("task_description", ""),
                            due_date=t.get("due_date", "TBD"),
                            matter_reference=t.get("matter_reference", "General"),
                            urgency=t.get("urgency", "Routine"),
                        )
                        for t in data.get("tasks", [])
                    ]
                    return TriageResult(
                        intake_id="",
                        subject=subject,
                        sender=sender,
                        received_at="",
                        priority=data.get("priority", "Routine"),
                        matter_reference=data.get("matter_reference", "General"),
                        identified_monetary_sums=data.get("monetary_sums", []),
                        tasks=tasks,
                        draft_reply=data.get("draft_reply", ""),
                    )
        except Exception:
            pass
        return None

    def _heuristic_fallback(
        self,
        intake_id: str,
        received_at: str,
        raw_text: str,
        subject: str,
        sender: str,
    ) -> TriageResult:
        """Deterministic heuristic extraction if model inference is offline."""
        lower_text = raw_text.lower()

        # Determine priority.
        urgent_keywords = ["urgent", "deadline", "hearing", "statute", "court", "asap"]
        priority = (
            "Urgent"
            if any(k in lower_text for k in urgent_keywords)
            else "Routine"
        )

        # Extract monetary figures (e.g. £1,500.00 or £250).
        money_matches = re.findall(r"£[0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?", raw_text)

        # Extract matter reference (e.g. MAT-1234 or Matter / Ref).
        matter_match = re.search(r"(?:Ref|Matter|Case)[:\s]+([A-Z0-9\-\/]+)", raw_text, re.IGNORECASE)
        matter_ref = matter_match.group(1) if matter_match else "General Practice"

        # Generate actionable task.
        tasks = [
            TriageTask(
                task_description=f"Review correspondence regarding {subject}",
                due_date="Within 24 hours" if priority == "Urgent" else "Within 3 business days",
                matter_reference=matter_ref,
                urgency=priority,
            )
        ]

        # Compose polite institutional draft reply.
        draft = (
            f"Dear Colleague,\n\n"
            f"Thank you for your correspondence regarding {subject}. "
            f"We acknowledge receipt and have staged this matter for the principal's "
            f"immediate consideration. A substantive reply will follow shortly.\n\n"
            f"Yours sincerely,\n"
            f"Practice Chambers"
        )

        return TriageResult(
            intake_id=intake_id,
            subject=subject,
            sender=sender,
            received_at=received_at,
            priority=priority,
            matter_reference=matter_ref,
            identified_monetary_sums=money_matches,
            tasks=tasks,
            draft_reply=draft,
            requires_approval=True,
        )
