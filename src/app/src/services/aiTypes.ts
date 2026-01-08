// 🛡️ Guardian: Extracted shared AI types to break circular dependencies.
// This file centralizes types used across multiple AI service modules,
// preventing circular import issues and improving architectural clarity.

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
