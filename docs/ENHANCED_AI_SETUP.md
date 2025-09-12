# 🚀 Chonost Enhanced AI Setup Guide

## Overview

Chonost now supports multiple AI providers with intelligent tier management, cost optimization, and local AI capabilities. This guide covers setup for all supported services.

## 🎯 Supported AI Services

### 1. **OpenAI** (Cloud)
- **Models**: GPT-3.5-Turbo, GPT-4
- **Best for**: Code generation, complex reasoning
- **Cost**: $0.0015/1K input, $0.002/1K output (GPT-3.5)

### 2. **Anthropic** (Cloud)
- **Models**: Claude-3-Haiku, Claude-3.5-Sonnet
- **Best for**: Creative writing, analysis
- **Cost**: $0.00025/1K input, $0.00125/1K output (Haiku)

### 3. **xAI** (Cloud)
- **Models**: Grok Beta
- **Best for**: Innovative responses, real-time info
- **Cost**: $0.005/1K input, $0.01/1K output

### 4. **OpenRouter** (Cloud)
- **Models**: WizardLM-2-8x22B, MythoMax-L2-13B
- **Best for**: Cost-effective alternatives
- **Cost**: $0.0005/1K input, $0.0005/1K output

### 5. **Ollama** (Local)
- **Models**: Llama2, CodeLlama, Mistral
- **Best for**: Privacy, offline usage
- **Cost**: Free (local hardware only)

## 🏷️ Tier System

### **Free Tier**
```json
{
  "maxTokens": 1000,
  "maxRequestsPerHour": 50,
  "allowedModels": [
    "gpt-3.5-turbo",
    "claude-3-haiku-20240307",
    "llama2:7b",
    "microsoft/wizardlm-2-8x22b"
  ]
}
```

### **Plus Tier**
```json
{
  "maxTokens": 10000,
  "maxRequestsPerHour": 500,
  "allowedModels": [
    "gpt-4",
    "claude-3-5-sonnet-20241022",
    "grok-beta",
    "meta-llama/llama-2-13b-chat",
    "codellama:7b",
    "mistral:7b"
  ]
}
```

## ⚙️ Setup Instructions

### Step 1: Environment Configuration

1. **Copy the .env template:**
```bash
cp .env.example .env
```

2. **Configure your API keys:**
```bash
# Edit .env file
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
XAI_API_KEY=your_xai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Set your tier
CHONOST_TIER=free  # or 'plus'
```

### Step 2: Service-Specific Setup

#### **OpenAI Setup**
1. Visit: https://platform.openai.com/api-keys
2. Create new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

#### **Anthropic Setup**
1. Visit: https://console.anthropic.com/
2. Generate API key
3. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

#### **xAI Setup**
1. Visit: https://platform.x.ai/
2. Generate API key
3. Add to `.env`: `XAI_API_KEY=xai-...`

#### **OpenRouter Setup**
1. Visit: https://openrouter.ai/
2. Create account and get API key
3. Add to `.env`: `OPENROUTER_API_KEY=sk-or-v1-...`

#### **Ollama Setup (Local AI)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama2:7b
ollama pull codellama:7b
ollama pull mistral:7b

# Start Ollama service
ollama serve

# Verify installation
curl http://localhost:11434/api/tags
```

### Step 3: Continue Configuration

The `.continue/config.yaml` is pre-configured with all models. The system will automatically:

- Use cost-optimized models by default
- Switch to local models when available
- Respect tier limitations
- Optimize for specific tasks

## 🎨 Dynamic Whiteboard Features

### "Everything is Text" Functionality

The Dynamic Whiteboard automatically handles large text content:

1. **Auto-conversion**: Text > 3000 characters → Automatic file creation
2. **Smart paste handling**: Large pasted content → File conversion
3. **AI suggestions**: Context-aware writing assistance
4. **Auto-save**: 30-second intervals
5. **File operations**: Import/export text files

### Usage:
```typescript
import DynamicWhiteboard from './components/DynamicWhiteboard';

// Basic usage
<DynamicWhiteboard
  content={initialText}
  onContentChange={(text) => console.log('Text changed:', text)}
/>
```

## 💰 Cost Optimization Features

### Automatic Model Selection
```typescript
// System automatically chooses best model for task
const optimizedModel = getOptimizedModel('coding'); // Returns CodeLlama for local, GPT-4 for Plus tier
```

### Cost Tracking
- Real-time usage monitoring
- Cost estimation before requests
- Budget alerts and limits
- Usage analytics dashboard

### Resource Management
```typescript
// Check tier limits
const canMakeRequest = checkTierLimits();

// Get usage statistics
const stats = aiService.getUsageStats();
console.log(`Cost: $${stats.totalCost}, Tokens: ${stats.tokensUsed}`);
```

## 🔄 AI Feedback Loop System

### Intelligent Model Switching
```typescript
// Automatic fallback system
if (primaryModelFails) {
  switchToBackupModel();
}

// Quality-based switching
if (responseQuality < threshold) {
  upgradeToBetterModel();
}
```

### Context Learning
- Remembers successful model-task combinations
- Learns user preferences
- Adapts to usage patterns
- Optimizes for speed vs. quality trade-offs

## 📊 Model Performance Matrix

| Task Type | Best Model | Fallback | Local Option |
|-----------|------------|----------|--------------|
| Code Generation | GPT-4 | Claude-3.5 | CodeLlama |
| Creative Writing | Claude-3.5 | GPT-4 | Llama2 |
| Data Analysis | Claude-3.5 | GPT-4 | - |
| Quick Tasks | GPT-3.5 | Claude-Haiku | Mistral |
| Cost-Effective | WizardLM | MythoMax | Llama2 |

## 🚀 Quick Start Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Start with Tauri (desktop)
npm run tauri:dev

# Test AI services
npm run test:ai

# Check Ollama status
curl http://localhost:11434/api/tags
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Model not allowed in tier"**
   - Check `CHONOST_TIER` in `.env`
   - Upgrade to Plus tier for premium models

2. **"API key not configured"**
   - Verify `.env` file exists
   - Check API key format and validity

3. **"Ollama service unavailable"**
   - Ensure Ollama is running: `ollama serve`
   - Check port 11434 availability

4. **"Tier limit exceeded"**
   - Wait for hourly reset
   - Upgrade to Plus tier for higher limits

### Performance Optimization:

```bash
# Enable caching
CACHE_ENABLED=true

# Set resource limits
MAX_CACHE_SIZE=500MB
MAX_TOKENS_FREE=1000
MAX_TOKENS_PLUS=10000
```

## 📈 Monitoring & Analytics

### Usage Dashboard
- Real-time cost tracking
- Model performance metrics
- Token usage statistics
- Error rate monitoring

### Optimization Tips
1. Use local models (Ollama) for privacy/cost
2. Enable caching for repeated requests
3. Monitor usage patterns for optimization
4. Set budget alerts for cost control

---

## 🎯 Next Steps

1. ✅ Configure API keys in `.env`
2. ✅ Set up Ollama for local AI
3. ✅ Test Dynamic Whiteboard features
4. ✅ Monitor usage and costs
5. 🔄 Optimize based on usage patterns

**Need help?** Check the [troubleshooting section](#troubleshooting) or create an issue in the repository.