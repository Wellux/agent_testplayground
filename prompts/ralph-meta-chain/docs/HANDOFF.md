# Handoff document — Ralph meta-chain

**For:** the next maintainer (you)
**From:** the previous maintainer (this session, 2026-05-09)
**Branch:** `claude/ralph-obsidian-cron-jobs-Mb4A9` → PR #2 (open, draft = false)

This document is the single source of truth for taking over. Read it
top-to-bottom; everything else is referenced.

---

## TL;DR

The chain is **shipped** through Round 10.1. CI is green on the latest
commit. PR #2 is open and ready-for-review. Three install targets
work: `cron`, `claude-code`, `codex`. The next-best-thing on the
backlog is wiring skill metrics so the autoevolve axis has real data
to optimize against.

If you do nothing else, do these in order:

1. Read [`PRD.md`](PRD.md) (15 min) — understand the goals + non-goals
2. Run [`QUICKSTART_CLAUDE_CODE.md`](QUICKSTART_CLAUDE_CODE.md) (10 min) — feel the surface
3. Read this doc fully (20 min)
4. Look at the **Backlog** section below — pick one item, ship it

---

## Current state (as of 2026-05-09)

### What works end-to-end

| Surface | Status | Verified by |
| --- | --- | --- |
| 8 cron axes | shipped; install_cron.sh wires them | manual + bats |
| 11 slash commands (Claude Code) | shipped, all read-only LOW-risk | bats stubs |
| 8 axis subagents (Claude Code) | shipped, descriptions hand-tuned | manual |
| 8 specialist topic skills | shipped (Round 6 deliverable) | structural test in `test_round6.py` |
| 5 lifecycle hooks (Claude Code) | shipped, fail-safe contract honoured | bats |
| 16 skills + 11 prompts (Codex) | shipped via install_codex.sh | bats `test_install_codex.bats` (21 cases) |
| MCP server | 4 tools, JSON-RPC over stdio, zero deps | `test_mcp_server.py` (14 cases) |
| Unified install dispatcher | `install.sh --target {cron,claude-code,codex,all}` | `test_install_dispatcher.bats` (12 cases) |
| Privacy guard | CI grep against user-identifier canary | CI privacy job |
| 4 read-only validators | provider conformance, business ledger, frontmatter, links | CI validators job |
| Round 8 migration apply | done (Phase 1-6 retired) | green CI on every commit since |

### What's stubbed but not wired

| Item | Where | What's missing |
| --- | --- | --- |
| Skill metrics (`invocations`, `success_rate`, `mean_tokens`) | `40-Skills/<slug>.md` frontmatter | No code path populates these. Autoevolve has nothing to optimize against. |
| Per-folder compress thresholds | `config.example.yml` | Single global `compress.token_threshold` only. Should be per-folder map. |
| Skip-when-empty prechecks | `scripts/ralph_context_compress.sh`, `scripts/ralph_research_digest.sh` | Cron firings always run the chain prompt even when there's no work. |
| Slash-command `--why` flags | `commands/ralph-*.md` | Output rendering exists; "explain how each line was computed" doesn't. |
| Voice-server multi-device runtime | `voice-server/`, `docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md` | Gated; not on the roadmap for next round. |

### Test counts (last commit `de028ac`)

| Suite | Cases | File |
| --- | --- | --- |
| Harness unit | 104 + 16 (B1 metrics) | `prompts/ralph-meta-chain/scripts/harness/tests/` |
| Voice-server unit | 12 | `prompts/ralph-meta-chain/voice-server/tests/` |
| MCP server protocol | 14 | `prompts/ralph-meta-chain/tests/test_mcp_server.py` |
| Claude Code installer bats | 13 | `prompts/ralph-meta-chain/tests/test_install_claude_code.bats` |
| Codex installer bats | 21 | `prompts/ralph-meta-chain/tests/test_install_codex.bats` |
| Dispatcher bats | 12 | `prompts/ralph-meta-chain/tests/test_install_dispatcher.bats` |
| Other bats stubs | 25 | `prompts/ralph-meta-chain/tests/test_*.bats` (4 files) |
| Read-only validators | 4 | `prompts/ralph-meta-chain/scripts/ralph_*.sh` |

**~204 cases total**, all green on `de028ac` and prior 4 commits.

### CI state

The 17 GitHub Actions checks all pass. **Kilo Code Review** has been
flagging on every commit due to a timeout / size cap (review duration
~22s on a 6.5k-line PR; posts zero comments). Treated as
non-actionable — see "Known issues" below.

### Recent commits (most recent first)

| Sha | Theme |
| --- | --- |
| `de028ac` | Codex P2-3 + P2-4 fixes (scope-aware prompts, manifest-gated MCP strip) |
| `7677056` | Codex P2-2 fix (self-test --no-log) |
| `4fdd2a4` | Codex P2-1 + P2-2 fixes (TOML duplicate, migration writes) |
| `ba6b7ed` | Round 10.1 (MCP harness shell-out fixes + unified install dispatcher) |
| `596f140` | Round 10 (Codex install surface) |
| `2f8d343` | Round 9 (Claude Code install surface) |

---

## How to run it

### As the maintainer (testing)

```bash
git clone https://github.com/Wellux/agent_testplayground.git
cd agent_testplayground
git checkout claude/ralph-obsidian-cron-jobs-Mb4A9

# Quickstart (10 min from clone to running):
prompts/ralph-meta-chain/install/install.sh --target all --dry-run
prompts/ralph-meta-chain/install/install.sh --target all
```

### As an end user

Point them at [`QUICKSTART_CLAUDE_CODE.md`](QUICKSTART_CLAUDE_CODE.md)
or [`QUICKSTART_CODEX.md`](QUICKSTART_CODEX.md).

### Running the test suite locally

```bash
# Bats (installer + dispatcher + stubs)
bats prompts/ralph-meta-chain/tests/

# Python (harness + MCP server)
cd prompts/ralph-meta-chain/scripts/harness && python3 -m unittest discover -s tests
cd ../../../../  # back to repo root
python3 prompts/ralph-meta-chain/tests/test_mcp_server.py

# Voice-server
cd prompts/ralph-meta-chain/voice-server && python3 -m unittest discover -s tests

# All validators
prompts/ralph-meta-chain/scripts/ralph_provider_validate.sh
prompts/ralph-meta-chain/scripts/ralph_business_ledger_check.sh
prompts/ralph-meta-chain/scripts/ralph_validate_frontmatter.sh
prompts/ralph-meta-chain/scripts/ralph_check_links.sh
```

---

## Architecture map (where to look first)

If you need to understand:

| Topic | Start here |
| --- | --- |
| The 8 axes' procedures | `prompts/ralph-meta-chain/0[1-8]-*.md` |
| The chain's invariants (append-only, privacy, budgets) | `prompts/ralph-meta-chain/CLAUDE.md` |
| Provider conformance (13-field interface) | `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` |
| Memory taxonomy (hot/warm/cold/frozen) | `docs/MEMORY_MODEL.md` |
| Why three install scripts | `install/install.sh` (the dispatcher's docstring) |
| Schedule rationale | `docs/CRON_JOBS.md`, `crontab.example` |
| Self-test surface | `scripts/harness/harness/self_test.py` |
| Each MCP tool's behaviour | `mcp-server/ralph_mcp_server.py` (with description fields) |
| Skill schema | `providers/claude-code/skills.md` § Frontmatter |
| Subagent format | `agents/README.md` |

---

## Backlog (post-handoff next steps)

Ordered by leverage. Top item is highest expected value.

### B1. ~~Wire skill metrics infrastructure~~ ✅ done (Round 12)

**Shipped:** `harness metrics record` + `harness metrics roll-up`
subcommands. Rows live in the existing `$VAULT/90-Meta/metrics.ndjson`
with a `kind: "skill_invocation"` namespace (no new file).

```bash
harness metrics record --skill ralph-memory --ok --tokens 1234 --ms 4500 --axis memory
harness metrics roll-up --window 7 --format json
```

8 axis subagents updated with `## Metrics (B1)` sections instructing
them to call `harness metrics record` at end of pass. 16 new unit
tests in `scripts/harness/tests/test_metrics.py`.

**Deferred to a follow-up (next session):**
- `--write-frontmatter` mode: roll-up writes back into each skill's
  frontmatter `metrics:` block. Skipped because not all skills have
  the block (the 8 axis subagents in `agents/` don't); design choice
  for which skills get the field is a separate decision.
- Auto-detection via Claude Code `PostToolUse` hook: skipped because
  hook fires for tool calls, not skill loads, and would record
  unrelated tool durations. Explicit `harness metrics record` call
  from each subagent's instruction is more reliable.

### B2. Per-folder compress thresholds (2h)

**Problem:** Single global `compress.token_threshold = 4000` over-
compresses MOCs (already meta) and under-compresses skills (should
stay terse).

**Proposed design:**

```yaml
compress:
  token_threshold: 4000   # default fallback
  thresholds:
    "30-Notes": 4000
    "40-Skills": 1500
    "20-MOCs": -1         # never compress
    "00_Inbox": -1
```

Update `harness/compress.py` to consult the map; fall back to
`token_threshold` if folder not listed.

### B3. Skip-when-empty prechecks (2h)

**Problem:** `scripts/ralph_context_compress.sh` fires every hour and
runs the chain prompt regardless of whether anything is above
threshold. Most hours are no-ops; the wrapper still spends a Claude
API call.

**Proposed design:**

```bash
# Top of ralph_context_compress.sh:
candidates=$(find "$VAULT/30-Notes" "$VAULT/40-Skills" -type f -name '*.md' \
  -newer "$VAULT/90-Meta/.last-compress-marker" -size +4000c | wc -l)
if [[ "$candidates" -eq 0 ]]; then
  echo "[compress] no candidates above threshold; skipping"
  exit 0
fi
# ... existing chain invocation
touch "$VAULT/90-Meta/.last-compress-marker"
```

Same pattern for `ralph_research_digest.sh` (skip if last fetch < 1h).

### B4. Auto-approve read-only slash commands (30 min)

**Problem:** Slash commands inherit from `permissions.allow`; any
tool not in the allowlist prompts. Audit found `ralph-autoheal.md`
declares `Bash(git:*)` but never uses git → unnecessary prompts.

**Proposed:** Tighten each read-only command's `allowed-tools` to
match exactly what it uses (cross-referenced against the existing
allowlist in `settings.template.json`).

### B5. Slash-command `--why` flags (3h)

Add `$ARGUMENTS` parsing for `--why` to every command; output now
explains how each line was computed (great for debugging dashboards
and for tutorial videos).

### B6. Migration script `--report-only` mode (1h)

`ralph_propose_migration.sh` writes `proposed-moves.md` etc. The
MCP tool exposes this as a "writing operation" (per Codex P2-2).
Cleaner: add a `--report-only` flag that prints to stdout without
writing files; MCP tool uses that mode.

### B7. Single `harness metrics dashboard` aggregator (1d)

Once B1 lands, build a single `harness metrics` command that prints
all 8 axes' fitness over the trailing 7d/30d. Replaces the current
need to roll-up by hand.

### B8. Drop deprecated Codex prompt installation (when upstream removes it)

Watch the Codex CLI changelog. Once `~/.codex/prompts/` is removed
upstream, drop our `--without-prompts` default-on path and remove
the prompt-symlinking branch entirely. (Skills are the future-proof
path already.)

---

## Known issues + decisions

### Kilo Code Review (external SaaS scanner)

**Status:** failing on every PR commit.
**Cause:** the PR is now ~6.5k lines / 67 files; Kilo's review fits
in a 22-second window with zero comments posted. Strong indication
of a per-review size cap.
**Decision:** skip silently; treat as non-actionable. Recommend
removing from required-checks if it doesn't fit this PR's scope.

### Codex bot review (chatgpt-codex-connector)

**Status:** working great. Posted 5 P2 inline comments on this PR;
all 5 addressed in commits `4fdd2a4` (P2-1, P2-2), `7677056` (P2-2
follow-up), and `de028ac` (P2-3, P2-4). Recommend keeping enabled.

### Privacy guard regression risk

The CI privacy job greps for a hardcoded user-identifier canary
(`equality.power...tothepeople`). If you fork or rename, update the
canary in `.github/workflows/ci.yml`.

### Voice-server gated

`voice-server/` is shipped but not exercised by the cron. The Apple-
Shortcuts + Mac mini + AirPods runtime is documented in
`docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md` and gated behind explicit
user enablement. Don't enable by default.

### Migration log auto-rotation

`migration/migration-log.md` self-rotates at 250 entries (logs
`op=log-rotate kept=250 dropped=N`). This is intentional, not
data loss. The audit chain remains complete via git history.

### settings.local.json (Claude Code on the web)

Claude Code on the web auto-creates `.claude/settings.local.json`
with session-scoped permission grants. The installer correctly leaves
this alone. Don't add it to git (it's already covered by `.gitignore`
in the bundled vault-template).

---

## How to extend

### Adding a new axis (call it #9)

1. Pick the next number: `09-<name>.md` under `prompts/ralph-meta-chain/`.
2. Follow the chain prompt schema (see existing `01-08`):
   - `## Goal` (one paragraph)
   - `## Inputs` (`$VAULT`, config keys, etc.)
   - `## Process` (numbered TodoWrite steps)
   - `## Output` (Karpathy-style log line)
   - `## Exit contract` (`<promise>COMPLETE</promise>` semantics)
3. Add an entry to `config.example.yml` `budgets.<axis>:`.
4. Add a row to `crontab.example` and `install/install_cron.sh`'s
   per-axis loop.
5. Add a slash command at `commands/ralph-<axis>.md`.
6. Add a subagent at `agents/ralph-<axis>.md`.
7. Update `commands/ralph-cron.md`'s axis table.
8. Add bats / py tests as appropriate.
9. Update `CHANGELOG.md` and `docs/CRON_JOBS.md`.

### Adding a new MCP tool

1. In `mcp-server/ralph_mcp_server.py`:
   - Add an entry to `TOOLS = [...]` with `name`, `description`,
     `inputSchema`. Be honest about side effects.
   - Add a `def tool_<name>(args): ...` implementation.
   - Register in `TOOL_IMPL = {...}`.
2. Add a regression test in `tests/test_mcp_server.py` using the
   fake-harness pattern (see `_spawn_with_fake_harness`).
3. Update `mcp-server/README.md` tools table.
4. Update `install/CLAUDE_CODE_INSTALL.md` and `install/CODEX_INSTALL.md`.

### Adding a new install target (e.g. for Cursor or Continue)

1. Mirror `install_codex.sh` as `install_<target>.sh`.
2. Add a case branch to `install/install.sh`'s `script_for()`.
3. Write `install/<TARGET>_INSTALL.md` (mirror `CODEX_INSTALL.md`).
4. Add `tests/test_install_<target>.bats`.
5. Wire into CI's `bats` job.

### Modifying a chain prompt

1. Edit the `0[N]-*.md` file.
2. If structural (sections renamed, schema changed), update both:
   - `commands/ralph-<axis>.md` (the dashboard)
   - `agents/ralph-<axis>.md` (the subagent that wraps it)
3. Run the validator: `prompts/ralph-meta-chain/scripts/ralph_validate_frontmatter.sh`
4. Update tests if axis count or budget changed.

### Adding a new specialist skill

1. Create `skills/<slug>/SKILL.md` with the canonical frontmatter
   (`name`, `description.Triggers`, `when_to_use`, `inputs`,
   `steps`, `tools`, `failure_modes`, `last_validated`,
   `metrics`, `prerequisites`, `is_prerequisite_of`, `tags`).
2. Update `skills/README.md`.
3. Update `agents/README.md`'s specialist table.
4. Update `tests/test_round6.py` (it asserts the specialist set).
5. The Codex installer auto-picks up new skill dirs; no install
   change needed.

---

## Pointers to deeper docs

| What you want to learn | Read |
| --- | --- |
| The full surface | [`PRD.md`](PRD.md) |
| How Claude Code integrates | [`CLAUDE_CODE_INTEGRATION.md`](CLAUDE_CODE_INTEGRATION.md), [`QUICKSTART_CLAUDE_CODE.md`](QUICKSTART_CLAUDE_CODE.md) |
| How Codex integrates | [`QUICKSTART_CODEX.md`](QUICKSTART_CODEX.md), [`../install/CODEX_INSTALL.md`](../install/CODEX_INSTALL.md) |
| The roadmap so far | [`ROADMAP.md`](ROADMAP.md), [`../CHANGELOG.md`](../CHANGELOG.md) |
| Memory invariants | [`MEMORY_MODEL.md`](MEMORY_MODEL.md), [`GOVERNANCE.md`](GOVERNANCE.md) |
| Privacy + secrets | [`SECURITY_PRIVACY.md`](SECURITY_PRIVACY.md) |
| Provider abstraction | [`PROVIDER_NEUTRAL_ARCHITECTURE.md`](PROVIDER_NEUTRAL_ARCHITECTURE.md) |
| The Round 8 migration runbook (already executed) | [`ROUND_8_RUNBOOK.md`](ROUND_8_RUNBOOK.md) |
| MCP server internals | [`../mcp-server/README.md`](../mcp-server/README.md) |
| Daily/weekly playbook | [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) |

---

## Contacts + context

This handoff was generated end-of-session 2026-05-09. The branch
`claude/ralph-obsidian-cron-jobs-Mb4A9` and PR #2 are the canonical
state. If you need session context, the PR description summarizes
Rounds 8 → 10.1 with rollback plans per commit.

For bugs that should NOT be fixed silently:
- privacy violations
- self-test failures persisting > 24h
- MCP tool description claiming a contract it doesn't honour
- installer clobbering user files
- chain mutating without `<promise>COMPLETE</promise>` exit

For everything else: trust the autoheal + autoevolve loops.

Welcome aboard.
