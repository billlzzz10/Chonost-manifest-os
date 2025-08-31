import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Save, Eye, Palette, Edit3, User, Book, RotateCcw } from 'lucide-react';

const RotaryPalette = ({ onColorSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [rotation, setRotation] = useState(0);
  
  const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#F97316'];

  const handleRotate = () => {
    setRotation(prev => prev + 60);
  };

  return (
    <div className="fixed top-4 left-4 z-50">
      <div className="relative">
        <Button
          variant="outline"
          size="icon"
          className="w-12 h-12 rounded-full shadow-lg"
          onClick={() => setIsOpen(!isOpen)}
        >
          <Palette className="h-5 w-5" />
        </Button>

        {isOpen && (
          <div className="absolute top-0 left-0 w-32 h-32">
            <div
              className="relative w-full h-full transition-transform duration-500 ease-in-out"
              style={{ transform: `rotate(${rotation}deg)` }}
            >
              {colors.map((color, index) => {
                const angle = (index * 60) * (Math.PI / 180);
                const radius = 40;
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;

                return (
                  <button
                    key={index}
                    onClick={() => onColorSelect(color)}
                    className="absolute w-8 h-8 rounded-full shadow-md hover:scale-110 transition-transform duration-200 border-2 border-white"
                    style={{
                      backgroundColor: color,
                      left: `calc(50% + ${x}px - 16px)`,
                      top: `calc(50% + ${y}px - 16px)`,
                    }}
                  />
                );
              })}
            </div>
            
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-6 h-6 rounded-full"
              onClick={handleRotate}
            >
              <RotateCcw className="h-3 w-3" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

const RotaryToolkit = ({ onSave }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [rotation, setRotation] = useState(0);

  const tools = [
    { name: 'Save', icon: Save, action: onSave },
    { name: 'Edit', icon: Edit3, action: () => console.log('Edit') },
    { name: 'Character', icon: User, action: () => console.log('Character') },
    { name: 'Reference', icon: Book, action: () => console.log('Reference') },
  ];

  const handleRotate = () => {
    setRotation(prev => prev + 90);
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className="relative">
        <Button
          variant="outline"
          size="icon"
          className="w-12 h-12 rounded-full shadow-lg"
          onClick={() => setIsOpen(!isOpen)}
        >
          <Edit3 className="h-5 w-5" />
        </Button>

        {isOpen && (
          <div className="absolute top-0 right-0 w-32 h-32">
            <div
              className="relative w-full h-full transition-transform duration-500 ease-in-out"
              style={{ transform: `rotate(${rotation}deg)` }}
            >
              {tools.map((tool, index) => {
                const angle = (index * 90) * (Math.PI / 180);
                const radius = 40;
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;

                return (
                  <Button
                    key={index}
                    variant="outline"
                    size="icon"
                    className="absolute w-10 h-10 rounded-full shadow-md hover:scale-110 transition-transform duration-200"
                    style={{
                      left: `calc(50% + ${x}px - 20px)`,
                      top: `calc(50% + ${y}px - 20px)`,
                    }}
                    onClick={() => tool.action()}
                    title={tool.name}
                  >
                    <tool.icon className="h-4 w-4" />
                  </Button>
                );
              })}
            </div>
            
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-1/2 right-1/2 transform translate-x-1/2 -translate-y-1/2 w-6 h-6 rounded-full"
              onClick={handleRotate}
            >
              <RotateCcw className="h-3 w-3" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

const Editor = () => {
  const [content, setContent] = useState('');
  const [selectedColor, setSelectedColor] = useState('#3B82F6');
  const [wordCount, setWordCount] = useState(0);
  const [characterCount, setCharacterCount] = useState(0);

  const handleContentChange = (value) => {
    setContent(value);
    setWordCount(value.split(' ').filter(word => word.length > 0).length);
    setCharacterCount(value.length);
  };

  const handleSave = () => {
    console.log('Saving document...');
    // Here you would typically save to the backend
  };

  return (
    <div className="min-h-screen bg-gray-50 relative">
      {/* Rotary Controls */}
      <RotaryPalette onColorSelect={setSelectedColor} />
      <RotaryToolkit onSave={handleSave} />

      {/* Main Editor */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card className="shadow-lg">
          <CardHeader className="border-b">
            <div className="flex justify-between items-center">
              <CardTitle className="text-xl">Document Editor</CardTitle>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4 mr-2" />
                  Preview
                </Button>
                <Button size="sm" onClick={handleSave}>
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="p-6">
            <Textarea
              value={content}
              onChange={(e) => handleContentChange(e.target.value)}
              placeholder="Start writing your story..."
              className="min-h-[500px] resize-none border-none focus:ring-0 focus:outline-none text-base leading-relaxed"
            />
          </CardContent>

          <div className="border-t bg-gray-50 px-6 py-3 rounded-b-lg">
            <div className="flex justify-between items-center text-sm text-gray-500">
              <div className="flex space-x-4">
                <span>Words: {wordCount}</span>
                <span>Characters: {characterCount}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span>Theme:</span>
                <div
                  className="w-4 h-4 rounded-full border border-gray-300"
                  style={{ backgroundColor: selectedColor }}
                />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Color Indicator */}
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

export default Editor;

