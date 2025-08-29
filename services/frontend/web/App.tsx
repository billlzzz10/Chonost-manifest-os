import React, { useState } from 'react';
import { Dashboard } from './Dashboard';
import { Editor } from '../../packages/ui/Editor';
import { CharacterDashboard } from '../../packages/ui/CharacterDashboard';
import { BookLayout } from '../../packages/ui/BookLayout';
import { RotaryPalette } from '../../packages/ui/RotaryPalette';
import { RotaryToolkit } from '../../packages/ui/RotaryToolkit';
import { Navigation } from './Navigation';
import './App.css';

type ViewType = 'dashboard' | 'editor' | 'characters' | 'book';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [selectedColor, setSelectedColor] = useState('#3B82F6');

  const tools = [
    { name: 'Dashboard', icon: 'book', action: () => setCurrentView('dashboard') },
    { name: 'Editor', icon: 'edit', action: () => setCurrentView('editor') },
    { name: 'Characters', icon: 'user', action: () => setCurrentView('characters') },
    { name: 'Book View', icon: 'save', action: () => setCurrentView('book') },
  ];

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'editor':
        return <Editor />;
      case 'characters':
        return <CharacterDashboard />;
      case 'book':
        return (
          <BookLayout title="Sample Story" author="Author Name">
            <div className="prose prose-lg">
              <h2>Chapter 1: The Beginning</h2>
              <p>
                In the mystical realm of Aetheria, where moonlight danced through ancient forests
                and magic flowed like rivers through the land, a young elven mage named Aria
                Moonwhisper stood at the edge of destiny.
              </p>
              <p>
                The silver pendant around her neck pulsed with ethereal light, responding to the
                growing darkness that threatened to consume everything she held dear. Tonight,
                under the full moon's watchful gaze, her journey would truly begin.
              </p>
            </div>
          </BookLayout>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      {/* Global Rotary Controls */}
      <RotaryPalette onColorSelect={setSelectedColor} />
      <RotaryToolkit tools={tools} />

      {/* Navigation */}
      <Navigation currentView={currentView} onViewChange={setCurrentView} />

      {/* Main Content */}
      <main className="main-content">
        {renderCurrentView()}
      </main>

      {/* Color Indicator */}
      <div className="fixed bottom-4 left-4 z-40">
        <div
          className="w-8 h-8 rounded-full border-2 border-white shadow-lg"
          style={{ backgroundColor: selectedColor }}
          title="Selected color"
        />
      </div>
    </div>
  );
};

