/**
 * Shared TypeScript types — mirrors the Django serializers.
 */

export type RiskStatus = "safe" | "unsafe" | "unknown";
export type RiskLevel = "low" | "medium" | "high";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "analyst" | "supervisor";
  role_display: string;
  is_supervisor: boolean;
  institution: string;
  registration_number: string;
}

export interface Hazard {
  id: number;
  code: string;
  code_display: string;
  name: string;
  description: string;
  default_severity: "low" | "medium" | "high";
  severity_display: string;
  pictogram: string;
}

export interface SubstanceListItem {
  id: number;
  name: string;
  formula: string;
  cas_number: string;
  physical_state: string;
  physical_state_display: string;
  hazard_codes: string[];
  is_active: boolean;
}

export interface Substance {
  id: number;
  name: string;
  formula: string;
  cas_number: string;
  description: string;
  physical_state: string;
  physical_state_display: string;
  molar_mass: string | null;
  ph_value: string | null;
  is_acid: boolean;
  is_base: boolean;
  is_water: boolean;
  is_organic_solvent: boolean;
  hazards: Hazard[];
  required_ppe: string[];
  handling_notes: string;
  critical_alerts: string;
  storage_instructions: string;
  storage_incompatibilities: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RuleFinding {
  rule_id: string;
  status: RiskStatus;
  risk_level: RiskLevel;
  reaction_type: string;
  message: string;
  notes: string[];
}

export interface PairResult {
  substance_a_id: number;
  substance_b_id: number;
  substance_a_name: string;
  substance_b_name: string;
  status: RiskStatus;
  risk_level: RiskLevel;
  reaction_type: string;
  message: string;
  sources: string[];
  findings: RuleFinding[];
  record_id: number | null;
}

export interface CompatibilityCheckResult {
  overall_status: RiskStatus;
  overall_risk: RiskLevel;
  overall_message: string;
  required_ppe: string[];
  critical_alerts: string[];
  pairs: PairResult[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
