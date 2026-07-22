import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'ksp' | 'scrb';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('cipa-theme');
      return (saved === 'ksp' || saved === 'scrb') ? saved : 'ksp';
    }
    return 'ksp';
  });

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('cipa-theme', newTheme);
  };

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'ksp') {
      root.classList.add('theme-ksp');
      root.classList.remove('theme-scrb');
    } else {
      root.classList.add('theme-scrb');
      root.classList.remove('theme-ksp');
    }
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
