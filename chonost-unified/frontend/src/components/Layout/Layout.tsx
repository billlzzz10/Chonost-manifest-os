import React, { useState } from 'react';
import { RotaryTools } from '../RotaryTools/RotaryTools';
import { useAppStore } from '../../store/appStore';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { currentView, setCurrentView } = useAppStore();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const viewOptions = [
    { id: 'editor', label: 'Editor', icon: '📝' },
    { id: 'whiteboard', label: 'Whiteboard', icon: '🎨' },
  ];

  return (
    <div className="layout-container h-screen w-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="header bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">Chonost</h1>
          <span className="text-sm text-gray-500">The Ultimate Creative Workspace</span>
        </div>
        
        {/* View Switcher */}
        <div className="flex items-center space-x-2">
          <div className="view-switcher flex bg-gray-100 rounded-lg p-1">
            {viewOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => setCurrentView(option.id as 'editor' | 'whiteboard')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  currentView === option.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <span className="mr-1">{option.icon}</span>
                {option.label}
              </button>
            ))}
          </div>
          
          <div className="separator w-px h-6 bg-gray-300 mx-2"></div>
          
          <RotaryTools />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Sidebar Toggle */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className={`sidebar-toggle bg-white border-r border-gray-200 px-2 py-1 hover:bg-gray-50 transition-all ${
            sidebarCollapsed ? 'w-8' : 'w-10'
          }`}
        >
          {sidebarCollapsed ? '▶' : '◀'}
        </button>

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {children}
        </div>
      </main>

      {/* Status Bar */}
      <footer className="status-bar bg-white border-t border-gray-200 px-4 py-1 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <span className="status-indicator flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Ready
          </span>
          <span>•</span>
          <span>Auto-save enabled</span>
          <span>•</span>
          <span>View: {currentView.charAt(0).toUpperCase() + currentView.slice(1)}</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>AI: Connected</span>
          <span>•</span>
          <span>RAG: Active</span>
          <span>•</span>
          <span>Documents: 3</span>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
