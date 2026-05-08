# Ralph Meta-Chain — Obsidian Second-Brain Cron Loop

A "Ralph" loop is the agentic pattern of running the *same* prompt repeatedly
until the work is done. A **meta-chain** points that loop at the agent itself:
each pass mines the day's traces, distills lessons into the Obsidian vault,
and rewrites the prompts/skills/playbooks the next run will execute.

Three drafts live in this folder. Run them once a day, in order, against the
same vault.

| Order | Cron (UTC)  | Prompt                          | Optimizes                               |
| ----- | ----------- | ------------------------------- | --------------------------------------- |
| 1     | `0 2 * * *` | `01-memory-optimizer.md`        | Long-term memory / notes / MOCs         |
| 2     | `0 3 * * *` | `02-skills-optimizer.md`        | Reusable skills, snippets, playbooks    |
| 3     | `0 4 * * *` | `03-interaction-optimizer.md`   | Tone, prompt patterns, user preferences |

The order matters: skills are derived from settled memory, and interaction
heuristics are derived from skills + memory. Run #1 → #2 → #3.

## Vault layout the prompts assume

```
$VAULT/
  00-Inbox/                  # raw captures (chat exports, journal, web clips)
  10-Daily/YYYY-MM-DD.md     # daily note (Ralph appends a session log here)
  20-MOCs/                   # Maps-of-Content per domain
  30-Notes/                  # atomic / evergreen notes
  40-Skills/                 # reusable skills + playbooks (one .md per skill)
  50-Prompts/                # prompt library, including this chain's outputs
  60-Interactions/           # per-thread distillations, user prefs, tone notes
  90-Meta/
    ralph-log.md             # append-only run log
    ralph-state.json         # last-run pointers, hashes, open follow-ups
```

If a folder is missing, the prompt creates it on first run.

## Wiring as cron

`crontab.example` shows a minimal setup using the Claude CLI. Each entry pipes
the prompt file into a non-interactive Claude run with the vault path exported
as `$VAULT`. Adjust the binary, model, and working directory for your setup.

## Ralph guarantees baked into every prompt

1. **Idempotent.** Re-running the same day is a no-op (the prompt diffs against
   `90-Meta/ralph-state.json` before writing).
2. **Append-only by default.** Edits to existing notes preserve prior content
   and add a dated `## Ralph YYYY-MM-DD` section.
3. **Bounded.** Each pass writes ≤ N notes (configurable per prompt) so the
   vault doesn't drown.
4. **Auditable.** Every run appends a one-line summary to `90-Meta/ralph-log.md`.
5. **Self-healing.** If a prompt detects drift between vault and state, it
   reconciles before doing new work.
