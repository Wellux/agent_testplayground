# hooks/ — Claude Code lifecycle hook examples

Per `docs/CLAUDE_CODE_INTEGRATION.md` § Hooks. These are **examples
only**, not auto-installed. Hook installation is HIGH-risk per
`docs/APPROVAL_GATES.md`.

## Files in this folder

| File                  | Purpose                                                           |
| --------------------- | ----------------------------------------------------------------- |
| `README.md`           | this file                                                         |
| `hooks.example.json`  | example settings.json hooks block (paste into ~/.claude/settings.json) |
| `pre-tool-use.sh`     | guard against forbidden Bash patterns                              |
| `post-tool-use.sh`    | append a Karpathy log line per tool call                           |
| `session-end.sh`      | propose a session-capture for the morning memory pass               |
| `notification.sh`     | placeholder routing for desktop notifications                       |

## Install (manual; HIGH risk)

```bash
# 1. Review every hook script.
$EDITOR prompts/ralph-meta-chain/hooks/*.sh

# 2. Copy them somewhere stable (NOT a checkout the user might delete).
mkdir -p ~/.claude/hooks
cp prompts/ralph-meta-chain/hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh

# 3. Merge prompts/ralph-meta-chain/hooks/hooks.example.json into your
#    ~/.claude/settings.json. Restart Claude Code.

# 4. Smoke-test: open a session, run `Bash(echo hi)`. Check
#    $VAULT/90-Meta/log.md for a `pre-tool-use` line.
```

## Fail-safe contract

Per `providers/claude-code/hooks.md`:

1. Hooks exit non-zero ONLY for the hook's OWN failure — never to
   block Claude Code (the hook is observability, not policy).
2. Each hook has a hard timeout (10 s default).
3. No hook depends on network reachability.
4. Diagnostics append to `90-Meta/heal-checks.ndjson` so the autoheal
   pass picks up persistent failures.

## Risk classes

| Hook event       | Risk | Default behavior |
| ---------------- | ---- | ---------------- |
| pre-tool-use     | LOW  | log only         |
| post-tool-use    | LOW  | log only         |
| session-end      | MEDIUM | propose memory capture |
| notification     | MEDIUM | placeholder route |

## Cross-references

- `providers/claude-code/hooks.md` — the canonical contract.
- `docs/CLAUDE_CODE_INTEGRATION.md` § Hooks.
- `docs/APPROVAL_GATES.md` § Cron / system — hook install is HIGH.
