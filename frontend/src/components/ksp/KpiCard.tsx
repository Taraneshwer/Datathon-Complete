import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect } from "react";
import type { LucideIcon } from "lucide-react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";

type Props = {
  label: string;
  value: number;
  suffix?: string;
  delta?: number; // percent
  icon: LucideIcon;
  tone?: "navy" | "gold" | "success" | "critical" | "info" | "warning";
  hint?: string;
  spark?: number[];
};

const toneMap = {
  navy:     { chip: "bg-navy-deep/10 text-navy-deep",  bar: "bg-navy-deep" },
  gold:     { chip: "bg-gold/15 text-[color:var(--khaki)]", bar: "bg-gold" },
  success:  { chip: "bg-success/10 text-success",      bar: "bg-success" },
  critical: { chip: "bg-critical/10 text-critical",    bar: "bg-critical" },
  info:     { chip: "bg-info/10 text-info",            bar: "bg-info" },
  warning:  { chip: "bg-warning/15 text-[color:var(--khaki)]", bar: "bg-warning" },
};

export function KpiCard({ label, value, suffix = "", delta, icon: Icon, tone = "navy", hint, spark }: Props) {
  const mv = useMotionValue(0);
  const rounded = useTransform(mv, (v) => Math.round(v).toLocaleString("en-IN"));
  useEffect(() => {
    const c = animate(mv, value, { duration: 1.2, ease: "easeOut" });
    return c.stop;
  }, [value, mv]);

  const t = toneMap[tone];
  const positive = (delta ?? 0) >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="govt-card topline p-5 flex flex-col gap-3 min-h-[148px]"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</p>
          {hint && <p className="text-[11px] text-muted-foreground/80 mt-0.5">{hint}</p>}
        </div>
        <div className={`h-9 w-9 rounded-md grid place-items-center ${t.chip}`}>
          <Icon className="h-[18px] w-[18px]" strokeWidth={2} />
        </div>
      </div>

      <div className="flex items-end justify-between gap-3">
        <div className="font-display text-[32px] leading-none font-semibold text-navy-deep tabular-nums">
          <motion.span>{rounded}</motion.span>
          {suffix && <span className="text-lg text-muted-foreground ml-1">{suffix}</span>}
        </div>
        {typeof delta === "number" && (
          <div className={`flex items-center gap-1 text-xs font-semibold ${positive ? "text-success" : "text-critical"}`}>
            {positive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
            {Math.abs(delta).toFixed(1)}%
          </div>
        )}
      </div>

      {spark && <Sparkline data={spark} color={`var(--${tone === "navy" ? "navy-deep" : tone})`} />}
    </motion.div>
  );
}

function Sparkline({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data), min = Math.min(...data);
  const range = max - min || 1;
  const pts = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 24 - ((d - min) / range) * 22;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg viewBox="0 0 100 26" preserveAspectRatio="none" className="w-full h-6">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}
