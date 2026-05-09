---
ralph_type: memory
memory_layer: raw
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Voice/Shortcut/Alexa landings — auto-populated by voice-server."
---

# Voice Capture Inbox

This file is **read-only via this view**. The actual captures live as
discrete `voice-<UTC-ts>.md` files in `00-Inbox/`, written by the
`voice-server`'s `POST /ralph/voice` endpoint.

The morning memory pass promotes them and moves originals to
`00-Inbox/_processed/`. By 02:30 UTC any voice from yesterday is
processed.

## Recent voice captures

```dataview
LIST
  source AS "From"
FROM "00-Inbox"
WHERE type = "voice-capture"
SORT file.cday DESC
LIMIT 20
```

(If you don't have Dataview installed, just browse `00-Inbox/voice-*.md`
in Obsidian's file explorer.)

## Cross-references

- `voice-server/voice_server/app.py` — the FastAPI handler.
- `voice-server/shortcuts/tell-ralph.shortcut.json` — iOS Shortcut spec.
- `voice-server/alexa-skill/lambda_function.py` — Alexa text → POST.
- `docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md` — full architecture.
