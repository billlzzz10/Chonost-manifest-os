import React, { useState } from 'react';

interface RotaryToolsProps {
  // Add props here
}

export const RotaryTools: React.FC<RotaryToolsProps> = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTool, setActiveTool] = useState<string | null>(null);

  // Left Palette Tools (Contextual)
  const leftTools = [
    { id: 'bold', icon: 'B', label: 'Bold', shortcut: 'Ctrl+B' },
    { id: 'italic', icon: 'I', label: 'Italic', shortcut: 'Ctrl+I' },
    { id: 'underline', icon: 'U', label: 'Underline', shortcut: 'Ctrl+U' },
    { id: 'link', icon: '🔗', label: 'Link', shortcut: 'Ctrl+K' },
    { id: 'image', icon: '🖼️', label: 'Image', shortcut: 'Ctrl+Shift+I' },
    { id: 'code', icon: '💻', label: 'Code', shortcut: 'Ctrl+Shift+C' },
  ];

  // Right Palette Tools (Global)
  const rightTools = [
    { id: 'save', icon: '💾', label: 'Save', shortcut: 'Ctrl+S' },
    { id: 'undo', icon: '↶', label: 'Undo', shortcut: 'Ctrl+Z' },
    { id: 'redo', icon: '↷', label: 'Redo', shortcut: 'Ctrl+Y' },
    { id: 'ai', icon: '🤖', label: 'AI Assistant', shortcut: 'Ctrl+Space' },
    { id: 'search', icon: '🔍', label: 'Search', shortcut: 'Ctrl+F' },
    { id: 'settings', icon: '⚙️', label: 'Settings', shortcut: 'Ctrl+,' },
  ];

  const handleToolClick = (toolId: string) => {
    setActiveTool(toolId);
    // Handle tool action
    console.log(`Tool clicked: ${toolId}`);
  };

  return (
    <div className="rotary-tools-container flex items-center space-x-2">
      {/* Left Palette */}
      <div className="left-palette flex items-center space-x-1">
        {leftTools.map((tool) => (
          <button
            key={tool.id}
            onClick={() => handleToolClick(tool.id)}
            className={`rotary-tool-btn w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-200 ${
              activeTool === tool.id
                ? 'bg-blue-500 text-white shadow-lg scale-110'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:scale-105'
            }`}
            title={`${tool.label} (${tool.shortcut})`}
          >
            {tool.icon}
          </button>
        ))}
      </div>

      {/* Separator */}
      <div className="separator w-px h-6 bg-gray-300"></div>

      {/* Right Palette */}
      <div className="right-palette flex items-center space-x-1">
        {rightTools.map((tool) => (
          <button
            key={tool.id}
            onClick={() => handleToolClick(tool.id)}
            className={`rotary-tool-btn w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-200 ${
              activeTool === tool.id
                ? 'bg-blue-500 text-white shadow-lg scale-110'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:scale-105'
            }`}
            title={`${tool.label} (${tool.shortcut})`}
          >
            {tool.icon}
          </button>
        ))}
      </div>

      {/* Expand/Collapse Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="expand-btn w-6 h-6 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 flex items-center justify-center text-xs transition-all duration-200"
        title={isExpanded ? 'Collapse tools' : 'Expand tools'}
      >
        {isExpanded ? '−' : '+'}
      </button>

      {/* Expanded Tools Panel */}
      {isExpanded && (
        <div className="expanded-tools-panel absolute top-full right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-64 z-50">
          <div className="grid grid-cols-2 gap-2">
            {[...leftTools, ...rightTools].map((tool) => (
              <button
                key={tool.id}
                onClick={() => handleToolClick(tool.id)}
                className="expanded-tool-btn flex items-center space-x-2 px-3 py-2 rounded hover:bg-gray-100 text-left"
              >
                <span className="text-lg">{tool.icon}</span>
                <div className="flex-1">
                  <div className="font-medium text-sm">{tool.label}</div>
                  <div className="text-xs text-gray-500">{tool.shortcut}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RotaryTools;
