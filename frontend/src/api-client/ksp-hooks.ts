import { useQuery } from '@tanstack/react-query';
import { customFetch } from './custom-fetch';

export function useGetNationalAlerts() {
  return useQuery({
    queryKey: ['nationalAlerts'],
    queryFn: () => customFetch<any[]>('/api/alerts/national'),
  });
}

export function useGetBlockchainLedger() {
  return useQuery({
    queryKey: ['blockchainLedger'],
    queryFn: () => customFetch<any[]>('/api/blockchain/ledger'),
  });
}

export function useGetEvidenceCenterItems() {
  return useQuery({
    queryKey: ['evidenceCenterItems'],
    queryFn: () => customFetch<any[]>('/api/evidence/items'),
  });
}

export function useGetInvestigationsCases() {
  return useQuery({
    queryKey: ['investigationsCases'],
    queryFn: () => customFetch<any[]>('/api/investigations/cases'),
  });
}

export function useGetReplayPath() {
  return useQuery({
    queryKey: ['replayPath'],
    queryFn: () => customFetch<any[]>('/api/replay/path'),
  });
}

export function useGetKspGraph() {
  return useQuery({
    queryKey: ['kspGraph'],
    queryFn: () => customFetch<{ nodes: any[]; edges: any[] }>('/api/graph/ksp'),
  });
}

export function useGetIdentityCredentials() {
  return useQuery({
    queryKey: ['identityCredentials'],
    queryFn: () => customFetch<any[]>('/api/identity/credentials'),
  });
}

export function useGetAssistantHistory() {
  return useQuery({
    queryKey: ['assistantHistory'],
    queryFn: () => customFetch<any[]>('/api/assistant/history'),
  });
}

export function useGetAssistantBlocked() {
  return useQuery({
    queryKey: ['assistantBlocked'],
    queryFn: () => customFetch<any[]>('/api/assistant/blocked'),
  });
}
