import React, { useState, useRef } from 'react';
import { Input } from './Input';
import { Button } from './Button';
import { Typography } from './Typography';
import { RotaryPalette } from './RotaryPalette';
import { RotaryToolkit } from './RotaryToolkit';
import { MarkdownAnalyzer } from './MarkdownAnalyzer';
import { CharacterRelationshipMap } from './CharacterRelationshipMap';
import { ApiService, Manuscript, ManuscriptAnalysis } from './ApiService';

interface AdvancedEditorProps {
  content?: string;
  onContentChange?: (content: string) => void;
  onSave?: () => void;
  className?: string;
}

export const AdvancedEditor: React.FC<AdvancedEditorProps> = ({
  content = '',
  onContentChange,
  onSave,
  className = '',
}) => {
  const [editorContent, setEditorContent] = useState(content);
  const [selectedColor, setSelectedColor] = useState('#3B82F6');
  const [showAnalyzer, setShowAnalyzer] = useState(false);
  const [showRelationshipMap, setShowRelationshipMap] = useState(false);
  const [characters, setCharacters] = useState([]);
  const [currentManuscript, setCurrentManuscript] = useState<Manuscript | null>(null);
  const [analysis, setAnalysis] = useState<ManuscriptAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [autoSaveStatus, setAutoSaveStatus] = useState<'saved' | 'saving' | 'error'>('saved');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleContentChange = (value: string) => {
    setEditorContent(value);
    if (onContentChange) {
      onContentChange(value);
    }
    
    // Auto-save after 2 seconds of inactivity
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    
    setAutoSaveStatus('saving');
    autoSaveTimeoutRef.current = setTimeout(async () => {
      if (currentManuscript) {
        try {
          await ApiService.autoSave(currentManuscript.id, value);
          setAutoSaveStatus('saved');
        } catch (error) {
          setAutoSaveStatus('error');
          console.error('Auto-save failed:', error);
        }
      }
    }, 2000);
  };

  const handleSave = async () => {
    if (currentManuscript) {
      try {
        setIsLoading(true);
        await ApiService.updateManuscript(currentManuscript.id, {
          content: editorContent,
          title: currentManuscript.title
        });
        setAutoSaveStatus('saved');
      } catch (error) {
        setAutoSaveStatus('error');
        console.error('Save failed:', error);
      } finally {
        setIsLoading(false);
      }
    }
    
    if (onSave) {
      onSave();
    }
  };

  const insertText = (text: string) => {
    if (!textareaRef.current) return;
    
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newContent = editorContent.substring(0, start) + text + editorContent.substring(end);
    
    setEditorContent(newContent);
    if (onContentChange) {
      onContentChange(newContent);
    }
    
    // Set cursor position after inserted text
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + text.length, start + text.length);
    }, 0);
  };

  const formatText = (format: string) => {
    if (!textareaRef.current) return;
    
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = editorContent.substring(start, end);
    
    let formattedText = '';
    switch (format) {
      case 'bold':
        formattedText = `**${selectedText}**`;
        break;
      case 'italic':
        formattedText = `*${selectedText}*`;
        break;
      case 'heading':
        formattedText = `## ${selectedText}`;
        break;
      default:
        formattedText = selectedText;
    }
    
    const newContent = editorContent.substring(0, start) + formattedText + editorContent.substring(end);
    setEditorContent(newContent);
    if (onContentChange) {
      onContentChange(newContent);
    }
  };

  const tools = [
    { name: 'Save', icon: 'save', action: handleSave },
    { name: 'Bold', icon: 'edit', action: () => formatText('bold') },
    { name: 'Character Analysis', icon: 'user', action: () => setShowAnalyzer(!showAnalyzer) },
    { name: 'Relationship Map', icon: 'book', action: () => setShowRelationshipMap(!showRelationshipMap) },
  ];

  const handleCharactersAnalyzed = (analyzedCharacters: any[]) => {
    const formattedCharacters = analyzedCharacters.map((char, index) => ({
      id: `char-${index}`,
      name: char.name,
      relationships: char.relationships,
      appearances: char.mentions,
    }));
    setCharacters(formattedCharacters);
  };

  return (
    <div className={`relative min-h-screen ${className}`}>
      {/* Rotary controls */}
      <RotaryPalette onColorSelect={setSelectedColor} />
      <RotaryToolkit tools={tools} />

      {/* Main editor area */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Editor Column */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
              {/* Editor header */}
              <div className="border-b border-gray-200 px-6 py-4">
                <div className="flex justify-between items-center">
                  <Typography variant="h3" className="mb-0">Advanced Editor</Typography>
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

              {/* Formatting toolbar */}
              <div className="border-b border-gray-100 px-6 py-3 bg-gray-50">
                <div className="flex space-x-2">
                  <Button variant="secondary" size="sm" onClick={() => formatText('bold')}>
                    Bold
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => formatText('italic')}>
                    Italic
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => formatText('heading')}>
                    Heading
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => insertText('\n---\n')}>
                    Divider
                  </Button>
                </div>
              </div>

              {/* Editor content */}
              <div className="p-6">
                <textarea
                  ref={textareaRef}
                  className="w-full h-96 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
                  placeholder="Start writing your story..."
                  value={editorContent}
                  onChange={(e) => handleContentChange(e.target.value)}
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

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Character Analysis */}
            {showAnalyzer && (
              <MarkdownAnalyzer 
                onCharactersAnalyzed={handleCharactersAnalyzed}
              />
            )}

            {/* Relationship Map */}
            {showRelationshipMap && characters.length > 0 && (
              <CharacterRelationshipMap characters={characters} />
            )}

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <Typography variant="h4" className="mb-4">Quick Actions</Typography>
              <div className="space-y-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={() => insertText('\n## Chapter \n\n')}
                >
                  Add Chapter
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={() => insertText('\n> ')}
                >
                  Add Quote
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={() => insertText('\n- ')}
                >
                  Add List Item
                </Button>
              </div>
            </div>

            {/* Writing Stats */}
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <Typography variant="h4" className="mb-4">Writing Stats</Typography>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Words:</span>
                  <span className="text-sm font-medium">
                    {editorContent.split(' ').filter(word => word.length > 0).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Characters:</span>
                  <span className="text-sm font-medium">{editorContent.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Paragraphs:</span>
                  <span className="text-sm font-medium">
                    {editorContent.split('\n\n').filter(p => p.trim().length > 0).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Reading Time:</span>
                  <span className="text-sm font-medium">
                    {Math.ceil(editorContent.split(' ').filter(word => word.length > 0).length / 200)} min
                  </span>
                </div>
              </div>
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

