
import { PageHeader, SectionCard, StatusPill } from "@/components/ksp/PageHeader";
import { CRIME_TREND, DISTRICTS } from "@/lib/ksp-data";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, PieChart, Pie, Cell, Legend } from "recharts";

const RES = [
  { name: "Chargesheeted", value: 62 },
  { name: "Investigating", value: 24 },
  { name: "Pending",       value: 9 },
  { name: "Closed",        value: 5 },
];
const COLORS = ["#0B1F3A", "#C9A227", "#A68B5B", "#94a3b8"];

const AGING = [
  { bucket: "<7 d",  cases: 210 },
  { bucket: "7–30 d", cases: 340 },
  { bucket: "30–90 d", cases: 180 },
  { bucket: ">90 d", cases: 62 },
];

export function Analytics() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Strategic Analytics"
        title="Command Analytics"
        description="Crime trends, district comparison, officer performance and resource allocation."
        actions={<StatusPill tone="info">Q4 FY25/26</StatusPill>}
      />

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-12 lg:col-span-8">
          <SectionCard title="Crime trends · 12 month">
            <div className="h-[300px]">
              <ResponsiveContainer>
                <LineChart data={CRIME_TREND} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 4" stroke="#e5e7eb" />
                  <XAxis dataKey="m" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line dataKey="ipc" stroke="#0B1F3A" strokeWidth={2} dot={false} />
                  <Line dataKey="cyber" stroke="#C9A227" strokeWidth={2} dot={false} />
                  <Line dataKey="econ" stroke="#c0392b" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="col-span-12 lg:col-span-4">
          <SectionCard title="Resolution mix">
            <div className="h-[300px]">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={RES} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2}>
                    {RES.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="col-span-12 lg:col-span-6">
          <SectionCard title="District comparison">
            <div className="h-[280px]">
              <ResponsiveContainer>
                <BarChart data={DISTRICTS} margin={{ top: 10, right: 8, left: -12, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 4" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} interval={0} angle={-15} textAnchor="end" height={50} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 12 }} />
                  <Bar dataKey="cases" fill="#0B1F3A" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="col-span-12 lg:col-span-6">
          <SectionCard title="Case aging">
            <div className="h-[280px]">
              <ResponsiveContainer>
                <BarChart data={AGING} margin={{ top: 10, right: 8, left: -12, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 4" stroke="#e5e7eb" />
                  <XAxis dataKey="bucket" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 12 }} />
                  <Bar dataKey="cases" fill="#C9A227" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
