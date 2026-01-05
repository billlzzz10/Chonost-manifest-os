import React, { Suspense } from 'react';
import { I18nextProvider } from 'react-i18next';
import { useTranslation } from 'react-i18next';
import i18n from './i18n';
import TopBar from "./components/TopBar";
import LeftPanel from "./components/LeftPanel";
import RightPanel from "./components/RightPanel";
import EditorWhiteboard from "./components/EditorWhiteboard";
import ReadingView from "./components/ReadingView";
import StickyNotes from "./components/StickyNotes";
import RotaryPalette from "./components/RotaryPalette";
const VisualDashboard = React.lazy(() => import('./components/VisualDashboard'));

// Language switcher component (floating button)
function LanguageSwitcher() {
  const { i18n } = useTranslation();
  
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('i18nextLng', lng);
    // Optional: Emit event to parent components for re-render
    document.documentElement.lang = lng;
    console.log(`🌐 Language changed to: ${lng} (${i18n.language})`);
  };
  
  return (
    <div className="fixed top-4 right-4 z-50 flex space-x-1 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg p-1 border border-gray-200 dark:border-gray-700">
      <button
        onClick={() => changeLanguage('th')}
        className={`px-2 py-1 text-xs rounded-md transition-all duration-200 ${
          i18n.language === 'th'
            ? 'bg-blue-500 text-white shadow-md'
            : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
        }`}
        title="ภาษาไทย"
        aria-label="เปลี่ยนเป็นภาษาไทย"
        aria-pressed={i18n.language === 'th'}
      >
        ไทย
      </button>
      <button
        onClick={() => changeLanguage('en')}
        className={`px-2 py-1 text-xs rounded-md transition-all duration-200 ${
          i18n.language === 'en'
            ? 'bg-blue-500 text-white shadow-md'
            : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
        }`}
        title="English"
        aria-label="Switch to English"
        aria-pressed={i18n.language === 'en'}
      >
        EN
      </button>
    </div>
  );
}

// Main app content with i18n
function AppContent() {
  const { t, i18n } = useTranslation();
  
  // Update document lang attribute for accessibility
  React.useEffect(() => {
    document.documentElement.lang = i18n.language;
    document.title = t('app.title') || 'Craft IDE';
  }, [i18n.language, t]);
  
  return (
    <div
      className="app min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300"
      lang={i18n.language}
      data-theme={i18n.language === 'th' ? 'thai' : 'english'}
    >
      {/* Top Bar - will use translations */}
      <TopBar />
      
      {/* Main layout */}
      <div className="layout flex flex-1 min-h-[calc(100vh-64px)]">
        <LeftPanel />
        <main className="flex-1 flex flex-col">
          <EditorWhiteboard />
        </main>
        <RightPanel />
      </div>
      
      {/* Floating UI components */}
      <div className="floating-ui">
        <RotaryPalette />
        <ReadingView content="" />
        <StickyNotes />
        <Suspense fallback={<div>Loading...</div>}>
          <VisualDashboard />
        </Suspense>
      </div>
      
      {/* Language switcher - always visible */}
      <LanguageSwitcher />
      
      {/* Global loading fallback */}
      <Suspense fallback={
        <div className="fixed inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-40">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600 dark:text-gray-300">{t('app.loading')}</p>
          </div>
        </div>
      }>
        {/* All child components now have access to i18n */}
      </Suspense>
    </div>
  );
}

// Root App component with i18n provider
export default function App() {
  return (
    <I18nextProvider i18n={i18n}>
      <AppContent />
    </I18nextProvider>
  );
}
