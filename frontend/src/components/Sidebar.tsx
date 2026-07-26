import { Link, useLocation } from 'wouter';
import { 
  LayoutDashboard, Map as MapIcon, Fingerprint, Activity, 
  Network, FileText, Bot, Shield, Scale as BalanceScale,
  Brain, Layers, History, Settings as SettingsIcon, FolderClosed,
  UserCheck, Database
} from 'lucide-react';
import { useIntel } from '../context/IntelContext';
import { useTheme } from '../context/ThemeContext';
import { KspLogo } from './ksp/KspLogo';

interface SidebarProps {
  collapsed: boolean;
}

export function Sidebar({ collapsed }: SidebarProps) {
  const [location] = useLocation();
  const { selectedCaseId } = useIntel();
  const { theme } = useTheme();

  const NavItem = ({ href, icon: Icon, label, disabled = false }: any) => {
    const isActive = location === href || location.startsWith(href + '/');
    const classes = `flex items-center h-10 px-3 mx-2 my-1 rounded-[6px] transition-all duration-150 ${
      isActive 
        ? 'bg-[#1F3A5C0F] text-[var(--accent-focus)] border-l-2 border-[var(--accent-focus)] font-medium' 
        : 'text-[var(--ink-secondary)] hover:bg-[var(--data-1)] hover:text-[var(--ink-primary)] border-l-2 border-transparent'
    } ${disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}`;

    return (
      <Link href={disabled ? '#' : href} className={classes} title={collapsed ? label : undefined}>
        <Icon className={`w-4 h-4 shrink-0 ${collapsed ? 'mx-auto' : 'mr-3'} ${isActive ? 'stroke-2' : 'stroke-[1.5]'}`} />
        <span className={`text-[13px] whitespace-nowrap overflow-hidden transition-opacity duration-200 ${collapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>
          {label}
        </span>
      </Link>
    );
  };

  const Section = ({ title, children }: any) => (
    <div className="mb-6">
      <div className={`px-5 mb-2 text-[10px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] overflow-hidden whitespace-nowrap transition-opacity duration-200 ${collapsed ? 'opacity-0' : 'opacity-100'}`}>
        {title}
      </div>
      <div>{children}</div>
    </div>
  );

  return (
    <div className="flex flex-col h-full bg-[var(--bg-canvas)] border-r border-[var(--border-hairline)] overflow-y-auto hide-scrollbar z-50">
      {/* Brand */}
      <div className="h-[64px] flex items-center px-4 shrink-0 border-b border-[var(--border-hairline)] mb-6 sticky top-0 bg-[var(--bg-canvas)]">
        {theme === 'ksp' ? (
          <div className="flex items-center">
            <KspLogo size={32} />
            <div className={`ml-3 overflow-hidden whitespace-nowrap transition-opacity duration-200 ${collapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>
              <div className="font-mono font-bold text-[14px] leading-tight text-[var(--ink-primary)] tracking-tight">KSP COPS</div>
              <div className="text-[11px] text-[var(--ink-tertiary)]">Karnataka State Police</div>
            </div>
          </div>
        ) : (
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-[6px] bg-[var(--accent-focus)] text-white flex items-center justify-center font-mono font-bold shrink-0`}>
              C
            </div>
            <div className={`ml-3 overflow-hidden whitespace-nowrap transition-opacity duration-200 ${collapsed ? 'opacity-0 w-0' : 'opacity-100'}`}>
              <div className="font-mono font-bold text-[14px] leading-tight text-[var(--ink-primary)] tracking-tight">CIPA</div>
              <div className="text-[11px] text-[var(--ink-tertiary)]">Karnataka SCRB</div>
            </div>
          </div>
        )}
      </div>

      <Section title="Intelligence">
        <NavItem href="/dashboard" icon={LayoutDashboard} label="Analytics Dashboard" />
        <NavItem href="/hotspots" icon={MapIcon} label="Tactical Map (KSP)" />
        <NavItem href="/prevention" icon={Layers} label="Crime Prevention" />
        <NavItem href="/patterns" icon={Fingerprint} label="Pattern Matching" />
        <NavItem href="/early-warning" icon={Activity} label="Early Warning Feed" />
      </Section>

      <Section title="Investigation">
        <NavItem href="/knowledge-graph" icon={Network} label="Knowledge Graph (Force)" />
        <NavItem href="/knowledge-graph-ksp" icon={Network} label="Schema Graph (ReactFlow)" />
        <NavItem href="/evidence" icon={FolderClosed} label="Evidence Hub" />
        <NavItem href={`/cases/${selectedCaseId || 'KA-2024-00847'}`} icon={FileText} label="Case Detail & Timeline" />
        <NavItem href="/replay" icon={History} label="Crime Scene Replay" />
        <NavItem href="/agent" icon={Bot} label="AI Investigative Agent" />
      </Section>

      <Section title="Trust & Oversight">
        <NavItem href="/trust" icon={Shield} label="Identity & Access Logs" />
        <NavItem href="/identity" icon={UserCheck} label="Biometric Profiling" />
        <NavItem href="/blockchain" icon={Database} label="Blockchain Audit Ledger" />
        <NavItem href="/bias-audit" icon={BalanceScale} label="Bias Audit" />
      </Section>

      <Section title="System">
        <NavItem href="/settings" icon={SettingsIcon} label="System Settings" />
      </Section>
    </div>
  );
}
