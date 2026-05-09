# mcp-server/ — `ralph` MCP server for Claude Code

A minimal stdio MCP server that exposes the harness CLI to Claude Code
as four tools. **Zero runtime dependencies beyond the Python standard
library** — the heavy lifting stays in `scripts/harness/`.

## Tools exposed

| MCP tool                    | Wraps                                                          | Mutates working tree? |
| --------------------------- | -------------------------------------------------------------- | --------------------- |
| `ralph_query`               | `harness query --semantic <q> --k <n>`                          | no                    |
| `ralph_axis_status`          | reads `$VAULT/90-Meta/log.md`                                   | no                    |
| `ralph_self_test`            | `harness self-test --no-log`                                    | no (the cron-default mode appends to `heal-checks.ndjson`; the MCP tool suppresses it) |
| `ralph_migration_dry_run`    | `migration/scripts/ralph_propose_migration.sh`                  | **yes (proposals only)** |

`ralph_migration_dry_run` writes Markdown proposals (`proposed-moves.md`,
`rollback-plan.md`, `conflicts.md`, audit line in `migration-log.md`)
but **never moves files**. The proposals are the artefact; the apply
gate (separate, explicit) is the only thing that runs `git mv`. Revert
proposals with `git restore prompts/ralph-meta-chain/migration/`. The
tool's `description` field surfaces this contract to the LLM client.

The other three tools are strictly read-only. Mutating commands stay
behind explicit slash commands or subagents that the user can review.

## How it talks

Newline-delimited JSON-RPC 2.0 over stdin/stdout. Implements:

- `initialize` (protocol version `2025-03-26`)
- `ping`
- `tools/list`
- `tools/call`

## How Claude Code finds it

Registered in `.mcp.json` by the installer:

```json
{
  "mcpServers": {
    "ralph": {
      "command": "python3",
      "args": ["-m", "ralph_mcp_server"],
      "env": {
        "PYTHONPATH": "<absolute path to prompts/ralph-meta-chain/mcp-server>",
        "RALPH_REPO": "<absolute path to repo root>"
      }
    }
  }
}
```

The installer (`install/install_claude_code.sh --with-mcp`) writes the
above for you with absolute paths resolved.

## Manual smoke test

```bash
# Send an initialize handshake then list tools.
python3 -m ralph_mcp_server <<'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"smoke","version":"0.0.1"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
EOF
```

You should see two JSON-RPC responses: the initialize result and the
tool catalog.

## Why no dependency on the official `mcp` SDK

- Keeps the server zero-dep (vendored stdlib only).
- The MCP stdio transport is small enough to implement directly.
- Avoids version drift with the official SDK during early MCP
  protocol churn.

If/when the protocol stabilizes and a feature in the SDK becomes load-
bearing, swap this module for a subclass of `mcp.server.Server` and
update `pyproject.toml`.

## Cross-references

- `install/install_claude_code.sh` — registers this server.
- `scripts/harness/harness/__main__.py` — the underlying CLI.
- `tests/test_mcp_server.py` — round-trip + protocol smoke tests.
