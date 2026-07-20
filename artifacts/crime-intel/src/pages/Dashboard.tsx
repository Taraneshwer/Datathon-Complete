import { useGetDashboardAnalytics, useGetCrimeTrend, useListCases } from '@workspace/api-client-react';
import { mockDashboardAnalytics, mockCases } from '../mockData';
import { PageTransition, StaggerItem } from '../components/Motion';
import { CaseIdLink } from '../components/CaseIdLink';
import { StatusPill } from '../components/Badges';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Minus, AlertTriangle } from 'lucide-react';
import { useIntel } from '../context/IntelContext';

export function Dashboard() {
  const { data: analyticsData } = useGetDashboardAnalytics();
  const { data: casesData } = useListCases({ limit: 10 });
  
  // Use Intel context for cross-filtering highlights
  const { highlightTrigger } = useIntel();

  const analytics = analyticsData || mockDashboardAnalytics;
  const cases = Array.isArray(casesData) ? casesData : mockCases;

  // Mock trend data
  const trendData = [
    { month: 'Jan', count: 120, avg: 135 },
    { month: 'Feb', count: 115, avg: 130 },
    { month: 'Mar', count: 140, avg: 135 },
    { month: 'Apr', count: 155, avg: 140 },
    { month: 'May', count: 180, avg: 145 },
    { month: 'Jun', count: 175, avg: 145 }
  ];

  return (
    <PageTransition className="space-y-8 pb-12">
      <header className="mb-2">
        <h1 className="text-section-header">Analytics Dashboard</h1>
        <p className="text-body text-[var(--ink-secondary)] mt-1">Statewide intelligence summary & active operations.</p>
      </header>

      {/* Risk Forecast Strip */}
      <StaggerItem>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {(analytics.riskForecast || []).map((forecast: any) => (
            <div key={forecast.districtId} className={`card-base py-3 px-4 flex items-center justify-between key-${highlightTrigger} animate-highlight`}>
              <div>
                <div className="text-caption text-[var(--ink-secondary)]">{forecast.districtName}</div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="font-mono text-[14px]">Level {forecast.riskLevel}</span>
                  <div className={`w-2 h-2 rounded-full ${forecast.riskLevel >= 4 ? 'bg-[var(--accent-critical)]' : forecast.riskLevel === 3 ? 'bg-[var(--accent-warning)]' : 'bg-[var(--accent-resolved)]'}`} />
                </div>
              </div>
              <div className="text-[var(--ink-tertiary)]">
                {forecast.trend === 'up' && <ArrowUpRight className="w-4 h-4 text-[var(--accent-critical)]" />}
                {forecast.trend === 'down' && <ArrowDownRight className="w-4 h-4 text-[var(--accent-resolved)]" />}
                {forecast.trend === 'flat' && <Minus className="w-4 h-4" />}
              </div>
            </div>
          ))}
        </div>
      </StaggerItem>

      {/* Anomaly Stats */}
      <StaggerItem>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {(analytics.anomalyStats || []).map((stat: any, idx: number) => (
            <div key={idx} className={`card-base flex flex-col relative ${stat.isAnomaly ? 'border-l-[3px] border-l-[var(--accent-critical)]' : ''}`}>
              <div className="text-caption text-[var(--ink-secondary)] uppercase tracking-wider">{stat.label}</div>
              <div className="mt-2 flex items-baseline gap-3">
                <span className="font-mono text-[32px] leading-none tracking-tight">{stat.value}</span>
                <span className={`font-mono text-[13px] ${stat.delta > 0 ? (stat.isAnomaly ? 'text-[var(--accent-critical)]' : 'text-[var(--ink-secondary)]') : 'text-[var(--accent-resolved)]'}`}>
                  {stat.delta > 0 ? '+' : ''}{stat.delta} {stat.unit || ''}
                </span>
              </div>
              {stat.isAnomaly && (
                <div className="absolute top-4 right-4 text-[var(--accent-critical)]">
                  <AlertTriangle className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}
        </div>
      </StaggerItem>

      {/* Trend Chart */}
      <StaggerItem>
        <div className="card-base">
          <div className="mb-6 flex justify-between items-center">
            <h2 className="text-card-title">Crime Volume Trend</h2>
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-0.5 bg-[var(--accent-focus)]"></div>
                <span className="text-caption text-[var(--ink-secondary)]">Actual</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-0.5 border-t border-dashed border-[var(--ink-tertiary)]"></div>
                <span className="text-caption text-[var(--ink-secondary)]">Historical Avg</span>
              </div>
            </div>
          </div>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-hairline)" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--ink-secondary)', fontFamily: 'Inter' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--ink-secondary)', fontFamily: 'IBM Plex Mono' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-hairline)', borderRadius: '6px', fontFamily: 'Inter', fontSize: '13px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}
                  itemStyle={{ fontFamily: 'IBM Plex Mono' }}
                />
                <ReferenceLine y={135} stroke="var(--ink-tertiary)" strokeDasharray="3 3" />
                <Line type="monotone" dataKey="count" stroke="var(--accent-focus)" strokeWidth={2} dot={{ r: 4, fill: 'var(--bg-surface)', strokeWidth: 2 }} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="avg" stroke="var(--ink-tertiary)" strokeWidth={1} strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </StaggerItem>

      {/* Active Cases Table */}
      <StaggerItem>
        <div className="card-base p-0 overflow-hidden">
          <div className="p-5 border-b border-[var(--border-hairline)] flex justify-between items-center bg-[var(--bg-canvas)]">
            <h2 className="text-card-title">Priority Cases</h2>
            <button className="text-[13px] text-[var(--accent-focus)] hover:underline decoration-[var(--border-hairline)] underline-offset-4">View All</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[var(--border-hairline)] bg-[var(--bg-canvas)]">
                  <th className="px-5 py-3 text-caption uppercase text-[var(--ink-tertiary)] font-medium">Case ID</th>
                  <th className="px-5 py-3 text-caption uppercase text-[var(--ink-tertiary)] font-medium">Title</th>
                  <th className="px-5 py-3 text-caption uppercase text-[var(--ink-tertiary)] font-medium">District</th>
                  <th className="px-5 py-3 text-caption uppercase text-[var(--ink-tertiary)] font-medium">Status</th>
                  <th className="px-5 py-3 text-caption uppercase text-[var(--ink-tertiary)] font-medium">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr key={c.id} className={`border-b border-[var(--border-hairline)] last:border-0 hover:bg-[var(--data-1)] transition-colors key-${highlightTrigger} animate-highlight`}>
                    <td className="px-5 py-4 whitespace-nowrap">
                      <CaseIdLink id={c.id} />
                    </td>
                    <td className="px-5 py-4 text-body font-medium">{c.title}</td>
                    <td className="px-5 py-4 text-[13px] text-[var(--ink-secondary)]">{c.districtName}</td>
                    <td className="px-5 py-4 whitespace-nowrap">
                      <StatusPill status={c.status} />
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap">
                      {c.confidence ? (
                        <div className="flex items-center gap-2">
                          <span className="tabular-data text-[13px] w-8">{(c.confidence * 100).toFixed(0)}%</span>
                          <div className="w-16 h-1.5 bg-[var(--data-1)] rounded-full overflow-hidden">
                            <div className="h-full bg-[var(--accent-focus)]" style={{ width: `${c.confidence * 100}%` }}></div>
                          </div>
                        </div>
                      ) : <span className="text-[var(--ink-tertiary)]">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </StaggerItem>
    </PageTransition>
  );
}
