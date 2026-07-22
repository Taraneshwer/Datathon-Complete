import { Suspense, lazy, useState, useEffect } from 'react';
import { PageTransition } from '../components/Motion';
import { useIntel } from '../context/IntelContext';
import { useListGraphNodes, useListGraphEdges } from '@workspace/api-client-react';

import { GraphNodeType } from '@workspace/api-client-react';
import { Skeleton } from '../components/Skeleton';
import { CaseIdLink } from '../components/CaseIdLink';

// Lazy load force graph to avoid SSR issues and heavy bundle upfront
const ForceGraph2D = lazy(() => import('react-force-graph-2d'));

export function KnowledgeGraph() {
  const { selectedDistrictId, selectedPatternId } = useIntel();
  const [timeIndex, setTimeIndex] = useState(1);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  const { data: nodesData } = useListGraphNodes({ districtId: selectedDistrictId || undefined, patternId: selectedPatternId || undefined });
  const { data: edgesData } = useListGraphEdges({ districtId: selectedDistrictId || undefined, patternId: selectedPatternId || undefined });

  const allNodes = Array.isArray(nodesData) ? nodesData : [];
  const allEdges = Array.isArray(edgesData) ? edgesData : [];

  // Filter based on time scrubber
  const visibleNodes = allNodes.filter(n => n.timeIndex <= timeIndex);
  const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
  const visibleEdges = allEdges.filter(e => e.timeIndex <= timeIndex && visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target));

  const graphData = {
    nodes: visibleNodes.map(n => ({ ...n })),
    links: visibleEdges.map(e => ({ ...e }))
  };

  // Resolved hex values for canvas context — CSS variables don't work in canvas fillStyle/strokeStyle
  const TOKEN = {
    accentFocus:    '#1F3A5C',
    borderHairline: '#EBEAE6',
    bgSurface:      '#FFFFFF',
    inkPrimary:     '#16181A',
    inkSecondary:   '#71767D',
    inkTertiary:    '#A8ACB1',
    victimGray:     '#6B7280',
    locationGold:   '#A67C3D',
    selectedHalo:   'rgba(31, 58, 92, 0.12)',
  } as const;

  // Node styling logic
  const getNodeColor = (node: any): string => {
    switch (node.type) {
      case GraphNodeType.suspect:  return TOKEN.accentFocus;
      case GraphNodeType.victim:   return TOKEN.victimGray;
      case GraphNodeType.location: return TOKEN.locationGold;
      case GraphNodeType.case:     return TOKEN.bgSurface;
      default:                     return TOKEN.inkTertiary;
    }
  };

  const drawNode = (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.label || node.id;
    const size = 6;
    
    ctx.beginPath();
    
    if (node.type === GraphNodeType.location) {
      ctx.rect(node.x - size, node.y - size, size * 2, size * 2);
    } else if (node.type === GraphNodeType.case) {
      for (let i = 0; i < 6; i++) {
        const angle = 2 * Math.PI / 6 * i;
        const x = node.x + size * 1.2 * Math.cos(angle);
        const y = node.y + size * 1.2 * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
    } else {
      ctx.arc(node.x, node.y, size, 0, 2 * Math.PI, false);
    }

    ctx.fillStyle = getNodeColor(node);
    ctx.fill();
    
    if (node.type === GraphNodeType.case) {
      ctx.lineWidth = 1.5 / globalScale;
      ctx.strokeStyle = TOKEN.inkPrimary;
      ctx.stroke();
    }
    
    if (node.id === selectedNode?.id) {
      ctx.lineWidth = 2 / globalScale;
      ctx.strokeStyle = TOKEN.accentFocus;
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI, false);
      ctx.fillStyle = TOKEN.selectedHalo;
      ctx.fill();
    }

    if (globalScale > 1.5) {
      ctx.font = `${3}px "IBM Plex Mono"`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillStyle = TOKEN.inkSecondary;
      ctx.fillText(label, node.x, node.y + size + 2);
    }
  };

  return (
    <PageTransition className="space-y-6 h-[calc(100vh-120px)] flex flex-col pb-4">
      <header className="shrink-0">
        <h1 className="text-section-header">Knowledge Graph</h1>
        <p className="text-body text-[var(--ink-secondary)] mt-1">Entity relationships and crime replay timeline.</p>
      </header>

      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Graph Area */}
        <div className="flex-1 card-base p-0 flex flex-col overflow-hidden relative">
          <div className="flex-1 relative bg-[var(--bg-canvas)] cursor-crosshair">
            <Suspense fallback={<Skeleton className="w-full h-full" />}>
              <ForceGraph2D
                graphData={graphData}
                nodeCanvasObject={drawNode}
                nodeLabel="label"
                onNodeClick={(node) => setSelectedNode(node)}
                linkColor={() => '#EBEAE6'}
                linkWidth={(link: any) => link.strength ? link.strength * 2 : 1}
                backgroundColor="#FAFAF9"
                d3VelocityDecay={0.3}
                width={800} // In a real app this would auto-resize, but we rely on container
              />
            </Suspense>
            
            {/* Legend Overlay */}
            <div className="absolute top-4 left-4 card-base p-3 py-2 bg-[var(--bg-surface)]/90 backdrop-blur-sm shadow-sm pointer-events-none">
              <div className="flex gap-4">
                <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[var(--accent-focus)]"></div><span className="text-[11px] font-mono text-[var(--ink-secondary)]">Suspect</span></div>
                <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#6B7280]"></div><span className="text-[11px] font-mono text-[var(--ink-secondary)]">Victim</span></div>
                <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 bg-[#A67C3D]"></div><span className="text-[11px] font-mono text-[var(--ink-secondary)]">Location</span></div>
                <div className="flex items-center gap-1.5"><div className="w-3 h-3 border border-[var(--ink-primary)] rotate-45 transform bg-white"></div><span className="text-[11px] font-mono text-[var(--ink-secondary)]">Case</span></div>
              </div>
            </div>
          </div>

          {/* Crime Replay Scrubber */}
          <div className="h-16 border-t border-[var(--border-hairline)] bg-[var(--bg-surface)] px-6 flex items-center gap-4">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] shrink-0">Time Index</span>
            <input 
              type="range" 
              min="0" 
              max="2" 
              value={timeIndex}
              onChange={(e) => setTimeIndex(parseInt(e.target.value))}
              className="flex-1 accent-[var(--accent-focus)]"
            />
            <span className="tabular-data text-[13px] w-8 text-right">T+{timeIndex}</span>
          </div>
        </div>

        {/* Side Panel (Slide-in) */}
        <div className={`w-80 shrink-0 card-base overflow-y-auto transition-transform duration-300 ease-out transform ${selectedNode ? 'translate-x-0' : 'translate-x-full opacity-0 absolute right-0'}`}>
          {selectedNode && (
            <>
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-1">
                    {selectedNode.type} Node
                  </div>
                  <h3 className="text-[18px] font-display font-medium text-[var(--ink-primary)]">
                    {selectedNode.label}
                  </h3>
                  <div className="text-[12px] font-mono text-[var(--ink-secondary)] mt-1 break-all">ID: {selectedNode.id}</div>
                </div>
                <button 
                  onClick={() => setSelectedNode(null)}
                  className="text-[var(--ink-tertiary)] hover:text-[var(--ink-primary)] transition-colors"
                >
                  ✕
                </button>
              </div>

              {selectedNode.riskScore && (
                <div className="mb-6">
                  <div className="text-[11px] text-[var(--ink-secondary)] mb-1">Risk Score</div>
                  <div className="flex items-center gap-2">
                    <span className="tabular-data text-[24px] leading-none">{selectedNode.riskScore}</span>
                    <div className="flex-1 h-1.5 bg-[var(--data-1)] rounded-full overflow-hidden">
                      <div className="h-full bg-[var(--accent-critical)]" style={{ width: `${selectedNode.riskScore}%` }}></div>
                    </div>
                  </div>
                </div>
              )}

              {selectedNode.moSummary && (
                <div className="mb-6">
                  <div className="text-[11px] text-[var(--ink-secondary)] mb-1">MO Summary</div>
                  <p className="text-[13px] leading-relaxed p-3 bg-[var(--data-1)] rounded-[4px] border border-[var(--border-hairline)]">
                    {selectedNode.moSummary}
                  </p>
                </div>
              )}

              {selectedNode.linkedCaseIds && selectedNode.linkedCaseIds.length > 0 && (
                <div>
                  <div className="text-[11px] text-[var(--ink-secondary)] mb-2">Linked Cases</div>
                  <ul className="space-y-2">
                    {selectedNode.linkedCaseIds.map((cid: string) => (
                      <li key={cid} className="flex items-center">
                        <div className="w-1.5 h-1.5 rounded-full bg-[var(--ink-tertiary)] mr-2"></div>
                        <CaseIdLink id={cid} />
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
