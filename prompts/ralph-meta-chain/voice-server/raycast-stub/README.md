# Raycast extension stub — Ralph

Three commands surface the same operations the Obsidian plugin and
Apple Shortcuts expose, but from your Mac launcher.

## Commands

- **Capture Thought** — text field → `POST /ralph/voice` (form `text=…`).
- **Ralph Status** — `GET /ralph/status` → list view with per-axis status.
- **Run Axis** — pick from the 8 axes → `POST /ralph/run`.

## Setup

```bash
cd voice-server/raycast-stub
npm install
ray develop
```

Then set the `voiceUrl` preference to your Mac mini's Tailscale URL.

## Why a stub?

The full Raycast extension wants their toolchain (`ray develop`) to live
outside CI; we ship the `package.json` + sources so anyone who has
Raycast can `ray develop` immediately. We do not run a Raycast build in
this repo's CI.
