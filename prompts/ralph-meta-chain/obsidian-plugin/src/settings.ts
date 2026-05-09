// Ralph Meta Chain plugin settings — master-spec shape. No secrets stored.

export interface RalphSettings {
  // Paths
  vaultRoot: string;             // auto-detected from Obsidian
  repoRoot: string;              // absolute path to agent_testplayground checkout

  // Identity (metadata only — never used for OAuth / login)
  userIdentityEmail: string;     // intentionally never stored as the user's real email by default

  // Compression / lifecycle thresholds
  compressionThreshold: number;  // word-count threshold above which a note is compress-eligible
  hotMemoryWindowDays: number;
  coldMemoryWindowDays: number;

  // Feature flags (all default-off except the always-safe scaffolds)
  enableExperimentalCommands: boolean;
  enableAutoCompression: boolean;
  enableGraphRanking: boolean;
  enableBusinessEntityScaffold: boolean;
  enableProviderNeutralScaffold: boolean;

  // Runtime
  claudeBin: string;             // default "claude"
  pythonBin: string;             // default "python3"
  maxIterations: number;         // mirrors ralph-wiggum --max-iterations
}

export const DEFAULT_SETTINGS: RalphSettings = {
  vaultRoot: "",
  repoRoot: "",
  userIdentityEmail: "",         // The user fills this in manually if desired; default empty per docs/SECURITY_PRIVACY.md
  compressionThreshold: 4000,
  hotMemoryWindowDays: 7,
  coldMemoryWindowDays: 90,
  enableExperimentalCommands: false,
  enableAutoCompression: false,
  enableGraphRanking: false,
  enableBusinessEntityScaffold: true,
  enableProviderNeutralScaffold: true,
  claudeBin: "claude",
  pythonBin: "python3",
  maxIterations: 8,
};
