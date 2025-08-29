import React, { useState } from 'react';
import { Icon } from '../atoms/Icon';

interface Tool {
  name: string;
  icon: string;
  action: () => void;
}

interface RotaryToolkitProps {
  tools?: Tool[];
  className?: string;
}

export const RotaryToolkit: React.FC<RotaryToolkitProps> = ({
  tools = [
    { name: 'Save', icon: 'save', action: () => console.log('Save') },
    { name: 'Edit', icon: 'edit', action: () => console.log('Edit') },
    { name: 'User', icon: 'user', action: () => console.log('User') },
    { name: 'Book', icon: 'book', action: () => console.log('Book') },
  ],
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [rotation, setRotation] = useState(0);

  const handleToolSelect = (tool: Tool) => {
    tool.action();
    setIsOpen(false);
  };

  const handleRotate = () => {
    setRotation(prev => prev + 90);
  };

  return (
    <div className={`fixed top-4 right-4 z-50 ${className}`}>
      <div className="relative">
        {/* Main toolkit button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-200 flex items-center justify-center hover:shadow-xl transition-all duration-200"
        >
          <Icon name="edit" size="md" />
        </button>

        {/* Tool palette */}
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
                  <button
                    key={index}
                    onClick={() => handleToolSelect(tool)}
                    className="absolute w-10 h-10 bg-white rounded-full shadow-md hover:scale-110 transition-transform duration-200 border-2 border-gray-200 flex items-center justify-center"
                    style={{
                      left: `calc(50% + ${x}px - 20px)`,
                      top: `calc(50% + ${y}px - 20px)`,
                    }}
                    title={tool.name}
                  >
                    <Icon name={tool.icon} size="sm" />
                  </button>
                );
              })}
            </div>
            
            {/* Rotate button */}
            <button
              onClick={handleRotate}
              className="absolute top-1/2 right-1/2 transform translate-x-1/2 -translate-y-1/2 w-6 h-6 bg-gray-100 rounded-full shadow-sm hover:bg-gray-200 transition-colors duration-200 flex items-center justify-center"
            >
              <div className="w-2 h-2 bg-gray-600 rounded-full"></div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

