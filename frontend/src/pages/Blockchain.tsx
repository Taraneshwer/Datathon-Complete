import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { useGetBlockchainLedger } from "@/api-client";
import { Blocks, ShieldCheck, Fingerprint, Key, User } from "lucide-react";

export function Blockchain() {
  const ledgerQuery = useGetBlockchainLedger();
  const ledger = (ledgerQuery.data as any[]) || [];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Immutable Audit"
        title="Blockchain Ledger & Access Log"
        description="Every evidence hash, custody transfer and permission change — signed, timestamped, tamper-evident."
        actions={<StatusPill tone="success">Chain integrity 100%</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 md:col-span-6 lg:col-span-3"><MiniStat icon={Blocks}      label="Blocks"          value="184,920" /></div>
        <div className="col-span-12 md:col-span-6 lg:col-span-3"><MiniStat icon={ShieldCheck} label="Verified events" value="72,481" /></div>
        <div className="col-span-12 md:col-span-6 lg:col-span-3"><MiniStat icon={Fingerprint} label="Evidence hashes"  value="18,204" /></div>
        <div className="col-span-12 md:col-span-6 lg:col-span-3"><MiniStat icon={Key}         label="Signatures (24h)" value="1,204" /></div>
      </div>

      <SectionCard title="Ledger · Latest events" subtitle="Genesis: Karnataka Police 2023-04-01">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-b border-border">
              <th className="py-2 px-2">Block</th><th>Hash</th><th>Actor</th><th>Action</th><th>Time</th><th>Integrity</th>
            </tr>
          </thead>
          <tbody>
            {ledger.map((l: any) => (
              <tr key={l.block} className="border-b border-border/60 hover:bg-muted/40">
                <td className="py-2.5 px-2 font-mono text-xs">#{l.block}</td>
                <td className="py-2.5 font-mono text-xs text-muted-foreground">{l.hash}</td>
                <td className="py-2.5 flex items-center gap-2"><User className="h-4 w-4 text-muted-foreground" />{l.actor}</td>
                <td className="py-2.5">{l.action}</td>
                <td className="py-2.5 font-mono text-xs text-muted-foreground">{l.time}</td>
                <td className="py-2.5"><StatusPill tone={l.ok ? "success" : "critical"}>{l.ok ? "OK" : "Tamper alert"}</StatusPill></td>
              </tr>
            ))}
          </tbody>
        </table>
      </SectionCard>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-6">
          <SectionCard title="Access Control · RBAC">
            <ul className="text-[13px] space-y-2">
              {[
                { role: "IPS · SP",    perms: "Full access",              tone: "navy" as const },
                { role: "DySP",        perms: "Case + evidence + audit",  tone: "info" as const },
                { role: "PI / SI",     perms: "Case + evidence",          tone: "info" as const },
                { role: "Analyst",     perms: "Read-only analytics",       tone: "success" as const },
              ].map((r) => (
                <li key={r.role} className="flex items-center justify-between rounded-md border border-border p-2.5">
                  <span className="text-navy-deep font-medium">{r.role}</span>
                  <StatusPill tone={r.tone}>{r.perms}</StatusPill>
                </li>
              ))}
            </ul>
          </SectionCard>
        </div>

        <div className="col-span-12 lg:col-span-6">
          <SectionCard title="Authentication · MFA + Biometric">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-md border border-border p-4 text-center">
                <Fingerprint className="h-8 w-8 mx-auto text-navy-deep" />
                <p className="text-[13px] font-semibold text-navy-deep mt-2">Biometric</p>
                <p className="text-[11px] text-muted-foreground">Aadhaar-Auth ready</p>
                <StatusPill tone="success"><span>Enabled</span></StatusPill>
              </div>
              <div className="rounded-md border border-border p-4 text-center">
                <Key className="h-8 w-8 mx-auto text-navy-deep" />
                <p className="text-[13px] font-semibold text-navy-deep mt-2">Hardware Key</p>
                <p className="text-[11px] text-muted-foreground">FIDO2 / U2F</p>
                <StatusPill tone="success"><span>Enabled</span></StatusPill>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}

function MiniStat({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <div className="govt-card p-4 flex items-center gap-3">
      <div className="h-10 w-10 rounded-md bg-navy-deep/10 text-navy-deep grid place-items-center"><Icon className="h-5 w-5" /></div>
      <div>
        <p className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</p>
        <p className="font-display text-xl font-semibold text-navy-deep tabular-nums">{value}</p>
      </div>
    </div>
  );
}
