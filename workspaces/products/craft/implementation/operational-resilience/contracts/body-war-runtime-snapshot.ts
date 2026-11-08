export const BODY_WAR_RUNTIME_SOURCE_MODE =
  "runtime-receipt-derived-offline-snapshot" as const;
export const BODY_WAR_RUNTIME_EVIDENCE_LANE =
  "candidate-local-prototype" as const;
export const BODY_WAR_RUNTIME_COMPATIBILITY = Object.freeze({
  docker_engine_version: "28.0.1",
  docker_compose_version: "2.33.1",
  platform: "linux/amd64",
} as const);
export const BODY_WAR_RUNTIME_ARTIFACTS = Object.freeze({
  body_war_image_id:
    "sha256:697e9a9ae0af2ae3c664cd6d663cd274d236620e0cdbc13c890258283bdf8ae1",
  prometheus_image_id:
    "sha256:1147c92841726a6fef55fe6124491d6f85480f8de204f7d420304ca5bbd0a8f7",
} as const);

export type PairedRuntimeWindow = Readonly<{
  started_at: string;
  ended_at: string;
  started_monotonic_ms: number;
  ended_monotonic_ms: number;
  duration_ms: number;
}>;

export type RuntimeCohortAccounting = Readonly<{
  good: number;
  bad: number;
  total: number;
}>;

export type RuntimeTelemetryAccounting = Readonly<{
  offered: number;
  queued: number;
  exported: number;
  rejected: number;
  dropped: number;
  pending: number;
  partial_success: number;
}>;

export type BodyWarRuntimeSnapshot = Readonly<{
  schema_version: "domainspec.orodi.body-war-runtime-snapshot/v1";
  snapshot_id: string;
  run_id: string;
  captured_at: string;
  source_mode: typeof BODY_WAR_RUNTIME_SOURCE_MODE;
  evidence_lane: typeof BODY_WAR_RUNTIME_EVIDENCE_LANE;
  runtime_admission: "denied";
  raw_evidence_pack_sha256: string;
  compatibility: typeof BODY_WAR_RUNTIME_COMPATIBILITY;
  artifacts: Readonly<{
    stable_body_war_image_id: string;
    candidate_body_war_image_id: string;
    gateway_image_id: string;
    prometheus_image_id: string;
  }>;
  provenance: Readonly<{
    fault_origin: "experiment-gateway";
    application_bytes_equal: true;
  }>;
  timing: Readonly<{
    fault_window: PairedRuntimeWindow;
    evaluation_window: PairedRuntimeWindow;
    rollback_window: PairedRuntimeWindow;
  }>;
  workload: Readonly<{
    scheduled: number;
    issued: number;
    completed: number;
    classified: number;
    max_in_flight: number;
    p99_issue_lateness_ms: number;
    stable: RuntimeCohortAccounting;
    candidate: RuntimeCohortAccounting;
  }>;
  telemetry: RuntimeTelemetryAccounting;
  decision: Readonly<{
    evaluated_at: string;
    telemetry_complete: true;
    candidate_assessment: "unacceptable";
    decision: "rollback";
  }>;
  observer: Readonly<{
    observed_at: string;
    restoration_verified: true;
    rollback_deadline_met: true;
    stable_image_unchanged: true;
    gateway_status_good_count: 20;
    direct_stable_good_count: 5;
    candidate_reference_denominator: Readonly<{
      gateway_target: null;
      gateway_weight: 0;
      reference_gauge: 0;
      candidate_container: "absent";
      candidate_endpoint: "absent";
    }>;
  }>;
  teardown: Readonly<{
    verified: true;
    verified_at: string;
    runtime_project_residue: Readonly<{
      containers: 0;
      networks: 0;
      volumes: 0;
      endpoints: 0;
    }>;
    declared_preparation_residue: readonly string[];
    evidence_residue_retained: true;
  }>;
  projection_ceiling: Readonly<{
    observation_plane: "product";
    observation_mode: "simulation";
    runtime_admitted_observation_ids: readonly [];
    eligible_control_ids: readonly [];
    runtime_admission: "denied";
    authority_effect: "none";
  }>;
  authority_effect: "none";
}>;

export type BodyWarRuntimeProjectionFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

type BodyWarRuntimeProjectionResultBase = Readonly<{
  schema_version: "domainspec.orodi.body-war-runtime-projection-result/v1";
  projector_id: "domainspec.orodi.body-war-runtime-projector";
  projector_version: "1.0.0-candidate-local";
  evidence_lane: typeof BODY_WAR_RUNTIME_EVIDENCE_LANE;
  projection_id: string;
  snapshot_id: string;
  raw_evidence_pack_sha256: string;
  source_mode: typeof BODY_WAR_RUNTIME_SOURCE_MODE;
  projected_at: string;
  observation_plane: "product";
  observation_mode: "simulation";
  runtime_admitted_observation_ids: readonly [];
  eligible_control_ids: readonly [];
  eligibility_decision: "replay-only";
  runtime_admission: "denied";
  authority_effect: "none";
}>;

export type BodyWarRuntimeProjectionResult =
  | (BodyWarRuntimeProjectionResultBase & Readonly<{
      verdict: "projected";
      observation_id: string;
      findings: readonly [];
    }>)
  | (BodyWarRuntimeProjectionResultBase & Readonly<{
      verdict: "rejected";
      observation_id: null;
      findings: readonly BodyWarRuntimeProjectionFinding[];
    }>);

export type BodyWarRuntimeContractFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

export type BodyWarRuntimeDecodeResult<T> = Readonly<
  | {
      verdict: "pass";
      value: T;
      findings: readonly [];
    }
  | {
      verdict: "reject";
      value: null;
      findings: readonly BodyWarRuntimeContractFinding[];
    }
>;

export type BodyWarRuntimeContractFamily = Readonly<{
  snapshot: BodyWarRuntimeSnapshot;
  projection_result: BodyWarRuntimeProjectionResult;
}>;

type JsonObject = Record<string, unknown>;
type AddFinding = (code: string, path: string, detail: string) => void;
type WindowValues = Readonly<{
  startedAt?: number;
  endedAt?: number;
  startedMonotonic?: number;
  endedMonotonic?: number;
  duration?: number;
  startedAtText?: string;
  endedAtText?: string;
}>;
type CohortValues = Readonly<{
  good?: number;
  bad?: number;
  total?: number;
}>;

const SHA256 = /^[a-f0-9]{64}$/;
const IMAGE_ID = /^sha256:[a-f0-9]{64}$/;
const RFC3339_UTC =
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactObject(
  value: unknown,
  required: readonly string[],
  path: string,
  add: AddFinding,
): JsonObject | null {
  if (!isObject(value)) {
    add("BODY_WAR_RUNTIME_SHAPE_INVALID", path, "expected an object");
    return null;
  }
  const allowed = new Set(required);
  for (const key of required) {
    if (!Object.hasOwn(value, key)) {
      add(
        "BODY_WAR_RUNTIME_REQUIRED_FIELD_MISSING",
        path + "/" + key,
        "required field is absent",
      );
    }
  }
  for (const key of Object.keys(value).sort()) {
    if (!allowed.has(key)) {
      add(
        "BODY_WAR_RUNTIME_UNKNOWN_FIELD",
        path + "/" + key,
        "field is outside the closed contract",
      );
    }
  }
  return value;
}

function literal(
  value: unknown,
  expected: unknown,
  path: string,
  code: string,
  add: AddFinding,
): void {
  if (value !== expected) {
    add(code, path, "expected " + JSON.stringify(expected));
  }
}

function nonEmptyString(
  value: unknown,
  path: string,
  add: AddFinding,
): string | undefined {
  if (typeof value !== "string" || value.length === 0) {
    add("BODY_WAR_RUNTIME_STRING_INVALID", path, "expected a non-empty string");
    return undefined;
  }
  return value;
}

function nonNegativeInteger(
  value: unknown,
  path: string,
  add: AddFinding,
): number | undefined {
  if (!Number.isInteger(value) || (value as number) < 0) {
    add(
      "BODY_WAR_RUNTIME_INTEGER_INVALID",
      path,
      "expected a finite non-negative integer",
    );
    return undefined;
  }
  return value as number;
}

function digest(
  value: unknown,
  path: string,
  add: AddFinding,
): string | undefined {
  if (typeof value !== "string" || !SHA256.test(value)) {
    add(
      "BODY_WAR_RUNTIME_DIGEST_INVALID",
      path,
      "expected a lowercase SHA-256 digest",
    );
    return undefined;
  }
  return value;
}

function imageId(
  value: unknown,
  path: string,
  add: AddFinding,
): string | undefined {
  if (typeof value !== "string" || !IMAGE_ID.test(value)) {
    add(
      "BODY_WAR_RUNTIME_IMAGE_ID_INVALID",
      path,
      "expected a lowercase sha256 image ID",
    );
    return undefined;
  }
  return value;
}

function timestamp(
  value: unknown,
  path: string,
  add: AddFinding,
): number | undefined {
  if (typeof value !== "string" || !RFC3339_UTC.test(value)) {
    add(
      "BODY_WAR_RUNTIME_TIMESTAMP_INVALID",
      path,
      "expected an RFC3339 UTC timestamp with a Z suffix",
    );
    return undefined;
  }
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) {
    add(
      "BODY_WAR_RUNTIME_TIMESTAMP_INVALID",
      path,
      "timestamp is not a real instant",
    );
    return undefined;
  }
  return parsed;
}

function emptyArray(value: unknown, path: string, add: AddFinding): void {
  if (!Array.isArray(value)) {
    add("BODY_WAR_RUNTIME_SHAPE_INVALID", path, "expected an array");
    return;
  }
  if (value.length !== 0) {
    add(
      "BODY_WAR_RUNTIME_ADMISSION_FORGED",
      path,
      "runtime-admitted observations and eligible controls must remain empty",
    );
  }
}

function pairedWindow(
  value: unknown,
  path: string,
  add: AddFinding,
): WindowValues {
  const window = exactObject(value, [
    "started_at",
    "ended_at",
    "started_monotonic_ms",
    "ended_monotonic_ms",
    "duration_ms",
  ], path, add);
  if (window === null) return {};
  const startedAt = timestamp(window.started_at, path + "/started_at", add);
  const endedAt = timestamp(window.ended_at, path + "/ended_at", add);
  const startedMonotonic = nonNegativeInteger(
    window.started_monotonic_ms,
    path + "/started_monotonic_ms",
    add,
  );
  const endedMonotonic = nonNegativeInteger(
    window.ended_monotonic_ms,
    path + "/ended_monotonic_ms",
    add,
  );
  const duration = nonNegativeInteger(
    window.duration_ms,
    path + "/duration_ms",
    add,
  );
  if (
    startedAt !== undefined &&
    endedAt !== undefined &&
    duration !== undefined &&
    endedAt - startedAt !== duration
  ) {
    add(
      "BODY_WAR_RUNTIME_TIME_PAIR_MISMATCH",
      path,
      "UTC duration must equal duration_ms",
    );
  }
  if (
    startedMonotonic !== undefined &&
    endedMonotonic !== undefined &&
    duration !== undefined &&
    endedMonotonic - startedMonotonic !== duration
  ) {
    add(
      "BODY_WAR_RUNTIME_TIME_PAIR_MISMATCH",
      path,
      "monotonic duration must equal duration_ms",
    );
  }
  if (
    (startedAt !== undefined && endedAt !== undefined && endedAt < startedAt) ||
    (startedMonotonic !== undefined &&
      endedMonotonic !== undefined &&
      endedMonotonic < startedMonotonic)
  ) {
    add(
      "BODY_WAR_RUNTIME_TIMESTAMP_ORDER",
      path,
      "window end must not precede its start",
    );
  }
  return {
    startedAt,
    endedAt,
    startedMonotonic,
    endedMonotonic,
    duration,
    startedAtText:
      typeof window.started_at === "string" ? window.started_at : undefined,
    endedAtText:
      typeof window.ended_at === "string" ? window.ended_at : undefined,
  };
}

function cohort(
  value: unknown,
  path: string,
  add: AddFinding,
): CohortValues {
  const accounting = exactObject(value, ["good", "bad", "total"], path, add);
  if (accounting === null) return {};
  const good = nonNegativeInteger(accounting.good, path + "/good", add);
  const bad = nonNegativeInteger(accounting.bad, path + "/bad", add);
  const total = nonNegativeInteger(accounting.total, path + "/total", add);
  if (
    good !== undefined &&
    bad !== undefined &&
    total !== undefined &&
    good + bad !== total
  ) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      path,
      "cohort total must equal good plus bad",
    );
  }
  return { good, bad, total };
}

function telemetryAccounting(
  value: unknown,
  path: string,
  add: AddFinding,
): RuntimeTelemetryAccounting | null {
  const telemetry = exactObject(value, [
    "offered",
    "queued",
    "exported",
    "rejected",
    "dropped",
    "pending",
    "partial_success",
  ], path, add);
  if (telemetry === null) return null;
  const values = {
    offered: nonNegativeInteger(telemetry.offered, path + "/offered", add),
    queued: nonNegativeInteger(telemetry.queued, path + "/queued", add),
    exported: nonNegativeInteger(telemetry.exported, path + "/exported", add),
    rejected: nonNegativeInteger(telemetry.rejected, path + "/rejected", add),
    dropped: nonNegativeInteger(telemetry.dropped, path + "/dropped", add),
    pending: nonNegativeInteger(telemetry.pending, path + "/pending", add),
    partial_success: nonNegativeInteger(
      telemetry.partial_success,
      path + "/partial_success",
      add,
    ),
  };
  if (Object.values(values).some((entry) => entry === undefined)) return null;
  const complete = values as RuntimeTelemetryAccounting;
  if (complete.offered !== complete.queued + complete.rejected) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      path,
      "offered must equal queued plus rejected",
    );
  }
  if (
    complete.queued !==
    complete.exported + complete.dropped + complete.pending
  ) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      path,
      "queued must equal exported plus dropped plus pending",
    );
  }
  if (complete.partial_success > complete.exported) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      path + "/partial_success",
      "partial_success cannot exceed exported",
    );
  }
  return complete;
}

function boundedUniqueStrings(
  value: unknown,
  path: string,
  add: AddFinding,
): void {
  if (!Array.isArray(value)) {
    add("BODY_WAR_RUNTIME_SHAPE_INVALID", path, "expected an array");
    return;
  }
  if (value.length > 8) {
    add(
      "BODY_WAR_RUNTIME_ARRAY_BOUND_EXCEEDED",
      path,
      "at most eight declared preparation residue entries are allowed",
    );
  }
  const strings: string[] = [];
  value.forEach((entry, index) => {
    const valid = nonEmptyString(entry, path + "/" + index, add);
    if (valid !== undefined) strings.push(valid);
  });
  if (new Set(strings).size !== strings.length) {
    add(
      "BODY_WAR_RUNTIME_ARRAY_DUPLICATE",
      path,
      "declared preparation residue entries must be unique",
    );
  }
}

function sortedFindings(
  findings: readonly BodyWarRuntimeContractFinding[],
): readonly BodyWarRuntimeContractFinding[] {
  return [...findings].sort((left, right) => {
    const a = left.path + "\u0000" + left.code + "\u0000" + left.detail;
    const b = right.path + "\u0000" + right.code + "\u0000" + right.detail;
    return a < b ? -1 : a > b ? 1 : 0;
  });
}

function finish<T>(
  value: unknown,
  findings: readonly BodyWarRuntimeContractFinding[],
): BodyWarRuntimeDecodeResult<T> {
  if (findings.length > 0) {
    return Object.freeze({
      verdict: "reject",
      value: null,
      findings: Object.freeze(sortedFindings(findings)),
    });
  }
  return Object.freeze({
    verdict: "pass",
    value: value as T,
    findings: Object.freeze([] as const),
  });
}

export function decodeBodyWarRuntimeSnapshot(
  value: unknown,
): BodyWarRuntimeDecodeResult<BodyWarRuntimeSnapshot> {
  const findings: BodyWarRuntimeContractFinding[] = [];
  const add: AddFinding = (code, path, detail) => {
    findings.push({ code, path, detail });
  };
  const root = exactObject(value, [
    "schema_version",
    "snapshot_id",
    "run_id",
    "captured_at",
    "source_mode",
    "evidence_lane",
    "runtime_admission",
    "raw_evidence_pack_sha256",
    "compatibility",
    "artifacts",
    "provenance",
    "timing",
    "workload",
    "telemetry",
    "decision",
    "observer",
    "teardown",
    "projection_ceiling",
    "authority_effect",
  ], "/snapshot", add);
  if (root === null) return finish(value, findings);

  literal(
    root.schema_version,
    "domainspec.orodi.body-war-runtime-snapshot/v1",
    "/snapshot/schema_version",
    "BODY_WAR_RUNTIME_FIXED_LITERAL",
    add,
  );
  nonEmptyString(root.snapshot_id, "/snapshot/snapshot_id", add);
  nonEmptyString(root.run_id, "/snapshot/run_id", add);
  const capturedAt = timestamp(root.captured_at, "/snapshot/captured_at", add);
  literal(
    root.source_mode,
    BODY_WAR_RUNTIME_SOURCE_MODE,
    "/snapshot/source_mode",
    "BODY_WAR_RUNTIME_SOURCE_MODE_FORGED",
    add,
  );
  literal(
    root.evidence_lane,
    BODY_WAR_RUNTIME_EVIDENCE_LANE,
    "/snapshot/evidence_lane",
    "BODY_WAR_RUNTIME_EVIDENCE_LANE_FORGED",
    add,
  );
  literal(
    root.runtime_admission,
    "denied",
    "/snapshot/runtime_admission",
    "BODY_WAR_RUNTIME_ADMISSION_FORGED",
    add,
  );
  digest(
    root.raw_evidence_pack_sha256,
    "/snapshot/raw_evidence_pack_sha256",
    add,
  );

  const compatibility = exactObject(root.compatibility, [
    "docker_engine_version",
    "docker_compose_version",
    "platform",
  ], "/snapshot/compatibility", add);
  if (compatibility !== null) {
    for (const key of Object.keys(BODY_WAR_RUNTIME_COMPATIBILITY) as Array<
      keyof typeof BODY_WAR_RUNTIME_COMPATIBILITY
    >) {
      literal(
        compatibility[key],
        BODY_WAR_RUNTIME_COMPATIBILITY[key],
        "/snapshot/compatibility/" + key,
        "BODY_WAR_RUNTIME_COMPATIBILITY_MISMATCH",
        add,
      );
    }
  }

  const artifacts = exactObject(root.artifacts, [
    "stable_body_war_image_id",
    "candidate_body_war_image_id",
    "gateway_image_id",
    "prometheus_image_id",
  ], "/snapshot/artifacts", add);
  if (artifacts !== null) {
    const stable = imageId(
      artifacts.stable_body_war_image_id,
      "/snapshot/artifacts/stable_body_war_image_id",
      add,
    );
    const candidate = imageId(
      artifacts.candidate_body_war_image_id,
      "/snapshot/artifacts/candidate_body_war_image_id",
      add,
    );
    imageId(
      artifacts.gateway_image_id,
      "/snapshot/artifacts/gateway_image_id",
      add,
    );
    imageId(
      artifacts.prometheus_image_id,
      "/snapshot/artifacts/prometheus_image_id",
      add,
    );
    literal(
      stable,
      BODY_WAR_RUNTIME_ARTIFACTS.body_war_image_id,
      "/snapshot/artifacts/stable_body_war_image_id",
      "BODY_WAR_RUNTIME_IMAGE_MISMATCH",
      add,
    );
    literal(
      candidate,
      BODY_WAR_RUNTIME_ARTIFACTS.body_war_image_id,
      "/snapshot/artifacts/candidate_body_war_image_id",
      "BODY_WAR_RUNTIME_IMAGE_MISMATCH",
      add,
    );
    literal(
      artifacts.prometheus_image_id,
      BODY_WAR_RUNTIME_ARTIFACTS.prometheus_image_id,
      "/snapshot/artifacts/prometheus_image_id",
      "BODY_WAR_RUNTIME_IMAGE_MISMATCH",
      add,
    );
    if (stable !== undefined && candidate !== undefined && stable !== candidate) {
      add(
        "BODY_WAR_RUNTIME_APPLICATION_BYTES_MISMATCH",
        "/snapshot/artifacts",
        "stable and candidate Body War image IDs must be equal",
      );
    }
  }

  const provenance = exactObject(root.provenance, [
    "fault_origin",
    "application_bytes_equal",
  ], "/snapshot/provenance", add);
  if (provenance !== null) {
    literal(
      provenance.fault_origin,
      "experiment-gateway",
      "/snapshot/provenance/fault_origin",
      "BODY_WAR_RUNTIME_FAULT_ORIGIN_FORGED",
      add,
    );
    literal(
      provenance.application_bytes_equal,
      true,
      "/snapshot/provenance/application_bytes_equal",
      "BODY_WAR_RUNTIME_APPLICATION_BYTES_MISMATCH",
      add,
    );
  }

  const timing = exactObject(root.timing, [
    "fault_window",
    "evaluation_window",
    "rollback_window",
  ], "/snapshot/timing", add);
  const fault = pairedWindow(
    timing?.fault_window,
    "/snapshot/timing/fault_window",
    add,
  );
  const evaluation = pairedWindow(
    timing?.evaluation_window,
    "/snapshot/timing/evaluation_window",
    add,
  );
  const rollback = pairedWindow(
    timing?.rollback_window,
    "/snapshot/timing/rollback_window",
    add,
  );
  if (
    fault.startedAt !== undefined &&
    fault.endedAt !== undefined &&
    evaluation.startedAt !== undefined &&
    evaluation.endedAt !== undefined &&
    (evaluation.startedAt < fault.startedAt ||
      evaluation.endedAt > fault.endedAt)
  ) {
    add(
      "BODY_WAR_RUNTIME_EVALUATION_WINDOW_DRIFT",
      "/snapshot/timing/evaluation_window",
      "evaluation window must be contained by the fault window",
    );
  }
  if (
    fault.endedAt !== undefined &&
    rollback.startedAt !== undefined &&
    rollback.startedAt < fault.endedAt
  ) {
    add(
      "BODY_WAR_RUNTIME_WINDOW_OVERLAP",
      "/snapshot/timing/rollback_window",
      "rollback window must not overlap the fault window",
    );
  }
  if (
    fault.startedMonotonic !== undefined &&
    fault.endedMonotonic !== undefined &&
    evaluation.startedMonotonic !== undefined &&
    evaluation.endedMonotonic !== undefined &&
    (evaluation.startedMonotonic < fault.startedMonotonic ||
      evaluation.endedMonotonic > fault.endedMonotonic)
  ) {
    add(
      "BODY_WAR_RUNTIME_EVALUATION_WINDOW_DRIFT",
      "/snapshot/timing/evaluation_window",
      "monotonic evaluation window must be contained by the fault window",
    );
  }
  if (
    fault.endedMonotonic !== undefined &&
    rollback.startedMonotonic !== undefined &&
    rollback.startedMonotonic < fault.endedMonotonic
  ) {
    add(
      "BODY_WAR_RUNTIME_WINDOW_OVERLAP",
      "/snapshot/timing/rollback_window",
      "monotonic rollback window must not overlap the fault window",
    );
  }

  const workload = exactObject(root.workload, [
    "scheduled",
    "issued",
    "completed",
    "classified",
    "max_in_flight",
    "p99_issue_lateness_ms",
    "stable",
    "candidate",
  ], "/snapshot/workload", add);
  const scheduled = nonNegativeInteger(
    workload?.scheduled,
    "/snapshot/workload/scheduled",
    add,
  );
  const issued = nonNegativeInteger(
    workload?.issued,
    "/snapshot/workload/issued",
    add,
  );
  const completed = nonNegativeInteger(
    workload?.completed,
    "/snapshot/workload/completed",
    add,
  );
  const classified = nonNegativeInteger(
    workload?.classified,
    "/snapshot/workload/classified",
    add,
  );
  const maxInFlight = nonNegativeInteger(
    workload?.max_in_flight,
    "/snapshot/workload/max_in_flight",
    add,
  );
  const p99Lateness = nonNegativeInteger(
    workload?.p99_issue_lateness_ms,
    "/snapshot/workload/p99_issue_lateness_ms",
    add,
  );
  const stable = cohort(workload?.stable, "/snapshot/workload/stable", add);
  const candidate = cohort(
    workload?.candidate,
    "/snapshot/workload/candidate",
    add,
  );
  if (scheduled !== undefined && (scheduled === 0 || scheduled > 900)) {
    add(
      "BODY_WAR_RUNTIME_WORKLOAD_BOUND_EXCEEDED",
      "/snapshot/workload/scheduled",
      "scheduled requests must be between 1 and 900",
    );
  }
  if (maxInFlight !== undefined && maxInFlight > 10) {
    add(
      "BODY_WAR_RUNTIME_WORKLOAD_BOUND_EXCEEDED",
      "/snapshot/workload/max_in_flight",
      "valid observed in-flight requests must not exceed 10",
    );
  }
  if (p99Lateness !== undefined && p99Lateness > 100) {
    add(
      "BODY_WAR_RUNTIME_WORKLOAD_BOUND_EXCEEDED",
      "/snapshot/workload/p99_issue_lateness_ms",
      "p99 issue lateness must not exceed 100 ms",
    );
  }
  if (
    scheduled !== undefined &&
    issued !== undefined &&
    (issued > scheduled || issued * 100 < scheduled * 99)
  ) {
    add(
      "BODY_WAR_RUNTIME_WORKLOAD_INVALID",
      "/snapshot/workload",
      "issued requests must be at least 99 percent and at most all scheduled requests",
    );
  }
  if (
    issued !== undefined &&
    completed !== undefined &&
    issued !== completed
  ) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      "/snapshot/workload",
      "every issued request must complete",
    );
  }
  if (
    completed !== undefined &&
    classified !== undefined &&
    completed !== classified
  ) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      "/snapshot/workload",
      "every completed request must be classified",
    );
  }
  if (
    classified !== undefined &&
    stable.total !== undefined &&
    candidate.total !== undefined &&
    classified !== stable.total + candidate.total
  ) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      "/snapshot/workload",
      "classified requests must equal stable plus candidate totals",
    );
  }

  const telemetry = telemetryAccounting(
    root.telemetry,
    "/snapshot/telemetry",
    add,
  );
  if (
    telemetry !== null &&
    classified !== undefined &&
    telemetry.offered !== classified
  ) {
    add(
      "BODY_WAR_RUNTIME_ACCOUNTING_DRIFT",
      "/snapshot/telemetry/offered",
      "telemetry offered must equal classified workload requests",
    );
  }

  const decision = exactObject(root.decision, [
    "evaluated_at",
    "telemetry_complete",
    "candidate_assessment",
    "decision",
  ], "/snapshot/decision", add);
  const evaluatedAt = timestamp(
    decision?.evaluated_at,
    "/snapshot/decision/evaluated_at",
    add,
  );
  literal(
    decision?.telemetry_complete,
    true,
    "/snapshot/decision/telemetry_complete",
    "BODY_WAR_RUNTIME_DECISION_INVALID",
    add,
  );
  literal(
    decision?.candidate_assessment,
    "unacceptable",
    "/snapshot/decision/candidate_assessment",
    "BODY_WAR_RUNTIME_DECISION_INVALID",
    add,
  );
  literal(
    decision?.decision,
    "rollback",
    "/snapshot/decision/decision",
    "BODY_WAR_RUNTIME_DECISION_INVALID",
    add,
  );
  if (
    evaluation.endedAtText !== undefined &&
    decision?.evaluated_at !== evaluation.endedAtText
  ) {
    add(
      "BODY_WAR_RUNTIME_DECISION_TIME_DRIFT",
      "/snapshot/decision/evaluated_at",
      "decision time must equal the evaluation-window end",
    );
  }
  if (
    candidate.total !== undefined &&
    candidate.bad !== undefined &&
    (candidate.total < 20 || candidate.bad * 100 < candidate.total * 20)
  ) {
    add(
      "BODY_WAR_RUNTIME_DECISION_INVALID",
      "/snapshot/workload/candidate",
      "rollback requires candidate total at least 20 and bad rate at least 20 percent",
    );
  }
  if (
    stable.total !== undefined &&
    stable.bad !== undefined &&
    (stable.total < 180 || stable.bad * 100 > stable.total)
  ) {
    add(
      "BODY_WAR_RUNTIME_DECISION_INVALID",
      "/snapshot/workload/stable",
      "rollback requires stable total at least 180 and bad rate at most 1 percent",
    );
  }

  const observer = exactObject(root.observer, [
    "observed_at",
    "restoration_verified",
    "rollback_deadline_met",
    "stable_image_unchanged",
    "gateway_status_good_count",
    "direct_stable_good_count",
    "candidate_reference_denominator",
  ], "/snapshot/observer", add);
  const observedAt = timestamp(
    observer?.observed_at,
    "/snapshot/observer/observed_at",
    add,
  );
  for (const key of [
    "restoration_verified",
    "rollback_deadline_met",
    "stable_image_unchanged",
  ] as const) {
    literal(
      observer?.[key],
      true,
      "/snapshot/observer/" + key,
      "BODY_WAR_RUNTIME_OBSERVER_INVALID",
      add,
    );
  }
  literal(
    observer?.gateway_status_good_count,
    20,
    "/snapshot/observer/gateway_status_good_count",
    "BODY_WAR_RUNTIME_OBSERVER_INVALID",
    add,
  );
  literal(
    observer?.direct_stable_good_count,
    5,
    "/snapshot/observer/direct_stable_good_count",
    "BODY_WAR_RUNTIME_OBSERVER_INVALID",
    add,
  );
  const denominator = exactObject(
    observer?.candidate_reference_denominator,
    [
      "gateway_target",
      "gateway_weight",
      "reference_gauge",
      "candidate_container",
      "candidate_endpoint",
    ],
    "/snapshot/observer/candidate_reference_denominator",
    add,
  );
  const denominatorExpected = {
    gateway_target: null,
    gateway_weight: 0,
    reference_gauge: 0,
    candidate_container: "absent",
    candidate_endpoint: "absent",
  } as const;
  if (denominator !== null) {
    for (const key of Object.keys(denominatorExpected) as Array<
      keyof typeof denominatorExpected
    >) {
      literal(
        denominator[key],
        denominatorExpected[key],
        "/snapshot/observer/candidate_reference_denominator/" + key,
        "BODY_WAR_RUNTIME_DENOMINATOR_DRIFT",
        add,
      );
    }
  }

  const teardown = exactObject(root.teardown, [
    "verified",
    "verified_at",
    "runtime_project_residue",
    "declared_preparation_residue",
    "evidence_residue_retained",
  ], "/snapshot/teardown", add);
  literal(
    teardown?.verified,
    true,
    "/snapshot/teardown/verified",
    "BODY_WAR_RUNTIME_TEARDOWN_INVALID",
    add,
  );
  const teardownAt = timestamp(
    teardown?.verified_at,
    "/snapshot/teardown/verified_at",
    add,
  );
  const residue = exactObject(teardown?.runtime_project_residue, [
    "containers",
    "networks",
    "volumes",
    "endpoints",
  ], "/snapshot/teardown/runtime_project_residue", add);
  if (residue !== null) {
    for (const key of ["containers", "networks", "volumes", "endpoints"]) {
      literal(
        residue[key],
        0,
        "/snapshot/teardown/runtime_project_residue/" + key,
        "BODY_WAR_RUNTIME_PROJECT_RESIDUE_PRESENT",
        add,
      );
    }
  }
  boundedUniqueStrings(
    teardown?.declared_preparation_residue,
    "/snapshot/teardown/declared_preparation_residue",
    add,
  );
  literal(
    teardown?.evidence_residue_retained,
    true,
    "/snapshot/teardown/evidence_residue_retained",
    "BODY_WAR_RUNTIME_TEARDOWN_INVALID",
    add,
  );

  if (
    evaluatedAt !== undefined &&
    rollback.endedAt !== undefined &&
    rollback.endedAt - evaluatedAt > 20_000
  ) {
    add(
      "BODY_WAR_RUNTIME_ROLLBACK_DEADLINE_EXCEEDED",
      "/snapshot/timing/rollback_window",
      "rollback must complete within 20 seconds of the accepted decision",
    );
  }
  if (
    observedAt !== undefined &&
    rollback.endedAt !== undefined &&
    observedAt < rollback.endedAt
  ) {
    add(
      "BODY_WAR_RUNTIME_TIMESTAMP_ORDER",
      "/snapshot/observer/observed_at",
      "independent observation must follow rollback completion",
    );
  }
  if (
    teardownAt !== undefined &&
    observedAt !== undefined &&
    teardownAt < observedAt
  ) {
    add(
      "BODY_WAR_RUNTIME_TIMESTAMP_ORDER",
      "/snapshot/teardown/verified_at",
      "teardown verification must follow restoration observation",
    );
  }
  const boundedTimes = [
    fault.endedAt,
    evaluation.endedAt,
    rollback.endedAt,
    evaluatedAt,
    observedAt,
    teardownAt,
  ];
  if (
    capturedAt !== undefined &&
    boundedTimes.some(
      (entry) => entry !== undefined && entry > capturedAt,
    )
  ) {
    add(
      "BODY_WAR_RUNTIME_FUTURE_TIMESTAMP",
      "/snapshot/captured_at",
      "no snapshot event may occur after captured_at",
    );
  }

  const ceiling = exactObject(root.projection_ceiling, [
    "observation_plane",
    "observation_mode",
    "runtime_admitted_observation_ids",
    "eligible_control_ids",
    "runtime_admission",
    "authority_effect",
  ], "/snapshot/projection_ceiling", add);
  literal(
    ceiling?.observation_plane,
    "product",
    "/snapshot/projection_ceiling/observation_plane",
    "BODY_WAR_RUNTIME_PROJECTION_CEILING_FORGED",
    add,
  );
  literal(
    ceiling?.observation_mode,
    "simulation",
    "/snapshot/projection_ceiling/observation_mode",
    "BODY_WAR_RUNTIME_PROJECTION_CEILING_FORGED",
    add,
  );
  emptyArray(
    ceiling?.runtime_admitted_observation_ids,
    "/snapshot/projection_ceiling/runtime_admitted_observation_ids",
    add,
  );
  emptyArray(
    ceiling?.eligible_control_ids,
    "/snapshot/projection_ceiling/eligible_control_ids",
    add,
  );
  literal(
    ceiling?.runtime_admission,
    "denied",
    "/snapshot/projection_ceiling/runtime_admission",
    "BODY_WAR_RUNTIME_ADMISSION_FORGED",
    add,
  );
  literal(
    ceiling?.authority_effect,
    "none",
    "/snapshot/projection_ceiling/authority_effect",
    "BODY_WAR_RUNTIME_AUTHORITY_FORGED",
    add,
  );
  literal(
    root.authority_effect,
    "none",
    "/snapshot/authority_effect",
    "BODY_WAR_RUNTIME_AUTHORITY_FORGED",
    add,
  );
  return finish(value, findings);
}

function projectionFindings(
  value: unknown,
  path: string,
  add: AddFinding,
): readonly BodyWarRuntimeProjectionFinding[] {
  if (!Array.isArray(value)) {
    add("BODY_WAR_RUNTIME_SHAPE_INVALID", path, "expected an array");
    return [];
  }
  const decoded: BodyWarRuntimeProjectionFinding[] = [];
  value.forEach((entry, index) => {
    const itemPath = path + "/" + index;
    const finding = exactObject(entry, ["code", "path", "detail"], itemPath, add);
    if (finding === null) return;
    const code = nonEmptyString(finding.code, itemPath + "/code", add);
    const findingPath = nonEmptyString(finding.path, itemPath + "/path", add);
    const detail = nonEmptyString(finding.detail, itemPath + "/detail", add);
    if (
      code !== undefined &&
      !/^[A-Z][A-Z0-9_]+$/.test(code)
    ) {
      add(
        "BODY_WAR_RUNTIME_FINDING_INVALID",
        itemPath + "/code",
        "finding code must use the stable uppercase discriminator format",
      );
    }
    if (
      code !== undefined &&
      findingPath !== undefined &&
      detail !== undefined
    ) {
      decoded.push({ code, path: findingPath, detail });
    }
  });
  const sorted = [...decoded].sort((left, right) => {
    const a = left.path + "\u0000" + left.code + "\u0000" + left.detail;
    const b = right.path + "\u0000" + right.code + "\u0000" + right.detail;
    return a < b ? -1 : a > b ? 1 : 0;
  });
  if (JSON.stringify(decoded) !== JSON.stringify(sorted)) {
    add(
      "BODY_WAR_RUNTIME_FINDINGS_ORDER_INVALID",
      path,
      "projection findings must be sorted by path, code, and detail",
    );
  }
  return decoded;
}

export function decodeBodyWarRuntimeProjectionResult(
  value: unknown,
): BodyWarRuntimeDecodeResult<BodyWarRuntimeProjectionResult> {
  const findings: BodyWarRuntimeContractFinding[] = [];
  const add: AddFinding = (code, path, detail) => {
    findings.push({ code, path, detail });
  };
  const root = exactObject(value, [
    "schema_version",
    "projector_id",
    "projector_version",
    "evidence_lane",
    "projection_id",
    "snapshot_id",
    "raw_evidence_pack_sha256",
    "source_mode",
    "projected_at",
    "verdict",
    "observation_id",
    "observation_plane",
    "observation_mode",
    "runtime_admitted_observation_ids",
    "eligible_control_ids",
    "eligibility_decision",
    "runtime_admission",
    "findings",
    "authority_effect",
  ], "/projection_result", add);
  if (root === null) return finish(value, findings);

  const fixed = {
    schema_version: "domainspec.orodi.body-war-runtime-projection-result/v1",
    projector_id: "domainspec.orodi.body-war-runtime-projector",
    projector_version: "1.0.0-candidate-local",
    evidence_lane: BODY_WAR_RUNTIME_EVIDENCE_LANE,
    source_mode: BODY_WAR_RUNTIME_SOURCE_MODE,
    observation_plane: "product",
    observation_mode: "simulation",
    eligibility_decision: "replay-only",
  } as const;
  for (const key of Object.keys(fixed) as Array<keyof typeof fixed>) {
    literal(
      root[key],
      fixed[key],
      "/projection_result/" + key,
      key === "source_mode"
        ? "BODY_WAR_RUNTIME_SOURCE_MODE_FORGED"
        : "BODY_WAR_RUNTIME_PROJECTION_CEILING_FORGED",
      add,
    );
  }
  nonEmptyString(root.projection_id, "/projection_result/projection_id", add);
  nonEmptyString(root.snapshot_id, "/projection_result/snapshot_id", add);
  digest(
    root.raw_evidence_pack_sha256,
    "/projection_result/raw_evidence_pack_sha256",
    add,
  );
  timestamp(root.projected_at, "/projection_result/projected_at", add);
  if (root.verdict !== "projected" && root.verdict !== "rejected") {
    add(
      "BODY_WAR_RUNTIME_PROJECTION_VERDICT_INVALID",
      "/projection_result/verdict",
      "expected projected or rejected",
    );
  }
  const resultFindings = projectionFindings(
    root.findings,
    "/projection_result/findings",
    add,
  );
  if (root.verdict === "projected") {
    nonEmptyString(
      root.observation_id,
      "/projection_result/observation_id",
      add,
    );
    if (resultFindings.length !== 0) {
      add(
        "BODY_WAR_RUNTIME_PROJECTION_VERDICT_INVALID",
        "/projection_result/findings",
        "a projected result must not contain findings",
      );
    }
  }
  if (root.verdict === "rejected") {
    literal(
      root.observation_id,
      null,
      "/projection_result/observation_id",
      "BODY_WAR_RUNTIME_PROJECTION_VERDICT_INVALID",
      add,
    );
    if (resultFindings.length === 0) {
      add(
        "BODY_WAR_RUNTIME_PROJECTION_VERDICT_INVALID",
        "/projection_result/findings",
        "a rejected result must contain at least one finding",
      );
    }
  }
  emptyArray(
    root.runtime_admitted_observation_ids,
    "/projection_result/runtime_admitted_observation_ids",
    add,
  );
  emptyArray(
    root.eligible_control_ids,
    "/projection_result/eligible_control_ids",
    add,
  );
  literal(
    root.runtime_admission,
    "denied",
    "/projection_result/runtime_admission",
    "BODY_WAR_RUNTIME_ADMISSION_FORGED",
    add,
  );
  literal(
    root.authority_effect,
    "none",
    "/projection_result/authority_effect",
    "BODY_WAR_RUNTIME_AUTHORITY_FORGED",
    add,
  );
  return finish(value, findings);
}

export function decodeBodyWarRuntimeContractFamily(
  snapshotValue: unknown,
  projectionResultValue: unknown,
): BodyWarRuntimeDecodeResult<BodyWarRuntimeContractFamily> {
  const snapshot = decodeBodyWarRuntimeSnapshot(snapshotValue);
  const projection = decodeBodyWarRuntimeProjectionResult(projectionResultValue);
  const findings: BodyWarRuntimeContractFinding[] = [
    ...snapshot.findings,
    ...projection.findings,
  ];
  if (snapshot.verdict === "pass" && projection.verdict === "pass") {
    if (projection.value.snapshot_id !== snapshot.value.snapshot_id) {
      findings.push({
        code: "BODY_WAR_RUNTIME_SNAPSHOT_BINDING_MISMATCH",
        path: "/projection_result/snapshot_id",
        detail: "projection result must bind the decoded snapshot identity",
      });
    }
    if (
      projection.value.raw_evidence_pack_sha256 !==
      snapshot.value.raw_evidence_pack_sha256
    ) {
      findings.push({
        code: "BODY_WAR_RUNTIME_RAW_PACK_BINDING_MISMATCH",
        path: "/projection_result/raw_evidence_pack_sha256",
        detail: "projection result must preserve the snapshot raw-pack digest",
      });
    }
    if (
      Date.parse(projection.value.projected_at) <
      Date.parse(snapshot.value.captured_at)
    ) {
      findings.push({
        code: "BODY_WAR_RUNTIME_TIMESTAMP_ORDER",
        path: "/projection_result/projected_at",
        detail: "projection must not precede snapshot capture",
      });
    }
  }
  if (
    findings.length === 0 &&
    snapshot.verdict === "pass" &&
    projection.verdict === "pass"
  ) {
    return finish({
      snapshot: snapshot.value,
      projection_result: projection.value,
    }, findings);
  }
  return finish(null, findings);
}
