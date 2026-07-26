import { Shield } from "lucide-react";

export function KspLogo({ size = 40 }: { size?: number }) {
  return (
    <div
      className="relative flex items-center justify-center rounded-full bg-gradient-to-br from-gold to-khaki text-navy-deep shadow-md"
      style={{ width: size, height: size }}
      aria-label="Karnataka State Police emblem"
    >
      <Shield className="absolute" style={{ width: size * 0.55, height: size * 0.55 }} strokeWidth={2.5} />
      <span
        className="relative font-display font-bold tracking-tight"
        style={{ fontSize: size * 0.28 }}
      >
        KSP
      </span>
    </div>
  );
}
