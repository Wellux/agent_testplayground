"""harness — Ralph meta-chain CLI."""
from __future__ import annotations

import json
import os
import pathlib
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def _find_repo_root() -> pathlib.Path:
    """Walk up from this module to the repo root (looks for .git).

    Pre-Round-8 the harness lived at <repo>/harness/harness/, so
    parents[2] gave the repo root. Post-Round-8 it lives at
    <repo>/prompts/ralph-meta-chain/scripts/harness/harness/, so a
    fixed parents[N] would tie config-resolution to one specific
    layout. Walk-up makes harness commands work in either."""
    p = pathlib.Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    # Fall back to the legacy parents[2] guess if no .git found
    # (e.g. installed-as-package somewhere with no git history).
    return pathlib.Path(__file__).resolve().parents[2]


def _default_config_path() -> pathlib.Path:
    return _find_repo_root() / "prompts" / "ralph-meta-chain" / "config.yml"


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """Load the ralph config.yml. Falls back to config.example.yml for safety."""
    p = pathlib.Path(config_path) if config_path else _default_config_path()
    if not p.exists():
        ex = p.with_name("config.example.yml")
        if ex.exists():
            p = ex
        else:
            raise FileNotFoundError(f"no config at {p}")
    if yaml is None:
        raise RuntimeError("pyyaml not installed; pip install pyyaml")
    with p.open() as f:
        return yaml.safe_load(f) or {}


def resolve_vault(vault_override: str | None, config: dict[str, Any]) -> pathlib.Path:
    raw = vault_override or os.environ.get("VAULT") or config.get("vault_path")
    if not raw:
        raise RuntimeError("vault path not set (pass --vault, set $VAULT, or fill config.yml)")
    return pathlib.Path(os.path.expanduser(str(raw))).resolve()


def metrics_path(vault: pathlib.Path) -> pathlib.Path:
    p = vault / "90-Meta" / "metrics.ndjson"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def append_metric(vault: pathlib.Path, row: dict[str, Any]) -> None:
    with metrics_path(vault).open("a", encoding="utf8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


__all__ = ["load_config", "resolve_vault", "metrics_path", "append_metric"]
