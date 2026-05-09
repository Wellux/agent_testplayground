import { promises as fs } from "fs";
import * as path from "path";
import { RalphSettings } from "./settings";

const MAX_LOG_LINES = 200;

interface State {
  [axis: string]: { date?: string; status?: string; counts?: Record<string, number> } | undefined;
}

export class StatusBar {
  private el: HTMLElement;
  private getSettings: () => RalphSettings;
  private logBuffer: string[] = [];

  constructor(el: HTMLElement, getSettings: () => RalphSettings) {
    this.el = el;
    this.getSettings = getSettings;
    this.el.addClass("ralph-status");
    this.el.textContent = "🌀 Ralph · …";
  }

  detach(): void {
    this.el.detach?.();
  }

  appendLog(line: string): void {
    this.logBuffer.push(line);
    if (this.logBuffer.length > MAX_LOG_LINES) {
      this.logBuffer.splice(0, this.logBuffer.length - MAX_LOG_LINES);
    }
  }

  async refresh(): Promise<void> {
    const s = this.getSettings();
    if (!s.vaultRoot) {
      this.el.textContent = "🌀 Ralph · set vaultRoot in settings";
      return;
    }
    const stateFile = path.join(s.vaultRoot, "90-Meta", "ralph-state.json");
    const stopFile = path.join(s.vaultRoot, "90-Meta", "STOP");

    let state: State = {};
    try {
      const raw = await fs.readFile(stateFile, "utf8");
      state = JSON.parse(raw) as State;
    } catch { /* first run */ }

    let paused = false;
    try {
      await fs.stat(stopFile);
      paused = true;
    } catch { /* no STOP */ }

    const today = new Date().toISOString().slice(0, 10);
    const axes: Array<[string, string]> = [
      ["research", "res"],
      ["memory", "mem"],
      ["skills", "skl"],
      ["interaction", "int"],
      ["compress", "cmp"],
      ["heal", "hal"],
      ["evolve", "evo"],
      ["update", "upd"],
    ];
    const parts = axes.map(([axis, short]) => {
      const entry = state?.[axis];
      const ok = entry?.date === today && entry?.status === "COMPLETE";
      return `${short} ${ok ? "✓" : "…"}`;
    });
    const prefix = paused ? "⏸ Ralph" : "🌀 Ralph";
    this.el.textContent = `${prefix} · ${parts.join(" · ")}`;
  }
}
