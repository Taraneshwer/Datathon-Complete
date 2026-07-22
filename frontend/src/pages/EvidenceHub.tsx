
import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { EVIDENCE_ITEMS } from "@/lib/ksp-data";
import { Upload, Image as ImageIcon, Video, FileText, Music, ScanSearch, Fingerprint, Sparkles } from "lucide-react";

const TYPE_ICON: Record<string, any> = { Video: Video, Image: ImageIcon, Audio: Music, Document: FileText };

export function EvidenceHub() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Digital Forensics"
        title="Evidence Center"
        description="Immutable evidence vault with AI OCR, object detection and blockchain chain-of-custody."
        actions={
          <button className="h-9 px-3 text-sm rounded-md bg-navy-deep text-white flex items-center gap-1.5"><Upload className="h-4 w-4" /> Upload Evidence</button>
        }
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-8">
          <SectionCard title="Evidence Vault" subtitle="Sorted by chain integrity">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-b border-border">
                  <th className="py-2 px-2">ID</th><th>Type</th><th>Case</th><th>Size</th><th>SHA-256</th><th>Chain</th>
                </tr>
              </thead>
              <tbody>
                {EVIDENCE_ITEMS.map((e) => {
                  const Icon = TYPE_ICON[e.type] ?? FileText;
                  return (
                    <tr key={e.id} className="border-b border-border/60 hover:bg-muted/40">
                      <td className="py-2.5 px-2 font-mono text-xs">{e.id}</td>
                      <td className="py-2.5 flex items-center gap-2"><Icon className="h-4 w-4 text-navy-deep" />{e.type}</td>
                      <td className="py-2.5 font-mono text-xs">{e.case}</td>
                      <td className="py-2.5 text-muted-foreground">{e.size}</td>
                      <td className="py-2.5 font-mono text-xs text-muted-foreground">{e.hash}</td>
                      <td className="py-2.5"><StatusPill tone={e.tone}>{e.chain}</StatusPill></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </SectionCard>
        </div>

        <aside className="col-span-12 lg:col-span-4 space-y-4">
          <SectionCard title="AI Analysis · EV-9812">
            <div className="aspect-video rounded-md bg-navy-deep text-white/70 scanline grid place-items-center text-xs mb-3">Video preview · frame 00:04:12</div>
            <ul className="space-y-2 text-[13px]">
              <Row icon={ScanSearch}  label="OCR" value="License plate: KA-05-MH-1234" />
              <Row icon={Fingerprint} label="Object" value="2 persons, 1 motorcycle" />
              <Row icon={Sparkles}    label="AI Summary" value="High-confidence match to Case KA-2886" />
            </ul>
            <div className="mt-3 flex items-center justify-between rounded-md bg-success/10 text-success p-2 text-[12px] font-semibold">
              Evidence confidence <span className="font-display text-lg">94%</span>
            </div>
          </SectionCard>

          <SectionCard title="Chain of Custody">
            <ol className="relative border-l-2 border-border ml-2 space-y-3">
              {["Collected · SI Iyer","Hash sealed · Blockchain","Transferred · PI Nair","Analyzed · Cyber lab","Archived · Central vault"].map((s, i) => (
                <li key={i} className="pl-4 relative">
                  <span className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-gold ring-2 ring-white" />
                  <p className="text-[13px] text-navy-deep">{s}</p>
                </li>
              ))}
            </ol>
          </SectionCard>
        </aside>
      </div>
    </div>
  );
}

function Row({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <li className="flex items-center justify-between gap-3">
      <span className="flex items-center gap-2 text-muted-foreground text-[11px] uppercase tracking-wider"><Icon className="h-3.5 w-3.5" /> {label}</span>
      <span className="text-navy-deep font-medium text-right">{value}</span>
    </li>
  );
}
