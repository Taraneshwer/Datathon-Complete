// Core Types and Enums for Crime Intel API

export enum CaseStatus {
  open = 'open',
  under_review = 'under_review',
  closed = 'closed',
}

export enum AlertSeverity {
  critical = 'critical',
  high = 'high',
  medium = 'medium',
  low = 'low',
}

export enum RiskForecastTrend {
  up = 'up',
  down = 'down',
  flat = 'flat',
}

export enum EvidenceItemType {
  forensic = 'forensic',
  video = 'video',
  image = 'image',
  document = 'document',
}

export enum TimelineEventType {
  incident = 'incident',
  update = 'update',
  evidence_collected = 'evidence_collected',
}

export enum GraphNodeType {
  case = 'case',
  suspect = 'suspect',
  victim = 'victim',
  location = 'location',
}

export enum AccessLogEntryVerificationStatus {
  verified = 'verified',
  failed = 'failed',
}

export enum LedgerStatusState {
  synced = 'synced',
  syncing = 'syncing',
  error = 'error',
}

export enum BiasDisparitySeverity {
  low = 'low',
  moderate = 'moderate',
  high = 'high',
  critical = 'critical',
}

// Interfaces
export interface District {
  id: string;
  name: string;
  lat: number;
  lng: number;
  crimeCount: number;
  riskLevel: number;
  patrolCoverage: number;
  population: number;
  isBlindSpot?: boolean;
  blindSpotReason?: string;
}

export interface HotspotPoint {
  id: string;
  lat: number;
  lng: number;
  intensity: number;
  districtId: string;
  crimeType: string;
  timeOfDay: number;
  isAnomaly: boolean;
  stationName: string;
}

export interface CaseDetail {
  id: string;
  title: string;
  status: CaseStatus;
  districtId: string;
  districtName: string;
  crimeType: string;
  openedAt: string;
  closedAt?: string;
  officerInCharge: string;
  suspectIds?: string[];
  victimIds?: string[];
  patternId?: string;
  confidence: number;
  evidenceCount: number;
  linkedCaseIds?: string[];
  summary: string;
  firNumber: string;
  ipcSections: string[];
  policeStation: string;
  beatNumber: string;
  priority: 'minor' | 'serious' | 'heinous';
  chargeSheetFiled: boolean;
  chargeSheetDate?: string;
  arrestCount: number;
}

export interface Suspect {
  id: string;
  name: string;
  alias?: string;
  age: number;
  caseIds: string[];
  districtId: string;
  riskScore: number;
  moSummary: string;
  lastSeenAt: string;
  priorConvictions: number;
  bailStatus: string;
  occupation?: string;
  address?: string;
  height?: string;
  identifyingMarks?: string;
}

export interface Victim {
  id: string;
  initials: string;
  age: number;
  caseIds: string[];
  districtId: string;
}

export interface BehavioralPattern {
  id: string;
  label: string;
  description: string;
  confidence: number;
  caseCount: number;
  matchedCaseIds: string[];
  sparkline: number[];
  districtIds: string[];
}

export interface GraphNode {
  id: string;
  type: GraphNodeType;
  label: string;
  x: number;
  y: number;
  timeIndex: number;
  riskScore?: number;
  linkedCaseIds?: string[];
  moSummary?: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  timeIndex: number;
  strength?: number;
}

export interface Alert {
  id: string;
  title: string;
  districtId: string;
  districtName: string;
  severity: AlertSeverity;
  timestamp: string;
  read: boolean;
  message: string;
  linkedCaseIds?: string[];
}

export interface TimelineEvent {
  id: string;
  caseId: string;
  timestamp: string;
  title: string;
  description: string;
  type: TimelineEventType;
  officerId?: string;
  evidenceIds?: string[];
}

export interface EvidenceItem {
  id: string;
  caseId: string;
  type: EvidenceItemType;
  label: string;
  timestamp: string;
  confidence: number;
  verified: boolean;
  notes: string;
}

export interface AccessLogEntry {
  id: string;
  officerId: string;
  officerName: string;
  action: string;
  timestamp: string;
  verificationStatus: AccessLogEntryVerificationStatus;
  blockRef: string;
}

export interface LedgerStatus {
  state: LedgerStatusState;
  blockHeight: number;
  lastBlockHash: string;
  lastAnchoredAt: string;
}

export interface BiasAudit {
  generatedAt: string;
  disparity: {
    detected: boolean;
    severity: BiasDisparitySeverity;
    description: string;
    recommendation: string;
  };
  buckets: Array<{
    label: string;
    closureRate: number;
    resourceAllocation: number;
    caseCount: number;
    flagged?: boolean;
  }>;
}

export interface DashboardAnalytics {
  anomalyStats: Array<{
    label: string;
    value: number;
    delta: number;
    isAnomaly: boolean;
    unit?: string;
  }>;
  activeCaseCount: number;
  criticalAlertCount: number;
  solvedThisMonth: number;
  riskForecast: Array<{
    districtId: string;
    districtName: string;
    riskLevel: number;
    trend: RiskForecastTrend;
  }>;
}

// Params Interfaces
export interface ListCasesParams { [key: string]: any; }
export interface ListHotspotsParams { [key: string]: any; }
export interface ListAlertsParams { [key: string]: any; }
export interface ListAccessLogParams { [key: string]: any; }
export interface ListGraphNodesParams { [key: string]: any; }
export interface ListGraphEdgesParams { [key: string]: any; }
export interface ListSuspectsParams { [key: string]: any; }
export interface ListVictimsParams { [key: string]: any; }
export interface ListPatternsParams { [key: string]: any; }
export interface ListDistrictsParams { [key: string]: any; }
