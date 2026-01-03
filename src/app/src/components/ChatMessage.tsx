// src/app/src/components/ChatMessage.tsx
// Memoized Chat Message Component for Craft IDE
// Prevents re-rendering of individual messages unless their props change.

import React from "react";
import { Bot, User } from "lucide-react";
import { type AIMessage } from "../lib/aiProviders";

// The interface is extended to include props that were previously defined in AIChat.tsx
interface ChatMessageProps extends AIMessage {
  id: string;
  timestamp: Date;
  isError?: boolean;
}

/**
 * ⚡ Bolt: This component is wrapped in React.memo to prevent unnecessary re-renders.
 * When the parent component's state changes (e.g., typing in the input), this
 * component will only re-render if its own props have changed. This is crucial
 * for performance in a chat application where the list of messages can grow long.
 */
const ChatMessage: React.FC<ChatMessageProps> = React.memo((message) => {
  return (
    <div
      className={`message ${message.role} ${message.isError ? "error" : ""}`}
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
  );
});

ChatMessage.displayName = "ChatMessage";

export default ChatMessage;
