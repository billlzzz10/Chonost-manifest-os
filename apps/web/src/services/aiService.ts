// 🛡️ Guardian: Consolidated from internal class to canonical GoogleAIService
// This file was refactored to remove the internal, duplicate `GoogleAIService` class.
// It now imports the canonical service from `./googleAIService.ts` to ensure a single source of truth.
import OpenAI from 'openai';
import { Anthropic } from '@anthropic-ai/sdk';
import { GoogleAIService } from './googleAIService';

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

// 🛡️ Guardian: Removed duplicate GoogleAIService class.

class OpenAIService {
  private openai: OpenAI;
  private model: string;

  constructor(apiKey: string, baseURL?: string, model = 'gpt-3.5-turbo') {
    this.model = model;
    this.openai = new OpenAI({
      apiKey,
      baseURL: baseURL || 'https://api.openai.com/v1',
    });
  }

  async chat(messages: Message[]): Promise<string> {
    const response = await this.openai.chat.completions.create({
      model: this.model,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
    });
    return response.choices[0].message?.content || '';
  }
}

class AnthropicService {
  private anthropic: Anthropic;
  private model: string;

  constructor(apiKey: string, model = 'claude-3-sonnet-20240229') {
    this.model = model;
    this.anthropic = new Anthropic({ apiKey });
  }

  async chat(messages: Message[]): Promise<string> {
    const response = await this.anthropic.messages.create({
      model: this.model,
      max_tokens: 1000,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
    });
    return (response.content[0] as any).text || '';
  }
}

let currentService: any = null;
let currentProvider: AIProvider = AIProvider.GOOGLE;

export const initializeAIService = (config: AIConfig): void => {
  const { provider, apiKey, model } = config;
  currentProvider = provider;

  switch (provider) {
    case AIProvider.GOOGLE:
      // 🛡️ Guardian: Updated instantiation to match canonical service's constructor.
      currentService = new GoogleAIService({ apiKey, model });
      break;
    case AIProvider.OPENAI:
      currentService = new OpenAIService(apiKey, undefined, model);
      break;
    case AIProvider.ANTHROPIC:
      currentService = new AnthropicService(apiKey, model);
      break;
    case AIProvider.XAI:
      currentService = new OpenAIService(apiKey, 'https://api.x.ai/v1', model);
      break;
    default:
      throw new Error('Unsupported provider');
  }
};

export const getAIService = (): any => {
  if (!currentService) {
    throw new Error('AI service not initialized');
  }
  return currentService;
};

export const chatWithAI = async (messages: Message[]): Promise<string> => {
  if (!currentService) {
    throw new Error('AI service not initialized');
  }
  return currentService.chat(messages);
};

export const setProvider = (provider: AIProvider, apiKey: string, model?: string): void => {
  initializeAIService({ provider, apiKey, model });
};
