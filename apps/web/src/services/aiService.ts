// 🛡️ Guardian: The AIProvider enum was removed to establish the backend as the single source of truth.
// The provider list is now fetched dynamically via getAIProviders().

export interface AIConfig {
  provider: string;
  model?: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

// 🛡️ Guardian: Refactored to use the backend's unified AI endpoint.
// This service now acts as a client for the backend, which centrally manages all AI provider interactions.
// This change improves maintainability by centralizing the provider list on the backend.

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

let currentProvider: string | undefined;
let currentModel: string | undefined = undefined;

export const initializeAIService = (config: AIConfig): void => {
  currentProvider = config.provider;
  currentModel = config.model;
};

export const chatWithAI = async (messages: Message[]): Promise<string> => {
  if (!currentProvider) {
    throw new Error('AI provider not set');
  }

  const response = await fetch(`${API_BASE_URL}/chat`, {
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

export const setProvider = (provider: string, model?: string): void => {
  initializeAIService({ provider, model });
};

// 🛡️ Guardian: Fetches the list of available providers from the backend.
// This ensures the frontend is always in sync with the backend's capabilities.
export const getAIProviders = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/providers`);
    if (!response.ok) {
      throw new Error('Failed to fetch AI providers');
    }
    const data = await response.json();
    return data.providers || [];
  } catch (error) {
    console.error('Error fetching AI providers:', error);
    // Return a default empty list or handle the error as needed
    return [];
  }
};
