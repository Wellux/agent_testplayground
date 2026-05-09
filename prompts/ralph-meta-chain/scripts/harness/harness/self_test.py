"""Local CI mirror for the autoheal prompt.

Runs the same checks the GitHub workflow runs (privacy guard, bash -n,
py_compile, tsc, plugin build, unit tests) and writes one ndjson row per
check to `90-Meta/heal-checks.ndjson`. The 06-autoheal prompt reads that
file to decide what to fix-or-escalate.

Why a local mirror instead of just calling `gh run view` against the live
PR: the user may run this between commits, on a branch that's never pushed,
or on a machine without `gh`. Local-first matches the rest of the chain.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Callable

from . import load_config, resolve_vault

log = logging.getLogger(__name__)


@dataclass
class CheckResult:
    name: str
    started: str
    duration_s: float
    rc: int
    ok: bool
    detail: str


def _repo_root() -> pathlib.Path:
    """Walk up from this module to find the repo root (looks for .git).

    Pre-Round-8 the harness lived at <repo>/harness/, so parents[2] was
    the repo root. Post-Round-8 it lives at
    <repo>/prompts/ralph-meta-chain/scripts/harness/, so a fixed
    parents[N] would tie self-test to one specific layout. Walk-up makes
    it work in both layouts (and any future migration too).
    """
    p = pathlib.Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    raise RuntimeError("self_test: no .git ancestor found")


# Master-spec target paths, post-Round-8.
# Each helper accepts a `repo` arg (so tests can override) and falls
# through to defaults rooted at repo / <master-spec target>.
HARNESS_RELPATH = "prompts/ralph-meta-chain/scripts/harness"
VOICE_SERVER_RELPATH = "prompts/ralph-meta-chain/voice-server"
PLUGIN_RELPATH = "prompts/ralph-meta-chain/obsidian-plugin"
INSTALL_DIR_RELPATH = "prompts/ralph-meta-chain/install"


def _run(cmd: list[str], cwd: pathlib.Path, timeout: int = 120) -> tuple[int, str, float]:
    started = _dt.datetime.now()
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        elapsed = (_dt.datetime.now() - started).total_seconds()
        out = (proc.stdout + proc.stderr).strip()
        return proc.returncode, out[-2000:], elapsed
    except subprocess.TimeoutExpired:
        return 124, "timeout", float(timeout)
    except FileNotFoundError as e:
        return 127, f"command not found: {e}", 0.0


def _check_privacy(repo: pathlib.Path) -> CheckResult:
    started = _dt.datetime.now()
    needle = "equality\\.power" + "tothepeople"  # split so this file doesn't self-match
    rc, out, elapsed = _run(
        ["git", "grep", "-in", "--", needle, ":!.github/workflows/ci.yml"],
        cwd=repo, timeout=15,
    )
    # `git grep` returns 1 when no match found — that's the success case.
    ok = rc == 1
    detail = "no leaks" if ok else f"matches found: {out}"
    return CheckResult(
        name="privacy", started=started.isoformat(), duration_s=elapsed,
        rc=rc, ok=ok, detail=detail,
    )


def _check_shell(repo: pathlib.Path) -> CheckResult:
    started = _dt.datetime.now()
    rcs = []
    # Master-spec target paths; falls back to legacy scripts/ for
    # pre-Round-8 trees.
    candidates = (
        f"{INSTALL_DIR_RELPATH}/install_cron.sh",
        f"{INSTALL_DIR_RELPATH}/uninstall_cron.sh",
        "scripts/install.sh",          # legacy
        "scripts/uninstall.sh",         # legacy
    )
    for f in candidates:
        if not (repo / f).exists():
            continue
        rc, _, _ = _run(["bash", "-n", f], cwd=repo, timeout=10)
        rcs.append((f, rc))
    elapsed = (_dt.datetime.now() - started).total_seconds()
    bad = [f for f, rc in rcs if rc != 0]
    ok = not bad
    return CheckResult(
        name="shell", started=started.isoformat(), duration_s=elapsed,
        rc=0 if ok else 1, ok=ok,
        detail="OK" if ok else f"failed: {bad}",
    )


def _check_python(repo: pathlib.Path) -> CheckResult:
    started = _dt.datetime.now()
    targets: list[str] = []
    # Master-spec target paths; falls back to legacy roots for
    # pre-Round-8 trees.
    candidates = (
        f"{HARNESS_RELPATH}/harness",
        f"{VOICE_SERVER_RELPATH}/voice_server",
        "harness/harness",                  # legacy
        "voice-server/voice_server",         # legacy
    )
    for sub in candidates:
        d = repo / sub
        if d.exists():
            targets.extend(str(p) for p in d.glob("*.py"))
    if not targets:
        return CheckResult(name="python", started=started.isoformat(),
                           duration_s=0.0, rc=0, ok=True, detail="no python sources")
    rc, out, elapsed = _run(
        [sys.executable, "-m", "py_compile", *targets], cwd=repo, timeout=60,
    )
    return CheckResult(
        name="python", started=started.isoformat(), duration_s=elapsed,
        rc=rc, ok=rc == 0, detail="OK" if rc == 0 else out,
    )


def _check_unit_tests(repo: pathlib.Path) -> CheckResult:
    started = _dt.datetime.now()
    # Master-spec target path first; legacy fallback.
    cwd = repo / HARNESS_RELPATH
    if not cwd.exists():
        cwd = repo / "harness"
    rc, out, elapsed = _run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=cwd, timeout=120,
    )
    return CheckResult(
        name="unit-tests", started=started.isoformat(), duration_s=elapsed,
        rc=rc, ok=rc == 0, detail="OK" if rc == 0 else out[-1000:],
    )


def _check_plugin(repo: pathlib.Path) -> CheckResult:
    started = _dt.datetime.now()
    # Master-spec target plugin first; legacy obsidian-ralph as fallback
    # (it is now archived under migration/_archive/_pre-migrated/ but a
    # pre-Round-8 checkout would still find it here).
    plugin = repo / PLUGIN_RELPATH
    if not plugin.exists():
        plugin = repo / "obsidian-ralph"
    if not (plugin / "node_modules").exists():
        return CheckResult(
            name="plugin", started=started.isoformat(), duration_s=0.0,
            rc=0, ok=True, detail="skipped (no node_modules; run `npm ci` to enable)",
        )
    if not shutil.which("npx"):
        return CheckResult(
            name="plugin", started=started.isoformat(), duration_s=0.0,
            rc=0, ok=True, detail="skipped (no npx on PATH)",
        )
    rc, out, elapsed = _run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"], cwd=plugin, timeout=120,
    )
    return CheckResult(
        name="plugin", started=started.isoformat(), duration_s=elapsed,
        rc=rc, ok=rc == 0, detail="tsc OK" if rc == 0 else out[-1000:],
    )


# Each check is registered as (name, function) so `run(only=...)` can invoke
# only the requested check without running the rest first. Previously
# `_all_checks` ran every check eagerly and then filtered the result list,
# which caused recursion: `_check_unit_tests` re-discovers this module's
# `SelfTest` test class, which calls `run(only="privacy")`, which then ran
# the full set again — looping until cron timeout.
_CHECK_REGISTRY: dict[str, "Callable[[pathlib.Path], CheckResult]"] = {
    "privacy":    _check_privacy,
    "shell":      _check_shell,
    "python":     _check_python,
    "unit-tests": _check_unit_tests,
    "plugin":     _check_plugin,
}

CHECK_NAMES = tuple(_CHECK_REGISTRY)


def _selected_checks(only: str | None, repo: pathlib.Path) -> list[CheckResult]:
    if only is None:
        return [fn(repo) for fn in _CHECK_REGISTRY.values()]
    fn = _CHECK_REGISTRY.get(only)
    if fn is None:
        return []
    return [fn(repo)]


def run(
    *,
    only: str | None,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    cfg = load_config(config_path)
    vault = resolve_vault(vault_override, cfg)
    repo = _repo_root()

    checks = _selected_checks(only, repo)
    if not checks:
        log.error("no check named %r; valid: %s", only, ", ".join(CHECK_NAMES))
        return 64

    out_path = vault / "90-Meta" / "heal-checks.ndjson"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf8") as f:
        for c in checks:
            f.write(json.dumps(asdict(c), separators=(",", ":")) + "\n")

    failed = [c for c in checks if not c.ok]
    if failed:
        for c in failed:
            log.warning("%s FAILED (rc=%d): %s", c.name, c.rc, c.detail.splitlines()[0] if c.detail else "")
    else:
        log.info("all %d check(s) passed", len(checks))
    return 0 if not failed else 1
