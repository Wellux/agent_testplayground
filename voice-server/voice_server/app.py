"""FastAPI app — voice + dispatch endpoints.

Endpoints:
  POST /ralph/voice    multipart audio (field=audio) OR JSON {"text":"..."} → 00-Inbox/voice-<ts>.md
  POST /ralph/run      JSON {"axis": "memory"} → run a single axis pass via claude -p
  POST /ralph/stop     create $VAULT/90-Meta/STOP (pause the chain)
  POST /ralph/resume   remove the STOP file
  GET  /ralph/status   read ralph-state.json + STOP presence + tool availability
  GET  /healthz        liveness for the launchd KeepAlive watcher
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import pathlib
import shutil
from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from .auth import origin_guard
from .config import claude_bin, load_ralph_config, vault_path
from .runner import AXIS_TO_PROMPT, run_axis, stop_file_path
from .whisper import WhisperUnavailable, is_available as whisper_available, transcribe

log = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="ralph-voice-server", version="0.1.0")

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ralph/status", dependencies=[Depends(origin_guard)])
    async def status() -> JSONResponse:
        cfg = load_ralph_config()
        try:
            vault = vault_path(cfg)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

        state_p = vault / "90-Meta" / "ralph-state.json"
        state: dict[str, Any] = {}
        if state_p.exists():
            try:
                state = json.loads(state_p.read_text(encoding="utf8"))
            except json.JSONDecodeError:
                state = {"_error": "state file malformed"}
        return JSONResponse(content={
            "vault": str(vault),
            "stopped": stop_file_path().exists(),
            "state": state,
            "tools": {
                "claude": shutil.which(claude_bin()) is not None,
                "whisper": whisper_available(),
            },
        })

    @app.post("/ralph/stop", dependencies=[Depends(origin_guard)])
    async def stop() -> dict[str, str]:
        f = stop_file_path()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("stopped via voice-server\n")
        return {"stopped": "true"}

    @app.post("/ralph/resume", dependencies=[Depends(origin_guard)])
    async def resume() -> dict[str, str]:
        f = stop_file_path()
        try:
            f.unlink()
            return {"resumed": "true"}
        except FileNotFoundError:
            return {"resumed": "noop"}

    @app.post("/ralph/run", dependencies=[Depends(origin_guard)])
    async def run(payload: dict[str, Any]) -> JSONResponse:
        axis = str(payload.get("axis", "")).strip()
        if axis not in AXIS_TO_PROMPT:
            raise HTTPException(status_code=400, detail=f"axis must be one of {list(AXIS_TO_PROMPT)}")
        max_it = int(payload.get("max_iterations", 8))
        timeout_s = int(payload.get("timeout_s", 1500))
        result = await run_axis(axis, max_iterations=max_it, hard_timeout_s=timeout_s)
        return JSONResponse(content={
            "axis": result.axis,
            "exit_code": result.exit_code,
            "iterations": result.iterations,
            "promise_seen": result.promise_seen,
            "tail": result.tail,
        })

    @app.post("/ralph/voice", dependencies=[Depends(origin_guard)])
    async def voice(
        audio: UploadFile | None = File(default=None),
        text: str | None = Form(default=None),
        source: str = Form(default="unknown"),
    ) -> JSONResponse:
        cfg = load_ralph_config()
        vault = vault_path(cfg)
        inbox = vault / "00-Inbox"
        inbox.mkdir(parents=True, exist_ok=True)

        body_text = ""
        used_whisper = False
        if text:
            body_text = text.strip()
        elif audio is not None:
            data = await audio.read()
            try:
                body_text = transcribe(data)
                used_whisper = True
            except WhisperUnavailable as e:
                raise HTTPException(status_code=503, detail=str(e)) from e
            if not body_text:
                raise HTTPException(status_code=422, detail="transcription empty")
        else:
            raise HTTPException(status_code=400, detail="send `audio` (multipart) or `text` (form field)")

        ts = _dt.datetime.now(_dt.UTC).strftime("%Y%m%dT%H%M%SZ")
        out = inbox / f"voice-{ts}.md"
        frontmatter = (
            f"---\n"
            f"id: voice-{ts}\n"
            f"type: voice-capture\n"
            f"source: {source}\n"
            f"used_whisper: {str(used_whisper).lower()}\n"
            f"created: {_dt.date.today().isoformat()}\n"
            f"tags: [voice, '#trending']\n"
            f"---\n\n"
        )
        out.write_text(frontmatter + body_text + "\n", encoding="utf8")
        return JSONResponse(content={"wrote": str(out.relative_to(vault)), "used_whisper": used_whisper})

    return app
