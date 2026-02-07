// 🛡️ Guardian: The hardcoded AIProvider enum has been removed.
// The list of available providers is now fetched dynamically from the backend
// to ensure a single source of truth.

export interface AIConfig {
  provider: string;
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

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

let currentProvider: string = '';
let currentModel: string | undefined = undefined;

export const getAIProviders = async (): Promise<string[]> => {
  const apiUrl = `${API_BASE_URL}/api/v1/providers`;
  const response = await fetch(apiUrl);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch AI providers');
  }
  const data = await response.json();
  return data.providers;
};

export const getAIModels = async (provider: string): Promise<string[]> => {
  if (!provider) return [];
  const apiUrl = `${API_BASE_URL}/api/v1/providers/${provider}/models`;
  const response = await fetch(apiUrl);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch AI models');
  }
  const data = await response.json();
  return data.models;
};

export const initializeAIService = (config: AIConfig): void => {
  currentProvider = config.provider;
  currentModel = config.model;
};

export const chatWithAI = async (messages: Message[]): Promise<string> => {
  if (!currentProvider) {
    throw new Error('AI provider not set');
  }

  const apiUrl = `${API_BASE_URL}/api/v1/chat`;

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

export const setProvider = (provider: string, apiKey: string, model?: string): void => {
  initializeAIService({ provider, apiKey, model });
};
