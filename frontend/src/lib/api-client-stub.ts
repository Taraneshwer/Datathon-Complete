// Custom API Client Stub for @workspace/api-client-react

export * from './api-client-types';
import {
  ListCasesParams, ListHotspotsParams, ListAlertsParams,
  ListAccessLogParams, ListGraphNodesParams, ListGraphEdgesParams,
  ListSuspectsParams, ListVictimsParams, ListPatternsParams, ListDistrictsParams
} from './api-client-types';

import { useQuery } from '@tanstack/react-query';
import {
  mockCases, mockDistricts, mockHotspots, mockPatterns, mockNodes, mockEdges,
  mockAlerts, mockTimeline, mockEvidence, mockAccessLog, mockLedgerStatus,
  mockBiasAudit, mockDashboardAnalytics, mockSuspects, mockVictims, mockCrimeTrend
} from '../mockData';

export function useGetDashboardAnalytics() {
  return useQuery({ queryKey: ['dashboardAnalytics'], queryFn: () => mockDashboardAnalytics });
}

export function useGetCrimeTrend() {
  return useQuery({ queryKey: ['crimeTrend'], queryFn: () => mockCrimeTrend });
}

export function useListCases(_params?: ListCasesParams) {
  return useQuery({ queryKey: ['cases', _params], queryFn: () => mockCases });
}

export function useGetCase(id: string) {
  return useQuery({ queryKey: ['case', id], queryFn: () => mockCases.find(c => c.id === id) || mockCases[0] });
}

export function useGetCaseEvidence(id: string) {
  return useQuery({ queryKey: ['caseEvidence', id], queryFn: () => mockEvidence.filter(e => e.caseId === id) });
}

export function useGetCaseTimeline(id: string) {
  return useQuery({ queryKey: ['caseTimeline', id], queryFn: () => mockTimeline.filter(t => t.caseId === id) });
}

export function useListAlerts(_params?: ListAlertsParams) {
  return useQuery({ queryKey: ['alerts', _params], queryFn: () => mockAlerts });
}

export function useListPatterns(_params?: ListPatternsParams) {
  return useQuery({ queryKey: ['patterns', _params], queryFn: () => mockPatterns });
}

export function useListHotspots(_params?: ListHotspotsParams) {
  return useQuery({ queryKey: ['hotspots', _params], queryFn: () => mockHotspots });
}

export function useListDistricts(_params?: ListDistrictsParams) {
  return useQuery({ queryKey: ['districts', _params], queryFn: () => mockDistricts });
}

export function useListGraphNodes(_params?: ListGraphNodesParams) {
  return useQuery({ queryKey: ['graphNodes', _params], queryFn: () => mockNodes });
}

export function useListGraphEdges(_params?: ListGraphEdgesParams) {
  return useQuery({ queryKey: ['graphEdges', _params], queryFn: () => mockEdges });
}

export function useGetBiasAudit() {
  return useQuery({ queryKey: ['biasAudit'], queryFn: () => mockBiasAudit });
}

export function useGetLedgerStatus() {
  return useQuery({ queryKey: ['ledgerStatus'], queryFn: () => mockLedgerStatus });
}

export function useListAccessLog(_params?: ListAccessLogParams) {
  return useQuery({ queryKey: ['accessLog', _params], queryFn: () => mockAccessLog });
}

export function useHealthCheck() {
  return useQuery({ queryKey: ['healthCheck'], queryFn: () => ({ status: 'ok', timestamp: new Date().toISOString() }) });
}

export function useListSuspects(_params?: ListSuspectsParams) {
  return useQuery({ queryKey: ['suspects', _params], queryFn: () => mockSuspects });
}

export function useListVictims(_params?: ListVictimsParams) {
  return useQuery({ queryKey: ['victims', _params], queryFn: () => mockVictims });
}
