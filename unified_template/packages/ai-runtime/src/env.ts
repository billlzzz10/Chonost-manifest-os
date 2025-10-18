const DEFAULT_BASE_URL = process.env.OLLAMA_BASE_URL ?? "http://localhost:11434";
const DEFAULT_MODEL = process.env.OLLAMA_MODEL ?? "qwen2.5-coder";

export interface RuntimeEnvironment {
  baseUrl: string;
  model: string;
}

export function resolveEnvironment(overrides?: Partial<RuntimeEnvironment>): RuntimeEnvironment {
  return {
    baseUrl: overrides?.baseUrl ?? DEFAULT_BASE_URL,
    model: overrides?.model ?? DEFAULT_MODEL
  };
}
