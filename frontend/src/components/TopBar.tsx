import { Link, useLocation } from 'wouter';
import { useIntel } from '../context/IntelContext';
import { useHealthCheck, useGetLedgerStatus } from '@/api-client';
import { LedgerStatusState } from '@/api-client';
import { ShieldCheck, ShieldAlert, Link as LinkIcon, Activity, ChevronRight, Menu } from 'lucide-react';
import { useState, useEffect } from 'react';

export function TopBar({ onToggleSidebar }: { onToggleSidebar: () => void }) {
  const [location] = useLocation();
  const [currentTime, setCurrentTime] = useState(new Date().toISOString().replace('T', ' ').substring(0, 19));
  
  // Custom polling for health since Orval doesn't poll by default
  const { data: health, isError, isFetching, refetch } = useHealthCheck({ query: { retry: false, queryKey: ['health-check'] } });
  const { data: ledger } = useGetLedgerStatus();
  
  const ledgerData = (ledger && (ledger as any).state) ? ledger : { state: '' } as any; // Fallback when backend not ready

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toISOString().replace('T', ' ').substring(0, 19));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const healthTimer = setInterval(() => refetch(), 10000);
    return () => clearInterval(healthTimer);
  }, [refetch]);

  // Derive connection state
  let connState: 'connected' | 'connecting' | 'disconnected' = 'connected';
  if (isFetching) connState = 'connecting';
  if (isError || (health && health.status !== 'ok')) connState = 'disconnected';

  // Breadcrumb formatting
  const pathParts = location.split('/').filter(Boolean);
  const breadcrumbs = pathParts.map((p, i) => (
    <div key={p} className="flex items-center">
      {i > 0 && <ChevronRight className="w-4 h-4 mx-1 text-[var(--ink-tertiary)]" />}
      <span className={`text-[13px] capitalize ${i === pathParts.length - 1 ? 'text-[var(--ink-primary)] font-medium' : 'text-[var(--ink-secondary)]'}`}>
        {p.replace('-', ' ')}
      </span>
    </div>
  ));

  return (
    <header className="h-[56px] border-b border-[var(--border-hairline)] bg-[var(--bg-canvas)] flex items-center justify-between px-4 sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <button 
          onClick={onToggleSidebar}
          className="p-1.5 rounded-[4px] hover:bg-[var(--data-1)] text-[var(--ink-secondary)] transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center">
          {breadcrumbs.length > 0 ? breadcrumbs : <span className="text-[13px] text-[var(--ink-primary)] font-medium">Dashboard</span>}
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        {/* Backend Status */}
        <div className="group relative flex items-center gap-2 px-2.5 py-1 rounded-[4px] border border-[var(--border-hairline)] bg-[var(--bg-surface)] cursor-help">
          <div className={`w-1.5 h-1.5 rounded-full ${
            connState === 'connected' ? 'bg-[var(--accent-resolved)]' : 
            connState === 'connecting' ? 'bg-[var(--ink-tertiary)] animate-pulse' : 
            'bg-[var(--accent-critical)]'
          }`} />
          <span className="text-[11px] font-mono text-[var(--ink-secondary)] capitalize">{connState}</span>
        </div>

        {/* Ledger Status */}
        <div className="group relative flex items-center gap-2 px-2.5 py-1 rounded-[4px] border border-[var(--border-hairline)] bg-[var(--bg-surface)] text-[var(--trust-chain)] cursor-help hover:bg-[var(--data-1)] transition-colors">
          {ledgerData.state === LedgerStatusState.synced && <ShieldCheck className="w-3.5 h-3.5" />}
          {ledgerData.state === LedgerStatusState.verifying && <Activity className="w-3.5 h-3.5 animate-pulse" />}
          {ledgerData.state === LedgerStatusState.integrity_alert && <ShieldAlert className="w-3.5 h-3.5 text-[var(--accent-critical)]" />}
          <span className="text-[11px] font-mono whitespace-nowrap">
            {ledgerData.state === LedgerStatusState.synced ? `Synced · block #${ledgerData.blockHeight}` : 
             ledgerData.state === LedgerStatusState.verifying ? 'Verifying...' : 'Integrity Alert'}
          </span>
          
          {/* Popover */}
          <div className="absolute top-full right-0 mt-1 hidden group-hover:block w-64 p-3 card-base shadow-[0_8px_24px_rgba(0,0,0,0.08)] z-50">
            <div className="text-[11px] font-mono text-[var(--ink-secondary)] mb-1">Last Block Hash</div>
            <div className="text-[12px] font-mono break-all bg-[var(--data-1)] p-1.5 rounded-[4px] mb-2">{ledgerData.lastBlockHash}</div>
            <div className="text-[11px] font-mono text-[var(--ink-secondary)] mb-3">Anchored: {ledgerData.lastAnchoredAt?.replace('T', ' ').substring(0, 19) ?? 'Unknown'}</div>
            <Link href="/trust" className="text-[13px] text-[var(--accent-focus)] hover:underline decoration-[var(--border-hairline)] underline-offset-4">
              View Ledger
            </Link>
          </div>
        </div>

        {/* Timestamp */}
        <div className="text-[12px] font-mono text-[var(--ink-secondary)] px-2">
          {currentTime}
        </div>

        {/* Alert Badge */}
        <Link href="/early-warning" className="relative flex items-center justify-center w-8 h-8 rounded-[4px] hover:bg-[var(--data-1)] text-[var(--ink-secondary)] transition-colors">
          <Activity className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[var(--accent-critical)] rounded-full ring-2 ring-[var(--bg-canvas)]"></span>
        </Link>
      </div>
    </header>
  );
}
