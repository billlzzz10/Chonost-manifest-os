import { describe, expect, it } from "vitest";
import { completeText, streamText } from "../src/stream.js";
import { createMockFetch } from "../src/testing/mockFetch.js";
import type { CompletionDelta } from "../src/types.js";

const mockLines = [
  JSON.stringify({
    message: { role: "assistant", content: "Hello" },
    done: false
  }),
  JSON.stringify({
    message: { role: "assistant", content: ", world!" },
    done: false
  }),
  JSON.stringify({
    done: true,
    prompt_eval_count: 12,
    eval_count: 6
  })
];

describe("ai-runtime", () => {
  it("merges streamed chunks into a completion", async () => {
    const result = await completeText(
      {
        model: "mock",
        messages: [{ role: "user", content: "Say hello" }]
      },
      { fetchImpl: createMockFetch(mockLines) }
    );

    expect(result.text).toBe("Hello, world!");
    expect(result.usage?.inputTokens).toBe(12);
    expect(result.usage?.outputTokens).toBe(6);
  });

  it("yields streaming deltas", async () => {
    const deltas: CompletionDelta[] = [];
    const iterator = streamText(
      {
        model: "mock",
        messages: [{ role: "user", content: "Say hello" }]
      },
      { fetchImpl: createMockFetch(mockLines) }
    );

    for await (const delta of iterator) {
      deltas.push(delta);
    }

    expect(deltas.filter((delta) => delta.type === "text")).toHaveLength(2);
    expect(deltas.some((delta) => delta.type === "usage")).toBe(true);
  });
});
