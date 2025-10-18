import { completeText, streamText } from "@unified/ai-runtime";
import type { CompletionDelta } from "@unified/ai-runtime";
import type { AgentConfig, ExecutionResult, Plan, PlanStep, TaskInput } from "./types.js";

export interface ExecutionOptions {
  stream?: boolean;
  onDelta?: (delta: CompletionDelta, step: PlanStep) => void;
}

export async function executePlan(
  plan: Plan,
  input: TaskInput,
  config: AgentConfig,
  options: ExecutionOptions = {}
): Promise<ExecutionResult[]> {
  const results: ExecutionResult[] = [];

  for (const step of plan.steps) {
    step.status = "running";
    const result = options.stream
      ? await runStream(step, input, config, options)
      : await runComplete(step, input, config);
    results.push(result);
    step.status = "completed";
  }

  return results;
}

async function runComplete(
  step: PlanStep,
  input: TaskInput,
  config: AgentConfig
): Promise<ExecutionResult> {
  const prompt = buildPrompt(step, input);
  const completion = await completeText({
    model: config.model ?? "qwen2.5-coder",
    messages: [
      { role: "system", content: "You are a helpful software engineering assistant." },
      { role: "user", content: prompt }
    ],
    temperature: config.temperature ?? 0
  });

  return {
    stepId: step.id,
    output: completion.text,
    toolsInvoked: completion.toolCalls,
    reasoning: deriveReasoning(completion.text)
  };
}

async function runStream(
  step: PlanStep,
  input: TaskInput,
  config: AgentConfig,
  options: ExecutionOptions
): Promise<ExecutionResult> {
  const prompt = buildPrompt(step, input);
  const chunks: string[] = [];
  const tools: ExecutionResult["toolsInvoked"] = [];
  let reasoning = "";

  const iterator = streamText(
    {
      model: config.model ?? "qwen2.5-coder",
      messages: [
        { role: "system", content: "You are a helpful software engineering assistant." },
        { role: "user", content: prompt }
      ],
      temperature: config.temperature ?? 0
    },
    {}
  );

  for await (const delta of iterator) {
    if (options.onDelta) {
      options.onDelta(delta, step);
    }
    if (delta.type === "text") {
      chunks.push(delta.text);
    } else if (delta.type === "tool") {
      tools.push({ name: delta.tool.name, arguments: delta.tool.arguments ?? {} });
    } else if (delta.type === "reasoning") {
      reasoning += delta.text;
    }
  }

  return {
    stepId: step.id,
    output: chunks.join(""),
    toolsInvoked: tools,
    reasoning: reasoning || deriveReasoning(chunks.join(""))
  };
}

function buildPrompt(step: PlanStep, input: TaskInput): string {
  const context = JSON.stringify(input.context ?? {}, null, 2);
  return [
    `Task: ${input.task}`,
    `Current step: ${step.title}`,
    `Detail: ${step.detail}`,
    `Context: ${context}`,
    "Provide actionable output and list follow-up tasks if needed."
  ].join("\n");
}

function deriveReasoning(output: string): string {
  const snippet = output.split("\n").slice(0, 3).join("\n");
  return snippet.trim();
}
