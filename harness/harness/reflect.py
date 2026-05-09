"""Reflexion lesson-loop — generate a one-line `reflection:` for a candidate
prompt based on its most recent A/B verdict, and append it to the candidate's
frontmatter `reflections:` list. Inspired by:

  - Reflexion (Shinn et al.) — runtime self-critique.
  - GEPA (gepa-ai/gepa) ICLR 2026 Oral — reflective text evolution.

The generated lesson is intentionally terse (≤ 80 chars) so a candidate can
accumulate many reflections without bloating frontmatter.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import pathlib
import re
from typing import Any

from . import load_config, resolve_vault

log = logging.getLogger(__name__)

REFLECT_PROMPT = """\
You are reading the verdict of an A/B test on a prompt candidate. Output ONE
line, ≤ 80 chars, in the format:
    [<YYYY-MM-DD>] <one-line takeaway>

Example outputs:
    [2026-05-09] preamble killed terse rubric (-0.4)
    [2026-05-12] missing format header dropped score (-0.3)
    [2026-05-13] candidate matches incumbent on rubric, +12 tokens — drop

Verdict facts:
- candidate path: {candidate}
- arm scores (rubric/tokens/banned):
    incumbent: {inc_rubric}/{inc_tokens}/{inc_banned}
    candidate: {can_rubric}/{can_tokens}/{can_banned}
- final verdict: {verdict}

Output ONE line, no prose, no fences:
"""


def _llm_one_liner(payload: dict[str, Any], judge_model: str) -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        log.warning("anthropic SDK missing; reflect is a no-op")
        return ""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.warning("ANTHROPIC_API_KEY missing; reflect is a no-op")
        return ""
    client = Anthropic()
    msg = client.messages.create(
        model=judge_model,
        max_tokens=64,
        temperature=0.0,
        messages=[{"role": "user", "content": REFLECT_PROMPT.format(**payload)}],
    )
    parts = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    line = " ".join("\n".join(parts).split()).strip()
    return line[:80]


def _last_metrics_for_candidate(vault: pathlib.Path, candidate: str) -> dict[str, Any] | None:
    """Find the most-recent `arm: candidate` row in metrics.ndjson whose
    `candidate_path` ends with the supplied basename."""
    needle = pathlib.Path(candidate).name
    p = vault / "90-Meta" / "metrics.ndjson"
    if not p.exists():
        return None
    inc: dict[str, Any] | None = None
    can: dict[str, Any] | None = None
    for line in p.read_text(encoding="utf8", errors="replace").splitlines()[::-1]:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        cp = str(row.get("candidate_path", ""))
        if not cp.endswith(needle):
            continue
        if row.get("arm") == "candidate" and can is None:
            can = row
        elif row.get("arm") == "incumbent" and inc is None:
            inc = row
        if inc and can:
            break
    if not (inc and can):
        return None
    return {"incumbent": inc, "candidate": can}


def _append_reflection(path: pathlib.Path, reflection: str) -> bool:
    """Append `reflection` to the candidate file's frontmatter
    `reflections:` list (creates the list if absent). Returns True if
    the file was modified."""
    text = path.read_text(encoding="utf8", errors="replace")
    if not text.startswith("---"):
        log.warning("%s has no frontmatter; skipping", path)
        return False
    end = text.find("\n---", 3)
    if end < 0:
        return False
    front = text[3:end]
    rest = text[end + 4:]

    if re.search(r"^reflections:\s*\[\s*\]\s*$", front, re.M):
        front = re.sub(
            r"^reflections:\s*\[\s*\]\s*$",
            f'reflections:\n  - "{reflection}"',
            front, count=1, flags=re.M,
        )
    elif re.search(r"^reflections:\s*$", front, re.M):
        front = re.sub(
            r"^(reflections:\s*\n)",
            rf'\1  - "{reflection}"\n',
            front, count=1, flags=re.M,
        )
    else:
        front = front.rstrip() + f'\nreflections:\n  - "{reflection}"\n'

    path.write_text("---" + front + "---" + rest, encoding="utf8")
    return True


def run(
    *,
    candidate: str,
    verdict: str | None,
    judge_model: str | None,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    cfg = load_config(config_path)
    vault = resolve_vault(vault_override, cfg)
    judge = judge_model or cfg.get("harness", {}).get("judge_model", cfg.get("model", "claude-sonnet-4-6"))

    cand_path = pathlib.Path(candidate)
    if not cand_path.is_absolute():
        cand_path = vault / cand_path
    if not cand_path.exists():
        log.error("candidate not found: %s", cand_path)
        return 66

    rows = _last_metrics_for_candidate(vault, candidate)
    if not rows:
        log.error("no A/B metrics found for %s — run `harness ab` first", candidate)
        return 65

    inc, can = rows["incumbent"], rows["candidate"]
    payload = {
        "candidate":  candidate,
        "inc_rubric": inc.get("rubric", "?"), "inc_tokens": inc.get("tokens", "?"), "inc_banned": inc.get("banned", "?"),
        "can_rubric": can.get("rubric", "?"), "can_tokens": can.get("tokens", "?"), "can_banned": can.get("banned", "?"),
        "verdict":    verdict or _heuristic_verdict(inc, can),
    }
    line = _llm_one_liner(payload, judge)
    if not line:
        line = f"[{_dt.date.today().isoformat()}] no judge available; verdict={payload['verdict']}"

    if _append_reflection(cand_path, line):
        log.info("appended reflection to %s: %s", cand_path, line)
        return 0
    return 1


def _heuristic_verdict(inc: dict[str, Any], can: dict[str, Any]) -> str:
    cr, ir = float(can.get("rubric", 0)), float(inc.get("rubric", 0))
    ct, it = int(can.get("tokens", 0)), int(inc.get("tokens", 0))
    cb, ib = int(can.get("banned", 0)), int(inc.get("banned", 0))
    if cr >= ir and (ct <= it or cb < ib):
        return "candidate-wins"
    if ir > cr or (ct > it and cb >= ib):
        return "incumbent-wins"
    return "tie"
