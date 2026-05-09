#!/usr/bin/env bats
# Round 7 — verify indexes/ + benchmarks/ + experiments/ scaffolds.
# Run via: bats prompts/ralph-meta-chain/tests/test_round7_indexes_benchmarks.bats

REPO="$(git rev-parse --show-toplevel)"
RMC="$REPO/prompts/ralph-meta-chain"

@test "indexes/ has 7 files (6 indexes + README)" {
  count=$(find "$RMC/indexes" -name '*.md' -type f | wc -l | tr -d ' ')
  [ "$count" -eq 7 ]
}

@test "benchmarks/ has 7 files (6 scorecards + README)" {
  count=$(find "$RMC/benchmarks" -name '*.md' -type f | wc -l | tr -d ' ')
  [ "$count" -eq 7 ]
}

@test "experiments/ has README + 3 .gitkeep" {
  [ -f "$RMC/experiments/README.md" ]
  [ -f "$RMC/experiments/fixtures/.gitkeep" ]
  [ -f "$RMC/experiments/outputs/.gitkeep" ]
  [ -f "$RMC/experiments/reports/.gitkeep" ]
}

@test "every index file has frontmatter" {
  # README.md is the human-prose entry point; intentionally lacks frontmatter.
  # Mirrors the exemption in harness/tests/test_round7.py.
  for f in "$RMC/indexes"/*.md; do
    [[ "$(basename "$f")" == "README.md" ]] && continue
    head -1 "$f" | grep -qE '^---[[:space:]]*$' || { echo "no frontmatter: $f"; return 1; }
  done
}

@test "every benchmark scorecard documents pass thresholds" {
  for f in "$RMC/benchmarks"/{memory,skill,prompt,interaction,business-action,migration}-quality.md; do
    grep -q "Pass threshold" "$f" || { echo "no Pass threshold section: $f"; return 1; }
  done
}

@test "indexes cross-reference at least one canonical doc" {
  for f in "$RMC/indexes"/{vault,memory,skill,prompt,provider,business}-index.md; do
    grep -qE "(docs/|vault-template/|prompts/ralph-meta-chain/)" "$f" || {
      echo "no cross-ref in: $f"; return 1
    }
  done
}
