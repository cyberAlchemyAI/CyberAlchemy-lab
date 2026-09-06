import { createHash } from "node:crypto";

import {
  FOUNDATIONAL_CONTROL_IDS,
  type ControlReceipt,
  type EvaluationFinding,
  type OperationalEvaluationBundle,
  type OperationalObservation,
} from "../contracts/operational-evidence.js";
import type {
  LegacyV1NormalizationResult,
  LegacyV1SourceInventory,
  LegacyV1SourceShape,
} from "../contracts/legacy-v1-adapter.js";
import type {
  EvidenceEligibilityFinding,
  EvidenceEligibilityReceipt,
  EvidenceEligibilityResult,
  LegacyV1EligibilityReplayRequest,
  ToolProfileEvidenceEligibilityCandidate,
  ToolProfileEvidenceEligibilityResult,
  ToolProfileEvidenceEligibilityReceipt,
} from "../contracts/evidence-eligibility.js";
import type { ToolEvidenceProfileNormalizationResult } from "../contracts/tool-evidence-profile-replay.js";
import { deriveFoundationalControlSet } from "./derive-foundational-controls.js";
import { decodeOperationalEvaluationBundle } from "./validate-operational-evidence.js";

type JsonRecord = Record<string, unknown>;

const rfc3339Pattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
const sha256Pattern = /^[0-9a-f]{64}$/;
const foundationalSet = new Set<string>(FOUNDATIONAL_CONTROL_IDS);
const zeroTelemetryKeys = Object.freeze([
  "offered", "queued", "exported", "rejected", "dropped", "pending", "partial_success",
] as const);

const isRecord = (value: unknown): value is JsonRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const add = (
  findings: EvidenceEligibilityFinding[],
  code: string,
  path: string,
  detail: string,
): void => {
  findings.push({ code, path, detail });
};

const exactKeys = (
  value: JsonRecord,
  expected: readonly string[],
  path: string,
  findings: EvidenceEligibilityFinding[],
): void => {
  const expectedSet = new Set(expected);
  for (const key of expected) {
    if (!(key in value)) add(findings, "ORODI_ELIGIBILITY_CONTRACT_REQUIRED", path, `missing ${key}`);
  }
  for (const key of Object.keys(value).sort()) {
    if (!expectedSet.has(key)) {
      add(findings, "ORODI_ELIGIBILITY_CONTRACT_CLOSED", `${path}.${key}`, "unexpected field");
    }
  }
};

const orderedFindings = (
  findings: readonly EvidenceEligibilityFinding[],
): readonly EvidenceEligibilityFinding[] => Object.freeze([...findings].sort((a, b) =>
  a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.detail.localeCompare(b.detail)));

const orderedObservations = (
  observations: readonly OperationalObservation[],
): readonly OperationalObservation[] => Object.freeze([...observations].sort((a, b) =>
  a.observation_id.localeCompare(b.observation_id)));

const invalidResult = (
  replayId: string,
  evaluatedAt: string,
  findings: readonly EvidenceEligibilityFinding[],
): EvidenceEligibilityResult => Object.freeze({
  schema_version: "domainspec.orodi.evidence-eligibility-result/v1",
  gate_id: "domainspec.orodi.legacy-v1-evidence-eligibility",
  gate_version: "1.0.0-candidate-local",
  evidence_lane: "candidate-local-prototype",
  replay_id: replayId,
  evaluated_at: evaluatedAt,
  decision: "rejected",
  runtime_admission: "denied",
  replay_observations: Object.freeze([]),
  runtime_admitted_observations: Object.freeze([]),
  eligibility_receipts: Object.freeze([]),
  derived_result: null,
  findings: orderedFindings(findings),
  authority_effect: "none",
});

const validateRequestRoot = (
  input: unknown,
  findings: EvidenceEligibilityFinding[],
): input is LegacyV1EligibilityReplayRequest => {
  if (!isRecord(input)) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", "$", "expected request object");
    return false;
  }
  exactKeys(input, [
    "schema_version", "evidence_lane", "replay_id", "normalizations",
    "evaluation_context", "evaluated_at", "authority_effect",
  ], "$", findings);
  if (input.schema_version !== "domainspec.orodi.eligibility-replay-request/v1") {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_LITERAL", "$.schema_version", "unexpected request schema");
  }
  if (input.evidence_lane !== "candidate-local-prototype") {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_LITERAL", "$.evidence_lane", "unexpected evidence lane");
  }
  if (typeof input.replay_id !== "string" || input.replay_id.length === 0) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_STRING", "$.replay_id", "expected non-empty replay ID");
  }
  if (!Array.isArray(input.normalizations) || input.normalizations.length === 0) {
    add(findings, "ORODI_ELIGIBILITY_NORMALIZATIONS_MISSING", "$.normalizations", "expected at least one normalization result");
  }
  if (!isRecord(input.evaluation_context)) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", "$.evaluation_context", "expected evaluation context object");
  } else {
    exactKeys(input.evaluation_context, ["binding", "controls"], "$.evaluation_context", findings);
    if (!isRecord(input.evaluation_context.binding)) {
      add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", "$.evaluation_context.binding", "expected binding object");
    }
    if (!Array.isArray(input.evaluation_context.controls)) {
      add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", "$.evaluation_context.controls", "expected control array");
    }
  }
  if (typeof input.evaluated_at !== "string" || !rfc3339Pattern.test(input.evaluated_at) ||
      !Number.isFinite(Date.parse(input.evaluated_at))) {
    add(findings, "ORODI_ELIGIBILITY_EVALUATION_TIME_INVALID", "$.evaluated_at", "expected explicit RFC 3339 date-time");
  }
  if (input.authority_effect !== "none") {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_LITERAL", "$.authority_effect", "authority effect must remain none");
  }
  return findings.length === 0;
};

const validateInventory = (
  inventory: unknown,
  findings: EvidenceEligibilityFinding[],
): inventory is LegacyV1SourceInventory => {
  if (!isRecord(inventory)) {
    add(findings, "ORODI_ELIGIBILITY_INVENTORY_INVALID", "$inventory", "expected inventory object");
    return false;
  }
  exactKeys(inventory, [
    "schema_version", "inventory_id", "captured_at", "sources", "claim_ceiling", "authority_effect",
  ], "$inventory", findings);
  if (inventory.schema_version !== "domainspec.orodi.legacy-v1-source-inventory/v1" ||
      inventory.authority_effect !== "none" || !Array.isArray(inventory.sources) ||
      !inventory.sources.every(isRecord)) {
    add(findings, "ORODI_ELIGIBILITY_INVENTORY_INVALID", "$inventory", "unexpected inventory contract");
    return false;
  }
  inventory.sources.forEach((source, index) => {
    const path = `$inventory.sources[${index}]`;
    exactKeys(source, [
      "shape_id", "path", "sha256", "selector", "shape_kind", "adapter_disposition", "exact_fields",
    ], path, findings);
    for (const key of ["shape_id", "path", "selector", "shape_kind", "adapter_disposition"] as const) {
      if (typeof source[key] !== "string" || source[key].length === 0) {
        add(findings, "ORODI_ELIGIBILITY_INVENTORY_INVALID", `${path}.${key}`, "expected non-empty string");
      }
    }
    if (typeof source.sha256 !== "string" || !sha256Pattern.test(source.sha256)) {
      add(findings, "ORODI_ELIGIBILITY_INVENTORY_INVALID", `${path}.sha256`, "expected lowercase SHA-256");
    }
    if (!Array.isArray(source.exact_fields) || !source.exact_fields.every((field) =>
      typeof field === "string" && field.length > 0)) {
      add(findings, "ORODI_ELIGIBILITY_INVENTORY_INVALID", `${path}.exact_fields`, "expected string array");
    }
  });
  return true;
};

const validateNormalizationContract = (
  value: unknown,
  path: string,
  findings: EvidenceEligibilityFinding[],
): value is LegacyV1NormalizationResult => {
  if (!isRecord(value)) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", path, "expected normalization result object");
    return false;
  }
  exactKeys(value, [
    "schema_version", "adapter_id", "adapter_version", "evidence_lane", "input_id",
    "source_shape_id", "source", "replayed_at", "verdict", "normalized_observations",
    "findings", "authority_effect",
  ], path, findings);
  const literalChecks: ReadonlyArray<readonly [unknown, string, string]> = [
    [value.schema_version, "domainspec.orodi.legacy-v1-normalization-result/v1", `${path}.schema_version`],
    [value.adapter_id, "domainspec.orodi.legacy-v1-adapter", `${path}.adapter_id`],
    [value.adapter_version, "1.0.0-candidate-local", `${path}.adapter_version`],
    [value.evidence_lane, "candidate-local-prototype", `${path}.evidence_lane`],
    [value.authority_effect, "none", `${path}.authority_effect`],
  ];
  for (const [actual, expected, literalPath] of literalChecks) {
    if (actual !== expected) add(findings, "ORODI_ELIGIBILITY_CONTRACT_LITERAL", literalPath, `expected ${expected}`);
  }
  if (typeof value.input_id !== "string" || value.input_id.length === 0) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_STRING", `${path}.input_id`, "expected non-empty input ID");
  }
  if (typeof value.source_shape_id !== "string" || value.source_shape_id.length === 0) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_STRING", `${path}.source_shape_id`, "expected non-empty source shape ID");
  }
  if (typeof value.replayed_at !== "string" || !rfc3339Pattern.test(value.replayed_at) ||
      !Number.isFinite(Date.parse(value.replayed_at))) {
    add(findings, "ORODI_ELIGIBILITY_REPLAY_TIME_INVALID", `${path}.replayed_at`, "expected explicit RFC 3339 date-time");
  }
  if (value.verdict !== "normalized") {
    add(findings, "ORODI_ELIGIBILITY_NORMALIZATION_REJECTED", `${path}.verdict`, "only normalized adapter results can enter replay eligibility");
  }
  if (!Array.isArray(value.normalized_observations) || value.normalized_observations.length !== 1) {
    add(findings, "ORODI_ELIGIBILITY_OBSERVATION_CARDINALITY", `${path}.normalized_observations`, "expected exactly one normalized observation");
  }
  if (!Array.isArray(value.findings) || value.findings.length !== 0) {
    add(findings, "ORODI_ELIGIBILITY_NORMALIZATION_FINDINGS_PRESENT", `${path}.findings`, "normalized input must have no adapter findings");
  }
  return true;
};

const sourceShape = (
  inventory: LegacyV1SourceInventory,
  shapeId: string,
  path: string,
  findings: EvidenceEligibilityFinding[],
): LegacyV1SourceShape | null => {
  const matches = inventory.sources.filter(({ shape_id }) => shape_id === shapeId);
  if (matches.length !== 1) {
    add(findings, "ORODI_ELIGIBILITY_SOURCE_SHAPE_UNKNOWN", path, "source shape is not uniquely pinned");
    return null;
  }
  if (matches[0]!.adapter_disposition !== "normalize-as-candidate-local-simulation") {
    add(findings, "ORODI_ELIGIBILITY_SOURCE_SHAPE_INELIGIBLE", path, "source disposition is not normalizable simulation");
    return null;
  }
  return matches[0]!;
};

const validateSourceBinding = (
  normalization: LegacyV1NormalizationResult,
  expected: LegacyV1SourceShape,
  path: string,
  findings: EvidenceEligibilityFinding[],
): void => {
  if (!isRecord(normalization.source)) {
    add(findings, "ORODI_ELIGIBILITY_SOURCE_BINDING_MISMATCH", `${path}.source`, "expected pinned source binding");
    return;
  }
  exactKeys(normalization.source, ["path", "sha256", "selector"], `${path}.source`, findings);
  for (const key of ["path", "sha256", "selector"] as const) {
    if (normalization.source[key] !== expected[key]) {
      add(findings, "ORODI_ELIGIBILITY_SOURCE_BINDING_MISMATCH", `${path}.source.${key}`, `expected pinned ${key}`);
    }
  }
  if (typeof normalization.source.sha256 !== "string" || !sha256Pattern.test(normalization.source.sha256)) {
    add(findings, "ORODI_ELIGIBILITY_SOURCE_BINDING_MISMATCH", `${path}.source.sha256`, "expected lowercase SHA-256");
  }
};

const validateReplayObservation = (
  rawObservation: unknown,
  normalization: LegacyV1NormalizationResult,
  path: string,
  evaluatedAt: string,
  findings: EvidenceEligibilityFinding[],
): void => {
  if (!isRecord(rawObservation)) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", path, "expected observation object");
    return;
  }
  const observation = rawObservation as unknown as OperationalObservation;
  if (observation.plane !== "product") {
    add(findings, "ORODI_ELIGIBILITY_WORKFLOW_PLANE_FORBIDDEN", `${path}.plane`, "workflow evidence cannot enter product replay");
  }
  if (observation.mode !== "simulation") {
    add(findings, "ORODI_ELIGIBILITY_LEGACY_LIVE_FORBIDDEN", `${path}.mode`, "legacy normalization cannot be live evidence");
  }
  if (observation.deployment_effect !== false) {
    add(findings, "ORODI_ELIGIBILITY_DEPLOYMENT_EFFECT_FORBIDDEN", `${path}.deployment_effect`, "legacy replay cannot claim deployment effect");
  }
  if (observation.independently_observed !== false) {
    add(findings, "ORODI_ELIGIBILITY_INDEPENDENT_OBSERVATION_FORBIDDEN", `${path}.independently_observed`, "legacy replay is not independently observed");
  }
  if (!isRecord(observation.telemetry)) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", `${path}.telemetry`, "expected telemetry object");
  } else if (zeroTelemetryKeys.some((key) => observation.telemetry[key] !== 0)) {
    add(findings, "ORODI_ELIGIBILITY_TELEMETRY_NONZERO", `${path}.telemetry`, "legacy replay must preserve zero telemetry accounting");
  }
  if (!isRecord(observation.attributes)) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", `${path}.attributes`, "expected attribute object");
  } else if (observation.attributes["legacy.family"] !== normalization.source_shape_id) {
    add(findings, "ORODI_ELIGIBILITY_FAMILY_MISMATCH", `${path}.attributes.legacy.family`, "legacy family must equal the pinned source shape ID");
  }
  if (normalization.source === null || observation.invalidation_key_digest !== normalization.source.sha256) {
    add(findings, "ORODI_ELIGIBILITY_SOURCE_BINDING_MISMATCH", `${path}.invalidation_key_digest`, "observation must preserve its source digest");
  }
  if (Date.parse(observation.observed_at) > Date.parse(evaluatedAt) ||
      Date.parse(normalization.replayed_at) > Date.parse(evaluatedAt) ||
      observation.observed_at !== normalization.replayed_at) {
    add(findings, "ORODI_ELIGIBILITY_REPLAY_FROM_FUTURE", `${path}.observed_at`, "replay time must equal observation time and not exceed evaluation time");
  }
};

const validateFoundationalControls = (
  rawControls: unknown,
  request: LegacyV1EligibilityReplayRequest,
  findings: EvidenceEligibilityFinding[],
): void => {
  if (!Array.isArray(rawControls)) return;
  if (!rawControls.every(isRecord)) {
    add(findings, "ORODI_ELIGIBILITY_CONTRACT_TYPE", "$.evaluation_context.controls", "every control must be an object");
    return;
  }
  const controls = rawControls as unknown as readonly ControlReceipt[];
  if (controls.length !== FOUNDATIONAL_CONTROL_IDS.length) {
    add(findings, "ORODI_ELIGIBILITY_FOUNDATIONAL_CONTROLS_INCOMPLETE", "$.evaluation_context.controls", "expected exactly six foundational control claims");
  }
  for (const controlId of FOUNDATIONAL_CONTROL_IDS) {
    const matches = controls.filter(({ control_id }) => control_id === controlId);
    if (matches.length !== 1) {
      add(findings, "ORODI_ELIGIBILITY_FOUNDATIONAL_CONTROL_CARDINALITY", "$.evaluation_context.controls", `expected exactly one ${controlId} claim`);
    }
  }
  controls.forEach((control, index) => {
    const path = `$.evaluation_context.controls[${index}]`;
    if (!foundationalSet.has(control.control_id)) {
      add(findings, "ORODI_ELIGIBILITY_CONTROL_UNADMITTED", `${path}.control_id`, "only foundational control claims are admitted");
    }
    if (control.observation_refs.length !== 0) {
      add(findings, "ORODI_ELIGIBILITY_CONTROL_OBSERVATION_REF_FORBIDDEN", `${path}.observation_refs`, "legacy replay observations cannot support runtime control claims");
    }
    if (control.evaluated_at !== request.evaluated_at ||
        control.expires_at !== request.evaluation_context.binding.expires_at ||
        control.invalidation_key_digest !== request.evaluation_context.binding.invalidation_key_digest) {
      add(findings, "ORODI_ELIGIBILITY_CONTROL_BINDING_MISMATCH", path, "control claim must bind the exact evaluation time, expiry, and invalidation key");
    }
  });
};

export const evaluateLegacyV1EvidenceEligibility = (
  rawRequest: unknown,
  rawInventory: unknown,
): EvidenceEligibilityResult => {
  const findings: EvidenceEligibilityFinding[] = [];
  const root = isRecord(rawRequest) ? rawRequest : {};
  const replayId = typeof root.replay_id === "string" && root.replay_id.length > 0
    ? root.replay_id : "invalid-replay";
  const evaluatedAt = typeof root.evaluated_at === "string" && root.evaluated_at.length > 0
    ? root.evaluated_at : "1970-01-01T00:00:00Z";

  if (!validateRequestRoot(rawRequest, findings) || !validateInventory(rawInventory, findings)) {
    return invalidResult(replayId, evaluatedAt, findings);
  }
  const request = rawRequest;
  const inventory = rawInventory;
  const replayObservations: OperationalObservation[] = [];

  request.normalizations.forEach((normalization, index) => {
    const path = `$.normalizations[${index}]`;
    validateNormalizationContract(normalization, path, findings);
    if (!isRecord(normalization)) return;
    const typed = normalization as unknown as LegacyV1NormalizationResult;
    const expected = sourceShape(inventory, String(typed.source_shape_id), `${path}.source_shape_id`, findings);
    if (expected !== null) validateSourceBinding(typed, expected, path, findings);
    if (Array.isArray(typed.normalized_observations) && typed.normalized_observations.length === 1) {
      const rawObservation = typed.normalized_observations[0] as unknown;
      validateReplayObservation(
        rawObservation, typed,
        `${path}.normalized_observations[0]`, request.evaluated_at, findings,
      );
      if (isRecord(rawObservation)) {
        replayObservations.push(rawObservation as unknown as OperationalObservation);
      }
    }
  });

  const duplicateIds = replayObservations
    .map(({ observation_id }) => observation_id)
    .filter((id, index, ids) => ids.indexOf(id) !== index);
  for (const duplicateId of [...new Set(duplicateIds)].sort()) {
    add(findings, "ORODI_ELIGIBILITY_OBSERVATION_DUPLICATE", "$.normalizations", `duplicate observation ID ${duplicateId}`);
  }

  const candidateBundle: OperationalEvaluationBundle = {
    schema_version: "domainspec.orodi.evaluation-bundle/v1",
    evidence_lane: "candidate-local-prototype",
    binding: request.evaluation_context.binding,
    observations: replayObservations,
    controls: request.evaluation_context.controls,
    claim: { claim_id: `${request.replay_id}-foundational`, required_controls: FOUNDATIONAL_CONTROL_IDS },
    authority_effect: "none",
  };
  const decoded = decodeOperationalEvaluationBundle(candidateBundle);
  for (const finding of decoded.findings) {
    add(findings, `ORODI_ELIGIBILITY_${finding.code}`, `$.evaluation_context${finding.path.slice(1)}`, finding.detail);
  }
  validateFoundationalControls(request.evaluation_context.controls, request, findings);

  if (findings.length > 0) return invalidResult(request.replay_id, request.evaluated_at, findings);

  const admittedBundle: OperationalEvaluationBundle = Object.freeze({
    ...candidateBundle,
    observations: Object.freeze([]),
  });
  const derivedResult = deriveFoundationalControlSet(admittedBundle, request.evaluated_at);
  if (derivedResult.mismatches.length > 0) {
    const mismatchFindings = derivedResult.mismatches.map((mismatch): EvidenceEligibilityFinding => ({
      code: "ORODI_ELIGIBILITY_CONTROL_CLAIM_MISMATCH",
      path: `$.evaluation_context.controls.${mismatch.control_id}`,
      detail: `${mismatch.control_id} claimed ${mismatch.claimed_state ?? "missing"} but empty admitted evidence derives ${mismatch.derived_state}`,
    }));
    return invalidResult(request.replay_id, request.evaluated_at, mismatchFindings);
  }

  const replay = orderedObservations(replayObservations);
  const receipts: readonly EvidenceEligibilityReceipt[] = Object.freeze(replay.map((observation) => {
    const normalization = request.normalizations.find(({ normalized_observations }) =>
      normalized_observations.some(({ observation_id }) => observation_id === observation.observation_id))!;
    return Object.freeze({
      schema_version: "domainspec.orodi.evidence-eligibility-receipt/v1",
      observation_id: observation.observation_id,
      source_shape_id: normalization.source_shape_id,
      decision: "replay-only",
      eligible_controls: Object.freeze([]),
      ineligible_controls: FOUNDATIONAL_CONTROL_IDS,
      reason_codes: Object.freeze([
        "ORODI_ELIGIBILITY_LEGACY_DECLARATION_REPLAY_ONLY",
        "ORODI_ELIGIBILITY_RUNTIME_PROFILE_NOT_ADMITTED",
      ]),
      authority_effect: "none",
    });
  }));

  return Object.freeze({
    schema_version: "domainspec.orodi.evidence-eligibility-result/v1",
    gate_id: "domainspec.orodi.legacy-v1-evidence-eligibility",
    gate_version: "1.0.0-candidate-local",
    evidence_lane: "candidate-local-prototype",
    replay_id: request.replay_id,
    evaluated_at: request.evaluated_at,
    decision: "replay-only",
    runtime_admission: "denied",
    replay_observations: replay,
    runtime_admitted_observations: Object.freeze([]),
    eligibility_receipts: receipts,
    derived_result: derivedResult,
    findings: Object.freeze([]),
    authority_effect: "none",
  });
};

const profileCanonicalJson = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(profileCanonicalJson).join(",")}]`;
  if (isRecord(value)) return `{${Object.keys(value).sort().map((key) =>
    `${JSON.stringify(key)}:${profileCanonicalJson(value[key])}`).join(",")}}`;
  const encoded = JSON.stringify(value);
  return encoded === undefined ? "null" : encoded;
};

const profileDigest = (value: unknown): string =>
  createHash("sha256").update(profileCanonicalJson(value)).digest("hex");

const profileInvalidResult = (
  candidate: unknown,
  evaluatedAt: string,
  findings: readonly EvidenceEligibilityFinding[],
): ToolProfileEvidenceEligibilityResult => {
  const root = isRecord(candidate) ? candidate : {};
  const normalization = isRecord(root.normalization) ? root.normalization : {};
  const replayId = typeof normalization.replay_id === "string" && normalization.replay_id.length > 0
    ? normalization.replay_id : "invalid-replay";
  return Object.freeze({
    schema_version: "domainspec.orodi.tool-profile-evidence-eligibility-result/v1",
    gate_id: "domainspec.orodi.tool-profile-replay-evidence-eligibility",
    gate_version: "1.0.0-candidate-local",
    evidence_lane: "candidate-local-prototype",
    replay_id: replayId,
    profile_id: typeof normalization.profile_id === "string" && normalization.profile_id.length > 0
      ? normalization.profile_id : "invalid-profile",
    profile_version: typeof normalization.profile_version === "string" && normalization.profile_version.length > 0
      ? normalization.profile_version : "invalid-version",
    family_id: typeof normalization.family_id === "string" && normalization.family_id.length > 0
      ? normalization.family_id : "telemetry",
    descriptor_sha256: typeof normalization.descriptor_sha256 === "string" && sha256Pattern.test(normalization.descriptor_sha256)
      ? normalization.descriptor_sha256 : "0".repeat(64),
    normalization_sha256: profileDigest(normalization),
    evaluated_at: evaluatedAt,
    decision: "rejected",
    runtime_admission: "denied",
    referent_trust: "unverified",
    replay_observations: Object.freeze([]),
    runtime_admitted_observations: Object.freeze([] as const),
    eligibility_receipts: Object.freeze([]),
    derived_result: null,
    findings: orderedFindings(findings),
    authority_effect: "none",
  });
};

const profileAdd = (
  findings: EvidenceEligibilityFinding[],
  code: string,
  path: string,
  detail: string,
): void => {
  findings.push({ code, path, detail });
};

const profileExactKeys = (
  value: JsonRecord,
  expected: readonly string[],
  path: string,
  findings: EvidenceEligibilityFinding[],
): void => {
  const allowed = new Set(expected);
  expected.forEach((key) => {
    if (!(key in value)) profileAdd(findings, "PROFILE_ELIGIBILITY_CONTRACT_REQUIRED", `${path}.${key}`, "required field is absent");
  });
  Object.keys(value).sort().forEach((key) => {
    if (!allowed.has(key)) profileAdd(findings, "PROFILE_ELIGIBILITY_CONTRACT_CLOSED", `${path}.${key}`, "unexpected field");
  });
};

const validateProfileNormalization = (
  value: unknown,
  findings: EvidenceEligibilityFinding[],
): value is ToolEvidenceProfileNormalizationResult => {
  if (!isRecord(value)) {
    profileAdd(findings, "PROFILE_ELIGIBILITY_NORMALIZATION_INVALID", "$.normalization", "expected normalization object");
    return false;
  }
  profileExactKeys(value, [
    "schema_version", "normalizer_id", "normalizer_version", "registry_entry", "replay_id",
    "profile_id", "profile_version", "family_id", "fixture_id", "descriptor_sha256",
    "wp5_result_sha256", "source_sha256", "selected_value_sha256", "invalidation_key_digest",
    "replayed_at", "verdict", "observations", "findings", "runtime_admission",
    "referent_trust", "authority_effect",
  ], "$.normalization", findings);
  if (value.schema_version === "domainspec.orodi.legacy-v1-normalization-result/v1") {
    profileAdd(findings, "LEGACY_V1_CONTRACT_IMPERSONATION", "$.normalization.schema_version", "legacy-v1 normalization cannot enter the profile gate");
  } else if (value.schema_version !== "domainspec.orodi.tool-evidence-profile-normalization-result/v1") {
    profileAdd(findings, "PROFILE_ELIGIBILITY_NORMALIZATION_INVALID", "$.normalization.schema_version", "unexpected normalization schema");
  }
  if (value.normalizer_version !== "1.0.0-candidate-local" || value.verdict !== "normalized" ||
      value.runtime_admission !== "denied" || value.referent_trust !== "unverified" ||
      value.authority_effect !== "none") {
    profileAdd(findings, "FORGED_TRUST_OR_RUNTIME_ADMISSION", "$.normalization", "normalization ceiling or verdict is invalid");
  }
  if (!Array.isArray(value.observations) || value.observations.length !== 1) {
    profileAdd(findings, "PROFILE_ELIGIBILITY_OBSERVATION_CARDINALITY", "$.normalization.observations", "expected exactly one replay observation");
  }
  if (!Array.isArray(value.findings) || value.findings.length !== 0) {
    profileAdd(findings, "PROFILE_ELIGIBILITY_NORMALIZATION_FINDINGS", "$.normalization.findings", "normalized input must have no findings");
  }
  for (const key of ["descriptor_sha256", "wp5_result_sha256", "source_sha256", "selected_value_sha256", "invalidation_key_digest"] as const) {
    if (typeof value[key] !== "string" || !sha256Pattern.test(value[key])) {
      profileAdd(findings, "PROFILE_ELIGIBILITY_DIGEST_INVALID", `$.normalization.${key}`, "expected lowercase SHA-256");
    }
  }
  return true;
};

export const evaluateToolProfileEvidenceEligibility = (
  rawCandidate: unknown,
): ToolProfileEvidenceEligibilityResult => {
  const findings: EvidenceEligibilityFinding[] = [];
  const root = isRecord(rawCandidate) ? rawCandidate : {};
  const evaluatedAt = typeof root.evaluated_at === "string" && root.evaluated_at.length > 0
    ? root.evaluated_at : "1970-01-01T00:00:00Z";
  if (!isRecord(rawCandidate)) {
    profileAdd(findings, "PROFILE_ELIGIBILITY_CONTRACT_TYPE", "$", "expected candidate object");
    return profileInvalidResult(rawCandidate, evaluatedAt, findings);
  }
  profileExactKeys(rawCandidate, ["normalization", "evaluation_context", "evaluated_at"], "$", findings);
  if (!rfc3339Pattern.test(evaluatedAt) || !Number.isFinite(Date.parse(evaluatedAt))) {
    profileAdd(findings, "PROFILE_ELIGIBILITY_EVALUATION_TIME_INVALID", "$.evaluated_at", "expected explicit RFC3339 time");
  }
  validateProfileNormalization(rawCandidate.normalization, findings);
  if (!isRecord(rawCandidate.evaluation_context)) {
    profileAdd(findings, "PROFILE_ELIGIBILITY_CONTEXT_INVALID", "$.evaluation_context", "expected evaluation context object");
  } else {
    profileExactKeys(rawCandidate.evaluation_context, ["binding", "controls"], "$.evaluation_context", findings);
  }
  if (findings.length > 0 || !isRecord(rawCandidate.normalization) || !isRecord(rawCandidate.evaluation_context)) {
    return profileInvalidResult(rawCandidate, evaluatedAt, findings);
  }
  const candidate = rawCandidate as unknown as ToolProfileEvidenceEligibilityCandidate;
  const normalization = candidate.normalization;
  const observation = normalization.observations[0];
  if (observation === undefined) {
    profileAdd(findings, "PROFILE_ELIGIBILITY_OBSERVATION_CARDINALITY", "$.normalization.observations", "observation is absent");
    return profileInvalidResult(rawCandidate, evaluatedAt, findings);
  }
  if (observation.plane !== "product") profileAdd(findings, "WORKFLOW_PLANE_OBSERVATION", "$.normalization.observations[0].plane", "workflow evidence is forbidden");
  if (observation.mode !== "simulation") profileAdd(findings, "LIVE_MODE_OBSERVATION", "$.normalization.observations[0].mode", "live evidence is forbidden");
  if (observation.independently_observed !== false) profileAdd(findings, "INDEPENDENT_OBSERVATION_CLAIM", "$.normalization.observations[0].independently_observed", "independent observation is forbidden");
  if (observation.deployment_effect !== false) profileAdd(findings, "DEPLOYMENT_EFFECT_CLAIM", "$.normalization.observations[0].deployment_effect", "deployment effect is forbidden");
  if (!isRecord(observation.telemetry) || zeroTelemetryKeys.some((key) => observation.telemetry[key] !== 0)) {
    profileAdd(findings, "NONZERO_TELEMETRY_CLAIM", "$.normalization.observations[0].telemetry", "replay telemetry must remain zero");
  }
  if (observation.invalidation_key_digest !== normalization.invalidation_key_digest) {
    profileAdd(findings, "INVALIDATION_KEY_MISMATCH", "$.normalization.observations[0].invalidation_key_digest", "observation and normalization keys differ");
  }
  if (observation.observed_at !== normalization.replayed_at ||
      Date.parse(observation.observed_at) > Date.parse(evaluatedAt)) {
    profileAdd(findings, "REPLAY_FROM_FUTURE", "$.normalization.observations[0].observed_at", "observation time is outside replay bounds");
  }

  const candidateBundle: OperationalEvaluationBundle = {
    schema_version: "domainspec.orodi.evaluation-bundle/v1",
    evidence_lane: "candidate-local-prototype",
    binding: candidate.evaluation_context.binding,
    observations: [observation],
    controls: candidate.evaluation_context.controls,
    claim: { claim_id: `${normalization.replay_id}-profile-foundational`, required_controls: FOUNDATIONAL_CONTROL_IDS },
    authority_effect: "none",
  };
  const decoded = decodeOperationalEvaluationBundle(candidateBundle);
  decoded.findings.forEach((item) => profileAdd(
    findings,
    `PROFILE_ELIGIBILITY_${item.code}`,
    `$.evaluation_context${item.path.slice(1)}`,
    item.detail,
  ));
  const controlsRaw: unknown = candidate.evaluation_context.controls;
  if (!Array.isArray(controlsRaw) || !controlsRaw.every(isRecord)) {
    profileAdd(findings, "FOUNDATIONAL_CONTROLS_INCOMPLETE", "$.evaluation_context.controls", "expected six closed control claims");
  } else {
    if (controlsRaw.length !== FOUNDATIONAL_CONTROL_IDS.length) {
      profileAdd(findings, "FOUNDATIONAL_CONTROLS_INCOMPLETE", "$.evaluation_context.controls", "expected exactly six foundational controls");
    }
    FOUNDATIONAL_CONTROL_IDS.forEach((controlId) => {
      if (controlsRaw.filter((control) => control.control_id === controlId).length !== 1) {
        profileAdd(findings, "FOUNDATIONAL_CONTROLS_INCOMPLETE", "$.evaluation_context.controls", `expected exactly one ${controlId}`);
      }
    });
    const binding = candidate.evaluation_context.binding;
    controlsRaw.forEach((control, index) => {
      const path = `$.evaluation_context.controls[${index}]`;
      if (!foundationalSet.has(String(control.control_id))) {
        profileAdd(findings, "PROFILE_ELIGIBILITY_CONTROL_UNADMITTED", `${path}.control_id`, "only foundational controls are accepted");
      }
      if (!Array.isArray(control.observation_refs) || control.observation_refs.length !== 0) {
        profileAdd(findings, "ELIGIBLE_CONTROL_OR_OBSERVATION_REF_LAUNDERING", `${path}.observation_refs`, "replay observations cannot support control claims");
      }
      if (control.evaluated_at !== evaluatedAt || control.expires_at !== binding.expires_at ||
          control.invalidation_key_digest !== binding.invalidation_key_digest) {
        profileAdd(findings, "PROFILE_ELIGIBILITY_CONTROL_BINDING_MISMATCH", path, "control does not bind the exact context");
      }
    });
  }
  if (findings.length > 0 || decoded.bundle === null) {
    return profileInvalidResult(rawCandidate, evaluatedAt, findings);
  }

  const admittedBundle: OperationalEvaluationBundle = Object.freeze({
    ...candidateBundle,
    observations: Object.freeze([]),
  });
  const derivedResult = deriveFoundationalControlSet(admittedBundle, evaluatedAt);
  if (derivedResult.mismatches.length > 0) {
    const mismatches = derivedResult.mismatches.map((mismatch): EvidenceEligibilityFinding => ({
      code: "PROFILE_ELIGIBILITY_CONTROL_CLAIM_MISMATCH",
      path: `$.evaluation_context.controls.${mismatch.control_id}`,
      detail: `${mismatch.control_id} claimed ${mismatch.claimed_state ?? "missing"} but empty admitted evidence derives ${mismatch.derived_state}`,
    }));
    return profileInvalidResult(rawCandidate, evaluatedAt, mismatches);
  }

  const receipt: ToolProfileEvidenceEligibilityReceipt = Object.freeze({
    schema_version: "domainspec.orodi.tool-profile-evidence-eligibility-receipt/v1",
    observation_id: observation.observation_id,
    profile_id: normalization.profile_id,
    family_id: normalization.family_id,
    decision: "replay-only",
    eligible_controls: Object.freeze([] as const),
    ineligible_controls: FOUNDATIONAL_CONTROL_IDS,
    reason_codes: Object.freeze([
      "PROFILE_REPLAY_DECLARATION_ONLY",
      "PROFILE_REPLAY_RUNTIME_ADMISSION_DENIED",
      "PROFILE_REPLAY_REFERENT_TRUST_UNVERIFIED",
    ]),
    authority_effect: "none",
  });
  return Object.freeze({
    schema_version: "domainspec.orodi.tool-profile-evidence-eligibility-result/v1",
    gate_id: "domainspec.orodi.tool-profile-replay-evidence-eligibility",
    gate_version: "1.0.0-candidate-local",
    evidence_lane: "candidate-local-prototype",
    replay_id: normalization.replay_id,
    profile_id: normalization.profile_id,
    profile_version: normalization.profile_version,
    family_id: normalization.family_id,
    descriptor_sha256: normalization.descriptor_sha256,
    normalization_sha256: profileDigest(normalization),
    evaluated_at: evaluatedAt,
    decision: "replay-only",
    runtime_admission: "denied",
    referent_trust: "unverified",
    replay_observations: Object.freeze([observation]),
    runtime_admitted_observations: Object.freeze([] as const),
    eligibility_receipts: Object.freeze([receipt]),
    derived_result: derivedResult,
    findings: Object.freeze([]),
    authority_effect: "none",
  });
};
