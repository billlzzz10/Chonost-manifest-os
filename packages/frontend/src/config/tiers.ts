// Chonost Tier Configuration
export interface TierConfig {
  name: string;
  maxTokens: number;
  maxRequestsPerHour: number;
  allowedModels: string[];
  features: string[];
  costMultiplier: number;
}

export const TIERS: Record<string, TierConfig> = {
  free: {
    name: 'Free',
    maxTokens: 1000,
    maxRequestsPerHour: 50,
    allowedModels: [
      'gpt-3.5-turbo',
      'claude-3-haiku-20240307',
      'llama2:7b',
      'microsoft/wizardlm-2-8x22b'
    ],
    features: [
      'Basic text editing',
      'Local AI models',
      'Basic file operations',
      'Community support'
    ],
    costMultiplier: 0
  },
  plus: {
    name: 'Plus',
    maxTokens: 10000,
    maxRequestsPerHour: 500,
    allowedModels: [
      'gpt-4',
      'claude-3-5-sonnet-20241022',
      'grok-beta',
      'meta-llama/llama-2-13b-chat',
      'codellama:7b',
      'mistral:7b'
    ],
    features: [
      'Advanced AI models',
      'Unlimited text editing',
      'Cloud AI integration',
      'Priority support',
      'Advanced file operations',
      'Export capabilities'
    ],
    costMultiplier: 1
  }
};

export const MODEL_COSTS = {
  // OpenAI Models
  'gpt-3.5-turbo': { input: 0.0015, output: 0.002 },
  'gpt-4': { input: 0.03, output: 0.06 },

  // Anthropic Models
  'claude-3-haiku-20240307': { input: 0.00025, output: 0.00125 },
  'claude-3-5-sonnet-20241022': { input: 0.003, output: 0.015 },

  // xAI Models
  'grok-beta': { input: 0.005, output: 0.01 },

  // OpenRouter Models
  'microsoft/wizardlm-2-8x22b': { input: 0.0005, output: 0.0005 },
  'meta-llama/llama-2-13b-chat': { input: 0.0008, output: 0.0008 },

  // Local Models (Ollama)
  'llama2:7b': { input: 0, output: 0 },
  'codellama:7b': { input: 0, output: 0 },
  'mistral:7b': { input: 0, output: 0 }
};

export const getCurrentTier = (): TierConfig => {
  const tier = process.env.CHONOST_TIER || 'free';
  return TIERS[tier] || TIERS.free;
};

export const isModelAllowed = (model: string): boolean => {
  const tier = getCurrentTier();
  return tier.allowedModels.includes(model);
};

export const calculateCost = (model: string, inputTokens: number, outputTokens: number): number => {
  const costs = MODEL_COSTS[model as keyof typeof MODEL_COSTS];
  if (!costs) return 0;

  const inputCost = (inputTokens / 1000) * costs.input;
  const outputCost = (outputTokens / 1000) * costs.output;

  return inputCost + outputCost;
};

export const getOptimizedModel = (task: string): string => {
  const tier = getCurrentTier();

  // Cost optimization logic
  switch (task.toLowerCase()) {
    case 'coding':
    case 'programming':
      return tier.allowedModels.includes('codellama:7b') ? 'codellama:7b' :
             tier.allowedModels.includes('gpt-4') ? 'gpt-4' : 'gpt-3.5-turbo';

    case 'writing':
    case 'creative':
      return tier.allowedModels.includes('claude-3-5-sonnet-20241022') ?
             'claude-3-5-sonnet-20241022' : 'claude-3-haiku-20240307';

    case 'analysis':
    case 'research':
      return tier.allowedModels.includes('gpt-4') ? 'gpt-4' :
             tier.allowedModels.includes('microsoft/wizardlm-2-8x22b') ?
             'microsoft/wizardlm-2-8x22b' : 'gpt-3.5-turbo';

    default:
      // Default to most cost-effective model
      return tier.allowedModels[0] || 'gpt-3.5-turbo';
  }
};