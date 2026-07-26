import { useEffect, useState } from "react";
import { Bell, Search, ShieldCheck, Command, Radio } from "lucide-react";

export function TopBar() {
  const [time, setTime] = useState(() => new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const timeStr = time.toLocaleTimeString("en-IN", { hour12: false });
  const dateStr = time.toLocaleDateString("en-IN", { weekday: "short", day: "2-digit", month: "short", year: "numeric" });

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur border-b border-border flex items-center gap-4 px-6">
      {/* Left: brand line */}
      <div className="hidden md:flex flex-col shrink-0">
        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[color:var(--khaki)]">Government of Karnataka · Home Department</p>
        <p className="text-sm font-display font-semibold text-navy-deep leading-tight">AI Crime Intelligence Platform</p>
      </div>

      {/* Center: global search */}
      <div className="flex-1 max-w-2xl mx-auto">
        <div className="flex items-center gap-2 h-10 rounded-md border border-border bg-muted/50 px-3 focus-within:border-gold focus-within:bg-card transition-colors">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            placeholder="Ask natural language · e.g. 'suspects near MG Road last 24h'"
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="hidden md:inline-flex items-center gap-1 text-[10px] font-semibold text-muted-foreground border border-border rounded px-1.5 py-0.5">
            <Command className="h-3 w-3" /> K
          </kbd>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-3 shrink-0">
        <div className="hidden lg:flex flex-col text-right">
          <span className="font-mono tabular-nums text-sm text-navy-deep font-semibold">{timeStr} IST</span>
          <span className="text-[10px] text-muted-foreground">{dateStr}</span>
        </div>

        <div className="hidden md:flex items-center gap-1.5 h-8 rounded-full bg-success/10 text-success px-2.5 text-[11px] font-semibold ring-1 ring-success/20">
          <ShieldCheck className="h-3.5 w-3.5" /> SECURE SESSION
        </div>

        <button className="relative h-9 w-9 rounded-md grid place-items-center hover:bg-muted transition-colors">
          <Bell className="h-[18px] w-[18px] text-navy-deep" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-critical ring-2 ring-white" />
        </button>

        <button className="relative h-9 w-9 rounded-md grid place-items-center hover:bg-muted transition-colors" title="National alerts">
          <Radio className="h-[18px] w-[18px] text-navy-deep" />
        </button>

        <div className="flex items-center gap-2.5 pl-3 border-l border-border">
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-navy-deep to-navy grid place-items-center text-gold font-semibold text-sm">AR</div>
          <div className="hidden lg:block">
            <p className="text-[13px] font-semibold text-navy-deep leading-tight">IPS Arun Rao</p>
            <p className="text-[11px] text-muted-foreground leading-tight">SP Cyber Crime · Bengaluru City</p>
          </div>
        </div>
      </div>
    </header>
  );
}
