"""Run a single Ralph axis pass via `claude -p`. Mirrors obsidian-ralph's
runner.ts so behavior is identical across surfaces."""
from __future__ import annotations

import asyncio
import logging
import pathlib
import shlex
from dataclasses import dataclass

from .config import claude_bin, ralph_dir, repo_root

log = logging.getLogger(__name__)

_PROMISE = b"<promise>COMPLETE</promise>"

AXIS_TO_PROMPT: dict[str, str] = {
    "research":    "04-research-ingest.md",
    "memory":      "01-memory-optimizer.md",
    "skills":      "02-skills-optimizer.md",
    "interaction": "03-interaction-optimizer.md",
    "compress":    "05-compress.md",
    "heal":        "06-autoheal.md",
    "evolve":      "07-autoevolve.md",
    "update":      "08-autoupdate.md",
}


@dataclass
class RunResult:
    axis: str
    exit_code: int
    iterations: int
    promise_seen: bool
    tail: str  # last ~4 KB of merged output


async def run_axis(axis: str, *, max_iterations: int = 8, hard_timeout_s: int = 1500) -> RunResult:
    if axis not in AXIS_TO_PROMPT:
        raise ValueError(f"unknown axis: {axis}")
    prompt_file = ralph_dir() / AXIS_TO_PROMPT[axis]
    if not prompt_file.exists():
        raise FileNotFoundError(prompt_file)
    prompt_text = prompt_file.read_text(encoding="utf8")

    cmd = [claude_bin(), "-p", prompt_text]
    log.info("axis=%s starting (max=%d, timeout=%ds): %s",
             axis, max_iterations, hard_timeout_s, shlex.join(cmd[:2]))

    last_rc = 0
    promise = False
    tail_chunks: list[bytes] = []
    iterations = 0

    deadline = asyncio.get_event_loop().time() + hard_timeout_s
    while iterations < max_iterations:
        iterations += 1
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            log.warning("axis=%s timed out at hard cap", axis)
            break

        # Run claude from the repo root. Without an explicit cwd, the
        # subprocess inherits voice-server's launch directory (typically
        # `voice-server/` per the documented launchd plist), and the
        # axis prompts that bootstrap by reading `prompts/ralph-meta-chain/
        # config.yml` and other repo-relative paths break. Mirrors the
        # plugin runner's repoRoot semantics.
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(repo_root()),
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=remaining)
        except asyncio.TimeoutError:
            proc.kill()
            stdout = b""
        last_rc = proc.returncode if proc.returncode is not None else -1
        tail_chunks.append(stdout[-4096:])
        if _PROMISE in stdout:
            promise = True
            break
        if last_rc != 0:
            break  # `until ! ...` semantics

    tail_text = b"".join(tail_chunks)[-4096:].decode("utf8", errors="replace")
    return RunResult(axis=axis, exit_code=last_rc, iterations=iterations,
                     promise_seen=promise, tail=tail_text)


def stop_file_path() -> pathlib.Path:
    from .config import load_ralph_config, vault_path
    cfg = load_ralph_config()
    return vault_path(cfg) / "90-Meta" / "STOP"
