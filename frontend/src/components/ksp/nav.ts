import {
  LayoutDashboard, Briefcase, Activity, MapPin, Network, PlayCircle,
  FileSearch, Bot, Scale, ShieldCheck, Radio, Fingerprint, Blocks,
  BarChart3, Settings,
} from "lucide-react";

export type NavItem = {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  group: "Command" | "Intelligence" | "Investigation" | "Security" | "System";
};

export const NAV: NavItem[] = [
  { to: "/",                  label: "Command Dashboard",     icon: LayoutDashboard, group: "Command" },
  { to: "/investigations",    label: "Active Investigations", icon: Briefcase,       group: "Command" },
  { to: "/patterns",          label: "Pattern Intelligence",  icon: Activity,        group: "Intelligence" },
  { to: "/hotspots",          label: "Crime Hotspots",        icon: MapPin,          group: "Intelligence" },
  { to: "/knowledge-graph",   label: "Knowledge Graph",       icon: Network,         group: "Intelligence" },
  { to: "/replay",            label: "Crime Replay",          icon: PlayCircle,      group: "Investigation" },
  { to: "/evidence",          label: "Evidence Center",       icon: FileSearch,      group: "Investigation" },
  { to: "/ai",                label: "Investigative AI",      icon: Bot,             group: "Investigation" },
  { to: "/bias",              label: "Bias Detector",         icon: Scale,           group: "Investigation" },
  { to: "/prevention",        label: "Crime Prevention",      icon: ShieldCheck,     group: "Intelligence" },
  { to: "/national-alerts",   label: "National Early Warning",icon: Radio,           group: "Intelligence" },
  { to: "/identity",          label: "Decentralized Identity",icon: Fingerprint,     group: "Security" },
  { to: "/blockchain",        label: "Blockchain Audit",      icon: Blocks,          group: "Security" },
  { to: "/analytics",         label: "Analytics",             icon: BarChart3,       group: "System" },
  { to: "/settings",          label: "Settings",              icon: Settings,        group: "System" },
];
