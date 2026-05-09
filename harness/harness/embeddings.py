"""Embeddings — Ollama → sqlite-vec + FTS5 (obra/knowledge-graph schema)."""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import pathlib
import re
import sqlite3
import struct
from typing import Any

import httpx

from . import load_config, resolve_vault
from .memory_backends import select_backend

log = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "nomic-embed-text"


def _parse_since(spec: str) -> int:
    m = re.fullmatch(r"(\d+)([smhd])", spec.strip())
    if not m:
        raise ValueError(f"bad --since spec: {spec!r} (use e.g. '2h', '30m', '1d')")
    n = int(m.group(1))
    return n * {"s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)]


def _connect(db_path: pathlib.Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    try:
        import sqlite_vec  # type: ignore[import-untyped]
        sqlite_vec.load(conn)
    except Exception as e:  # pragma: no cover
        log.warning("sqlite-vec load failed (%s); falling back to BLOB storage only", e)
    conn.enable_load_extension(False)

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS notes(
            id        TEXT PRIMARY KEY,
            path      TEXT NOT NULL,
            mtime     INTEGER NOT NULL,
            tokens    INTEGER NOT NULL,
            updated   TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_notes USING fts5(
            id UNINDEXED, body, tokenize='unicode61'
        );
    """)
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS vec_notes USING vec0("
            "id TEXT PRIMARY KEY, embedding float[768]"
            ")"
        )
    except sqlite3.OperationalError as e:  # pragma: no cover
        log.warning("could not create vec0 table (%s); semantic queries will degrade", e)
    return conn


def _ollama_embed(text: str, base_url: str, model: str) -> list[float]:
    r = httpx.post(
        f"{base_url}/api/embeddings",
        json={"model": model, "prompt": text},
        timeout=30.0,
    )
    r.raise_for_status()
    body = r.json()
    return list(body["embedding"])


def _vec_blob(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _id_for(path: pathlib.Path, vault: pathlib.Path) -> str:
    return str(path.relative_to(vault))


def _iter_notes(vault: pathlib.Path, *, since_seconds: int | None) -> list[pathlib.Path]:
    cutoff = _dt.datetime.now().timestamp() - since_seconds if since_seconds else None
    out: list[pathlib.Path] = []
    for root in ("00-Inbox", "10-Daily", "20-MOCs", "30-Notes", "40-Skills", "50-Prompts", "60-Interactions"):
        base = vault / root
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            if "/_archive/" in str(p) or "/_processed/" in str(p) or "/_rejected/" in str(p):
                continue
            if cutoff and p.stat().st_mtime < cutoff:
                continue
            out.append(p)
    return out


def _embed_one(conn: sqlite3.Connection, path: pathlib.Path, vault: pathlib.Path, base_url: str, model: str) -> None:
    body = path.read_text(encoding="utf8", errors="replace")
    if not body.strip():
        return
    vec = _ollama_embed(body, base_url, model)
    nid = _id_for(path, vault)
    mtime = int(path.stat().st_mtime)
    tokens = max(1, len(body.split()))
    updated = _dt.datetime.now(_dt.UTC).isoformat()

    conn.execute(
        "INSERT OR REPLACE INTO notes(id,path,mtime,tokens,updated) VALUES (?,?,?,?,?)",
        (nid, str(path), mtime, tokens, updated),
    )
    conn.execute("DELETE FROM fts_notes WHERE id = ?", (nid,))
    conn.execute("INSERT INTO fts_notes(id, body) VALUES (?, ?)", (nid, body))
    try:
        conn.execute("INSERT OR REPLACE INTO vec_notes(id, embedding) VALUES (?, ?)", (nid, _vec_blob(vec)))
    except sqlite3.OperationalError:  # pragma: no cover
        pass
    conn.commit()


def _open(config_path: str | None, vault_override: str | None) -> tuple[pathlib.Path, sqlite3.Connection, str, str]:
    cfg = load_config(config_path)
    vault = resolve_vault(vault_override, cfg)
    em = cfg.get("embeddings", {}) or {}
    base_url = os.environ.get("OLLAMA_BASE_URL") or em.get("base_url") or DEFAULT_OLLAMA_URL
    model = em.get("model") or DEFAULT_MODEL
    db = vault / (em.get("db_path") or "90-Meta/embeddings.db")
    conn = _connect(db)
    return vault, conn, base_url, model


def _resolve_backend(cfg: dict[str, Any], vault: pathlib.Path, model: str):
    em = cfg.get("embeddings", {}) or {}
    backend_name = os.environ.get("RALPH_MEM_BACKEND") or em.get("backend")
    return select_backend(backend_name or "", vault=vault, model=model)


def run_embed(
    *,
    note: str | None,
    full_vault: bool,
    since: str | None,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    vault, conn, base_url, model = _open(config_path, vault_override)
    backend = _resolve_backend(load_config(config_path), vault, model)

    paths: list[pathlib.Path]
    if note:
        p = (vault / note) if not pathlib.Path(note).is_absolute() else pathlib.Path(note)
        paths = [p]
    else:
        seconds = _parse_since(since) if since else None
        paths = _iter_notes(vault, since_seconds=seconds if not full_vault else None)

    n = 0
    for p in paths:
        if not p.exists():
            log.warning("skip missing %s", p)
            continue
        try:
            if backend is not None:
                backend.embed_one(p, vault)  # type: ignore[attr-defined]
            else:
                _embed_one(conn, p, vault, base_url, model)
            n += 1
        except Exception as e:
            log.warning("embed failed for %s: %s", p, e)
    log.info("embedded %d note(s) (backend=%s)", n, getattr(backend, "name", "local-sqlite-vec"))
    return 0 if n > 0 or note is None else 1


def run_query(
    *,
    query: str,
    k: int,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    vault, conn, base_url, model = _open(config_path, vault_override)
    vec = _ollama_embed(query, base_url, model)

    fts_rows: list[tuple[str, float]] = []
    try:
        cur = conn.execute(
            "SELECT id, bm25(fts_notes) AS s FROM fts_notes WHERE fts_notes MATCH ? ORDER BY s LIMIT ?",
            (query, k * 2),
        )
        fts_rows = [(r[0], -float(r[1])) for r in cur]
    except sqlite3.OperationalError:
        pass

    vec_rows: list[tuple[str, float]] = []
    try:
        cur = conn.execute(
            "SELECT id, distance FROM vec_notes WHERE embedding MATCH ? ORDER BY distance LIMIT ?",
            (_vec_blob(vec), k * 2),
        )
        vec_rows = [(r[0], -float(r[1])) for r in cur]
    except sqlite3.OperationalError:
        pass

    rrf: dict[str, float] = {}
    for rank, (nid, _) in enumerate(fts_rows):
        rrf[nid] = rrf.get(nid, 0.0) + 1.0 / (60 + rank)
    for rank, (nid, _) in enumerate(vec_rows):
        rrf[nid] = rrf.get(nid, 0.0) + 1.0 / (60 + rank)
    ranked = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:k]

    if not ranked:
        print("(no results)")
        return 1

    print(f"# Query: {query}\n")
    for nid, sc in ranked:
        cur = conn.execute("SELECT path FROM notes WHERE id = ?", (nid,))
        row = cur.fetchone()
        path = row[0] if row else nid
        slug = pathlib.Path(nid).stem
        print(f"- [[{slug}]] · {path}  (rrf={sc:.3f})")
    return 0


__all__ = ["run_embed", "run_query"]
