import { ItemView, WorkspaceLeaf } from "obsidian";
import { promises as fs } from "fs";
import * as path from "path";
import { RalphSettings } from "./settings";

export const LOG_VIEW_TYPE = "ralph-log-view";

const POLL_MS = 5_000;
const TAIL_LINES = 200;

export class LogView extends ItemView {
  private timer?: number;
  private getSettings: () => RalphSettings;

  constructor(leaf: WorkspaceLeaf, getSettings: () => RalphSettings) {
    super(leaf);
    this.getSettings = getSettings;
  }

  getViewType(): string {
    return LOG_VIEW_TYPE;
  }

  getDisplayText(): string {
    return "Ralph log";
  }

  getIcon(): string {
    return "file-text";
  }

  async onOpen(): Promise<void> {
    this.contentEl.empty();
    this.contentEl.addClass("ralph-log-view");
    const pre = this.contentEl.createEl("pre", { cls: "ralph-log-pre" });
    pre.style.whiteSpace = "pre-wrap";
    pre.style.fontFamily = "var(--font-monospace)";
    pre.style.fontSize = "12px";

    const refresh = async () => {
      const s = this.getSettings();
      if (!s.vaultPath) {
        pre.textContent = "Set vaultPath in plugin settings.";
        return;
      }
      const logPath = path.join(s.vaultPath, "90-Meta", "log.md");
      try {
        const text = await fs.readFile(logPath, "utf8");
        const lines = text.split("\n");
        const tail = lines.slice(Math.max(0, lines.length - TAIL_LINES));
        pre.textContent = tail.join("\n");
      } catch (e: unknown) {
        const err = e as NodeJS.ErrnoException;
        pre.textContent = err.code === "ENOENT"
          ? `(no log yet at ${logPath})`
          : `error: ${err.message}`;
      }
    };

    await refresh();
    this.timer = window.setInterval(() => void refresh(), POLL_MS);
  }

  async onClose(): Promise<void> {
    if (this.timer !== undefined) {
      window.clearInterval(this.timer);
      this.timer = undefined;
    }
  }
}
