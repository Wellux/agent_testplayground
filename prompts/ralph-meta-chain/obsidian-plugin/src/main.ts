import { App, Notice, Plugin, PluginSettingTab, Setting, WorkspaceLeaf } from "obsidian";
import { promises as fs } from "fs";
import * as path from "path";
import {
  runAxis, runFullChain, runHarness, runShim, runCommandPromptOnNote,
  touchStop, removeStop, AXIS_TO_PROMPT,
} from "./runner";
import { LogView, LOG_VIEW_TYPE } from "./log-view";
import { MetricsView, METRICS_VIEW_TYPE } from "./metrics-view";
import { ControlPanelView, CONTROL_PANEL_VIEW_TYPE } from "./control-panel-view";
import { StatusBar } from "./status-bar";
import { DEFAULT_SETTINGS, RalphSettings } from "./settings";

export default class RalphPlugin extends Plugin {
  settings: RalphSettings = DEFAULT_SETTINGS;
  statusBar?: StatusBar;

  async onload() {
    await this.loadSettings();

    // Auto-detect vault path on first load.
    if (!this.settings.vaultRoot) {
      const adapterAny = this.app.vault.adapter as unknown as { getBasePath?: () => string };
      if (typeof adapterAny.getBasePath === "function") {
        this.settings.vaultRoot = adapterAny.getBasePath();
        await this.saveSettings();
      }
    }

    this.registerView(LOG_VIEW_TYPE, (leaf: WorkspaceLeaf) =>
      new LogView(leaf, () => this.settings));
    this.registerView(METRICS_VIEW_TYPE, (leaf: WorkspaceLeaf) =>
      new MetricsView(leaf, () => this.settings));
    this.registerView(CONTROL_PANEL_VIEW_TYPE, (leaf: WorkspaceLeaf) =>
      new ControlPanelView(leaf, () => this.settings, (id) => {
        // The control panel posts command launches back through the
        // command-palette's executeCommandById API.
        void (this.app as App & {
          commands: { executeCommandById: (id: string) => boolean };
        }).commands.executeCommandById(id);
      }));

    this.statusBar = new StatusBar(this.addStatusBarItem(), () => this.settings);
    this.registerInterval(window.setInterval(() => this.statusBar?.refresh(), 30_000));
    void this.statusBar.refresh();

    // Phase 1-6 axis run commands.
    for (const [id, file] of Object.entries(AXIS_TO_PROMPT)) {
      this.addCommand({
        id: `ralph-run-${id}`,
        name: `Ralph: Run ${id} pass`,
        callback: () => this.runOneAxis(file, id),
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
      },
    });

    this.addCommand({
      id: "ralph-pause",
      name: "Ralph: Pause (touch 90-Meta/STOP)",
      callback: async () => {
        await touchStop(this.settings);
        new Notice("Ralph paused");
        void this.statusBar?.refresh();
      },
    });

    this.addCommand({
      id: "ralph-resume",
      name: "Ralph: Resume",
      callback: async () => {
        await removeStop(this.settings);
        new Notice("Ralph resumed");
        void this.statusBar?.refresh();
      },
    });

    this.addCommand({
      id: "ralph-self-test",
      name: "Ralph: Run self-test (local CI mirror)",
      callback: () => this.spawnHarness(["self-test"], "self-test"),
    });

    this.addCommand({
      id: "ralph-open-log",
      name: "Ralph: Open log view",
      callback: () => this.activateView(LOG_VIEW_TYPE),
    });

    this.addCommand({
      id: "ralph-open-metrics",
      name: "Ralph: Open metrics view",
      callback: () => this.activateView(METRICS_VIEW_TYPE),
    });

    this.addCommand({
      id: "ralph-control-panel",
      name: "Ralph: Open Control Panel",
      callback: () => this.activateView(CONTROL_PANEL_VIEW_TYPE),
    });

    // Round 6 commands (master spec set).

    this.addCommand({
      id: "ralph-run-full-index",
      name: "Ralph: Run Full Index",
      callback: () => this.spawnHarness(["embed", "--vault-full"], "full-index"),
    });

    this.addCommand({
      id: "ralph-run-memory-index",
      name: "Ralph: Run Memory Index",
      callback: () => this.spawnHarness(["embed", "--since", "24h"], "memory-index"),
    });

    this.addCommand({
      id: "ralph-compress-current",
      name: "Ralph: Compress Current Note",
      callback: () => this.actOnCurrentNote("compress", async (rel) => {
        await runHarness(this.settings, ["compress", "--note", rel], line =>
          this.statusBar?.appendLog(line));
      }),
    });

    this.addCommand({
      id: "ralph-skill-from-note",
      name: "Ralph: Generate Skill From Current Note",
      callback: () => this.actOnCurrentNote("skill", async (rel) => {
        await runCommandPromptOnNote(
          this.settings, "ralph-skill.md", rel,
          line => this.statusBar?.appendLog(line),
        );
        new Notice(`Ralph: skill candidate proposed from ${rel} (review 40-Skills/)`);
      }),
    });

    this.addCommand({
      id: "ralph-experiment-from-note",
      name: "Ralph: Generate Experiment From Current Note",
      callback: () => this.actOnCurrentNote("experiment", async (rel) => {
        await runCommandPromptOnNote(
          this.settings, "ralph-experiment.md", rel,
          line => this.statusBar?.appendLog(line),
        );
        new Notice(`Ralph: experiment fixture proposed from ${rel} (review harness/fixtures/)`);
      }),
    });

    this.addCommand({
      id: "ralph-promote-canonical",
      name: "Ralph: Promote Current Note To Canonical Memory",
      callback: () => this.actOnCurrentNote("promote", async (rel) => {
        await this.appendFrontmatterFlag(rel, "stability", "canonical");
        new Notice(`Marked ${rel} stability: canonical (HIGH-risk; review).`);
      }),
    });

    this.addCommand({
      id: "ralph-archive-stale",
      name: "Ralph: Archive Stale Context",
      callback: () => this.spawnHarness(
        ["compress", "--older-than", "7d"], "archive-stale"),
    });

    this.addCommand({
      id: "ralph-detect-duplicates",
      name: "Ralph: Detect Duplicate Memory",
      callback: () => this.spawnHarness(
        ["query", "--semantic", "duplicates", "--k", "20"], "detect-duplicates"),
    });

    this.addCommand({
      id: "ralph-create-business-approval",
      name: "Ralph: Create Business Approval Request",
      // install.sh seeds pending-approvals.md into the vault at
      // 07_Business/pending-approvals.md (Round-2 master-spec layout).
      // The repo-side business-entity/ledgers/pending-approvals.md is
      // the SCHEMA source — copied during seed but lives at a different
      // vault path. Try the seeded path first; fall back to the schema
      // path so trees that haven't been seeded still find SOMETHING.
      callback: () => this.openVaultFileWithFallback([
        "07_Business/pending-approvals.md",
        "business-entity/ledgers/pending-approvals.md",
      ]),
    });

    this.addCommand({
      id: "ralph-open-provider-registry",
      name: "Ralph: Open Provider Registry",
      callback: () => this.openVaultFile("00_System/Provider Registry.md"),
    });

    this.addCommand({
      id: "ralph-open-migration-control",
      name: "Ralph: Open Migration Control Panel",
      callback: () => this.openVaultFile("00_System/Repo Migration Control Panel.md"),
    });

    this.addCommand({
      id: "ralph-vault-diagnostics",
      name: "Ralph: Run Vault Diagnostics",
      callback: () => this.runVaultDiagnostics(),
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

  private async runOneAxis(promptFile: string, axisId: string) {
    new Notice(`Ralph: ${axisId} pass started`);
    const code = await runAxis(this.settings, promptFile, line => this.statusBar?.appendLog(line));
    new Notice(`Ralph: ${axisId} exited (${code})`);
    void this.statusBar?.refresh();
  }

  private async spawnHarness(args: string[], label: string) {
    new Notice(`Ralph: ${label} started`);
    const code = await runHarness(this.settings, args, line => this.statusBar?.appendLog(line));
    new Notice(`Ralph: ${label} exited (${code})`);
    void this.statusBar?.refresh();
  }

  private async actOnCurrentNote(label: string, fn: (rel: string) => Promise<void>) {
    const file = this.app.workspace.getActiveFile();
    if (!file) {
      new Notice("Ralph: open a note first");
      return;
    }
    new Notice(`Ralph: ${label} → ${file.path}`);
    try {
      await fn(file.path);
    } catch (e) {
      new Notice(`Ralph: ${label} failed: ${e instanceof Error ? e.message : String(e)}`);
    }
    void this.statusBar?.refresh();
  }

  private async appendFrontmatterFlag(rel: string, key: string, value: string) {
    if (!this.settings.vaultRoot) throw new Error("vaultRoot not set");
    const full = path.join(this.settings.vaultRoot, rel);
    const text = await fs.readFile(full, "utf8");
    if (!text.startsWith("---")) {
      throw new Error(`${rel}: no frontmatter to update`);
    }
    const end = text.indexOf("\n---", 3);
    if (end < 0) throw new Error(`${rel}: malformed frontmatter`);
    const front = text.slice(3, end);
    const rest = text.slice(end + 4);
    const re = new RegExp(`^${key}:.*$`, "m");
    let newFront: string;
    if (re.test(front)) {
      newFront = front.replace(re, `${key}: ${value}`);
    } else {
      newFront = front.trimEnd() + `\n${key}: ${value}\n`;
    }
    // Normalize: ensure exactly one trailing newline so the closing
    // `---` always starts on its own line. Without this, when the
    // regex replaces an existing line (or appends a new one without
    // a trailing newline), the rewrite glues `<value>---` together
    // and downstream YAML parsers see corrupt frontmatter. Mirrors
    // the harness/reflect.py fix.
    const normalizedFront = newFront.replace(/\n+$/, "") + "\n";
    await fs.writeFile(full, "---" + normalizedFront + "---" + rest, "utf8");
  }

  private async openVaultFile(rel: string) {
    if (!this.settings.vaultRoot) {
      new Notice("Ralph: vaultRoot not set");
      return;
    }
    const file = this.app.vault.getAbstractFileByPath(rel);
    if (file && "path" in file) {
      await this.app.workspace.getLeaf().openFile(file as never);
    } else {
      new Notice(`Ralph: ${rel} not found in vault`);
    }
  }

  // Open the first path that exists in the vault. Useful when the same
  // logical file might live at the seeded path OR the schema-source path
  // (e.g. pending-approvals.md → 07_Business/ vs business-entity/ledgers/).
  private async openVaultFileWithFallback(rels: string[]) {
    if (!this.settings.vaultRoot) {
      new Notice("Ralph: vaultRoot not set");
      return;
    }
    for (const rel of rels) {
      const file = this.app.vault.getAbstractFileByPath(rel);
      if (file && "path" in file) {
        await this.app.workspace.getLeaf().openFile(file as never);
        return;
      }
    }
    new Notice(`Ralph: none of ${rels.join(" / ")} found in vault`);
  }

  private async runVaultDiagnostics() {
    new Notice("Ralph: running vault diagnostics");
    await runShim(this.settings, "ralph_validate_frontmatter.sh", [], line =>
      this.statusBar?.appendLog(line));
    await runShim(this.settings, "ralph_check_links.sh", [], line =>
      this.statusBar?.appendLog(line));
    new Notice("Ralph: diagnostics complete; check log view for details");
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
      .setDesc("Absolute path to the agent_testplayground checkout.")
      .addText(t => t
        .setPlaceholder("/Users/me/code/agent_testplayground")
        .setValue(this.plugin.settings.repoRoot)
        .onChange(async v => { this.plugin.settings.repoRoot = v.trim(); await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Vault path")
      .setDesc("Auto-detected from Obsidian; override only if needed.")
      .addText(t => t
        .setValue(this.plugin.settings.vaultRoot)
        .onChange(async v => { this.plugin.settings.vaultRoot = v.trim(); await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("User identity (metadata only)")
      .setDesc("Never used for OAuth / login. Default empty per docs/SECURITY_PRIVACY.md.")
      .addText(t => t
        .setValue(this.plugin.settings.userIdentityEmail)
        .onChange(async v => { this.plugin.settings.userIdentityEmail = v.trim(); await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Compression threshold (words)")
      .setDesc("Notes above this size become compress candidates.")
      .addText(t => t
        .setValue(String(this.plugin.settings.compressionThreshold))
        .onChange(async v => {
          const n = parseInt(v, 10);
          if (Number.isFinite(n) && n > 0) {
            this.plugin.settings.compressionThreshold = n;
            await this.plugin.saveSettings();
          }
        }));

    new Setting(containerEl)
      .setName("Hot memory window (days)")
      .addText(t => t
        .setValue(String(this.plugin.settings.hotMemoryWindowDays))
        .onChange(async v => {
          const n = parseInt(v, 10);
          if (Number.isFinite(n) && n > 0) {
            this.plugin.settings.hotMemoryWindowDays = n;
            await this.plugin.saveSettings();
          }
        }));

    new Setting(containerEl)
      .setName("Cold memory window (days)")
      .addText(t => t
        .setValue(String(this.plugin.settings.coldMemoryWindowDays))
        .onChange(async v => {
          const n = parseInt(v, 10);
          if (Number.isFinite(n) && n > 0) {
            this.plugin.settings.coldMemoryWindowDays = n;
            await this.plugin.saveSettings();
          }
        }));

    new Setting(containerEl)
      .setName("Enable experimental commands")
      .setDesc("Surfaces HIGH-risk commands; default off.")
      .addToggle(t => t
        .setValue(this.plugin.settings.enableExperimentalCommands)
        .onChange(async v => { this.plugin.settings.enableExperimentalCommands = v; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Enable auto-compression")
      .setDesc("Allows the plugin to compress without confirming each note.")
      .addToggle(t => t
        .setValue(this.plugin.settings.enableAutoCompression)
        .onChange(async v => { this.plugin.settings.enableAutoCompression = v; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Enable graph ranking")
      .setDesc("Reserved; off by default.")
      .addToggle(t => t
        .setValue(this.plugin.settings.enableGraphRanking)
        .onChange(async v => { this.plugin.settings.enableGraphRanking = v; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Enable business-entity scaffold")
      .setDesc("Show business-entity routes (control panel, ledgers).")
      .addToggle(t => t
        .setValue(this.plugin.settings.enableBusinessEntityScaffold)
        .onChange(async v => { this.plugin.settings.enableBusinessEntityScaffold = v; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Enable provider-neutral scaffold")
      .setDesc("Show provider registry route.")
      .addToggle(t => t
        .setValue(this.plugin.settings.enableProviderNeutralScaffold)
        .onChange(async v => { this.plugin.settings.enableProviderNeutralScaffold = v; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Claude binary")
      .setDesc("Defaults to `claude` on PATH.")
      .addText(t => t
        .setPlaceholder("claude")
        .setValue(this.plugin.settings.claudeBin)
        .onChange(async v => { this.plugin.settings.claudeBin = v.trim() || "claude"; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Python binary")
      .setDesc("Defaults to `python3` on PATH.")
      .addText(t => t
        .setPlaceholder("python3")
        .setValue(this.plugin.settings.pythonBin)
        .onChange(async v => { this.plugin.settings.pythonBin = v.trim() || "python3"; await this.plugin.saveSettings(); }));

    new Setting(containerEl)
      .setName("Max iterations per pass")
      .setDesc("Mirrors ralph-wiggum --max-iterations.")
      .addText(t => t
        .setValue(String(this.plugin.settings.maxIterations))
        .onChange(async v => {
          const n = parseInt(v, 10);
          if (Number.isFinite(n) && n > 0) {
            this.plugin.settings.maxIterations = n;
            await this.plugin.saveSettings();
          }
        }));
  }
}
