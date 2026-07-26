import { ReactNode, useState } from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { useTheme } from '../context/ThemeContext';
import { FloatingAI } from './ksp/FloatingAI';

export function Shell({ children }: { children: ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { theme } = useTheme();

  return (
    <div className="h-screen w-full flex bg-[var(--bg-canvas)] overflow-hidden">
      {/* Left Rail */}
      <div 
        className="shrink-0 transition-all duration-200 ease-in-out"
        style={{ width: sidebarCollapsed ? '64px' : '240px' }}
      >
        <Sidebar collapsed={sidebarCollapsed} />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        <TopBar onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)} />
        <main className="flex-1 overflow-y-auto p-8 relative">
          <div className="max-w-[1400px] mx-auto">
            {children}
          </div>
        </main>
        {theme === 'ksp' && <FloatingAI />}
      </div>
    </div>
  );
}

