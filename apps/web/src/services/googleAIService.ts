// This file is now the single source of truth for all Google AI interactions.
// It removes the duplicate implementation from `aiService.ts` and exports a feature-complete class.
import { GoogleGenerativeAI } from '@google/generative-ai';
import { AIConfig, Message } from './aiTypes';

export class GoogleAIService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(config: AIConfig) {
    this.genAI = new GoogleGenerativeAI(config.apiKey);
    this.model = this.genAI.getGenerativeModel({
      model: config.model || 'gemini-1.5-flash'
    });
  }

  private async generateResponse(prompt: string): Promise<string> {
    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Google AI Error:', error);
      throw new Error(`Google AI request failed: ${error}`);
    }
  }

  async analyzeText(text: string, instruction?: string): Promise<string> {
    const prompt = instruction
      ? `${instruction}\n\nข้อความที่ต้องการวิเคราะห์:\n${text}`
      : `กรุณาวิเคราะห์ข้อความต่อไปนี้และให้ข้อมูลสรุปที่เป็นประโยชน์:\n\n${text}`;

    return this.generateResponse(prompt);
  }

  async chat(messages: Message[]): Promise<string> {
    const conversation = messages.map(msg =>
      `${msg.role === 'user' ? 'ผู้ใช้' : 'AI'}: ${msg.content}`
    ).join('\n\n');

    const prompt = `สนทนาต่อไปนี้:\n\n${conversation}\n\nAI: `;
    return this.generateResponse(prompt);
  }
}
