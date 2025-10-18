import { describe, expect, it, vi } from "vitest";
import { createAgent } from "../src/agent.js";

describe("agent-core", () => {
  it("produces a deterministic plan", async () => {
    const agent = createAgent({ model: "mock" });
    const spy = vi.fn();
    agent.on("agent:plan", spy);

    const result = await agent.run("architect", { task: "Write summary for chapter 1" });
    expect(result.plan.steps.length).toBeGreaterThan(0);
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
