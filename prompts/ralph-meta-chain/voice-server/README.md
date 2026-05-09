# ralph-voice-server

FastAPI dispatcher that turns voice / text from any of the user's devices
into raw inbox captures, plus an HTTP front-door for the same axis runs the
cron jobs perform. Designed to live on the user's Mac mini, behind Tailscale.

## Endpoints

| Method | Path             | Body                                          | Result                                         |
| ------ | ---------------- | --------------------------------------------- | ---------------------------------------------- |
| POST   | `/ralph/voice`   | multipart `audio=…` OR form `text=…`, `source=…`| writes `$VAULT/00-Inbox/voice-<UTC>.md`        |
| POST   | `/ralph/run`     | `{"axis": "memory"}` (axis ∈ all 8 prompts)   | runs that axis under the Ralph loop            |
| POST   | `/ralph/stop`    | —                                             | touches `$VAULT/90-Meta/STOP`                  |
| POST   | `/ralph/resume`  | —                                             | removes the STOP file                          |
| GET    | `/ralph/status`  | —                                             | returns `ralph-state.json`, STOP, tool checks  |
| GET    | `/healthz`       | —                                             | `{"status":"ok"}` (no auth, for KeepAlive)     |

All endpoints (except `/healthz`) require the request to come from a
trusted subnet (`100.64.0.0/10` Tailscale CGNAT + loopback by default;
override with `RALPH_TRUSTED_SUBNETS`).

## Run

```bash
cd voice-server
uv venv && uv pip install -e .
RALPH_CONFIG=../prompts/ralph-meta-chain/config.yml \
  ralph-voice --host 127.0.0.1 --port 7117
```

For Mac mini use, run under launchd as a separate plist (template below)
so it restarts on crash and survives reboots.

```xml
<!-- ~/Library/LaunchAgents/ai.ralph.voice-server.plist -->
<plist version="1.0"><dict>
  <key>Label</key><string>ai.ralph.voice-server</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/ralph-voice</string>
    <string>--host</string><string>0.0.0.0</string>
    <string>--port</string><string>7117</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>EnvironmentVariables</key><dict>
    <key>VAULT</key><string>/Users/me/Obsidian/SecondBrain</string>
    <key>RALPH_CONFIG</key><string>/Users/me/code/agent_testplayground/prompts/ralph-meta-chain/config.yml</string>
  </dict>
</dict></plist>
```

## Whisper

`/ralph/voice` with audio expects `whisper-cli` (whisper.cpp) on PATH.
Install on macOS:

```bash
brew install whisper-cpp
ralph-voice ...    # auto-detected
```

If audio comes in but whisper isn't available, the server returns 503
with a message. **Audio never leaves the host** — there is no fallback
to a third-party transcription endpoint.

## Privacy

- Default bind is loopback. Tailscale tunnels traffic from your other
  devices to `100.x.y.z` addresses, which the origin guard accepts.
- No secrets are stored or required by this server. The Anthropic API
  key the harness uses lives in `harness/.env`, not here.
