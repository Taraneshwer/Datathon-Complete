
import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { GoogleMap } from "@/components/ksp/GoogleMap";
import { NATIONAL_ALERTS } from "@/lib/ksp-data";
import { Radio, ArrowRight } from "lucide-react";

export function NationalAlerts() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Inter-State Coordination"
        title="National Crime Early Warning System"
        description="Live advisories from CCTNS, NCB and neighbouring state DGPs — auto-triaged for Karnataka."
        actions={<StatusPill tone="critical">2 CRITICAL active</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-4 space-y-3">
          {NATIONAL_ALERTS.map((a) => (
            <div key={a.id} className="govt-card p-4 hover:border-gold/60 transition-colors">
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono text-[11px] text-muted-foreground">{a.id}</span>
                <StatusPill tone={a.tone}>{a.risk}</StatusPill>
              </div>
              <div className="flex items-start gap-3 mb-2">
                <div className="h-9 w-9 rounded-md bg-navy-deep/10 text-navy-deep grid place-items-center shrink-0"><Radio className="h-4 w-4" /></div>
                <div className="min-w-0">
                  <p className="text-[13px] font-semibold text-navy-deep">{a.title}</p>
                  <p className="text-[11px] text-muted-foreground">{a.cat}</p>
                </div>
              </div>
              <button className="text-xs font-semibold text-navy-deep hover:text-gold flex items-center gap-1">
                View intervention <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>

        <div className="col-span-12 lg:col-span-8">
          <GoogleMap
            center={{ lat: 14.5, lng: 76 }}
            zoom={7}
            markers={NATIONAL_ALERTS.map(a => ({ lat: a.lat, lng: a.lng, tone: a.tone as any, label: a.title }))}
            height={560}
          />
        </div>
      </div>
    </div>
  );
}
