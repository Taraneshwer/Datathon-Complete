/**
 * Police-domain extensions on top of the generated API types.
 * These fields are present in the enriched mock data and any real backend
 * that returns them in the same payload shape.
 */
import type { CaseDetail, Suspect } from '@workspace/api-client-react';

export type CasePriority = 'heinous' | 'serious' | 'minor';
export type BailStatus = 'in_custody' | 'bailed' | 'absconding' | 'acquitted';
export type OfficerRank = 'DGP' | 'ADGP' | 'IGP' | 'DIG' | 'SP' | 'ASP' | 'DSP' | 'PI' | 'PSI' | 'ASI' | 'HC' | 'PC';
export type ClearanceLevel = 1 | 2 | 3;

export interface PoliceCase extends CaseDetail {
  firNumber?: string;
  ipcSections?: string[];
  policeStation?: string;
  beatNumber?: string;
  priority?: CasePriority;
  chargeSheetFiled?: boolean;
  chargeSheetDate?: string;
  arrestCount?: number;
}

export interface PoliceSuspect extends Suspect {
  priorConvictions?: number;
  bailStatus?: BailStatus;
  occupation?: string;
  address?: string;
  height?: string;
  identifyingMarks?: string;
  nationalId?: string;
}

export interface LoggedInOfficer {
  id: string;
  name: string;
  rank: OfficerRank;
  badgeNumber: string;
  district: string;
  station: string;
  clearanceLevel: ClearanceLevel;
  avatar?: string;
}

export const CURRENT_OFFICER: LoggedInOfficer = {
  id: 'O-4491',
  name: 'Ravi Kumar',
  rank: 'DSP',
  badgeNumber: 'KA-DSP-4491',
  district: 'Bengaluru Urban',
  station: 'Indiranagar PS',
  clearanceLevel: 3,
};
