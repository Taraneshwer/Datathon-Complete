
import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { OpenStreetMap } from "@/components/ksp/OpenStreetMap";
import { useEffect, useRef, useState } from "react";
import { Play, Pause, SkipBack, SkipForward, Gauge } from "lucide-react";

const PATH = [
  { t: 0,  lat: 12.9716, lng: 77.5946, event: "Victim leaves MG Road metro" },
  { t: 12, lat: 12.9686, lng: 77.6060, event: "Vehicle KA-05 seen tailing" },
  { t: 27, lat: 12.9640, lng: 77.6180, event: "Suspect intercepts victim" },
  { t: 41, lat: 12.9552, lng: 77.6220, event: "Chain snatched · fled east" },
  { t: 55, lat: 12.9410, lng: 77.6300, event: "Suspect reaches HSR safehouse" },
  { t: 72, lat: 12.9081, lng: 77.6476, event: "PCR unit responds" },
];

export function Replay() {
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(1);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    if (!playing) return;
    let last = performance.now();
    const tick = (now: number) => {
      const dt = (now - last) / 1000; last = now;
      setT((v) => (v + dt * speed) % 100);
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => { if (raf.current) cancelAnimationFrame(raf.current); };
  }, [playing, speed]);

  const idx = Math.min(PATH.length - 1, Math.floor((t / 100) * PATH.length));
  const currentEvent = PATH[idx];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Investigation Agent"
        title="Crime Replay · Timeline Reconstruction"
        description="Synchronised playback of suspect, victim and officer movement on OpenStreetMap."
        actions={<StatusPill tone="info">Case KA-2886 · 12 min timeline</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-8">
          <OpenStreetMap
            center={currentEvent}
            zoom={13}
            markers={PATH.slice(0, idx + 1).map((p, i) => ({
              ...p, tone: i === idx ? "critical" : "info", label: p.event,
            }))}
            height={520}
          />
        </div>

        <aside className="col-span-12 lg:col-span-4 space-y-4">
          <SectionCard title="Event Log" subtitle="Chronological reconstruction">
            <ol className="relative border-l-2 border-border ml-2 space-y-3">
              {PATH.map((p, i) => (
                <li key={i} className="pl-4 relative">
                  <span className={`absolute -left-[7px] top-1 h-3 w-3 rounded-full ring-2 ring-white ${i === idx ? "bg-critical animate-pulse" : i < idx ? "bg-success" : "bg-muted-foreground/40"}`} />
                  <p className="text-[11px] font-mono text-muted-foreground">T+{p.t}s</p>
                  <p className={`text-[13px] ${i === idx ? "text-navy-deep font-semibold" : "text-muted-foreground"}`}>{p.event}</p>
                </li>
              ))}
            </ol>
          </SectionCard>
        </aside>
      </div>

      <SectionCard>
        <div className="flex items-center gap-4">
          <button onClick={() => setT(0)} className="h-9 w-9 rounded-md border border-border grid place-items-center hover:bg-muted"><SkipBack className="h-4 w-4" /></button>
          <button onClick={() => setPlaying((p) => !p)} className="h-11 w-11 rounded-full bg-navy-deep text-white grid place-items-center hover:bg-navy">
            {playing ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-0.5" />}
          </button>
          <button onClick={() => setT(100)} className="h-9 w-9 rounded-md border border-border grid place-items-center hover:bg-muted"><SkipForward className="h-4 w-4" /></button>

          <div className="flex-1 mx-4">
            <input type="range" min={0} max={100} step={0.1} value={t} onChange={(e) => setT(+e.target.value)} className="w-full accent-[color:var(--gold)]" />
            <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
              <span>00:00</span><span className="font-mono text-navy-deep font-semibold">{Math.round(t)}%</span><span>12:00</span>
            </div>
          </div>

          <div className="flex items-center gap-1 text-xs">
            <Gauge className="h-4 w-4 text-muted-foreground" />
            {[0.5, 1, 2, 4].map((s) => (
              <button key={s} onClick={() => setSpeed(s)} className={`px-2 py-1 rounded ${speed === s ? "bg-navy-deep text-white" : "hover:bg-muted"}`}>{s}×</button>
            ))}
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
