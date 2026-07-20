import { useRoute } from 'wouter';
import { useGetCase, useGetCaseEvidence, useGetCaseTimeline } from '@workspace/api-client-react';
import { mockCases, mockEvidence, mockTimeline } from '../mockData';
import { PageTransition, StaggerItem } from '../components/Motion';
import { StatusPill } from '../components/Badges';
import { Skeleton } from '../components/Skeleton';
import { FileText, Camera, ShieldCheck, MapPin, Fingerprint, Calendar, ShieldAlert } from 'lucide-react';
import { EvidenceItemType, TimelineEventType } from '@workspace/api-client-react';

export function CaseEvidence() {
  const [match, params] = useRoute('/cases/:id');
  const id = params?.id || 'KA-2024-00847';

  // These would fetch based on id, but fallback to mock data since backend might just echo it
  const { data: caseData, isLoading: caseLoading } = useGetCase(id);
  const { data: evidenceData, isLoading: evidenceLoading } = useGetCaseEvidence(id);
  const { data: timelineData, isLoading: timelineLoading } = useGetCaseTimeline(id);

  // Fallbacks
  const caseDetail = caseData || mockCases.find(c => c.id === id) || mockCases[0];
  const evidence = Array.isArray(evidenceData) ? evidenceData : mockEvidence.filter(e => e.caseId === id);
  const timeline = Array.isArray(timelineData) ? timelineData : mockTimeline.filter(t => t.caseId === id).sort((a,b) => (a.timestamp ? new Date(a.timestamp).getTime() : 0) - (b.timestamp ? new Date(b.timestamp).getTime() : 0));

  if (caseLoading) return (
    <div className="space-y-8 animate-pulse">
      <Skeleton className="h-24 w-full max-w-3xl" />
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4"><Skeleton className="h-64 w-full" /></div>
        <Skeleton className="h-96 w-full" />
      </div>
    </div>
  );

  const getEvidenceIcon = (type: EvidenceItemType) => {
    switch(type) {
      case EvidenceItemType.video:
      case EvidenceItemType.image: return Camera;
      case EvidenceItemType.forensic: return Fingerprint;
      default: return FileText;
    }
  };

  const getEventIcon = (type: TimelineEventType) => {
    switch(type) {
      case TimelineEventType.incident: return ShieldAlert;
      case TimelineEventType.evidence_collected: return Camera;
      default: return FileText;
    }
  };

  return (
    <PageTransition className="space-y-6">
      {/* Header Block */}
      <div className="pb-6 border-b border-[var(--border-hairline)] mb-8">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <h1 className="tabular-data text-[32px] tracking-tight">{caseDetail.id}</h1>
            <StatusPill status={caseDetail.status} />
          </div>
          <div className="text-right">
            <div className="text-[11px] font-mono text-[var(--ink-tertiary)] uppercase mb-1">Lead Officer</div>
            <div className="text-[14px] font-medium">{caseDetail.officerInCharge}</div>
          </div>
        </div>
        
        <h2 className="text-[24px] font-display mb-4">{caseDetail.title}</h2>
        
        <div className="flex flex-wrap gap-x-8 gap-y-4 text-[13px]">
          <div className="flex items-center gap-2 text-[var(--ink-secondary)]">
            <MapPin className="w-4 h-4" /> <span>{caseDetail.districtName}</span>
          </div>
          <div className="flex items-center gap-2 text-[var(--ink-secondary)]">
            <Calendar className="w-4 h-4" /> <span className="tabular-data">{caseDetail?.openedAt ? new Date(caseDetail.openedAt).toISOString().split('T')[0] : 'N/A'}</span>
          </div>
          <div className="flex items-center gap-2 text-[var(--ink-secondary)] font-mono">
            CRIME_TYPE: <span className="text-[var(--ink-primary)]">{caseDetail.crimeType}</span>
          </div>
          {caseDetail.confidence && (
            <div className="flex items-center gap-2 text-[var(--ink-secondary)] font-mono">
              CONFIDENCE: <span className="text-[var(--accent-focus)]">{(caseDetail.confidence * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Summary & Evidence */}
        <div className="lg:col-span-2 space-y-8">
          <section>
            <h3 className="text-[11px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-3">AI Case Summary</h3>
            <p className="text-[15px] leading-relaxed text-[var(--ink-primary)] p-5 bg-[var(--data-1)] rounded-[6px] border border-[var(--border-hairline)]">
              {caseDetail.summary || "No summary available."}
            </p>
          </section>

          <section>
            <h3 className="text-[11px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-3">Verified Evidence Ledger</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {evidence.map(ev => {
                const Icon = getEvidenceIcon(ev.type);
                return (
                  <div key={ev.id} className="card-base flex flex-col hover:border-[var(--accent-focus)] cursor-pointer group">
                    <div className="flex justify-between items-start mb-3">
                      <div className="w-8 h-8 rounded-[4px] bg-[var(--bg-canvas)] border border-[var(--border-hairline)] flex items-center justify-center text-[var(--ink-secondary)] group-hover:text-[var(--accent-focus)] transition-colors">
                        <Icon className="w-4 h-4" />
                      </div>
                      {ev.verified && <ShieldCheck className="w-4 h-4 text-[var(--trust-chain)]" />}
                    </div>
                    <div className="text-[14px] font-medium mb-1 line-clamp-1">{ev.label}</div>
                    <div className="flex justify-between items-center mt-auto pt-4">
                      <span className="tabular-data text-[11px] text-[var(--ink-tertiary)]">{ev.id}</span>
                      <span className="tabular-data text-[11px] text-[var(--accent-focus)] bg-[#1F3A5C0A] px-2 py-0.5 rounded-[4px]">
                        Conf: {(ev.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                );
              })}
              {evidence.length === 0 && <div className="text-[13px] text-[var(--ink-secondary)] py-4">No evidence recorded yet.</div>}
            </div>
          </section>
        </div>

        {/* Right Column: Timeline */}
        <div className="lg:col-span-1">
          <div className="card-base bg-[var(--bg-canvas)] h-full">
            <h3 className="text-[11px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-6">Chronology</h3>
            
            <div className="relative border-l border-[var(--border-hairline)] ml-3 space-y-6 pb-4">
              {timeline.map((event, idx) => {
                const Icon = getEventIcon(event.type);
                const isFirst = idx === 0;
                
                return (
                  <StaggerItem key={event.id} className="relative pl-6">
                    <div className={`absolute -left-1.5 top-1.5 w-3 h-3 rounded-full border-2 border-[var(--bg-canvas)] ${isFirst ? 'bg-[var(--accent-critical)] ring-2 ring-[var(--accent-critical)]/20' : 'bg-[var(--ink-tertiary)]'}`}></div>
                    
                    <div className="tabular-data text-[11px] text-[var(--ink-secondary)] mb-1">
                      {event.timestamp ? new Date(event.timestamp).toISOString().replace('T', ' ').substring(0, 16) : 'N/A'}
                    </div>
                    
                    <div className="text-[14px] font-medium mb-1 flex items-center gap-2">
                      {event.title}
                    </div>
                    
                    <p className="text-[13px] text-[var(--ink-secondary)] leading-relaxed">
                      {event.description}
                    </p>
                    
                    {event.evidenceIds && event.evidenceIds.length > 0 && (
                      <div className="mt-2 flex gap-2">
                        {event.evidenceIds.map((eid: string) => (
                          <span key={eid} className="tabular-data text-[10px] px-1.5 py-0.5 border border-[var(--border-hairline)] rounded-[2px] bg-white text-[var(--ink-secondary)]">
                            {eid}
                          </span>
                        ))}
                      </div>
                    )}
                  </StaggerItem>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
