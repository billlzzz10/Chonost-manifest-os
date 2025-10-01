import React, { useState } from 'react';
import { Icon } from './Icon';

interface RotaryPaletteProps {
  colors?: string[];
  onColorSelect?: (color: string) => void;
  className?: string;
}

export const RotaryPalette: React.FC<RotaryPaletteProps> = ({
  colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#F97316'],
  onColorSelect,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [rotation, setRotation] = useState(0);

  const handleColorSelect = (color: string) => {
    if (onColorSelect) {
      onColorSelect(color);
    }
    setIsOpen(false);
  };

  const handleRotate = () => {
    setRotation(prev => prev + 60);
  };

  return (
    <div className={`fixed top-4 left-4 z-50 ${className}`}>
      <div className="relative">
        {/* Main palette button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-12 h-12 bg-white rounded-full shadow-lg border-2 border-gray-200 flex items-center justify-center hover:shadow-xl transition-all duration-200"
        >
          <Icon name="palette" size="md" />
        </button>

        {/* Color palette */}
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
                    onClick={() => handleColorSelect(color)}
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
            
            {/* Rotate button */}
            <button
              onClick={handleRotate}
              className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-6 h-6 bg-gray-100 rounded-full shadow-sm hover:bg-gray-200 transition-colors duration-200 flex items-center justify-center"
            >
              <div className="w-2 h-2 bg-gray-600 rounded-full"></div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

