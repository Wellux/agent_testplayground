// Greenfield runner: spawns claude -p <prompt> or python -m harness <subcmd>.
// Mirrors obsidian-ralph/src/runner.ts but reads prompts from the master-spec
// path (prompts/ralph-meta-chain/0[1-8]-*.md) and resolves the harness via
// the user-configured repoRoot.

import { spawn } from "child_process";
import { promises as fs } from "fs";
import * as path from "path";
import { RalphSettings } from "./settings";

const PROMISE_RE = /<promise>COMPLETE<\/promise>/;

// Sentinel returned by runAxisOnce when the agent emitted the completion
// promise. runAxis breaks on any non-zero return, so this just has to be
// != 0; -2 is unused by Node's child_process exit codes.
export const EXIT_PROMISE_COMPLETE = -2;

export type LogSink = (line: string) => void;

export const AXIS_TO_PROMPT: Record<string, string> = {
  research:    "04-research-ingest.md",
  memory:      "01-memory-optimizer.md",
  skills:      "02-skills-optimizer.md",
  interaction: "03-interaction-optimizer.md",
  compress:    "05-compress.md",
  heal:        "06-autoheal.md",
  evolve:      "07-autoevolve.md",
  update:      "08-autoupdate.md",
};

function ralphDir(s: RalphSettings): string {
  if (!s.repoRoot) {
    throw new Error("Ralph: repoRoot not set in plugin settings.");
  }
  return path.join(s.repoRoot, "prompts", "ralph-meta-chain");
}

export function stopFile(s: RalphSettings): string {
  if (!s.vaultRoot) throw new Error("Ralph: vaultRoot not set.");
  return path.join(s.vaultRoot, "90-Meta", "STOP");
}

export async function touchStop(s: RalphSettings): Promise<void> {
  const f = stopFile(s);
  await fs.mkdir(path.dirname(f), { recursive: true });
  await fs.writeFile(f, "stopped via obsidian-plugin\n");
}

export async function removeStop(s: RalphSettings): Promise<void> {
  try {
    await fs.unlink(stopFile(s));
  } catch (e: unknown) {
    if ((e as NodeJS.ErrnoException).code !== "ENOENT") throw e;
  }
}

async function readPrompt(file: string, s: RalphSettings): Promise<string> {
  return fs.readFile(path.join(ralphDir(s), file), "utf8");
}

/**
 * Spawn `claude -p <prompt-text>` once. Streams stdout/stderr to `sink`.
 * Detects `<promise>COMPLETE</promise>` and tags the final line.
 */
export async function runAxisOnce(
  s: RalphSettings,
  promptFile: string,
  sink: LogSink
): Promise<number> {
  const promptText = await readPrompt(promptFile, s);

  return await new Promise<number>((resolve, reject) => {
    const child = spawn(s.claudeBin, ["-p", promptText], {
      cwd: s.repoRoot,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    let sawPromise = false;
    const onLine = (chunk: Buffer | string) => {
      const text = typeof chunk === "string" ? chunk : chunk.toString("utf8");
      for (const line of text.split(/\r?\n/)) {
        if (!line) continue;
        if (PROMISE_RE.test(line)) sawPromise = true;
        sink(line);
      }
    };

    child.stdout?.on("data", onLine);
    child.stderr?.on("data", onLine);
    child.on("error", err => reject(err));
    child.on("close", code => {
      // Honor the prompt's exit contract: if the agent emitted
      // <promise>COMPLETE</promise>, the axis is done — return a sentinel
      // so runAxis() breaks the loop instead of re-firing the same prompt
      // up to maxIterations times. claude exits 0 on either "more work
      // pending" or "done"; without this check the iteration cap is the
      // only brake. Mirrors voice-server/runner.py.
      if (sawPromise) {
        sink("[ralph] promise=COMPLETE detected");
        resolve(EXIT_PROMISE_COMPLETE);
        return;
      }
      resolve(code ?? -1);
    });
  });
}

/**
 * Run an axis under the Ralph loop: re-invoke until exit != 0 or
 * maxIterations reached.
 */
export async function runAxis(
  s: RalphSettings,
  promptFile: string,
  sink: LogSink
): Promise<number> {
  const max = s.maxIterations > 0 ? s.maxIterations : 8;
  let last = 0;
  for (let i = 0; i < max; i++) {
    sink(`[ralph] ${promptFile} iteration ${i + 1}/${max}`);
    last = await runAxisOnce(s, promptFile, sink);
    if (last !== 0) break;
  }
  return last;
}

const FULL_CHAIN_ORDER = [
  "04-research-ingest.md",
  "01-memory-optimizer.md",
  "02-skills-optimizer.md",
  "03-interaction-optimizer.md",
];

export async function runFullChain(s: RalphSettings, sink: LogSink): Promise<void> {
  for (const promptFile of FULL_CHAIN_ORDER) {
    sink(`[ralph] ── chain: starting ${promptFile} ──`);
    await runAxis(s, promptFile, sink);
  }
}

/**
 * Spawn `python -m harness <args>` once. Used for self-test, traces,
 * reflect, embed, etc. The plugin's auto-detected vaultRoot is passed
 * as `--vault <path>` so harness commands operate on the open Obsidian
 * vault, NOT on the sample path in config.example.yml.
 */
export async function runHarness(
  s: RalphSettings,
  args: string[],
  sink: LogSink
): Promise<number> {
  if (!s.repoRoot) {
    sink("[ralph] runHarness: repoRoot not set");
    return -1;
  }
  // Inject --vault from the plugin's auto-detected vaultRoot. Without
  // this, `python -m harness ...` falls back to config.yml (often
  // missing) or config.example.yml's sample vault path — so commands
  // like Run Full Index / Compress Current Note / Detect Duplicates /
  // Run Vault Diagnostics operate on the wrong path despite the plugin
  // knowing the right one.
  const argsWithVault: string[] = [...args];
  if (s.vaultRoot && !args.includes("--vault")) {
    argsWithVault.unshift("--vault", s.vaultRoot);
  }
  return await new Promise<number>((resolve, reject) => {
    // Phase 1-6 reference layout: harness/ at repo root. Round 8
    // migration moves it to prompts/ralph-meta-chain/scripts/harness/.
    // Try the new path first, fall back to the old.
    const newPath = path.join(s.repoRoot, "prompts", "ralph-meta-chain", "scripts", "harness");
    const oldPath = path.join(s.repoRoot, "harness");
    fs.access(path.join(newPath, "harness"))
      .then(() => spawnHarness(newPath))
      .catch(() => spawnHarness(oldPath));

    function spawnHarness(cwd: string) {
      const child = spawn(s.pythonBin, ["-m", "harness", ...argsWithVault], {
        cwd,
        env: process.env,
        stdio: ["ignore", "pipe", "pipe"],
      });
      const onLine = (chunk: Buffer | string) => {
        const text = typeof chunk === "string" ? chunk : chunk.toString("utf8");
        for (const line of text.split(/\r?\n/)) {
          if (line) sink(line);
        }
      };
      child.stdout?.on("data", onLine);
      child.stderr?.on("data", onLine);
      child.on("error", err => reject(err));
      child.on("close", code => resolve(code ?? -1));
    }
  });
}

/**
 * Spawn an arbitrary Bash shim from prompts/ralph-meta-chain/scripts/.
 */
export async function runShim(
  s: RalphSettings,
  shimName: string,
  args: string[],
  sink: LogSink
): Promise<number> {
  const shim = path.join(ralphDir(s), "scripts", shimName);
  return await new Promise<number>((resolve, reject) => {
    const child = spawn("bash", [shim, ...args], {
      cwd: s.repoRoot,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    const onLine = (chunk: Buffer | string) => {
      const text = typeof chunk === "string" ? chunk : chunk.toString("utf8");
      for (const line of text.split(/\r?\n/)) {
        if (line) sink(line);
      }
    };
    child.stdout?.on("data", onLine);
    child.stderr?.on("data", onLine);
    child.on("error", err => reject(err));
    child.on("close", code => resolve(code ?? -1));
  });
}

/**
 * Run a Claude Code slash-command spec from prompts/ralph-meta-chain/commands/
 * with the active note as `$ARGUMENTS`. Used by the plugin's
 * "Generate Skill From Current Note" / "Generate Experiment From Current Note"
 * commands. Composes:
 *
 *   <commands/<commandFile>>            (the slash-command spec)
 *   ---
 *   ## $ARGUMENTS
 *   <noteRelPath>
 *   ## Source note content
 *   <note body>
 *   Now perform the work above. Emit <promise>COMPLETE</promise> when done.
 *
 * Then spawns `claude -p` so the LLM uses Edit/Write tools to land the
 * draft (skill candidate or fixture YAML) per the spec's instructions.
 */
export async function runCommandPromptOnNote(
  s: RalphSettings,
  commandFile: string,
  noteRelPath: string,
  sink: LogSink,
): Promise<number> {
  if (!s.repoRoot) throw new Error("Ralph: repoRoot not set in plugin settings.");
  if (!s.vaultRoot) throw new Error("Ralph: vaultRoot not set in plugin settings.");

  const commandPath = path.join(ralphDir(s), "commands", commandFile);
  const noteAbsPath = path.join(s.vaultRoot, noteRelPath);

  let commandSpec: string;
  let noteText: string;
  try {
    commandSpec = await fs.readFile(commandPath, "utf8");
  } catch {
    throw new Error(`Ralph: command spec missing at ${commandPath}`);
  }
  try {
    noteText = await fs.readFile(noteAbsPath, "utf8");
  } catch {
    throw new Error(`Ralph: active note not readable at ${noteAbsPath}`);
  }

  const fullPrompt = [
    commandSpec,
    "",
    "---",
    "",
    "## $ARGUMENTS",
    "",
    noteRelPath,
    "",
    `## Source note content (${noteRelPath})`,
    "",
    "```markdown",
    noteText,
    "```",
    "",
    "Now perform the work described above. Use the Edit/Write tools to",
    "create the draft file in the location the spec names. When done,",
    "emit `<promise>COMPLETE</promise>` on its own line.",
  ].join("\n");

  return await new Promise<number>((resolve, reject) => {
    const child = spawn(s.claudeBin, ["-p", fullPrompt], {
      cwd: s.repoRoot,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    const onLine = (chunk: Buffer | string) => {
      const text = typeof chunk === "string" ? chunk : chunk.toString("utf8");
      for (const line of text.split(/\r?\n/)) {
        if (line) sink(line);
      }
    };
    child.stdout?.on("data", onLine);
    child.stderr?.on("data", onLine);
    child.on("error", err => reject(err));
    child.on("close", code => resolve(code ?? -1));
  });
}
