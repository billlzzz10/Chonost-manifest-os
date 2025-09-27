import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from './widgets/sidebar/Sidebar'
import { ChatInterface } from './features/chat/ChatInterface'
import { Editor } from './features/editor/Editor'
import { Whiteboard } from './features/whiteboard/Whiteboard'
import { Connections } from '../Connections.jsx'
import { Automations } from '../Automations.jsx'
import { Settings } from './features/settings/Settings'
import ErrorBoundary from '../ErrorBoundary.jsx'
import { ThemeProvider } from './shared/ThemeProvider'
import { NotFound } from './shared/NotFound'

function App() {
  const [currentView, setCurrentView] = useState('chat')
  const [selectedChatId, setSelectedChatId] = useState(null)

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
          <Sidebar 
            currentView={currentView} 
            setCurrentView={setCurrentView}
            selectedChatId={selectedChatId}
            setSelectedChatId={setSelectedChatId}
          />
          
          <main className="flex-1 flex flex-col">
            {currentView === 'chat' && (
              <ChatInterface 
                selectedChatId={selectedChatId}
                setSelectedChatId={setSelectedChatId}
              />
            )}
            {currentView === 'editor' && <Editor />}
            {currentView === 'whiteboard' && <Whiteboard />}
            {currentView === 'connections' && <Connections />}
            {currentView === 'automations' && <Automations />}
            {currentView === 'settings' && <Settings />}
          </main>
        </div>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
