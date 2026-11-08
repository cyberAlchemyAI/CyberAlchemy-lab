import { digestSfolValue } from "../cases/index.js";

export const NEGATIVE_CONTROL_PROFILE_VERSION =
  "domainspec-sfol-negative-control/v1" as const;

export type NegativeControlSeam =
  | "semantic"
  | "derivation"
  | "binding"
  | "observation"
  | "lineage"
  | "scope"
  | "provider";

export interface FaultModel {
  readonly fault_model_id: string;
  readonly seam: NegativeControlSeam;
  readonly fault: string;
  readonly expected_detector_id: string;
  readonly expected_reason: string;
  readonly required: boolean;
}

export interface NegativeControl {
  readonly control_id: string;
  readonly fault_model_id: string;
  readonly original_digest: string;
  readonly changed_digest: string;
  readonly applicability: "applicable" | "unsupported";
}

export interface NegativeControlObservation {
  readonly control_id: string;
  readonly detector_id: string;
  readonly outcome: "detected" | "not-detected" | "indeterminate";
  readonly reason: string;
}

export interface NegativeControlEvaluationInput {
  readonly profile_version: typeof NEGATIVE_CONTROL_PROFILE_VERSION;
  readonly fault_models: readonly FaultModel[];
  readonly controls: readonly NegativeControl[];
  readonly observations: readonly NegativeControlObservation[];
}

export interface DetectionMatrixRow {
  readonly control_id: string;
  readonly fault_model_id: string;
  readonly seam: NegativeControlSeam;
  readonly required: boolean;
  readonly expected_detector_id: string;
  readonly expected_reason: string;
  readonly observed_detector_id: string;
  readonly observed_reason: string;
  readonly classification:
    | "detected"
    | "survived"
    | "indeterminate"
    | "unsupported"
    | "invalid-control";
}

export interface DetectionMatrixReceipt {
  readonly schema_version: "domainspec-sfol-detection-matrix/v1";
  readonly profile_version: typeof NEGATIVE_CONTROL_PROFILE_VERSION;
  readonly fault_model_set_digest: string;
  readonly control_set_digest: string;
  readonly observation_set_digest: string;
  readonly required_count: number;
  readonly detected_count: number;
  readonly surviving_count: number;
  readonly indeterminate_count: number;
  readonly invalid_control_count: number;
  readonly unsupported_count: number;
  readonly result: "pass" | "fail";
  readonly rows: readonly DetectionMatrixRow[];
  readonly receipt_digest: string;
}

export interface NegativeControlDiagnostic {
  readonly code:
    | "SFOL_NEGATIVE_CONTROL_PROFILE_UNSUPPORTED"
    | "SFOL_NEGATIVE_CONTROL_DUPLICATE_ID"
    | "SFOL_NEGATIVE_CONTROL_FAULT_MODEL_UNAVAILABLE"
    | "SFOL_NEGATIVE_CONTROL_OBSERVATION_MISSING"
    | "SFOL_NEGATIVE_CONTROL_OBSERVATION_EXTRA";
  readonly stage: "negative-control-evaluation";
  readonly subject: string;
  readonly detail: string;
}

export type NegativeControlEvaluationResult =
  | { readonly ok: true; readonly value: DetectionMatrixReceipt }
  | { readonly ok: false; readonly diagnostics: readonly NegativeControlDiagnostic[] };

export function evaluateNegativeControls(
  input: NegativeControlEvaluationInput,
): NegativeControlEvaluationResult {
  const diagnostics: NegativeControlDiagnostic[] = [];
  if (input.profile_version !== NEGATIVE_CONTROL_PROFILE_VERSION) {
    diagnostics.push(diagnostic("SFOL_NEGATIVE_CONTROL_PROFILE_UNSUPPORTED", "profile_version", `expected ${NEGATIVE_CONTROL_PROFILE_VERSION}`));
  }
  collectDuplicates(input.fault_models.map(({ fault_model_id }) => fault_model_id), "fault_model", diagnostics);
  collectDuplicates(input.controls.map(({ control_id }) => control_id), "control", diagnostics);
  collectDuplicates(input.observations.map(({ control_id }) => control_id), "observation", diagnostics);

  const models = new Map(input.fault_models.map((model) => [model.fault_model_id, model]));
  const controls = new Map(input.controls.map((control) => [control.control_id, control]));
  const observations = new Map(input.observations.map((observation) => [observation.control_id, observation]));
  for (const control of input.controls) {
    if (!models.has(control.fault_model_id)) {
      diagnostics.push(diagnostic("SFOL_NEGATIVE_CONTROL_FAULT_MODEL_UNAVAILABLE", control.control_id, `fault model ${control.fault_model_id} is unavailable`));
    }
    if (!observations.has(control.control_id)) {
      diagnostics.push(diagnostic("SFOL_NEGATIVE_CONTROL_OBSERVATION_MISSING", control.control_id, "exactly one observation is required"));
    }
  }
  for (const observation of input.observations) {
    if (!controls.has(observation.control_id)) {
      diagnostics.push(diagnostic("SFOL_NEGATIVE_CONTROL_OBSERVATION_EXTRA", observation.control_id, "observation has no declared negative control"));
    }
  }
  if (diagnostics.length > 0) {
    return Object.freeze({ ok: false, diagnostics: deepFreeze(diagnostics.sort(compareDiagnostics)) });
  }

  const rows = input.controls.map((control): DetectionMatrixRow => {
    const model = models.get(control.fault_model_id)!;
    const observation = observations.get(control.control_id)!;
    const classification =
      control.applicability === "unsupported"
        ? "unsupported"
        : control.original_digest === control.changed_digest
        ? "invalid-control"
        : observation.outcome === "indeterminate"
          ? "indeterminate"
          : observation.outcome === "detected" &&
              observation.detector_id === model.expected_detector_id &&
              observation.reason === model.expected_reason
            ? "detected"
            : "survived";
    return deepFreeze({
      control_id: control.control_id,
      fault_model_id: model.fault_model_id,
      seam: model.seam,
      required: model.required,
      expected_detector_id: model.expected_detector_id,
      expected_reason: model.expected_reason,
      observed_detector_id: observation.detector_id,
      observed_reason: observation.reason,
      classification,
    });
  }).sort((left, right) => left.control_id.localeCompare(right.control_id));
  const requiredRows = rows.filter(({ required }) => required);
  const unsigned = {
    schema_version: "domainspec-sfol-detection-matrix/v1" as const,
    profile_version: input.profile_version,
    fault_model_set_digest: digestSfolValue([...input.fault_models].sort((a, b) => a.fault_model_id.localeCompare(b.fault_model_id))),
    control_set_digest: digestSfolValue([...input.controls].sort((a, b) => a.control_id.localeCompare(b.control_id))),
    observation_set_digest: digestSfolValue([...input.observations].sort((a, b) => a.control_id.localeCompare(b.control_id))),
    required_count: requiredRows.length,
    detected_count: rows.filter(({ classification }) => classification === "detected").length,
    surviving_count: rows.filter(({ classification }) => classification === "survived").length,
    indeterminate_count: rows.filter(({ classification }) => classification === "indeterminate").length,
    invalid_control_count: rows.filter(({ classification }) => classification === "invalid-control").length,
    unsupported_count: rows.filter(({ classification }) => classification === "unsupported").length,
    result: requiredRows.every(({ classification }) => classification === "detected") ? ("pass" as const) : ("fail" as const),
    rows: deepFreeze(rows),
  };
  return Object.freeze({ ok: true, value: deepFreeze({ ...unsigned, receipt_digest: digestSfolValue(unsigned) }) });
}

function collectDuplicates(ids: readonly string[], kind: string, output: NegativeControlDiagnostic[]): void {
  const seen = new Set<string>();
  for (const id of ids) {
    if (seen.has(id)) output.push(diagnostic("SFOL_NEGATIVE_CONTROL_DUPLICATE_ID", id, `duplicate ${kind} identity`));
    seen.add(id);
  }
}

function diagnostic(code: NegativeControlDiagnostic["code"], subject: string, detail: string): NegativeControlDiagnostic {
  return Object.freeze({ code, stage: "negative-control-evaluation", subject, detail });
}

function compareDiagnostics(left: NegativeControlDiagnostic, right: NegativeControlDiagnostic): number {
  return `${left.code}|${left.subject}|${left.detail}`.localeCompare(`${right.code}|${right.subject}|${right.detail}`);
}

function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) deepFreeze(child);
  }
  return value;
}
