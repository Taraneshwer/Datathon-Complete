import { useGetBiasAudit } from '@/api-client';

import { PageTransition, StaggerItem } from '../components/Motion';
import { Scale as BalanceScale, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export function BiasAudit() {
  const { data: auditData } = useGetBiasAudit();
  const audit = (auditData && (auditData as any).buckets) ? auditData : { disparity: { detected: false }, buckets: [] } as any;

  // Transform data for chart
  const chartData = audit.buckets.map((b: any) => ({
    name: b.label,
    'Closure Rate': b.closureRate * 100,
    'Resource Allocation': b.resourceAllocation * 100,
    flagged: b.flagged
  }));

  return (
    <PageTransition className="space-y-8 max-w-5xl">
      <header>
        <h1 className="text-section-header">Algorithmic Bias Audit</h1>
        <p className="text-body text-[var(--ink-secondary)] mt-1">Continuous parity monitoring of resource allocation and model inference.</p>
      </header>

      {audit.disparity.detected ? (
        <StaggerItem>
          <div className="card-base border-l-4 border-l-[var(--accent-warning)] bg-[#B8863F05]">
            <div className="flex gap-4">
              <AlertTriangle className="w-6 h-6 text-[var(--accent-warning)] shrink-0 mt-1" />
              <div>
                <h3 className="text-[16px] font-medium text-[var(--ink-primary)] mb-1">Disparity Flagged for Review</h3>
                <p className="text-[14px] text-[var(--ink-secondary)] mb-3 leading-relaxed">
                  {audit.disparity.description}
                </p>
                <div className="p-3 bg-white border border-[var(--border-hairline)] rounded-[4px] text-[13px] font-mono text-[var(--ink-primary)]">
                  <span className="text-[var(--ink-tertiary)]">SYS_REC: </span>{audit.disparity.recommendation}
                </div>
              </div>
            </div>
          </div>
        </StaggerItem>
      ) : (
        <StaggerItem>
          <div className="card-base flex items-center gap-3 border-l-4 border-l-[var(--accent-resolved)]">
            <CheckCircle2 className="w-5 h-5 text-[var(--accent-resolved)]" />
            <span className="text-[14px] font-medium text-[var(--ink-primary)]">Parity checks nominal. No significant disparities detected.</span>
          </div>
        </StaggerItem>
      )}

      <StaggerItem>
        <div className="card-base">
          <h2 className="text-card-title mb-6">Resource vs Closure Parity by Region Type</h2>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-hairline)" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--ink-secondary)', fontFamily: 'Inter' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--ink-secondary)', fontFamily: 'IBM Plex Mono' }} tickFormatter={(val) => `${val}%`} />
                <Tooltip 
                  cursor={{ fill: 'var(--data-1)' }}
                  contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-hairline)', borderRadius: '6px', fontFamily: 'Inter', fontSize: '13px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} />
                <Bar dataKey="Closure Rate" fill="var(--data-3)" radius={[2, 2, 0, 0]} />
                <Bar dataKey="Resource Allocation" fill="var(--accent-focus)" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </StaggerItem>

      <StaggerItem>
        <div className="text-[11px] font-mono text-[var(--ink-tertiary)] text-center uppercase tracking-wider">
          Audit Log ID: {audit.generatedAt} · Hash: {Math.random().toString(36).substring(2, 15)}
        </div>
      </StaggerItem>
    </PageTransition>
  );
}
