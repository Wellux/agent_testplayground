# CHANGELOG

All notable phases of the Ralph meta-chain shipped on branch
`claude/ralph-obsidian-cron-jobs-Mb4A9` toward [PR #1](https://github.com/Wellux/agent_testplayground/pull/1).

## Phase 6 — local CI mirror + day-1 sample inbox + Obsidian self-test command

- `harness self-test` — local CI mirror (privacy / shell / py_compile /
  unit-tests / plugin-tsc). Writes one ndjson row per check to
  `90-Meta/heal-checks.ndjson` so the autoheal prompt has structured input.
- `06-autoheal.md` updated to call `harness self-test` first; gh-CLI path
  is now the secondary fallback (was primary).
- `prompts/ralph-meta-chain/seed/00-Inbox/sample-capture.md` and
  `seed/10-Daily/2026-05-09.md` so the chain has something to ingest on
  the very first cron firing.
- Obsidian plugin gains a `Ralph: Run self-test` command.
- CHANGELOG.md (this file).

## Phase 5 — day-1 seed vault + Reflexion code loop + traces viewer

- `prompts/ralph-meta-chain/seed/` — first-day vault: schema (`CLAUDE.md`),
  starter skills (`recall`, `pr-from-branch` with Voyager prerequisites),
  starter prompts (`code-review`, `daily-summary` matching shipped fixtures),
  and bootstrap `user-profile.md`.
- `scripts/install.sh seed_vault()` — `cp -n` the seed tree into `$VAULT/`
  on first install (never overwrites).
- `harness reflect` — closes the Reflexion lesson loop in code: reads the
  most recent A/B pair from `metrics.ndjson`, asks the judge for one
  ≤80-char takeaway, and appends to the candidate's `reflections:`.
- `harness traces` — `--tail N [--axis X]` summarizes `metrics.ndjson`.
- 30 unit tests (21 harness + 9 voice-server).

## Phase 4 — 2026 agent-memory + self-evolving research

- `harness/harness/memory_backends.py` — pluggable selector with
  `local-sqlite-vec` (default), `cognee` (local-first graph), `letta`
  (OS-style tiered) opt-ins. Cited rationale: 2026 LongMemEval surveys
  (Zep 63.8% vs Mem0 49.0%); Atlan / vectorize.io / n1n.ai comparisons.
- Prompt 02 (skills): GEPA × MAP-Elites bins + Voyager skill curriculum.
- Prompt 07 (autoevolve): Reflexion lesson-loop; ADAS / OpenEvolve /
  EvoAgentX / OpenAI Cookbook citations.
- Prompt 08 (autoupdate): Cursor 3, Aider, Cline, Roo, Continue, Goose,
  Cognee, Letta, Mem0, Zep, GEPA, OpenEvolve, EvoAgentX, DSPy added.
  `harness ingest --creators @h1,@h2` resolves YouTube `@handle →
  channelId` and reads the per-channel RSS.

## Phase 3 — autoheal / autoevolve / autoupdate + voice-server

- New prompts `06-autoheal.md` (every 6h, Nate Herk supervisor pattern),
  `07-autoevolve.md` (weekly Sunday, Alex Finn ruthless iteration),
  `08-autoupdate.md` (weekly Monday, Matt Wolfe FutureTools weekly scan).
- `voice-server/` — FastAPI app for the Mac mini: `/ralph/voice` (Whisper
  local), `/ralph/run`, `/ralph/{stop,resume}`, `/ralph/status`,
  `/healthz`. Tailscale-aware origin guard.
- Apple Shortcuts JSON specs (iPhone/iPad/Watch/AirPods), Alexa Lambda +
  skill.json, Raycast extension stub.

## Phase 2 — cron installer + Obsidian plugin + Python harness + prompts 04/05

- `scripts/install.sh` / `uninstall.sh` — Linux cron + macOS launchd,
  idempotent, `--dry-run`, tagged `# RALPH-managed:` lines.
- `obsidian-ralph/` — TypeScript plugin (esbuild). Commands, status bar,
  log + metrics side-pane views.
- `harness/` — Python CLI (uv): `ab`, `embed`, `query`, `ingest`,
  `compress`. Storage = sqlite-vec + FTS5 (obra/knowledge-graph schema).
- New prompts `04-research-ingest.md`, `05-compress.md`.
- CHANGELOG retroactively notes this is when the system became "real".

## Phase 1 — three Ralph prompts + cron example

- `prompts/ralph-meta-chain/{01-memory,02-skills,03-interaction}.md`,
  `config.example.yml`, `crontab.example`, `README.md`.

## CI

A single `.github/workflows/ci.yml` runs four jobs on every PR + push:
privacy guard, shell, harness Python (py_compile + `unittest`),
voice-server Python (py_compile + `unittest`), obsidian-ralph TypeScript
(`tsc --noEmit` + esbuild build).
