import React, { useState, useEffect } from 'react';
import { aiService, AIMessage } from '../../services/aiService';

interface AssistantPanelProps {
  // Add props here
}

export const AssistantPanel: React.FC<AssistantPanelProps> = () => {
  const [messages, setMessages] = useState<AIMessage[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your AI assistant. How can I help you with your creative work today?',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [quickActions, setQuickActions] = useState<string[]>([]);

  // Load quick actions on component mount
  useEffect(() => {
    loadQuickActions();
  }, []);

  const loadQuickActions = async () => {
    try {
      const actions = await aiService.getQuickActions();
      setQuickActions(actions);
    } catch (error) {
      console.error('Error loading quick actions:', error);
      setQuickActions([
        "help me improve this text",
        "generate some creative ideas",
        "analyze the character development",
        "suggest plot improvements"
      ]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: AIMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsTyping(true);

    try {
      // Get AI response
      const aiResponse = await aiService.sendMessage(currentInput);
      
      const assistantMessage: AIMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: aiResponse.message,
        timestamp: new Date(),
        metadata: {
          searchResults: aiResponse.searchResults,
          suggestions: aiResponse.suggestions,
          confidence: aiResponse.confidence
        }
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMessage: AIMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: "I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (action: string) => {
    setInputValue(action);
  };

  return (
    <div className="assistant-panel-container w-96 bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="assistant-header bg-blue-50 border-b border-gray-200 px-4 py-3">
        <div className="flex items-center space-x-2">
          <div className="ai-avatar w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
            AI
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
            <p className="text-sm text-gray-600">Your creative writing partner</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions bg-gray-50 border-b border-gray-200 px-4 py-2">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Quick Actions</h3>
        <div className="grid grid-cols-2 gap-2">
          {quickActions.slice(0, 4).map((action, index) => (
            <button
              key={index}
              onClick={() => handleQuickAction(action)}
              className="quick-action-btn px-3 py-2 bg-white border border-gray-200 rounded-md text-xs text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-colors"
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.type === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div
              className={`message-bubble max-w-xs px-3 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white ml-auto'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="assistant-message">
            <div className="message-bubble bg-gray-100 text-gray-900 max-w-xs px-3 py-2 rounded-lg">
              <div className="flex items-center space-x-1">
                <div className="typing-indicator">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
                <span className="text-sm">AI is typing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="input-container border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your writing..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={2}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="send-btn px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </div>

      {/* Styles for typing indicator */}
      <style jsx>{`
        .typing-indicator {
          display: flex;
          align-items: center;
          gap: 2px;
        }
        
        .dot {
          width: 4px;
          height: 4px;
          background-color: #6b7280;
          border-radius: 50%;
          animation: typing 1.4s infinite ease-in-out;
        }
        
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
          0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
          }
          40% {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default AssistantPanel;
