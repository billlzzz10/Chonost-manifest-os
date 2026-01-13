import { Anthropic } from '@anthropic-ai/sdk';
import { Message } from './aiTypes';

export class AnthropicService {
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
