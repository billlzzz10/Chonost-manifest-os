import React from 'react';
import { RotaryTools } from '../RotaryTools/RotaryTools';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="layout-container h-screen w-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="header bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">Chonost</h1>
          <span className="text-sm text-gray-500">The Ultimate Creative Workspace</span>
        </div>
        
        <div className="flex items-center space-x-2">
          <RotaryTools />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {children}
      </main>

      {/* Status Bar */}
      <footer className="status-bar bg-white border-t border-gray-200 px-4 py-1 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <span>Ready</span>
          <span>•</span>
          <span>Auto-save enabled</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>View: Editor</span>
          <span>•</span>
          <span>AI: Connected</span>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
