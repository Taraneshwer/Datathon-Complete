export * from '../lib/api-client-types';
import {
  District, HotspotPoint, Victim,
  GraphNode, GraphEdge, BehavioralPattern, DashboardAnalytics,
  Alert, EvidenceItem, TimelineEvent, BiasAudit, AccessLogEntry, LedgerStatus,
  CaseStatus, AlertSeverity, RiskForecastTrend, EvidenceItemType, TimelineEventType,
  GraphNodeType, AccessLogEntryVerificationStatus, LedgerStatusState, BiasDisparitySeverity
} from '../lib/api-client-types';
import type { PoliceCase, PoliceSuspect } from '../types/police';

// Placeholder data scaffold for backend integration.
// Replace these records with API responses without changing component code.

const placeholderDistricts: District[] = [
  { id: 'district-001', name: 'District Placeholder 01', lat: 0, lng: 0, crimeCount: 0, riskLevel: 0, patrolCoverage: 0, population: 0 },
  { id: 'district-002', name: 'District Placeholder 02', lat: 0, lng: 0, crimeCount: 0, riskLevel: 0, patrolCoverage: 0, population: 0 },
  { id: 'district-003', name: 'District Placeholder 03', lat: 0, lng: 0, crimeCount: 0, riskLevel: 0, patrolCoverage: 0, population: 0 },
];

export const mockDistricts: District[] = placeholderDistricts;

export const mockCases: PoliceCase[] = [
  {
    id: 'case-001',
    title: 'Case Placeholder 001',
    status: CaseStatus.open,
    districtId: 'district-001',
    districtName: 'District Placeholder 01',
    crimeType: 'Pending classification',
    openedAt: '1970-01-01T00:00:00Z',
    officerInCharge: 'Officer Placeholder',
    suspectIds: [],
    victimIds: [],
    patternId: 'pattern-001',
    confidence: 0,
    evidenceCount: 0,
    linkedCaseIds: [],
    summary: 'Backend data will populate this case record.',
    firNumber: 'FIR-000000',
    ipcSections: [],
    policeStation: 'Station Placeholder',
    beatNumber: 'Beat 00',
    priority: 'serious',
    chargeSheetFiled: false,
    arrestCount: 0,
  },
  {
    id: 'case-002',
    title: 'Case Placeholder 002',
    status: CaseStatus.under_review,
    districtId: 'district-002',
    districtName: 'District Placeholder 02',
    crimeType: 'Pending classification',
    openedAt: '1970-01-01T00:00:00Z',
    officerInCharge: 'Officer Placeholder',
    suspectIds: [],
    victimIds: [],
    patternId: 'pattern-002',
    confidence: 0,
    evidenceCount: 0,
    linkedCaseIds: [],
    summary: 'Backend data will populate this case record.',
    firNumber: 'FIR-000001',
    ipcSections: [],
    policeStation: 'Station Placeholder',
    beatNumber: 'Beat 00',
    priority: 'serious',
    chargeSheetFiled: false,
    arrestCount: 0,
  },
];

export const mockSuspects: PoliceSuspect[] = [
  {
    id: 'suspect-001',
    name: 'Suspect Placeholder 01',
    alias: 'SP-01',
    age: 0,
    caseIds: ['case-001'],
    districtId: 'district-001',
    riskScore: 0,
    moSummary: 'Backend data will populate suspect details.',
    lastSeenAt: '1970-01-01T00:00:00Z',
    priorConvictions: 0,
    bailStatus: 'unknown',
    occupation: 'Pending',
    address: 'Pending',
    height: 'Pending',
  },
];

export const mockVictims: Victim[] = [
  { id: 'victim-001', initials: 'V.P.', age: 0, caseIds: ['case-001'], districtId: 'district-001' },
];

export const mockPatterns: BehavioralPattern[] = [
  {
    id: 'pattern-001',
    label: 'Pattern Placeholder',
    description: 'Backend data will populate pattern insights.',
    confidence: 0,
    caseCount: 0,
    matchedCaseIds: [],
    sparkline: [0, 0, 0, 0, 0, 0],
    districtIds: ['district-001'],
  },
];

export const mockHotspots: HotspotPoint[] = [];

export const mockNodes: GraphNode[] = [
  { id: 'case-001', type: GraphNodeType.case, label: 'Case Placeholder', x: 0, y: 0, timeIndex: 0 },
  { id: 'suspect-001', type: GraphNodeType.suspect, label: 'Suspect Placeholder', x: 0, y: 0, timeIndex: 0 },
];

export const mockEdges: GraphEdge[] = [
  { id: 'edge-001', source: 'case-001', target: 'suspect-001', label: 'Pending', timeIndex: 0 },
];

export const mockAlerts: Alert[] = [
  {
    id: 'alert-001',
    title: 'Alert Placeholder',
    districtId: 'district-001',
    districtName: 'District Placeholder 01',
    severity: AlertSeverity.medium,
    timestamp: new Date().toISOString(),
    read: false,
    message: 'Backend data will populate alert content.',
    linkedCaseIds: ['case-001'],
  },
];

export const mockTimeline: TimelineEvent[] = [
  {
    id: 'timeline-001',
    caseId: 'case-001',
    timestamp: new Date().toISOString(),
    title: 'Timeline Placeholder',
    description: 'Backend data will populate the timeline.',
    type: TimelineEventType.update,
  },
];

export const mockEvidence: EvidenceItem[] = [
  {
    id: 'evidence-001',
    caseId: 'case-001',
    type: EvidenceItemType.document,
    label: 'Evidence Placeholder',
    timestamp: new Date().toISOString(),
    confidence: 0,
    verified: false,
    notes: 'Backend data will populate evidence details.',
  },
];

export const mockAccessLog: AccessLogEntry[] = [
  {
    id: 'access-001',
    officerId: 'officer-placeholder',
    officerName: 'Officer Placeholder',
    action: 'Pending backend sync',
    timestamp: new Date().toISOString(),
    verificationStatus: AccessLogEntryVerificationStatus.verified,
    blockRef: '0x00000000',
  },
];

export const mockLedgerStatus: LedgerStatus = {
  state: LedgerStatusState.synced,
  blockHeight: 0,
  lastBlockHash: '0x00000000000000000000000000000000',
  lastAnchoredAt: new Date().toISOString(),
};

export const mockBiasAudit: BiasAudit = {
  generatedAt: new Date().toISOString(),
  disparity: {
    detected: false,
    severity: BiasDisparitySeverity.moderate,
    description: 'Bias audit placeholder — backend data will provide the analysis.',
    recommendation: 'Pending backend response.',
  },
  buckets: [],
};

export const mockDashboardAnalytics: DashboardAnalytics = {
  anomalyStats: [
    { label: 'Active Cases', value: 0, delta: 0, isAnomaly: false, unit: 'open' },
    { label: 'Critical Alerts', value: 0, delta: 0, isAnomaly: false },
    { label: 'Anomaly Rate (30d)', value: 0, delta: 0, isAnomaly: false, unit: '%' },
    { label: 'Solved This Month', value: 0, delta: 0, isAnomaly: false },
  ],
  activeCaseCount: 0,
  criticalAlertCount: 0,
  solvedThisMonth: 0,
  riskForecast: [
    { districtId: 'district-001', districtName: 'District Placeholder 01', riskLevel: 0, trend: RiskForecastTrend.flat },
    { districtId: 'district-002', districtName: 'District Placeholder 02', riskLevel: 0, trend: RiskForecastTrend.flat },
    { districtId: 'district-003', districtName: 'District Placeholder 03', riskLevel: 0, trend: RiskForecastTrend.flat },
  ],
};

export const mockCrimeTrend = [
  { month: 'P1', count: 0, avg: 0 },
  { month: 'P2', count: 0, avg: 0 },
  { month: 'P3', count: 0, avg: 0 },
  { month: 'P4', count: 0, avg: 0 },
  { month: 'P5', count: 0, avg: 0 },
  { month: 'P6', count: 0, avg: 0 },
];
