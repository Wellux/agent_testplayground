"""harness — Ralph meta-chain CLI entrypoint."""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Sequence

from . import ab as ab_mod
from . import compress as compress_mod
from . import embeddings as embeddings_mod
from . import ingest as ingest_mod
from . import reflect as reflect_mod
from . import self_test as self_test_mod
from . import traces as traces_mod


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harness", description="Ralph meta-chain CLI")
    parser.add_argument("--vault", help="vault path (overrides config); defaults to $VAULT or config.yml")
    parser.add_argument("--config", help="path to ralph config.yml; defaults to ../prompts/ralph-meta-chain/config.yml")
    parser.add_argument("-v", "--verbose", action="store_true")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ab = sub.add_parser("ab", help="A/B two prompts on a fixture")
    p_ab.add_argument("--incumbent", required=True, help="path to incumbent prompt .md")
    p_ab.add_argument("--candidate", required=True, help="path to candidate prompt .md")
    p_ab.add_argument("--fixture", required=True, help="path to promptfoo-shaped YAML fixture")
    p_ab.add_argument("--judge-model", default=None, help="override judge model")

    p_em = sub.add_parser("embed", help="Embed notes via Ollama → sqlite-vec")
    g = p_em.add_mutually_exclusive_group(required=True)
    g.add_argument("--note", help="single vault-relative path")
    g.add_argument("--vault-full", action="store_true", help="reindex the whole vault")
    g.add_argument("--since", help="only files modified within this window (e.g. '2h', '1d')")

    p_q = sub.add_parser("query", help="Hybrid semantic + FTS5 query")
    p_q.add_argument("--semantic", required=True, help="query text")
    p_q.add_argument("--k", type=int, default=10)

    p_in = sub.add_parser("ingest", help="GitHub trending → 00-Inbox/")
    p_in.add_argument("--topics", help="comma-separated topic list (mutually exclusive with --creators)")
    p_in.add_argument("--max-repos", type=int, default=30)
    p_in.add_argument("--creators", help="comma-separated YouTube @handles (Matt Wolfe weekly lens)")
    p_in.add_argument("--max-per-channel", type=int, default=5)
    p_in.add_argument("--out", required=True, help="output path under $VAULT")

    p_c = sub.add_parser("compress", help="Summarize bloated notes / weekly rollups")
    g2 = p_c.add_mutually_exclusive_group(required=True)
    g2.add_argument("--note", help="vault-relative path")
    g2.add_argument("--older-than", help="time window (e.g. '7d')")
    g2.add_argument("--weekly", action="store_true", help="weekly rollup mode")
    p_c.add_argument("--iso-week", help="ISO week (YYYY-Www) for --weekly")

    p_r = sub.add_parser("reflect", help="Append a Reflexion lesson to a candidate prompt")
    p_r.add_argument("--candidate", required=True, help="vault-relative path to .candidate-N.md")
    p_r.add_argument("--verdict", default=None, help="optional pre-computed verdict label")
    p_r.add_argument("--judge-model", default=None, help="override judge model")

    p_t = sub.add_parser("traces", help="Tail / summarize 90-Meta/metrics.ndjson")
    p_t.add_argument("--tail", type=int, default=200)
    p_t.add_argument("--axis", default=None, help="filter to one axis")

    p_st = sub.add_parser("self-test", help="Local CI mirror; appends to 90-Meta/heal-checks.ndjson by default")
    p_st.add_argument("--only", default=None,
                      help="run a single check: privacy | shell | python | unit-tests | plugin")
    p_st.add_argument("--no-log", action="store_true",
                      help="skip the heal-checks.ndjson append (truly read-only mode for MCP / dashboards)")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )

    if args.cmd == "ab":
        return ab_mod.run(
            incumbent=args.incumbent,
            candidate=args.candidate,
            fixture=args.fixture,
            judge_model=args.judge_model,
            vault_override=args.vault,
            config_path=args.config,
        )
    if args.cmd == "embed":
        return embeddings_mod.run_embed(
            note=args.note,
            full_vault=args.vault_full,
            since=args.since,
            vault_override=args.vault,
            config_path=args.config,
        )
    if args.cmd == "query":
        return embeddings_mod.run_query(
            query=args.semantic,
            k=args.k,
            vault_override=args.vault,
            config_path=args.config,
        )
    if args.cmd == "ingest":
        if args.creators:
            return ingest_mod.run_creators(
                handles=args.creators,
                max_per_channel=args.max_per_channel,
                out=args.out,
                vault_override=args.vault,
                config_path=args.config,
            )
        if not args.topics:
            print("ingest: pass --topics or --creators", flush=True)
            return 64
        return ingest_mod.run(
            topics=args.topics,
            max_repos=args.max_repos,
            out=args.out,
            vault_override=args.vault,
            config_path=args.config,
        )
    if args.cmd == "compress":
        return compress_mod.run(
            note=args.note,
            older_than=args.older_than,
            weekly=args.weekly,
            iso_week=args.iso_week,
            vault_override=args.vault,
            config_path=args.config,
        )
    if args.cmd == "reflect":
        return reflect_mod.run(
            candidate=args.candidate,
            verdict=args.verdict,
            judge_model=args.judge_model,
            vault_override=args.vault,
            config_path=args.config,
        )
    if args.cmd == "traces":
        return traces_mod.run(
            tail=args.tail,
            axis=args.axis,
            vault_override=args.vault,
            config_path=args.config,
        )
    if args.cmd == "self-test":
        return self_test_mod.run(
            only=args.only,
            vault_override=args.vault,
            config_path=args.config,
            no_log=args.no_log,
        )
    return 64


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
