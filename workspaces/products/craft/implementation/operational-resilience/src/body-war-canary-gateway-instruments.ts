export const GATEWAY_INSTRUMENTS = Object.freeze({
  requests: "orodi_gateway_requests",
  duration: "orodi_gateway_request_duration",
  candidateWeight: "orodi_gateway_candidate_weight",
  candidateFaultActive: "orodi_gateway_candidate_fault_active",
  candidateReferencePresent: "orodi_gateway_candidate_reference_present",
  configGeneration: "orodi_gateway_config_generation",
});

export type Cohort = "stable" | "candidate";
export type Outcome = "good" | "bad";
export type StatusClass = "2xx" | "4xx" | "5xx" | "timeout" | "transport";

export interface RequestMetricAttributes {
  readonly cohort: Cohort;
  readonly outcome: Outcome;
  readonly status_class: StatusClass;
}

const COHORTS = new Set<Cohort>(["stable", "candidate"]);
const OUTCOMES = new Set<Outcome>(["good", "bad"]);
const STATUS_CLASSES = new Set<StatusClass>(["2xx", "4xx", "5xx", "timeout", "transport"]);

export function validateMetricAttributes(value: RequestMetricAttributes): void {
  if (!COHORTS.has(value.cohort) || !OUTCOMES.has(value.outcome) || !STATUS_CLASSES.has(value.status_class)) throw new Error("GATEWAY_METRIC_LABEL_REJECTED");
  if (Object.keys(value).sort().join(",") !== "cohort,outcome,status_class") throw new Error("GATEWAY_METRIC_LABEL_CARDINALITY_REJECTED");
}
