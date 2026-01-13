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
