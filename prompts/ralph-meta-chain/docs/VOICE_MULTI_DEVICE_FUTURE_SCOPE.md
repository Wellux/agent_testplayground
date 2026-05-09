# VOICE_MULTI_DEVICE_FUTURE_SCOPE.md

## Purpose

The architecture for putting Ralph on the user's iPhone, iPad, Watch,
AirPods, MacBook, Mac mini, and Alexa. The Phase 1-6 reference
implementation already ships `voice-server/` (FastAPI app) plus iOS
Shortcut JSON / Alexa Lambda / Raycast extension specs. The master spec
treats voice/multi-device as **deferred until separately authorized**.
This doc keeps the canonical design here; activation stays user-
initiated.

## Topology

```
   ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ iPhone     │  │ Watch +  │  │ MacBook  │  │ Alexa    │
   │ Shortcuts  │  │ AirPods  │  │ Raycast  │  │ Echo     │
   └─────┬──────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
         │ Tailscale    │ Tailscale   │ Tailscale   │ Lambda → Cloudflare Tunnel (opt-in)
         └──────┬───────┴─────────────┴──────┬──────┘
                ▼                            ▼
          ┌─────────────────────────────────────┐
          │ Mac mini @ 127.0.0.1:7117 (FastAPI) │
          │  POST /ralph/voice                  │
          │  POST /ralph/run                    │
          │  POST /ralph/stop                   │
          │  POST /ralph/resume                 │
          │  GET  /ralph/status                 │
          │  GET  /healthz                      │
          │  Whisper.cpp (local) for ASR        │
          └────────────────┬────────────────────┘
                           ▼
                $VAULT/00-Inbox/voice-<UTC>.md
                $VAULT/90-Meta/log.md (status)
                claude -p (run kicks ad-hoc Ralph pass)
```

## Components

### Mac mini server (FastAPI)

Phase 1-6 reference: `voice-server/voice_server/app.py`.

- Bound to `127.0.0.1:7117` by default (Tailscale-only).
- Origin guard: `100.64.0.0/10` (Tailscale CGNAT) + loopback.
- `/healthz` is the only unauth'd endpoint (for launchd KeepAlive).
- Whisper.cpp local-only; missing binary = HTTP 503.

### Apple Shortcuts

JSON specs at `voice-server/shortcuts/`:

- `tell-ralph.shortcut.json` — Dictate Text → POST `/ralph/voice` →
  notification. Trigger: Siri / Watch face / iPhone / iPad.
- `ralph-status.shortcut.json` — GET `/ralph/status` → menu chooser
  with Pause / Resume / Run-axis options.

User imports via Shortcuts app; the JSON is reproducible documentation,
not an installable artifact (Apple Shortcuts use signed plists).

### AirPods + Watch

Audio capture surfaces. Watch dictation hits the `tell-ralph` shortcut;
AirPods are just the mic, no special integration. Wake-phrase support
is intentionally out of scope (privacy + accidental-activation
concerns).

### MacBook (Raycast extension)

Stub at `voice-server/raycast-stub/`:
- Capture Thought → text field → POST `/ralph/voice`.
- Ralph Status → list view of last-run-per-axis.
- Run Axis → axis picker → POST `/ralph/run`.

The user runs `ray develop` to install; CI does not build Raycast.

### Alexa skill

Lambda + skill manifest at `voice-server/alexa-skill/`:
- Amazon transcribes on-device; Lambda receives **text only**.
- Lambda forwards to the Mac mini via Cloudflare Tunnel.
- Audio NEVER leaves Amazon → Lambda flow; never reaches the Mac
  mini's audio path.

Cloudflare Tunnel + Cloudflare Access policy is the only WAN path. The
user can disable Alexa entirely and the chain stays local-only.

## Phased activation plan

The master spec mandates phased rollout. Each phase requires explicit
authorization separate from this round.

| Phase | Capability                                                          | Status |
| ----- | ------------------------------------------------------------------- | ------ |
| 1     | Manual Apple Shortcut appends Markdown to Obsidian inbox             | shipped (reference impl) |
| 2     | Local webhook with token + audit log                                  | partial — Tailscale guard exists; token planned |
| 3     | Authenticated command router                                          | not yet |
| 4     | Limited safe commands (Pause / Resume / Status)                       | shipped |
| 5     | Approval-gated remote execution (Run axis)                            | shipped behind Tailscale only |
| 6     | Optional continuous agent daemon                                       | DEFERRED — needs threat model + separate scoping |

## Risk analysis

| Risk                                                | Mitigation                                            |
| --------------------------------------------------- | ----------------------------------------------------- |
| Privacy leakage (audio over network)                 | local Whisper.cpp; 503 if missing                      |
| Accidental activation (wake phrase)                  | no wake phrases; user-initiated shortcut only          |
| Unauthorized command injection                       | Tailscale ACLs; origin guard CIDR                       |
| Family/guest voice confusion                         | per-device shortcut; no cross-device speaker recognition |
| Device compromise                                    | Tailscale kills traffic from non-tailnet devices         |
| Cloud relay exposure (Alexa)                         | Cloudflare Access; opt-in only                         |
| GDPR / client data via Alexa                         | document explicit prohibition; never auto-route        |
| Replay attack                                        | future signed-JWT token (Round 6+)                      |
| Always-listening daemon                              | DEFERRED; never enabled without separate scoping       |
| Remote code execution via `/ralph/run`               | axis whitelist; rate limit; CRITICAL gate              |

## Consent model

- **Capture is the default consent.** A `tell-ralph` shortcut invocation
  IS the user's explicit consent for that capture.
- **Recipient consent is separate.** If a captured thought references
  another person, the user is responsible for whether that's
  privacy-appropriate. Ralph adds `privacy: private` by default; the
  user can re-tag.
- **No silent recording.** Whisper runs only on shortcut invocation.

## Audit

Every voice-server endpoint logs to `~/.ralph-voice.log`:

```
2026-05-09T12:00:00 source=ios-shortcut text=... wrote=00-Inbox/voice-...md
```

Future round: per-source audit (Watch vs iPhone vs Alexa) + per-call
SHA256 hash for integrity.

## Emergency stop

In order:

1. `touch $VAULT/90-Meta/STOP` — pauses every cron firing.
2. `POST /ralph/stop` — same effect, from any device in the tailnet.
3. `launchctl unload ~/Library/LaunchAgents/ai.ralph.voice-server.plist`
   — kills the FastAPI server.
4. `tailscale down` — cuts off cross-device traffic entirely.
5. Disable the Alexa skill in the Alexa app — kills Cloudflare path.

## Safety notes

- **Default off the WAN.** Alexa is the only WAN path and is opt-in.
- **Local Whisper or 503.** No fallback to a third-party transcription
  endpoint, ever.
- **Phase 6 (always-on agent daemon) requires separate scoping.** Don't
  enable it casually. Threat-model exercise + privacy review first.
- **The voice-server is HIGH-risk infrastructure.** Treat its config
  edits accordingly.

## Cross-references

- `ARCHITECTURE.md` — where voice-server sits in the system.
- `SECURITY_PRIVACY.md` — full threat model.
- `APPROVAL_GATES.md` — class assignments for each endpoint.
- Phase 1-6 reference: `voice-server/voice_server/app.py`,
  `voice-server/voice_server/auth.py`,
  `voice-server/voice_server/whisper.py`,
  `voice-server/shortcuts/`, `voice-server/alexa-skill/`,
  `voice-server/raycast-stub/`.

## Next actions

If you want voice today: read `voice-server/README.md` and run the
FastAPI server on the Mac mini behind Tailscale. Skip Alexa unless you
specifically want a WAN path. Phase 6 (always-on daemon) stays
deferred until a separate scoping conversation.
