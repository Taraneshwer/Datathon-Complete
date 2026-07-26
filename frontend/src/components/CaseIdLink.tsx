import { Link, useLocation } from 'wouter';
import { useIntel } from '../context/IntelContext';
import { ReactNode } from 'react';

interface CaseIdLinkProps {
  id: string;
  className?: string;
  children?: ReactNode;
}

export function CaseIdLink({ id, className = '', children }: CaseIdLinkProps) {
  const { setSelectedCaseId } = useIntel();
  const [, setLocation] = useLocation();

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setSelectedCaseId(id);
    setLocation(`/cases/${id}`);
  };

  return (
    <a 
      href={`/cases/${id}`}
      onClick={handleClick}
      className={`tabular-data hover:text-[var(--accent-focus)] hover:underline decoration-[var(--border-hairline)] underline-offset-4 cursor-pointer transition-colors ${className}`}
    >
      {children || id}
    </a>
  );
}
