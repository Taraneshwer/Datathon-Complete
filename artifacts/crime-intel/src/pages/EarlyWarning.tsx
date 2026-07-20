import { useListAlerts } from '@workspace/api-client-react';
import { mockAlerts } from '../mockData';
import { PageTransition, StaggerItem } from '../components/Motion';
import { SeverityBadge } from '../components/Badges';
import { CaseIdLink } from '../components/CaseIdLink';
import { Bell, CheckCircle2 } from 'lucide-react';
import { AlertSeverity } from '@workspace/api-client-react';

export function EarlyWarning() {
  const { data: alertsData } = useListAlerts();
  const alerts = Array.isArray(alertsData) ? alertsData : mockAlerts;

  return (
    <PageTransition className="space-y-6 max-w-4xl">
      <header className="mb-8">
        <h1 className="text-section-header">Early Warning System</h1>
        <p className="text-body text-[var(--ink-secondary)] mt-1">Real-time threat detection and anomaly alerts.</p>
      </header>

      <div className="flex flex-col gap-4">
        {alerts.length === 0 ? (
          <div className="card-base py-12 flex flex-col items-center justify-center text-center">
            <CheckCircle2 className="w-12 h-12 text-[var(--accent-resolved)] mb-4" />
            <h3 className="text-card-title mb-1">No Active Threats</h3>
            <p className="text-[13px] text-[var(--ink-secondary)]">All monitoring systems nominal.</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <StaggerItem key={alert.id}>
              <div className={`card-base flex gap-4 ${!alert.read ? 'bg-white' : 'bg-[var(--bg-canvas)] opacity-75'} ${
                alert.severity === AlertSeverity.critical && !alert.read ? 'border-l-[3px] border-l-[var(--accent-critical)]' : ''
              }`}>
                <div className="shrink-0 mt-1">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${!alert.read ? 'bg-[var(--data-1)] text-[var(--ink-primary)]' : 'bg-transparent text-[var(--ink-tertiary)] border border-[var(--border-hairline)]'}`}>
                    <Bell className="w-4 h-4" />
                  </div>
                </div>
                
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-1">
                    <div className="flex items-center gap-3">
                      <h3 className={`text-[16px] font-medium ${!alert.read ? 'text-[var(--ink-primary)]' : 'text-[var(--ink-secondary)]'}`}>
                        {alert.title}
                      </h3>
                      <SeverityBadge severity={alert.severity} />
                    </div>
                    <span className="tabular-data text-[12px] text-[var(--ink-tertiary)]">
                      {alert.timestamp ? new Date(alert.timestamp).toISOString().replace('T', ' ').substring(0, 16) : 'N/A'}
                    </span>
                  </div>
                  
                  <p className="text-[14px] text-[var(--ink-secondary)] leading-relaxed mb-3">
                    {alert.message}
                  </p>
                  
                  <div className="flex items-center gap-4 mt-2">
                    <span className="text-[11px] font-mono text-[var(--ink-tertiary)] uppercase tracking-wider">
                      Location: <span className="text-[var(--ink-primary)]">{alert.districtName}</span>
                    </span>
                    
                    {alert.linkedCaseIds && alert.linkedCaseIds.length > 0 && (
                      <span className="text-[11px] font-mono text-[var(--ink-tertiary)] uppercase tracking-wider flex items-center gap-1.5">
                        Linked: 
                        {alert.linkedCaseIds.map((cid: string) => <CaseIdLink key={cid} id={cid} className="text-[var(--accent-focus)] lowercase" />)}
                      </span>
                    )}
                  </div>
                </div>
                
                {!alert.read && (
                  <div className="shrink-0 flex items-center">
                    <button className="w-2.5 h-2.5 rounded-full bg-[var(--accent-focus)] hover:scale-125 transition-transform" title="Mark as read"></button>
                  </div>
                )}
              </div>
            </StaggerItem>
          ))
        )}
      </div>
    </PageTransition>
  );
}
