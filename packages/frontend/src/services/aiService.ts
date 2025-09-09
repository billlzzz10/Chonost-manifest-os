// Chonost AI Service Manager
import { getCurrentTier, isModelAllowed, calculateCost, getOptimizedModel, MODEL_COSTS } from '../config/tiers';

export interface AIRequest {
  model: string;
  messages: Array<{ role: string; content: string }>;
  temperature?: number;
  maxTokens?: number;
}

export interface AIResponse {
  content: string;
  usage: {
    inputTokens: number;
    outputTokens: number;
    cost: number;
  };
  model: string;
}

class AIService {
  private usageStats = {
    totalRequests: 0,
    totalCost: 0,
    tokensUsed: 0,
    lastReset: Date.now()
  };

  // Check if request is within tier limits
  private checkTierLimits(): boolean {
    const tier = getCurrentTier();
    return this.usageStats.totalRequests < tier.maxRequestsPerHour;
  }

  // Get the best available model for the task
  getOptimizedModel(task: string): string {
    return getOptimizedModel(task);
  }

  // Make AI request with cost optimization
  async makeRequest(request: AIRequest): Promise<AIResponse> {
    // Check tier limits
    if (!this.checkTierLimits()) {
      throw new Error('Tier limit exceeded. Please upgrade to Plus tier for higher limits.');
    }

    // Check if model is allowed
    if (!isModelAllowed(request.model)) {
      throw new Error(`Model ${request.model} is not available in your current tier.`);
    }

    // Optimize model if needed
    const optimizedModel = this.getOptimizedModel('general');
    const finalModel = request.model === 'auto' ? optimizedModel : request.model;

    try {
      const response = await this.callAIProvider(finalModel, request);

      // Update usage stats
      this.usageStats.totalRequests++;
      this.usageStats.tokensUsed += response.usage.inputTokens + response.usage.outputTokens;
      this.usageStats.totalCost += response.usage.cost;

      return response;
    } catch (error) {
      console.error('AI request failed:', error);
      throw error;
    }
  }

  // Model registry for robust detection
  private static MODEL_REGISTRY: Record<string, { provider: string }> = {
    // Local models
    'llama': { provider: 'ollama' },
    'codellama': { provider: 'ollama' },
    'mistral': { provider: 'ollama' },
    // OpenAI models
    'gpt-3.5-turbo': { provider: 'openai' },
    'gpt-4': { provider: 'openai' },
    // Anthropic models
    'claude-2': { provider: 'anthropic' },
    'claude-3': { provider: 'anthropic' },
    // xAI models
    'grok-1': { provider: 'xai' },
    // OpenRouter models
    'microsoft-phi': { provider: 'openrouter' },
    'meta-llama-3': { provider: 'openrouter' }
  };

  // Call the appropriate AI provider using registry
  private async callAIProvider(model: string, request: AIRequest): Promise<AIResponse> {
    const tier = getCurrentTier();

    // Find provider by exact match or prefix
    const modelKey = Object.keys(AIService.MODEL_REGISTRY).find(key =>
      model === key || model.startsWith(key)
    );
    const registryEntry = modelKey ? AIService.MODEL_REGISTRY[modelKey] : null;

    if (!registryEntry) {
      throw new Error(`Unsupported model: ${model}`);
    }

    // Tier check for GPT-4
    if (tier.name === 'Free' && modelKey === 'gpt-4') {
      throw new Error('GPT-4 requires Plus tier. Using GPT-3.5 instead.');
    }

    switch (registryEntry.provider) {
      case 'ollama':
        return this.callOllama(model, request);
      case 'openai':
        return this.callOpenAI(model, request);
      case 'anthropic':
        return this.callAnthropic(model, request);
      case 'xai':
        return this.callXAI(model, request);
      case 'openrouter':
        return this.callOpenRouter(model, request);
      default:
        throw new Error(`Unsupported provider for model: ${model}`);
    }
  }

  // Ollama local AI
  private async callOllama(model: string, request: AIRequest): Promise<AIResponse> {
    const ollamaUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';

    try {
      const response = await fetch(`${ollamaUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: model.replace('ollama/', ''),
          prompt: request.messages.map(m => m.content).join('\n'),
          stream: false
        })
      });

      if (!response.ok) {
        throw new Error('Ollama service unavailable');
      }

      const data = await response.json();

      return {
        content: data.response,
        usage: {
          inputTokens: Math.ceil(request.messages.reduce((sum, m) => sum + m.content.length, 0) / 4),
          outputTokens: Math.ceil(data.response.length / 4),
          cost: 0 // Local models are free
        },
        model: model
      };
    } catch (error) {
      console.error('Ollama call failed:', error);
      throw new Error('Local AI service unavailable. Please ensure Ollama is running.');
    }
  }

  // OpenAI API
  private async callOpenAI(model: string, request: AIRequest): Promise<AIResponse> {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error('OpenAI API key not configured');

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: model,
        messages: request.messages,
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 1000
      })
    });

    if (!response.ok) {
      throw new Error('OpenAI API request failed');
    }

    const data = await response.json();
    const usage = data.usage;

    return {
      content: data.choices[0].message.content,
      usage: {
        inputTokens: usage.prompt_tokens,
        outputTokens: usage.completion_tokens,
        cost: calculateCost(model, usage.prompt_tokens, usage.completion_tokens)
      },
      model: model
    };
  }

  // Anthropic API
  private async callAnthropic(model: string, request: AIRequest): Promise<AIResponse> {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error('Anthropic API key not configured');

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: model,
        messages: request.messages,
        max_tokens: request.maxTokens || 1000
      })
    });

    if (!response.ok) {
      throw new Error('Anthropic API request failed');
    }

    const data = await response.json();

    return {
      content: data.content[0].text,
      usage: {
        inputTokens: Math.ceil(request.messages.reduce((sum, m) => sum + m.content.length, 0) / 4),
        outputTokens: Math.ceil(data.content[0].text.length / 4),
        cost: calculateCost(model, data.usage.input_tokens, data.usage.output_tokens)
      },
      model: model
    };
  }

  // xAI API
  private async callXAI(model: string, request: AIRequest): Promise<AIResponse> {
    const apiKey = process.env.XAI_API_KEY;
    if (!apiKey) throw new Error('xAI API key not configured');

    const response = await fetch('https://api.x.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: model,
        messages: request.messages,
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 1000
      })
    });

    if (!response.ok) {
      throw new Error('xAI API request failed');
    }

    const data = await response.json();

    return {
      content: data.choices[0].message.content,
      usage: {
        inputTokens: data.usage?.prompt_tokens || 0,
        outputTokens: data.usage?.completion_tokens || 0,
        cost: calculateCost(model, data.usage?.prompt_tokens || 0, data.usage?.completion_tokens || 0)
      },
      model: model
    };
  }

  // OpenRouter API
  private async callOpenRouter(model: string, request: AIRequest): Promise<AIResponse> {
    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) throw new Error('OpenRouter API key not configured');

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: model,
        messages: request.messages,
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 1000
      })
    });

    if (!response.ok) {
      throw new Error('OpenRouter API request failed');
    }

    const data = await response.json();

    return {
      content: data.choices[0].message.content,
      usage: {
        inputTokens: data.usage?.prompt_tokens || 0,
        outputTokens: data.usage?.completion_tokens || 0,
        cost: calculateCost(model, data.usage?.prompt_tokens || 0, data.usage?.completion_tokens || 0)
      },
      model: model
    };
  }

  // Get usage statistics
  getUsageStats() {
    return { ...this.usageStats };
  }

  // Reset usage statistics
  resetUsageStats() {
    this.usageStats = {
      totalRequests: 0,
      totalCost: 0,
      tokensUsed: 0,
      lastReset: Date.now()
    };
  }
}

export const aiService = new AIService();