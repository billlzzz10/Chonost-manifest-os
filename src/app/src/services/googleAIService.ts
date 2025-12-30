import { GoogleGenerativeAI } from '@google/generative-ai';

export interface GoogleAIServiceConfig {
  apiKey: string;
  model?: string;
}

export class GoogleAIService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(config: GoogleAIServiceConfig) {
    this.genAI = new GoogleGenerativeAI(config.apiKey);
    this.model = this.genAI.getGenerativeModel({
      model: config.model || 'gemini-1.5-flash'
    });
  }

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

  async analyzeText(text: string, instruction?: string): Promise<string> {
    const prompt = instruction
      ? `${instruction}\n\nข้อความที่ต้องการวิเคราะห์:\n${text}`
      : `กรุณาวิเคราะห์ข้อความต่อไปนี้และให้ข้อมูลสรุปที่เป็นประโยชน์:\n\n${text}`;

    return this.generateResponse(prompt);
  }

  async chat(messages: Array<{role: string, content: string}>): Promise<string> {
    const conversation = messages.map(msg =>
      `${msg.role === 'user' ? 'ผู้ใช้' : 'AI'}: ${msg.content}`
    ).join('\n\n');

    const prompt = `สนทนาต่อไปนี้:\n\n${conversation}\n\nAI: `;
    return this.generateResponse(prompt);
  }
}

let googleAIService: GoogleAIService | null = null;

export const initializeGoogleAI = (apiKey: string): GoogleAIService => {
  googleAIService = new GoogleAIService({ apiKey });
  return googleAIService;
};

export const getGoogleAIService = (): GoogleAIService | null => {
  return googleAIService;
};

export const analyzeWithGoogleAI = async (text: string): Promise<string> => {
  if (!googleAIService) {
    throw new Error('Google AI service not initialized. Please set GOOGLE_AI_API_KEY');
  }
  return googleAIService.analyzeText(text);
};

export const chatWithGoogleAI = async (messages: Array<{role: string, content: string}>): Promise<string> => {
  if (!googleAIService) {
    throw new Error('Google AI service not initialized. Please set GOOGLE_AI_API_KEY');
  }
  return googleAIService.chat(messages);
};