// src/components/EditorWhiteboard.tsx
// TODO: Replace textarea with Monaco Editor for better code editing experience
// TODO: Add support for Mermaid diagram rendering in Reading View
// TODO: Implement more advanced canvas tools (shapes, text, arrows)
// TODO: Add file system integration via Tauri

import { useEffect, useRef, useState } from "react";
import { useStore } from "@/state/store";
import { mockHandleBigPaste, mockImportUrl } from "@/lib/mockApi";
import { analyzeText } from "@/lib/metrics";
import StickyNotes from "./StickyNotes";
import ReadingView from "./ReadingView";
import MonacoEditor from "./MonacoEditor";
import { Pen, Eraser, Ruler, Code, FileText } from "lucide-react";

export default function EditorWhiteboard() {
  const { mode, content, setContent, tool, penColor, setData } = useStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [editorMode, setEditorMode] = useState<"monaco" | "textarea">("monaco");

  // Auto-analyze content when it changes
  useEffect(() => {
    if (content) {
      const data = analyzeText(content);
      setData(data);
    }
  }, [content, setData]);

  // Handle paste events
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const text = e.clipboardData?.getData("text") || "";

      // Check if it's a URL
      if (text.match(/^https?:\/\//)) {
        e.preventDefault();
        mockImportUrl(text);
        return;
      }

      // Check if it's a big paste
      if (mockHandleBigPaste(text)) {
        e.preventDefault();
      }
    };

    document.addEventListener("paste", handlePaste);
    return () => document.removeEventListener("paste", handlePaste);
  }, []);

  // Canvas drawing logic
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || mode !== "whiteboard") return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
      ctx.fillStyle = "#0b1322";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    const startDrawing = (e: MouseEvent) => {
      if (tool === "pen" || tool === "erase") {
        setIsDrawing(true);
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        ctx.beginPath();
        ctx.moveTo(x, y);
      }
    };

    const draw = (e: MouseEvent) => {
      if (!isDrawing) return;

      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      if (tool === "pen") {
        ctx.globalCompositeOperation = "source-over";
        ctx.strokeStyle = penColor;
        ctx.lineWidth = 2;
      } else if (tool === "erase") {
        ctx.globalCompositeOperation = "destination-out";
        ctx.lineWidth = 10;
      }

      ctx.lineTo(x, y);
      ctx.stroke();
    };

    const stopDrawing = () => {
      setIsDrawing(false);
    };

    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
    canvas.addEventListener("mouseout", stopDrawing);

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      canvas.removeEventListener("mousedown", startDrawing);
      canvas.removeEventListener("mousemove", draw);
      canvas.removeEventListener("mouseup", stopDrawing);
      canvas.removeEventListener("mouseout", stopDrawing);
    };
  }, [mode, tool, penColor, isDrawing]);

  if (mode === "reading") {
    return <ReadingView content={content} />;
  }

  if (mode === "whiteboard") {
    return (
      <div className="editorWrap">
        <div className="toolbar">
          <button
            className={`btn ${tool === "pen" ? "active" : ""}`}
            onClick={() => useStore.getState().setTool("pen")}
          >
            <Pen size={16} />
          </button>
          <button
            className={`btn ${tool === "erase" ? "active" : ""}`}
            onClick={() => useStore.getState().setTool("erase")}
          >
            <Eraser size={16} />
          </button>
          <button
            className={`btn ${tool === "ruler" ? "active" : ""}`}
            onClick={() => useStore.getState().setTool("ruler")}
          >
            <Ruler size={16} />
          </button>
          <div
            style={{
              width: "1px",
              height: "20px",
              background: "var(--stroke)",
              margin: "0 8px",
            }}
          />
          <div
            style={{
              width: "24px",
              height: "24px",
              background: penColor,
              borderRadius: "50%",
              border: "2px solid rgba(255,255,255,0.3)",
            }}
          />
        </div>
        <div className="canvasWrap">
          <canvas
            ref={canvasRef}
            style={{
              width: "100%",
              height: "100%",
              cursor:
                tool === "pen"
                  ? "crosshair"
                  : tool === "erase"
                  ? "grab"
                  : "default",
            }}
          />
          <StickyNotes />
        </div>
      </div>
    );
  }

  // Editor mode
  return (
    <div className="editorWrap">
      <div className="toolbar">
        <span className="sectionTitle">Editor</span>
        <div className="row">
          <button
            className={`btn ${editorMode === "monaco" ? "active" : ""}`}
            onClick={() => setEditorMode("monaco")}
            title="Monaco Editor"
          >
            <Code size={16} />
          </button>
          <button
            className={`btn ${editorMode === "textarea" ? "active" : ""}`}
            onClick={() => setEditorMode("textarea")}
            title="Simple Editor"
          >
            <FileText size={16} />
          </button>
        </div>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: "12px", color: "var(--muted)" }}>
          {content.length} chars
        </span>
      </div>

      {editorMode === "monaco" ? (
        <MonacoEditor
          value={content}
          onChange={setContent}
          language="markdown"
          height="calc(100% - 40px)"
        />
      ) : (
        <textarea
          className="textarea"
          style={{
            flex: 1,
            resize: "none",
            fontFamily:
              'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
            fontSize: "14px",
            lineHeight: "1.6",
          }}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Start writing your ideas here..."
        />
      )}
    </div>
  );
}
