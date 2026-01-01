// src/app/src/components/ChatMessage.tsx
import React from 'react';
import { Bot, User } from 'lucide-react';

// The AIMessage interface is defined in AIChat.tsx, but since we're creating a new file,
// we'll need to either export it from there and import it here, or redefine it.
// For now, we'll define a similar structure for clarity.
interface ChatMessageProps {
  message: {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    isError?: boolean;
  };
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
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
};

// ⚡ Bolt: Memoize the component to prevent unnecessary re-renders.
// In a chat application, the list of messages grows over time. When a new
// message is added, the parent component (AIChat) re-renders, which would
// cause all `ChatMessage` components in the list to re-render as well.
// `React.memo` performs a shallow comparison of props and prevents the
// component from re-rendering if its props haven't changed, significantly
// improving performance for long conversations.
export default React.memo(ChatMessage);
