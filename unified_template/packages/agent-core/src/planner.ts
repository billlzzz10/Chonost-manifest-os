import { v4 as uuid } from "uuid";
import type { Plan, PlanStep, TaskInput } from "./types.js";

const FALLBACK_STEPS = [
  "Analyse the task and gather context",
  "Produce the artefact or run the command",
  "Verify the outcome and note follow-ups"
];

export function buildPlan(input: TaskInput): Plan {
  const tokens = tokenise(input.task);
  const steps = tokens.length > 1 ? tokens : FALLBACK_STEPS;

  const planSteps: PlanStep[] = steps.map((step, index) => ({
    id: uuid(),
    title: step,
    detail: deriveDetail(step, index, input.task),
    status: "pending"
  }));

  return {
    summary: `Plan for: ${input.task}`,
    steps: planSteps
  };
}

function tokenise(task: string): string[] {
  return task
    .split(/[.;\n]/)
    .map((chunk) => chunk.trim())
    .filter((chunk) => chunk.length > 6);
}

function deriveDetail(step: string, index: number, task: string): string {
  if (index === 0) {
    return `Clarify requirements for "${task}" and collect relevant files or notes.`;
  }
  if (step.toLowerCase().includes("verify") || step.toLowerCase().includes("test")) {
    return "Run automated checks and document remaining risks.";
  }
  return step;
}
