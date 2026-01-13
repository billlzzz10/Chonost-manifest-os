// This file was refactored to remove the internal, duplicate `GoogleAIService` class.
// It now imports the canonical service from `./googleAIService.ts` to ensure a single source of truth.
import { GoogleAIService } from './googleAIService';
import { OpenAIService } from './openAIService';
import { AnthropicService } from './anthropicService';

import { AIProvider, AIConfig, Message } from './aiTypes';


let currentService: any = null;
let currentProvider: AIProvider = AIProvider.GOOGLE;

export const initializeAIService = (config: AIConfig): void => {
  const { provider, apiKey, model } = config;
  currentProvider = provider;

  switch (provider) {
    case AIProvider.GOOGLE:
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
