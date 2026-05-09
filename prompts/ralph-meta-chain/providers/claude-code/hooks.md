---
ralph_type: provider
provider: claude-code
created: 2026-05-09
status: scaffold
summary: "Claude Code hooks surface — examples + safety contract."
---

# Claude Code Hooks

Hooks are how Ralph integrates with Claude Code's session lifecycle
without touching the agent's prompt. Round 5+ ships actual hook
scripts under `prompts/ralph-meta-chain/hooks/`; this file documents
what they'll do.

## Hook events

| Event           | When it fires                              | Risk class | Default behavior |
| --------------- | ------------------------------------------ | ---------- | ---------------- |
| pre-tool-use    | before any tool call                       | LOW        | log to `90-Meta/log.md` |
| post-tool-use   | after every tool call                      | LOW        | log + heal-check counter |
| session-end     | when a session terminates normally          | MEDIUM     | propose memory capture for the session |
| notification    | error / important event                    | MEDIUM     | route to user (Notice / desktop notif) |

## Fail-safe contract

Every hook script MUST:

1. Exit non-zero ONLY for the hook's own failure (never to block
   Claude Code).
2. Have a hard timeout (10 s default).
3. Never depend on network reachability (Anthropic API call may
   already be in flight).
4. Append diagnostics to `90-Meta/heal-checks.ndjson` so the autoheal
   pass picks up persistent failures.

## pre-tool-use example sketch (Round 5+)

```bash
#!/usr/bin/env bash
# .claude/hooks/pre-tool-use.sh
# Emitted before any tool call. Receives JSON on stdin.

set -euo pipefail
input="$(cat)"
tool="$(jq -r .tool_name <<<"$input")"
args="$(jq -r '.tool_input | tostring' <<<"$input")"

echo "## [$(date -u +%Y-%m-%dT%H:%M:%SZ)] pre-tool-use | tool=$tool" \
  >> "${VAULT}/90-Meta/log.md"

# Refuse forbidden Bash patterns regardless of allowlist.
if [[ "$tool" == "Bash" && "$args" == *"rm -rf /"* ]]; then
  jq -n '{decision:"block", reason:"forbidden Bash pattern"}'
  exit 0
fi

# Default: allow.
jq -n '{decision:"allow"}'
```

## post-tool-use example sketch

```bash
#!/usr/bin/env bash
# .claude/hooks/post-tool-use.sh

set -euo pipefail
input="$(cat)"
tool="$(jq -r .tool_name <<<"$input")"
duration="$(jq -r '.duration_ms // 0' <<<"$input")"

echo "## [$(date -u +%Y-%m-%dT%H:%M:%SZ)] post-tool-use | tool=$tool ms=$duration" \
  >> "${VAULT}/90-Meta/log.md"
```

## session-end example sketch

```bash
#!/usr/bin/env bash
# .claude/hooks/session-end.sh
# Append a session capture to the inbox so the morning memory pass
# can ingest the session's notable signals.

set -euo pipefail
ts="$(date -u +%Y%m%dT%H%M%SZ)"
out="${VAULT}/00-Inbox/session-${ts}.md"

cat > "$out" <<EOF
---
id: session-${ts}
type: session-capture
created: $(date -u +%Y-%m-%d)
---

(session-end hook — Ralph will distill notable signals here at next
memory pass)
EOF
```

## Installation gate

Per `docs/APPROVAL_GATES.md`, installing Claude Code hooks is
HIGH-risk (system-wide impact on every Claude Code session). Default:
hooks NOT installed. The Round 5+ install script is opt-in.

## Cross-references

- Anthropic ralph-wiggum plugin's Stop hook is the canonical example
  Ralph builds on.
- `docs/CLAUDE_CODE_INTEGRATION.md` § Hooks.
- `docs/APPROVAL_GATES.md` § Cron / system.

## Next actions

- Round 5+ ships these as actual `.sh` files under
  `prompts/ralph-meta-chain/hooks/`.
- Until then, this file is reference only.
