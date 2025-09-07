import React, { useState, useRef, useEffect } from 'react';

interface WhiteboardProps {
  // Add props here
}

interface CanvasElement {
  id: string;
  type: 'text' | 'shape' | 'image' | 'connection' | 'drawing';
  x: number;
  y: number;
  width?: number;
  height?: number;
  content?: string;
  style?: any;
  points?: { x: number; y: number }[];
}

export const Whiteboard: React.FC<WhiteboardProps> = () => {
  const [elements, setElements] = useState<CanvasElement[]>([]);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentTool, setCurrentTool] = useState<'select' | 'draw' | 'text' | 'shape'>('select');
  const [drawingPoints, setDrawingPoints] = useState<{ x: number; y: number }[]>([]);
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
        backgroundColor: 'transparent',
        border: 'none',
        outline: 'none',
        minWidth: '100px',
        minHeight: '30px',
        padding: '4px',
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
        cursor: 'move',
      },
    };
    setElements([...elements, newElement]);
  };

  const addDrawingElement = (points: { x: number; y: number }[]) => {
    if (points.length < 2) return;
    
    const newElement: CanvasElement = {
      id: Date.now().toString(),
      type: 'drawing',
      x: Math.min(...points.map(p => p.x)),
      y: Math.min(...points.map(p => p.y)),
      width: Math.max(...points.map(p => p.x)) - Math.min(...points.map(p => p.x)),
      height: Math.max(...points.map(p => p.y)) - Math.min(...points.map(p => p.y)),
      points,
      style: {
        stroke: '#374151',
        strokeWidth: '2px',
        fill: 'none',
      },
    };
    setElements([...elements, newElement]);
  };

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      switch (currentTool) {
        case 'text':
          addTextElement(x, y);
          break;
        case 'shape':
          addShapeElement(x, y, 'rectangle');
          break;
        case 'draw':
          setIsDrawing(true);
          setDrawingPoints([{ x, y }]);
          break;
      }
    }
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (isDrawing && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      setDrawingPoints(prev => [...prev, { x, y }]);
    }
  };

  const handleCanvasMouseUp = () => {
    if (isDrawing && drawingPoints.length > 1) {
      addDrawingElement(drawingPoints);
      setIsDrawing(false);
      setDrawingPoints([]);
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

  const deleteSelectedElement = () => {
    if (selectedElement) {
      setElements(elements.filter(el => el.id !== selectedElement));
      setSelectedElement(null);
    }
  };

  const tools = [
    { id: 'select', label: 'Select', icon: '👆' },
    { id: 'draw', label: 'Draw', icon: '✏️' },
    { id: 'text', label: 'Text', icon: '📝' },
    { id: 'shape', label: 'Shape', icon: '⬜' },
  ];

  return (
    <div className="whiteboard-container flex-1 flex flex-col bg-gray-50">
      {/* Whiteboard Toolbar */}
      <div className="whiteboard-toolbar bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {tools.map((tool) => (
            <button
              key={tool.id}
              onClick={() => setCurrentTool(tool.id as any)}
              className={`tool-btn px-3 py-1 rounded text-sm flex items-center space-x-1 ${
                currentTool === tool.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <span>{tool.icon}</span>
              <span>{tool.label}</span>
            </button>
          ))}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={deleteSelectedElement}
            disabled={!selectedElement}
            className="delete-btn px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Delete
          </button>
          <button className="clear-btn px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600">
            Clear All
          </button>
        </div>
      </div>

      {/* Whiteboard Canvas */}
      <div 
        ref={canvasRef}
        className="whiteboard-canvas flex-1 relative overflow-auto bg-white"
        onClick={handleCanvasClick}
        onMouseMove={handleCanvasMouseMove}
        onMouseUp={handleCanvasMouseUp}
        style={{ 
          cursor: currentTool === 'draw' ? 'crosshair' : 
                 currentTool === 'text' ? 'text' : 'default' 
        }}
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

        {/* Drawing in Progress */}
        {isDrawing && drawingPoints.length > 1 && (
          <svg className="absolute inset-0 pointer-events-none">
            <polyline
              points={drawingPoints.map(p => `${p.x},${p.y}`).join(' ')}
              stroke="#374151"
              strokeWidth="2"
              fill="none"
            />
          </svg>
        )}

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

            {element.type === 'drawing' && element.points && (
              <svg className="w-full h-full absolute inset-0">
                <polyline
                  points={element.points.map(p => `${p.x - element.x},${p.y - element.y}`).join(' ')}
                  stroke={element.style?.stroke || '#374151'}
                  strokeWidth={element.style?.strokeWidth || '2px'}
                  fill="none"
                />
              </svg>
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
          <span>•</span>
          <span>Tool: {currentTool}</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>Zoom: 100%</span>
          <span>•</span>
          <span>Grid: 20px</span>
          <span>•</span>
          <span>Drawing: {isDrawing ? 'Active' : 'Inactive'}</span>
        </div>
      </div>
    </div>
  );
};

export default Whiteboard;
