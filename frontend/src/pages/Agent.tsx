import { PageTransition, StaggerItem } from '../components/Motion';
import { Bot, Terminal, Send, ShieldCheck } from 'lucide-react';
import { CaseIdLink } from '../components/CaseIdLink';
import { useGetCase, useGetSuspect } from '@/api-client';

export function Agent() {
  const caseQuery = useGetCase('KA-2024-00847');
  const suspectQuery = useGetSuspect('S01');

  const caseData = (caseQuery.data as any) || {};
  const suspectData = (suspectQuery.data as any) || {};

  const moSummary = caseData.summary || "Late-night forced entry via rear windows targeting portable electronics. The alarm system was bypassed using techniques consistent with Pattern P01.";
  const suspectName = suspectData.name ? `${suspectData.name} (${suspectData.id})` : "Arun Kumar (S01)";
  const suspectRisk = suspectData.riskScore || 85;
  const suspectNotes = suspectData.moSummary || "Known associate of Syed Ali. Last seen: 2024-06-05 in Indiranagar.";

  return (
    <PageTransition className="max-w-4xl mx-auto h-[calc(100vh-140px)] flex flex-col">
      <header className="mb-6 shrink-0">
        <h1 className="text-section-header">Investigative Agent</h1>
        <p className="text-body text-[var(--ink-secondary)] mt-1">Tier-3 clearance required. Sandbox environment active.</p>
      </header>

      <div className="flex-1 card-base p-0 flex flex-col overflow-hidden border-[var(--border-hairline)] shadow-sm relative bg-white">
        
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-white">
          
          <StaggerItem>
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-[4px] bg-[var(--accent-focus)] text-white flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="pt-1 text-[14px]">
                <p className="text-[var(--ink-primary)] leading-relaxed">
                  I am the CIPA Investigative Agent. I have access to state-wide case files, biometric records, and real-time ledger data. 
                  How can I assist your investigation today?
                </p>
              </div>
            </div>
          </StaggerItem>

          <StaggerItem className="opacity-90">
            <div className="flex gap-4 flex-row-reverse">
              <div className="w-8 h-8 rounded-[4px] bg-[var(--data-1)] border border-[var(--border-hairline)] text-[var(--ink-secondary)] flex items-center justify-center shrink-0 font-mono text-[11px]">
                ME
              </div>
              <div className="pt-1 text-[14px] text-right max-w-2xl">
                <p className="text-[var(--ink-primary)] leading-relaxed">
                  Summarize the MO for <CaseIdLink id="KA-2024-00847" /> and identify if any suspects from past 6 months match this profile in adjacent districts.
                </p>
              </div>
            </div>
          </StaggerItem>

          <StaggerItem>
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-[4px] bg-[var(--accent-focus)] text-white flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="pt-1 text-[14px] max-w-3xl">
                <div className="mb-4">
                  <span className="inline-flex items-center gap-1.5 text-[10px] font-mono uppercase bg-[var(--data-1)] px-2 py-0.5 rounded-[4px] text-[var(--ink-tertiary)] mb-2">
                    <Terminal className="w-3 h-3" /> Querying KG / Pattern Matching
                  </span>
                </div>
                <p className="text-[var(--ink-primary)] leading-relaxed mb-4">
                  {moSummary}
                </p>
                <p className="text-[var(--ink-primary)] leading-relaxed mb-4">
                  I scanned adjacent districts (Mysuru, Tumakuru) for the past 6 months. I found 1 high-confidence match:
                </p>
                <div className="p-4 border border-[var(--border-hairline)] rounded-[6px] bg-[var(--bg-canvas)] space-y-2">
                  <div className="flex justify-between items-center border-b border-[var(--border-hairline)] pb-2 mb-2">
                    <span className="font-medium">Suspect: {suspectName}</span>
                    <span className="text-[11px] font-mono text-[var(--accent-critical)]">Risk Score: {suspectRisk}</span>
                  </div>
                  <div className="text-[13px] text-[var(--ink-secondary)]">
                    {suspectNotes}
                    <br />Linked to <CaseIdLink id="KA-2024-00812" /> with identical entry method.
                  </div>
                </div>
              </div>
            </div>
          </StaggerItem>
          
        </div>

        {/* Input Area */}
        <div className="p-4 bg-[var(--bg-canvas)] border-t border-[var(--border-hairline)]">
          <div className="relative flex items-center">
            <div className="absolute left-3 flex items-center justify-center h-full">
               <ShieldCheck className="w-4 h-4 text-[var(--trust-chain)]" />
            </div>
            <input 
              type="text" 
              placeholder="Ask a question or request an analysis... (Sandbox mode)" 
              disabled
              className="w-full h-12 pl-10 pr-12 bg-white border border-[var(--border-hairline)] rounded-[6px] text-[14px] focus:outline-none focus:border-[var(--accent-focus)] focus:ring-1 focus:ring-[var(--accent-focus)] cursor-not-allowed opacity-70"
            />
            <button disabled className="absolute right-2 w-8 h-8 flex items-center justify-center rounded-[4px] text-[var(--ink-tertiary)] hover:bg-[var(--data-1)] cursor-not-allowed">
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="text-center mt-2">
            <span className="text-[10px] font-mono text-[var(--ink-tertiary)]">Responses are AI-generated. Verify all claims against cryptographic ledger.</span>
          </div>
        </div>

      </div>
    </PageTransition>
  );
}
