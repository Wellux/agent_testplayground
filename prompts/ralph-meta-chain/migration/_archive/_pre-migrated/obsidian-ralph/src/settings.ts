export interface RalphSettings {
  repoPath: string;
  vaultPath: string;
  claudeBin: string;
  maxIterations: number;
}

export const DEFAULT_SETTINGS: RalphSettings = {
  repoPath: "",
  vaultPath: "",
  claudeBin: "claude",
  maxIterations: 8
};
