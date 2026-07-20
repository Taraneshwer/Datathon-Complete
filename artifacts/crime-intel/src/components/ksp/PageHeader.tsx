import type { ReactNode } from "react";

export function PageHeader({
  eyebrow, title, description, actions,
}: { eyebrow?: string; title: string; description?: string; actions?: ReactNode }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4 border-b border-border pb-5 mb-6">
      <div className="min-w-0">
        {eyebrow && (
          <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[color:var(--khaki)]">
            {eyebrow}
          </p>
        )}
        <h1 className="font-display text-2xl md:text-[28px] font-semibold text-navy-deep tracking-tight mt-1">
          {title}
        </h1>
        {description && (
          <p className="text-sm text-muted-foreground mt-1 max-w-3xl">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
  );
}

export function SectionCard({
  title, subtitle, actions, children, className = "",
}: { title?: string; subtitle?: string; actions?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`govt-card p-5 ${className}`}>
      {(title || actions) && (
        <header className="flex items-center justify-between mb-4">
          <div>
            {title && <h3 className="font-display text-[15px] font-semibold text-navy-deep">{title}</h3>}
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}

export function StatusPill({
  tone = "info", children,
}: { tone?: "success" | "critical" | "warning" | "info" | "navy"; children: ReactNode }) {
  const map = {
    success:  "bg-success/10 text-success ring-success/20",
    critical: "bg-critical/10 text-critical ring-critical/20",
    warning:  "bg-warning/15 text-[color:var(--khaki)] ring-warning/30",
    info:     "bg-info/10 text-info ring-info/20",
    navy:     "bg-navy-deep/10 text-navy-deep ring-navy-deep/20",
  } as const;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ${map[tone]}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${
        tone === "success" ? "bg-success" :
        tone === "critical" ? "bg-critical" :
        tone === "warning" ? "bg-warning" :
        tone === "info" ? "bg-info" : "bg-navy-deep"
      }`} />
      {children}
    </span>
  );
}
