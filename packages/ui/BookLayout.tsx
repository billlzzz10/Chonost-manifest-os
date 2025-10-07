import React from 'react';
import { PageDivider } from './PageDivider';
import { Typography } from './Typography';

interface BookLayoutProps {
  children: React.ReactNode;
  title?: string;
  author?: string;
  className?: string;
}

export const BookLayout: React.FC<BookLayoutProps> = ({
  children,
  title,
  author,
  className = '',
}) => {
  return (
    <div className={`max-w-4xl mx-auto bg-white ${className}`}>
      {/* Book cover/header */}
      {(title || author) && (
        <div className="text-center py-12 border-b border-gray-200">
          {title && (
            <Typography variant="h1" className="mb-4">
              {title}
            </Typography>
          )}
          {author && (
            <Typography variant="body" className="text-gray-600">
              {author}
            </Typography>
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
        <Typography variant="caption" className="text-gray-500">
          Created with Chonost
        </Typography>
      </div>
    </div>
  );
};

