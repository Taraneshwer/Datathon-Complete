import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import ReactFlow, { Background, Controls, MiniMap, type Node, type Edge } from "reactflow";
import "reactflow/dist/style.css";
import { useState } from "react";
import { User, Car, Phone, Landmark, Package, DollarSign, MapPin } from "lucide-react";
import { useGetKspGraph } from "@/api-client";

export function KnowledgeGraphKsp() {
  const [selected, setSelected] = useState<string>("suspect1");
  const graphQuery = useGetKspGraph();
  
  const nodes = ((graphQuery.data as any)?.nodes || []) as Node[];
  const edges = ((graphQuery.data as any)?.edges || []) as Edge[];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Link Analysis"
        title="Investigative Knowledge Graph"
        description="Entities, relationships and financial flows across cases — click any node for context."
        actions={<StatusPill tone="info">{nodes.length} entities · {edges.length} edges</StatusPill>}
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
