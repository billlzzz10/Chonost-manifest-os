import React from 'react';

interface TypographyProps {
  variant: 'h1' | 'h2' | 'h3' | 'h4' | 'body' | 'caption';
  children: React.ReactNode;
  className?: string;
}

export const Typography: React.FC<TypographyProps> = ({ variant, children, className = '' }) => {
  const baseClasses = 'text-gray-800 font-normal';
  
  const variantClasses = {
    h1: 'text-4xl font-medium mb-6',
    h2: 'text-3xl font-medium mb-5',
    h3: 'text-2xl font-medium mb-4',
    h4: 'text-xl font-medium mb-3',
    body: 'text-base leading-relaxed mb-3',
    caption: 'text-sm text-gray-600 mb-2',
  };

  const Component = variant.startsWith('h') ? variant as keyof JSX.IntrinsicElements : 'p';
  
  return (
    <Component className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {children}
    </Component>
  );
};

