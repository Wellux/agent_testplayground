"""harness.metrics — skill invocation tracking + roll-up.

The autoevolve axis (07) needs per-skill fitness data to make
data-driven mutation proposals. Each skill / axis subagent should
call `harness metrics record` at the end of its pass; the chain's
roll-up reads `$VAULT/90-Meta/metrics.ndjson` and produces per-skill
aggregates (invocations, success rate, mean tokens, p95 ms,
last_invoked).

Rows are written via `append_metric` (defined in `harness/__init__.py`)
and namespaced by a `kind` field so skill events coexist with the
existing per-axis run rows.

Schema (skill invocation):

    {
      "ts": "2026-05-09T21:30:00Z",
      "kind": "skill_invocation",
      "skill": "ralph-memory",
      "ok": true,
      "tokens": 1234,
      "ms": 4500,
      "axis": "memory"            (optional: which axis the skill is wrapping)
    }

Roll-up (returned by `roll_up()`):

    {
      "ralph-memory": {
        "invocations": 23,
        "successes": 21,
        "failures": 2,
        "success_rate": 0.913,
        "mean_tokens": 1342,
        "median_ms": 2300,
        "p95_ms": 6700,
        "last_invoked": "2026-05-09T22:00:00Z"
      },
      ...
    }
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import pathlib
import statistics
from typing import Any

from . import append_metric, metrics_path

log = logging.getLogger(__name__)

KIND = "skill_invocation"


def record(
    vault: pathlib.Path,
    *,
    skill: str,
    ok: bool,
    tokens: int | None = None,
    ms: int | None = None,
    axis: str | None = None,
    ts: str | None = None,
) -> dict[str, Any]:
    """Append one skill_invocation row to metrics.ndjson.

    Returns the row written (for caller assertion / logging).
    """
    if not skill or not isinstance(skill, str):
        raise ValueError(f"skill must be a non-empty string (got {skill!r})")
    row: dict[str, Any] = {
        "ts": ts or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kind": KIND,
        "skill": skill,
        "ok": bool(ok),
    }
    if tokens is not None:
        row["tokens"] = int(tokens)
    if ms is not None:
        row["ms"] = int(ms)
    if axis is not None:
        row["axis"] = axis
    append_metric(vault, row)
    return row


def _parse_ts(ts: str) -> _dt.datetime:
    """Parse the ISO 8601 'Z'-suffixed timestamps written by record()."""
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return _dt.datetime.fromisoformat(s)


def _quantile(sorted_xs: list[float], q: float) -> float:
    """Inclusive quantile of an already-sorted list. Returns 0.0 if empty.

    We avoid statistics.quantiles() because it requires n>=2 and we want
    a sane behaviour for n==1.
    """
    if not sorted_xs:
        return 0.0
    if len(sorted_xs) == 1:
        return sorted_xs[0]
    pos = q * (len(sorted_xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_xs) - 1)
    frac = pos - lo
    return sorted_xs[lo] * (1 - frac) + sorted_xs[hi] * frac


def roll_up(
    vault: pathlib.Path,
    *,
    window_days: int = 7,
    now: _dt.datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Aggregate skill_invocation rows in the trailing window.

    Reads `vault/90-Meta/metrics.ndjson`. Filters to `kind ==
    skill_invocation` AND `ts >= now - window_days`. Groups by skill;
    computes invocations / successes / failures / success_rate /
    mean_tokens / median_ms / p95_ms / last_invoked.

    Returns an empty dict if the metrics file is absent.
    """
    path = metrics_path(vault)
    if not path.exists():
        return {}

    cutoff: _dt.datetime | None = None
    if window_days > 0:
        ref = now or _dt.datetime.now(_dt.timezone.utc)
        cutoff = ref - _dt.timedelta(days=window_days)

    by_skill: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # tolerate corruption rather than fail roll-up
            if row.get("kind") != KIND:
                continue
            skill = row.get("skill")
            if not skill or not isinstance(skill, str):
                continue
            ts_str = row.get("ts")
            try:
                ts = _parse_ts(ts_str) if ts_str else None
            except ValueError:
                continue
            if cutoff and ts and ts < cutoff:
                continue
            agg = by_skill.setdefault(
                skill,
                {
                    "invocations": 0,
                    "successes": 0,
                    "failures": 0,
                    "_tokens": [],
                    "_ms": [],
                    "_last_ts": None,
                },
            )
            agg["invocations"] += 1
            if row.get("ok"):
                agg["successes"] += 1
            else:
                agg["failures"] += 1
            if isinstance(row.get("tokens"), (int, float)):
                agg["_tokens"].append(float(row["tokens"]))
            if isinstance(row.get("ms"), (int, float)):
                agg["_ms"].append(float(row["ms"]))
            if ts is not None:
                cur = agg["_last_ts"]
                if cur is None or ts > cur:
                    agg["_last_ts"] = ts

    out: dict[str, dict[str, Any]] = {}
    for skill, agg in by_skill.items():
        n = agg["invocations"]
        sorted_ms = sorted(agg["_ms"])
        sorted_tokens = sorted(agg["_tokens"])
        out[skill] = {
            "invocations": n,
            "successes": agg["successes"],
            "failures": agg["failures"],
            "success_rate": (agg["successes"] / n) if n else 0.0,
            "mean_tokens": (statistics.fmean(sorted_tokens)) if sorted_tokens else None,
            "median_ms": (statistics.median(sorted_ms)) if sorted_ms else None,
            "p95_ms": _quantile(sorted_ms, 0.95) if sorted_ms else None,
            "last_invoked": (
                agg["_last_ts"].strftime("%Y-%m-%dT%H:%M:%SZ")
                if agg["_last_ts"]
                else None
            ),
        }
    return out


def render_markdown(rollup: dict[str, dict[str, Any]]) -> str:
    """Pretty-print a roll-up dict as a Markdown table sorted by invocations desc."""
    if not rollup:
        return "_(no skill invocations recorded yet)_"
    rows = sorted(rollup.items(), key=lambda kv: kv[1]["invocations"], reverse=True)
    lines = [
        "| skill | invocations | success rate | mean tokens | p95 ms | last invoked |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for skill, m in rows:
        success_rate = f"{m['success_rate']:.0%}" if m["invocations"] else "—"
        mean_tokens = f"{int(m['mean_tokens'])}" if m["mean_tokens"] is not None else "—"
        p95_ms = f"{int(m['p95_ms'])}" if m["p95_ms"] is not None else "—"
        last = m["last_invoked"] or "—"
        lines.append(
            f"| `{skill}` | {m['invocations']} | {success_rate} | {mean_tokens} | {p95_ms} | {last} |"
        )
    return "\n".join(lines)


def render_json(rollup: dict[str, dict[str, Any]]) -> str:
    """Render a roll-up dict as JSON for programmatic consumption (autoevolve)."""
    return json.dumps(rollup, indent=2, sort_keys=True)


__all__ = ["record", "roll_up", "render_markdown", "render_json", "KIND"]
