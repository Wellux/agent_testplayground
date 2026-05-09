---
ralph_type: provider
provider: local-models-deferred
created: 2026-05-09
status: deferred
summary: "What activating local-model COMPLETION would involve."
---

# Local Models — Deferred Implementation

Embeddings are already ACTIVE. This file scopes the work for promoting
**completion** (the harness's judge model) to a local Ollama LLM.

## Estimated work

| Component                              | Effort      |
| -------------------------------------- | ----------- |
| Implement `harness/.../local_judge.py`  | 1-2 days    |
| `ollama/<model>` prefix routing in      |             |
| `harness/harness/judge.py`              | 0.5 day     |
| Calibration: rubric quality vs Claude   | 1-2 days    |
| Token-cost analysis (zero $; model RAM) | 0.5 day     |
| Update fixtures with `--judge-model`    | 0.5 day     |
| Update `08-autoupdate.md` model registry | 0.5 day    |
| Total                                    | ~4-6 days   |

## Pre-requisites (from user)

1. Hardware capable of running the chosen model (e.g. Mac mini with
   ≥ 64 GB RAM for llama3.1:70b-instruct-q4).
2. Approval to spend disk space on the model (~40 GB for 70b-q4).
3. Calibration: the local judge must score ≥ 3.5/5 on the day-1
   fixtures, otherwise we keep Claude as judge.

## What activation looks like (sketch)

```python
# harness/harness/judge.py — Round 5+ extension

def _llm_rubric(text: str, judge_model: str) -> float:
    if judge_model.startswith("ollama/"):
        return _ollama_rubric(text, judge_model.split("/", 1)[1])
    return _anthropic_rubric(text, judge_model)

def _ollama_rubric(text: str, model: str) -> float:
    r = httpx.post(
        "http://localhost:11434/v1/chat/completions",
        json={
            "model": model,
            "messages": [{"role": "user", "content": RUBRIC_PROMPT.format(output=text)}],
            "temperature": 0.0,
            "max_tokens": 128,
        },
    )
    raw = r.json()["choices"][0]["message"]["content"]
    return _parse_rubric_json(raw)
```

## Calibration plan

1. Pick 5 fixture outputs at known rubric scores (set by Claude judge).
2. Run each through the local judge.
3. Compute mean absolute error.
4. If < 0.5 / 5.0: ship.
5. If ≥ 0.5: try a larger model OR keep Claude.

## What activation does NOT change

- The Anthropic SDK call from `harness ab` for the actual prompt
  (the candidate / incumbent runs). Switching THOSE to local models is
  a separate, larger activation (Round 7+).
- Hooks, slash commands, skills — all stay Claude-Code-specific.

## Cross-references

- `providers/local-models/adapter-spec.md`.
- `providers/local-models/ollama-notes.md`.
- `harness/harness/judge.py` — current implementation.
- `harness/harness/memory_backends.py` — embeddings precedent.
