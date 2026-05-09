import { Action, ActionPanel, getPreferenceValues, List, showToast, Toast } from "@raycast/api";

interface Prefs { voiceUrl: string; }
const AXES = ["research", "memory", "skills", "interaction", "compress", "heal", "evolve", "update"];

export default function Run() {
  const { voiceUrl } = getPreferenceValues<Prefs>();

  async function trigger(axis: string) {
    try {
      const r = await fetch(`${voiceUrl.replace(/\/$/, "")}/ralph/run`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ axis }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = (await r.json()) as { exit_code?: number; promise_seen?: boolean };
      await showToast({
        style: j.promise_seen ? Toast.Style.Success : Toast.Style.Animated,
        title: `${axis} → exit ${j.exit_code}${j.promise_seen ? " (COMPLETE)" : ""}`,
      });
    } catch (e) {
      await showToast({
        style: Toast.Style.Failure,
        title: `${axis} failed`,
        message: e instanceof Error ? e.message : String(e),
      });
    }
  }

  return (
    <List>
      {AXES.map(axis => (
        <List.Item
          key={axis}
          title={axis}
          actions={
            <ActionPanel>
              <Action title={`Run ${axis}`} onAction={() => trigger(axis)} />
            </ActionPanel>
          }
        />
      ))}
    </List>
  );
}
