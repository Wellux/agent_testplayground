"""Config loader — reads the same prompts/ralph-meta-chain/config.yml the
prompts read, plus voice-server-specific env vars."""
from __future__ import annotations

import os
import pathlib
from typing import Any


def repo_root() -> pathlib.Path:
    """Walk up from this file to the repo root (looks for .git).

    Pre-Round-8 voice-server lived at <repo>/voice-server/, so parents[2]
    was the repo root. Post-Round-8 it lives at
    <repo>/prompts/ralph-meta-chain/voice-server/, so a fixed parents[N]
    would tie the server to one specific layout. Walk-up makes it work
    in either."""
    p = pathlib.Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    raise RuntimeError("voice-server: no .git ancestor found")


def load_ralph_config() -> dict[str, Any]:
    cfg_path = pathlib.Path(
        os.environ.get("RALPH_CONFIG")
        or repo_root() / "prompts" / "ralph-meta-chain" / "config.yml"
    )
    if not cfg_path.exists():
        # Fall back to example so the server still boots in CI / first install.
        cfg_path = repo_root() / "prompts" / "ralph-meta-chain" / "config.example.yml"
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("pyyaml not installed") from e
    with cfg_path.open() as f:
        return yaml.safe_load(f) or {}


def vault_path(cfg: dict[str, Any]) -> pathlib.Path:
    raw = os.environ.get("VAULT") or cfg.get("vault_path")
    if not raw:
        raise RuntimeError("vault path not set (env $VAULT or config.yml vault_path)")
    return pathlib.Path(os.path.expanduser(str(raw))).resolve()


def claude_bin() -> str:
    return os.environ.get("RALPH_CLAUDE_BIN", "claude")


def ralph_dir() -> pathlib.Path:
    return repo_root() / "prompts" / "ralph-meta-chain"


def trusted_subnets() -> list[str]:
    """CIDR subnets allowed to reach this server. Default: Tailscale + loopback."""
    raw = os.environ.get("RALPH_TRUSTED_SUBNETS", "100.64.0.0/10,127.0.0.0/8,::1/128")
    return [s.strip() for s in raw.split(",") if s.strip()]
