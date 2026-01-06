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

  // 🛡️ Guardian: Consolidated from src/services/googleAIService.ts (deleted)
  // This function was duplicated - moved to canonical location
  async generateResponse(prompt: string): Promise<string> {
    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Google AI Error:', error);
      throw new Error(`Google AI request failed: ${error}`);
    }
  }

  async chat(messages: Message[]): Promise<string> {
    const conversation = messages.map(msg =>
      `${msg.role === 'user' ? 'ผู้ใช้' : 'AI'}: ${msg.content}`
    ).join('\n\n');
    const prompt = `สนทนาต่อไปนี้:\n\n${conversation}\n\nAI: `;
    return this.generateResponse(prompt);
  }

  // 🛡️ Guardian: Consolidated from src/services/googleAIService.ts (deleted)
  // This function was missing from the central service
  async analyzeText(text: string, instruction?: string): Promise<string> {
    const prompt = instruction
      ? `${instruction}\n\nข้อความที่ต้องการวิเคราะห์:\n${text}`
      : `กรุณาวิเคราะห์ข้อความต่อไปนี้และให้ข้อมูลสรุปที่เป็นประโยชน์:\n\n${text}`;

    return this.generateResponse(prompt);
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

let currentService: any = null;
let currentProvider: AIProvider = AIProvider.GOOGLE;

export const initializeAIService = (config: AIConfig): void => {
  const { provider, apiKey, model } = config;
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