"""Alexa skill Lambda — translates ASK intents into voice-server calls.

Deploy as an AWS Lambda; set RALPH_VOICE_URL to the Cloudflare-Tunnel
hostname pointed at your Mac mini voice-server. The skill itself never
sees audio; Alexa transcribes and we forward the text. Audio paths are
reserved for the iOS Shortcut + AirPods flow.

Env vars (in Lambda console):
  RALPH_VOICE_URL    e.g. https://ralph.<your-cf-tunnel-hostname>
  RALPH_VOICE_TOKEN  optional bearer token if you front the tunnel with
                     Cloudflare Access — added as `Authorization: Bearer …`.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def _post(path: str, body: dict[str, Any] | None = None, *, form: bool = False) -> dict[str, Any]:
    base = os.environ.get("RALPH_VOICE_URL")
    if not base:
        raise RuntimeError("RALPH_VOICE_URL not set")
    headers = {"Accept": "application/json"}
    token = os.environ.get("RALPH_VOICE_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if form:
        data = urllib.parse.urlencode(body or {}).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    else:
        data = json.dumps(body or {}).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{base.rstrip('/')}{path}", data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf8") or "{}")


def _get(path: str) -> dict[str, Any]:
    base = os.environ.get("RALPH_VOICE_URL")
    if not base:
        raise RuntimeError("RALPH_VOICE_URL not set")
    headers = {"Accept": "application/json"}
    token = os.environ.get("RALPH_VOICE_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{base.rstrip('/')}{path}", headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf8") or "{}")


def _say(text: str) -> dict[str, Any]:
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": True,
        },
    }


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    request = event.get("request", {})
    rtype = request.get("type")

    if rtype == "LaunchRequest":
        return _say("Ralph here. Say 'remember' followed by your thought, or ask for status.")

    if rtype == "IntentRequest":
        intent = request.get("intent", {})
        name = intent.get("name")

        if name == "CaptureIntent":
            slots = intent.get("slots", {})
            thought = (slots.get("Thought") or {}).get("value", "").strip()
            if not thought:
                return _say("I didn't catch the thought — try again with 'remember' followed by what you want to capture.")
            try:
                _post("/ralph/voice", {"text": thought, "source": "alexa"}, form=True)
                return _say("Captured.")
            except urllib.error.URLError as e:
                return _say(f"Couldn't reach the brain: {e.reason}.")

        if name == "StatusIntent":
            try:
                data = _get("/ralph/status")
                stopped = data.get("stopped")
                state = data.get("state", {})
                count = sum(
                    1 for v in state.values()
                    if isinstance(v, dict) and v.get("status") == "COMPLETE"
                )
                paused = "Paused. " if stopped else ""
                return _say(f"{paused}{count} axes complete today.")
            except urllib.error.URLError as e:
                return _say(f"Couldn't reach the brain: {e.reason}.")

        if name == "PauseIntent":
            _post("/ralph/stop")
            return _say("Paused.")

        if name == "ResumeIntent":
            _post("/ralph/resume")
            return _say("Resumed.")

        if name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
            return _say("Bye.")

        if name == "AMAZON.HelpIntent":
            return _say("Say 'remember' followed by your thought, or ask for status, or say pause or resume.")

    return _say("I didn't understand. Try 'remember' followed by your thought.")
