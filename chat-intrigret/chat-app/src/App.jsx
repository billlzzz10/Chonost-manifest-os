import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { ChatInterface } from './components/ChatInterface'
import { Connections } from './components/Connections'
import { Automations } from './components/Automations'
import { Settings } from './components/Settings'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ThemeProvider } from './components/ThemeProvider'
import { NotFound } from './components/NotFound'
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
