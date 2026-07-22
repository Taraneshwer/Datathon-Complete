import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { User, Bell, ShieldCheck, Key, Globe } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export function Settings() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Preferences"
        title="Platform Settings"
        description="Officer profile, branding preferences, security posture and integration keys."
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-4 space-y-4">
          <SectionCard title="Officer Profile">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-14 w-14 rounded-full bg-[var(--accent-focus)] text-white grid place-items-center font-semibold text-lg">AR</div>
              <div>
                <p className="text-[14px] font-semibold text-[var(--ink-primary)]">IPS Arun Rao</p>
                <p className="text-[11px] text-muted-foreground">SP Cyber Crime · Bengaluru City</p>
                <StatusPill tone="success">Active duty</StatusPill>
              </div>
            </div>
            <Field icon={User} label="Service ID" value="KSP-IPS-2011-0431" />
            <Field icon={Globe} label="Jurisdiction" value="Bengaluru City · Cyber" />
          </SectionCard>

          <SectionCard title="Branding Preference">
            <p className="text-xs text-muted-foreground mb-3">
              Switch the theme and branding of the CIPA platform.
            </p>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => setTheme('ksp')}
                className={`flex items-center justify-between text-left text-[13px] px-3 py-2 rounded-md border ${
                  theme === 'ksp'
                    ? 'border-[var(--accent-focus)] bg-[var(--data-1)] font-semibold'
                    : 'border-border hover:bg-[var(--data-1)]'
                }`}
              >
                <span>Karnataka State Police (KSP)</span>
                {theme === 'ksp' && <StatusPill tone="success">Active</StatusPill>}
              </button>
              <button
                onClick={() => setTheme('scrb')}
                className={`flex items-center justify-between text-left text-[13px] px-3 py-2 rounded-md border ${
                  theme === 'scrb'
                    ? 'border-[var(--accent-focus)] bg-[var(--data-1)] font-semibold'
                    : 'border-border hover:bg-[var(--data-1)]'
                }`}
              >
                <span>State Crime Records Bureau (SCRB)</span>
                {theme === 'scrb' && <StatusPill tone="success">Active</StatusPill>}
              </button>
            </div>
          </SectionCard>
        </div>

        <div className="col-span-12 lg:col-span-8 space-y-4">
          <SectionCard title="Notifications">
            <ul className="text-[13px] space-y-2">
              {["High-priority alerts","Evidence added","Officer assignment","Blockchain verification","National advisories","Case escalation"].map((n, i) => (
                <li key={n} className="flex items-center justify-between rounded-md border border-border p-2.5">
                  <span className="flex items-center gap-2 text-[var(--ink-primary)]"><Bell className="h-4 w-4 text-[color:var(--khaki)]" /> {n}</span>
                  <Toggle on={i !== 5} />
                </li>
              ))}
            </ul>
          </SectionCard>

          <SectionCard title="Security">
            <ul className="text-[13px] space-y-2">
              <li className="flex items-center justify-between rounded-md border border-border p-2.5">
                <span className="flex items-center gap-2 text-[var(--ink-primary)]"><ShieldCheck className="h-4 w-4 text-success" /> Multi-factor authentication</span>
                <StatusPill tone="success">Enabled</StatusPill>
              </li>
              <li className="flex items-center justify-between rounded-md border border-border p-2.5">
                <span className="flex items-center gap-2 text-[var(--ink-primary)]"><Key className="h-4 w-4 text-success" /> Hardware key (FIDO2)</span>
                <StatusPill tone="success">Enabled</StatusPill>
              </li>
              <li className="flex items-center justify-between rounded-md border border-border p-2.5">
                <span className="flex items-center gap-2 text-[var(--ink-primary)]"><Globe className="h-4 w-4 text-info" /> Google Maps API</span>
                <StatusPill tone="info">Configure in Cloud secrets</StatusPill>
              </li>
            </ul>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}

function Field({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 py-1.5 text-[13px]">
      <Icon className="h-4 w-4 text-muted-foreground" />
      <span className="text-muted-foreground">{label}</span>
      <span className="ml-auto text-[var(--ink-primary)] font-medium">{value}</span>
    </div>
  );
}

function Toggle({ on }: { on: boolean }) {
  return (
    <div className={`h-5 w-9 rounded-full ${on ? "bg-[var(--accent-focus)]" : "bg-muted"} relative transition-colors`}>
      <div className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-all ${on ? "left-4" : "left-0.5"}`} />
    </div>
  );
}
