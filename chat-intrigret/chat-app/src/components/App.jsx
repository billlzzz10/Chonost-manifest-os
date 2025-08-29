import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Sidebar } from '../widgets/sidebar/Sidebar'
import { ChatInterface } from '../features/chat/ChatInterface'
import { Connections } from '../features/connections/Connections'
import { Automations } from '../features/automations/Automations'
import { Settings } from '../features/settings/Settings'
import { FileManagement } from '../features/files/FileManagement'
import { AgentTemplates } from '../features/agent-templates/AgentTemplates'
import AgentBuilder from '../features/agent-builder/AgentBuilder'
import { ErrorBoundary } from '../shared/ErrorBoundary'
import { ThemeProvider } from '../shared/ThemeProvider'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <Router>
          <div className="flex h-screen bg-gray-50">
            <Sidebar />
            
            <main className="flex-1 flex flex-col">
              <Routes>
                <Route path="/" element={<Navigate to="/chat" replace />} />
                <Route path="/chat" element={<ChatInterface />} />
                <Route path="/chat/:sessionId" element={<ChatInterface />} />
                <Route path="/files" element={<FileManagement />} />
                <Route path="/connections" element={<Connections />} />
                <Route path="/automations" element={<Automations />} />
                <Route path="/templates" element={<AgentTemplates />} />
                <Route path="/agents" element={<AgentBuilder />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/chat" replace />} />
              </Routes>
            </main>
          </div>
        </Router>
      </ErrorBoundary>
    </ThemeProvider>
  )
}

export default App
