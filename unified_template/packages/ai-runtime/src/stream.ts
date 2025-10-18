import type {
  CompletionDelta,
  CompletionInput,
  CompletionResult,
  FetchImplementation
} from "./types.js";
import { streamFromOllama } from "./providers/ollama.js";

export interface StreamOptions {
  signal?: AbortSignal;
  fetchImpl?: FetchImplementation;
}

export async function* streamText(
  input: CompletionInput,
  options: StreamOptions = {}
): AsyncGenerator<CompletionDelta, CompletionResult, unknown> {
  const deltas: CompletionDelta[] = [];
  for await (const delta of streamFromOllama(input, {
    signal: options.signal,
    fetchImpl: options.fetchImpl
  })) {
    deltas.push(delta);
    yield delta;
  }
  return normaliseResult(deltas);
}

export async function completeText(
  input: CompletionInput,
  options: StreamOptions = {}
): Promise<CompletionResult> {
  const deltas: CompletionDelta[] = [];
  for await (const delta of streamFromOllama(input, {
    signal: options.signal,
    fetchImpl: options.fetchImpl
  })) {
    deltas.push(delta);
  }
  return normaliseResult(deltas);
}

function normaliseResult(deltas: CompletionDelta[]): CompletionResult {
  const chunks: string[] = [];
  const toolCalls = [];
  let usage;

  for (const delta of deltas) {
    if (delta.type === "text" || delta.type === "reasoning") {
      chunks.push(delta.text);
    } else if (delta.type === "tool") {
      toolCalls.push(delta.tool);
    } else if (delta.type === "usage") {
      usage = {
        inputTokens: delta.inputTokens,
        outputTokens: delta.outputTokens
      };
    }
  }

  return {
    text: chunks.join(""),
    toolCalls,
    usage,
    metadata: {}
  };
}
