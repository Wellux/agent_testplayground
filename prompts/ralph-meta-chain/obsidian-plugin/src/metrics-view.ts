import { ItemView, WorkspaceLeaf } from "obsidian";
import { promises as fs } from "fs";
import * as path from "path";
import { RalphSettings } from "./settings";

export const METRICS_VIEW_TYPE = "ralph-metrics-view";

const POLL_MS = 10_000;
const MAX_LINES = 2000;

interface MetricRow {
  axis?: string;
  [k: string]: unknown;
}

export class MetricsView extends ItemView {
  private timer?: number;
  private getSettings: () => RalphSettings;

  constructor(leaf: WorkspaceLeaf, getSettings: () => RalphSettings) {
    super(leaf);
    this.getSettings = getSettings;
  }

  getViewType(): string { return METRICS_VIEW_TYPE; }
  getDisplayText(): string { return "Ralph metrics"; }
  getIcon(): string { return "bar-chart"; }

  async onOpen(): Promise<void> {
    this.contentEl.empty();
    this.contentEl.addClass("ralph-metrics-view");
    const root = this.contentEl.createEl("div", { cls: "ralph-metrics" });

    const refresh = async () => {
      const s = this.getSettings();
      if (!s.vaultRoot) {
        root.textContent = "Set vaultRoot in plugin settings.";
        return;
      }
      const ndjsonPath = path.join(s.vaultRoot, "90-Meta", "metrics.ndjson");
      let lines: string[] = [];
      try {
        const text = await fs.readFile(ndjsonPath, "utf8");
        lines = text.split("\n").filter(Boolean).slice(-MAX_LINES);
      } catch (e: unknown) {
        const err = e as NodeJS.ErrnoException;
        root.empty();
        root.textContent = err.code === "ENOENT" ? `(no metrics yet at ${ndjsonPath})` : `error: ${err.message}`;
        return;
      }

      const counts = new Map<string, number>();
      for (const line of lines) {
        try {
          const row: MetricRow = JSON.parse(line);
          const axis = typeof row.axis === "string" ? row.axis : "?";
          counts.set(axis, (counts.get(axis) ?? 0) + 1);
        } catch { /* ignore */ }
      }

      root.empty();
      const h = root.createEl("h4", { text: `metrics.ndjson — last ${lines.length} rows` });
      h.style.margin = "4px 0";
      const ul = root.createEl("ul");
      for (const axis of ["research", "memory", "skills", "interaction", "compress", "heal", "evolve", "update"]) {
        const li = ul.createEl("li");
        li.textContent = `${axis}: ${counts.get(axis) ?? 0}`;
      }

      // Sparklines for the three primary axes.
      for (const axis of ["memory", "skills", "interaction"]) {
        const counts60 = new Array<number>(60).fill(0);
        for (const line of lines) {
          try {
            const row = JSON.parse(line) as MetricRow;
            if (row.axis !== axis) continue;
            const ts = typeof row["started"] === "string" ? Date.parse(row["started"]) : NaN;
            if (!Number.isFinite(ts)) continue;
            const ageDays = Math.floor((Date.now() - ts) / 86_400_000);
            if (ageDays >= 0 && ageDays < 60) counts60[59 - ageDays] += 1;
          } catch { /* ignore */ }
        }
        const max = Math.max(1, ...counts60);
        const w = 4;
        const h0 = 32;
        const svg = root.createSvg("svg", { attr: { width: String(w * 60), height: String(h0) } });
        for (let i = 0; i < 60; i++) {
          const v = counts60[i];
          const bh = (v / max) * h0;
          svg.createSvg("rect", {
            attr: {
              x: String(i * w),
              y: String(h0 - bh),
              width: String(w - 1),
              height: String(bh),
              fill: "currentColor",
              opacity: "0.7",
            },
          });
        }
        const label = root.createEl("div");
        label.style.opacity = "0.7";
        label.textContent = `${axis} — last 60 days`;
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
