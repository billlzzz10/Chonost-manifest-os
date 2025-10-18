import { z } from "zod";

export const messageSchema = z.object({
  role: z.enum(["system", "user", "assistant", "tool"]),
  content: z.string(),
  name: z.string().optional()
});

export type Message = z.infer<typeof messageSchema>;

export const toolCallSchema = z.object({
  name: z.string(),
  arguments: z.union([z.string(), z.record(z.any())]).optional()
});

export type ToolCall = z.infer<typeof toolCallSchema>;

export const completionInputSchema = z.object({
  model: z.string().min(1),
  messages: z.array(messageSchema).min(1),
  temperature: z.number().min(0).max(2).default(0),
  topP: z.number().min(0).max(1).default(1),
  maxTokens: z.number().positive().int().optional(),
  stream: z.boolean().default(true),
  tools: z
    .array(
      z.object({
        name: z.string(),
        description: z.string().optional(),
        schema: z.record(z.any()).optional()
      })
    )
    .default([]),
  metadata: z.record(z.any()).default({})
});

export type CompletionInput = z.infer<typeof completionInputSchema>;

export type CompletionDelta =
  | { type: "text"; text: string }
  | { type: "tool"; tool: ToolCall }
  | { type: "reasoning"; text: string }
  | { type: "usage"; inputTokens: number; outputTokens: number };

export interface CompletionResult {
  text: string;
  toolCalls: ToolCall[];
  usage?: {
    inputTokens: number;
    outputTokens: number;
  };
  metadata: Record<string, unknown>;
}

export type FetchImplementation = (
  input: string | URL | Request,
  init?: RequestInit
) => Promise<Response>;
