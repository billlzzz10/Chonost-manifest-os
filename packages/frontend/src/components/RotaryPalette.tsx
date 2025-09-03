import React, { useMemo } from 'react';
import { useAppStore } from '@/state/store';
import { GradientIcon } from './Icon';
import { PaletteItem } from '@/state/store';

interface RotaryPaletteProps {
  side: 'left' | 'right';
  className?: string;
}

export function RotaryPalette({ side, className = '' }: RotaryPaletteProps) {
  const { theme, leftPalette, rightPalette, setCurrentView } = useAppStore();
  
  const palette = side === 'left' ? leftPalette : rightPalette;
  const isCoolTheme = theme === 'dark';
  
  // Calculate positions for rotary layout
  const itemPositions = useMemo(() => {
    const radius = 80;
    const centerX = 0;
    const centerY = 0;
    const angleStep = (2 * Math.PI) / Math.max(palette.length, 1);
    
    return palette.map((_, index) => {
      const angle = index * angleStep - Math.PI / 2; // Start from top
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      return { x, y };
    });
  }, [palette.length]);
  
  const handlePaletteItemClick = (item: PaletteItem) => {
    switch (item.type) {
      case 'color':
        // Handle color selection
        console.log('Selected color:', item.color);
        break;
      case 'tool':
        // Handle tool selection
        console.log('Selected tool:', item.value);
        break;
      case 'command':
        // Handle command execution
        switch (item.value) {
          case 'toggle-mode':
            useAppStore.getState().toggleTheme();
            break;
          case 'analyze':
            setCurrentView('whiteboard');
            break;
          case 'run-script':
            console.log('Running script...');
            break;
          case 'export':
            console.log('Exporting...');
            break;
          case 'open-github':
            window.open('https://github.com', '_blank');
            break;
          case 'open-figma':
            window.open('https://figma.com', '_blank');
            break;
          case 'open-notion':
            window.open('https://notion.so', '_blank');
            break;
          default:
            console.log('Command:', item.value);
        }
        break;
      case 'script':
        // Handle script execution
        console.log('Running script:', item.value);
        break;
    }
  };
  
  return (
    <div className={`rotary-palette ${className}`}>
      <div className="rotary-core">
        {/* Center indicator */}
        <div className="rotary-center">
          <div className="center-dot" />
        </div>
        
        {/* Palette items */}
        {palette.map((item, index) => {
          const position = itemPositions[index];
          const isActive = false; // You can add active state logic here
          
          return (
            <button
              key={item.id}
              className={`rotary-item ${isActive ? 'active' : ''}`}
              title={item.label}
              style={{
                transform: `translate(${position.x}px, ${position.y}px)`,
                background: item.color || 'var(--card)',
                border: item.gradient ? '2px solid transparent' : '1px solid var(--stroke)',
              }}
              onClick={() => handlePaletteItemClick(item)}
            >
              <span className="rotary-icon">
                {item.gradient ? (
                  <GradientIcon
                    name={item.icon}
                    idSeed={item.id}
                    size={20}
                    strokeWidth={2}
                    cool={isCoolTheme}
                  />
                ) : (
                  <GradientIcon
                    name={item.icon}
                    idSeed={item.id}
                    size={20}
                    strokeWidth={2}
                    cool={isCoolTheme}
                  />
                )}
              </span>
              
              {/* Tooltip */}
              <span className="rotary-tooltip">
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
      
      {/* Theme toggle button */}
      <button
        className="theme-toggle"
        onClick={() => useAppStore.getState().toggleTheme()}
        title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
      >
        <GradientIcon
          name={theme === 'light' ? 'lucide:moon' : 'lucide:sun'}
          idSeed="theme-toggle"
          size={16}
          strokeWidth={2}
          cool={isCoolTheme}
        />
      </button>
    </div>
  );
}

export default RotaryPalette;
