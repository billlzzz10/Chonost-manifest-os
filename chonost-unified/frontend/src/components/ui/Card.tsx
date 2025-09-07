import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  shadow?: boolean;
  rounded?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  className = '',
  padding = 'md',
  shadow = true,
  rounded = true,
}) => {
  const baseClasses = 'bg-white border border-gray-200';
  const shadowClasses = shadow ? 'shadow-md hover:shadow-lg transition-shadow duration-200' : '';
  const roundedClasses = rounded ? 'rounded-xl' : '';
  
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div className={`${baseClasses} ${shadowClasses} ${roundedClasses} ${className}`}>
      {title && (
        <div className="border-b border-gray-100 pb-4 mb-4">
          <h3 className="text-lg font-medium text-gray-800">{title}</h3>
        </div>
      )}
      <div className={paddingClasses[padding]}>
        {children}
      </div>
    </div>
  );
};

