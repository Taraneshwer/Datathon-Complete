export * from '@/api-client';
import {
  District, HotspotPoint, CaseDetail, Suspect, Victim,
  GraphNode, GraphEdge, BehavioralPattern, DashboardAnalytics,
  Alert, EvidenceItem, TimelineEvent, BiasAudit, AccessLogEntry, LedgerStatus,
  CaseStatus, AlertSeverity, RiskForecastTrend, EvidenceItemType, TimelineEventType,
  GraphNodeType, AccessLogEntryVerificationStatus, LedgerStatusState, BiasDisparitySeverity
} from '@/api-client';
import type { PoliceCase, PoliceSuspect } from '../types/police';

// ─────────────────────────────────────────────
// Districts
// ─────────────────────────────────────────────
export const mockDistricts: District[] = [
  { id: 'D01', name: 'Bengaluru Urban', lat: 12.9716, lng: 77.5946, crimeCount: 412, riskLevel: 5, patrolCoverage: 0.85, population: 13608220 },
  { id: 'D02', name: 'Mysuru',          lat: 12.2958, lng: 76.6394, crimeCount: 185, riskLevel: 3, patrolCoverage: 0.65, population: 3001127 },
  { id: 'D03', name: 'Hubballi-Dharwad',lat: 15.3647, lng: 75.1240, crimeCount: 201, riskLevel: 4, patrolCoverage: 0.70, population: 1847023, isBlindSpot: true, blindSpotReason: 'Low reported crime vs high socio-economic risk indicators (unemployment spike +18%).' },
  { id: 'D04', name: 'Mangaluru',       lat: 12.9141, lng: 74.8560, crimeCount: 156, riskLevel: 3, patrolCoverage: 0.75, population: 2089649 },
  { id: 'D05', name: 'Kalaburagi',      lat: 17.3297, lng: 76.8343, crimeCount: 220, riskLevel: 4, patrolCoverage: 0.55, population: 2566326, isBlindSpot: true, blindSpotReason: 'Patrol coverage below 60% threshold in 3 sub-divisions.' },
  { id: 'D06', name: 'Belagavi',        lat: 15.8497, lng: 74.4977, crimeCount: 110, riskLevel: 2, patrolCoverage: 0.60, population: 4779661 },
  { id: 'D07', name: 'Shivamogga',      lat: 13.9299, lng: 75.5681, crimeCount: 95,  riskLevel: 2, patrolCoverage: 0.50, population: 1752753 },
  { id: 'D08', name: 'Tumakuru',        lat: 13.3392, lng: 77.1016, crimeCount: 88,  riskLevel: 2, patrolCoverage: 0.65, population: 2678980 },
];

// ─────────────────────────────────────────────
// Cases (enriched with police fields)
// ─────────────────────────────────────────────
export const mockCases: PoliceCase[] = [
  {
    id: 'KA-2024-00847', title: 'Late Night Forced Entry, Indiranagar',
    status: CaseStatus.open, districtId: 'D01', districtName: 'Bengaluru Urban',
    crimeType: 'Burglary', openedAt: '2024-05-12T08:30:00Z',
    officerInCharge: 'PI R. Sharma', suspectIds: ['S01', 'S02'], victimIds: ['V01'],
    patternId: 'P01', confidence: 0.89, evidenceCount: 4, linkedCaseIds: ['KA-2024-00812'],
    summary: 'Forced entry via rear window. High-value electronics and jewellery taken. Similar MO to recent cases in Koramangala. Latent prints recovered match AFIS entry for S01.',
    firNumber: 'FIR-2024-1089', ipcSections: ['IPC 457', 'IPC 380'],
    policeStation: 'Indiranagar PS', beatNumber: 'Beat 12-A',
    priority: 'serious', chargeSheetFiled: false, arrestCount: 0,
  },
  {
    id: 'KA-2024-00812', title: 'Commercial Break-in, Koramangala',
    status: CaseStatus.under_review, districtId: 'D01', districtName: 'Bengaluru Urban',
    crimeType: 'Burglary', openedAt: '2024-05-02T10:15:00Z',
    officerInCharge: 'PI R. Sharma', suspectIds: ['S01'], patternId: 'P01', confidence: 0.75,
    summary: 'Commercial property entered via skylight. Cash register compromised. CCTV footage inconclusive due to camera obstruction.', evidenceCount: 2,
    firNumber: 'FIR-2024-1042', ipcSections: ['IPC 457', 'IPC 380', 'IPC 411'],
    policeStation: 'Koramangala PS', beatNumber: 'Beat 08-B',
    priority: 'serious', chargeSheetFiled: false, arrestCount: 0,
  },
  {
    id: 'KA-2024-00910', title: 'Financial Fraud Syndicate, Kuvempunagar',
    status: CaseStatus.open, districtId: 'D02', districtName: 'Mysuru',
    crimeType: 'Fraud', openedAt: '2024-06-01T14:20:00Z',
    officerInCharge: 'PSI M. Gowda', patternId: 'P03', confidence: 0.92, evidenceCount: 12,
    summary: 'Coordinated phishing attacks targeting elderly citizens. Traced to local IP subnet. Network of 4 accused identified. Total loss: ₹18.6 lakh across 22 victims.',
    firNumber: 'FIR-2024-1201', ipcSections: ['IPC 420', 'IPC 406', 'IT Act 66D'],
    policeStation: 'Kuvempunagar PS', beatNumber: 'Beat 03-C',
    priority: 'heinous', chargeSheetFiled: false, arrestCount: 2,
  },
  {
    id: 'KA-2024-00755', title: 'Assault Outside Pub, MG Road',
    status: CaseStatus.closed, districtId: 'D01', districtName: 'Bengaluru Urban',
    crimeType: 'Assault', openedAt: '2024-04-15T02:10:00Z', closedAt: '2024-05-10T16:00:00Z',
    officerInCharge: 'PI K. Kumar', suspectIds: ['S03'], victimIds: ['V02', 'V03'],
    confidence: 0.99, evidenceCount: 5,
    summary: 'Altercation leading to physical assault. CCTV captured incident. Accused arrested and chargesheeted. Case closed after conviction.',
    firNumber: 'FIR-2024-0921', ipcSections: ['IPC 323', 'IPC 324'],
    policeStation: 'Brigade Road PS', beatNumber: 'Beat 05-A',
    priority: 'minor', chargeSheetFiled: true, chargeSheetDate: '2024-05-08T00:00:00Z', arrestCount: 1,
  },
  {
    id: 'KA-2024-00963', title: 'Vehicle Theft Ring, Yeshwanthpur',
    status: CaseStatus.open, districtId: 'D01', districtName: 'Bengaluru Urban',
    crimeType: 'Vehicle Theft', openedAt: '2024-06-15T09:00:00Z',
    officerInCharge: 'PSI D. Raju', suspectIds: ['S04', 'S05'], confidence: 0.77, evidenceCount: 7,
    summary: 'Organized ring stripping two-wheelers near ISRO Layout. Six vehicles recovered, chassis numbers altered. Tied to chop shop in Tumakuru.',
    firNumber: 'FIR-2024-1312', ipcSections: ['IPC 379', 'IPC 411', 'MV Act 197'],
    policeStation: 'Yeshwanthpur PS', beatNumber: 'Beat 14-D',
    priority: 'serious', chargeSheetFiled: false, arrestCount: 2,
  },
  {
    id: 'KA-2024-00988', title: 'Narcotics Smuggling, Mangaluru Port',
    status: CaseStatus.open, districtId: 'D04', districtName: 'Mangaluru',
    crimeType: 'Narcotics', openedAt: '2024-06-20T18:45:00Z',
    officerInCharge: 'PI S. Kamath', suspectIds: ['S06'], confidence: 0.84, evidenceCount: 9,
    summary: 'Seizure of 12 kg methamphetamine concealed in fish cargo at Old Port. Intelligence from Central NCB tip-off. One accused arrested, two absconding.',
    firNumber: 'FIR-2024-1389', ipcSections: ['NDPS Act 21(c)', 'NDPS Act 29'],
    policeStation: 'Mangaluru Port PS', beatNumber: 'Beat 01-P',
    priority: 'heinous', chargeSheetFiled: false, arrestCount: 1,
  },
  {
    id: 'KA-2024-01012', title: 'Organised Extortion, Kalaburagi',
    status: CaseStatus.under_review, districtId: 'D05', districtName: 'Kalaburagi',
    crimeType: 'Extortion', openedAt: '2024-07-01T11:30:00Z',
    officerInCharge: 'PSI A. Patil', suspectIds: ['S07', 'S08'], confidence: 0.68, evidenceCount: 3,
    summary: 'Threats and extortion targeting local traders. Accused linked to inter-district organised crime syndicate. KCOCA provisions being examined.',
    firNumber: 'FIR-2024-1456', ipcSections: ['IPC 384', 'IPC 506', 'KCOCA'],
    policeStation: 'Kalaburagi Central PS', beatNumber: 'Beat 07-B',
    priority: 'heinous', chargeSheetFiled: false, arrestCount: 0,
  },
];

// ─────────────────────────────────────────────
// Suspects (enriched)
// ─────────────────────────────────────────────
export const mockSuspects: PoliceSuspect[] = [
  {
    id: 'S01', name: 'Arun Kumar', alias: 'AK', age: 34,
    caseIds: ['KA-2024-00847', 'KA-2024-00812'], districtId: 'D01', riskScore: 85,
    moSummary: 'Targets electronics, operates 2–4 AM, uses glass cutters and rope ladders.',
    lastSeenAt: '2024-06-05T22:00:00Z',
    priorConvictions: 2, bailStatus: 'absconding',
    occupation: 'Scrap dealer (front)', address: 'Hennur, Bengaluru',
    height: '5\'9"', identifyingMarks: 'Scar on left forearm',
  },
  {
    id: 'S02', name: 'Syed Ali', alias: 'Bhai', age: 29,
    caseIds: ['KA-2024-00847'], districtId: 'D01', riskScore: 60,
    moSummary: 'Getaway driver, fences stolen goods in neighbouring districts. Known to use stolen vehicles.',
    lastSeenAt: '2024-06-02T18:30:00Z',
    priorConvictions: 1, bailStatus: 'bailed',
    occupation: 'Auto driver', address: 'Shivajinagar, Bengaluru',
    height: '5\'6"',
  },
  {
    id: 'S03', name: 'Prakash Rao', alias: 'PK', age: 41,
    caseIds: ['KA-2024-00755'], districtId: 'D01', riskScore: 40,
    moSummary: 'History of public altercations when intoxicated. No organised crime links.',
    lastSeenAt: '2024-05-10T10:00:00Z',
    priorConvictions: 3, bailStatus: 'acquitted',
    occupation: 'Daily wage labour', address: 'Rajajinagar, Bengaluru',
    height: '5\'7"',
  },
  {
    id: 'S04', name: 'Mohammed Faizal', alias: 'Faizi', age: 26,
    caseIds: ['KA-2024-00963'], districtId: 'D01', riskScore: 72,
    moSummary: 'Identifies targets in crowded areas, key finder using bent wire. Network spans Bengaluru–Tumakuru corridor.',
    lastSeenAt: '2024-06-20T15:00:00Z',
    priorConvictions: 1, bailStatus: 'in_custody',
    occupation: 'Garage mechanic', address: 'Yeshwanthpur, Bengaluru',
    height: '5\'8"', identifyingMarks: 'Tattoo on right shoulder',
  },
  {
    id: 'S05', name: 'Ravi Naik', alias: 'Chotu', age: 31,
    caseIds: ['KA-2024-00963'], districtId: 'D08', riskScore: 65,
    moSummary: 'Operates chop shop. Alters chassis numbers and resells parts inter-state.',
    lastSeenAt: '2024-06-18T09:00:00Z',
    priorConvictions: 0, bailStatus: 'in_custody',
    occupation: 'Spare parts shop owner', address: 'Tumakuru Central',
    height: '5\'5"',
  },
  {
    id: 'S06', name: 'Ismail Kutty', alias: 'Captain', age: 44,
    caseIds: ['KA-2024-00988'], districtId: 'D04', riskScore: 91,
    moSummary: 'Mid-level smuggler with coastal network. Prior NCB record in Kerala. Uses fishing vessels as cover.',
    lastSeenAt: '2024-06-20T18:45:00Z',
    priorConvictions: 1, bailStatus: 'in_custody',
    occupation: 'Fish exporter', address: 'Old Port Road, Mangaluru',
    height: '5\'10"', identifyingMarks: 'Gold tooth, left side',
  },
  {
    id: 'S07', name: 'Basavaraj Patil', alias: 'Boss', age: 52,
    caseIds: ['KA-2024-01012'], districtId: 'D05', riskScore: 88,
    moSummary: 'Organiser of extortion network. Sends proxies to deliver threats. Politically connected, requires approval for arrest.',
    lastSeenAt: '2024-07-01T10:00:00Z',
    priorConvictions: 0, bailStatus: 'absconding',
    occupation: 'Contractor (civil works)', address: 'Kalaburagi North',
    height: '5\'11"',
  },
  {
    id: 'S08', name: 'Raju Bidari', alias: 'Raju', age: 38,
    caseIds: ['KA-2024-01012'], districtId: 'D05', riskScore: 74,
    moSummary: 'Collector for extortion ring. Directly approaches victims. Known to carry weapon.',
    lastSeenAt: '2024-07-01T11:00:00Z',
    priorConvictions: 2, bailStatus: 'absconding',
    occupation: 'Unemployed', address: 'Kalaburagi South',
    height: '5\'8"', identifyingMarks: 'Missing left index finger',
  },
];

// ─────────────────────────────────────────────
// Victims
// ─────────────────────────────────────────────
export const mockVictims: Victim[] = [
  { id: 'V01', initials: 'A. N.', age: 45, caseIds: ['KA-2024-00847'], districtId: 'D01' },
  { id: 'V02', initials: 'S. K.', age: 28, caseIds: ['KA-2024-00755'], districtId: 'D01' },
  { id: 'V03', initials: 'R. M.', age: 31, caseIds: ['KA-2024-00755'], districtId: 'D01' },
];

// ─────────────────────────────────────────────
// Patterns
// ─────────────────────────────────────────────
export const mockPatterns: BehavioralPattern[] = [
  {
    id: 'P01', label: 'Urban Tech Burglary',
    description: 'Late-night forced entry into high-income residential areas. Target: portable electronics and jewellery. Entry via rear windows or skylights using glass cutters.',
    confidence: 0.88, caseCount: 14,
    matchedCaseIds: ['KA-2024-00847', 'KA-2024-00812'],
    sparkline: [2, 3, 1, 5, 8, 14], districtIds: ['D01', 'D02'],
  },
  {
    id: 'P02', label: 'Highway Cargo Theft',
    description: 'Intercepting logistics trucks at rural rest stops between 11 PM–3 AM. Suspects pose as traffic police. Targets FMCG and pharma cargo.',
    confidence: 0.72, caseCount: 6,
    matchedCaseIds: [], sparkline: [1, 2, 2, 1, 0, 0], districtIds: ['D08', 'D06'],
  },
  {
    id: 'P03', label: 'Elderly Phishing Ring',
    description: 'Coordinated calls posing as bank officials targeting retirees. Victims directed to share OTPs. Average loss ₹84,000 per victim.',
    confidence: 0.95, caseCount: 28,
    matchedCaseIds: ['KA-2024-00910'], sparkline: [5, 12, 18, 22, 25, 28], districtIds: ['D01', 'D02', 'D04'],
  },
  {
    id: 'P04', label: 'Vehicle Stripping Network',
    description: 'Inter-district ring targeting two-wheelers. Vehicles stripped within 2 hours, parts moved to chop shops outside city limits.',
    confidence: 0.79, caseCount: 9,
    matchedCaseIds: ['KA-2024-00963'], sparkline: [0, 1, 3, 5, 7, 9], districtIds: ['D01', 'D08'],
  },
  {
    id: 'P05', label: 'Coastal Narcotics Smuggling',
    description: 'Use of fishing vessels and cargo containers to move narcotics through Mangaluru and Udupi ports. Linked to Kerala and Goa syndicates.',
    confidence: 0.83, caseCount: 4,
    matchedCaseIds: ['KA-2024-00988'], sparkline: [0, 0, 1, 2, 3, 4], districtIds: ['D04'],
  },
];

// ─────────────────────────────────────────────
// Hotspots
// ─────────────────────────────────────────────
export const mockHotspots: HotspotPoint[] = [];
const generateHotspots = (
  centerLat: number, centerLng: number, count: number,
  dId: string, isAnomalyZone = false
) => {
  const stations = ['Indiranagar PS', 'Koramangala PS', 'Whitefield PS', 'Yelahanka PS', 'Jayanagar PS'];
  for (let i = 0; i < count; i++) {
    mockHotspots.push({
      id: `H${dId}${i}`,
      lat: centerLat + (Math.random() - 0.5) * 0.18,
      lng: centerLng + (Math.random() - 0.5) * 0.18,
      intensity: Math.random() * 0.5 + (isAnomalyZone ? 0.5 : 0.1),
      districtId: dId,
      crimeType: ['Burglary', 'Assault', 'Theft', 'Fraud', 'Vehicle Theft'][Math.floor(Math.random() * 5)],
      timeOfDay: Math.floor(Math.random() * 24),
      isAnomaly: isAnomalyZone && Math.random() > 0.6,
      stationName: stations[Math.floor(Math.random() * stations.length)],
    });
  }
};
generateHotspots(12.9716, 77.5946, 40, 'D01', true);
generateHotspots(12.2958, 76.6394, 18, 'D02', false);
generateHotspots(15.3647, 75.1240, 12, 'D03', true);
generateHotspots(12.9141, 74.8560, 8,  'D04', false);
generateHotspots(17.3297, 76.8343, 10, 'D05', true);

// ─────────────────────────────────────────────
// Knowledge Graph
// ─────────────────────────────────────────────
export const mockNodes: GraphNode[] = [
  { id: 'KA-2024-00847', type: GraphNodeType.case,    label: 'KA-2024-00847',  x: 300, y: 200, timeIndex: 1, linkedCaseIds: ['KA-2024-00812'] },
  { id: 'KA-2024-00812', type: GraphNodeType.case,    label: 'KA-2024-00812',  x: 480, y: 160, timeIndex: 0 },
  { id: 'KA-2024-00963', type: GraphNodeType.case,    label: 'KA-2024-00963',  x: 150, y: 80,  timeIndex: 2 },
  { id: 'S01',           type: GraphNodeType.suspect, label: 'Arun Kumar',     x: 360, y: 330, timeIndex: 1, riskScore: 85, linkedCaseIds: ['KA-2024-00847', 'KA-2024-00812'], moSummary: 'Targets electronics, 2–4 AM, glass cutters.' },
  { id: 'S02',           type: GraphNodeType.suspect, label: 'Syed Ali',       x: 180, y: 300, timeIndex: 1, riskScore: 60, linkedCaseIds: ['KA-2024-00847'] },
  { id: 'S04',           type: GraphNodeType.suspect, label: 'M. Faizal',      x: 100, y: 180, timeIndex: 2, riskScore: 72, linkedCaseIds: ['KA-2024-00963'] },
  { id: 'S05',           type: GraphNodeType.suspect, label: 'Ravi Naik',      x: 60,  y: 80,  timeIndex: 2, riskScore: 65, linkedCaseIds: ['KA-2024-00963'] },
  { id: 'V01',           type: GraphNodeType.victim,  label: 'A. N.',          x: 250, y: 100, timeIndex: 1, linkedCaseIds: ['KA-2024-00847'] },
  { id: 'L01',           type: GraphNodeType.location, label: 'Indiranagar',   x: 180, y: 230, timeIndex: 1 },
  { id: 'L02',           type: GraphNodeType.location, label: 'Koramangala',   x: 480, y: 280, timeIndex: 0 },
  { id: 'L03',           type: GraphNodeType.location, label: 'Yeshwanthpur',  x: 60,  y: 260, timeIndex: 2 },
];

export const mockEdges: GraphEdge[] = [
  { id: 'E01', source: 'KA-2024-00847', target: 'S01',           label: 'Prime Suspect', timeIndex: 1, strength: 0.9 },
  { id: 'E02', source: 'KA-2024-00847', target: 'S02',           label: 'Suspect',       timeIndex: 1, strength: 0.6 },
  { id: 'E03', source: 'KA-2024-00812', target: 'S01',           label: 'Suspect',       timeIndex: 0, strength: 0.7 },
  { id: 'E04', source: 'KA-2024-00847', target: 'V01',           label: 'Victim',        timeIndex: 1 },
  { id: 'E05', source: 'KA-2024-00847', target: 'L01',           label: 'Scene',         timeIndex: 1 },
  { id: 'E06', source: 'KA-2024-00812', target: 'L02',           label: 'Scene',         timeIndex: 0 },
  { id: 'E07', source: 'S01',           target: 'S02',           label: 'Known Associate', timeIndex: 0, strength: 0.8 },
  { id: 'E08', source: 'KA-2024-00847', target: 'KA-2024-00812', label: 'Linked Case',   timeIndex: 1 },
  { id: 'E09', source: 'KA-2024-00963', target: 'S04',           label: 'Prime Suspect', timeIndex: 2, strength: 0.8 },
  { id: 'E10', source: 'KA-2024-00963', target: 'S05',           label: 'Suspect',       timeIndex: 2, strength: 0.6 },
  { id: 'E11', source: 'KA-2024-00963', target: 'L03',           label: 'Scene',         timeIndex: 2 },
  { id: 'E12', source: 'S04',           target: 'S05',           label: 'Co-accused',    timeIndex: 2, strength: 0.7 },
];

// ─────────────────────────────────────────────
// Alerts
// ─────────────────────────────────────────────
export const mockAlerts: Alert[] = [
  {
    id: 'A01', title: 'Pattern Signature Matched — Urban Tech Burglary',
    districtId: 'D01', districtName: 'Bengaluru Urban',
    severity: AlertSeverity.critical, timestamp: new Date(Date.now() - 3600000).toISOString(),
    read: false, message: 'New FIR KA-2024-00847 matches 88% with Pattern P01. Two prior cases with identical MO. Immediate investigation recommended.',
    linkedCaseIds: ['KA-2024-00847'],
  },
  {
    id: 'A02', title: 'Anomaly Spike — Cyber Fraud Mysuru',
    districtId: 'D02', districtName: 'Mysuru',
    severity: AlertSeverity.high, timestamp: new Date(Date.now() - 86400000).toISOString(),
    read: false, message: 'Fraud case count up 45% in 72 hours. Pattern P03 detected in 6 new FIRs. Coordinate with Cyber Crime Cell.',
    linkedCaseIds: ['KA-2024-00910'],
  },
  {
    id: 'A03', title: 'Blind Spot Risk — Hubballi-Dharwad',
    districtId: 'D03', districtName: 'Hubballi-Dharwad',
    severity: AlertSeverity.medium, timestamp: new Date(Date.now() - 172800000).toISOString(),
    read: true, message: 'Divergence between reported crime count and socioeconomic risk index. Recommend proactive patrol in industrial zones.',
  },
  {
    id: 'A04', title: 'Suspect Sighting — Arun Kumar (S01)',
    districtId: 'D01', districtName: 'Bengaluru Urban',
    severity: AlertSeverity.critical, timestamp: new Date(Date.now() - 1800000).toISOString(),
    read: false, message: 'Informant tip: S01 (Arun Kumar, Risk 85) spotted near RT Nagar at 21:30. Absconding since FIR-2024-1089. Deploy nearest patrol unit.',
    linkedCaseIds: ['KA-2024-00847'],
  },
  {
    id: 'A05', title: 'Narcotics Seizure Follow-up — Mangaluru',
    districtId: 'D04', districtName: 'Mangaluru',
    severity: AlertSeverity.high, timestamp: new Date(Date.now() - 7200000).toISOString(),
    read: false, message: 'Two accused in FIR-2024-1389 still absconding. NCB confirms inter-state network. Request inter-district co-ordination.',
    linkedCaseIds: ['KA-2024-00988'],
  },
  {
    id: 'A06', title: 'Patrol Coverage Alert — Kalaburagi Sub-Division',
    districtId: 'D05', districtName: 'Kalaburagi',
    severity: AlertSeverity.medium, timestamp: new Date(Date.now() - 259200000).toISOString(),
    read: true, message: 'Beat 07-B has had no patrol logs for 36 hours. Possible unit shortage. SP notified.',
  },
  {
    id: 'A07', title: 'Vehicle Theft Cluster — Yeshwanthpur',
    districtId: 'D01', districtName: 'Bengaluru Urban',
    severity: AlertSeverity.high, timestamp: new Date(Date.now() - 14400000).toISOString(),
    read: false, message: '3 new two-wheeler thefts in 500m radius within 4 hours. Pattern P04 confidence elevated to 79%. Recommend Beat 14-D night patrol increase.',
    linkedCaseIds: ['KA-2024-00963'],
  },
];

// ─────────────────────────────────────────────
// Timeline & Evidence
// ─────────────────────────────────────────────
export const mockTimeline: TimelineEvent[] = [
  { id: 'T01', caseId: 'KA-2024-00847', timestamp: '2024-05-12T02:15:00Z', title: 'Incident Occurred', description: 'Estimated time of break-in based on alarm logs and neighbour statement.', type: TimelineEventType.incident },
  { id: 'T02', caseId: 'KA-2024-00847', timestamp: '2024-05-12T08:30:00Z', title: 'FIR Registered', description: 'Homeowner reported incident. FIR-2024-1089 registered at Indiranagar PS. Patrol unit 12-A dispatched.', type: TimelineEventType.update, officerId: 'PI R. Sharma' },
  { id: 'T03', caseId: 'KA-2024-00847', timestamp: '2024-05-12T10:00:00Z', title: 'Forensics Collected', description: 'FSL team lifted 3 latent prints from rear window sill. Scene photographed.', type: TimelineEventType.evidence_collected, evidenceIds: ['EV01'] },
  { id: 'T04', caseId: 'KA-2024-00847', timestamp: '2024-05-13T14:20:00Z', title: 'CCTV Footage Secured', description: 'Video from adjacent building shows silver sedan at 02:18. Partial plate: KA-03 M*.', type: TimelineEventType.evidence_collected, evidenceIds: ['EV02'] },
  { id: 'T05', caseId: 'KA-2024-00847', timestamp: '2024-05-15T09:00:00Z', title: 'AFIS Match — S01', description: 'Fingerprint EV01 matched to Arun Kumar (S01) in AFIS database. Look-out circular issued.', type: TimelineEventType.update, officerId: 'PI R. Sharma' },
  { id: 'T06', caseId: 'KA-2024-00847', timestamp: '2024-05-22T16:45:00Z', title: 'Linked to KA-2024-00812', description: 'MO analysis by Pattern Engine links this case to prior Koramangala burglary. Cases consolidated.', type: TimelineEventType.update },
];

export const mockEvidence: EvidenceItem[] = [
  { id: 'EV01', caseId: 'KA-2024-00847', type: EvidenceItemType.forensic, label: 'Latent Fingerprint — Rear Window Sill', timestamp: '2024-05-12T10:00:00Z', confidence: 0.95, verified: true, notes: 'Matches S01 (Arun Kumar) in AFIS. Chain of custody ref: FSL/BLR/2024/0512.' },
  { id: 'EV02', caseId: 'KA-2024-00847', type: EvidenceItemType.video,    label: 'Exterior CCTV — Adjacent Building', timestamp: '2024-05-13T14:20:00Z', confidence: 0.80, verified: true, notes: 'Silver sedan, partial plate KA-03 M*. Exits frame 02:21.' },
  { id: 'EV03', caseId: 'KA-2024-00847', type: EvidenceItemType.image,    label: 'Scene Photographs (18 frames)', timestamp: '2024-05-12T11:00:00Z', confidence: 0.99, verified: true, notes: 'Photographed by Beat 12-A PC. Exhibits 001–018.' },
  { id: 'EV04', caseId: 'KA-2024-00847', type: EvidenceItemType.document, label: 'Victim Statement — A. N.', timestamp: '2024-05-12T09:30:00Z', confidence: 0.90, verified: true, notes: 'Recorded under Sec 161 CrPC. Statement signed.' },
];

// ─────────────────────────────────────────────
// Access Log & Ledger
// ─────────────────────────────────────────────
export const mockAccessLog: AccessLogEntry[] = [
  { id: 'AL01', officerId: 'O-4491', officerName: 'DSP R. Kumar',     action: 'Accessed case KA-2024-00847 evidence EV01',   timestamp: new Date(Date.now() - 1200000).toISOString(),  verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x8f2a9b1c' },
  { id: 'AL02', officerId: 'O-2884', officerName: 'PSI M. Gowda',     action: 'Queried Pattern P03 — Mysuru region filter',   timestamp: new Date(Date.now() - 3600000).toISOString(),  verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x4c9f2e3a' },
  { id: 'AL03', officerId: 'SYS',    officerName: 'SYSTEM',            action: 'Automated anomaly scan — full state',          timestamp: new Date(Date.now() - 7200000).toISOString(),  verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x1a2b3c4d' },
  { id: 'AL04', officerId: 'O-1032', officerName: 'PI K. Kumar',       action: 'Updated case status KA-2024-00755 → Closed',   timestamp: new Date(Date.now() - 86400000).toISOString(), verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x9d3f4a5b' },
  { id: 'AL05', officerId: 'O-3391', officerName: 'PI S. Kamath',      action: 'Accessed suspect S06 full profile',            timestamp: new Date(Date.now() - 10800000).toISOString(), verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x6c1d2e3f' },
  { id: 'AL06', officerId: 'O-7721', officerName: 'DSP T. Nair',       action: 'Exported bias audit report — Q2 2024',         timestamp: new Date(Date.now() - 172800000).toISOString(), verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x2f5a6b7c' },
  { id: 'AL07', officerId: 'O-4491', officerName: 'DSP R. Kumar',      action: 'Accessed Knowledge Graph — P01 filter',        timestamp: new Date(Date.now() - 1800000).toISOString(),  verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x3e4f5a6b' },
  { id: 'AL08', officerId: 'O-9910', officerName: 'PSI A. Patil',      action: 'Registered FIR-2024-1456 in system',           timestamp: new Date(Date.now() - 43200000).toISOString(), verificationStatus: AccessLogEntryVerificationStatus.verified, blockRef: '0x7b8c9d0e' },
];

export const mockLedgerStatus: LedgerStatus = {
  state: LedgerStatusState.synced,
  blockHeight: 48218,
  lastBlockHash: '0x8f2a9b1c4e7d3f2a1b5c8d9e0f1a2b3c',
  lastAnchoredAt: new Date(Date.now() - 45000).toISOString(),
};

// ─────────────────────────────────────────────
// Bias Audit
// ─────────────────────────────────────────────
export const mockBiasAudit: BiasAudit = {
  generatedAt: new Date().toISOString(),
  disparity: {
    detected: true,
    severity: BiasDisparitySeverity.moderate,
    description: 'Patrol allocation in D03 (Hubballi-Dharwad) is 15% below state average despite high baseline risk indicators. Rural Beat coverage consistently below threshold.',
    recommendation: 'Review resource allocation algorithm for non-metro districts. Suggest 12% rebalance from Bengaluru Urban to Tier-2 zones.',
  },
  buckets: [
    { label: 'Metro High-Income', closureRate: 0.72, resourceAllocation: 0.85, caseCount: 450 },
    { label: 'Metro Low-Income',  closureRate: 0.68, resourceAllocation: 0.70, caseCount: 520 },
    { label: 'Tier-2 Urban',      closureRate: 0.65, resourceAllocation: 0.60, caseCount: 380, flagged: true },
    { label: 'Rural/Coastal',     closureRate: 0.58, resourceAllocation: 0.50, caseCount: 210 },
  ],
};

// ─────────────────────────────────────────────
// Dashboard Analytics
// ─────────────────────────────────────────────
export const mockDashboardAnalytics: DashboardAnalytics = {
  anomalyStats: [
    { label: 'Active Cases',             value: 9,    delta: 2,   isAnomaly: false, unit: 'open' },
    { label: 'Critical Alerts',          value: 2,    delta: 1,   isAnomaly: true  },
    { label: 'Anomaly Rate (30d)',        value: 12.4, delta: 3.1, isAnomaly: true,  unit: '%' },
    { label: 'Solved This Month',        value: 3,    delta: -1,  isAnomaly: false },
  ],
  activeCaseCount: 9,
  criticalAlertCount: 4,
  solvedThisMonth: 3,
  riskForecast: [
    { districtId: 'D01', districtName: 'Bengaluru Urban',  riskLevel: 5, trend: RiskForecastTrend.up   },
    { districtId: 'D02', districtName: 'Mysuru',           riskLevel: 3, trend: RiskForecastTrend.up   },
    { districtId: 'D03', districtName: 'Hubballi-Dharwad', riskLevel: 4, trend: RiskForecastTrend.flat },
    { districtId: 'D04', districtName: 'Mangaluru',        riskLevel: 3, trend: RiskForecastTrend.down },
    { districtId: 'D05', districtName: 'Kalaburagi',       riskLevel: 4, trend: RiskForecastTrend.up   },
  ],
};
