import React, { useState, useRef } from 'react';

interface WhiteboardProps {
  // Add props here
}

interface CanvasElement {
  id: string;
  type: 'text' | 'shape' | 'image' | 'connection';
  x: number;
  y: number;
  width?: number;
  height?: number;
  content?: string;
  style?: any;
}

export const Whiteboard: React.FC<WhiteboardProps> = () => {
  const [elements, setElements] = useState<CanvasElement[]>([]);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);

  const addTextElement = (x: number, y: number) => {
    const newElement: CanvasElement = {
      id: Date.now().toString(),
      type: 'text',
      x,
      y,
      content: 'Double click to edit',
      style: {
        fontSize: '16px',
        fontFamily: 'Inter, sans-serif',
        color: '#374151',
      },
    };
    setElements([...elements, newElement]);
  };

  const addShapeElement = (x: number, y: number, shapeType: 'rectangle' | 'circle') => {
    const newElement: CanvasElement = {
      id: Date.now().toString(),
      type: 'shape',
      x,
      y,
      width: 100,
      height: 100,
      style: {
        backgroundColor: '#e5e7eb',
        border: '2px solid #d1d5db',
        borderRadius: shapeType === 'circle' ? '50%' : '4px',
      },
    };
    setElements([...elements, newElement]);
  };

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      addTextElement(x, y);
    }
  };

  const handleElementClick = (elementId: string) => {
    setSelectedElement(elementId);
  };

  const updateElement = (elementId: string, updates: Partial<CanvasElement>) => {
    setElements(elements.map(el => 
      el.id === elementId ? { ...el, ...updates } : el
    ));
  };

  return (
    <div className="whiteboard-container flex-1 flex flex-col bg-gray-50">
      {/* Whiteboard Toolbar */}
      <div className="whiteboard-toolbar bg-white border-b border-gray-200 px-4 py-2 flex items-center space-x-2">
        <button 
          className="tool-btn px-3 py-1 rounded hover:bg-gray-100 text-sm"
          onClick={() => setIsDrawing(!isDrawing)}
        >
          ✏️ Draw
        </button>
        <button className="tool-btn px-3 py-1 rounded hover:bg-gray-100 text-sm">
          📝 Text
        </button>
        <button className="tool-btn px-3 py-1 rounded hover:bg-gray-100 text-sm">
          ⬜ Rectangle
        </button>
        <button className="tool-btn px-3 py-1 rounded hover:bg-gray-100 text-sm">
          ⭕ Circle
        </button>
        <button className="tool-btn px-3 py-1 rounded hover:bg-gray-100 text-sm">
          🔗 Connect
        </button>
        <div className="separator w-px h-4 bg-gray-300 mx-2"></div>
        <button className="tool-btn px-3 py-1 rounded hover:bg-gray-100 text-sm">
          🎨 Color
        </button>
        <button className="tool-btn px-3 py-1 rounded hover:bg-gray-100 text-sm">
          📏 Size
        </button>
      </div>

      {/* Whiteboard Canvas */}
      <div 
        ref={canvasRef}
        className="whiteboard-canvas flex-1 relative overflow-auto bg-white"
        onClick={handleCanvasClick}
        style={{ cursor: isDrawing ? 'crosshair' : 'default' }}
      >
        {/* Grid Background */}
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '20px 20px',
          }}
        />

        {/* Canvas Elements */}
        {elements.map((element) => (
          <div
            key={element.id}
            className={`canvas-element absolute ${
              selectedElement === element.id ? 'ring-2 ring-blue-500' : ''
            }`}
            style={{
              left: element.x,
              top: element.y,
              width: element.width,
              height: element.height,
              ...element.style,
            }}
            onClick={(e) => {
              e.stopPropagation();
              handleElementClick(element.id);
            }}
          >
            {element.type === 'text' && (
              <div 
                className="text-element p-2 min-w-[100px] min-h-[30px]"
                contentEditable
                suppressContentEditableWarning
                onBlur={(e) => updateElement(element.id, { content: e.currentTarget.textContent || '' })}
              >
                {element.content}
              </div>
            )}
            
            {element.type === 'shape' && (
              <div className="shape-element w-full h-full" />
            )}
          </div>
        ))}
      </div>

      {/* Whiteboard Status */}
      <div className="whiteboard-status bg-white border-t border-gray-200 px-4 py-1 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <span>Elements: {elements.length}</span>
          <span>•</span>
          <span>Selected: {selectedElement ? '1' : '0'}</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>Zoom: 100%</span>
          <span>•</span>
          <span>Grid: 20px</span>
        </div>
      </div>
    </div>
  );
};

export default Whiteboard;
