"""Support ticket classification through the shared LLM door (common/llm.py).

Pure functions, no web framework: `classify(text)` returns a validated `TicketResult`.
Works with no API key (deterministic offline answer) and with Anthropic / OpenAI / Gemini via env.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import llm  # noqa: E402  (sys.path set above)

TAGS = ["billing", "technical", "feature_request", "account", "security", "other"]
PRIORITIES = ["Low", "Medium", "High", "Urgent"]
Priority = Literal["Low", "Medium", "High", "Urgent"]

SYSTEM_PROMPT = (
    "You are a support ticket triage assistant for a SaaS company. "
    "Read the ticket and return structured metadata. "
    f"Allowed tags: {', '.join(TAGS)} (one or more, lowercase). "
    f"Priority is one of {', '.join(PRIORITIES)}: Urgent means revenue, security or a full outage; "
    "High means a blocked user or money at risk; Medium means degraded but working; Low means a question or wish. "
    "suggested_action is one concise sentence naming the team and the next step."
)

SCHEMA_HINT = {
    "tags": ["|".join(TAGS)],
    "priority": "|".join(PRIORITIES),
    "suggested_action": "<one sentence next step>",
}


class TicketResult(BaseModel):
    tags: list[str] = Field(default_factory=list)
    priority: Priority = "Medium"
    suggested_action: str = ""
    provider: str = "offline"
    model: str = "offline"

    @field_validator("tags", mode="before")
    @classmethod
    def _norm_tags(cls, v):
        if isinstance(v, str):
            v = [t for t in v.replace(";", ",").split(",")]
        out = []
        for t in v or []:
            t = str(t).strip().lower().replace(" ", "_").replace("-", "_")
            if t and t not in out:
                out.append(t)
        return out or ["other"]

    @field_validator("priority", mode="before")
    @classmethod
    def _norm_priority(cls, v):
        s = str(v or "").strip().capitalize()
        return s if s in PRIORITIES else "Medium"


def classify(ticket_text: str) -> TicketResult:
    """Classify one ticket. Raises ValueError on empty text."""
    text = (ticket_text or "").strip()
    if not text:
        raise ValueError("ticket_text is empty")
    raw = llm.complete_json(SYSTEM_PROMPT, text, schema_hint=SCHEMA_HINT)
    return TicketResult(
        tags=raw.get("tags", []),
        priority=raw.get("priority", "Medium"),
        suggested_action=str(raw.get("suggested_action", "")).strip(),
        provider=llm.provider(),
        model=llm.model(),
    )
