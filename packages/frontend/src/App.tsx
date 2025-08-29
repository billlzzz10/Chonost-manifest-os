import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Layout from './components/Layout/Layout';
import Editor from './components/Editor/Editor';
import Whiteboard from './components/Whiteboard/Whiteboard';
import KnowledgeExplorer from './components/KnowledgeExplorer/KnowledgeExplorer';
import AssistantPanel from './components/AssistantPanel/AssistantPanel';

// Store
import { useAppStore } from './store/appStore';

// Styles
import './styles/globals.css';

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const { currentView } = useAppStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Layout>
            <Routes>
              <Route path="/" element={
                <div className="flex h-full">
                  {/* Left Sidebar - Knowledge Explorer */}
                  <KnowledgeExplorer />
                  
                  {/* Main Content Area */}
                  <main className="flex-1 flex flex-col">
                    {currentView === 'editor' && <Editor />}
                    {currentView === 'whiteboard' && <Whiteboard />}
                  </main>
                  
                  {/* Right Sidebar - Assistant Panel */}
                  <AssistantPanel />
                </div>
              } />
            </Routes>
          </Layout>
          
          {/* Toast notifications */}
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
