import { GoogleGenerativeAI } from '@google/generative-ai';
import OpenAI from 'openai';
import { Anthropic } from '@anthropic-ai/sdk';

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

class GoogleAIService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(apiKey: string, model = 'gemini-1.5-flash') {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model });
  }

  async chat(messages: Message[]): Promise<string> {
    const conversation = messages.map(msg =>
      `${msg.role === 'user' ? 'ผู้ใช้' : 'AI'}: ${msg.content}`
    ).join('\n\n');
    const prompt = `สนทนาต่อไปนี้:\n\n${conversation}\n\nAI: `;
    const result = await this.model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }
}

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

// ⚡ Bolt: Cache AI service instances to avoid redundant instantiation.
const serviceCache: Record<string, any> = {};

let currentService: any = null;
let currentProvider: AIProvider = AIProvider.GOOGLE;

export const initializeAIService = (config: AIConfig): void => {
  const { provider, apiKey, model } = config;
  const cacheKey = `${provider}-${apiKey}-${model || ''}`;

  // ⚡ Bolt: Reuse cached service if available.
  if (serviceCache[cacheKey]) {
    currentService = serviceCache[cacheKey];
    currentProvider = provider;
    return;
  }

  currentProvider = provider;

  switch (provider) {
    case AIProvider.GOOGLE:
      currentService = new GoogleAIService(apiKey, model);
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

  // ⚡ Bolt: Store the new service instance in the cache.
  serviceCache[cacheKey] = currentService;
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