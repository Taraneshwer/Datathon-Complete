
import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import ReactFlow, { Background, Controls, MiniMap, type Node, type Edge } from "reactflow";
import "reactflow/dist/style.css";
import { useMemo, useState } from "react";
import { User, Car, Phone, Landmark, Package, DollarSign, MapPin } from "lucide-react";

const NODES: Node[] = [
  { id: "victim",   position: { x: 60, y: 220 },  data: { label: "🧑 Victim · R. Sharma" },     style: nodeStyle("#0B1F3A") },
  { id: "suspect1", position: { x: 340, y: 80 },  data: { label: "🕶 Suspect A-441" },           style: nodeStyle("#c0392b") },
  { id: "suspect2", position: { x: 340, y: 360 }, data: { label: "🕶 Suspect A-317" },           style: nodeStyle("#c0392b") },
  { id: "vehicle",  position: { x: 620, y: 60 },  data: { label: "🏍 KA-05-MH-1234" },          style: nodeStyle("#C9A227") },
  { id: "phone",    position: { x: 620, y: 200 }, data: { label: "📞 +91 98••••2211" },         style: nodeStyle("#C9A227") },
  { id: "weapon",   position: { x: 620, y: 340 }, data: { label: "🔪 Weapon · Machete" },        style: nodeStyle("#A68B5B") },
  { id: "acct",     position: { x: 900, y: 140 }, data: { label: "🏦 Account 47829" },           style: nodeStyle("#1e40af") },
  { id: "loc",      position: { x: 900, y: 300 }, data: { label: "📍 HSR Layout" },              style: nodeStyle("#1e40af") },
  { id: "org",      position: { x: 1140, y: 220 },data: { label: "🏛 Ring · East BLR" },         style: nodeStyle("#0B1F3A") },
];

const EDGES: Edge[] = [
  { id: "e1", source: "victim", target: "suspect1", label: "assaulted by", animated: true },
  { id: "e2", source: "victim", target: "suspect2", label: "identified" },
  { id: "e3", source: "suspect1", target: "vehicle", label: "used" },
  { id: "e4", source: "suspect1", target: "phone", label: "owns" },
  { id: "e5", source: "suspect2", target: "weapon", label: "possessed" },
  { id: "e6", source: "phone", target: "acct", label: "linked" },
  { id: "e7", source: "vehicle", target: "loc", label: "seen at", animated: true },
  { id: "e8", source: "suspect1", target: "org", label: "member of" },
  { id: "e9", source: "suspect2", target: "org", label: "member of" },
];

function nodeStyle(bg: string) {
  return {
    background: bg, color: "white", border: "none", borderRadius: 8, padding: "8px 12px",
    fontSize: 12, fontWeight: 600, boxShadow: "0 4px 12px rgba(11,31,58,0.15)",
  } as const;
}

export function KnowledgeGraphKsp() {
  const [selected, setSelected] = useState<string>("suspect1");
  const nodes = useMemo(() => NODES, []);
  const edges = useMemo(() => EDGES, []);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Link Analysis"
        title="Investigative Knowledge Graph"
        description="Entities, relationships and financial flows across cases — click any node for context."
        actions={<StatusPill tone="info">9 entities · 9 edges</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-9">
          <SectionCard className="p-0">
            <div className="h-[560px] rounded-md overflow-hidden">
              <ReactFlow
                nodes={nodes} edges={edges} fitView
                onNodeClick={(_, n) => setSelected(n.id)}
                proOptions={{ hideAttribution: true }}
              >
                <Background gap={16} color="#e5e7eb" />
                <Controls />
                <MiniMap pannable zoomable maskColor="rgba(11,31,58,0.1)" nodeColor={() => "#0B1F3A"} />
              </ReactFlow>
            </div>
          </SectionCard>
        </div>

        <aside className="col-span-12 lg:col-span-3">
          <SectionCard title="Entity Profile" subtitle="Suspect A-441">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-12 w-12 rounded-full bg-navy-deep text-gold grid place-items-center font-semibold">A441</div>
              <div>
                <p className="text-[13px] font-semibold text-navy-deep">Suspect A-441</p>
                <p className="text-[11px] text-muted-foreground">Male · 34 · Bengaluru</p>
              </div>
            </div>
            <ul className="text-[13px] space-y-1.5">
              <Row icon={User}     label="Aliases"     value="Ravi K., Ravanna" />
              <Row icon={Car}      label="Vehicles"    value="1 (stolen · KA-05)" />
              <Row icon={Phone}    label="Phones"      value="2 traced" />
              <Row icon={Landmark} label="Organization" value="Ring · East BLR" />
              <Row icon={Package}  label="Cases"       value="7 open · 4 closed" />
              <Row icon={DollarSign} label="Fin. flows" value="₹4.2L (12 tx)" />
              <Row icon={MapPin}   label="Last seen"   value="HSR · 22:14" />
            </ul>
            <div className="mt-3 rounded-md bg-critical/10 text-critical p-2.5 text-[11px] font-semibold flex items-center justify-between">
              Risk Score <span className="text-lg font-display">91/100</span>
            </div>
          </SectionCard>
        </aside>
      </div>
    </div>
  );
}

function Row({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <li className="flex items-center justify-between">
      <span className="flex items-center gap-2 text-muted-foreground"><Icon className="h-3.5 w-3.5" />{label}</span>
      <span className="text-navy-deep font-medium">{value}</span>
    </li>
  );
}
