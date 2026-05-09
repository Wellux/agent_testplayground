import { App, Notice, Plugin, PluginSettingTab, Setting, WorkspaceLeaf } from "obsidian";
import { runAxis, runFullChain, runHarness, touchStop, removeStop } from "./runner";
import { LogView, LOG_VIEW_TYPE } from "./log-view";
import { MetricsView, METRICS_VIEW_TYPE } from "./metrics-view";
import { StatusBar } from "./status-bar";
import { DEFAULT_SETTINGS, RalphSettings } from "./settings";

export default class RalphPlugin extends Plugin {
  settings: RalphSettings = DEFAULT_SETTINGS;
  statusBar?: StatusBar;

  async onload() {
    await this.loadSettings();

    this.registerView(LOG_VIEW_TYPE, (leaf: WorkspaceLeaf) => new LogView(leaf, () => this.settings));
    this.registerView(METRICS_VIEW_TYPE, (leaf: WorkspaceLeaf) => new MetricsView(leaf, () => this.settings));

    this.statusBar = new StatusBar(this.addStatusBarItem(), () => this.settings);
    this.registerInterval(window.setInterval(() => this.statusBar?.refresh(), 30_000));
    void this.statusBar.refresh();

    const axes: Array<{ id: string; name: string; prompt: string }> = [
      { id: "research",    name: "research-ingest", prompt: "04-research-ingest.md" },
      { id: "memory",      name: "memory",          prompt: "01-memory-optimizer.md" },
      { id: "skills",      name: "skills",          prompt: "02-skills-optimizer.md" },
      { id: "interaction", name: "interaction",     prompt: "03-interaction-optimizer.md" },
      { id: "compress",    name: "compress",        prompt: "05-compress.md" },
      { id: "heal",        name: "autoheal",        prompt: "06-autoheal.md" },
      { id: "evolve",      name: "autoevolve",      prompt: "07-autoevolve.md" },
      { id: "update",      name: "autoupdate",      prompt: "08-autoupdate.md" }
    ];

    for (const axis of axes) {
      this.addCommand({
        id: `ralph-run-${axis.id}`,
        name: `Ralph: Run ${axis.name} pass`,
        callback: () => this.run(axis.prompt, axis.name)
      });
    }

    this.addCommand({
      id: "ralph-run-full-chain",
      name: "Ralph: Run full chain (4 → 1 → 2 → 3)",
      callback: async () => {
        new Notice("Ralph: full chain started");
        await runFullChain(this.settings, line => this.statusBar?.appendLog(line));
        new Notice("Ralph: full chain complete");
        void this.statusBar?.refresh();
      }
    });

    this.addCommand({
      id: "ralph-pause",
      name: "Ralph: Pause (touch 90-Meta/STOP)",
      callback: async () => {
        await touchStop(this.settings);
        new Notice("Ralph paused (STOP file present)");
        void this.statusBar?.refresh();
      }
    });

    this.addCommand({
      id: "ralph-resume",
      name: "Ralph: Resume",
      callback: async () => {
        await removeStop(this.settings);
        new Notice("Ralph resumed");
        void this.statusBar?.refresh();
      }
    });

    this.addCommand({
      id: "ralph-open-log",
      name: "Ralph: Open log view",
      callback: () => this.activateView(LOG_VIEW_TYPE)
    });

    this.addCommand({
      id: "ralph-open-metrics",
      name: "Ralph: Open metrics view",
      callback: () => this.activateView(METRICS_VIEW_TYPE)
    });

    this.addCommand({
      id: "ralph-self-test",
      name: "Ralph: Run self-test (local CI mirror)",
      callback: async () => {
        new Notice("Ralph: self-test started");
        const code = await runHarness(this.settings, ["self-test"], line => this.statusBar?.appendLog(line));
        new Notice(`Ralph: self-test exited (${code})`);
        void this.statusBar?.refresh();
      }
    });

    this.addSettingTab(new RalphSettingTab(this.app, this));
  }

  onunload() {
    this.statusBar?.detach();
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  private async run(prompt: string, axisName: string) {
    new Notice(`Ralph: ${axisName} started`);
    const code = await runAxis(this.settings, prompt, line => this.statusBar?.appendLog(line));
    new Notice(`Ralph: ${axisName} exited (${code})`);
    void this.statusBar?.refresh();
  }

  private async activateView(viewType: string) {
    const { workspace } = this.app;
    let leaf = workspace.getLeavesOfType(viewType)[0];
    if (!leaf) {
      leaf = workspace.getRightLeaf(false) ?? workspace.getLeaf(true);
      await leaf.setViewState({ type: viewType, active: true });
    }
    workspace.revealLeaf(leaf);
  }
}

class RalphSettingTab extends PluginSettingTab {
  plugin: RalphPlugin;

  constructor(app: App, plugin: RalphPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();

    new Setting(containerEl)
      .setName("Repo path")
      .setDesc("Absolute path to the agent_testplayground repo (contains prompts/ralph-meta-chain).")
      .addText(t => t
        .setPlaceholder("/Users/me/code/agent_testplayground")
        .setValue(this.plugin.settings.repoPath)
        .onChange(async v => { this.plugin.settings.repoPath = v.trim(); await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Vault path")
      .setDesc("Defaults to the current Obsidian vault.")
      .addText(t => t
        .setPlaceholder("auto")
        .setValue(this.plugin.settings.vaultPath)
        .onChange(async v => { this.plugin.settings.vaultPath = v.trim(); await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Claude binary")
      .setDesc("Defaults to `claude` on PATH.")
      .addText(t => t
        .setPlaceholder("claude")
        .setValue(this.plugin.settings.claudeBin)
        .onChange(async v => { this.plugin.settings.claudeBin = v.trim() || "claude"; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Max iterations per pass")
      .setDesc("Mirrors ralph-wiggum --max-iterations. 8 for daily, 4 for compress.")
      .addText(t => t
        .setValue(String(this.plugin.settings.maxIterations))
        .onChange(async v => {
          const n = Number.parseInt(v, 10);
          if (Number.isFinite(n) && n > 0) {
            this.plugin.settings.maxIterations = n;
            await this.plugin.saveSettings();
          }
        }));
  }
}
