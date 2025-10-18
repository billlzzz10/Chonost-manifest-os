import EventEmitter from "eventemitter3";
import { buildPlan } from "./planner.js";
import { executePlan } from "./executor.js";
import { verify } from "./verifier.js";
import type {
  AgentConfig,
  AgentEventMap,
  AgentMode,
  ExecutionResult,
  Plan,
  TaskInput
} from "./types.js";

export interface AgentRunResult {
  plan: Plan;
  executions: ExecutionResult[];
}

export class Agent extends EventEmitter<AgentEventMap> {
  private readonly config: AgentConfig;

  constructor(config: AgentConfig = {}) {
    super();
    this.config = {
      maxSteps: config.maxSteps ?? 8,
      model: config.model,
      baseUrl: config.baseUrl,
      temperature: config.temperature ?? 0
    };
  }

  async run(mode: AgentMode, input: TaskInput): Promise<AgentRunResult> {
    try {
      const plan = buildPlan(input);
      this.emit("agent:plan", plan);

      if (mode === "architect") {
        this.emit("agent:complete", { summary: plan.summary, output: "" });
        return { plan, executions: [] };
      }

      const executions = await executePlan(
        plan,
        input,
        this.config,
        {
          stream: mode !== "coder" ? true : false,
          onDelta: (delta, step) => {
            if (delta.type === "text") {
              this.emit("agent:step-start", step);
            }
          }
        }
      );

      for (const execution of executions) {
        this.emit("agent:step-end", execution);
      }

      if (mode === "debugger") {
        const issues = verify(executions);
        for (const issue of issues) {
          this.emit("agent:issue", issue);
        }
      }

      const output = executions.map((item) => item.output).join("\n\n");
      this.emit("agent:complete", { summary: plan.summary, output });
      return { plan, executions };
    } catch (error) {
      this.emit("agent:error", {
        message: error instanceof Error ? error.message : "Unknown agent error",
        cause: error
      });
      throw error;
    }
  }
}

export function createAgent(config: AgentConfig = {}): Agent {
  return new Agent(config);
}
