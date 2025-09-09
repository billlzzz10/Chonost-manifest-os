import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../store/appStore';
import { Save, FileText, Copy, Download, Upload, Zap } from 'lucide-react';
import { getOptimizedModel, calculateCost } from '../config/tiers';
import toast from 'react-hot-toast';

const MAX_TEXT_LENGTH = 3000;
const AUTO_SAVE_INTERVAL = 30000; // 30 seconds

interface DynamicWhiteboardProps {
  content?: string;
  onContentChange?: (content: string) => void;
}

const DynamicWhiteboard: React.FC<DynamicWhiteboardProps> = ({
  content = '',
  onContentChange
}) => {
  const [text, setText] = useState(content);
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { createDocument, updateDocument, currentDocument } = useAppStore();

  // Auto-save functionality
  useEffect(() => {
    const interval = setInterval(() => {
      if (text && text !== content) {
        handleAutoSave();
      }
    }, AUTO_SAVE_INTERVAL);

    return () => clearInterval(interval);
  }, [text, content]);

  // Handle text changes
  const handleTextChange = (value: string) => {
    setText(value);
    onContentChange?.(value);

    // Auto-convert to file if text is too long
    if (value.length > MAX_TEXT_LENGTH && !currentDocument) {
      handleConvertToFile(value);
    }
  };

  // Auto-save function
  const handleAutoSave = async () => {
    if (!text.trim()) return;

    setIsAutoSaving(true);
    try {
      if (currentDocument) {
        await updateDocument(currentDocument.id, { content: text });
      } else {
        await createDocument('Auto-saved Whiteboard', text);
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    } finally {
      setIsAutoSaving(false);
    }
  };

  // Convert long text to file
  const handleConvertToFile = async (content: string) => {
    try {
      const fileName = `whiteboard_${Date.now()}.txt`;
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      // Create document in store
      await createDocument(fileName, content);

      // Clear the whiteboard
      setText('');
      onContentChange?.('');

      toast.success(`Text converted to file: ${fileName}`);
    } catch (error) {
      console.error('File conversion failed:', error);
    }
  };

  // Handle paste events
  const handlePaste = (e: React.ClipboardEvent) => {
    const pastedText = e.clipboardData.getData('text');
    const currentText = text;
    const newText = currentText + pastedText;

    if (newText.length > MAX_TEXT_LENGTH) {
      e.preventDefault();
      handleConvertToFile(newText);
    }
  };

  // Generate AI suggestions
  const generateAISuggestions = async () => {
    if (!text.trim()) return;

    setIsGenerating(true);
    try {
      const optimizedModel = getOptimizedModel('writing');

      // Simulate AI suggestions (replace with actual AI call)
      const suggestions = [
        "Consider breaking this into smaller sections",
        "Add more descriptive language",
        "Include specific examples",
        "Consider the reader's perspective"
      ];

      setAiSuggestions(suggestions);
    } catch (error) {
      console.error('AI suggestion failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content.length > MAX_TEXT_LENGTH) {
        alert('File is too large. It will be loaded as a document instead.');
        createDocument(file.name, content);
      } else {
        setText(content);
        onContentChange?.(content);
      }
    };
    reader.readAsText(file);
  };

  // Export as file
  const handleExport = () => {
    if (!text.trim()) return;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `whiteboard_${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Copied to clipboard!');
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  return (
    <div className="dynamic-whiteboard h-full flex flex-col bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-gray-800">Dynamic Whiteboard</h2>
          <span className="text-sm text-gray-500">
            {text.length}/{MAX_TEXT_LENGTH} characters
          </span>
          {isAutoSaving && (
            <span className="text-sm text-blue-600 flex items-center gap-1">
              <Save size={14} />
              Auto-saving...
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={generateAISuggestions}
            disabled={isGenerating || !text.trim()}
            className="p-2 text-purple-600 hover:bg-purple-50 rounded disabled:opacity-50"
            title="Get AI suggestions"
          >
            <Zap size={18} />
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded"
            title="Upload file"
          >
            <Upload size={18} />
          </button>

          <button
            onClick={handleCopy}
            disabled={!text.trim()}
            className="p-2 text-green-600 hover:bg-green-50 rounded disabled:opacity-50"
            title="Copy to clipboard"
          >
            <Copy size={18} />
          </button>

          <button
            onClick={handleExport}
            disabled={!text.trim()}
            className="p-2 text-orange-600 hover:bg-orange-50 rounded disabled:opacity-50"
            title="Export as file"
          >
            <Download size={18} />
          </button>
        </div>
      </div>

      {/* AI Suggestions */}
      {aiSuggestions.length > 0 && (
        <div className="border-b border-gray-200 p-4 bg-blue-50">
          <h3 className="text-sm font-medium text-blue-800 mb-2">AI Suggestions:</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            {aiSuggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-500">•</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Text Area */}
      <div className="flex-1 p-4">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => handleTextChange(e.target.value)}
          onPaste={handlePaste}
          placeholder="Start writing... Text over 3000 characters will automatically be saved as a file."
          className="w-full h-full resize-none border-none outline-none text-gray-800 placeholder-gray-400"
          style={{ minHeight: '400px' }}
        />
      </div>

      {/* Warning for long text */}
      {text.length > MAX_TEXT_LENGTH * 0.8 && (
        <div className="border-t border-yellow-200 bg-yellow-50 p-4">
          <div className="flex items-center gap-2 text-yellow-800">
            <FileText size={18} />
            <span className="text-sm">
              Text is getting long. Consider converting to a file or document.
            </span>
            <button
              onClick={() => handleConvertToFile(text)}
              className="ml-auto px-3 py-1 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700"
            >
              Convert to File
            </button>
          </div>
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.md"
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  );
};

export default DynamicWhiteboard;