import React from 'react';
import { Button } from '../../packages/ui/Button';
import { Typography } from '../../packages/ui/Typography';
import { Icon } from '../../packages/ui/Icon';

type ViewType = 'dashboard' | 'editor' | 'characters' | 'book';

interface NavigationProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ currentView, onViewChange }) => {
  const navItems = [
    { id: 'dashboard' as ViewType, label: 'Dashboard', icon: 'book' },
    { id: 'editor' as ViewType, label: 'Editor', icon: 'edit' },
    { id: 'characters' as ViewType, label: 'Characters', icon: 'user' },
    { id: 'book' as ViewType, label: 'Book View', icon: 'save' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-3">
          <Icon name="book" size="lg" color="#3B82F6" />
          <Typography variant="h3" className="mb-0 text-blue-600">
            Chonost
          </Typography>
        </div>

        {/* Navigation Items */}
        <div className="flex space-x-2">
          {navItems.map((item) => (
            <Button
              key={item.id}
              variant={currentView === item.id ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => onViewChange(item.id)}
              className="flex items-center space-x-2"
            >
              <Icon name={item.icon} size="sm" />
              <span>{item.label}</span>
            </Button>
          ))}
        </div>

        {/* User Menu */}
        <div className="flex items-center space-x-3">
          <Typography variant="caption" className="text-gray-600 mb-0">
            Welcome, Writer
          </Typography>
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <Icon name="user" size="sm" color="#3B82F6" />
          </div>
        </div>
      </div>
    </nav>
  );
};

