#!/usr/bin/env bash
# scripts/lib/paths.sh — canonical path helpers.

# Repo root via git.
ralph_paths_repo() { git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null; }

# Phase 1-6 reference path → master-spec target path mapping.
# Echoes target if there's a known mapping; otherwise echoes input as-is.
ralph_paths_target() {
  local p="$1"
  case "$p" in
    harness|harness/*)
      echo "prompts/ralph-meta-chain/scripts/${p}" ;;
    voice-server|voice-server/*)
      echo "prompts/ralph-meta-chain/${p}" ;;
    obsidian-ralph|obsidian-ralph/*)
      echo "prompts/ralph-meta-chain/obsidian-plugin/${p#obsidian-ralph/}" ;;
    scripts/install.sh)
      echo "prompts/ralph-meta-chain/install/install_cron.sh" ;;
    scripts/uninstall.sh)
      echo "prompts/ralph-meta-chain/install/uninstall_cron.sh" ;;
    scripts/launchd|scripts/launchd/*)
      echo "prompts/ralph-meta-chain/install/launchd/${p#scripts/launchd/}" ;;
    *)
      echo "$p" ;;
  esac
}

# Standard vault subfolder paths under $VAULT.
ralph_paths_inbox()       { echo "${VAULT:-}/00-Inbox"; }
ralph_paths_daily()        { echo "${VAULT:-}/10-Daily"; }
ralph_paths_mocs()         { echo "${VAULT:-}/20-MOCs"; }
ralph_paths_notes()        { echo "${VAULT:-}/30-Notes"; }
ralph_paths_skills()       { echo "${VAULT:-}/40-Skills"; }
ralph_paths_prompts()      { echo "${VAULT:-}/50-Prompts"; }
ralph_paths_interactions() { echo "${VAULT:-}/60-Interactions"; }
ralph_paths_meta()         { echo "${VAULT:-}/90-Meta"; }
