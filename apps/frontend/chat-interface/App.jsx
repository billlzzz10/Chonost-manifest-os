import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from './src/widgets/sidebar/Sidebar'
import { ChatInterface } from './src/features/chat/ChatInterface'
import { Connections } from './src/features/connections/Connections'
import { Automations } from './src/features/automations/Automations'
import { Settings } from './src/features/settings/Settings'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('chat')
  const [selectedChatId, setSelectedChatId] = useState(null)

  return (
    <div className="flex h-screen bg-gray-50">
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
  )
}

export default App
