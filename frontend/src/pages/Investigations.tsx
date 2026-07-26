
import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { CASES } from "@/lib/ksp-data";
import { Filter, Plus, Search, Briefcase } from "lucide-react";

export function Investigations() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Case Management"
        title="Active Investigations"
        description="Live view of open cases assigned across Karnataka jurisdictions."
        actions={
          <>
            <button className="h-9 px-3 text-sm rounded-md border border-border bg-card hover:bg-muted flex items-center gap-1.5"><Filter className="h-4 w-4" /> Filters</button>
            <button className="h-9 px-3 text-sm rounded-md bg-navy-deep text-white hover:bg-navy flex items-center gap-1.5"><Plus className="h-4 w-4" /> New Case</button>
          </>
        }
      />

      <SectionCard>
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center gap-2 h-9 flex-1 max-w-md rounded-md border border-border bg-muted/40 px-3">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input placeholder="Search cases, suspects, FIR numbers…" className="flex-1 bg-transparent text-sm outline-none" />
          </div>
          <div className="flex items-center gap-1.5">
            {["All", "Property", "Cyber", "Narcotics", "Economic", "Missing"].map((t, i) => (
              <button key={t} className={`text-xs px-3 py-1.5 rounded-md border ${i === 0 ? "bg-navy-deep text-white border-navy-deep" : "border-border hover:bg-muted"}`}>{t}</button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {CASES.map((c) => (
            <article key={c.id} className="govt-card p-4 hover:border-gold/60 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="h-9 w-9 rounded-md bg-navy-deep/10 text-navy-deep grid place-items-center">
                    <Briefcase className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-mono text-[11px] text-muted-foreground">{c.id}</p>
                    <p className="text-[11px] font-semibold text-[color:var(--khaki)] uppercase tracking-wider">{c.type}</p>
                  </div>
                </div>
                <StatusPill tone={c.tone}>{c.status}</StatusPill>
              </div>

              <h3 className="font-display text-[14px] font-semibold text-navy-deep leading-snug mb-3">{c.title}</h3>

              <div className="text-xs text-muted-foreground space-y-1 mb-3">
                <p><span className="text-navy-deep font-medium">Assigned:</span> {c.assigned}</p>
                <p><span className="text-navy-deep font-medium">Priority:</span> {c.priority} · <span className="text-navy-deep font-medium">Evidence:</span> {c.evidence}</p>
              </div>

              <div className="mb-1 flex items-center justify-between text-[11px]">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-semibold text-navy-deep">{c.progress}%</span>
              </div>
              <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                <div className="h-full bg-gradient-to-r from-navy-deep to-gold" style={{ width: `${c.progress}%` }} />
              </div>
            </article>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
