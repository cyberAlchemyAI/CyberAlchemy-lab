import {
  CONTROL_IDS,
  EVIDENCE_STATES,
  type BoundReference,
  type ControlId,
  type ControlReceipt,
  type DerivedControlSetResult,
  type EvidenceState,
  type EvaluationFinding,
  type OperationalEvaluationBundle,
  type OperationalEvaluationResult,
  type OperationalObservation,
} from "../contracts/operational-evidence.js";
import {
  deriveFoundationalControlSet,
  invalidDerivedControlSetResult,
} from "./derive-foundational-controls.js";

type JsonRecord = Record<string, unknown>;

const controlIds = new Set<string>(CONTROL_IDS);
const evidenceStates = new Set<string>(EVIDENCE_STATES);
const sha256Pattern = /^[0-9a-f]{64}$/;
const ambientLatestPattern = /(^|[/:@._-])latest($|[/:@._-])/i;

const isRecord = (value: unknown): value is JsonRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const add = (
  findings: EvaluationFinding[],
  code: string,
  path: string,
  detail: string,
): void => {
  findings.push({ code, path, detail });
};

const requireRecord = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): JsonRecord | null => {
  if (!isRecord(value)) {
    add(findings, "ORODI_CONTRACT_TYPE", path, "expected object");
    return null;
  }
  return value;
};

const exactKeys = (
  value: JsonRecord,
  expected: readonly string[],
  path: string,
  findings: EvaluationFinding[],
): void => {
  const expectedSet = new Set(expected);
  for (const key of expected) {
    if (!(key in value)) add(findings, "ORODI_CONTRACT_REQUIRED", path, `missing ${key}`);
  }
  for (const key of Object.keys(value).sort()) {
    if (!expectedSet.has(key)) add(findings, "ORODI_CONTRACT_CLOSED", `${path}.${key}`, "unexpected field");
  }
};

const requireString = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): value is string => {
  if (typeof value !== "string" || value.length === 0) {
    add(findings, "ORODI_CONTRACT_STRING", path, "expected non-empty string");
    return false;
  }
  return true;
};

const requireLiteral = (
  value: unknown,
  expected: string,
  path: string,
  findings: EvaluationFinding[],
): void => {
  if (value !== expected) add(findings, "ORODI_CONTRACT_LITERAL", path, `expected ${expected}`);
};

const requireBoolean = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): value is boolean => {
  if (typeof value !== "boolean") {
    add(findings, "ORODI_CONTRACT_BOOLEAN", path, "expected boolean");
    return false;
  }
  return true;
};

const requireNonNegativeInteger = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): value is number => {
  if (!Number.isInteger(value) || (value as number) < 0) {
    add(findings, "ORODI_CONTRACT_INTEGER", path, "expected non-negative integer");
    return false;
  }
  return true;
};

const requireTimestamp = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): value is string => {
  if (!requireString(value, path, findings)) return false;
  if (!Number.isFinite(Date.parse(value))) {
    add(findings, "ORODI_CONTRACT_TIMESTAMP", path, "expected RFC 3339 date-time");
    return false;
  }
  return true;
};

const requireSha256 = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): value is string => {
  if (!requireString(value, path, findings)) return false;
  if (!sha256Pattern.test(value)) {
    add(findings, "ORODI_CONTRACT_SHA256", path, "expected lowercase SHA-256");
    return false;
  }
  return true;
};

const requireVersion = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): value is string => {
  if (!requireString(value, path, findings)) return false;
  if (ambientLatestPattern.test(value)) {
    add(findings, "ORODI_AMBIENT_VERSION_FORBIDDEN", path, "ambient latest is not an exact version");
    return false;
  }
  return true;
};

const requireStringArray = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): value is string[] => {
  if (!Array.isArray(value)) {
    add(findings, "ORODI_CONTRACT_ARRAY", path, "expected array");
    return false;
  }
  value.forEach((entry, index) => requireString(entry, `${path}[${index}]`, findings));
  if (new Set(value).size !== value.length) {
    add(findings, "ORODI_CONTRACT_UNIQUE", path, "duplicate entries are forbidden");
  }
  return value.every((entry) => typeof entry === "string" && entry.length > 0);
};

const validateBoundReference = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): void => {
  const ref = requireRecord(value, path, findings);
  if (ref === null) return;
  exactKeys(ref, ["ref", "version", "sha256"], path, findings);
  requireString(ref.ref, `${path}.ref`, findings);
  requireVersion(ref.version, `${path}.version`, findings);
  requireSha256(ref.sha256, `${path}.sha256`, findings);
  if (typeof ref.ref === "string" && ambientLatestPattern.test(ref.ref)) {
    add(findings, "ORODI_AMBIENT_VERSION_FORBIDDEN", `${path}.ref`, "ambient latest is not an exact reference");
  }
};

const validateBinding = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): void => {
  const binding = requireRecord(value, path, findings);
  if (binding === null) return;
  exactKeys(binding, [
    "schema_version", "binding_id", "subject", "environment", "stable_artifact",
    "candidate_artifact", "configuration", "topology", "fixture", "evaluator",
    "receipt_schema", "owners", "profiles", "policies", "invalidation_key_digest",
    "created_at", "expires_at",
  ], path, findings);
  requireLiteral(binding.schema_version, "domainspec.orodi.evaluation-binding/v1", `${path}.schema_version`, findings);
  requireString(binding.binding_id, `${path}.binding_id`, findings);
  for (const key of ["subject", "environment", "stable_artifact", "candidate_artifact", "configuration", "topology", "fixture", "evaluator", "receipt_schema"] as const) {
    validateBoundReference(binding[key], `${path}.${key}`, findings);
  }

  const owners = requireRecord(binding.owners, `${path}.owners`, findings);
  if (owners !== null) {
    exactKeys(owners, ["semantic", "integration", "evidence", "privacy", "evaluator"], `${path}.owners`, findings);
    for (const role of ["semantic", "integration", "evidence", "privacy", "evaluator"] as const) {
      requireString(owners[role], `${path}.owners.${role}`, findings);
    }
  }

  if (!Array.isArray(binding.profiles) || binding.profiles.length === 0) {
    add(findings, "ORODI_CONTRACT_ARRAY", `${path}.profiles`, "expected non-empty array");
  } else {
    binding.profiles.forEach((raw, index) => {
      const profilePath = `${path}.profiles[${index}]`;
      const profile = requireRecord(raw, profilePath, findings);
      if (profile === null) return;
      exactKeys(profile, ["role", "profile_id", "version", "sha256", "status"], profilePath, findings);
      requireString(profile.role, `${profilePath}.role`, findings);
      requireString(profile.profile_id, `${profilePath}.profile_id`, findings);
      requireVersion(profile.version, `${profilePath}.version`, findings);
      requireSha256(profile.sha256, `${profilePath}.sha256`, findings);
      requireLiteral(profile.status, "candidate-local", `${profilePath}.status`, findings);
    });
  }

  if (!Array.isArray(binding.policies) || binding.policies.length === 0) {
    add(findings, "ORODI_CONTRACT_ARRAY", `${path}.policies`, "expected non-empty array");
  } else {
    binding.policies.forEach((raw, index) => {
      const policyPath = `${path}.policies[${index}]`;
      const policy = requireRecord(raw, policyPath, findings);
      if (policy === null) return;
      exactKeys(policy, ["role", "policy_id", "version", "sha256", "enabled"], policyPath, findings);
      requireString(policy.role, `${policyPath}.role`, findings);
      requireString(policy.policy_id, `${policyPath}.policy_id`, findings);
      requireVersion(policy.version, `${policyPath}.version`, findings);
      requireSha256(policy.sha256, `${policyPath}.sha256`, findings);
      if (policy.enabled !== true) add(findings, "ORODI_POLICY_DISABLED", `${policyPath}.enabled`, "policy must be enabled");
    });
  }
  requireSha256(binding.invalidation_key_digest, `${path}.invalidation_key_digest`, findings);
  requireTimestamp(binding.created_at, `${path}.created_at`, findings);
  requireTimestamp(binding.expires_at, `${path}.expires_at`, findings);
};

const validateObservation = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): void => {
  const observation = requireRecord(value, path, findings);
  if (observation === null) return;
  exactKeys(observation, [
    "schema_version", "observation_id", "plane", "kind", "mode", "correlation_id",
    "attributes", "attribute_allowlist", "cardinality", "telemetry", "deployment_effect",
    "independently_observed", "observed_at", "invalidation_key_digest",
  ], path, findings);
  requireLiteral(observation.schema_version, "domainspec.orodi.observation/v1", `${path}.schema_version`, findings);
  requireString(observation.observation_id, `${path}.observation_id`, findings);
  if (observation.plane !== "product" && observation.plane !== "workflow") {
    add(findings, "ORODI_CONTRACT_ENUM", `${path}.plane`, "expected product or workflow");
  }
  if (!["metric", "trace", "log", "health", "deployment-effect", "rollback-effect"].includes(String(observation.kind))) {
    add(findings, "ORODI_CONTRACT_ENUM", `${path}.kind`, "unsupported observation kind");
  }
  if (observation.mode !== "simulation" && observation.mode !== "live") {
    add(findings, "ORODI_CONTRACT_ENUM", `${path}.mode`, "expected simulation or live");
  }
  requireString(observation.correlation_id, `${path}.correlation_id`, findings);

  const attributes = requireRecord(observation.attributes, `${path}.attributes`, findings);
  if (attributes !== null) {
    for (const [key, entry] of Object.entries(attributes).sort(([a], [b]) => a.localeCompare(b))) {
      requireString(key, `${path}.attributes`, findings);
      requireString(entry, `${path}.attributes.${key}`, findings);
    }
  }
  requireStringArray(observation.attribute_allowlist, `${path}.attribute_allowlist`, findings);

  const cardinality = requireRecord(observation.cardinality, `${path}.cardinality`, findings);
  if (cardinality !== null) {
    exactKeys(cardinality, ["observed", "budget"], `${path}.cardinality`, findings);
    requireNonNegativeInteger(cardinality.observed, `${path}.cardinality.observed`, findings);
    requireNonNegativeInteger(cardinality.budget, `${path}.cardinality.budget`, findings);
  }

  const telemetry = requireRecord(observation.telemetry, `${path}.telemetry`, findings);
  if (telemetry !== null) {
    exactKeys(telemetry, ["offered", "queued", "exported", "rejected", "dropped", "pending", "partial_success"], `${path}.telemetry`, findings);
    for (const key of ["offered", "queued", "exported", "rejected", "dropped", "pending", "partial_success"] as const) {
      requireNonNegativeInteger(telemetry[key], `${path}.telemetry.${key}`, findings);
    }
  }
  requireBoolean(observation.deployment_effect, `${path}.deployment_effect`, findings);
  requireBoolean(observation.independently_observed, `${path}.independently_observed`, findings);
  requireTimestamp(observation.observed_at, `${path}.observed_at`, findings);
  requireSha256(observation.invalidation_key_digest, `${path}.invalidation_key_digest`, findings);
};

const validateControl = (
  value: unknown,
  path: string,
  findings: EvaluationFinding[],
): void => {
  const control = requireRecord(value, path, findings);
  if (control === null) return;
  exactKeys(control, ["schema_version", "control_id", "state", "observation_refs", "evaluated_at", "expires_at", "invalidation_key_digest", "authority_effect"], path, findings);
  requireLiteral(control.schema_version, "domainspec.orodi.control-receipt/v1", `${path}.schema_version`, findings);
  if (!controlIds.has(String(control.control_id))) add(findings, "ORODI_CONTROL_UNADMITTED", `${path}.control_id`, "expected C01-C16");
  if (!evidenceStates.has(String(control.state))) add(findings, "ORODI_STATE_COLLAPSE", `${path}.state`, "evidence state must remain one of the seven disjoint values");
  requireStringArray(control.observation_refs, `${path}.observation_refs`, findings);
  requireTimestamp(control.evaluated_at, `${path}.evaluated_at`, findings);
  requireTimestamp(control.expires_at, `${path}.expires_at`, findings);
  requireSha256(control.invalidation_key_digest, `${path}.invalidation_key_digest`, findings);
  requireLiteral(control.authority_effect, "none", `${path}.authority_effect`, findings);
};

export const decodeOperationalEvaluationBundle = (
  input: unknown,
): Readonly<{ bundle: OperationalEvaluationBundle | null; findings: readonly EvaluationFinding[] }> => {
  const findings: EvaluationFinding[] = [];
  const root = requireRecord(input, "$", findings);
  if (root === null) return { bundle: null, findings };
  exactKeys(root, ["schema_version", "evidence_lane", "binding", "observations", "controls", "claim", "authority_effect"], "$", findings);
  requireLiteral(root.schema_version, "domainspec.orodi.evaluation-bundle/v1", "$.schema_version", findings);
  requireLiteral(root.evidence_lane, "candidate-local-prototype", "$.evidence_lane", findings);
  requireLiteral(root.authority_effect, "none", "$.authority_effect", findings);
  validateBinding(root.binding, "$.binding", findings);

  if (!Array.isArray(root.observations) || root.observations.length === 0) {
    add(findings, "ORODI_CONTRACT_ARRAY", "$.observations", "expected non-empty array");
  } else {
    root.observations.forEach((entry, index) => validateObservation(entry, `$.observations[${index}]`, findings));
  }
  if (!Array.isArray(root.controls)) {
    add(findings, "ORODI_CONTRACT_ARRAY", "$.controls", "expected array");
  } else {
    root.controls.forEach((entry, index) => validateControl(entry, `$.controls[${index}]`, findings));
  }

  const claim = requireRecord(root.claim, "$.claim", findings);
  if (claim !== null) {
    exactKeys(claim, ["claim_id", "required_controls"], "$.claim", findings);
    requireString(claim.claim_id, "$.claim.claim_id", findings);
    if (requireStringArray(claim.required_controls, "$.claim.required_controls", findings)) {
      claim.required_controls.forEach((id, index) => {
        if (!controlIds.has(id)) add(findings, "ORODI_CONTROL_UNADMITTED", `$.claim.required_controls[${index}]`, "expected C01-C16");
      });
    }
  }
  const ordered = [...findings].sort((a, b) => a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.detail.localeCompare(b.detail));
  return {
    bundle: ordered.length === 0 ? input as OperationalEvaluationBundle : null,
    findings: Object.freeze(ordered),
  };
};

const duplicateValues = (values: readonly string[]): string[] =>
  [...new Set(values.filter((value, index) => values.indexOf(value) !== index))].sort();

const claimStateFromControls = (controls: readonly ControlReceipt[]): EvidenceState => {
  for (const id of CONTROL_IDS) {
    const state = controls.find((control) => control.control_id === id)?.state;
    if (state !== undefined && state !== "passed") return state;
  }
  return "passed";
};

const invalidResult = (
  findings: readonly EvaluationFinding[],
  evaluatedAt: string,
  bindingId = "invalid-binding",
  claimId = "invalid-claim",
  claimState: EvidenceState = "invalid",
  controlStates: OperationalEvaluationResult["required_control_states"] = [],
): OperationalEvaluationResult => Object.freeze({
  schema_version: "domainspec.orodi.evaluation-result/v1",
  validator_id: "domainspec.orodi.generic-validator",
  validator_version: "1.0.0-candidate-local",
  evidence_lane: "candidate-local-prototype",
  binding_id: bindingId,
  claim_id: claimId,
  evaluated_at: evaluatedAt,
  verdict: "reject",
  claim_state: claimState,
  required_control_states: Object.freeze([...controlStates]),
  findings: Object.freeze([...findings]),
  authority_effect: "none",
});

const semanticFindings = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): EvaluationFinding[] => {
  const findings: EvaluationFinding[] = [];
  const at = Date.parse(evaluatedAt);
  const binding = bundle.binding;

  if (Date.parse(binding.created_at) >= Date.parse(binding.expires_at)) {
    add(findings, "ORODI_FRESHNESS_WINDOW_INVALID", "$.binding", "created_at must precede expires_at");
  }
  if (at >= Date.parse(binding.expires_at)) {
    add(findings, "ORODI_BINDING_STALE", "$.binding.expires_at", "binding is stale at the explicit evaluation time");
  }

  for (const duplicate of duplicateValues(binding.profiles.map(({ role }) => role))) {
    add(findings, "ORODI_PROFILE_ROLE_DUPLICATE", "$.binding.profiles", `duplicate role ${duplicate}`);
  }
  for (const duplicate of duplicateValues(binding.policies.map(({ role }) => role))) {
    add(findings, "ORODI_POLICY_ROLE_DUPLICATE", "$.binding.policies", `duplicate role ${duplicate}`);
  }

  const observationById = new Map<string, OperationalObservation>();
  bundle.observations.forEach((observation, index) => {
    const path = `$.observations[${index}]`;
    if (observationById.has(observation.observation_id)) {
      add(findings, "ORODI_OBSERVATION_DUPLICATE", `${path}.observation_id`, "observation id must be unique");
    }
    observationById.set(observation.observation_id, observation);
    if (observation.plane !== "product") {
      add(findings, "ORODI_EVIDENCE_PLANE_INVALID", `${path}.plane`, "workflow telemetry cannot satisfy a product control");
    }
    const allowed = new Set(observation.attribute_allowlist);
    for (const key of Object.keys(observation.attributes).sort()) {
      if (!allowed.has(key)) add(findings, "ORODI_ATTRIBUTE_NOT_ALLOWLISTED", `${path}.attributes.${key}`, "attribute is not allowlisted");
    }
    if (observation.cardinality.observed > observation.cardinality.budget) {
      add(findings, "ORODI_CARDINALITY_EXCEEDED", `${path}.cardinality`, "observed cardinality exceeds budget");
    }
    const telemetry = observation.telemetry;
    if (telemetry.offered !== telemetry.queued + telemetry.rejected) {
      add(findings, "ORODI_TELEMETRY_OFFERED_ACCOUNTING", `${path}.telemetry`, "offered must equal queued plus rejected");
    }
    if (telemetry.queued !== telemetry.exported + telemetry.dropped + telemetry.pending) {
      add(findings, "ORODI_TELEMETRY_QUEUE_ACCOUNTING", `${path}.telemetry`, "queued must equal exported plus dropped plus pending");
    }
    if (telemetry.partial_success > telemetry.exported) {
      add(findings, "ORODI_TELEMETRY_PARTIAL_SUCCESS_INVALID", `${path}.telemetry.partial_success`, "partial_success cannot exceed exported");
    }
    if (observation.mode === "simulation" && observation.deployment_effect) {
      add(findings, "ORODI_SIMULATION_EFFECT_FORBIDDEN", `${path}.deployment_effect`, "simulation must record deployment_effect false");
    }
    if (observation.invalidation_key_digest !== binding.invalidation_key_digest) {
      add(findings, "ORODI_INVALIDATION_KEY_MISMATCH", `${path}.invalidation_key_digest`, "observation does not match the binding invalidation key");
    }
    if (Date.parse(observation.observed_at) > at) {
      add(findings, "ORODI_OBSERVATION_FROM_FUTURE", `${path}.observed_at`, "observation occurs after evaluation time");
    }
  });

  const controlIdsObserved = bundle.controls.map(({ control_id: id }) => id);
  for (const duplicate of duplicateValues(controlIdsObserved)) {
    add(findings, "ORODI_CONTROL_DUPLICATE", "$.controls", `duplicate control ${duplicate}`);
  }
  for (const id of CONTROL_IDS) {
    if (!controlIdsObserved.includes(id)) add(findings, "ORODI_CONTROL_MISSING", "$.controls", `missing required control ${id}`);
  }
  if (bundle.controls.length !== CONTROL_IDS.length) {
    add(findings, "ORODI_CONTROL_CARDINALITY", "$.controls", "controls must contain exactly C01-C16");
  }

  const required = bundle.claim.required_controls;
  for (const duplicate of duplicateValues(required)) {
    add(findings, "ORODI_CLAIM_CONTROL_DUPLICATE", "$.claim.required_controls", `duplicate control ${duplicate}`);
  }
  for (const id of CONTROL_IDS) {
    if (!required.includes(id)) add(findings, "ORODI_CLAIM_CONTROL_MISSING", "$.claim.required_controls", `missing required control ${id}`);
  }
  if (required.length !== CONTROL_IDS.length) {
    add(findings, "ORODI_CLAIM_CONTROL_CARDINALITY", "$.claim.required_controls", "claim must require exactly C01-C16");
  }

  bundle.controls.forEach((control, index) => {
    const path = `$.controls[${index}]`;
    if (control.observation_refs.length === 0) {
      add(findings, "ORODI_CONTROL_EVIDENCE_MISSING", `${path}.observation_refs`, "control must cite at least one observation");
    }
    const observations = control.observation_refs.flatMap((ref) => {
      const observation = observationById.get(ref);
      if (observation === undefined) {
        add(findings, "ORODI_OBSERVATION_REF_MISSING", `${path}.observation_refs`, `unknown observation ${ref}`);
        return [];
      }
      return [observation];
    });
    if (control.invalidation_key_digest !== binding.invalidation_key_digest) {
      add(findings, "ORODI_INVALIDATION_KEY_MISMATCH", `${path}.invalidation_key_digest`, "control does not match the binding invalidation key");
    }
    if (Date.parse(control.evaluated_at) > at) {
      add(findings, "ORODI_CONTROL_FROM_FUTURE", `${path}.evaluated_at`, "control was evaluated after the explicit evaluation time");
    }
    if (Date.parse(control.expires_at) > Date.parse(binding.expires_at)) {
      add(findings, "ORODI_CONTROL_EXPIRY_OUTSIDE_BINDING", `${path}.expires_at`, "control expiry exceeds binding expiry");
    }
    if (at >= Date.parse(control.expires_at) && control.state !== "stale") {
      add(findings, "ORODI_CONTROL_STALE", `${path}.expires_at`, "expired control must be reported stale");
    }
    if (control.control_id === "C11" && control.state === "passed") {
      if (!observations.some(({ mode, deployment_effect }) => mode === "simulation" && deployment_effect === false)) {
        add(findings, "ORODI_C11_SIMULATION_REQUIRED", path, "C11 pass requires a simulation observation with no deployment effect");
      }
    }
    if (control.control_id === "C12" && control.state === "passed") {
      if (!observations.some(({ mode, kind, deployment_effect }) => mode === "live" && kind === "deployment-effect" && deployment_effect)) {
        add(findings, "ORODI_C12_LIVE_EFFECT_REQUIRED", path, "C12 pass requires an observed live deployment effect");
      }
      if (!observations.some(({ mode, independently_observed }) => mode === "live" && independently_observed)) {
        add(findings, "ORODI_C12_INDEPENDENT_OBSERVATION_REQUIRED", path, "C12 pass requires independent live observation");
      }
    }
  });
  return findings;
};

export const validateOperationalEvidence = (
  input: unknown,
  evaluatedAt: string,
): OperationalEvaluationResult => {
  const timeFindings: EvaluationFinding[] = [];
  requireTimestamp(evaluatedAt, "$.evaluated_at", timeFindings);
  if (timeFindings.length > 0) return invalidResult(timeFindings, evaluatedAt);

  const decoded = decodeOperationalEvaluationBundle(input);
  if (decoded.bundle === null) return invalidResult(decoded.findings, evaluatedAt);
  const bundle = decoded.bundle;
  const controlStates = CONTROL_IDS.flatMap((id) => {
    const receipt = bundle.controls.find(({ control_id }) => control_id === id);
    return receipt === undefined ? [] : [{ control_id: id, state: receipt.state }];
  });
  const derived = deriveFoundationalControlSet(bundle, evaluatedAt);
  const derivedMismatchFindings: EvaluationFinding[] = derived.mismatches.map((mismatch) => ({
    code: mismatch.code,
    path: `$.controls.${mismatch.control_id}.state`,
    detail: mismatch.claimed_state === null
      ? `no supplied ${mismatch.control_id} state exists; derived state is ${mismatch.derived_state}`
      : `supplied state ${mismatch.claimed_state} differs from derived state ${mismatch.derived_state}`,
  }));
  const semantic = semanticFindings(bundle, evaluatedAt);
  const findings = [...semantic, ...derivedMismatchFindings];
  if (findings.length > 0) {
    const sorted = findings.sort((a, b) => a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.detail.localeCompare(b.detail));
    const staleOnly = semantic.length > 0 && semantic.every(({ code }) => code.includes("STALE"));
    const missingControl = semantic.some(({ code }) => code === "ORODI_CONTROL_MISSING" || code === "ORODI_CLAIM_CONTROL_MISSING");
    const suppliedState = claimStateFromControls(bundle.controls);
    const resultState = suppliedState !== "passed"
      ? suppliedState
      : staleOnly
        ? "stale"
        : missingControl
          ? "missing"
          : "invalid";
    return invalidResult(sorted, evaluatedAt, bundle.binding.binding_id, bundle.claim.claim_id, resultState, controlStates);
  }

  const claimState = claimStateFromControls(bundle.controls);
  const stateFindings = bundle.controls
    .filter(({ state }) => state !== "passed")
    .map(({ control_id, state }) => ({ code: "ORODI_CONTROL_NOT_PASSED", path: `$.controls.${control_id}`, detail: `control state is ${state}` }));
  return Object.freeze({
    schema_version: "domainspec.orodi.evaluation-result/v1",
    validator_id: "domainspec.orodi.generic-validator",
    validator_version: "1.0.0-candidate-local",
    evidence_lane: "candidate-local-prototype",
    binding_id: bundle.binding.binding_id,
    claim_id: bundle.claim.claim_id,
    evaluated_at: evaluatedAt,
    verdict: claimState === "passed" ? "pass" : "reject",
    claim_state: claimState,
    required_control_states: Object.freeze(controlStates),
    findings: Object.freeze(stateFindings),
    authority_effect: "none",
  });
};

export const deriveOperationalControls = (
  input: unknown,
  evaluatedAt: string,
): DerivedControlSetResult => {
  const timeFindings: EvaluationFinding[] = [];
  requireTimestamp(evaluatedAt, "$.evaluated_at", timeFindings);
  if (timeFindings.length > 0) return invalidDerivedControlSetResult(evaluatedAt, timeFindings);

  const decoded = decodeOperationalEvaluationBundle(input);
  if (decoded.bundle === null) return invalidDerivedControlSetResult(evaluatedAt, decoded.findings);
  return deriveFoundationalControlSet(decoded.bundle, evaluatedAt);
};

export const allBoundReferences = (bundle: OperationalEvaluationBundle): readonly BoundReference[] => Object.freeze([
  bundle.binding.subject,
  bundle.binding.environment,
  bundle.binding.stable_artifact,
  bundle.binding.candidate_artifact,
  bundle.binding.configuration,
  bundle.binding.topology,
  bundle.binding.fixture,
  bundle.binding.evaluator,
  bundle.binding.receipt_schema,
]);
