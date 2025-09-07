import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../../store/appStore';

interface EditorProps {
  // Add props here
}

export const Editor: React.FC<EditorProps> = () => {
  const [content, setContent] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
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
          console.log('Saving document...');
          break;
        case 'b':
          e.preventDefault();
          // Bold text
          document.execCommand('bold', false);
          break;
        case 'i':
          e.preventDefault();
          // Italic text
          document.execCommand('italic', false);
          break;
        case 'k':
          e.preventDefault();
          // Create link
          const url = prompt('Enter URL:');
          if (url) {
            document.execCommand('createLink', false, url);
          }
          break;
        case 'p':
          e.preventDefault();
          // Toggle preview
          setShowPreview(!showPreview);
          break;
      }
    }
  };

  const insertMarkdown = (markdown: string) => {
    const textarea = editorRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const selectedText = content.substring(start, end);
      
      let newContent = content.substring(0, start);
      if (markdown.includes('{}')) {
        newContent += markdown.replace('{}', selectedText);
      } else {
        newContent += markdown + selectedText;
      }
      newContent += content.substring(end);
      
      setContent(newContent);
      
      // Set cursor position
      setTimeout(() => {
        if (textarea) {
          textarea.focus();
          textarea.setSelectionRange(start + markdown.length, start + markdown.length);
        }
      }, 0);
    }
  };

  const toolbarActions = [
    { label: 'Bold', action: () => insertMarkdown('**{}**'), shortcut: 'Ctrl+B' },
    { label: 'Italic', action: () => insertMarkdown('*{}*'), shortcut: 'Ctrl+I' },
    { label: 'Link', action: () => insertMarkdown('[{}](url)'), shortcut: 'Ctrl+K' },
    { label: 'H1', action: () => insertMarkdown('# {}'), shortcut: '' },
    { label: 'H2', action: () => insertMarkdown('## {}'), shortcut: '' },
    { label: 'H3', action: () => insertMarkdown('### {}'), shortcut: '' },
    { label: 'List', action: () => insertMarkdown('- {}'), shortcut: '' },
    { label: 'Code', action: () => insertMarkdown('`{}`'), shortcut: '' },
  ];

  return (
    <div className="editor-container flex-1 flex flex-col bg-white">
      {/* Editor Toolbar */}
      <div className="editor-toolbar bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {toolbarActions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              className="toolbar-btn px-3 py-1 rounded hover:bg-gray-200 text-sm flex items-center space-x-1"
              title={action.shortcut ? `${action.label} (${action.shortcut})` : action.label}
            >
              <span>{action.label}</span>
              {action.shortcut && (
                <span className="text-xs text-gray-500">({action.shortcut})</span>
              )}
            </button>
          ))}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className={`preview-btn px-3 py-1 rounded text-sm ${
              showPreview ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {showPreview ? 'Hide Preview' : 'Show Preview'}
          </button>
        </div>
      </div>

      {/* Editor Content */}
      <div className="editor-content flex-1 flex">
        {/* Editor */}
        <div className={`editor-pane ${showPreview ? 'w-1/2' : 'w-full'} p-6`}>
          <div
            ref={editorRef}
            className={`editor-textarea w-full h-full outline-none resize-none border rounded-lg p-4 ${
              isFocused ? 'ring-2 ring-blue-500 border-blue-300' : 'border-gray-300'
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

        {/* Preview */}
        {showPreview && (
          <div className="preview-pane w-1/2 border-l border-gray-200 p-6">
            <div className="preview-content prose prose-sm max-w-none">
              <div 
                className="markdown-preview"
                dangerouslySetInnerHTML={{ 
                  __html: content
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
                    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold">$1</h1>')
                    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold">$1</h2>')
                    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold">$1</h3>')
                    .replace(/^- (.*$)/gm, '<li>$1</li>')
                    .replace(/\n/g, '<br>')
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Editor Status */}
      <div className="editor-status bg-gray-50 border-t border-gray-200 px-4 py-1 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <span>Words: {content.split(/\s+/).filter(word => word.length > 0).length}</span>
          <span>Characters: {content.length}</span>
          <span>Lines: {content.split('\n').length}</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>Last saved: Just now</span>
          <span>•</span>
          <span>AI suggestions: 3</span>
          <span>•</span>
          <span>Mode: {showPreview ? 'Split' : 'Edit'}</span>
        </div>
      </div>
    </div>
  );
};

export default Editor;
