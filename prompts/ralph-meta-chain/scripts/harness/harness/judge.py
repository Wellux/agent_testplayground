"""Rubric judge — score a single output against assert rules + an LLM rubric."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

log = logging.getLogger(__name__)

BANNED_PHRASES = [
    "Great question",
    "I'd be happy to",
    "Certainly!",
    "As an AI",
]

RUBRIC_PROMPT = """\
You are a strict prompt-output judge. Score the OUTPUT below on a 1-5 rubric:
- helpfulness (does it answer the task?)
- brevity     (no preambles, no padding)
- format      (matches any explicit format requirements)

Return JSON ONLY, no prose, exactly:
{"helpfulness": <1..5>, "brevity": <1..5>, "format": <1..5>}

OUTPUT:
{output}
"""


def _llm_rubric(text: str, judge_model: str) -> float:
    """Average of helpfulness/brevity/format from a single judge call."""
    try:
        from anthropic import Anthropic
    except ImportError:  # pragma: no cover
        log.warning("anthropic SDK not installed; using stub rubric=3.0")
        return 3.0

    client = Anthropic()
    msg = client.messages.create(
        model=judge_model,
        max_tokens=128,
        temperature=0.0,
        messages=[{"role": "user", "content": RUBRIC_PROMPT.format(output=text)}],
    )
    raw = ""
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            raw += block.text
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        log.warning("rubric judge returned non-JSON; defaulting to 3.0")
        return 3.0
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return 3.0
    vals = [float(d.get(k, 3)) for k in ("helpfulness", "brevity", "format")]
    return sum(vals) / len(vals)


def _check_asserts(text: str, asserts: list[dict[str, Any]]) -> int:
    """Return number of failed asserts (banned-phrase + max-tokens, etc)."""
    failed = 0
    tokens = max(1, len(text.split()))
    for a in asserts:
        kind = a.get("type")
        val = a.get("value")
        if kind == "max-tokens" and tokens > int(val):
            failed += 1
        elif kind == "not-contains" and isinstance(val, str) and val in text:
            failed += 1
        elif kind == "contains" and isinstance(val, str) and val not in text:
            failed += 1
    return failed


def _count_banned(text: str) -> int:
    return sum(1 for p in BANNED_PHRASES if p.lower() in text.lower())


def score(*, text: str, judge_model: str, asserts: list[dict[str, Any]] | None = None) -> dict[str, float]:
    rubric = _llm_rubric(text, judge_model)
    banned = _count_banned(text)
    failed = _check_asserts(text, asserts or [])
    return {"rubric": rubric, "banned": banned + failed}
