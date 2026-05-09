"""ralph_mcp_server — minimal stdio MCP server exposing the harness CLI.

Implements just enough of the MCP protocol (newline-delimited JSON-RPC 2.0
over stdio) to register four tools with Claude Code:

  - ralph_query              semantic search of the vault
  - ralph_axis_status        last log entry for an axis (or all)
  - ralph_self_test          run the local CI mirror (read-only)
  - ralph_migration_dry_run  preview a vault migration without writing

We deliberately avoid the official `mcp` Python SDK so this server has no
runtime dependency beyond the stdlib. The harness CLI does the real work;
this module is a thin transport adapter.

Spec references:
  - JSON-RPC 2.0:                https://www.jsonrpc.org/specification
  - MCP base protocol:            https://modelcontextprotocol.io/specification
  - MCP stdio transport:          newline-delimited JSON-RPC, no framing.

Read by Claude Code via .mcp.json:
    { "mcpServers": { "ralph": { "command": "python3",
                                  "args": ["-m", "ralph_mcp_server"],
                                  "env": { "PYTHONPATH": "<server_dir>",
                                            "RALPH_REPO": "<repo_root>" } } } }
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import traceback
from typing import Any

PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "ralph"
SERVER_VERSION = "0.1.0"


# ── Tool registry ───────────────────────────────────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "name": "ralph_query",
        "description": (
            "Semantic search the vault via the harness CLI. Returns Markdown "
            "bullets with [[wikilinks]] to relevant notes. Read-only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language search query.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 8, max 50).",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 8,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "ralph_axis_status",
        "description": (
            "Return the most recent 90-Meta/log.md line(s) for one Ralph axis "
            "(research|memory|skills|interaction|compress|heal|evolve|update) "
            "or all axes if `axis` is omitted. Read-only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "axis": {
                    "type": "string",
                    "enum": [
                        "research",
                        "memory",
                        "skills",
                        "interaction",
                        "compress",
                        "heal",
                        "evolve",
                        "update",
                    ],
                    "description": "Single axis to query; omit to get all 8.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "ralph_self_test",
        "description": (
            "Run the local CI mirror (frontmatter, links, privacy, shell, "
            "python). Returns each check + status. Read-only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "only": {
                    "type": "string",
                    "description": (
                        "Optional check name to run alone (e.g. 'privacy', "
                        "'unit-tests', 'plugin'). Omit to run all."
                    ),
                },
            },
            "required": [],
        },
    },
    {
        "name": "ralph_migration_dry_run",
        "description": (
            "Preview the next migration pass without writing anything. "
            "Returns proposed moves + conflict count."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]


# ── Helpers ─────────────────────────────────────────────────────────────────


def _ralph_root() -> str:
    """Return the prompts/ralph-meta-chain directory (best-effort)."""
    repo = os.environ.get("RALPH_REPO")
    if repo:
        cand = os.path.join(repo, "prompts", "ralph-meta-chain")
        if os.path.isdir(cand):
            return cand
    here = os.path.dirname(os.path.abspath(__file__))
    cand = os.path.dirname(here)
    if os.path.isdir(cand):
        return cand
    return here


def _vault_path() -> str | None:
    """Read vault_path from config.yml or config.example.yml."""
    root = _ralph_root()
    for name in ("config.yml", "config.example.yml"):
        p = os.path.join(root, name)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.startswith("vault_path:"):
                    continue
                v = line.split(":", 1)[1].strip().strip('"').strip("'")
                if not v:
                    continue
                if v.startswith("~"):
                    v = os.path.expanduser(v)
                return v
    return None


def _harness_cmd() -> list[str] | None:
    """Find the `harness` CLI (entry point installed via pip) or fall back."""
    if shutil.which("harness"):
        return ["harness"]
    root = _ralph_root()
    pkg = os.path.join(root, "scripts", "harness")
    if os.path.isdir(pkg):
        env_pythonpath = os.path.join(pkg)
        return ["python3", "-c", f"import sys; sys.path.insert(0, {env_pythonpath!r}); from harness.__main__ import main; sys.exit(main())"]
    return None


def _run_subprocess(cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
    try:
        cp = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return cp.returncode, cp.stdout, cp.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return 127, "", str(e)
    except OSError as e:
        return 1, "", str(e)


# ── Tool implementations ────────────────────────────────────────────────────


def tool_ralph_query(args: dict[str, Any]) -> dict[str, Any]:
    query = args.get("query", "").strip()
    limit = int(args.get("limit", 8))
    if not query:
        return _err("query is required and must be non-empty")
    cmd = _harness_cmd()
    if cmd is None:
        return _err("harness CLI not found on PATH and no local checkout")
    # The harness CLI uses `--k` for the result count (not --limit).
    rc, out, err = _run_subprocess(
        cmd + ["query", "--semantic", query, "--k", str(limit)],
        timeout=30,
    )
    if rc != 0:
        return _err(
            f"harness query failed (rc={rc}): {err.strip() or out.strip()}\n"
            "Hint: the local Ollama embedding endpoint may not be reachable."
        )
    return _text(out.strip() or "_(no results)_")


def tool_ralph_axis_status(args: dict[str, Any]) -> dict[str, Any]:
    axis = args.get("axis", "").strip().lower() if args.get("axis") else ""
    vault = _vault_path()
    if not vault:
        return _err("vault_path not configured (config.yml missing)")
    log = os.path.join(vault, "90-Meta", "log.md")
    if not os.path.exists(log):
        return _text("_(no 90-Meta/log.md yet — chain has not run)_")

    axes = (
        [axis]
        if axis
        else [
            "research",
            "memory",
            "skills",
            "interaction",
            "compress",
            "heal",
            "evolve",
            "update",
        ]
    )
    lines = []
    with open(log, encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()
    for ax in axes:
        prefix_inner = f"] {ax} |"
        last = ""
        for line in all_lines:
            if line.startswith("## [") and prefix_inner in line:
                last = line.rstrip("\n")
        lines.append(last or f"## [—] {ax} | (no entries yet)")
    return _text("```\n" + "\n".join(lines) + "\n```")


def tool_ralph_self_test(args: dict[str, Any]) -> dict[str, Any]:
    cmd = _harness_cmd()
    if cmd is None:
        return _err("harness CLI not found on PATH and no local checkout")
    sub = ["self-test"]
    only = args.get("only")
    if only:
        sub += ["--only", str(only)]
    rc, out, err = _run_subprocess(cmd + sub, timeout=180)
    body = (out + err).strip() or "_(no output)_"
    status = "✓ all green" if rc == 0 else f"✗ failed (rc={rc})"
    return _text(f"**{status}**\n\n```\n{body}\n```")


def tool_ralph_migration_dry_run(args: dict[str, Any]) -> dict[str, Any]:
    # Migration is owned by shell scripts under migration/scripts/; the
    # harness CLI doesn't expose a `migration` subcommand. The propose
    # script generates Markdown proposals + conflict reports without
    # moving any file (MEDIUM risk per the script's own header).
    root = _ralph_root()
    propose = os.path.join(root, "migration", "scripts", "ralph_propose_migration.sh")
    if not os.path.exists(propose):
        return _err(f"propose script not found at {propose}")
    rc, out, err = _run_subprocess(["bash", propose], timeout=120)
    body = (out + err).strip() or "_(no output)_"
    suffix = ""
    proposed = os.path.join(root, "migration", "proposed-moves.md")
    conflicts = os.path.join(root, "migration", "conflicts.md")
    if os.path.exists(proposed):
        try:
            with open(proposed, encoding="utf-8", errors="replace") as f:
                lines = [ln for ln in f.readlines() if ln.startswith("- ")]
            suffix += f"\n\n**Proposed moves:** {len(lines)}"
        except OSError:
            pass
    if os.path.exists(conflicts):
        try:
            with open(conflicts, encoding="utf-8", errors="replace") as f:
                lines = [ln for ln in f.readlines() if ln.startswith("- ")]
            if lines:
                suffix += f"\n**Conflicts:** {len(lines)} (apply gate would refuse)"
        except OSError:
            pass
    return _text(f"```\n{body}\n```{suffix}")


TOOL_IMPL = {
    "ralph_query": tool_ralph_query,
    "ralph_axis_status": tool_ralph_axis_status,
    "ralph_self_test": tool_ralph_self_test,
    "ralph_migration_dry_run": tool_ralph_migration_dry_run,
}


# ── JSON-RPC plumbing ───────────────────────────────────────────────────────


def _text(s: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": s}]}


def _err(msg: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"ERROR: {msg}"}], "isError": True}


def _make_response(req_id: Any, result: Any | None = None, error: dict | None = None):
    msg: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    return msg


def _handle_request(req: dict[str, Any]) -> dict[str, Any] | None:
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {}) or {}

    # Notifications (no id) → no response.
    if req_id is None and method.startswith("notifications/"):
        return None

    if method == "initialize":
        return _make_response(
            req_id,
            result={
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "ping":
        return _make_response(req_id, result={})

    if method == "tools/list":
        return _make_response(req_id, result={"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        impl = TOOL_IMPL.get(name)
        if impl is None:
            return _make_response(
                req_id,
                error={"code": -32601, "message": f"unknown tool: {name}"},
            )
        try:
            result = impl(arguments)
        except Exception as e:  # noqa: BLE001 — surface to client
            tb = traceback.format_exc(limit=5)
            return _make_response(
                req_id,
                result=_err(f"{type(e).__name__}: {e}\n\n{tb}"),
            )
        return _make_response(req_id, result=result)

    # Unknown method.
    if req_id is None:
        return None
    return _make_response(
        req_id, error={"code": -32601, "message": f"method not found: {method}"}
    )


def serve() -> None:
    """Read newline-delimited JSON-RPC from stdin; write to stdout."""
    stdin = sys.stdin
    stdout = sys.stdout
    for raw in stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except json.JSONDecodeError as e:
            stdout.write(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"parse error: {e}"},
                    }
                )
                + "\n"
            )
            stdout.flush()
            continue
        resp = _handle_request(req)
        if resp is None:
            continue
        stdout.write(json.dumps(resp) + "\n")
        stdout.flush()


def main() -> int:
    try:
        serve()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
