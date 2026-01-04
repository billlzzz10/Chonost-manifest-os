// src/app/src/components/ChatMessage.tsx
import React from "react";

// This interface is duplicated from ChatBox.tsx.
// In a real-world scenario, this would be moved to a shared types file.
interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  context?: {
    type: "editor" | "canvas" | "file";
    data: any;
  };
}

const ChatMessageComponent: React.FC<{ msg: ChatMessageProps }> = ({ msg }) => {
  return (
    <div className="chat-message">
      <div className="row" style={{ marginBottom: "4px" }}>
        <div style={{ fontSize: "11px", color: "var(--muted)" }}>
          {msg.role === "user" ? "You" : "AI"}
        </div>
        {msg.context && (
          <div style={{ fontSize: "9px", color: "var(--brand)" }}>
            with context
          </div>
        )}
      </div>
      <div style={{ whiteSpace: "pre-wrap", fontSize: "12px" }}>
        {msg.content}
      </div>
    </div>
  );
};

// ⚡ Bolt: Memoizing the ChatMessageComponent to prevent unnecessary re-renders.
// Each message in the chat list is now wrapped in React.memo,
// ensuring it only re-renders if its own props (content, role, etc.) change.
// This significantly improves performance when new messages are added or when
// the parent component's state (like the input field) updates.
export const ChatMessage = React.memo(ChatMessageComponent);
