import OpenAI from 'openai';
import { Message } from './aiTypes';

export class OpenAIService {
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
