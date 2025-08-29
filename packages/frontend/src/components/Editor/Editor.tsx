import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../../store/appStore';

interface EditorProps {
  // Add props here
}

export const Editor: React.FC<EditorProps> = () => {
  const [content, setContent] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);
  const { currentDocument } = useAppStore();

  useEffect(() => {
    // Load document content
    if (currentDocument) {
      setContent(currentDocument.content || '');
    }
  }, [currentDocument]);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    // Auto-save functionality
    // TODO: Implement auto-save
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Handle special key combinations
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 's':
          e.preventDefault();
          // Save document
          break;
        case 'b':
          e.preventDefault();
          // Bold text
          break;
        case 'i':
          e.preventDefault();
          // Italic text
          break;
        case 'k':
          e.preventDefault();
          // Create link
          break;
      }
    }
  };

  return (
    <div className="editor-container flex-1 flex flex-col bg-white">
      {/* Editor Toolbar */}
      <div className="editor-toolbar bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center space-x-2">
        <button className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm">
          Bold
        </button>
        <button className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm">
          Italic
        </button>
        <button className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm">
          Link
        </button>
        <div className="separator w-px h-4 bg-gray-300 mx-2"></div>
        <button className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm">
          Heading 1
        </button>
        <button className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm">
          Heading 2
        </button>
        <div className="separator w-px h-4 bg-gray-300 mx-2"></div>
        <button className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm">
          Bullet List
        </button>
        <button className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm">
          Numbered List
        </button>
      </div>

      {/* Editor Content */}
      <div className="editor-content flex-1 p-6">
        <div
          ref={editorRef}
          className={`editor-textarea w-full h-full outline-none resize-none ${
            isFocused ? 'ring-2 ring-blue-500' : ''
          }`}
          contentEditable
          suppressContentEditableWarning
          onInput={(e) => handleContentChange(e.currentTarget.textContent || '')}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          style={{
            minHeight: '100%',
            fontFamily: 'Inter, system-ui, sans-serif',
            fontSize: '16px',
            lineHeight: '1.6',
            color: '#374151'
          }}
        >
          {content}
        </div>
      </div>

      {/* Editor Status */}
      <div className="editor-status bg-gray-50 border-t border-gray-200 px-4 py-1 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <span>Words: {content.split(/\s+/).filter(word => word.length > 0).length}</span>
          <span>Characters: {content.length}</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>Last saved: Just now</span>
          <span>•</span>
          <span>AI suggestions: 3</span>
        </div>
      </div>
    </div>
  );
};

export default Editor;
