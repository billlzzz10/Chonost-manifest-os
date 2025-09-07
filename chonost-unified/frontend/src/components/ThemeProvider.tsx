import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAppStore } from '@/state/store';

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const { theme, setTheme, toggleTheme } = useAppStore();
  const [mounted, setMounted] = useState(false);

  // Apply theme to document root
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Remove existing theme classes
      document.documentElement.classList.remove('light', 'dark');
      
      // Add current theme class
      document.documentElement.classList.add(theme);
      
      // Update CSS custom properties
      updateCSSVariables(theme);
      
      setMounted(true);
    }
  }, [theme]);

  // Update CSS custom properties based on theme
  const updateCSSVariables = (currentTheme: 'light' | 'dark') => {
    const root = document.documentElement;
    
    if (currentTheme === 'light') {
      // Light theme - กระดาษเก่า
      root.style.setProperty('--bg', '#F8F5E7');
      root.style.setProperty('--card', '#FFFBED');
      root.style.setProperty('--stroke', '#E6DEC2');
      root.style.setProperty('--text', '#1F2937');
      root.style.setProperty('--text-2', '#6B7280');
      root.style.setProperty('--accent', '#2563EB');
      root.style.setProperty('--accent-2', '#14B8A6');
      root.style.setProperty('--rotary-bg', '#FFFBED');
      root.style.setProperty('--rotary-hover', '#F3F4F6');
      root.style.setProperty('--panel-bg', 'rgba(255, 251, 237, 0.95)');
      root.style.setProperty('--glass-border', 'rgba(230, 222, 194, 0.3)');
    } else {
      // Dark theme - ดำ-น้ำเงินเข้ม
      root.style.setProperty('--bg', '#0B1322');
      root.style.setProperty('--card', '#1A2234');
      root.style.setProperty('--stroke', '#2D3748');
      root.style.setProperty('--text', '#F9FAFB');
      root.style.setProperty('--text-2', '#A0AEC0');
      root.style.setProperty('--accent', '#3B82F6');
      root.style.setProperty('--accent-2', '#6EE7B7');
      root.style.setProperty('--rotary-bg', '#1A2234');
      root.style.setProperty('--rotary-hover', '#2D3748');
      root.style.setProperty('--panel-bg', 'rgba(26, 34, 52, 0.95)');
      root.style.setProperty('--glass-border', 'rgba(45, 55, 72, 0.3)');
    }
  };

  // Initialize theme on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Check for saved theme preference
      const savedTheme = localStorage.getItem('chonost-app-store');
      if (savedTheme) {
        try {
          const parsed = JSON.parse(savedTheme);
          if (parsed.state?.theme && parsed.state.theme !== theme) {
            setTheme(parsed.state.theme);
          }
        } catch (e) {
          console.warn('Failed to parse saved theme');
        }
      }
      
      // Check for system preference
      if (!savedTheme) {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark && theme !== 'dark') {
          setTheme('dark');
        }
      }
    }
  }, []);

  // Listen for system theme changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleChange = (e: MediaQueryListEvent) => {
        const newTheme = e.matches ? 'dark' : 'light';
        // Only auto-switch if user hasn't manually set a preference
        const savedTheme = localStorage.getItem('chonost-app-store');
        if (!savedTheme) {
          setTheme(newTheme);
        }
      };
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, []);

  const contextValue: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return <div style={{ visibility: 'hidden' }}>{children}</div>;
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

export default ThemeProvider;
