# ARCHITECTURE.md

## Purpose

System overview for Ralph Meta Chain. Explains the component map, data
flow, and where each piece of the master spec lands today (Phase 1-6
reference implementation) vs. tomorrow (master-spec greenfield).

## Component map

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Cron / launchd (host)                          │
│   research → memory → skills → interaction (daily)                       │
│   compress (hourly)                                                      │
│   heal (every 6h) · evolve (Sun) · update (Mon)                          │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        Ralph prompts (8 axes)                             │
│   prompts/ralph-meta-chain/0[1-8]-*.md                                    │
│   each: same prompt, mutating workspace, <promise>COMPLETE</promise>      │
└─────────────┬───────────────────────────────────────┬────────────────────┘
              ▼                                       ▼
   ┌──────────────────────┐                ┌─────────────────────────┐
   │   Obsidian vault      │                │   harness (Python CLI)  │
   │   $VAULT/             │                │   ab / embed / query /  │
   │   00-Inbox/           │◄──── reads ────│   ingest / compress /   │
   │   10-Daily/           │                │   reflect / traces /    │
   │   20-MOCs/            │                │   self-test             │
   │   30-Notes/           │── writes ─────►│                         │
   │   40-Skills/          │                └─────────────┬───────────┘
   │   50-Prompts/         │                              │
   │   60-Interactions/    │                              ▼
   │   90-Meta/            │                ┌─────────────────────────┐
   │     index.md          │                │  Local services         │
   │     log.md            │                │  - Ollama (embeddings)  │
   │     ralph-state.json  │                │  - Anthropic SDK        │
   │     metrics.ndjson    │                │  - sqlite-vec + FTS5    │
   │     embeddings.db     │                └─────────────────────────┘
   │     heal-checks.ndjson│
   │     STOP              │
   └──────┬───────────────┘
          ▼
   ┌──────────────────────┐                ┌─────────────────────────┐
   │ obsidian-ralph        │                │  voice-server (FastAPI) │
   │ (TypeScript plugin)   │                │  on Mac mini            │
   │ command palette       │                │  /ralph/voice (Whisper) │
   │ status bar            │                │  /ralph/run             │
   │ log + metrics views   │                │  /ralph/{stop,resume}   │
   └───────────────────────┘                │  /ralph/status          │
                                            │  /healthz               │
                                            └────────────┬────────────┘
                                                         ▼
                              ┌─────────────────────────────────────┐
                              │  Multi-device entry points (Phase 3)│
                              │  iOS Shortcut · Watch · Alexa skill │
                              │  Raycast extension                  │
                              └─────────────────────────────────────┘
```

## Data flow

1. **Capture.** Voice/text from any device → POST `/ralph/voice` →
   `00-Inbox/voice-<UTC>.md`. Manual capture also lands in `00-Inbox/`.
2. **Ingest (01:00 UTC research).** `harness ingest` pulls GitHub trending
   + creator RSS → `00-Inbox/trending-YYYY-MM-DD.md` and
   `00-Inbox/creators-YYYY-MM-DD.md`.
3. **Promote (02:00 UTC memory).** Prompt #1 reads inbox, writes atomic
   notes to `30-Notes/<id>-<slug>.md`, updates MOCs, embeds via
   `harness embed`, archives originals to `00-Inbox/_processed/`.
4. **Mine skills (03:00 UTC skills).** Prompt #2 detects repeated action
   patterns from daily notes; drafts new `40-Skills/<slug>.md`; runs
   GEPA × MAP-Elites population A/B against canonical fixtures via
   `harness ab`.
5. **Tune interaction (04:00 UTC interaction).** Prompt #3 distills tone
   prefs into `60-Interactions/user-profile.md`; A/B-tests prompt
   rewrites in `50-Prompts/`; appends Reflexion lessons via
   `harness reflect`.
6. **Compress (every hour at :30).** Prompt #5 finds bloated notes
   (> token threshold), summarizes via `harness compress`, archives
   originals.
7. **Heal (every 6 hours).** Prompt #6 runs `harness self-test`, reads
   `heal-checks.ndjson`, fixes safe drift or escalates to
   `60-Interactions/escalations.md`.
8. **Evolve (Sun 05:00 UTC).** Prompt #7 reads `metrics.ndjson` for the
   trailing week, deprecates skills with success_rate < 0.6, opens
   rewrite proposals.
9. **Update (Mon 06:00 UTC).** Prompt #8 scans release feeds + creator
   RSS, opens dependency-bump proposals.

## Provider architecture

- **Active runtime:** Claude Code (`claude -p ...`). Cited everywhere.
- **Adapter specs (deferred):** Codex, Gemini AI Studio, local Ollama
  models. Documented in `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` and
  `providers/*` (Round 4).

## Failure modes

| Failure                                      | Detection                                      | Recovery                              |
| -------------------------------------------- | ---------------------------------------------- | ------------------------------------- |
| Ollama down                                  | `harness embed` exits non-zero                  | Memory pass continues; tag `#unrecalled` |
| Anthropic 5xx                                | harness ab returns rc=2 + log line              | Skip A/B for that fixture this pass    |
| sqlite-vec not loadable                      | `_connect()` warns; FTS5 still works            | Hybrid retrieval falls back to BM25    |
| Vault path missing                           | install.sh refuses to install cron              | User creates dir, retries              |
| Cron drift (entries removed)                 | autoheal detects no `# RALPH-managed:` lines    | Escalate; user reruns install.sh       |
| voice-server unreachable                      | iOS Shortcut shows error                        | Capture falls back to manual          |
| STOP file present                            | every prompt checks; emits COMPLETE immediately | User removes STOP                     |
| Loop never terminates                         | `until !` outer counter caps at max_iterations  | Hard `timeout` outer cap              |

## Rollback approach

- **Code changes (prompts / harness / plugin):** git revert + push.
- **Vault changes (memory):** every mutation appends; archives originals;
  `git -C $VAULT log` shows everything if vault is git-tracked.
- **Cron entries:** `scripts/uninstall.sh` removes only `# RALPH-managed:`
  lines; backup at `~/.ralph-crontab.bak.<UTC-ts>`.
- **Plugin:** unload + remove plist (macOS) / remove plugin folder
  (vault).

## Safety notes

- The architecture assumes **local-first**. Network calls happen only at
  embedding time (Ollama on localhost) and at A/B time (Anthropic API);
  no other endpoints by default.
- **Always-on attack surface:** the voice-server. Tailscale-only origin
  guard; `/healthz` is the only unauth'd endpoint.
- The chain **never deletes**; it only archives. Restoring an archived
  note is `mv` from `_archive/` back.

## Cross-references

- Master prompt: see top-level conversation.
- `MEMORY_MODEL.md` — what each memory layer contains.
- `CONTEXT_LIFECYCLE.md` — observe → diagnose → … → audit → learn loop.
- `CRON_JOBS.md` — schedule + install/uninstall.
- `CLAUDE_CODE_INTEGRATION.md` — CLAUDE.md, hooks, skills.
- Phase 1-6 reference implementation:
  - `harness/` — Python CLI.
  - `voice-server/` — FastAPI app.
  - `obsidian-ralph/` — TypeScript plugin.
  - `scripts/install.sh`, `scripts/launchd/`.

## Next actions

After reading this, start with `MEMORY_MODEL.md` to understand the
frontmatter taxonomy, then `CRON_JOBS.md` to install Ralph on your
machine.
