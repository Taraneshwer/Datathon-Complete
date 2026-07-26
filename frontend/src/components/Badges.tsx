import { CaseStatus, AlertSeverity } from '@/api-client';

export function StatusPill({ status }: { status: CaseStatus }) {
  switch (status) {
    case CaseStatus.open:
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] border border-[var(--accent-critical)] text-[var(--accent-critical)] text-[11px] font-mono uppercase tracking-wider">
          Open
        </span>
      );
    case CaseStatus.under_review:
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] border border-[var(--accent-warning)] text-[var(--accent-warning)] text-[11px] font-mono uppercase tracking-wider">
          Under Review
        </span>
      );
    case CaseStatus.closed:
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-[4px] border border-[var(--accent-resolved)] text-[var(--accent-resolved)] text-[11px] font-mono uppercase tracking-wider">
          Closed
        </span>
      );
    default:
      return null;
  }
}

export function SeverityBadge({ severity }: { severity: AlertSeverity }) {
  const baseClasses = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-mono uppercase tracking-wider border";
  switch (severity) {
    case AlertSeverity.critical:
      return <span className={`${baseClasses} border-[var(--accent-critical)] text-[var(--accent-critical)] bg-red-50`}>Critical</span>;
    case AlertSeverity.high:
      return <span className={`${baseClasses} border-[var(--accent-warning)] text-[var(--accent-warning)] bg-orange-50`}>High</span>;
    case AlertSeverity.medium:
      return <span className={`${baseClasses} border-[var(--accent-focus)] text-[var(--accent-focus)] bg-blue-50`}>Medium</span>;
    case AlertSeverity.low:
      return <span className={`${baseClasses} border-[var(--ink-secondary)] text-[var(--ink-secondary)] bg-gray-50`}>Low</span>;
    default:
      return null;
  }
}
