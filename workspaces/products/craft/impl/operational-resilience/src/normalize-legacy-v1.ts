import type {
  LegacyV1AdapterInput,
  LegacyV1NormalizationFinding,
  LegacyV1NormalizationResult,
  LegacyV1SourceBinding,
  LegacyV1SourceInventory,
  LegacyV1SourceShape,
} from "../contracts/legacy-v1-adapter.js";
import type { OperationalObservation } from "../contracts/operational-evidence.js";

type JsonRecord = Record<string, unknown>;

const sha256Pattern = /^[0-9a-f]{64}$/;
const idPattern = /^[a-z0-9][a-z0-9._-]{0,127}$/;
const attributePattern = /^[a-z][a-z0-9_.-]{0,63}$/;
const rfc3339Pattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
const unsafeAttributePattern = /(authorization|cookie|email|password|secret|token|user[_-]?id)/i;
const supportedInstruments = new Set(["Counter", "UpDownCounter", "Histogram", "Gauge"]);
const zeroTelemetry = Object.freeze({
  offered: 0,
  queued: 0,
  exported: 0,
  rejected: 0,
  dropped: 0,
  pending: 0,
  partial_success: 0,
});

const isRecord = (value: unknown): value is JsonRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const add = (
  findings: LegacyV1NormalizationFinding[],
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
  findings: LegacyV1NormalizationFinding[],
): void => {
  const expectedSet = new Set(expected);
  for (const key of expected) {
    if (!(key in value)) add(findings, "ORODI_V1_CONTRACT_REQUIRED", path, `missing ${key}`);
  }
  for (const key of Object.keys(value).sort()) {
    if (!expectedSet.has(key)) add(findings, "ORODI_V1_CONTRACT_CLOSED", `${path}.${key}`, "unexpected field");
  }
};

const requireString = (
  value: unknown,
  path: string,
  findings: LegacyV1NormalizationFinding[],
): value is string => {
  if (typeof value !== "string" || value.length === 0) {
    add(findings, "ORODI_V1_CONTRACT_STRING", path, "expected non-empty string");
    return false;
  }
  return true;
};

const sourceFromUnknown = (
  value: unknown,
  findings: LegacyV1NormalizationFinding[],
): LegacyV1SourceBinding | null => {
  if (!isRecord(value)) {
    add(findings, "ORODI_V1_CONTRACT_TYPE", "$.source", "expected object");
    return null;
  }
  exactKeys(value, ["path", "sha256", "selector"], "$.source", findings);
  const validPath = requireString(value.path, "$.source.path", findings);
  const validDigest = requireString(value.sha256, "$.source.sha256", findings);
  const validSelector = requireString(value.selector, "$.source.selector", findings);
  if (validDigest && !sha256Pattern.test(value.sha256 as string)) {
    add(findings, "ORODI_V1_CONTRACT_SHA256", "$.source.sha256", "expected lowercase SHA-256");
  }
  if (!validPath || !validDigest || !validSelector || !sha256Pattern.test(String(value.sha256))) return null;
  return { path: value.path as string, sha256: value.sha256 as string, selector: value.selector as string };
};

const rejected = (
  inputId: string,
  sourceShapeId: string,
  source: LegacyV1SourceBinding | null,
  replayedAt: string,
  findings: readonly LegacyV1NormalizationFinding[],
): LegacyV1NormalizationResult => ({
  schema_version: "domainspec.orodi.legacy-v1-normalization-result/v1",
  adapter_id: "domainspec.orodi.legacy-v1-adapter",
  adapter_version: "1.0.0-candidate-local",
  evidence_lane: "candidate-local-prototype",
  input_id: inputId,
  source_shape_id: sourceShapeId,
  source,
  replayed_at: replayedAt,
  verdict: "rejected",
  normalized_observations: [],
  findings,
  authority_effect: "none",
});

const normalized = (
  input: LegacyV1AdapterInput,
  source: LegacyV1SourceBinding,
  replayedAt: string,
  observation: OperationalObservation,
): LegacyV1NormalizationResult => ({
  schema_version: "domainspec.orodi.legacy-v1-normalization-result/v1",
  adapter_id: "domainspec.orodi.legacy-v1-adapter",
  adapter_version: "1.0.0-candidate-local",
  evidence_lane: "candidate-local-prototype",
  input_id: input.input_id,
  source_shape_id: input.source_shape_id,
  source,
  replayed_at: replayedAt,
  verdict: "normalized",
  normalized_observations: [observation],
  findings: [],
  authority_effect: "none",
});

const makeObservation = (
  input: LegacyV1AdapterInput,
  source: LegacyV1SourceBinding,
  replayedAt: string,
  kind: "log" | "metric",
  attributes: Readonly<Record<string, string>>,
): OperationalObservation => ({
  schema_version: "domainspec.orodi.observation/v1",
  observation_id: `legacy-v1-${input.input_id}`,
  plane: "product",
  kind,
  mode: "simulation",
  correlation_id: input.input_id,
  attributes,
  attribute_allowlist: Object.keys(attributes).sort(),
  cardinality: { observed: Object.keys(attributes).length, budget: 16 },
  telemetry: zeroTelemetry,
  deployment_effect: false,
  independently_observed: false,
  observed_at: replayedAt,
  invalidation_key_digest: source.sha256,
});

const matchSource = (
  input: LegacyV1AdapterInput,
  inventory: LegacyV1SourceInventory,
  source: LegacyV1SourceBinding,
  findings: LegacyV1NormalizationFinding[],
): LegacyV1SourceShape | null => {
  const entries = inventory.sources.filter(({ shape_id }) => shape_id === input.source_shape_id);
  if (entries.length !== 1) {
    add(findings, "ORODI_V1_SOURCE_SHAPE_UNKNOWN", "$.source_shape_id", "shape ID is not uniquely pinned");
    return null;
  }
  const expected = entries[0]!;
  for (const key of ["path", "sha256", "selector"] as const) {
    if (source[key] !== expected[key]) {
      add(findings, "ORODI_V1_SOURCE_BINDING_MISMATCH", `$.source.${key}`, `expected pinned ${key}`);
    }
  }
  return expected;
};

const validateFailurePayload = (
  value: unknown,
  findings: LegacyV1NormalizationFinding[],
): { condition: string; error_type: string; code: string; retryable: boolean } | null => {
  if (!isRecord(value)) {
    add(findings, "ORODI_V1_CONTRACT_TYPE", "$.payload", "expected failure mapping row object");
    return null;
  }
  exactKeys(value, ["condition", "error_type", "code", "retryable"], "$.payload", findings);
  const stringsValid = ["condition", "error_type", "code"].every((key) =>
    requireString(value[key], `$.payload.${key}`, findings));
  if (typeof value.retryable !== "boolean") {
    add(findings, "ORODI_V1_CONTRACT_BOOLEAN", "$.payload.retryable", "expected boolean");
  }
  if (!stringsValid || typeof value.retryable !== "boolean") return null;
  return {
    condition: value.condition as string,
    error_type: value.error_type as string,
    code: value.code as string,
    retryable: value.retryable,
  };
};

const validateMetricPayload = (
  value: unknown,
  findings: LegacyV1NormalizationFinding[],
): { name: string; instrument: string; unit: string; description: string; attributes: string[] } | null => {
  if (!isRecord(value)) {
    add(findings, "ORODI_V1_CONTRACT_TYPE", "$.payload", "expected OTel metric declaration object");
    return null;
  }
  exactKeys(value, ["name", "instrument", "unit", "description", "attributes"], "$.payload", findings);
  const stringsValid = ["name", "instrument", "unit", "description"].every((key) =>
    requireString(value[key], `$.payload.${key}`, findings));
  if (typeof value.instrument === "string" && !supportedInstruments.has(value.instrument)) {
    add(findings, "ORODI_V1_INSTRUMENT_UNSUPPORTED", "$.payload.instrument", "unsupported legacy OTel instrument");
  }
  if (!Array.isArray(value.attributes)) {
    add(findings, "ORODI_V1_CONTRACT_ARRAY", "$.payload.attributes", "expected attribute-name array");
    return null;
  }
  const attributes = value.attributes;
  if (attributes.length > 12) {
    add(findings, "ORODI_V1_CARDINALITY_EXCEEDED", "$.payload.attributes", "declared attribute count exceeds replay budget");
  }
  const attributeStrings = attributes.every((entry, index) =>
    requireString(entry, `$.payload.attributes[${index}]`, findings));
  for (const [index, entry] of attributes.entries()) {
    if (typeof entry === "string" && (!attributePattern.test(entry) || unsafeAttributePattern.test(entry))) {
      add(findings, "ORODI_V1_ATTRIBUTE_UNSAFE", `$.payload.attributes[${index}]`, "attribute name is outside the safe legacy replay allowlist");
    }
  }
  if (new Set(attributes).size !== attributes.length) {
    add(findings, "ORODI_V1_CONTRACT_UNIQUE", "$.payload.attributes", "duplicate attribute names are forbidden");
  }
  if (!stringsValid || !attributeStrings || !supportedInstruments.has(String(value.instrument)) ||
      attributes.length > 12 || findings.length > 0) return null;
  return {
    name: value.name as string,
    instrument: value.instrument as string,
    unit: value.unit as string,
    description: value.description as string,
    attributes: attributes as string[],
  };
};

export const normalizeLegacyV1 = (
  rawInput: unknown,
  inventory: LegacyV1SourceInventory,
  replayedAt: string,
): LegacyV1NormalizationResult => {
  const findings: LegacyV1NormalizationFinding[] = [];
  const timestampValid = typeof replayedAt === "string" && rfc3339Pattern.test(replayedAt) && Number.isFinite(Date.parse(replayedAt));
  if (!timestampValid) {
    add(findings, "ORODI_V1_REPLAY_TIME_INVALID", "$replayed_at", "expected explicit RFC 3339 date-time");
  }

  if (!isRecord(rawInput)) {
    add(findings, "ORODI_V1_CONTRACT_TYPE", "$", "expected adapter input object");
    return rejected("invalid-input", "unknown", null, replayedAt, findings);
  }
  exactKeys(rawInput, ["schema_version", "input_id", "source_shape_id", "source", "payload"], "$", findings);
  if (rawInput.schema_version !== "domainspec.orodi.legacy-v1-adapter-input/v1") {
    add(findings, "ORODI_V1_CONTRACT_LITERAL", "$.schema_version", "unexpected adapter input schema");
  }
  const inputId = typeof rawInput.input_id === "string" ? rawInput.input_id : "invalid-input";
  const shapeId = typeof rawInput.source_shape_id === "string" ? rawInput.source_shape_id : "unknown";
  if (!requireString(rawInput.input_id, "$.input_id", findings) || !idPattern.test(inputId)) {
    add(findings, "ORODI_V1_INPUT_ID_INVALID", "$.input_id", "expected stable lower-case identifier");
  }
  requireString(rawInput.source_shape_id, "$.source_shape_id", findings);
  const source = sourceFromUnknown(rawInput.source, findings);
  if (source === null || findings.length > 0) return rejected(inputId, shapeId, source, replayedAt, findings);

  const input = rawInput as unknown as LegacyV1AdapterInput;
  const shape = matchSource(input, inventory, source, findings);
  if (shape === null || findings.length > 0 || !timestampValid) {
    return rejected(inputId, shapeId, source, replayedAt, findings);
  }

  if (shape.adapter_disposition === "reject-workflow-plane") {
    add(findings, "ORODI_V1_WORKFLOW_TELEMETRY_FORBIDDEN", "$.source_shape_id", "workflow telemetry cannot satisfy product evidence");
    return rejected(inputId, shapeId, source, replayedAt, findings);
  }
  if (shape.adapter_disposition === "reject-not-observed-evidence") {
    add(findings, "ORODI_V1_SOURCE_FAMILY_NOT_EVIDENCE", "$.source_shape_id", "policy or configuration declaration is not an observation");
    return rejected(inputId, shapeId, source, replayedAt, findings);
  }
  if (shape.adapter_disposition === "reject-proposal-only") {
    add(findings, "ORODI_V1_SOURCE_FAMILY_PROPOSAL_ONLY", "$.source_shape_id", "procedure or proposal is not execution evidence");
    return rejected(inputId, shapeId, source, replayedAt, findings);
  }
  if (shape.adapter_disposition === "reject-family-absent") {
    add(findings, "ORODI_V1_SOURCE_FAMILY_ABSENT", "$.source_shape_id", "legacy v1 has no admitted evidence shape for this family");
    return rejected(inputId, shapeId, source, replayedAt, findings);
  }

  if (shape.shape_id === "legacy-v1.failure-mapping-row/v1") {
    const payload = validateFailurePayload(input.payload, findings);
    if (payload === null || findings.length > 0) return rejected(inputId, shapeId, source, replayedAt, findings);
    const attributes = {
      "failure.code": payload.code,
      "failure.condition": payload.condition,
      "failure.error_type": payload.error_type,
      "failure.retryable": String(payload.retryable),
      "legacy.family": shape.shape_id,
    };
    return normalized(input, source, replayedAt, makeObservation(input, source, replayedAt, "log", attributes));
  }

  if (shape.shape_id === "legacy-v1.otel-metric-declaration/v1") {
    const payload = validateMetricPayload(input.payload, findings);
    if (payload === null || findings.length > 0) return rejected(inputId, shapeId, source, replayedAt, findings);
    const attributes = {
      "legacy.family": shape.shape_id,
      "metric.attributes": payload.attributes.join(","),
      "metric.description": payload.description,
      "metric.instrument": payload.instrument,
      "metric.name": payload.name,
      "metric.unit": payload.unit,
    };
    return normalized(input, source, replayedAt, makeObservation(input, source, replayedAt, "metric", attributes));
  }

  add(findings, "ORODI_V1_SOURCE_SHAPE_UNKNOWN", "$.source_shape_id", "normalizable shape has no implementation");
  return rejected(inputId, shapeId, source, replayedAt, findings);
};
