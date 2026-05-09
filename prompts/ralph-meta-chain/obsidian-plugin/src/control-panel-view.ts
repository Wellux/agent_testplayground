import { ItemView, WorkspaceLeaf } from "obsidian";
import { promises as fs } from "fs";
import * as path from "path";
import { RalphSettings } from "./settings";

export const CONTROL_PANEL_VIEW_TYPE = "ralph-control-panel-view";

const POLL_MS = 15_000;

export type CommandLauncher = (commandId: string) => void;

interface State {
  [axis: string]: { date?: string; status?: string; counts?: Record<string, number> } | undefined;
}

const AXES: Array<[string, string]> = [
  ["research", "ralph-run-research"],
  ["memory", "ralph-run-memory"],
  ["skills", "ralph-run-skills"],
  ["interaction", "ralph-run-interaction"],
  ["compress", "ralph-run-compress"],
  ["heal", "ralph-run-heal"],
  ["evolve", "ralph-run-evolve"],
  ["update", "ralph-run-update"],
];

const QUICK_ACTIONS: Array<[string, string]> = [
  ["Run full chain", "ralph-run-full-chain"],
  ["Self-test", "ralph-self-test"],
  ["Pause", "ralph-pause"],
  ["Resume", "ralph-resume"],
  ["Open log", "ralph-open-log"],
  ["Open metrics", "ralph-open-metrics"],
  ["Compress current note", "ralph-compress-current"],
  ["Promote to canonical", "ralph-promote-canonical"],
  ["Generate skill from note", "ralph-skill-from-note"],
  ["Run vault diagnostics", "ralph-vault-diagnostics"],
];

export class ControlPanelView extends ItemView {
  private timer?: number;
  private getSettings: () => RalphSettings;
  private launch: CommandLauncher;

  constructor(leaf: WorkspaceLeaf, getSettings: () => RalphSettings, launch: CommandLauncher) {
    super(leaf);
    this.getSettings = getSettings;
    this.launch = launch;
  }

  getViewType(): string { return CONTROL_PANEL_VIEW_TYPE; }
  getDisplayText(): string { return "Ralph control panel"; }
  getIcon(): string { return "compass"; }

  async onOpen(): Promise<void> {
    this.contentEl.empty();
    this.contentEl.addClass("ralph-control-panel");

    const refresh = async () => this.render();
    await refresh();
    this.timer = window.setInterval(() => void refresh(), POLL_MS);
  }

  async onClose(): Promise<void> {
    if (this.timer !== undefined) {
      window.clearInterval(this.timer);
      this.timer = undefined;
    }
  }

  private async render(): Promise<void> {
    this.contentEl.empty();
    const s = this.getSettings();
    if (!s.vaultRoot || !s.repoRoot) {
      this.contentEl.createEl("p", {
        text: "Set vaultRoot AND repoRoot in plugin settings to use the control panel.",
      });
      return;
    }

    // Status block
    this.contentEl.createEl("h3", { text: "Status" });
    const stateFile = path.join(s.vaultRoot, "90-Meta", "ralph-state.json");
    const stopFile = path.join(s.vaultRoot, "90-Meta", "STOP");
    let state: State = {};
    try {
      const raw = await fs.readFile(stateFile, "utf8");
      state = JSON.parse(raw) as State;
    } catch { /* first run */ }
    let paused = false;
    try { await fs.stat(stopFile); paused = true; } catch { /* none */ }

    if (paused) {
      const p = this.contentEl.createEl("div");
      p.style.color = "var(--text-warning)";
      p.textContent = "⏸ PAUSED — touch 90-Meta/STOP";
    }

    const today = new Date().toISOString().slice(0, 10);
    for (const [axis] of AXES) {
      const row = this.contentEl.createEl("div", { cls: "ralph-axis-row" });
      const left = row.createEl("span");
      const entry = state?.[axis];
      const ok = entry?.date === today && entry?.status === "COMPLETE";
      left.textContent = `${ok ? "✓" : "…"} ${axis}`;
      const right = row.createEl("span");
      right.textContent = entry?.date ?? "(no run)";
    }

    // Quick actions
    this.contentEl.createEl("h3", { text: "Quick actions" });
    const buttons = this.contentEl.createEl("div");
    for (const [label, commandId] of QUICK_ACTIONS) {
      const btn = buttons.createEl("span", { cls: "ralph-cmd-button" });
      btn.textContent = label;
      btn.onclick = () => this.launch(commandId);
    }

    // Pending approvals (count from business-entity ledger if present)
    this.contentEl.createEl("h3", { text: "Pending approvals" });
    const pending = path.join(
      s.vaultRoot,
      "business-entity",
      "ledgers",
      "pending-approvals.md"
    );
    let approvalCount = 0;
    try {
      const text = await fs.readFile(pending, "utf8");
      approvalCount = (text.match(/^\| /gm) ?? []).length;
    } catch { /* none */ }
    const ap = this.contentEl.createEl("div");
    ap.textContent = approvalCount > 0
      ? `${approvalCount} open approval(s) — open business-entity/ledgers/pending-approvals.md`
      : "(none)";
  }
}
