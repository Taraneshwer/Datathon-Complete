import { useListPatterns } from '@/api-client';

import { useIntel } from '../context/IntelContext';
import { PageTransition, StaggerItem } from '../components/Motion';
import { Activity, Fingerprint } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line } from 'recharts';
import { useLocation } from 'wouter';

export function Patterns() {
  const { data: patternsData } = useListPatterns();
  const patterns = Array.isArray(patternsData) ? patternsData : [];
  const { selectedPatternId, setSelectedPatternId, highlightTrigger } = useIntel();
  const [, setLocation] = useLocation();

  const handlePatternClick = (id: string) => {
    if (selectedPatternId === id) {
      setSelectedPatternId(null);
    } else {
      setSelectedPatternId(id);
      // Optional: Navigate to graph pre-filtered
      // setLocation('/knowledge-graph'); 
    }
  };

  return (
    <PageTransition className="space-y-8">
      <header>
        <h1 className="text-section-header">Behavioral Patterns</h1>
        <p className="text-body text-[var(--ink-secondary)] mt-1">Algorithmic clustering of Modus Operandi (MO) signatures.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {patterns.map((p) => {
          const isSelected = selectedPatternId === p.id;
          const sparklineData = (p.sparkline || []).map((val: number, i: number) => ({ index: i, value: val }));

          return (
            <StaggerItem key={p.id}>
              <div
                onClick={() => handlePatternClick(p.id)}
                className={`card-base cursor-pointer group ${isSelected ? 'ring-2 ring-[var(--accent-focus)] ring-offset-2 border-[var(--accent-focus)]' : 'card-hover'} key-${highlightTrigger} animate-highlight`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="w-10 h-10 rounded-[6px] bg-[var(--data-1)] flex items-center justify-center text-[var(--accent-focus)]">
                    <Fingerprint className="w-5 h-5" />
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)]">Confidence</div>
                    <div className="tabular-data text-[18px] text-[var(--accent-focus)]">{(p.confidence * 100).toFixed(1)}%</div>
                  </div>
                </div>

                <h3 className="text-card-title text-[18px] mb-2">{p.label}</h3>
                <p className="text-[13px] text-[var(--ink-secondary)] leading-relaxed h-[60px] line-clamp-3 mb-4">
                  {p.description}
                </p>

                <div className="pt-4 border-t border-[var(--border-hairline)] flex items-end justify-between">
                  <div>
                    <div className="text-[11px] text-[var(--ink-secondary)] mb-1">Matched Cases</div>
                    <div className="tabular-data text-[16px]">{p.caseCount}</div>
                  </div>

                  <div className="w-24 h-8 opacity-70 group-hover:opacity-100 transition-opacity">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={sparklineData}>
                        <Line type="monotone" dataKey="value" stroke="var(--accent-focus)" strokeWidth={1.5} dot={false} isAnimationActive={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {isSelected && (
                  <div className="mt-4 pt-3 border-t border-[var(--border-hairline)] flex justify-between items-center text-[12px] font-medium text-[var(--accent-focus)] animate-in fade-in">
                    <span>Filter applied globally</span>
                    <button onClick={(e) => { e.stopPropagation(); setLocation('/knowledge-graph'); }} className="hover:underline">View in Graph →</button>
                  </div>
                )}
              </div>
            </StaggerItem>
          );
        })}
      </div>
    </PageTransition>
  );
}
