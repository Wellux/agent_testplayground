# CONTEXT_LIFECYCLE.md

## Purpose

The canonical 9-step self-improvement loop for Ralph Meta Chain:
**observe → diagnose → propose → test → score → approve → apply → audit
→ learn**. Adapted from the OpenAI Cookbook self-evolving-agents recipe,
applied at the prompt/skill level rather than weight level. Every cron-
driven prompt walks this loop within its budget.

## Step-by-step

### 1. Observe

Read local evidence only (research streams are gated). Sources per axis:

- **memory** → `00-Inbox/`, last 7 daily notes, orphan-tagged notes.
- **skills** → `40-Skills/`, daily-note `## actions` sections, freshly
  promoted notes.
- **interaction** → `60-Interactions/`, last 7 daily notes' `## transcript`
  / `## feedback`, `50-Prompts/`.
- **research** → external feeds (only with explicit `--apply` /
  network env enabled).
- **compress** → `30-Notes/`, `10-Daily/` (older than 7d).
- **heal** → `90-Meta/ralph-state.json`, `90-Meta/log.md` tail,
  `90-Meta/heal-checks.ndjson`.
- **evolve** → `90-Meta/metrics.ndjson` (full week), per-skill rolling
  success_rate.
- **update** → release feeds + creator RSS.

### 2. Diagnose

Pure read-mostly classification:

- missing capability (no skill covers a repeated action).
- repeated failure (same error message in `log.md` ≥ 3 times).
- fragile script (heal-check fails twice consecutively).
- memory bloat (notes > token threshold).
- obsolete docs (link rot, outdated commands).
- stale prompt (validated_against fixture > 14d old).
- poor retrieval (recall hit-rate trending down).
- business workflow gap (ledger entry without matching workflow doc).

Output: `30-Notes/<id>-hypothesis-<topic>.md` with `status: open`.

### 3. Propose

For each diagnosis, write a proposal note. Proposals are Markdown:

```yaml
---
ralph_type: experiment
memory_layer: experiment
created: <YYYY-MM-DD>
status: proposed
risk_class: LOW | MEDIUM | HIGH | CRITICAL
files_affected: ["..."]
expected_benefit: "..."
test_plan: "..."
rollback_plan: "..."
approval_required: true | false
confidence: 0.0-1.0
---
```

Proposals are **append-only**; nothing executes from this step.

### 4. Test

Programmatic validation:

- `harness ab` for prompt/skill candidates,
- `harness self-test` for cross-cutting drift,
- `harness embed` + `harness query` for retrieval changes,
- bats / pytest for code-only changes (Round 4+).

Tests run in dry-run mode unless explicitly applied.

### 5. Score

Each test outputs metrics (one ndjson row per arm) per the rubric in
`AB_HARNESS.md` (rubric: 1-5 brevity, helpfulness, format-compliance,
banned-phrase count). Scores feed back into proposal frontmatter.

### 6. Approve

Approval gating per `APPROVAL_GATES.md`:

| Risk class | Gate                                       |
| ---------- | ------------------------------------------ |
| LOW        | may auto-apply if non-destructive          |
| MEDIUM     | proposal recorded; auto-apply with audit    |
| HIGH       | explicit user approval required             |
| CRITICAL   | explicit approval + audit + rollback plan   |

LOW examples: tagging an orphan note, creating a missing index entry,
appending to log.md.
HIGH examples: deprecating a skill, rewriting a prompt, modifying cron.
CRITICAL examples: business action, repo-wide migration apply.

### 7. Apply

Apply only the approved changes. All applies:

- write through git when the target is repo-tracked,
- archive originals (`_archive/<id>-original.md`) when the target is
  vault content,
- update `90-Meta/index.md` and `90-Meta/log.md` after every change,
- run a follow-up `harness self-test` to confirm no regression.

### 8. Audit

Append:

- one line to `90-Meta/log.md` (Karpathy format `## [YYYY-MM-DD] axis | k=v`),
- one line to `90-Meta/ralph-state.json` (atomic temp+rename),
- a `## Ralph YYYY-MM-DD` block to every modified file.

For HIGH/CRITICAL changes also append to:

- `60-Interactions/escalations.md` (heal-style summary),
- `business-entity/ledgers/audit-log.md` (Round 3+).

### 9. Learn

Extract durable lessons:

- skill amend → bumped `last_validated`, refreshed `metrics`.
- prompt rewrite → appended `reflections:` line via `harness reflect`.
- proposal validated → status flipped to `validated`, evidence cited in
  next-week's `RESEARCH_SYNTHESIS.md` if it generalizes.

The lesson loop is what makes "same prompt, mutating workspace" a
ratchet rather than a treadmill: each iteration starts smarter than the
last.

## Context-scoring dimensions

When the memory pass decides what to keep loaded ("hot") vs demote, it
scores each candidate across these dimensions (each 0-1, weighted in
`config.yml`):

1. current project relevance,
2. recurrence frequency (how often the user references this),
3. business leverage,
4. actionability (is this a step or a fact?),
5. uniqueness (deduped against existing notes),
6. confidence,
7. freshness,
8. privacy sensitivity (high → demote sooner),
9. token cost (heavy notes demote faster),
10. retrieval value (`harness query` hit-rate),
11. contradiction risk,
12. archival value.

The weighted sum determines the recommendation; the user (or, for LOW
risk, the chain itself) acts on it.

## Safety notes

- The loop runs **inside the budget**. Each prompt has `budgets.<axis>`
  in `config.yml` capping promotions / rewrites / experiments per pass.
- The loop **stops cleanly** on `90-Meta/STOP`. Every step honors it.
- The loop is **append-only by default**. Only Step 7 (apply) mutates
  existing content, and only after Step 6 (approve).
- The loop is **idempotent**: re-running a converged pass produces zero
  writes and emits `<promise>COMPLETE</promise>` immediately.

## Cross-references

- `ARCHITECTURE.md` — where the loop sits.
- `MEMORY_MODEL.md` — what the observe step reads.
- `AB_HARNESS.md` — how scoring is computed.
- `APPROVAL_GATES.md` — risk class definitions and required gates.
- `AUTOHEAL.md` — heal axis specialization of this loop.
- `AUTOUPDATE.md` — update axis specialization.
- Phase 1-6 reference implementations:
  `prompts/ralph-meta-chain/0[1-8]-*.md`, `harness/harness/`.

## Next actions

After this, read `AB_HARNESS.md` for the test/score mechanics, then
`APPROVAL_GATES.md` for the gating rules.
