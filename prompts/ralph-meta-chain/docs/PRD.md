# Product Requirements Document — Ralph Meta-Chain

**Status:** approved (Round 1-10.1 shipped)
**Owner:** repo maintainer
**Last updated:** 2026-05-09

---

## 1. Problem statement

Power users of LLM coding agents (Claude Code, Codex CLI, Cursor, etc.)
hit four compounding problems within weeks of regular use:

1. **Memory drift.** The agent forgets context between sessions. Each
   new conversation re-explains the same things; useful patterns from
   yesterday don't surface today.
2. **Skill regression.** A workflow that worked last week subtly stops
   working — a tool was renamed, a flag changed, a path moved — and
   the agent has no way to detect or self-heal.
3. **Prompt entropy.** The user keeps hand-editing system prompts and
   custom instructions. Without measurement, every edit is a coin flip
   between improvement and regression.
4. **Toolchain rot.** Upstream libraries, MCP servers, model versions,
   and CLI flags change constantly. The user discovers regressions only
   when something visibly breaks.

These problems compound: drifted memory means lower-quality skill
mining; regressing skills mean noisier interaction signals; rotted
tools mean false-positive heal alerts. **Without intervention, the
agent's effective capability decays over time despite improving
upstream models.**

## 2. Goals

The Ralph meta-chain is a **self-improving substrate** that runs
alongside the user's coding agent and:

| G# | Goal | Success looks like |
| --- | --- | --- |
| G1 | **Cumulative memory** that survives sessions | Yesterday's promotions appear as `[[wikilinks]]` in today's context. Trailing-30d retrieval F1 ≥ 0.7. |
| G2 | **Self-healing skills** with measurable success rates | Every skill has a populated `metrics.success_rate`. Stale skills (last_invoked > 90d) auto-flagged. |
| G3 | **A/B-tested prompt evolution** | No prompt change ships without a judged win-rate ≥ 0.6 vs. its predecessor. |
| G4 | **Local CI mirror** that catches regressions before the user does | `harness self-test` runs every 6h; first-pass auto-fix rate ≥ 80%. |
| G5 | **Provider-neutral** — works equally with Claude Code and Codex | Same chain, same skills, same MCP server; config divergence ≤ 10 lines per provider. |
| G6 | **Privacy-clean** — never leaks user identity to git | Zero matches for the user-identifier canary in tracked files. |

## 3. Non-goals

| NG# | Out of scope | Why |
| --- | --- | --- |
| NG1 | Multi-user / multi-tenant | Single-user, single-machine product. Sharing happens via git, not a SaaS. |
| NG2 | Cloud-hosted memory | Local-first by design (Ollama embeddings, sqlite-vec storage). Users may opt into a cloud backend later, but it's never the default. |
| NG3 | Replacing the coding agent | The chain SUPPORTS Claude Code / Codex; it doesn't BECOME them. No model wrapping, no proxy. |
| NG4 | A general-purpose Obsidian plugin | The bundled plugin is a UI for THIS chain, not a Voltron of Obsidian features. |
| NG5 | Real-time | All loops are bounded-budget cron firings. No streaming, no sub-second latency requirements. |

## 4. Personas

### Primary — the **practitioner** (week 2+)

Someone who's used Claude Code or Codex daily for at least two weeks
and has accumulated:
- 10+ recurring workflows they've explained from scratch
- a handful of bash one-liners they keep retyping
- a system-prompt stub that's been hand-edited 5+ times
- a vague sense that the agent should remember more

### Secondary — the **integrator**

A team lead deploying the chain across a small team. Cares about:
- repo-scoped install (`--scope project`) so collaborators inherit
  the surface via git
- privacy guard (no user identifiers leaked)
- audit trail (`90-Meta/log.md` + `heal-checks.ndjson`)

### Tertiary — the **evaluator**

Someone running A/B experiments on prompt strategies. Cares about:
- the harness CLI's `ab` subcommand
- promptfoo-shaped fixtures under `harness/fixtures/`
- the `interaction` axis's judge

## 5. User journey (happy path)

```
Day 0:   git clone + install.sh --target all
         → 3 surfaces wired, vault seeded from template
Day 1:   user runs Claude Code normally; no chain interaction
         → cron fires research at 01:00, memory at 02:00, skills at 03:00
Day 2:   user types `/ralph-cron`
         → sees yesterday's promotions, new skills, A/B winners
         → notices an open evolution proposal; accepts via harness CLI
Week 1:  user has 50+ atomic notes, 5 new skills, 3 system-prompt rewrites
         → autoheal catches a frontmatter validation regression at 06:15 UTC; auto-fixed
Week 4:  autoevolve fitness rolls show interaction axis regressing
         → proposes a prompt rewrite; user accepts; next week's fitness recovers
Month 3: skills stale-rate < 5%; memory retrieval F1 ≥ 0.75; user trusts
         the chain enough to delegate "promote this inbox" to a subagent
```

## 6. Architecture

### High-level surfaces

```
┌──────────────────────────┐    ┌──────────────────────────┐
│  Claude Code             │    │  OpenAI Codex CLI         │
│  ─────────────           │    │  ─────────────            │
│  /ralph-* slash commands │    │  /ralph-* prompts (dep)   │
│  Agent(ralph-*) subagents│    │  $ralph-* skills          │
│  PreToolUse / Stop hooks │    │  AGENTS.md auto-load      │
│  ralph_* MCP tools       │    │  ralph_* MCP tools         │
└──────────┬───────────────┘    └──────────┬───────────────┘
           │                               │
           ▼                               ▼
   ┌────────────────────────────────────────────┐
   │  Shared MCP server (ralph_mcp_server.py)    │
   │  ────────────────────────────────────       │
   │  ralph_query / ralph_axis_status            │
   │  ralph_self_test / ralph_migration_dry_run  │
   └────────────────┬────────────────────────────┘
                    │
                    ▼
   ┌────────────────────────────────────────────┐
   │  harness CLI  (Python)                       │
   │  ────────────                                │
   │  ab embed query ingest compress reflect      │
   │  traces self-test                            │
   └─────────────┬──────────────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────────────┐
   │  $VAULT (Obsidian)                           │
   │  ────────────                                │
   │  00_Inbox/   30-Notes/   40-Skills/          │
   │  20-MOCs/    60-Interactions/   90-Meta/    │
   └────────────────────────────────────────────┘
                 ▲
                 │ scheduled execution
                 │
   ┌────────────────────────────────────────────┐
   │  cron (Linux) / launchd (macOS)              │
   │  ────────────                                │
   │  8 numbered prompts at UTC schedule          │
   │  research → memory → skills → interaction    │
   │  hourly compress / 6h heal / weekly evolve   │
   │  + update                                    │
   └────────────────────────────────────────────┘
```

### Component responsibilities

| Component | Owns | Responsibility |
| --- | --- | --- |
| `0[1-8]-*.md` chain prompts | the procedure for each axis | Single source of truth for what each axis does. Cron and subagents both reference these. |
| `harness/` CLI (Python) | execution + measurement | A/B harness, embeddings, ingest, compression, traces, self-test. The MCP server shells out here. |
| `mcp-server/` (Python, stdlib only) | LLM-callable tool surface | 4 tools, JSON-RPC 2.0 over stdio. Same server serves both Claude Code and Codex. |
| `voice-server/` (FastAPI) | optional voice input dispatcher | Mac mini endpoint for "hey ralph, capture this" via Apple Shortcuts. Gated behind `docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md`. |
| `obsidian-plugin/` (TypeScript) | UI for the chain | Status bar, command palette, log/metrics panes. Built with esbuild. |
| `install/install*.sh` | deployment | `install.sh` dispatcher + 3 per-target installers. All idempotent, manifest-tracked, refuse-to-clobber. |
| `vault-template/` | day-1 vault | `cp -n`'d into the user's `$VAULT` on first install. Includes `CLAUDE.md`, day-1 skills, MOC stubs. |

### Data flow (a typical daily cycle)

```
01:00 research    → fetches GitHub trending → writes 00_Inbox/research/
02:00 memory      → reads 00_Inbox/ → promotes to 30-Notes/, updates 20-MOCs/
03:00 skills      → mines 30-Notes/ patterns → writes 40-Skills/
04:00 interaction → reads 60-Interactions/feedback.ndjson → A/B fixtures
:30 compress     → scans 30-Notes/ + 40-Skills/ → archives over-threshold
06:15+6h heal    → harness self-test → 90-Meta/heal-checks.ndjson
Sun 05:00 evolve → metrics → 06_Reports/evolve-*.md (proposals only)
Mon 06:00 update → release feeds → 06_Reports/weekly-digest-*.md
```

## 7. Surfaces shipped

| Surface | Count | Where defined |
| --- | --- | --- |
| Cron axes | 8 | `0[1-8]-*.md` |
| Slash commands | 11 | `commands/ralph-*.md` |
| Subagents (Claude Code) | 8 | `agents/ralph-*.md` |
| Specialist skills | 8 | `skills/<slug>/SKILL.md` |
| Lifecycle hooks (Claude Code) | 5 | `hooks/*.sh` |
| MCP tools | 4 | `mcp-server/ralph_mcp_server.py` |
| Install targets | 3 | `install/install_{cron,claude_code,codex}.sh` + dispatcher |
| Validators (read-only) | 4 | `scripts/ralph_*_check*.sh` + `scripts/ralph_validate_*.sh` |

## 8. Success metrics

### Quantitative

| Metric | Target | Measured via |
| --- | --- | --- |
| Trailing-30d retrieval F1 (semantic + FTS5) | ≥ 0.70 | `harness traces` + manual spot-check |
| Skill stale rate (last_invoked > 90d) | < 5% | `harness query` over `40-Skills/` |
| Self-test green pass rate (last 30 days) | ≥ 95% | `90-Meta/heal-checks.ndjson` |
| Mean A/B winner confidence (interaction axis) | ≥ 0.7 | `harness ab` judge output |
| Privacy-guard violations | 0 | CI's privacy job |
| Average daily user-facing chain artefacts written | 5–15 | `90-Meta/log.md` axis lines |

### Qualitative

| Signal | How we'd know |
| --- | --- |
| User stops re-explaining recurring context | session-capture inbox depth grows; promotions sustained |
| User trusts the autoheal pass | self-test failures get auto-fixed without escalations piling up |
| The system feels "alive" without being noisy | weekly evolve proposals = 1-3 (not 0, not 10+) |

## 9. Approval classes (deployment risk)

Inherited from `docs/APPROVAL_GATES.md`:

| Class | What | Examples |
| --- | --- | --- |
| LOW | read-only / vault-scoped / fixture | dashboards, reports, A/B fixtures, slash commands |
| MEDIUM | writes to repo / vault outside `30-Notes/` | new skills, prompt rewrites, harness/plugin code, installers |
| HIGH | mutates outside repo / vault | cron registration, host-side files, Dependabot auto-merge |
| CRITICAL | irreversible / cross-repo / data loss risk | `git push --force`, schema migration apply, secrets rotation |

The chain runs only LOW + MEDIUM autonomously. HIGH requires explicit
user invocation (e.g. `install.sh`, `harness migration apply`).
CRITICAL is never automated.

## 10. Out of scope (explicit non-goals + future scope)

### Explicitly out (will not ship in this product)

- a SaaS hosted version
- model-agnostic adapter for non-tool-use models
- collaborative multi-user vault
- real-time / streaming responses

### Future scope (separate documents; gated behind feature flags)

- voice multi-device runtime (`docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md`)
- business-entity ledger automation (`docs/BUSINESS_ENTITY_SCOPE.md`)
- cloud-hosted memory backend swap (cognee / letta) — config exists,
  not exercised by the cron yet

## 11. Open questions (pending resolution)

| Q# | Question | Owner | Resolution path |
| --- | --- | --- | --- |
| OQ1 | Should `autoupdate` defer entirely to Dependabot now that we have it wired? | maintainer | Compare 4 weeks of overlap; deprecate the chain's bump proposals if Dependabot covers ≥ 90% |
| OQ2 | Per-folder compress thresholds — config schema design | maintainer | See `docs/HANDOFF.md` § Backlog item 2 |
| OQ3 | Skill-metrics auto-collection — record API design | maintainer | See `docs/HANDOFF.md` § Backlog item 1 |
| OQ4 | Codex prompt deprecation timeline — should we drop them by Round 12? | maintainer | Watch upstream; if Codex removes the prompt directory, drop our installer surface |
| OQ5 | Should the autoevolve axis be allowed to amend axis prompts, or only skills? | maintainer | Risk-rate prompt mutations; current default = skills-only is conservative |

## 12. Cross-references

- [`docs/ROADMAP.md`](ROADMAP.md) — round-by-round shipping log
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — deeper architectural decisions
- [`docs/CRON_JOBS.md`](CRON_JOBS.md) — schedule + axis details
- [`docs/MEMORY_MODEL.md`](MEMORY_MODEL.md) — memory layers, compression rules
- [`docs/EVOLUTION_MODEL.md`](EVOLUTION_MODEL.md) — fitness contract, A/B promotion
- [`docs/SECURITY_PRIVACY.md`](SECURITY_PRIVACY.md) — privacy guard, secrets handling
- [`docs/GOVERNANCE.md`](GOVERNANCE.md) — append-only invariants, refusal patterns
- [`docs/PROVIDER_NEUTRAL_ARCHITECTURE.md`](PROVIDER_NEUTRAL_ARCHITECTURE.md) — 13-field interface
- [`docs/HANDOFF.md`](HANDOFF.md) — next-maintainer guide
