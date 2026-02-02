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

// 🛡️ Guardian: Refactored to use the backend's unified AI endpoint.
// This service now acts as a client for the backend, which centrally manages all AI provider interactions.
// This change improves security by keeping API keys off the frontend and simplifies maintenance.

let currentProvider: AIProvider = AIProvider.GOOGLE;
let currentModel: string | undefined = undefined;

export const initializeAIService = (config: AIConfig): void => {
  currentProvider = config.provider;
  currentModel = config.model;
};

export const chatWithAI = async (messages: Message[]): Promise<string> => {
  if (!currentProvider) {
    throw new Error('AI provider not set');
  }

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1/chat';

  const response = await fetch(apiUrl, {
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
    throw new Error(errorData.detail || 'Failed to chat with AI');
  }

  const data = await response.json();
  return data.content;
};

export const setProvider = (provider: AIProvider, apiKey: string, model?: string): void => {
  initializeAIService({ provider, apiKey, model });
};
