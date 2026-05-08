"""GitHub trending ingest — pulls per-topic trending repos and writes one inbox file."""
from __future__ import annotations

import datetime as _dt
import logging
import pathlib
import re
import time
from typing import Iterable

import httpx

from . import load_config, resolve_vault

log = logging.getLogger(__name__)

UA = "ralph-meta-chain/0.1 (+https://github.com/Wellux/agent_testplayground)"
TRENDING_URL = "https://github.com/trending/{topic}?since=daily"

_REPO_RE = re.compile(
    r'<h2[^>]*>\s*<a\s+href="/(?P<full>[^/"]+/[^"]+)"',
    re.S,
)
_DESC_RE = re.compile(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>\s*(?P<desc>.*?)</p>', re.S)
_STARS_RE = re.compile(r'(\d[\d,]*)\s*stars\s*today', re.I)


def _scrape_topic(topic: str, *, max_repos: int, timeout: float = 30.0) -> list[dict]:
    url = TRENDING_URL.format(topic=topic.strip())
    try:
        r = httpx.get(url, timeout=timeout, headers={"User-Agent": UA})
        r.raise_for_status()
    except httpx.HTTPError as e:
        log.warning("trending fetch failed for %s: %s", topic, e)
        return []
    html = r.text
    out: list[dict] = []
    for m in _REPO_RE.finditer(html):
        full = m.group("full").strip()
        # Slice forward to find this repo's description / stars-today.
        chunk = html[m.end(): m.end() + 4000]
        desc_m = _DESC_RE.search(chunk)
        desc = re.sub(r"\s+", " ", desc_m.group("desc")).strip() if desc_m else ""
        stars_m = _STARS_RE.search(chunk)
        stars_today = int(stars_m.group(1).replace(",", "")) if stars_m else 0
        out.append({
            "topic": topic,
            "full": full,
            "url": f"https://github.com/{full}",
            "desc": desc[:240],
            "stars_today": stars_today,
        })
        if len(out) >= max_repos:
            break
    return out


def _seen_urls(vault: pathlib.Path) -> set[str]:
    seen: set[str] = set()
    for root in ("00-Inbox", "30-Notes"):
        base = vault / root
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            try:
                for line in p.read_text(encoding="utf8", errors="replace").splitlines():
                    if "https://github.com/" in line:
                        for token in re.findall(r"https://github\.com/[^\s)\"]+", line):
                            seen.add(token.rstrip("/"))
            except OSError:
                continue
    return seen


def _render(date: str, topics: list[str], rows: Iterable[dict], seen: set[str]) -> str:
    yaml_topics = ", ".join(topics)
    lines: list[str] = []
    lines.append("---")
    lines.append(f"id: {date.replace('-', '')}-trending")
    lines.append("type: research")
    lines.append(f"created: {date}")
    lines.append(f"topics: [{yaml_topics}]")
    lines.append("source: github-trending")
    lines.append("---")
    lines.append("")
    lines.append(f"# GitHub trending — {date}")
    lines.append("")
    new_count = 0
    for r in rows:
        seen_marker = " (seen)" if r["url"].rstrip("/") in seen else ""
        if not seen_marker:
            new_count += 1
        lines.append(f"## {r['full']} — ★ +{r['stars_today']} today{seen_marker}")
        lines.append(f"- Topic: {r['topic']}")
        lines.append(f"- Url: {r['url']}")
        if r["desc"]:
            lines.append(f"- Summary: {r['desc']}")
        tags = "[#trending"
        slug = re.sub(r"[^a-z0-9]+", "-", r["topic"].lower()).strip("-")
        if slug:
            tags += f", #{slug}"
        tags += "]"
        lines.append(f"- Tags: {tags}")
        lines.append("")
    lines.append(f"_new={new_count} total={len(list(rows)) if False else new_count + (len(seen) & 0)}_")
    return "\n".join(lines).rstrip() + "\n"


def run(
    *,
    topics: str,
    max_repos: int,
    out: str,
    vault_override: str | None,
    config_path: str | None,
) -> int:
    cfg = load_config(config_path)
    vault = resolve_vault(vault_override, cfg)
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    if not topic_list:
        log.error("no topics provided")
        return 64

    out_path = pathlib.Path(out)
    if not out_path.is_absolute():
        out_path = vault / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    seen = _seen_urls(vault)
    all_rows: list[dict] = []
    per_topic_cap = max(3, max_repos // max(1, len(topic_list)))
    for t in topic_list:
        rows = _scrape_topic(t, max_repos=per_topic_cap)
        log.info("topic=%s repos=%d", t, len(rows))
        all_rows.extend(rows)
        time.sleep(0.5)
        if len(all_rows) >= max_repos:
            break
    all_rows = all_rows[:max_repos]

    date = _dt.date.today().isoformat()
    body = _render(date, topic_list, all_rows, seen)
    out_path.write_text(body, encoding="utf8")
    log.info("wrote %s (%d repos)", out_path, len(all_rows))
    return 0
