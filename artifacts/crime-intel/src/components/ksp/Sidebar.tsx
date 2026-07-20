import { Link, useLocation } from "wouter";
import { useState } from "react";
import { ChevronsLeft, ChevronsRight } from "lucide-react";
import { NAV } from "./nav";
import { KspLogo } from "./KspLogo";

const GROUPS: Array<{ name: string; items: typeof NAV }> = [
  { name: "Command",       items: NAV.filter(n => n.group === "Command") },
  { name: "Intelligence",  items: NAV.filter(n => n.group === "Intelligence") },
  { name: "Investigation", items: NAV.filter(n => n.group === "Investigation") },
  { name: "Security",      items: NAV.filter(n => n.group === "Security") },
  { name: "System",        items: NAV.filter(n => n.group === "System") },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [pathname] = useLocation();

  return (
    <aside
      className={`${collapsed ? "w-[68px]" : "w-[248px]"} shrink-0 bg-sidebar text-sidebar-foreground border-r border-sidebar-border flex flex-col transition-[width] duration-200 sticky top-0 h-screen`}
    >
      <div className="h-16 flex items-center gap-3 px-4 border-b border-sidebar-border">
        <KspLogo size={36} />
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-[11px] uppercase tracking-[0.16em] text-gold font-semibold">Karnataka Police</p>
            <p className="text-[12px] text-white/70 truncate">Crime Intelligence OS</p>
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        {GROUPS.map((g) => (
          <div key={g.name}>
            {!collapsed && (
              <p className="px-3 mb-1.5 text-[10px] font-bold uppercase tracking-[0.18em] text-white/40">{g.name}</p>
            )}
            <ul className="space-y-0.5">
              {g.items.map((item) => {
                const active = pathname === item.to;
                const Icon = item.icon;
                return (
                  <li key={item.to}>
                    <Link
                      href={item.to}
                      className={`group flex items-center gap-3 rounded-md px-3 py-2 text-[13px] font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-gold
                        ${active
                          ? "bg-white/5 text-white border-l-2 border-gold pl-[10px]"
                          : "text-white/70 hover:text-white hover:bg-white/5"}`}
                    >
                      <Icon className={`h-[18px] w-[18px] shrink-0 ${active ? "text-gold" : "text-white/60 group-hover:text-white"}`} strokeWidth={2} />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="p-2 border-t border-sidebar-border">
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="w-full flex items-center justify-center gap-2 rounded-md px-3 py-2 text-xs text-white/70 hover:text-white hover:bg-white/5"
        >
          {collapsed ? <ChevronsRight className="h-4 w-4" /> : <><ChevronsLeft className="h-4 w-4" /> Collapse</>}
        </button>
      </div>
    </aside>
  );
}
