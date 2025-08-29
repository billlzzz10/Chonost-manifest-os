import { useState } from 'react'
import Navigation from './components/Navigation'
import Dashboard from './components/Dashboard'
import Editor from './components/Editor'
import CharacterProfile from './components/CharacterProfile'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'editor':
        return <Editor />
      case 'characters':
        return <CharacterProfile />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      {renderCurrentPage()}
    </div>
  )
}

export default App
