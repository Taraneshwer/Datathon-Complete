
import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { Fingerprint, QrCode, ShieldCheck, User } from "lucide-react";

const CREDS = [
  { type: "Officer DID",  id: "did:ksp:0xA1..B2", holder: "IPS Arun Rao",    status: "Verified", tone: "success" as const },
  { type: "Citizen DID",  id: "did:ksp:0xC3..D4", holder: "R. Sharma",       status: "Verified", tone: "success" as const },
  { type: "Witness DID",  id: "did:ksp:0xE5..F6", holder: "Witness W-14",    status: "Pending",  tone: "warning" as const },
  { type: "Evidence DID", id: "did:ksp:0x77..99", holder: "EV-9812",         status: "Verified", tone: "success" as const },
];

export function Identity() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Trust Infrastructure"
        title="Decentralized Identity Registry"
        description="Verifiable credentials for officers, citizens, witnesses and evidence — anchored to the Karnataka Police ledger."
        actions={<StatusPill tone="success">Ledger sync: 100%</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-8">
          <SectionCard title="Credentials">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {CREDS.map((c) => (
                <div key={c.id} className="govt-card p-4 topline">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-[color:var(--khaki)]">{c.type}</span>
                    <StatusPill tone={c.tone}>{c.status}</StatusPill>
                  </div>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-11 w-11 rounded-md bg-navy-deep text-gold grid place-items-center"><Fingerprint className="h-5 w-5" /></div>
                    <div>
                      <p className="text-[14px] font-semibold text-navy-deep">{c.holder}</p>
                      <p className="text-[11px] font-mono text-muted-foreground">{c.id}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t border-border">
                    <button className="text-xs font-semibold text-navy-deep hover:text-gold flex items-center gap-1"><QrCode className="h-3.5 w-3.5" /> Verify QR</button>
                    <button className="text-xs font-semibold text-navy-deep hover:text-gold flex items-center gap-1"><ShieldCheck className="h-3.5 w-3.5" /> On-chain</button>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <aside className="col-span-12 lg:col-span-4">
          <SectionCard title="Verification Timeline">
            <ol className="relative border-l-2 border-border ml-2 space-y-3">
              {["Credential issued","Signed by DGP office","Broadcast to ledger","Verified by 5 nodes","Public attestation available"].map((s, i) => (
                <li key={i} className="pl-4 relative">
                  <span className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-success ring-2 ring-white" />
                  <p className="text-[13px] text-navy-deep">{s}</p>
                  <p className="text-[10px] font-mono text-muted-foreground">block #18492{4-i}</p>
                </li>
              ))}
            </ol>
          </SectionCard>
        </aside>
      </div>
    </div>
  );
}
