import { useState } from "react";
import { Button, Card, CommandMenu, Stack } from "@unified/ui";
import { sendMessage } from "./api.js";

function App() {
  const [conversationId] = useState(() => crypto.randomUUID());
  const [input, setInput] = useState("Summarise the latest manuscript edits.");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const actions = [
    {
      id: "summarise",
      label: "Summarise draft",
      onSelect: () => setInput("Summarise the latest manuscript edits."),
      shortcut: "S"
    },
    {
      id: "outline",
      label: "Generate outline",
      onSelect: () => setInput("Create a chapter outline for the manuscript."),
      shortcut: "O"
    },
    {
      id: "qa",
      label: "Ask questions about memory",
      onSelect: () => setInput("What open issues remain in the manuscript?"),
      shortcut: "Q"
    }
  ];

  async function handleSend() {
    setLoading(true);
    try {
      const result = await sendMessage({ conversationId, message: input });
      setResponse(result);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[var(--ui-surface)] text-[var(--ui-text)]">
      <main className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-10">
        <header>
          <h1 className="text-3xl font-semibold">Unified Template Dashboard</h1>
          <p className="text-[var(--ui-text-muted)]">
            Local-first interface for orchestrating agents, reviewing context, and collaborating with the backend.
          </p>
        </header>

        <Card>
          <Stack gap="md">
            <label className="text-sm text-[var(--ui-text-muted)]">Quick actions</label>
            <CommandMenu items={actions} />
          </Stack>
        </Card>

        <Card className="flex flex-col gap-4">
          <textarea
            className="min-h-[120px] resize-y rounded-lg border border-[var(--ui-border)] bg-[var(--ui-surface)] p-3 text-sm text-[var(--ui-text)] focus:outline-none"
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <div className="flex items-center justify-between">
            <span className="text-xs text-[var(--ui-text-muted)]">Conversation: {conversationId}</span>
            <Button onClick={handleSend} disabled={loading}>
              {loading ? "Thinking…" : "Send"}
            </Button>
          </div>
        </Card>

        {response ? (
          <Card>
            <h2 className="text-lg font-medium">Response</h2>
            <pre className="mt-3 whitespace-pre-wrap text-sm text-[var(--ui-text)]">{response}</pre>
          </Card>
        ) : null}
      </main>
    </div>
  );
}

export default App;
