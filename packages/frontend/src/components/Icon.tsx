import React, { cloneElement, isValidElement } from 'react';
import * as Lucide from 'lucide-react';

// Icon Types
export interface IconProps {
  name: string;
  size?: number;
  color?: string;
  strokeWidth?: number;
  className?: string;
}

export interface GradientIconProps extends IconProps {
  idSeed: string;
  cool?: boolean;
}

// Gradient Color Palettes
const WARM_GRADIENTS = [
  ['#F97316', '#F43F5E'],
  ['#F59E0B', '#EF4444'],
  ['#FB7185', '#C026D3']
];

const COOL_GRADIENTS = [
  ['#22D3EE', '#3B82F6'],
  ['#06B6D4', '#14B8A6'],
  ['#818CF8', '#06B6D4']
];

// Utility Functions
function pascalCase(str: string): string {
  return str
    .split(/[:._-]/)
    .map(s => s.charAt(0)?.toUpperCase() + s.slice(1))
    .join('');
}

function pickGradientPair(id: string, cool: boolean): [string, string] {
  const gradients = cool ? COOL_GRADIENTS : WARM_GRADIENTS;
  let hash = 0;
  
  for (const char of id) {
    hash = ((hash * 31) + char.charCodeAt(0)) >>> 0;
  }
  
  return gradients[hash % gradients.length];
}

// Basic Icon Component
export function Icon({ 
  name, 
  size = 20, 
  color = 'currentColor', 
  strokeWidth = 2,
  className = ''
}: IconProps) {
  // Handle Lucide icons
  if (name.startsWith('lucide:')) {
    const iconName = name.split(':')[1];
    const IconComponent = (Lucide as any)[pascalCase(iconName)] || Lucide.HelpCircle;
    
    return (
      <IconComponent 
        size={size} 
        strokeWidth={strokeWidth} 
        color={color}
        className={className}
      />
    );
  }
  
  // Handle logo icons (simple-icons)
  if (name.startsWith('logo:')) {
    const logoName = name.split(':')[1];
    // For now, return a placeholder. You can integrate simple-icons later
    return (
      <div 
        className={`logo-placeholder ${className}`}
        style={{ 
          width: size, 
          height: size, 
          backgroundColor: color,
          borderRadius: '4px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: size * 0.6,
          color: 'white',
          fontWeight: 'bold'
        }}
      >
        {logoName.charAt(0).toUpperCase()}
      </div>
    );
  }
  
  // Default fallback
  return (
    <Lucide.HelpCircle 
      size={size} 
      strokeWidth={strokeWidth} 
      color={color}
      className={className}
    />
  );
}

// Gradient Icon Component
export function GradientIcon({ 
  name, 
  idSeed, 
  size = 20, 
  strokeWidth = 2, 
  cool = false,
  className = ''
}: GradientIconProps) {
  const [color1, color2] = pickGradientPair(idSeed, cool);
  const gradientId = `gradient-${idSeed}`;
  
  // Handle Lucide icons with gradient
  if (name.startsWith('lucide:')) {
    const iconName = name.split(':')[1];
    const IconComponent = (Lucide as any)[pascalCase(iconName)] || Lucide.HelpCircle;
    
    return (
      <svg 
        width={size} 
        height={size} 
        viewBox={`0 0 ${size} ${size}`} 
        focusable="false" 
        aria-hidden="true"
        className={className}
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={color1} />
            <stop offset="100%" stopColor={color2} />
          </linearGradient>
        </defs>
        <g>
          <IconComponent 
            size={size} 
            strokeWidth={strokeWidth} 
            color={`url(#${gradientId})`}
          />
        </g>
      </svg>
    );
  }
  
  // Handle logo icons with gradient
  if (name.startsWith('logo:')) {
    const logoName = name.split(':')[1];
    
    return (
      <svg 
        width={size} 
        height={size} 
        viewBox={`0 0 ${size} ${size}`} 
        focusable="false" 
        aria-hidden="true"
        className={className}
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={color1} />
            <stop offset="100%" stopColor={color2} />
          </linearGradient>
        </defs>
        <rect 
          width={size} 
          height={size} 
          fill={`url(#${gradientId})`}
          rx="4"
        />
        <text
          x={size / 2}
          y={size / 2 + 4}
          textAnchor="middle"
          fill="white"
          fontSize={size * 0.6}
          fontWeight="bold"
          fontFamily="system-ui, sans-serif"
        >
          {logoName.charAt(0).toUpperCase()}
        </text>
      </svg>
    );
  }
  
  // Default fallback with gradient
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox={`0 0 ${size} ${size}`} 
      focusable="false" 
      aria-hidden="true"
      className={className}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={color1} />
          <stop offset="100%" stopColor={color2} />
        </linearGradient>
      </defs>
      <g>
        <Lucide.HelpCircle 
          size={size} 
          strokeWidth={strokeWidth} 
          color={`url(#${gradientId})`}
        />
      </g>
    </svg>
  );
}

// Export default as Icon
export default Icon;
