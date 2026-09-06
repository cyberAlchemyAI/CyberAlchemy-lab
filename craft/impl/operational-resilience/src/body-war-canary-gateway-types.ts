export const GATEWAY_SCHEMA_VERSION = "domainspec.orodi.body-war-canary-gateway-state/v1" as const;

export interface GatewayState {
  readonly schema_version: typeof GATEWAY_SCHEMA_VERSION;
  readonly generation: number;
  readonly stable_target: string;
  readonly candidate_target: string | null;
  readonly stable_weight: 90 | 100;
  readonly candidate_weight: 0 | 10;
  readonly candidate_fault_active: boolean;
  readonly last_transition_at: string;
  readonly authority_effect: "none";
}

export type GatewayControlAction =
  | { readonly kind: "install-candidate"; readonly target: string }
  | { readonly kind: "set-candidate-fault"; readonly active: boolean }
  | { readonly kind: "rollback" };

export type ControlTransition =
  | { readonly status: "applied"; readonly before: GatewayState; readonly after: GatewayState }
  | { readonly status: "conflict"; readonly code: string; readonly state: GatewayState };

export interface RouteDecision {
  readonly sequence: number;
  readonly cohort: "stable" | "candidate";
  readonly target: string;
  readonly action: "forward" | "inject-503";
}

export interface SequenceAudit {
  readonly first_sequence: number;
  readonly last_sequence: number;
  readonly stable_selected: number;
  readonly candidate_selected: number;
  readonly stable_injected_fault_count: 0;
  readonly candidate_injected_fault_count: number;
  readonly forwarded_stable: number;
  readonly forwarded_candidate: number;
  readonly accounting_equal: boolean;
}
