# agent_testplayground — Ralph meta-chain

A self-improving Claude Code agent that uses an Obsidian vault as its
second brain. Five daily/hourly prompts run as cron jobs; each one mines
the previous run's traces, hypothesizes improvements, runs cheap experiments,
and rewrites the agent's own substrate.

## What's in this repo

| Path                             | What                                                      |
| -------------------------------- | --------------------------------------------------------- |
| `prompts/ralph-meta-chain/`      | Five Ralph prompts + config + crontab                     |
| `scripts/`                       | Idempotent install / uninstall (Linux cron, macOS launchd)|
| `obsidian-ralph/`                | TypeScript Obsidian plugin (commands, status bar, views)  |
| `harness/`                       | Python CLI: `ab`, `embed`, `query`, `ingest`, `compress`  |
| `docs/voice-multidevice-design.md` | Phase G architecture sketch (no code yet)                |

## Cron order (UTC)

| Time   | Prompt                              | Optimizes                                      |
| ------ | ----------------------------------- | ---------------------------------------------- |
| 01:00  | `04-research-ingest.md`             | GitHub-trending → vault inbox                  |
| 02:00  | `01-memory-optimizer.md`            | Atomic notes, MOCs, orphans (Karpathy LLM-Wiki)|
| 03:00  | `02-skills-optimizer.md`            | Reusable skills + revalidation (Hermes-style)  |
| 04:00  | `03-interaction-optimizer.md`       | A/B-tested prompt rewrites                     |
| :30 h  | `05-compress.md`                    | Context bloat / weekly daily-note rollups      |

## Quick start

```bash
git clone <this repo>
cd agent_testplayground

# 1) Configure your vault
cp prompts/ralph-meta-chain/config.example.yml prompts/ralph-meta-chain/config.yml
$EDITOR prompts/ralph-meta-chain/config.yml      # set vault_path

# 2) Build the Obsidian plugin (optional but recommended)
cd obsidian-ralph && npm install && npm run build && cd ..
ln -s "$PWD/obsidian-ralph" "$VAULT/.obsidian/plugins/ralph-meta-chain"

# 3) Install the Python harness
cd harness && uv sync && cp .env.example .env && cd ..
$EDITOR harness/.env                              # add ANTHROPIC_API_KEY

# 4) Pull the local embedding model
ollama pull nomic-embed-text

# 5) Install the cron / launchd entries
./scripts/install.sh --dry-run                    # preview
./scripts/install.sh                              # install
```

## Privacy

- Every secret lives in `harness/.env` (gitignored). `prompts/ralph-meta-chain/config.yml` is also gitignored — only `config.example.yml` is tracked.
- Embeddings run locally via Ollama by default. No data leaves the machine for the embedding path.
- The optional voice / multi-device plane (Phase G, sketched in `docs/`) is Tailscale-only by default; the Alexa path is the only network egress and is opt-in.

## Inspirations

This project lifts conventions from a number of public projects, cited
inline in each prompt:

[Anthropic ralph-wiggum plugin](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) ·
[ghuntley/how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum) ·
[snarktank/ralph](https://github.com/snarktank/ralph) ·
[karpathy/autoresearch](https://github.com/karpathy/autoresearch) ·
[Karpathy LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) ·
[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) ·
[NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) ·
[obra/knowledge-graph](https://github.com/obra/knowledge-graph) ·
[brianpetro/obsidian-smart-connections](https://github.com/brianpetro/obsidian-smart-connections) ·
[promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) ·
[openai/codex](https://github.com/openai/codex) ·
[moazbuilds/claudeclaw](https://github.com/moazbuilds/claudeclaw) ·
[swarmclawai/swarmclaw](https://github.com/swarmclawai/swarmclaw)
