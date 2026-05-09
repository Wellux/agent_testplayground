# SECURITY_PRIVACY.md

## Purpose

The threat model + privacy model for Ralph Meta Chain. Local-first by
design: no telemetry, no third-party sync by default, no audio leaves
the host, no secrets in git.

## Trust boundary

```
       │ trust boundary │
─────  │  (Tailscale)   │  ─────
host A │                │ host B
       │                │
       └────────────────┘
              │
              ▼
       Mac mini (voice-server)
              │
              ▼
       Obsidian vault on local disk
```

Inside the boundary:
- the user's Mac mini, MacBook, iPhone, iPad, Watch, AirPods,
- Tailscale tailnet linking them,
- voice-server bound to `100.64.0.0/10` + loopback only.

Outside the boundary:
- Anthropic API (only target the harness contacts; minimum-data sent),
- (opt-in) Cloudflare Tunnel for the Alexa skill,
- (opt-in) GitHub for `08-autoupdate` release feeds,
- (opt-in) YouTube RSS for creator scout.

Default mode: **only Anthropic API** crosses the boundary. Everything
else is opt-in.

## Local-first invariants

1. **Vault lives on local disk only.** No cloud sync configured by
   Ralph (the user may use iCloud / Obsidian Sync / Git themselves;
   their choice).
2. **Embeddings via Ollama on localhost.** No external embedding
   endpoint by default. `embeddings.backend: cognee | letta` are both
   local-first too.
3. **Whisper.cpp on the Mac mini.** Audio NEVER leaves the host. If
   `whisper-cli` is missing, `/ralph/voice` returns 503 instead of
   falling back to a third-party transcription endpoint.
4. **Anthropic SDK only crosses boundary for A/B + summarize calls.**
   The vault content sent is the candidate prompt + the fixture
   variables — bounded by `harness/fixtures/*.yml`. The judge sees
   the output text only; never raw vault content.

## Secret handling

| Secret                    | Lives in                              | Notes                                  |
| ------------------------- | ------------------------------------- | -------------------------------------- |
| `ANTHROPIC_API_KEY`       | `harness/.env` (gitignored)           | required for `harness ab` + `compress` |
| `OLLAMA_BASE_URL`         | env or `config.yml`                   | default `http://localhost:11434`        |
| Tailscale auth key        | not stored by Ralph                   | use Tailscale's own keychain            |
| Cloudflare Tunnel token   | not stored by Ralph                    | configured via Cloudflare's CLI         |
| Alexa skill credentials   | AWS Lambda env vars                   | not in this repo                        |
| User identifiers (email)  | `~/.ralph/secrets.local` (outside repo) | never committed; CI privacy guard       |

The repo includes `.gitignore` entries for `.env`, `*.local.yml`,
`secrets.local`. The CI privacy guard fails the build if any tracked
file contains the user-identifier needle.

## Threat model

| Threat                                          | Impact                                | Mitigation                                |
| ----------------------------------------------- | ------------------------------------- | ----------------------------------------- |
| Malicious prompt injection via inbox            | unauthorized tool call                 | permissions allow/deny; subagent isolation |
| Stolen API key from `.env`                      | model bill                             | `.env` gitignored; key revocation procedure |
| Compromised cron host                            | loop runaway / data exfiltration       | timeout + max_iterations; vault on disk only |
| Cloudflare Tunnel exposure                       | Alexa flow used to issue commands     | Cloudflare Access policy; opt-in only      |
| Vault contains client PII                        | accidental sharing                     | `privacy: client` tag; HIGH-risk on edit   |
| Subagent (Explore) reads sensitive file          | leaks via context window               | subagent results are digests only          |
| Whisper.cpp absent → audio sent elsewhere         | impossible by design                  | `WhisperUnavailable` returns 503; no fallback |
| Replay attack against `/ralph/voice`             | spurious capture                       | Tailscale-only origin guard; future token  |
| Bad actor in tailnet                             | full vault access                      | document but rely on Tailscale ACLs        |
| Malicious autoupdate proposal                    | bad bump applied                       | proposal-only; user merges manually        |
| Memory backend swap to cloud-hosted              | vault content leaves boundary          | `embeddings.backend` requires explicit edit |

## Privacy specifics

- **GDPR-relevant**: client PII may live in the vault under
  `privacy: client`. The chain treats those notes as HIGH-risk for any
  edit. Future business-entity ledgers will track per-subject access.
- **Right to erasure**: archived notes are recoverable; truly erasing a
  note is a HIGH-risk explicit operation (`harness erase --note ...`,
  Round 5+).
- **No analytics, no telemetry.** Ralph never phones home. The Obsidian
  plugin similarly does not send any events.

## Emergency shutdown

In order of escalation:

1. `touch $VAULT/90-Meta/STOP` — pauses every cron firing at next tick.
2. `./scripts/uninstall.sh` — removes all `# RALPH-managed:` cron lines
   / launchd plists.
3. `git reset --hard HEAD~N` — back out recent code changes (HIGH risk;
   the chain's vault content is preserved).
4. Disable Tailscale tailnet — cuts off voice-server reachability from
   any non-loopback device.
5. Stop the voice-server: `launchctl unload
   ~/Library/LaunchAgents/ai.ralph.voice-server.plist`.

## Data map

| Data                              | Location                                   | Privacy             |
| --------------------------------- | ------------------------------------------ | ------------------- |
| Captured thoughts                 | `$VAULT/00-Inbox/voice-<UTC>.md`            | private (default)    |
| Promoted atomic notes             | `$VAULT/30-Notes/`                          | private              |
| Skill files                       | `$VAULT/40-Skills/`                         | private              |
| Prompt files                      | `$VAULT/50-Prompts/`                        | work (default)       |
| User profile                      | `$VAULT/60-Interactions/user-profile.md`    | private              |
| Feedback log                       | `$VAULT/60-Interactions/feedback-log.md`   | private              |
| Logs / metrics                    | `$VAULT/90-Meta/`                           | private              |
| Embeddings                        | `$VAULT/90-Meta/embeddings.db`              | private              |
| Cron log                          | `~/.ralph.log`                               | private              |
| Crontab backup                    | `~/.ralph-crontab.bak.<UTC-ts>`              | private              |
| Anthropic API key                 | `harness/.env`                               | secret               |

The repo itself contains: prompts, scripts, plugin source, harness
source, tests, fixtures, docs. **No vault content. No secrets.**

## Cross-references

- `MEMORY_MODEL.md` — privacy frontmatter field semantics.
- `APPROVAL_GATES.md` — risk classes that map to privacy concerns.
- `BUSINESS_ENTITY_SCOPE.md` — client-data handling rules (Round 3+).
- `VOICE_MULTI_DEVICE_FUTURE_SCOPE.md` — Tailscale + Cloudflare Tunnel
  topology.
- Phase 1-6 reference: `voice-server/voice_server/auth.py` (origin
  guard), `voice-server/voice_server/whisper.py` (local-only),
  `harness/.env.example`.

## Next actions

Run `harness self-test --only privacy` to confirm no user-identifier
strings have leaked into tracked files. Then read `APPROVAL_GATES.md`
to understand the risk-class ladder.
