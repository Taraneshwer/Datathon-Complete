import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { OpenStreetMap } from "@/components/ksp/OpenStreetMap";
import { useListHotspots } from "@/api-client";
import { Lightbulb, Camera, ShieldCheck, Route as RouteIcon } from "lucide-react";

export function Prevention() {
  const hotspotsQuery = useListHotspots();
  const hotspots = (hotspotsQuery.data as any[]) || [];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Predictive Policing"
        title="Crime Prevention & Blind-Spot Discovery"
        description="Overlay streetlight, CCTV and patrol coverage against crime density — AI predicts vulnerable zones."
        actions={<StatusPill tone="info">Confidence 87%</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-8">
          <OpenStreetMap heatmap={hotspots} markers={hotspots.slice(0, 5).map((m: any) => ({ ...m, tone: "critical" }))} height={520} />
        </div>
        <aside className="col-span-12 lg:col-span-4 space-y-4">
          <SectionCard title="Coverage layers">
            {[
              { icon: Lightbulb, label: "Streetlight coverage", value: 74 },
              { icon: Camera,    label: "CCTV coverage",        value: 58 },
              { icon: ShieldCheck, label: "Patrol density",     value: 63 },
              { icon: RouteIcon, label: "Predictive blindspots", value: 12, tone: "critical" as const },
            ].map((l) => (
              <div key={l.label} className="mb-3 last:mb-0">
                <div className="flex items-center justify-between mb-1">
                  <span className="flex items-center gap-2 text-[13px] text-navy-deep"><l.icon className="h-4 w-4 text-[color:var(--khaki)]" /> {l.label}</span>
                  <span className="text-[12px] font-semibold tabular-nums">{l.value}%</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className={`h-full ${l.tone === "critical" ? "bg-critical" : "bg-navy-deep"}`} style={{ width: `${l.value}%` }} />
                </div>
              </div>
            ))}
          </SectionCard>

          <SectionCard title="Suggested interventions">
            <ul className="space-y-2 text-[13px]">
              <li className="rounded-md border border-border p-2.5"><b className="text-navy-deep">Install 4 CCTV</b> · Koramangala inner ring</li>
              <li className="rounded-md border border-border p-2.5"><b className="text-navy-deep">Add streetlights</b> · HSR sector 4 alleyway</li>
              <li className="rounded-md border border-border p-2.5"><b className="text-navy-deep">Patrol route Bravo</b> · 22:00–02:00 window</li>
            </ul>
          </SectionCard>
        </aside>
      </div>
    </div>
  );
}
