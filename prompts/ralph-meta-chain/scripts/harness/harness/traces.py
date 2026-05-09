"""traces — tail / group / filter metrics.ndjson and log.md for quick review.

Inspired by the OpenAI Cookbook Self-Evolving Agents recipe (collect-traces
→ score → select → retrain): the first step is just being able to LOOK at
the traces. This subcommand is the "look" step.
"""
from __future__ import annotations

import json
import logging
import pathlib
from collections import Counter
from typing import Any

from . import load_config, resolve_vault

log = logging.getLogger(__name__)


def _read_ndjson(p: pathlib.Path, *, tail: int) -> list[dict[str, Any]]:
    if not p.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in p.read_text(encoding="utf8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-tail:]


def run(
    *,
    tail: int,
    axis: str | None,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    cfg = load_config(config_path)
    vault = resolve_vault(vault_override, cfg)

    metrics = _read_ndjson(vault / "90-Meta" / "metrics.ndjson", tail=tail)
    if axis:
        metrics = [r for r in metrics if r.get("axis") == axis]

    if not metrics:
        print("(no rows)")
        return 1

    by_axis = Counter(r.get("axis", "?") for r in metrics)
    print(f"# metrics.ndjson — last {len(metrics)} rows")
    print()
    print("## by axis")
    for ax, n in by_axis.most_common():
        print(f"- {ax}: {n}")

    if axis == "interaction":
        print()
        print("## A/B verdicts (last 20)")
        pairs: dict[tuple[str, str], dict[str, Any]] = {}
        for r in metrics:
            key = (str(r.get("fixture", "?")), str(r.get("started", "?")))
            pairs.setdefault(key, {})[str(r.get("arm", "?"))] = r
        for (fix, started), arms in list(pairs.items())[-20:]:
            inc, can = arms.get("incumbent", {}), arms.get("candidate", {})
            print(
                f"- [{started[:16]}] {fix}: "
                f"inc rubric={inc.get('rubric', '?')} tok={inc.get('tokens', '?')} | "
                f"can rubric={can.get('rubric', '?')} tok={can.get('tokens', '?')}"
            )
    elif axis in {"compress", "research"}:
        print()
        print(f"## last {min(20, len(metrics))} {axis} rows")
        for r in metrics[-20:]:
            print(f"- {json.dumps(r, separators=(',', ':'))}")
    else:
        print()
        print("## last 20 rows")
        for r in metrics[-20:]:
            print(f"- axis={r.get('axis', '?')} verdict={r.get('verdict', '-')} {json.dumps({k: v for k, v in r.items() if k not in {'axis', 'verdict'}})}")

    return 0
