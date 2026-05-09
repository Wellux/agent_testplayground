"""Whisper transcription wrapper. Uses local `whisper-cli` (whisper.cpp) when
available; otherwise raises a clear error so callers can fall back to a
client-side transcript field instead of audio.

Why local: keeps voice on the user's network. The voice-server NEVER ships
audio to a third-party transcription endpoint.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)


class WhisperUnavailable(RuntimeError):
    """Raised when no local Whisper backend is found."""


def _binary() -> str:
    return os.environ.get("RALPH_WHISPER_BIN", "whisper-cli")


def is_available() -> bool:
    return shutil.which(_binary()) is not None


def transcribe(audio_bytes: bytes, *, language: str = "en") -> str:
    """Transcribe a single in-memory audio buffer. Returns plain text."""
    if not audio_bytes:
        return ""
    if not is_available():
        raise WhisperUnavailable(
            f"local whisper binary {_binary()!r} not found; "
            f"install whisper.cpp (brew install whisper-cpp) or set RALPH_WHISPER_BIN."
        )
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        path = Path(f.name)
    try:
        # whisper.cpp's `whisper-cli` writes <input>.txt next to the input.
        proc = subprocess.run(
            [_binary(), "-l", language, "-otxt", "-of", str(path.with_suffix("")), "-f", str(path)],
            capture_output=True, text=True, check=False, timeout=120,
        )
        if proc.returncode != 0:
            log.warning("whisper-cli failed (rc=%s): %s", proc.returncode, proc.stderr)
            return ""
        out = path.with_suffix(".txt")
        if not out.exists():
            return ""
        return out.read_text(encoding="utf8").strip()
    finally:
        try:
            path.unlink(missing_ok=True)
            path.with_suffix(".txt").unlink(missing_ok=True)
        except OSError:
            pass
