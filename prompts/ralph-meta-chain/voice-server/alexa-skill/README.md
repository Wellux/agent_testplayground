# Alexa skill — Ralph

Custom Alexa skill that posts the user's spoken thought to the Mac mini
voice-server. The Lambda itself never receives audio; Amazon transcribes
on-device and Alexa forwards the text via the intent slot.

## Files

- `skill.json` — interaction model + manifest. Drop into Alexa Developer
  Console under "JSON Editor" and "Build → Custom".
- `lambda_function.py` — handler. Zip alongside no other files (no
  third-party deps; stdlib only) and upload to AWS Lambda.

## Privacy / network path

```
Echo  ──Amazon ASR──►  Lambda  ──HTTPS──►  Cloudflare Tunnel  ──►  Mac mini  voice-server
                       (text)              (token-gated)            127.0.0.1:7117
```

Audio NEVER leaves Amazon. Text is the only payload. The tunnel is
opt-in: skip Alexa entirely and the chain stays local-only.

## Env vars (Lambda)

| Var                 | Purpose                                                          |
| ------------------- | ---------------------------------------------------------------- |
| `RALPH_VOICE_URL`   | e.g. `https://ralph.<your-tunnel-host>`                          |
| `RALPH_VOICE_TOKEN` | optional bearer (Cloudflare Access)                              |

## Test phrases

- "Alexa, tell Ralph my idea is to use sqlite-vec for embeddings."
- "Alexa, ask Ralph for status."
- "Alexa, tell Ralph to pause."
- "Alexa, tell Ralph to resume."
