// 🛡️ Guardian: Consolidated from internal class to canonical GoogleAIService
// This file was refactored to remove the internal, duplicate `GoogleAIService` class.
// It now imports the canonical service from `./googleAIService.ts` to ensure a single source of truth.
export enum AIProvider {
  GOOGLE = 'google',
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
  XAI = 'xai'
}

export interface AIConfig {
  provider: AIProvider;
  apiKey: string;
  model?: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

let currentProvider: AIProvider = AIProvider.GOOGLE;
let currentModel: string | undefined;

export const initializeAIService = (config: AIConfig): void => {
  currentProvider = config.provider;
  currentModel = config.model;
};

export const chatWithAI = async (messages: Message[]): Promise<string> => {
  const response = await fetch('http://localhost:8000/api/v1/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      provider: currentProvider,
      messages: messages,
      model: currentModel,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch from chat API');
  }

  const data = await response.json();
  return data.content;
};

export const setProvider = (provider: AIProvider, apiKey: string, model?: string): void => {
  initializeAIService({ provider, apiKey, model });
};
