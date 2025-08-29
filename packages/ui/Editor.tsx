import React, { useState } from 'react';
import { Input } from './Input';
import { Button } from './Button';
import { Typography } from './Typography';
import { RotaryPalette } from './RotaryPalette';
import { RotaryToolkit } from './RotaryToolkit';

interface EditorProps {
  content?: string;
  onContentChange?: (content: string) => void;
  onSave?: () => void;
  className?: string;
}

export const Editor: React.FC<EditorProps> = ({
  content = '',
  onContentChange,
  onSave,
  className = '',
}) => {
  const [editorContent, setEditorContent] = useState(content);
  const [selectedColor, setSelectedColor] = useState('#3B82F6');

  const handleContentChange = (value: string) => {
    setEditorContent(value);
    if (onContentChange) {
      onContentChange(value);
    }
  };

  const handleSave = () => {
    if (onSave) {
      onSave();
    }
  };

  const tools = [
    { name: 'Save', icon: 'save', action: handleSave },
    { name: 'Bold', icon: 'edit', action: () => console.log('Bold') },
    { name: 'Character', icon: 'user', action: () => console.log('Character') },
    { name: 'Reference', icon: 'book', action: () => console.log('Reference') },
  ];

  return (
    <div className={`relative min-h-screen ${className}`}>
      {/* Rotary controls */}
      <RotaryPalette onColorSelect={setSelectedColor} />
      <RotaryToolkit tools={tools} />

      {/* Main editor area */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Editor header */}
          <div className="border-b border-gray-200 px-6 py-4">
            <div className="flex justify-between items-center">
              <Typography variant="h3" className="mb-0">Document Editor</Typography>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  Preview
                </Button>
                <Button variant="primary" size="sm" onClick={handleSave}>
                  Save
                </Button>
              </div>
            </div>
          </div>

          {/* Editor content */}
          <div className="p-6">
            <Input
              type="textarea"
              value={editorContent}
              onChange={handleContentChange}
              placeholder="Start writing your story..."
              rows={20}
              className="mb-0"
            />
          </div>

          {/* Editor footer */}
          <div className="border-t border-gray-100 px-6 py-3 bg-gray-50">
            <div className="flex justify-between items-center text-sm text-gray-500">
              <span>Words: {editorContent.split(' ').filter(word => word.length > 0).length}</span>
              <span>Characters: {editorContent.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Color indicator */}
      <div className="fixed bottom-4 left-4 z-40">
        <div
          className="w-8 h-8 rounded-full border-2 border-white shadow-lg"
          style={{ backgroundColor: selectedColor }}
          title="Selected color"
        />
      </div>
    </div>
  );
};

