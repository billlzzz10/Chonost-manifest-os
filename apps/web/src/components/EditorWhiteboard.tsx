// src/components/EditorWhiteboard.tsx
// TODO: Replace textarea with Monaco Editor for better code editing experience
// TODO: Add support for Mermaid diagram rendering in Reading View
// TODO: Implement more advanced canvas tools (shapes, text, arrows)
// TODO: Add file system integration via Tauri

import { useEffect, useRef, useState } from "react";
import { useAppStore } from "@/state/store";
import { mockHandleBigPaste, mockImportUrl } from "@/lib/mockApi";
import { analyzeText } from "@/lib/metrics";
import StickyNotes from "./StickyNotes";
import ReadingView from "./ReadingView";
import LazyMonacoEditor from "./LazyMonacoEditor";
import { Pen, Eraser, Ruler, Code, FileText, MousePointer, Square, Circle, Minus, ArrowRight, Type, Layers, Settings } from "lucide-react";

export default function EditorWhiteboard() {
  const {
    mode,
    content,
    setContent,
    tool,
    penColor,
    setData,
    canvasObjects,
    layers,
    selectedObjectId,
    currentLayerId,
    addCanvasObject,
    updateCanvasObject,
    removeCanvasObject,
    setSelectedObjectId,
    setCurrentLayerId,
    updateLayer,
    setTool
  } = useAppStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [editorMode, setEditorMode] = useState<"monaco" | "textarea">("monaco");
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);
  const [currentPoint, setCurrentPoint] = useState<{ x: number; y: number } | null>(null);
  const [editingText, setEditingText] = useState<string>("");
  const [showLayersPanel, setShowLayersPanel] = useState(false);
  const [showPropertiesPanel, setShowPropertiesPanel] = useState(false);

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

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (mode !== "whiteboard") return;

      if (e.key === "Delete" && selectedObjectId) {
        removeCanvasObject(selectedObjectId);
        setSelectedObjectId(null);
      } else if (e.key === "Escape") {
        setSelectedObjectId(null);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [mode, selectedObjectId, removeCanvasObject, setSelectedObjectId]);

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

    const getMousePos = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    };

    const startDrawing = (e: MouseEvent) => {
      const pos = getMousePos(e);

      if (tool === "pen" || tool === "erase") {
        setIsDrawing(true);
        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);
      } else if (["rectangle", "circle", "line", "arrow", "text"].includes(tool)) {
        setStartPoint(pos);
        setIsDrawing(true);
      } else if (tool === "select") {
        // Handle selection logic
        const clickedObject = canvasObjects.find(obj => {
          if (obj.type === "rectangle") {
            return pos.x >= obj.x && pos.x <= obj.x + (obj.width || 0) &&
                   pos.y >= obj.y && pos.y <= obj.y + (obj.height || 0);
          }
          return false;
        });

        if (clickedObject) {
          setSelectedObjectId(clickedObject.id);
        } else {
          setSelectedObjectId(null);
        }
      }
    };

    const draw = (e: MouseEvent) => {
      if (!isDrawing) return;

      const pos = getMousePos(e);
      setCurrentPoint(pos);

      if (tool === "pen") {
        ctx.globalCompositeOperation = "source-over";
        ctx.strokeStyle = penColor;
        ctx.lineWidth = 2;
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
      } else if (tool === "erase") {
        ctx.globalCompositeOperation = "destination-out";
        ctx.lineWidth = 10;
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
      }
    };

    const stopDrawing = () => {
      if (!isDrawing) return;

      if (startPoint && currentPoint && ["rectangle", "circle", "line", "arrow", "text"].includes(tool)) {
        const width = Math.abs(currentPoint.x - startPoint.x);
        const height = Math.abs(currentPoint.y - startPoint.y);
        const x = Math.min(startPoint.x, currentPoint.x);
        const y = Math.min(startPoint.y, currentPoint.y);

        addCanvasObject({
          type: tool as any,
          x,
          y,
          width: tool === "line" || tool === "arrow" ? undefined : width,
          height: tool === "line" || tool === "arrow" ? undefined : height,
          startX: tool === "line" || tool === "arrow" ? startPoint.x : undefined,
          startY: tool === "line" || tool === "arrow" ? startPoint.y : undefined,
          endX: tool === "line" || tool === "arrow" ? currentPoint.x : undefined,
          endY: tool === "line" || tool === "arrow" ? currentPoint.y : undefined,
          text: tool === "text" ? "Double-click to edit" : undefined,
          color: penColor,
          strokeWidth: 2,
          layerId: currentLayerId,
          zIndex: layers.find(l => l.id === currentLayerId)?.zIndex || 0
        });
      }

      setIsDrawing(false);
      setStartPoint(null);
      setCurrentPoint(null);
    };

    const handleDoubleClick = (e: MouseEvent) => {
      const pos = getMousePos(e);
      const clickedObject = canvasObjects.find(obj => {
        if (obj.type === "text") {
          return pos.x >= obj.x && pos.x <= obj.x + 200 &&
                 pos.y >= obj.y && pos.y <= obj.y + 20;
        }
        return false;
      });

      if (clickedObject && clickedObject.type === "text") {
        setSelectedObjectId(clickedObject.id);
        setEditingText(clickedObject.text || "");
        // Focus on text input (will be added to UI)
      }
    };

    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
    canvas.addEventListener("mouseout", stopDrawing);
    canvas.addEventListener("dblclick", handleDoubleClick);

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      canvas.removeEventListener("mousedown", startDrawing);
      canvas.removeEventListener("mousemove", draw);
      canvas.removeEventListener("mouseup", stopDrawing);
      canvas.removeEventListener("mouseout", stopDrawing);
      canvas.removeEventListener("dblclick", handleDoubleClick);
    };
  }, [mode, tool, penColor, isDrawing, startPoint, currentPoint, canvasObjects, layers, currentLayerId, addCanvasObject, setSelectedObjectId]);

  // Render canvas objects
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || mode !== "whiteboard") return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear canvas
    ctx.fillStyle = "#0b1322";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Render objects sorted by z-index
    const visibleLayers = layers.filter(l => l.visible);
    const visibleObjects = canvasObjects
      .filter(obj => visibleLayers.some(l => l.id === obj.layerId))
      .sort((a, b) => a.zIndex - b.zIndex);

    visibleObjects.forEach(obj => {
      ctx.strokeStyle = obj.color;
      ctx.lineWidth = obj.strokeWidth;
      ctx.fillStyle = obj.color;

      switch (obj.type) {
        case "rectangle":
          if (obj.width && obj.height) {
            ctx.strokeRect(obj.x, obj.y, obj.width, obj.height);
          }
          break;
        case "circle":
          if (obj.width && obj.height) {
            const radius = Math.min(obj.width, obj.height) / 2;
            const centerX = obj.x + obj.width / 2;
            const centerY = obj.y + obj.height / 2;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.stroke();
          }
          break;
        case "line":
          if (obj.startX !== undefined && obj.startY !== undefined && obj.endX !== undefined && obj.endY !== undefined) {
            ctx.beginPath();
            ctx.moveTo(obj.startX, obj.startY);
            ctx.lineTo(obj.endX, obj.endY);
            ctx.stroke();
          }
          break;
        case "arrow":
          if (obj.startX !== undefined && obj.startY !== undefined && obj.endX !== undefined && obj.endY !== undefined) {
            // Draw line
            ctx.beginPath();
            ctx.moveTo(obj.startX, obj.startY);
            ctx.lineTo(obj.endX, obj.endY);
            ctx.stroke();

            // Draw arrowhead
            const angle = Math.atan2(obj.endY - obj.startY, obj.endX - obj.startX);
            const arrowLength = 10;
            ctx.beginPath();
            ctx.moveTo(obj.endX, obj.endY);
            ctx.lineTo(
              obj.endX - arrowLength * Math.cos(angle - Math.PI / 6),
              obj.endY - arrowLength * Math.sin(angle - Math.PI / 6)
            );
            ctx.moveTo(obj.endX, obj.endY);
            ctx.lineTo(
              obj.endX - arrowLength * Math.cos(angle + Math.PI / 6),
              obj.endY - arrowLength * Math.sin(angle + Math.PI / 6)
            );
            ctx.stroke();
          }
          break;
        case "text":
          if (obj.text) {
            ctx.font = "16px Arial";
            ctx.fillStyle = obj.color;
            ctx.fillText(obj.text, obj.x, obj.y + 16);
          }
          break;
      }

      // Draw selection highlight
      if (obj.id === selectedObjectId) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        if (obj.type === "rectangle" && obj.width && obj.height) {
          ctx.strokeRect(obj.x - 2, obj.y - 2, obj.width + 4, obj.height + 4);
        } else if (obj.type === "circle" && obj.width && obj.height) {
          const radius = Math.min(obj.width, obj.height) / 2;
          const centerX = obj.x + obj.width / 2;
          const centerY = obj.y + obj.height / 2;
          ctx.beginPath();
          ctx.arc(centerX, centerY, radius + 2, 0, 2 * Math.PI);
          ctx.stroke();
        }
        ctx.setLineDash([]);
      }
    });

    // Draw current shape preview while drawing
    if (isDrawing && startPoint && currentPoint && ["rectangle", "circle", "line", "arrow"].includes(tool)) {
      ctx.strokeStyle = penColor;
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);

      if (tool === "rectangle") {
        const width = Math.abs(currentPoint.x - startPoint.x);
        const height = Math.abs(currentPoint.y - startPoint.y);
        const x = Math.min(startPoint.x, currentPoint.x);
        const y = Math.min(startPoint.y, currentPoint.y);
        ctx.strokeRect(x, y, width, height);
      } else if (tool === "circle") {
        const width = Math.abs(currentPoint.x - startPoint.x);
        const height = Math.abs(currentPoint.y - startPoint.y);
        const radius = Math.min(width, height) / 2;
        const centerX = (startPoint.x + currentPoint.x) / 2;
        const centerY = (startPoint.y + currentPoint.y) / 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.stroke();
      } else if (tool === "line" || tool === "arrow") {
        ctx.beginPath();
        ctx.moveTo(startPoint.x, startPoint.y);
        ctx.lineTo(currentPoint.x, currentPoint.y);
        ctx.stroke();

        if (tool === "arrow") {
          const angle = Math.atan2(currentPoint.y - startPoint.y, currentPoint.x - startPoint.x);
          const arrowLength = 10;
          ctx.beginPath();
          ctx.moveTo(currentPoint.x, currentPoint.y);
          ctx.lineTo(
            currentPoint.x - arrowLength * Math.cos(angle - Math.PI / 6),
            currentPoint.y - arrowLength * Math.sin(angle - Math.PI / 6)
          );
          ctx.moveTo(currentPoint.x, currentPoint.y);
          ctx.lineTo(
            currentPoint.x - arrowLength * Math.cos(angle + Math.PI / 6),
            currentPoint.y - arrowLength * Math.sin(angle + Math.PI / 6)
          );
          ctx.stroke();
        }
      }

      ctx.setLineDash([]);
    }
  }, [canvasObjects, layers, selectedObjectId, isDrawing, startPoint, currentPoint, tool, penColor, mode]);

  if (mode === "reading") {
    return <ReadingView content={content} />;
  }

  if (mode === "whiteboard") {
    return (
      <div className="editorWrap">
        <div className="toolbar">
          {/* Selection Tool */}
          <button
            className={`btn ${tool === "select" ? "active" : ""}`}
            onClick={() => setTool("select")}
            title="Select Tool"
          >
            <MousePointer size={16} />
          </button>

          {/* Drawing Tools */}
          <button
            className={`btn ${tool === "pen" ? "active" : ""}`}
            onClick={() => setTool("pen")}
            title="Pen Tool"
          >
            <Pen size={16} />
          </button>
          <button
            className={`btn ${tool === "erase" ? "active" : ""}`}
            onClick={() => setTool("erase")}
            title="Eraser Tool"
          >
            <Eraser size={16} />
          </button>

          {/* Shape Tools */}
          <div
            style={{
              width: "1px",
              height: "20px",
              background: "var(--stroke)",
              margin: "0 8px",
            }}
          />
          <button
            className={`btn ${tool === "rectangle" ? "active" : ""}`}
            onClick={() => setTool("rectangle")}
            title="Rectangle Tool"
          >
            <Square size={16} />
          </button>
          <button
            className={`btn ${tool === "circle" ? "active" : ""}`}
            onClick={() => setTool("circle")}
            title="Circle Tool"
          >
            <Circle size={16} />
          </button>
          <button
            className={`btn ${tool === "line" ? "active" : ""}`}
            onClick={() => setTool("line")}
            title="Line Tool"
          >
            <Minus size={16} />
          </button>
          <button
            className={`btn ${tool === "arrow" ? "active" : ""}`}
            onClick={() => setTool("arrow")}
            title="Arrow Tool"
          >
            <ArrowRight size={16} />
          </button>
          <button
            className={`btn ${tool === "text" ? "active" : ""}`}
            onClick={() => setTool("text")}
            title="Text Tool"
          >
            <Type size={16} />
          </button>

          {/* Layers and Settings */}
          <div
            style={{
              width: "1px",
              height: "20px",
              background: "var(--stroke)",
              margin: "0 8px",
            }}
          />
          <button
            className={`btn ${showLayersPanel ? "active" : ""}`}
            onClick={() => setShowLayersPanel(!showLayersPanel)}
            title="Layers Panel"
          >
            <Layers size={16} />
          </button>
          <button
            className={`btn ${showPropertiesPanel ? "active" : ""}`}
            onClick={() => setShowPropertiesPanel(!showPropertiesPanel)}
            title="Properties Panel"
          >
            <Settings size={16} />
          </button>

          {/* Color Picker */}
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
              cursor: "pointer",
            }}
            title="Current Color"
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
                  : tool === "select"
                  ? "pointer"
                  : ["rectangle", "circle", "line", "arrow", "text"].includes(tool)
                  ? "crosshair"
                  : "default",
            }}
          />
          <StickyNotes />

          {/* Layers Panel */}
          {showLayersPanel && (
            <div
              style={{
                position: "absolute",
                top: "10px",
                right: "10px",
                background: "var(--bg-secondary)",
                border: "1px solid var(--stroke)",
                borderRadius: "8px",
                padding: "12px",
                minWidth: "200px",
                zIndex: 1000,
              }}
            >
              <h4 style={{ margin: "0 0 8px 0", color: "var(--text)" }}>Layers</h4>
              {layers.map((layer) => (
                <div
                  key={layer.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    padding: "4px 0",
                    cursor: "pointer",
                    background: currentLayerId === layer.id ? "var(--accent)" : "transparent",
                    borderRadius: "4px",
                  }}
                  onClick={() => setCurrentLayerId(layer.id)}
                >
                  <input
                    type="checkbox"
                    checked={layer.visible}
                    onChange={(e) => {
                      e.stopPropagation();
                      updateLayer(layer.id, { visible: e.target.checked });
                    }}
                    style={{ marginRight: "8px" }}
                  />
                  <span style={{ flex: 1, color: "var(--text)" }}>{layer.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* Properties Panel */}
          {showPropertiesPanel && selectedObjectId && (
            <div
              style={{
                position: "absolute",
                top: "10px",
                right: showLayersPanel ? "220px" : "10px",
                background: "var(--bg-secondary)",
                border: "1px solid var(--stroke)",
                borderRadius: "8px",
                padding: "12px",
                minWidth: "200px",
                zIndex: 1000,
              }}
            >
              <h4 style={{ margin: "0 0 8px 0", color: "var(--text)" }}>Properties</h4>
              {(() => {
                const selectedObj = canvasObjects.find(obj => obj.id === selectedObjectId);
                if (!selectedObj) return null;

                return (
                  <div>
                    <div style={{ marginBottom: "8px" }}>
                      <label style={{ display: "block", marginBottom: "4px", color: "var(--text)" }}>
                        Color:
                      </label>
                      <input
                        type="color"
                        value={selectedObj.color}
                        onChange={(e) => updateCanvasObject(selectedObjectId, { color: e.target.value })}
                        style={{ width: "100%" }}
                      />
                    </div>
                    <div style={{ marginBottom: "8px" }}>
                      <label style={{ display: "block", marginBottom: "4px", color: "var(--text)" }}>
                        Stroke Width:
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={selectedObj.strokeWidth}
                        onChange={(e) => updateCanvasObject(selectedObjectId, { strokeWidth: parseInt(e.target.value) })}
                        style={{ width: "100%" }}
                      />
                    </div>
                    {selectedObj.type === "text" && (
                      <div style={{ marginBottom: "8px" }}>
                        <label style={{ display: "block", marginBottom: "4px", color: "var(--text)" }}>
                          Text:
                        </label>
                        <input
                          type="text"
                          value={editingText}
                          onChange={(e) => {
                            setEditingText(e.target.value);
                            updateCanvasObject(selectedObjectId, { text: e.target.value });
                          }}
                          style={{ width: "100%", padding: "4px" }}
                        />
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
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
        <LazyMonacoEditor
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
