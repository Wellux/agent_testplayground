# Voice / multi-device design (Phase G — sketch only)

This is the architecture sketch for putting the Ralph meta-chain on
the user's phone, watch, AirPods, Mac mini, MacBook, and Alexa. **No code
in this PR** — the implementation will be a separate engagement.

## Goals

- Reach the agent from any device the user owns, hands-free.
- Capture voice → text → an inbox file the chain ingests next morning.
- Privacy-first: voice never leaves the user's network unless they opt in.
- Always-on, always-listening — but only inside the trust boundary.

## Topology

```
   ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ iPhone     │  │ Watch +  │  │ Mac      │  │ Alexa    │
   │ Shortcuts  │  │ AirPods  │  │ Book     │  │ Echo     │
   └─────┬──────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
         │ Tailscale    │ Tailscale   │ Tailscale   │ Lambda → Cloudflare Tunnel
         └──────┬───────┴─────────────┴──────┬──────┘
                ▼                            ▼
          ┌─────────────────────────────────────┐
          │ Mac mini @ 127.0.0.1:7117 (FastAPI) │
          │  - POST /ralph/voice                │
          │  - POST /ralph/run                  │
          │  - GET  /ralph/status               │
          │  Whisper (local) for transcription  │
          └────────────────┬────────────────────┘
                           ▼
                $VAULT/00-Inbox/voice-<ts>.md
                $VAULT/90-Meta/log.md (status reads)
                claude -p (run kicks off ad-hoc Ralph pass)
```

## Components

### Mac mini server

- **FastAPI** + **uvicorn**, listens on `127.0.0.1:7117` (Tailscale-only;
  not exposed on LAN or WAN).
- Endpoints:
  - `POST /ralph/voice`  — multipart audio → Whisper transcribe →
    write `$VAULT/00-Inbox/voice-<UTC-ts>.md` with frontmatter
    `{type: voice-capture, source: <device>}`.
  - `POST /ralph/run`    — body `{axis: "memory"|"skills"|...}` runs the
    matching prompt under the same Ralph loop the cron uses.
  - `GET  /ralph/status` — returns `ralph-state.json` plus the `STOP` flag.
- **Auth**: Tailscale node-ACL only (the Mac mini accepts traffic only from
  named devices in the user's tailnet). No tokens to leak.
- **Whisper**: `whisper.cpp` running locally on the Mac mini's GPU. Models
  pulled once.

### iPhone / iPad

- Apple **Shortcuts** workflows (`.shortcut` files exported separately and
  installed via AirDrop):
  - `Tell Ralph` — dictate, POST audio to `/ralph/voice`.
  - `Ralph Status` — GET `/ralph/status`, render with summary.
- Personal Automation: when on home Wi-Fi or Tailscale, allow Siri to
  invoke `Tell Ralph` via voice keyword.

### Apple Watch + AirPods

- Watch Shortcut mirrors `Tell Ralph` (dictation tap or "Hey Siri, tell
  Ralph …"). AirPods are just the mic; no special integration needed.

### MacBook

- Raycast extension stub (separate repo): hits `/ralph/run` from the
  command launcher. Optional menu-bar app (Tauri) showing status.

### Alexa

- AWS Lambda skill receives intents → posts to a **Cloudflare Tunnel**
  forwarded to the Mac mini's `/ralph/voice`. Tunnel uses Cloudflare Access
  policies to restrict to the skill's source IPs. This is the only path
  that crosses the internet; user can disable it with one toggle.

## Privacy / safety guardrails

- **No user identifier in code or repo**. Any account login (e.g. Google /
  Apple ID) lives in `~/.ralph/secrets.local` (gitignored, outside the repo).
- **Local Whisper**, local Ollama, local SQLite. No third-party API in the
  default path.
- **Trust boundary = Tailscale tailnet** + (optionally) the Cloudflare
  Tunnel for Alexa only.
- **`STOP` file is canonical**: any device can hit `POST /ralph/stop`
  to touch `$VAULT/90-Meta/STOP`; every cron pass and every API run
  honors it.
- **Rate limit**: `/ralph/run` rejects more than 1 invocation per axis per
  5 minutes (the cron handles the schedule; ad-hoc is for follow-ups).

## Build order (when this becomes its own PR)

1. Mac mini server with `/ralph/voice` only (1 day).
2. iPhone Shortcut (`.shortcut` exported, screenshots in docs).
3. Watch + AirPods Shortcut delegation (½ day).
4. Status endpoint + Raycast extension (1 day).
5. Alexa Lambda + Cloudflare Tunnel (1 day, opt-in).

## Out of scope

- "Autonomous business entity" framing — separate engagement (legal,
  durable identity, billing).
- Multi-user vault sharing.
