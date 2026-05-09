# MEMORY_MODEL.md

## Purpose

The memory taxonomy for Ralph Meta Chain: types, temperatures, stability
classes, and the canonical frontmatter schema. Maps the Karpathy LLM-Wiki
three-layer model (raw / wiki / schema) onto a typed Obsidian vault so
prompts and the harness agree on what they're reading.

## Memory types

| Type           | Where it lives          | Lifecycle                                   |
| -------------- | ----------------------- | ------------------------------------------- |
| **raw**        | `00-Inbox/`              | promoted to atomic note within 24h, then archived to `00-Inbox/_processed/` |
| **episodic**   | `10-Daily/`              | rolled up weekly to `10-Daily/_weekly/`       |
| **semantic**   | `30-Notes/`              | atomic Zettelkasten; updated via append-only |
| **procedural** | `40-Skills/`             | reusable; revalidated every 14d              |
| **preference** | `60-Interactions/`        | single source of truth; `user-profile.md`    |
| **interaction**| `60-Interactions/feedback-log.md` | append-only signal stream             |
| **entity**     | `30-Notes/` w/ tag       | people / orgs / products                     |
| **project**    | `30-Notes/` w/ tag       | active work; demoted when status=complete    |
| **decision**   | `30-Notes/` w/ tag       | irreversible; never compressed without approval |
| **business**   | `business-entity/ledgers/` (Round 3) | append-only ledgers              |
| **research**   | `00-Inbox/` raw + `30-Notes/` post-promotion | from `harness ingest`     |
| **experiment** | `harness/fixtures/`, `90-Meta/metrics.ndjson` | structured + reproducible |
| **system**     | `90-Meta/`               | meta-state; index, log, embeddings, state    |
| **canonical**  | `30-Notes/` flagged stable | source of truth; HIGH-risk edits           |

## Memory temperatures

| Temperature | Meaning                                  | Retrieval priority    |
| ----------- | ---------------------------------------- | --------------------- |
| **hot**     | active project / current week            | always loaded          |
| **warm**    | useful, not always loaded                | retrieved on match     |
| **cold**    | archived but searchable                  | retrieved on demand    |
| **frozen**  | retained for provenance only             | not loaded by default  |

`hot_memory_window_days` and `cold_memory_window_days` in `config.yml`
control demotion. Default: hot ≤ 7d since last touch, warm ≤ 90d, cold
> 90d, frozen on explicit demotion.

## Memory stability

| Stability       | Meaning                                     |
| --------------- | ------------------------------------------- |
| **volatile**    | may change soon (today's daily note)         |
| **provisional** | useful but uncertain (open hypotheses)       |
| **stable**      | trusted unless contradicted (most semantic)  |
| **canonical**   | source of truth (flagged HIGH-risk to edit)  |
| **deprecated**  | do not use unless specifically needed        |

Auto-deprecation: a skill whose `success_rate < 0.6` over 14d and ≥ 5
invocations is **proposed** for deprecation by `07-autoevolve` — never
auto-deprecated.

## Canonical frontmatter schema

Every Ralph-managed Markdown file uses this schema (subset of fields per
type). The full surface:

```yaml
---
ralph_type:        memory | skill | experiment | report | research | decision |
                   entity | project | provider | business | migration | prompt | system
memory_layer:      raw | episodic | semantic | procedural | preference |
                   interaction | entity | project | decision | business |
                   research | experiment | system | canonical
memory_temperature: hot | warm | cold | frozen
created:           ISO_DATE
updated:           ISO_DATE
source:            manual | cron | plugin | harness | claude-code | import |
                   migration | research
confidence:        0.0-1.0
stability:         volatile | provisional | stable | canonical | deprecated
privacy:           private | work | client | public
provider:          claude-code | provider-neutral | openai-codex-deferred |
                   gemini-ai-studio-deferred | local-models-deferred
approval_required: true | false
status:            draft | proposed | approved | active | archived | deprecated
tags:
  - ralph
related:
  - "[[Some Note]]"
summary: "One-sentence compressed summary"
---
```

Type-specific extensions:

- **skill** adds: `name, description, when_to_use, inputs, steps, tools,
  failure_modes, last_validated, metrics, prerequisites, is_prerequisite_of`.
- **prompt** adds: `name, last_rewritten, validated_against, bin (MAP-Elites
  bin), reflections (Reflexion lesson loop)`.
- **hypothesis** (a memory of `ralph_type: experiment`) adds: `axis,
  experiment, cheap_to_test, evidence`.
- **bump-proposal** adds: `package, from, to, breaking_changes, test_plan,
  rollback_plan`.

## Memory pipeline

```
capture → frontmatter → classify → score (usefulness, stability, privacy,
retrieval) → dedupe → link → extract (durable facts) → propose compression
→ archive raw → promote distilled → update indexes → daily report → emit
recommendations
```

Each arrow is implemented either in a prompt (`01-memory-optimizer.md`,
`05-compress.md`) or in the harness (`harness embed`, `harness compress`).

## Memory backends

The retrieval store is pluggable per `embeddings.backend` in `config.yml`:

| Backend            | Implementation                            | Default? |
| ------------------ | ----------------------------------------- | -------- |
| `local-sqlite-vec` | sqlite-vec + FTS5 in `90-Meta/embeddings.db` (obra/knowledge-graph schema) | yes |
| `cognee`           | local-first graph reasoning (cognee-ai/cognee) | no, opt-in |
| `letta`            | OS-style tiered memory (letta-ai/letta)   | no, opt-in |

See `harness/harness/memory_backends.py` for the `select_backend()`
selector. Mem0 and Zep are documented for comparison but not wired —
they're external-service-shaped and conflict with our local-first default.

## Compression rules

Compression must:

1. preserve raw input in `_archive/` before any rewrite,
2. produce a summary ≤ 40% of the original word count,
3. retain every `[[wikilink]]`,
4. retain every claim flagged `stability: canonical`,
5. mark uncertain claims as `provisional`,
6. write a diff-like proposal note before applying when token threshold
   exceeded by > 4×.

Compression must NOT:

1. delete the original,
2. collapse contradictory notes silently,
3. silently rewrite preferences (`60-Interactions/user-profile.md`),
4. silently alter business ledgers,
5. silently change approval gates.

## Safety notes

- **Vault is privacy-sensitive.** Treat `00-Inbox/` and any
  `60-Interactions/feedback-log.md` entries as private by default. Tag
  `privacy: client` on any client-related capture.
- **Append-only is non-negotiable.** Compression archives originals;
  deletion requires explicit approval per `APPROVAL_GATES.md`.
- **Canonical claims are HIGH-risk.** Any edit that would flip
  `stability: canonical` requires explicit approval.
- **Embeddings are best-effort.** Ollama down ≠ memory pass blocked.
  Notes get tagged `#unrecalled` and re-embedded on the next compress run.

## Cross-references

- `ARCHITECTURE.md` — where this fits in the system.
- `CONTEXT_LIFECYCLE.md` — how memory feeds the observe→…→learn loop.
- `AB_HARNESS.md` — how prompt frontmatter integrates with A/B.
- `APPROVAL_GATES.md` — risk classes for memory edits.
- Phase 1-6 reference: `harness/harness/memory_backends.py`,
  `harness/harness/embeddings.py`, `prompts/ralph-meta-chain/01-memory-optimizer.md`.

## Next actions

After this, read `CONTEXT_LIFECYCLE.md` to understand how the memory
layers feed the self-improvement loop, then `CRON_JOBS.md` to see when
each memory transformation fires.
