import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const PageDivider = ({ variant = 'line' }) => {
  if (variant === 'line') {
    return (
      <div className="flex items-center justify-center my-8">
        <div className="flex-grow h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
      </div>
    );
  }

  if (variant === 'dots') {
    return (
      <div className="flex items-center justify-center my-8">
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
      <div className="flex items-center justify-center my-8">
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

const BookLayout = ({ children, title, author, className = '' }) => {
  return (
    <div className={`max-w-4xl mx-auto bg-white ${className}`}>
      {/* Book cover/header */}
      {(title || author) && (
        <div className="text-center py-12 border-b border-gray-200">
          {title && (
            <h1 className="text-4xl font-medium text-gray-800 mb-4">{title}</h1>
          )}
          {author && (
            <p className="text-lg text-gray-600">{author}</p>
          )}
        </div>
      )}

      {/* Book content */}
      <div className="px-8 py-12">
        <div className="prose prose-lg max-w-none">
          {children}
        </div>
      </div>

      {/* Page divider at the bottom */}
      <PageDivider variant="ornament" />

      {/* Book footer */}
      <div className="text-center py-8 border-t border-gray-200">
        <p className="text-sm text-gray-500">
          Created with Chonost
        </p>
      </div>
    </div>
  );
};

export default BookLayout;

