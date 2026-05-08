import { spawn } from "child_process";
import { promises as fs } from "fs";
import * as path from "path";
import { RalphSettings } from "./settings";

const PROMISE_RE = /<promise>COMPLETE<\/promise>/;

export type LogSink = (line: string) => void;

function resolveRalphDir(s: RalphSettings): string {
  if (!s.repoPath) {
    throw new Error("Ralph: repoPath setting is empty. Set it in plugin settings.");
  }
  return path.join(s.repoPath, "prompts", "ralph-meta-chain");
}

function stopFile(s: RalphSettings): string {
  if (!s.vaultPath) {
    throw new Error("Ralph: vaultPath is empty. Set it in plugin settings.");
  }
  return path.join(s.vaultPath, "90-Meta", "STOP");
}

export async function touchStop(s: RalphSettings): Promise<void> {
  const f = stopFile(s);
  await fs.mkdir(path.dirname(f), { recursive: true });
  await fs.writeFile(f, "stopped via obsidian-ralph\n");
}

export async function removeStop(s: RalphSettings): Promise<void> {
  try {
    await fs.unlink(stopFile(s));
  } catch (e: unknown) {
    if ((e as NodeJS.ErrnoException).code !== "ENOENT") throw e;
  }
}

async function readPrompt(ralphDir: string, file: string): Promise<string> {
  return fs.readFile(path.join(ralphDir, file), "utf8");
}

/**
 * Run a single axis once. Returns the exit code from `claude -p`. Streams
 * stdout / stderr to `sink`. Detects <promise>COMPLETE</promise> in the
 * stream and tags the final line.
 *
 * The Ralph loop semantics live OUTSIDE this function: callers should call
 * `runAxis` repeatedly until exit != 0 OR maxIterations reached.
 */
export async function runAxisOnce(
  s: RalphSettings,
  promptFile: string,
  sink: LogSink
): Promise<number> {
  const ralphDir = resolveRalphDir(s);
  const promptText = await readPrompt(ralphDir, promptFile);

  return await new Promise<number>((resolve, reject) => {
    const child = spawn(s.claudeBin, ["-p", promptText], {
      cwd: s.repoPath,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"]
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
      if (sawPromise) sink("[ralph] promise=COMPLETE detected");
      resolve(code ?? -1);
    });
  });
}

/**
 * Run an axis under the Ralph loop: re-invoke until exit != 0 or
 * maxIterations reached. This mirrors `until ! claude -p ...` from the
 * crontab, but inside Obsidian.
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
  "03-interaction-optimizer.md"
];

export async function runFullChain(s: RalphSettings, sink: LogSink): Promise<void> {
  for (const promptFile of FULL_CHAIN_ORDER) {
    sink(`[ralph] ── chain: starting ${promptFile} ──`);
    await runAxis(s, promptFile, sink);
  }
}
