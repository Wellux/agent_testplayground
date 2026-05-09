"""Compressor — summarize bloated atomic notes; weekly daily-note rollups."""
from __future__ import annotations

import datetime as _dt
import logging
import os
import pathlib
import re
import shutil
from typing import Any

from . import append_metric, load_config, resolve_vault

log = logging.getLogger(__name__)

WEEKLY_DIR = "10-Daily/_weekly"
ARCHIVE_DIR = "_archive"


SUMMARIZE_PROMPT = """\
You are compressing a personal knowledge note. Preserve every claim, link, and
hypothesis; remove rhetorical filler, restate sections as bullets, keep all
[[wikilinks]] intact. Target: ≤ 40% of original token count. Return ONLY the
new body (no commentary, no fences):

{body}
"""


WEEKLY_PROMPT = """\
You are rolling up a week of daily notes into a single weekly summary.
Preserve open hypotheses (`status: open`), carry-over follow-ups, and every
[[wikilink]]. One section per day with a one-line headline; one final
"## Carry-over" section at the bottom. Return ONLY the markdown body:

{body}
"""


def _summarize(text: str, model: str, prompt_tpl: str) -> str:
    """LLM summary via Anthropic SDK; returns "" on failure."""
    try:
        from anthropic import Anthropic
    except ImportError:
        log.warning("anthropic SDK not installed; compress is a no-op")
        return ""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.warning("ANTHROPIC_API_KEY missing; compress is a no-op")
        return ""
    client = Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt_tpl.format(body=text)}],
    )
    parts = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()


def _archive(note_path: pathlib.Path, vault: pathlib.Path) -> pathlib.Path:
    archive_dir = note_path.parent / ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)
    dst = archive_dir / f"{note_path.stem}-original{note_path.suffix}"
    shutil.move(str(note_path), str(dst))
    return dst


_PRESERVE_FM_FIELDS = (
    # Required by ralph_validate_frontmatter.sh.
    "ralph_type",
    "created",
    # Useful to carry forward; the note is still the same memory item,
    # just compressed.
    "memory_layer",
    "memory_temperature",
    "tags",
    "privacy",
    "stability",
    "source",
    "id",
)


def _extract_frontmatter(body: str) -> tuple[dict[str, str], str]:
    """Return (fields, body_after_fm). Tiny single-pass YAML reader —
    only top-level scalar/list-as-string fields. Returns ({}, body) if
    no frontmatter."""
    if not body.startswith("---"):
        return {}, body
    end = body.find("\n---", 3)
    if end < 0:
        return {}, body
    fm_text = body[3:end]
    rest = body[end + 4:]
    fields: dict[str, str] = {}
    for line in fm_text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if ":" not in s:
            continue
        k, _, v = s.partition(":")
        fields[k.strip()] = v.strip()
    return fields, rest


def _write_compressed(
    note_path: pathlib.Path,
    original_relpath: str,
    summary: str,
    preserved: dict[str, str] | None = None,
) -> None:
    archive_link = pathlib.Path(original_relpath).stem
    # Required by ralph_validate_frontmatter.sh: the rewritten note must
    # carry `ralph_type` + `created` (else vault diagnostics fail). We
    # preserve any fields from _PRESERVE_FM_FIELDS that the original
    # had, then layer the compressed_* metadata on top. If the original
    # lacked `ralph_type` (legacy file), default to memory/semantic.
    preserved = preserved or {}
    fm_lines = ["---"]
    fm_lines.append(
        f"ralph_type: {preserved.get('ralph_type', 'memory')}"
    )
    if "memory_layer" in preserved:
        fm_lines.append(f"memory_layer: {preserved['memory_layer']}")
    else:
        fm_lines.append("memory_layer: semantic")
    if "memory_temperature" in preserved:
        fm_lines.append(f"memory_temperature: {preserved['memory_temperature']}")
    fm_lines.append(
        f"created: {preserved.get('created', _dt.date.today().isoformat())}"
    )
    fm_lines.append(f"updated: {_dt.date.today().isoformat()}")
    for k in ("tags", "privacy", "stability", "source", "id"):
        if k in preserved:
            fm_lines.append(f"{k}: {preserved[k]}")
    fm_lines.append(f'compressed_from: "[[{archive_link}]]"')
    fm_lines.append(
        f"compressed_at: {_dt.datetime.now(_dt.UTC).isoformat()}"
    )
    fm_lines.append("---")
    fm_lines.append("")
    body = "\n".join(fm_lines) + f"\n{summary}\n\n> Archived: [[{archive_link}]]\n"
    note_path.write_text(body, encoding="utf8")


def _resolve(note: str, vault: pathlib.Path) -> pathlib.Path:
    p = pathlib.Path(note)
    if not p.is_absolute():
        p = vault / p
    return p


def _compress_one(path: pathlib.Path, vault: pathlib.Path, model: str) -> dict[str, Any] | None:
    body = path.read_text(encoding="utf8", errors="replace")
    tokens_before = max(1, len(body.split()))
    summary = _summarize(body, model, SUMMARIZE_PROMPT)
    if not summary:
        return None
    # Extract the original's frontmatter BEFORE archiving so we can
    # preserve required fields (ralph_type, created, etc) on the
    # rewritten note. Vault validators reject any non-archived file
    # without ralph_type+created.
    fm_fields, _ = _extract_frontmatter(body)
    preserved = {k: v for k, v in fm_fields.items() if k in _PRESERVE_FM_FIELDS}
    archived = _archive(path, vault)
    _write_compressed(path, str(archived.relative_to(vault)), summary, preserved)
    tokens_after = max(1, len(summary.split()))
    log.info("compressed %s (%d → %d words)", path, tokens_before, tokens_after)
    return {
        "axis": "compress",
        "action": "atomic",
        "note": str(path.relative_to(vault)),
        "tokens_before": tokens_before,
        "tokens_after": tokens_after,
        "ratio": tokens_after / tokens_before,
    }


def _weekly_rollup(iso_week: str, vault: pathlib.Path, model: str) -> dict[str, Any] | None:
    m = re.fullmatch(r"(\d{4})-W(\d{2})", iso_week)
    if not m:
        log.error("bad ISO week: %s (expected YYYY-Www)", iso_week)
        return None
    year, week = int(m.group(1)), int(m.group(2))

    daily = vault / "10-Daily"
    if not daily.exists():
        return None

    contributing: list[pathlib.Path] = []
    bodies: list[str] = []
    for p in sorted(daily.glob("*.md")):
        try:
            d = _dt.date.fromisoformat(p.stem)
        except ValueError:
            continue
        iso_year, iso_week_n, _ = d.isocalendar()
        if iso_year != year or iso_week_n != week:
            continue
        text = p.read_text(encoding="utf8", errors="replace")
        if "weekly_rollup_id:" in text:
            continue
        contributing.append(p)
        bodies.append(f"## {p.stem}\n\n{text}\n")

    if not contributing:
        return None

    summary = _summarize("\n".join(bodies), model, WEEKLY_PROMPT)
    if not summary:
        return None

    out = vault / WEEKLY_DIR / f"{iso_week}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"---\nid: {iso_week}\ntype: weekly-rollup\ncreated: {_dt.date.today().isoformat()}\n"
        f"days: {len(contributing)}\n---\n\n# Week {iso_week}\n\n{summary}\n",
        encoding="utf8",
    )

    for p in contributing:
        text = p.read_text(encoding="utf8", errors="replace")
        if text.startswith("---"):
            new = re.sub(r"^---", f"---\nweekly_rollup_id: {iso_week}", text, count=1)
        else:
            new = f"---\nweekly_rollup_id: {iso_week}\n---\n\n{text}"
        p.write_text(new, encoding="utf8")

    tokens_before = sum(max(1, len(b.split())) for b in bodies)
    tokens_after = max(1, len(summary.split()))
    log.info("weekly rollup %s — %d days, %d → %d words", iso_week, len(contributing), tokens_before, tokens_after)
    return {
        "axis": "compress",
        "action": "weekly",
        "week": iso_week,
        "days": len(contributing),
        "tokens_before": tokens_before,
        "tokens_after": tokens_after,
    }


def run(
    *,
    note: str | None,
    older_than: str | None,
    weekly: bool,
    iso_week: str | None,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    cfg = load_config(config_path)
    vault = resolve_vault(vault_override, cfg)
    model = cfg.get("model", "claude-sonnet-4-6")

    if weekly:
        if not iso_week:
            log.error("--weekly requires --iso-week YYYY-Www")
            return 64
        row = _weekly_rollup(iso_week, vault, model)
        if row:
            append_metric(vault, row)
            return 0
        return 1

    if note:
        path = _resolve(note, vault)
        row = _compress_one(path, vault, model)
        if row:
            append_metric(vault, row)
            return 0
        return 1

    # --older-than 7d (default scan)
    cutoff = None
    if older_than:
        m = re.fullmatch(r"(\d+)d", older_than.strip())
        if m:
            cutoff = _dt.datetime.now().timestamp() - int(m.group(1)) * 86400

    n = 0
    for p in (vault / "30-Notes").rglob("*.md"):
        if "/_archive/" in str(p):
            continue
        if cutoff and p.stat().st_mtime > cutoff:
            continue
        body = p.read_text(encoding="utf8", errors="replace")
        if len(body.split()) * 1.3 < 4000:
            continue
        row = _compress_one(p, vault, model)
        if row:
            append_metric(vault, row)
            n += 1
        if n >= 5:
            break

    log.info("compressed %d note(s)", n)
    return 0
