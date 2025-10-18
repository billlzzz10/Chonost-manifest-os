export type AgentMode = "architect" | "coder" | "debugger";

export interface AgentConfig {
  model?: string;
  maxSteps?: number;
  baseUrl?: string;
  temperature?: number;
}

export interface TaskInput {
  task: string;
  context?: Record<string, unknown>;
}

export interface PlanStep {
  id: string;
  title: string;
  detail: string;
  status: "pending" | "running" | "completed" | "skipped" | "failed";
}

export interface Plan {
  summary: string;
  steps: PlanStep[];
}

export interface ExecutionResult {
  stepId: string;
  output: string;
  reasoning?: string;
  toolsInvoked: Array<{ name: string; arguments: unknown }>;
}

export interface VerificationIssue {
  stepId: string;
  description: string;
  severity: "info" | "warn" | "error";
  suggestion?: string;
}

export interface AgentEventMap {
  "agent:plan": Plan;
  "agent:step-start": PlanStep;
  "agent:step-end": ExecutionResult;
  "agent:issue": VerificationIssue;
  "agent:complete": { summary: string; output: string };
  "agent:error": { message: string; cause?: unknown };
}
