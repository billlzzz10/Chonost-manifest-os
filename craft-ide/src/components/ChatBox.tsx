// src/components/ChatBox.tsx
import { useState, useEffect, useCallback, useMemo } from "react";
import { useStore } from "../state/store";
import { mockStreamChat } from "../lib/mockApi";
import { CraftFileManager } from "../lib/tauri";
import { LargeFileHandler } from "../lib/largeFileHandler";
import { Send, Paperclip, FileText, Trash2 } from "lucide-react";


// Constants for file handling
const MAX_FILE_SIZE_CHARS = LargeFileHandler.getThreshold();
const PREVIEW_CHARS = 500;
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  context?: {
    type: "editor" | "canvas" | "file";
    data: any;
  };
}

interface AttachedContext {
  id: string;
  type: "editor" | "canvas" | "file" | "selection";
  title: string;
  content: string;
  size: number;
}

export default function ChatBox() {
  const { content, mode } = useStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [attachedContexts, setAttachedContexts] = useState<AttachedContext[]>(
    []
  );
  const [autoAttachEditor, setAutoAttachEditor] = useState(true);

  // Auto-attach editor content when it changes (if enabled)
  useEffect(() => {
    if (autoAttachEditor && content.trim()) {
      const editorContext: AttachedContext = {
        id: "editor-content",
        type: "editor",
        title: "Current Editor Content",
        content: content,
        size: content.length,
      };

      setAttachedContexts((prev) => {
        const filtered = prev.filter((ctx) => ctx.id !== "editor-content");
        return [...filtered, editorContext];
      });
    }
  }, [content, autoAttachEditor]);

  const attachCurrentEditor = useCallback(() => {
    if (!content.trim()) {
      return;
    }

    const editorContext: AttachedContext = {
      id: "editor-content",
      type: "editor",
      title: "Current Editor Content",
      content: content,
      size: content.length,
    };

    setAttachedContexts((prev) => {
      const filtered = prev.filter((ctx) => ctx.id !== "editor-content");
      return [...filtered, editorContext];
    });
  }, [content]);

  const attachSelection = () => {
    // In a real implementation, this would get the selected text from Monaco Editor
    const selection = window.getSelection()?.toString() || "";
    if (!selection.trim()) {
      return;
    }

    const selectionContext: AttachedContext = {
      id: `selection-${Date.now()}`,
      type: "selection",
      title: "Selected Text",
      content: selection,
      size: selection.length,
    };

    setAttachedContexts((prev) => [...prev, selectionContext]);
  };

  const attachCanvasState = () => {
    if (mode !== "whiteboard") {
      return;
    }

    // In a real implementation, this would capture canvas state
    const canvasContext: AttachedContext = {
      id: "canvas-state",
      type: "canvas",
      title: "Current Canvas State",
      content: "Canvas state with drawings and notes", // Placeholder
      size: 100, // Placeholder
    };

    setAttachedContexts((prev) => {
      const filtered = prev.filter((ctx) => ctx.id !== "canvas-state");
      return [...filtered, canvasContext];
    });
  };

  const attachFile = async () => {
    try {
      // Use Tauri file dialog to select file
      const filePath = await CraftFileManager.openProject();
      if (!filePath) return;

      // Read file content (placeholder - would use actual Tauri API)
      const fileContent = `File content from ${filePath}`;

      // Check if file is too large
      if (fileContent.length > MAX_FILE_SIZE_CHARS) {
        // Use LargeFileHandler for large files
        const reference = await LargeFileHandler.handleLargePaste(fileContent);
        if (reference) {
          const fileName = filePath.split(/[/\\]/).pop() || "Unknown file";
          const fileContext: AttachedContext = {
            id: `file-${Date.now()}`,
            type: "file",
            title: `File: ${fileName} (Reference)`,
            content: `Large file saved as reference: ${reference.filePath}\n\nPreview:\n${reference.preview}`,
            size: reference.originalSize,
          };
          setAttachedContexts((prev) => [...prev, fileContext]);
        }
      } else {
        const fileName = filePath.split(/[/\\]/).pop() || "Unknown file";
        const fileContext: AttachedContext = {
          id: `file-${Date.now()}`,
          type: "file",
          title: `File: ${fileName}`,
          content: fileContent,
          size: fileContent.length,
        };
        setAttachedContexts((prev) => [...prev, fileContext]);
      }
    } catch (error) {
      console.error("Failed to attach file:", error);
    }
  };

  const removeContext = (contextId: string) => {
    setAttachedContexts((prev) => prev.filter((ctx) => ctx.id !== contextId));
  };

  const buildContextualPrompt = useCallback(
    (userInput: string): string => {
      if (attachedContexts.length === 0) {
        return userInput;
      }

      let contextualPrompt = `User Question: ${userInput}\n\n`;
      contextualPrompt += `Context Information:\n`;

      attachedContexts.forEach((ctx, index) => {
        contextualPrompt += `\n--- Context ${index + 1}: ${ctx.title} ---\n`;
        contextualPrompt += ctx.content;
        contextualPrompt += `\n--- End Context ${index + 1} ---\n`;
      });

      contextualPrompt += `\nPlease answer the user's question using the provided context information. If the context is relevant, reference it in your response.`;

      return contextualPrompt;
    },
    [attachedContexts]
  );

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input,
      timestamp: Date.now(),
      context:
        attachedContexts.length > 0
          ? {
              type: "editor", // Simplified for now
              data: attachedContexts,
            }
          : undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Build contextual prompt
    const contextualPrompt = buildContextualPrompt(input);

    // Add empty assistant message that will be filled by streaming
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: "",
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      await mockStreamChat(contextualPrompt, (chunk: string) => {
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.role === "assistant") {
            lastMessage.content += chunk;
          }
          return newMessages;
        });
      });
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage.role === "assistant") {
          lastMessage.content =
            "Sorry, I encountered an error while processing your request.";
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
      // Clear attached contexts after sending
      setAttachedContexts([]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} chars`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}K chars`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}M chars`;
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="row">
          <span style={{ fontSize: "12px", fontWeight: "bold" }}>
            AI Assistant
          </span>
          <label
            className="row"
            style={{ fontSize: "10px", cursor: "pointer" }}
          >
            <input
              type="checkbox"
              checked={autoAttachEditor}
              onChange={(e) => setAutoAttachEditor(e.target.checked)}
              style={{ marginRight: "4px" }}
            />
            Auto-attach editor
          </label>
        </div>
      </div>

      {/* Attached Contexts */}
      {attachedContexts.length > 0 && (
        <div className="attached-contexts">
          <div
            style={{
              fontSize: "10px",
              color: "var(--muted)",
              marginBottom: "4px",
            }}
          >
            Attached Context ({attachedContexts.length}):
          </div>
          {attachedContexts.map((ctx) => (
            <div key={ctx.id} className="attached-context-item">
              <div className="row">
                <FileText size={12} />
                <span style={{ fontSize: "10px", flex: 1 }}>{ctx.title}</span>
                <span style={{ fontSize: "9px", color: "var(--muted)" }}>
                  {formatFileSize(ctx.size)}
                </span>
                <button
                  className="btn-icon"
                  onClick={() => removeContext(ctx.id)}
                  title="Remove context"
                  style={{ padding: "2px" }}
                >
                  <Trash2 size={10} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 && (
          <div
            style={{
              color: "var(--muted)",
              fontSize: "12px",
              textAlign: "center",
              padding: "20px",
            }}
          >
            Ask me anything about your content...
            <br />
            <span style={{ fontSize: "10px" }}>
              I can see your editor content, canvas state, and attached files.
            </span>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className="chat-message">
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
        ))}
        {isLoading && (
          <div className="chat-message">
            <div
              style={{
                fontSize: "11px",
                color: "var(--muted)",
                marginBottom: "4px",
              }}
            >
              AI
            </div>
            <div style={{ color: "var(--muted)", fontSize: "12px" }}>
              Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="chat-input">
        <div className="chat-input-toolbar">
          <button
            className="btn-icon"
            onClick={attachCurrentEditor}
            title="Attach current editor content"
            disabled={!content.trim()}
          >
            <FileText size={14} />
          </button>
          <button
            className="btn-icon"
            onClick={attachSelection}
            title="Attach selected text"
          >
            <Paperclip size={14} />
          </button>
          <button
            className="btn-icon"
            onClick={attachCanvasState}
            title="Attach canvas state"
            disabled={mode !== "whiteboard"}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="9" cy="9" r="2" />
              <path d="M21 15l-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
            </svg>
          </button>
          <button className="btn-icon" onClick={attachFile} title="Attach file">
            <Paperclip size={14} />
          </button>
        </div>

        <div className="chat-input-main">
          <textarea
            className="input"
            placeholder="Ask about your content..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            rows={1}
            style={{
              resize: "none",
              minHeight: "32px",
              maxHeight: "100px",
            }}
          />
          <button
            className="btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            title="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
