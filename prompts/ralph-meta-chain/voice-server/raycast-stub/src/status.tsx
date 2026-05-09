import { getPreferenceValues, List } from "@raycast/api";
import { useEffect, useState } from "react";

interface Prefs { voiceUrl: string; }
interface AxisState { date?: string; status?: string }
interface Status { stopped?: boolean; state?: Record<string, AxisState>; }

const AXES = ["research", "memory", "skills", "interaction", "compress", "heal", "evolve", "update"];

export default function Statuses() {
  const { voiceUrl } = getPreferenceValues<Prefs>();
  const [data, setData] = useState<Status | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${voiceUrl.replace(/\/$/, "")}/ralph/status`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        setData((await r.json()) as Status);
      } catch (e) {
        setErr(e instanceof Error ? e.message : String(e));
      }
    })();
  }, [voiceUrl]);

  if (err) return <List><List.EmptyView title="Error" description={err} /></List>;
  if (!data) return <List isLoading />;

  const today = new Date().toISOString().slice(0, 10);
  return (
    <List navigationTitle={data.stopped ? "Ralph (PAUSED)" : "Ralph"}>
      {AXES.map(axis => {
        const s = data.state?.[axis];
        const ok = s?.date === today && s?.status === "COMPLETE";
        return (
          <List.Item
            key={axis}
            icon={ok ? "✅" : "•"}
            title={axis}
            subtitle={s ? `${s.date ?? "—"} · ${s.status ?? "—"}` : "no run yet"}
          />
        );
      })}
    </List>
  );
}
