#!/usr/bin/env bash
# scripts/lib/scoring.sh — small scoring helpers used by reporting shims.

# Read a single rubric/banned/tokens column from metrics.ndjson and
# return the mean. Format expected: ndjson rows from `harness ab`.
#   ralph_score_mean <ndjson-file> <field> [<arm>]
ralph_score_mean() {
  local file="$1"; local field="$2"; local arm="${3:-}"
  [[ -f "$file" ]] || return 1
  local jq_filter='.'
  if [[ -n "$arm" ]]; then
    jq_filter="select(.arm == \"$arm\")"
  fi
  if ! command -v jq >/dev/null 2>&1; then
    echo "0"
    return 0
  fi
  jq -r --argjson cap 0 \
    "[.[] | $jq_filter | .${field}] | add / length // 0" \
    <(jq -s '.' "$file") 2>/dev/null || echo "0"
}

# Compute a simple win/loss verdict from candidate vs incumbent metrics.
#   ralph_score_verdict <inc_rubric> <can_rubric> <inc_tokens> <can_tokens> <inc_banned> <can_banned>
# Echoes one of: candidate-wins | incumbent-wins | tie
ralph_score_verdict() {
  local ir="$1" cr="$2" it="$3" ct="$4" ib="$5" cb="$6"
  awk -v ir="$ir" -v cr="$cr" -v it="$it" -v ct="$ct" -v ib="$ib" -v cb="$cb" '
    BEGIN {
      rubric_ok = (cr + 0) >= (ir + 0)
      tokens_ok = (ct + 0) <= (it + 0)
      banned_ok = (cb + 0) <  (ib + 0)
      if (rubric_ok && (tokens_ok || banned_ok)) { print "candidate-wins"; exit }
      if ((ir + 0) > (cr + 0) || (!tokens_ok && !banned_ok)) { print "incumbent-wins"; exit }
      print "tie"
    }
  '
}
