"""Pluggable memory backends.

The harness ships with one default backend — `local-sqlite-vec` — that mirrors
`obra/knowledge-graph`'s schema (sqlite-vec + FTS5 in a single file, all on
the user's disk). The other backends are opt-in stubs that import the
relevant Python package lazily; if the package isn't installed, calling the
backend raises a clear error so the user can `pip install` and retry.

Why we ship stubs: the 2026 agent-memory comparison work (Atlan, vectorize.io,
Hermes OS, n1n.ai, dev.to LongMemEval re-runs) consistently shows that no
single backend wins across all use-cases:

  - mem0/mem0           — best for personalization-style chatbots
  - getzep/zep + Graphiti — best for temporal facts (LongMemEval 63.8 vs
                            Mem0 49.0 — a 15-pt gap)
  - letta/letta         — best for long-running agents (OS-style tiered
                            context management; the MemGPT line)
  - cognee-ai/cognee    — best for local-first graph reasoning over
                            unstructured docs; aligns with our Ollama-only
                            default
  - obra/knowledge-graph — what we already use; sqlite-vec + FTS5

Sources:
  https://atlan.com/know/best-ai-agent-memory-frameworks-2026/
  https://vectorize.io/articles/best-ai-agent-memory-systems
  https://github.com/cognee-ai/cognee
  https://github.com/letta-ai/letta
"""
from __future__ import annotations

import logging
import pathlib
from typing import Any, Protocol

log = logging.getLogger(__name__)


class MemoryBackend(Protocol):
    """Minimum surface every backend must implement."""

    name: str

    def embed_one(self, path: pathlib.Path, vault: pathlib.Path) -> None: ...
    def query(self, query_text: str, *, k: int) -> list[tuple[str, float, str]]:
        """Return [(id, score, path)] ranked by relevance, up to k entries."""
        ...


class LocalSqliteVec:
    """The shipped default — implemented inside `embeddings.py`. The selector
    below recognizes this name and returns None so the existing code path
    runs unchanged. Kept as a marker class for clarity and tests."""

    name = "local-sqlite-vec"


class CogneeBackend:
    """Local-first graph-reasoning memory via the `cognee` Python package.

    Lazy-import. The user opts in via:
        embeddings:
          backend: cognee

    Repo: https://github.com/cognee-ai/cognee
    """

    name = "cognee"

    def __init__(self, vault: pathlib.Path, model: str) -> None:
        try:
            import cognee  # type: ignore[import-not-found]  # noqa: F401
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "cognee backend requested but package missing; "
                "`pip install cognee` then re-run."
            ) from e
        self.vault = vault
        self.model = model

    def embed_one(self, path: pathlib.Path, vault: pathlib.Path) -> None:  # pragma: no cover
        import cognee  # type: ignore[import-not-found]
        text = path.read_text(encoding="utf8", errors="replace")
        try:
            import asyncio
            asyncio.run(cognee.add(text, dataset_name="ralph"))
            asyncio.run(cognee.cognify())
        except Exception as e:
            log.warning("cognee embed failed for %s: %s", path, e)

    def query(self, query_text: str, *, k: int) -> list[tuple[str, float, str]]:  # pragma: no cover
        import cognee  # type: ignore[import-not-found]
        import asyncio
        results = asyncio.run(cognee.search("INSIGHTS", query_text))
        out: list[tuple[str, float, str]] = []
        for i, r in enumerate(results[:k]):
            score = 1.0 / (1 + i)
            out.append((str(getattr(r, "id", i)), score, str(getattr(r, "source", ""))))
        return out


class LettaBackend:
    """OS-style tiered memory via the `letta` Python package.

    Best for long-running agents that need >> context-window memory. Most
    users will not need this; we ship the stub so opt-in is one line.

    Repo: https://github.com/letta-ai/letta
    """

    name = "letta"

    def __init__(self, vault: pathlib.Path, model: str) -> None:
        try:
            import letta  # type: ignore[import-not-found]  # noqa: F401
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "letta backend requested but package missing; "
                "`pip install letta` then re-run."
            ) from e
        self.vault = vault
        self.model = model

    def embed_one(self, path: pathlib.Path, vault: pathlib.Path) -> None:  # pragma: no cover
        # Letta manages memory inside a running agent; we register the doc as
        # an "archival memory" entry. Implementations vary by Letta version,
        # so we keep this stub deliberately defensive.
        try:
            from letta.client.client import LocalClient  # type: ignore[import-not-found]
            client = LocalClient()
            client.archive_memory(name="ralph", text=path.read_text(encoding="utf8", errors="replace"))
        except Exception as e:
            log.warning("letta embed failed for %s: %s", path, e)

    def query(self, query_text: str, *, k: int) -> list[tuple[str, float, str]]:  # pragma: no cover
        try:
            from letta.client.client import LocalClient  # type: ignore[import-not-found]
            client = LocalClient()
            results = client.archive_search(name="ralph", query=query_text, top_k=k)
            return [(str(r.id), float(getattr(r, "score", 0.0)), str(getattr(r, "source", ""))) for r in results]
        except Exception as e:
            log.warning("letta query failed: %s", e)
            return []


def select_backend(name: str, *, vault: pathlib.Path, model: str) -> object | None:
    """Return a non-default backend instance, or None if name is the default
    (in which case `embeddings.py` runs its existing sqlite-vec code path)."""
    canonical = (name or "local-sqlite-vec").strip().lower()
    if canonical in ("local-sqlite-vec", "default", "sqlite-vec", ""):
        return None
    if canonical == "cognee":
        return CogneeBackend(vault, model)
    if canonical in ("letta", "memgpt"):
        return LettaBackend(vault, model)
    raise ValueError(
        f"unknown memory backend {canonical!r}; "
        f"valid: local-sqlite-vec | cognee | letta"
    )


__all__ = ["LocalSqliteVec", "CogneeBackend", "LettaBackend", "select_backend"]
