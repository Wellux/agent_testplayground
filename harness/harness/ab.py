"""A/B harness — runs incumbent vs candidate prompts on a promptfoo-shaped fixture."""
from __future__ import annotations

import datetime as _dt
import logging
import os
import pathlib
import time
from typing import Any

from . import append_metric, load_config, resolve_vault
from .judge import score

log = logging.getLogger(__name__)


def _read_text(path: str) -> str:
    return pathlib.Path(path).read_text(encoding="utf8")


def _load_fixture(path: str) -> dict[str, Any]:
    import yaml  # type: ignore[import-untyped]
    with pathlib.Path(path).open() as f:
        return yaml.safe_load(f) or {}


def _render_prompt(template: str, vars_: dict[str, Any]) -> str:
    """Minimal handlebars-style {{var}} substitution. Promptfoo-compatible
    for the simple case; we deliberately don't pull in a templating engine."""
    out = template
    for k, v in vars_.items():
        out = out.replace("{{" + str(k) + "}}", str(v))
    return out


def _call_anthropic(model: str, prompt: str) -> tuple[str, dict[str, int], float]:
    """Returns (text, {input_tokens, output_tokens}, latency_s)."""
    from anthropic import Anthropic
    client = Anthropic()
    started = time.monotonic()
    msg = client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.monotonic() - started
    parts = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    text = "\n".join(parts)
    usage = {
        "input_tokens": getattr(msg.usage, "input_tokens", 0),
        "output_tokens": getattr(msg.usage, "output_tokens", 0),
    }
    return text, usage, elapsed


def run(
    *,
    incumbent: str,
    candidate: str,
    fixture: str,
    judge_model: str | None,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    """Run A/B and write 2 rows to metrics.ndjson. Returns 0 if candidate
    wins, 1 if incumbent wins, 2 on tie / inconclusive."""
    cfg = load_config(config_path)
    vault = resolve_vault(vault_override, cfg)
    model = cfg.get("model", "claude-sonnet-4-6")
    judge = judge_model or cfg.get("harness", {}).get("judge_model", model)

    fx = _load_fixture(fixture)
    tests = fx.get("tests", [{}])
    incumbent_tpl = _read_text(incumbent)
    candidate_tpl = _read_text(candidate)
    fixture_name = pathlib.Path(fixture).stem

    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.error("ANTHROPIC_API_KEY missing; cannot run A/B. Add it to harness/.env")
        return 65

    inc_total = {"tokens": 0, "rubric": 0.0, "banned": 0, "latency": 0.0}
    can_total = {"tokens": 0, "rubric": 0.0, "banned": 0, "latency": 0.0}

    started = _dt.datetime.now(_dt.UTC).isoformat()

    for case in tests:
        vars_ = case.get("vars", {}) or {}
        inc_prompt = _render_prompt(incumbent_tpl, vars_)
        can_prompt = _render_prompt(candidate_tpl, vars_)

        inc_text, inc_usage, inc_lat = _call_anthropic(model, inc_prompt)
        can_text, can_usage, can_lat = _call_anthropic(model, can_prompt)

        inc_score = score(text=inc_text, judge_model=judge, asserts=case.get("assert", []))
        can_score = score(text=can_text, judge_model=judge, asserts=case.get("assert", []))

        inc_total["tokens"] += inc_usage["output_tokens"]
        can_total["tokens"] += can_usage["output_tokens"]
        inc_total["rubric"] += inc_score["rubric"]
        can_total["rubric"] += can_score["rubric"]
        inc_total["banned"] += inc_score["banned"]
        can_total["banned"] += can_score["banned"]
        inc_total["latency"] += inc_lat
        can_total["latency"] += can_lat

    inc_total["rubric"] /= max(1, len(tests))
    can_total["rubric"] /= max(1, len(tests))

    base = {
        "axis": "interaction",
        "fixture": fixture_name,
        "started": started,
        "incumbent_path": incumbent,
        "candidate_path": candidate,
        "model": model,
        "judge_model": judge,
    }
    append_metric(vault, {**base, "arm": "incumbent", **inc_total})
    append_metric(vault, {**base, "arm": "candidate", **can_total})

    rubric_ok = can_total["rubric"] >= inc_total["rubric"]
    tokens_ok = can_total["tokens"] <= inc_total["tokens"]
    banned_ok = can_total["banned"] < inc_total["banned"]

    if rubric_ok and (tokens_ok or banned_ok):
        verdict = "candidate-wins"
        rc = 0
    elif (
        inc_total["rubric"] > can_total["rubric"]
        or (not tokens_ok and not banned_ok)
    ):
        verdict = "incumbent-wins"
        rc = 1
    else:
        verdict = "tie"
        rc = 2

    log.info(
        "A/B %s — incumbent rubric=%.2f tokens=%d banned=%d | candidate rubric=%.2f tokens=%d banned=%d | verdict=%s",
        fixture_name,
        inc_total["rubric"],
        inc_total["tokens"],
        inc_total["banned"],
        can_total["rubric"],
        can_total["tokens"],
        can_total["banned"],
        verdict,
    )
    return rc
