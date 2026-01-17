// src/components/AIChat.tsx
// AI Chat Component for Craft IDE
// Provides chat interface with AI providers (Ollama, OpenRouter, etc.)

import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Settings, Loader2 } from "lucide-react";
import {
  getAIProviders,
  getAIModels,
  setProvider,
  chatWithAI,
  type Message as AIMessage,
} from "../../services/aiService";

interface ChatMessage extends AIMessage {
  id: string;
  timestamp: Date;
  isError?: boolean;
}

export default function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [providers, setProviders] = useState<string[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize with welcome message
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content:
          "Hello! I'm your AI assistant. I can help you with writing, coding, analysis, and more. What would you like to work on?",
        timestamp: new Date(),
      },
    ]);

    // Load available providers
    loadProviders();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadProviders = async () => {
    try {
      const availableProviders = await getAIProviders();
      setProviders(availableProviders);

      if (availableProviders.length > 0) {
        const defaultProvider = availableProviders[0];
        const defaultModel = "gpt-4o-mini";
        setSelectedProvider(defaultProvider);
        setSelectedModel(defaultModel);
        setProvider(defaultProvider, "", defaultModel);
      }
    } catch (error) {
      console.error("Failed to load AI providers:", error);
      // Optionally, set an error message in the chat
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentChatHistory = [...messages, userMessage].map(
      ({ role, content }) => ({ role, content })
    );

    setInput("");
    setIsLoading(true);

    try {
      const aiResponse = await chatWithAI(currentChatHistory);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: aiResponse,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("AI chat error:", error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleProviderChange = async (newProvider: string) => {
    setSelectedProvider(newProvider);
    try {
      const modelList = await getAIModels(newProvider);
      setModels(modelList);
      if (modelList.length > 0) {
        const newModel = modelList[0];
        setSelectedModel(newModel);
        setProvider(newProvider, "", newModel);
      } else {
        setSelectedModel("");
        setProvider(newProvider, "", "");
      }
    } catch (error) {
      console.error("Failed to load AI models:", error);
      setModels([]);
      setSelectedModel("");
    }
  };

  const handleModelChange = (newModel: string) => {
    setSelectedModel(newModel);
    setProvider(selectedProvider, "", newModel);
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "Chat cleared. How can I help you?",
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="ai-chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="header-left">
          <Bot size={20} />
          <span>AI Assistant</span>
        </div>
        <div className="header-right">
          <button
            className="icon-button"
            onClick={() => setShowSettings(!showSettings)}
            title="Settings"
          >
            <Settings size={16} />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="settings-panel">
          <div className="setting-group">
            <label>Provider:</label>
            <select
              value={selectedProvider}
              onChange={(e) => handleProviderChange(e.target.value)}
              title="Select AI Provider"
            >
              {providers.map((provider) => (
                <option key={provider} value={provider}>
                  {provider}
                </option>
              ))}
            </select>
          </div>
          <div className="setting-group">
            <label>Model:</label>
            <select
              value={selectedModel}
              onChange={(e) => handleModelChange(e.target.value)}
              title="Select AI Model"
              disabled={models.length === 0}
            >
              {models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
          <button className="clear-button" onClick={clearChat}>
            Clear Chat
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="messages-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.role} ${
              message.isError ? "error" : ""
            }`}
          >
            <div className="message-avatar">
              {message.role === "user" ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">
              <Bot size={16} />
            </div>
            <div className="message-content">
              <div className="message-text">
                <Loader2 size={16} className="animate-spin" />
                Thinking...
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Use /help for commands)"
          disabled={isLoading}
          rows={1}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="send-button"
          title="Send message"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
