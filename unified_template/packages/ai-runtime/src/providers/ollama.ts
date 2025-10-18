import { resolveEnvironment } from "../env.js";
import {
  CompletionDelta,
  CompletionInput,
  FetchImplementation,
  completionInputSchema
} from "../types.js";

export interface OllamaOptions {
  fetchImpl?: FetchImplementation;
  signal?: AbortSignal;
  baseUrl?: string;
}

interface OllamaChunk {
  message?: {
    role: string;
    content?: string;
    tool_calls?: Array<{ name: string; arguments?: unknown }>;
  };
  done?: boolean;
  error?: string;
  eval_count?: number;
  prompt_eval_count?: number;
}

const decoder = new TextDecoder();

export async function* streamFromOllama(
  rawInput: CompletionInput,
  options: OllamaOptions = {}
): AsyncGenerator<CompletionDelta, void, unknown> {
  const input = completionInputSchema.parse(rawInput);
  const env = resolveEnvironment({ baseUrl: options.baseUrl, model: input.model });
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;

  if (!fetchImpl) {
    throw new Error("fetch implementation is required");
  }

  const url = new URL("/api/chat", env.baseUrl);
  const response = await fetchImpl(url, {
    method: "POST",
    signal: options.signal,
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: input.model ?? env.model,
      messages: input.messages.map((message) => ({
        role: message.role,
        content: message.content
      })),
      stream: true,
      options: {
        temperature: input.temperature,
        top_p: input.topP,
        num_predict: input.maxTokens
      }
    })
  });

  if (!response.ok || !response.body) {
    throw new Error(`Ollama responded with ${response.status} ${response.statusText}`);
  }

  const reader = response.body.getReader();
  let buffer = "";
  let promptTokens = 0;
  let completionTokens = 0;

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    buffer = await emitBufferedChunks(buffer, (delta) => {
      if (delta.type === "usage") {
        promptTokens = delta.inputTokens;
        completionTokens = delta.outputTokens;
      }
      return delta;
    }, yield);
  }

  if (buffer.trim().length > 0) {
    await emitBufferedChunks(buffer + "\n", (delta) => {
      if (delta.type === "usage") {
        promptTokens = delta.inputTokens;
        completionTokens = delta.outputTokens;
      }
      return delta;
    }, yield);
  }

  if (promptTokens || completionTokens) {
    yield {
      type: "usage",
      inputTokens: promptTokens,
      outputTokens: completionTokens
    };
  }
}

type DeltaTransformer = (delta: CompletionDelta) => CompletionDelta;

async function emitBufferedChunks(
  buffer: string,
  transform: DeltaTransformer,
  emitter: (value: CompletionDelta) => unknown
): Promise<string> {
  let newlineIndex: number;
  let localBuffer = buffer;

  while ((newlineIndex = localBuffer.indexOf("\n")) !== -1) {
    const raw = localBuffer.slice(0, newlineIndex).trim();
    localBuffer = localBuffer.slice(newlineIndex + 1);
    if (!raw) {
      continue;
    }

    let parsed: OllamaChunk;
    try {
      parsed = JSON.parse(raw) as OllamaChunk;
    } catch (error) {
      console.error("[ai-runtime] failed to parse Ollama chunk", error);
      continue;
    }

    if (parsed.error) {
      throw new Error(parsed.error);
    }

    if (parsed.message?.content) {
      emitter(transform({ type: "text", text: parsed.message.content }));
    }

    if (parsed.message?.tool_calls?.length) {
      for (const toolCall of parsed.message.tool_calls) {
        emitter(
          transform({
            type: "tool",
            tool: {
              name: toolCall.name,
              arguments: toolCall.arguments
            }
          })
        );
      }
    }

    if (parsed.done) {
      const usage = {
        type: "usage" as const,
        inputTokens: parsed.prompt_eval_count ?? 0,
        outputTokens: parsed.eval_count ?? 0
      };
      emitter(transform(usage));
    }
  }
  return localBuffer;
}
