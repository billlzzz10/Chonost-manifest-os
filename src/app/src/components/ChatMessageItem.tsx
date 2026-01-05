// src/app/src/components/ChatMessageItem.tsx
import React from 'react';
import { Bot, User } from 'lucide-react';

// Replicating the ChatMessage interface from AIChat.tsx to define props
// In a real app, this might be moved to a shared types file.
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isError?: boolean;
}

interface ChatMessageItemProps {
  message: ChatMessage;
}

// Optimization: This component is wrapped in React.memo to prevent
// re-rendering if its props (the message object) have not changed.
// This is crucial in a chat application where new messages are added
// or the parent component's state changes (e.g., typing in the input),
// as it prevents the entire list of messages from re-rendering.
const ChatMessageItem: React.FC<ChatMessageItemProps> = React.memo(({ message }) => {
  return (
    <div
      className={`message ${message.role} ${message.isError ? 'error' : ''}`}
    >
      <div className="message-avatar">
        {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
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

export default ChatMessageItem;
