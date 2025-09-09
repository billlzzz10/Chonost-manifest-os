require('dotenv').config();

module.exports = {
  // Commit Message Generation
  commit: {
    apiKey: process.env.OPENROUTER_API_KEY,
    model: 'google/gemini-2.5-flash-free',
    baseUrl: 'https://openrouter.ai/api/v1',
    fallbackModels: [
      'meta-llama/llama-3.1-8b-instruct',
      'mistralai/mistral-7b-instruct',
      'deepseek/deepseek-chat'
    ]
  },
  // Version Management
  version: {
    apiKey: process.env.OPENROUTER_API_KEY,
    model: 'google/gemini-2.5-flash-free',
    baseUrl: 'https://openrouter.ai/api/v1',
    fallbackModels: [
      'groq/llama-3.1-70b-versatile',
      'meta-llama/llama-3.1-8b-instruct',
      'mistralai/mistral-7b-instruct'
    ]
  }
};