import { Action, ActionPanel, Form, getPreferenceValues, showToast, Toast } from "@raycast/api";
import { useState } from "react";

interface Prefs { voiceUrl: string; }

export default function Capture() {
  const { voiceUrl } = getPreferenceValues<Prefs>();
  const [text, setText] = useState("");

  async function submit(values: { thought: string }) {
    const body = new URLSearchParams({ text: values.thought, source: "raycast" });
    try {
      const r = await fetch(`${voiceUrl.replace(/\/$/, "")}/ralph/voice`, {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = (await r.json()) as { wrote?: string };
      await showToast({ style: Toast.Style.Success, title: "Captured", message: j.wrote ?? "" });
    } catch (e) {
      await showToast({
        style: Toast.Style.Failure,
        title: "Capture failed",
        message: e instanceof Error ? e.message : String(e),
      });
    }
  }

  return (
    <Form
      actions={
        <ActionPanel>
          <Action.SubmitForm title="Capture" onSubmit={submit} />
        </ActionPanel>
      }
    >
      <Form.TextArea
        id="thought"
        title="Thought"
        placeholder="What goes in the inbox?"
        value={text}
        onChange={setText}
      />
    </Form>
  );
}
