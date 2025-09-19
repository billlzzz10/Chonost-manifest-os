import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import enTranslation from './locales/en.json';
import thTranslation from './locales/th.json';

// i18n resources configuration
const resources = {
  en: {
    translation: enTranslation
  },
  th: {
    translation: thTranslation
  }
};

// Initialize i18next
i18n
  .use(initReactI18next) // Bind React
  .use(LanguageDetector) // Auto-detect language
  .init({
    resources,
    lng: localStorage.getItem('i18nextLng') || 'th', // Default: Thai (Thailand market)
    fallbackLng: 'en', // Fallback to English
    debug: import.meta.env.DEV, // Debug mode in development
    
    // Allow interpolation and formatting
    interpolation: {
      escapeValue: false, // React already escapes values
      formatSeparator: ','
    },
    
    // Language detection configuration
    detection: {
      order: [
        'localStorage',  // Check localStorage first
        'navigator',     // Browser language
        'htmlTag'        // HTML lang attribute
      ],
      caches: ['localStorage'], // Cache language in localStorage
      exclude: [], // No exclusions
      lookupLocalStorage: 'i18nextLng',
      lookupSessionStorage: 'i18nextLng',
      lookupFromNavigator: 'language',
      lookupFromHtmlTag: 'lang',
      // Auto-detect Thai if not explicitly set
      checkWhitelistOnly: false
    },
    
    // React-specific options
    react: {
      useSuspense: false, // Disable Suspense for smoother UX
      bindI18n: 'languageChanged loaded',
      bindStore: false
    },
    
    // Thai/English specific settings
    saveMissing: import.meta.env.DEV, // Log missing keys in development
    missingKeyHandler: (lng, ns, key) => {
      if (import.meta.env.DEV) {
        console.warn(`Missing translation: ${key} in ${lng}`);
      }
    }
  })
  .then(() => {
    console.log('🌐 i18next initialized successfully');
    console.log(`Current language: ${i18n.language}`);
  })
  .catch((error) => {
    console.error('❌ i18next initialization failed:', error);
  });

export default i18n;