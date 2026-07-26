import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { Send, Mic, Sparkles, ShieldAlert, Bot, User, FileText, MapPin } from "lucide-react";
import { useState } from "react";
import { useGetAssistantHistory, useGetAssistantBlocked } from "@/api-client";

export function AiAssistant() {
  const [q, setQ] = useState("");
  const historyQuery = useGetAssistantHistory();
  const blockedQuery = useGetAssistantBlocked();

  const history = (historyQuery.data as any[]) || [];
  const blocked = (blockedQuery.data as any[]) || [];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="DRISHTI AI"
        title="Personalized Investigative Assistant"
        description="Grounded in case memory, evidence and CCTNS. Prompt-injection firewall active."
        actions={<StatusPill tone="success">Firewall: 12 attacks blocked (24h)</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4 h-[calc(100vh-260px)] min-h-[560px]">
        {/* History */}
        <aside className="col-span-12 lg:col-span-3 govt-card p-3 flex flex-col">
          <p className="text-[11px] uppercase tracking-wider text-muted-foreground px-2 mb-2">Conversations</p>
          <ul className="space-y-1 overflow-y-auto">
            {history.map((h: any, i: number) => (
              <li key={h.id}>
                <button className={`w-full text-left px-2.5 py-2 rounded-md text-[13px] ${i === 0 ? "bg-muted text-navy-deep font-medium" : "hover:bg-muted text-muted-foreground"}`}>
                  <p className="truncate">{h.title}</p>
                  <p className="text-[11px] text-muted-foreground">{h.time}</p>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        {/* Chat */}
        <div className="col-span-12 lg:col-span-6 govt-card flex flex-col">
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            <Msg role="user"      text="Summarize the East Bengaluru chain snatching cluster and recommend next actions." />
            <Msg role="assistant" text={
              <div className="space-y-2">
                <p><b>Cluster C-38</b> spans 12 chain snatching cases along the MG Road → HSR corridor between 21:00–02:00. 7 use two-wheelers with tampered plates. Suspects A-441 and A-317 recur across 5 cases.</p>
                <div className="rounded-md bg-muted p-3 text-[12px]">
                  <div className="flex items-center gap-1.5 text-[color:var(--khaki)] font-semibold text-[11px] uppercase tracking-wider mb-1"><Sparkles className="h-3 w-3" /> Reasoning</div>
                  MO similarity 0.88 · Temporal overlap 0.74 · Geo Kmeans coherence 0.82. Confidence: 92%.
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <Suggestion icon={FileText} label="Draft chargesheet" />
                  <Suggestion icon={MapPin}   label="Deploy patrol Alpha" />
                </div>
              </div>
            } />
          </div>

          <div className="border-t border-border p-3 bg-muted/30">
            <div className="flex items-center gap-2 rounded-md bg-card border border-border p-2">
              <button className="h-8 w-8 rounded-md grid place-items-center hover:bg-muted"><Mic className="h-4 w-4 text-navy-deep" /></button>
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask DRISHTI — grounded in your cases…"
                className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground py-1.5" />
              <button className="h-8 px-3 rounded-md bg-navy-deep text-white text-xs font-semibold flex items-center gap-1.5"><Send className="h-3.5 w-3.5" /> Send</button>
            </div>
            <p className="text-[10px] text-muted-foreground mt-1.5 flex items-center gap-1"><ShieldAlert className="h-3 w-3 text-success" /> All prompts sanitized · Injection firewall v2.1</p>
          </div>
        </div>

        {/* Security panel */}
        <aside className="col-span-12 lg:col-span-3 space-y-4 overflow-y-auto">
          <SectionCard title="Prompt Firewall">
            <div className="rounded-md bg-critical/10 text-critical p-3 flex items-center justify-between mb-3">
              <div>
                <p className="text-[11px] uppercase tracking-wider">Threat score</p>
                <p className="text-2xl font-display font-semibold">18/100</p>
              </div>
              <ShieldAlert className="h-8 w-8" />
            </div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">Blocked prompts</p>
            <ul className="space-y-1.5 text-[12px]">
              {blocked.map((b: any) => (
                <li key={b.id} className="rounded-md border border-critical/20 bg-critical/5 p-2">
                  <p className="text-navy-deep truncate">"{b.msg}"</p>
                  <p className="text-[10px] text-muted-foreground flex items-center justify-between"><span>{b.id} · {b.time}</span><span className="text-critical font-semibold">Score {b.score}</span></p>
                </li>
              ))}
            </ul>
          </SectionCard>
        </aside>
      </div>
    </div>
  );
}

function Msg({ role, text }: { role: "user" | "assistant"; text: any }) {
  const isUser = role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`h-8 w-8 rounded-md grid place-items-center shrink-0 ${isUser ? "bg-navy-deep text-gold" : "bg-gold text-navy-deep"}`}>
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div className={`rounded-lg px-3.5 py-2.5 text-[13px] max-w-[80%] ${isUser ? "bg-navy-deep text-white" : "bg-muted text-navy-deep"}`}>
        {text}
      </div>
    </div>
  );
}

function Suggestion({ icon: Icon, label }: { icon: any; label: string }) {
  return (
    <button className="flex items-center gap-2 text-[12px] px-3 py-2 rounded-md border border-border hover:border-gold hover:bg-accent">
      <Icon className="h-3.5 w-3.5 text-[color:var(--khaki)]" /> {label}
    </button>
  );
}
