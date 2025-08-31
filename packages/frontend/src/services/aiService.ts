import { knowledgeService } from './knowledgeService';

export interface AIMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    searchResults?: any[];
    suggestions?: string[];
    confidence?: number;
  };
}

export interface AIResponse {
  message: string;
  suggestions?: string[];
  searchResults?: any[];
  confidence: number;
}

class AIService {
  private baseUrl = 'http://localhost:8000/api';

  async sendMessage(message: string): Promise<AIResponse> {
    try {
      // First, search for relevant knowledge
      const searchResults = await knowledgeService.searchKnowledge(message, 3);
      
      // For now, simulate AI response with search results
      // In the future, this would connect to LiteLLM or other AI service
      const response = await this.generateAIResponse(message, searchResults);
      
      return response;
    } catch (error) {
      console.error('Error sending message to AI:', error);
      return {
        message: "I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later.",
        confidence: 0.5
      };
    }
  }

  private async generateAIResponse(userMessage: string, searchResults: any[]): Promise<AIResponse> {
    // Simulate AI processing time
    await new Promise(resolve => setTimeout(resolve, 1000));

    const suggestions = [
      "Can you tell me more about the Trinity Layout?",
      "How does the RAG system work?",
      "What are the main features of Chonost?",
      "How can I improve my writing?"
    ];

    let response = "";
    let confidence = 0.8;

    if (searchResults.length > 0) {
      const topResult = searchResults[0];
      response = `Based on the available information, I found some relevant content about "${topResult.title}". ${topResult.content.substring(0, 200)}...\n\nWould you like me to search for more specific information?`;
      confidence = topResult.score || 0.8;
    } else {
      response = `I understand you're asking about "${userMessage}". While I don't have specific information about that in my knowledge base, I can help you with general writing questions or search for related topics. What would you like to know more about?`;
      confidence = 0.6;
    }

    return {
      message: response,
      suggestions: suggestions.slice(0, 2),
      searchResults: searchResults.slice(0, 2),
      confidence
    };
  }

  async getQuickActions(): Promise<string[]> {
    return [
      "help me improve this text",
      "generate some creative ideas",
      "analyze the character development",
      "suggest plot improvements",
      "explain the Trinity Layout",
      "how does RAG work?",
      "what are the main features?",
      "help with writing structure"
    ];
  }

  async getAISuggestions(context: string): Promise<string[]> {
    try {
      // Search for relevant content based on context
      const searchResults = await knowledgeService.searchKnowledge(context, 2);
      
      const suggestions = [
        "Consider adding more descriptive details",
        "This section could benefit from dialogue",
        "Try varying your sentence structure",
        "Add sensory details to make it more vivid"
      ];

      if (searchResults.length > 0) {
        suggestions.unshift(`Based on "${searchResults[0].title}", you might want to explore this topic further`);
      }

      return suggestions.slice(0, 3);
    } catch (error) {
      console.error('Error getting AI suggestions:', error);
      return [
        "Consider adding more descriptive details",
        "This section could benefit from dialogue",
        "Try varying your sentence structure"
      ];
    }
  }
}

export const aiService = new AIService();
