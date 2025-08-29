import React from 'react';

interface PageDividerProps {
  variant?: 'line' | 'dots' | 'ornament';
  className?: string;
}

export const PageDivider: React.FC<PageDividerProps> = ({
  variant = 'line',
  className = '',
}) => {
  const baseClasses = 'flex items-center justify-center my-8';

  if (variant === 'line') {
    return (
      <div className={`${baseClasses} ${className}`}>
        <div className="flex-grow h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
      </div>
    );
  }

  if (variant === 'dots') {
    return (
      <div className={`${baseClasses} ${className}`}>
        <div className="flex space-x-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
        </div>
      </div>
    );
  }

  if (variant === 'ornament') {
    return (
      <div className={`${baseClasses} ${className}`}>
        <div className="flex items-center space-x-4">
          <div className="flex-grow h-px bg-gradient-to-r from-transparent to-gray-300"></div>
          <div className="text-gray-400 text-xl">❦</div>
          <div className="flex-grow h-px bg-gradient-to-l from-transparent to-gray-300"></div>
        </div>
      </div>
    );
  }

  return null;
};

