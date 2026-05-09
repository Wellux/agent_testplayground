# RESEARCH_SYNTHESIS.md

Cross-source synthesis derived from `RESEARCH_NOTES.md`. Organized on the
master spec's nine synthesis axes.

## 1. Strongest patterns across projects

| Pattern                                            | Sources                                                    |
| -------------------------------------------------- | ---------------------------------------------------------- |
| Same-prompt-mutating-workspace loop                 | anthropics/ralph-wiggum, ghuntley, snarktank              |
| `<promise>COMPLETE</promise>` + max_iterations exit | anthropics/ralph-wiggum                                    |
| Three-layer memory: raw / wiki / schema             | Karpathy LLM Wiki, NicholasSpisak/second-brain             |
| sqlite-vec + FTS5 single-file local store          | obra/knowledge-graph                                       |
| Genetic-Pareto / MAP-Elites prompt evolution        | gepa-ai/gepa, hermes-self-evolution, OpenEvolve            |
| Reflexion lesson loop                              | gepa-ai/gepa, OpenAI Cookbook self-evolving                |
| Skills-from-experience (≥ 2× use → candidate)      | NousResearch/hermes-agent, Voyager                         |
| Voyager skill curriculum (prerequisite chain)       | Voyager (via EvoAgentX survey)                             |
| Heartbeat + zombie detection                       | NousResearch/hermes-agent                                  |
| Supervisor + specialized sub-agents                 | Nate Herk (n8n)                                            |
| Weekly news + scan-everything ethos                 | Matt Wolfe / FutureTools                                   |
| Aggressive deprecation                             | Alex Finn ("Claude Life OS")                               |
| Background daemon on cron / launchd                | moazbuilds/claudeclaw                                      |
| Permissions allow/deny allowlist                   | swarmclawai/swarmclaw                                      |
| Promptfoo-shaped fixture YAML                      | promptfoo/promptfoo                                        |

These are the patterns Ralph Meta Chain visibly inherits.

## 2. Weak patterns to avoid

- **Multi-provider-by-default runtime** (swarmclaw 23+ providers). Sends
  user data widely. We stay Claude-Code-only at runtime, multi-provider
  only at the *fixture* layer.
- **Always-listening voice** (some ClaudeClaw demos). Privacy hazard
  without consent + audit. Gated.
- **Cloud-sandbox coding agents** (Cursor 3, OpenAI Codex cloud). Ship
  user code to vendor. Local CLIs only.
- **Auto-applied prompt rewrites** without human review (some Hermes
  demos). Ralph stays proposal-based above LOW risk.
- **Weight-level retraining** (OpenAI Cookbook's full path). We're
  prompt/skill level only.
- **Loops without iteration cap** (raw `while :;`). Always wrap.
- **Deletion as compression** (some second-brain projects). Always
  archive originals.
- **External eval services** (promptfoo cloud variant). Local rubric
  judge only.
- **n8n-style monolithic workflow stacks** (Nate Herk demos). We use
  composable Markdown prompts + Bash + Python instead.

## 3. Architecture recommendations

1. **Markdown is the canonical interface.** Every state — memory, skills,
   prompts, ledgers, reports — is a Markdown file with frontmatter.
2. **Three layers persist.** raw (`00-Inbox/`) → wiki (`30-Notes/`,
   `20-MOCs/`) → schema (`CLAUDE.md`, `90-Meta/`).
3. **sqlite-vec + FTS5** for retrieval, Ollama for embeddings. One file:
   `90-Meta/embeddings.db`.
4. **Prompt evolution = GEPA × MAP-Elites × Reflexion.** Population A/B,
   per-bin survivor, accumulated lessons.
5. **Cron is the heartbeat.** External `until ! ...` loop wraps each
   firing; in-loop iteration counter caps it.
6. **8 axes today.** research → memory → skills → interaction (daily) +
   compress (hourly) + heal (every 6h) + evolve (weekly Sun) + update
   (weekly Mon).
7. **Approval gates at every risk class.** LOW autonomous; MEDIUM proposal;
   HIGH explicit approval; CRITICAL approval + audit + rollback plan.
8. **Provider-neutral specs, Claude-Code-only runtime.** Codex, Gemini,
   local-models all have adapter specs but no active execution.
9. **Local-first by default.** No external endpoints called by default.
   Tailscale-only for any cross-device path.
10. **Append-only by default.** Compression archives originals; nothing
    is deleted without explicit approval.

## 4. Implementation priorities (greenfield rebuild path)

In order of leverage:

1. Research notes (this file's siblings) — done in Round 1.
2. Design docs (`docs/*.md`) — done in Round 1.
3. Vault-template expansion (00_System through 99_Archive). Round 2.
4. Business-entity governance scaffold (Markdown only). Round 3.
5. Migration tooling (inventory + dry-run). Round 4.
6. Provider adapter specs (Markdown only). Round 4.
7. Bash shims wrapping the existing Python harness (`scripts/ralph_*.sh`).
   Round 5.
8. Plugin rebuild under `prompts/ralph-meta-chain/obsidian-plugin/`.
   Round 6.
9. JSON schemas + bats tests. Round 7.
10. Remove the Phase 1-6 reference implementation when greenfield is
    feature-complete. Last round.

## 5. Missing knowledge

- How well Cognee performs over a 5k-note vault. No benchmark numbers
  in our research yet.
- Letta vs sqlite-vec break-even — what vault size makes Letta worth
  the install?
- Apple Shortcuts API stability across iOS 19 / 20.
- Cloudflare Tunnel rate limits for Alexa skill traffic.
- Whisper.cpp Apple Silicon perf (cold-start latency for /ralph/voice).
- GEPA's MAP-Elites bin geometry sensitivity — does (token × format)
  bin best, or (token × banned)?

These belong in the research watchlist for incremental answer-gathering.

## 6. Deferred research

- Multi-vault federation (one Ralph, N Obsidian vaults).
- Cross-device mobile capture without Tailscale.
- Browser-extension capture surface.
- Full-graph reasoning over the vault (Cognee deeper integration).
- Structured outputs / function-calling for the rubric judge.
- Differential privacy for client-data ingestion in the business
  entity.

## 7. Security risks

| Risk                                                       | Mitigation                                          |
| ---------------------------------------------------------- | --------------------------------------------------- |
| Loop-without-cap → runaway cost                             | max_iterations + `timeout` outer wrapper            |
| Auto-rewritten prompt regresses                             | harness ab + reflect + reject-on-loss               |
| Background daemon = always-on attack surface                | Tailscale-only origin guard                         |
| Audio leaves the host                                      | Local Whisper.cpp; 503 if missing                   |
| API key leakage                                            | `.env` gitignored; never in vault                   |
| Vault overwrite                                            | Append-only; archive-not-delete                     |
| Cron drift                                                 | install.sh idempotent + `# RALPH-managed:` tagging  |
| External research run unsupervised                         | Default off; explicit env to enable                 |
| Business action sent without approval                      | Approval ledger; HIGH-risk gates                    |
| Repo-wide migration moves wrong files                      | Inventory-first, proposal-second, apply-last        |

## 8. Fastest useful MVP path

If a user wants Ralph running on their machine within an hour:

1. `git clone` the repo, `cp config.example.yml config.yml`, edit
   `vault_path`.
2. `cd harness && uv sync && cp .env.example .env`, paste API key.
3. `ollama pull nomic-embed-text`.
4. `./scripts/install.sh --dry-run` to preview cron entries.
5. `./scripts/install.sh`.

That's the **Phase 1-6 reference implementation** path. It works today.
The greenfield rebuild will preserve this UX.

## 9. Long-term architecture path

- **Year 1:** Phase 1-6 → master-spec greenfield → business-entity
  scaffold operational with approval gates → voice/multi-device after
  separate scoping.
- **Year 2:** multi-vault federation; offline-first mobile capture;
  graph reasoning; richer rubric judge with self-rubric calibration.
- **Year 3:** durable identity layer (the deferred "autonomous business
  entity" with legal/financial agency); contributor model for shared
  vaults (consent-gated).

---

## Confidence summary

- **High confidence** (≥ 0.85): the architecture recommendations, the
  identified weak patterns, the Phase 1-6 implementation that already
  works.
- **Medium confidence** (0.6 – 0.85): timing of the rebuild rounds, the
  specifics of the business-entity workflow set, Apple Shortcut
  stability across OS versions.
- **Low confidence** (< 0.6): year-2 and year-3 directions; specific
  benchmark numbers for memory backends.

Cross-link any new entry in `RESEARCH_NOTES.md` from at least one section
above to keep the synthesis honest.
