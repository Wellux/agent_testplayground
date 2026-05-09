#!/usr/bin/env bats
# Smoke tests for the Phase 1-6 Python harness CLI surface.
# Run via: bats prompts/ralph-meta-chain/tests/test_harness.bats

REPO="$(git rev-parse --show-toplevel)"
HARNESS="$REPO/harness"

@test "harness --help lists all 8 subcommands" {
  cd "$HARNESS"
  run python3 -m harness --help
  [ "$status" -eq 0 ]
  for sub in ab embed query ingest compress reflect traces self-test; do
    [[ "$output" == *"$sub"* ]] || { echo "missing subcmd: $sub"; return 1; }
  done
}

@test "harness self-test --only privacy returns 0 on a clean tree" {
  cd "$HARNESS"
  run python3 -m harness self-test --only privacy
  [ "$status" -eq 0 ]
}

@test "harness ab --help describes the fixture format" {
  cd "$HARNESS"
  run python3 -m harness ab --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"--incumbent"* ]]
  [[ "$output" == *"--candidate"* ]]
  [[ "$output" == *"--fixture"* ]]
}

@test "harness embed --help mentions Ollama" {
  cd "$HARNESS"
  run python3 -m harness embed --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"Ollama"* ]] || [[ "$output" == *"ollama"* ]] || [[ "$output" == *"sqlite-vec"* ]]
}
