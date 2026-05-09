"""Launch entrypoint: `python -m voice_server` or `ralph-voice`."""
from __future__ import annotations

import argparse
import logging
import os

import uvicorn

from .app import create_app


def main() -> int:
    parser = argparse.ArgumentParser(prog="ralph-voice")
    parser.add_argument("--host", default=os.environ.get("RALPH_VOICE_HOST", "127.0.0.1"),
                        help="Bind address. 127.0.0.1 means Tailscale-only when bound there.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("RALPH_VOICE_PORT", "7117")))
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level=args.log_level)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
