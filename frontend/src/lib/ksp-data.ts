import type { MapPoint } from "@/components/ksp/GoogleMap";

export const HOTSPOTS: MapPoint[] = [
  { lat: 12.9716, lng: 77.5946, weight: 3, label: "MG Road · Chain snatching", tone: "critical" },
  { lat: 12.9352, lng: 77.6245, weight: 2, label: "Koramangala · Cyber fraud cluster", tone: "warning" },
  { lat: 13.0298, lng: 77.5710, weight: 2, label: "Malleshwaram · Burglary", tone: "warning" },
  { lat: 12.9081, lng: 77.6476, weight: 3, label: "HSR Layout · Vehicle theft", tone: "critical" },
  { lat: 12.9784, lng: 77.6408, weight: 1, label: "Indiranagar · Public nuisance", tone: "info" },
  { lat: 13.0067, lng: 77.5670, weight: 2, label: "Rajajinagar · Assault", tone: "warning" },
  { lat: 12.9250, lng: 77.5938, weight: 2, label: "Jayanagar · Narcotics tip", tone: "warning" },
  { lat: 12.9915, lng: 77.7383, weight: 3, label: "Whitefield · Cybercrime hub", tone: "critical" },
  { lat: 12.9538, lng: 77.4913, weight: 2, label: "RR Nagar · Property offence", tone: "info" },
  { lat: 13.0475, lng: 77.6208, weight: 1, label: "Hebbal · Traffic incident", tone: "info" },
  { lat: 12.8452, lng: 77.6602, weight: 2, label: "Electronic City · Fraud", tone: "warning" },
  { lat: 12.9698, lng: 77.7500, weight: 2, label: "KR Puram · Chain of custody alert", tone: "warning" },
];

export type Tone = "critical" | "warning" | "info" | "success" | "navy";

export const ALERTS: { id: string; title: string; district: string; time: string; severity: string; tone: Tone }[] = [
  { id: "AL-1029", title: "Interstate vehicle theft ring detected", district: "Bengaluru City", time: "12 min ago", severity: "CRITICAL", tone: "critical" },
  { id: "AL-1028", title: "Cyber phishing wave · Karnataka Bank customers", district: "Mangaluru", time: "24 min ago", severity: "HIGH", tone: "warning" },
  { id: "AL-1027", title: "Suspicious drone activity near Vidhana Soudha", district: "Bengaluru City", time: "42 min ago", severity: "HIGH", tone: "critical" },
  { id: "AL-1026", title: "National advisory · Interstate narcotics route", district: "Belagavi", time: "1 hr ago", severity: "MEDIUM", tone: "info" },
  { id: "AL-1025", title: "Missing person match on facial recognition", district: "Mysuru", time: "2 hr ago", severity: "MEDIUM", tone: "info" },
];

export const RECENT_INCIDENTS: { id: string; category: string; location: string; officer: string; time: string; status: string; tone: Tone }[] = [
  { id: "FIR/2026/00871", category: "Cybercrime · UPI Fraud",   location: "HSR Layout PS",     officer: "SI R. Iyer",    time: "18:42",  status: "Investigating", tone: "warning" },
  { id: "FIR/2026/00870", category: "Theft · Two-wheeler",       location: "Koramangala PS",    officer: "SI M. Deshpande", time: "18:11", status: "New",           tone: "info" },
  { id: "FIR/2026/00869", category: "Assault · Grievous hurt",   location: "Jayanagar PS",      officer: "PI K. Nair",    time: "17:58",  status: "Chargesheet",   tone: "success" },
  { id: "FIR/2026/00868", category: "Narcotics · NDPS Act",      location: "Electronic City PS",officer: "PI S. Gowda",   time: "17:20",  status: "Investigating", tone: "warning" },
  { id: "FIR/2026/00867", category: "Missing Person",            location: "Malleshwaram PS",   officer: "SI P. Kumar",   time: "16:47",  status: "Verified",      tone: "success" },
  { id: "FIR/2026/00866", category: "Cheating · IPC 420",        location: "Whitefield PS",     officer: "SI L. Menon",   time: "16:03",  status: "Escalated",     tone: "critical" },
];

export const CRIME_TREND = [
  { m: "Jan", ipc: 3200, cyber: 720, econ: 410 },
  { m: "Feb", ipc: 3100, cyber: 780, econ: 430 },
  { m: "Mar", ipc: 3350, cyber: 860, econ: 460 },
  { m: "Apr", ipc: 3280, cyber: 910, econ: 480 },
  { m: "May", ipc: 3420, cyber: 970, econ: 520 },
  { m: "Jun", ipc: 3510, cyber: 1050, econ: 540 },
  { m: "Jul", ipc: 3600, cyber: 1120, econ: 580 },
  { m: "Aug", ipc: 3550, cyber: 1180, econ: 610 },
  { m: "Sep", ipc: 3480, cyber: 1240, econ: 640 },
  { m: "Oct", ipc: 3400, cyber: 1310, econ: 660 },
  { m: "Nov", ipc: 3320, cyber: 1380, econ: 690 },
  { m: "Dec", ipc: 3280, cyber: 1420, econ: 710 },
];

export const DISTRICTS = [
  { name: "Bengaluru City", cases: 1287 },
  { name: "Mysuru",         cases: 542 },
  { name: "Mangaluru",      cases: 478 },
  { name: "Hubballi",       cases: 421 },
  { name: "Belagavi",       cases: 389 },
  { name: "Kalaburagi",     cases: 342 },
  { name: "Tumakuru",       cases: 298 },
  { name: "Ballari",        cases: 264 },
];

export const CASES = [
  { id: "KA-2891", title: "Serial two-wheeler theft ring · East Bengaluru", type: "Property", assigned: "PI K. Nair", status: "Investigating", tone: "warning" as Tone, priority: "High",  progress: 62, evidence: 18 },
  { id: "KA-2890", title: "UPI phishing operation targeting senior citizens", type: "Cyber", assigned: "SI R. Iyer", status: "Chargesheet", tone: "success" as Tone, priority: "High", progress: 88, evidence: 26 },
  { id: "KA-2889", title: "Interstate narcotics corridor · NH-48",            type: "Narcotics", assigned: "DySP A. Rao", status: "Investigating", tone: "warning" as Tone, priority: "Critical", progress: 41, evidence: 12 },
  { id: "KA-2888", title: "Corporate embezzlement · Whitefield tech firm",    type: "Economic", assigned: "PI L. Menon", status: "New", tone: "info" as Tone, priority: "Medium",   progress: 12, evidence: 4  },
  { id: "KA-2887", title: "Missing minor · Mysuru rural",                     type: "Missing",  assigned: "SI P. Kumar", status: "Verified", tone: "success" as Tone, priority: "High",   progress: 74, evidence: 9  },
  { id: "KA-2886", title: "Chain snatching pattern · MG Road corridor",       type: "Property", assigned: "SI M. Deshpande", status: "Escalated", tone: "critical" as Tone, priority: "Critical", progress: 35, evidence: 15 },
];

export const REPEAT_OFFENDERS = [
  { name: "Suspect A-441", offences: 7, mo: "Chain snatching · two-wheeler", risk: 91 },
  { name: "Suspect A-317", offences: 5, mo: "UPI phishing · SIM swap",       risk: 82 },
  { name: "Suspect A-208", offences: 4, mo: "Burglary · night entry",         risk: 74 },
  { name: "Suspect A-193", offences: 6, mo: "Vehicle theft · resale racket",  risk: 88 },
  { name: "Suspect A-102", offences: 3, mo: "Narcotics · courier",            risk: 69 },
];

export const TEMPORAL = Array.from({ length: 24 }, (_, h) => ({
  hour: `${String(h).padStart(2, "0")}:00`,
  value: Math.round(20 + 40 * Math.sin((h - 6) / 24 * Math.PI * 2) + Math.random() * 20 + (h >= 20 || h <= 3 ? 30 : 0)),
}));

export const EVIDENCE_ITEMS = [
  { id: "EV-9812", type: "Video",  case: "KA-2886", size: "412 MB", chain: "Verified", tone: "success" as Tone, hash: "0x8f9a…c421" },
  { id: "EV-9811", type: "Image",  case: "KA-2891", size: "3.2 MB", chain: "Verified", tone: "success" as Tone, hash: "0x1cbe…7734" },
  { id: "EV-9810", type: "Audio",  case: "KA-2890", size: "18 MB",  chain: "Pending",  tone: "warning" as Tone, hash: "0xa22e…9910" },
  { id: "EV-9809", type: "Document", case: "KA-2889", size: "1.1 MB", chain: "Verified", tone: "success" as Tone, hash: "0x5d31…441a" },
  { id: "EV-9808", type: "Video",  case: "KA-2888", size: "820 MB", chain: "Anomaly",  tone: "critical" as Tone, hash: "0xffea…0012" },
];

export const LEDGER = Array.from({ length: 10 }, (_, i) => ({
  block: 184920 - i,
  hash: `0x${Math.random().toString(16).slice(2, 10)}…${Math.random().toString(16).slice(2, 6)}`,
  actor: ["SI R. Iyer", "PI K. Nair", "DySP A. Rao", "SI P. Kumar", "PI L. Menon"][i % 5],
  action: ["Evidence hash added", "Case access", "Chain-of-custody transfer", "Signature verified", "Permission update"][i % 5],
  time: `${String(23 - i).padStart(2, "0")}:${String((i * 13) % 60).padStart(2, "0")}:${String((i * 7) % 60).padStart(2, "0")}`,
  ok: i !== 3,
}));

export const NATIONAL_ALERTS = [
  { id: "NAT-771", title: "Interstate gang migration · Maharashtra → Karnataka", cat: "Gang Migration", risk: "High",     tone: "critical" as Tone, lat: 15.85, lng: 74.5 },
  { id: "NAT-770", title: "Cyber attack wave targeting cooperative banks",       cat: "Cyber",          risk: "Critical", tone: "critical" as Tone, lat: 12.97, lng: 77.59 },
  { id: "NAT-769", title: "Drug corridor advisory · NH-48",                      cat: "Narcotics",      risk: "High",     tone: "warning" as Tone,  lat: 13.34, lng: 75.78 },
  { id: "NAT-768", title: "Human trafficking network flagged",                   cat: "Trafficking",    risk: "High",     tone: "warning" as Tone,  lat: 12.29, lng: 76.64 },
  { id: "NAT-767", title: "Cross-border financial fraud ring",                    cat: "Financial",     risk: "Medium",   tone: "info" as Tone,     lat: 15.36, lng: 75.13 },
];
