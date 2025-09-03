import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from './widgets/sidebar/Sidebar'
import { ChatInterface } from './features/chat/ChatInterface'
import { Connections } from './features/connections/Connections'
import { Automations } from './features/automations/Automations'
import { Settings } from './features/settings/Settings'
import { ErrorBoundary } from './shared/ErrorBoundary'
import { ThemeProvider } from './shared/ThemeProvider'
import { NotFound } from './shared/NotFound'
import './App.css'

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
