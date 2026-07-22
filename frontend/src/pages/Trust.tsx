import { PageTransition, StaggerItem } from '../components/Motion';
import { Shield, Lock, FileKey, Database, Link as LinkIcon, CheckCircle2 } from 'lucide-react';
import { useGetLedgerStatus, useListAccessLog } from '@workspace/api-client-react';

import { AccessLogEntryVerificationStatus, LedgerStatusState } from '@workspace/api-client-react';

export function TrustOversight() {
  const { data: ledgerData } = useGetLedgerStatus();
  const { data: logsData } = useListAccessLog({ limit: 10 });

  const ledger = (ledgerData && (ledgerData as any).state) ? ledgerData : { blockHeight: 0, lastBlockHash: '' };
  const logs = Array.isArray(logsData) ? logsData : [];

  return (
    <PageTransition className="space-y-10 max-w-5xl mx-auto">
      <header className="text-center py-8 border-b border-[var(--border-hairline)]">
        <div className="w-12 h-12 mx-auto bg-[var(--data-1)] rounded-full flex items-center justify-center mb-4 text-[var(--trust-chain)]">
          <Shield className="w-6 h-6" />
        </div>
        <h1 className="text-section-header">Identity & Cryptographic Oversight</h1>
        <p className="text-body text-[var(--ink-secondary)] mt-2 max-w-2xl mx-auto">
          Every read, write, and query within CIPA is bound to a Decentralized Identifier (DID) and anchored to a tamper-evident distributed ledger.
        </p>
      </header>

      {/* Architecture Diagram */}
      <StaggerItem>
        <div className="card-base p-8 relative overflow-hidden bg-white">
          <h3 className="text-[11px] font-mono uppercase tracking-wider text-[var(--ink-tertiary)] mb-8 text-center">Chain of Custody Flow</h3>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-0 relative z-10">

            <div className="flex flex-col items-center text-center w-40">
              <div className="w-12 h-12 rounded-[8px] border border-[var(--trust-chain)] bg-white flex items-center justify-center mb-3">
                <FileKey className="w-5 h-5 text-[var(--trust-chain)]" />
              </div>
              <div className="text-[13px] font-medium">Officer Auth</div>
              <div className="text-[10px] font-mono text-[var(--ink-tertiary)] mt-1">DID Auth Token</div>
            </div>

            <div className="hidden md:block flex-1 h-[1px] bg-gradient-to-r from-[var(--border-hairline)] via-[var(--trust-chain)] to-[var(--border-hairline)] opacity-30 relative">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-2">
                <Lock className="w-3 h-3 text-[var(--ink-tertiary)]" />
              </div>
            </div>

            <div className="flex flex-col items-center text-center w-40">
              <div className="w-12 h-12 rounded-[8px] bg-[var(--trust-chain)] text-white flex items-center justify-center mb-3 shadow-[0_4px_12px_rgba(74,78,84,0.3)]">
                <Database className="w-5 h-5" />
              </div>
              <div className="text-[13px] font-medium">Encrypted Query</div>
              <div className="text-[10px] font-mono text-[var(--ink-tertiary)] mt-1">Zero-Knowledge Proof</div>
            </div>

            <div className="hidden md:block flex-1 h-[1px] bg-[var(--border-hairline)] relative">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[10px] font-mono text-[var(--trust-chain)] bg-white px-2">
                SHA-256 Hash
              </div>
            </div>

            <div className="flex flex-col items-center text-center w-40">
              <div className="w-12 h-12 rounded-[8px] border-[2px] border-[var(--trust-chain)] bg-[var(--bg-canvas)] flex items-center justify-center mb-3">
                <LinkIcon className="w-5 h-5 text-[var(--trust-chain)]" />
              </div>
              <div className="text-[13px] font-medium">Ledger Anchor</div>
              <div className="text-[10px] font-mono text-[var(--ink-tertiary)] mt-1">Immutable Record</div>
            </div>

          </div>
        </div>
      </StaggerItem>

      {/* Ledger Status Bar */}
      <StaggerItem>
        <div className="flex flex-col md:flex-row items-center justify-between p-4 bg-[var(--trust-chain)] text-white rounded-[6px]">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            <span className="font-mono text-[14px]">State Node: Connected & Synced</span>
          </div>
          <div className="flex items-center gap-6 mt-4 md:mt-0 font-mono text-[12px] opacity-80">
            <div>Block Height: {ledger.blockHeight}</div>
            <div>Latest: {ledger.lastBlockHash.substring(0, 16)}...</div>
          </div>
        </div>
      </StaggerItem>

      {/* Access Log */}
      <StaggerItem>
        <div className="card-base p-0">
          <div className="p-5 border-b border-[var(--border-hairline)] flex justify-between items-center bg-[var(--bg-canvas)]">
            <h2 className="text-card-title text-[16px]">Cryptographic Access Log</h2>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border-hairline)]">
                <th className="px-5 py-3 text-[10px] uppercase font-mono text-[var(--ink-tertiary)]">Timestamp</th>
                <th className="px-5 py-3 text-[10px] uppercase font-mono text-[var(--ink-tertiary)]">Identity</th>
                <th className="px-5 py-3 text-[10px] uppercase font-mono text-[var(--ink-tertiary)]">Action</th>
                <th className="px-5 py-3 text-[10px] uppercase font-mono text-[var(--ink-tertiary)]">Verification</th>
                <th className="px-5 py-3 text-[10px] uppercase font-mono text-[var(--ink-tertiary)] text-right">Block Ref</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-[var(--border-hairline)] last:border-0 hover:bg-[var(--data-1)] text-[13px]">
                  <td className="px-5 py-3 font-mono text-[var(--ink-secondary)]">
                    {log.timestamp ? new Date(log.timestamp).toISOString().replace('T', ' ').substring(0, 19) : 'N/A'}
                  </td>
                  <td className="px-5 py-3">
                    <div className="font-medium text-[var(--ink-primary)]">{log.officerName}</div>
                    <div className="font-mono text-[10px] text-[var(--ink-tertiary)]">{log.officerId}</div>
                  </td>
                  <td className="px-5 py-3 text-[var(--ink-secondary)]">{log.action}</td>
                  <td className="px-5 py-3">
                    {log.verificationStatus === AccessLogEntryVerificationStatus.verified ? (
                      <span className="inline-flex items-center gap-1.5 text-[var(--accent-resolved)] font-mono text-[11px]">
                        <Shield className="w-3 h-3" /> Valid
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-[var(--accent-critical)] font-mono text-[11px]">
                        Invalidated
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-right font-mono text-[11px] text-[var(--ink-tertiary)]">
                    {log.blockRef}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </StaggerItem>
    </PageTransition>
  );
}
