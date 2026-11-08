import { createHash } from "node:crypto";

import type {
  ToolEvidenceProfile,
  ToolEvidenceProfileFinding,
  ToolEvidenceProfileValidationResult,
} from "../contracts/tool-evidence-profile.js";
import {
  type DecodedToolEvidenceProfileReplayInputs,
  type ToolEvidenceProfileNormalizationResult,
  type ToolEvidenceProfileReplayFinding,
  type ToolEvidenceProfileReplayFixture,
  type ToolEvidenceProfileReplayInputs,
  type ToolEvidenceProfileReplayResult,
  type ToolProfileNormalizerCandidateValidation,
} from "../contracts/tool-evidence-profile-replay.js";
import { evaluateToolProfileEvidenceEligibility } from "./evaluate-evidence-eligibility.js";
import {
  runToolEvidenceProfileNormalizer,
  selectToolEvidenceProfileNormalizer,
  TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY,
  validateToolEvidenceProfileNormalizerRegistry,
} from "./tool-evidence-profile-normalizer-registry.js";
import { validateToolEvidenceProfile } from "./validate-tool-evidence-profile.js";

type JsonRecord = Record<string, unknown>;
type AddFinding = (code: string, path: string, detail: string) => void;

const sha256Pattern = /^[0-9a-f]{64}$/;
const rfc3339UtcPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;

const toBytes = (value: Uint8Array | string): Uint8Array =>
  typeof value === "string" ? new TextEncoder().encode(value) : value;

const digest = (value: Uint8Array | string): string =>
  createHash("sha256").update(toBytes(value)).digest("hex");

const digestJson = (value: unknown): string => digest(canonicalJson(value));

const isRecord = (value: unknown): value is JsonRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const canonicalJson = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (isRecord(value)) return `{${Object.keys(value).sort().map((key) =>
    `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  const encoded = JSON.stringify(value);
  return encoded === undefined ? "null" : encoded;
};

const finding = (code: string, path: string, detail: string): ToolEvidenceProfileReplayFinding =>
  Object.freeze({ code, path, detail });

const orderedFindings = (
  findings: readonly ToolEvidenceProfileReplayFinding[],
): readonly ToolEvidenceProfileReplayFinding[] => Object.freeze(
  [...new Map(findings.map((item) => [`${item.path}\u0000${item.code}\u0000${item.detail}`, item])).values()]
    .sort((left, right) => left.path.localeCompare(right.path) ||
      left.code.localeCompare(right.code) || left.detail.localeCompare(right.detail)),
);

const scanForDuplicateKeys = (text: string, rootPath: string, add: AddFinding): void => {
  let cursor = 0;
  const whitespace = (): void => { while (/\s/.test(text[cursor] ?? "")) cursor += 1; };
  const readString = (): string => {
    const start = cursor;
    cursor += 1;
    while (cursor < text.length) {
      if (text[cursor] === "\\") cursor += 2;
      else {
        const char = text[cursor];
        cursor += 1;
        if (char === '"') break;
      }
    }
    return JSON.parse(text.slice(start, cursor)) as string;
  };
  const parseValue = (path: string): void => {
    whitespace();
    if (text[cursor] === "{") {
      cursor += 1;
      whitespace();
      const keys = new Set<string>();
      if (text[cursor] === "}") { cursor += 1; return; }
      while (cursor < text.length) {
        whitespace();
        const key = readString();
        if (keys.has(key)) add("REPLAY_JSON_DUPLICATE_OBJECT_KEY", `${path}/${key}`, "duplicate keys are forbidden");
        keys.add(key);
        whitespace();
        cursor += 1;
        parseValue(`${path}/${key.replaceAll("~", "~0").replaceAll("/", "~1")}`);
        whitespace();
        if (text[cursor] === "}") { cursor += 1; return; }
        cursor += 1;
      }
      return;
    }
    if (text[cursor] === "[") {
      cursor += 1;
      whitespace();
      if (text[cursor] === "]") { cursor += 1; return; }
      let index = 0;
      while (cursor < text.length) {
        parseValue(`${path}/${index}`);
        index += 1;
        whitespace();
        if (text[cursor] === "]") { cursor += 1; return; }
        cursor += 1;
      }
      return;
    }
    if (text[cursor] === '"') { readString(); return; }
    while (cursor < text.length && !/[\s,\]}]/.test(text[cursor] ?? "")) cursor += 1;
  };
  parseValue(rootPath);
};

const parseExactJson = (input: Uint8Array | string, path: string, add: AddFinding): unknown => {
  let text: string;
  try {
    text = typeof input === "string" ? input : new TextDecoder("utf-8", { fatal: true }).decode(input);
  } catch {
    add("REPLAY_JSON_INVALID_UTF8", path, "input is not valid UTF-8");
    return undefined;
  }
  try {
    const value = JSON.parse(text) as unknown;
    scanForDuplicateKeys(text, path, add);
    return value;
  } catch {
    add("REPLAY_JSON_INVALID", path, "input is not one complete JSON value");
    return undefined;
  }
};

const exactKeys = (value: JsonRecord, expected: readonly string[], path: string, add: AddFinding): void => {
  const allowed = new Set(expected);
  expected.forEach((key) => { if (!(key in value)) add("REPLAY_CONTRACT_REQUIRED", `${path}/${key}`, "required field is absent"); });
  Object.keys(value).sort().forEach((key) => {
    if (!allowed.has(key)) add("REPLAY_CONTRACT_CLOSED", `${path}/${key}`, "field is outside the closed contract");
  });
};

const decodeInputs = (
  inputs: ToolEvidenceProfileReplayInputs,
  add: AddFinding,
): DecodedToolEvidenceProfileReplayInputs | null => {
  const values = {
    descriptor: parseExactJson(inputs.descriptor, "/descriptor", add),
    family_inventory: parseExactJson(inputs.family_inventory, "/family_inventory", add),
    attribute_policy: parseExactJson(inputs.attribute_policy, "/attribute_policy", add),
    referent_inventory: parseExactJson(inputs.referent_inventory, "/referent_inventory", add),
    wp5_validation_result: parseExactJson(inputs.wp5_validation_result, "/wp5_validation_result", add),
    fixture: parseExactJson(inputs.fixture, "/fixture", add),
    evaluation_context: parseExactJson(inputs.evaluation_context, "/evaluation_context", add),
  };
  if (!Object.values(values).every(isRecord)) return null;
  return values as unknown as DecodedToolEvidenceProfileReplayInputs;
};

const validateFixture = (
  fixture: ToolEvidenceProfileReplayFixture,
  profile: ToolEvidenceProfile,
  decoded: DecodedToolEvidenceProfileReplayInputs,
  evaluatedAt: string,
  add: AddFinding,
): unknown => {
  const raw = fixture as unknown as JsonRecord;
  exactKeys(raw, [
    "schema_version", "fixture_id", "profile_id", "profile_version", "family_id", "producer",
    "source_bytes_utf8", "source_sha256", "replayed_at", "invalidation_key_digest",
    "execution_mode", "runtime_admission", "authority_effect",
  ], "/fixture", add);
  if (fixture.schema_version !== "domainspec.orodi.tool-evidence-profile-replay-fixture/v1" ||
      fixture.execution_mode !== "offline-fixture-only" || fixture.runtime_admission !== "denied" ||
      fixture.authority_effect !== "none") {
    add("FIXTURE_CONTRACT_LITERAL_INVALID", "/fixture", "fixture ceiling literals are invalid");
  }
  if (fixture.profile_id !== profile.profile_id || fixture.profile_version !== profile.profile_version ||
      fixture.family_id !== profile.family_id) {
    add("FIXTURE_PROFILE_FAMILY_MISMATCH", "/fixture", "fixture does not bind the validated profile identity");
  }
  if (!isRecord(fixture.producer)) {
    add("FIXTURE_PRODUCER_INVALID", "/fixture/producer", "producer reference must be an object");
  } else {
    exactKeys(fixture.producer as unknown as JsonRecord, ["ref", "version", "sha256", "role"], "/fixture/producer", add);
    if (fixture.producer.role !== "producer" || fixture.producer.ref !== profile.producer.ref ||
        fixture.producer.version !== profile.producer.version || fixture.producer.sha256 !== profile.producer.sha256) {
      add("FIXTURE_PRODUCER_REF_MISMATCH", "/fixture/producer", "producer tuple does not match the descriptor");
    }
  }
  if (typeof fixture.source_bytes_utf8 !== "string" || digest(fixture.source_bytes_utf8) !== fixture.source_sha256 ||
      fixture.source_sha256 !== profile.producer.sha256) {
    add("FIXTURE_SOURCE_DIGEST_MISMATCH", "/fixture/source_sha256", "source bytes do not match the pinned producer digest");
  }
  const producerReferents = decoded.referent_inventory.referents.filter((referent) =>
    referent.ref === profile.producer.ref && referent.role === "producer" &&
    referent.version === profile.producer.version && referent.sha256 === profile.producer.sha256);
  if (producerReferents.length !== 1 || producerReferents[0]?.bytes_utf8 !== fixture.source_bytes_utf8) {
    add("FIXTURE_PRODUCER_REFERENT_MISMATCH", "/fixture/source_bytes_utf8", "fixture bytes do not equal the sole producer referent");
  }
  if (fixture.invalidation_key_digest !== profile.invalidation_key_digest) {
    add("INVALIDATION_KEY_MISMATCH", "/fixture/invalidation_key_digest", "fixture invalidation key does not match the profile");
  }
  if (!rfc3339UtcPattern.test(fixture.replayed_at) || !Number.isFinite(Date.parse(fixture.replayed_at)) ||
      Date.parse(fixture.replayed_at) > Date.parse(evaluatedAt)) {
    add("REPLAY_FROM_FUTURE", "/fixture/replayed_at", "replay time must be explicit and no later than evaluation time");
  }
  const source = parseExactJson(fixture.source_bytes_utf8, "/fixture/source_bytes_utf8", add);
  return source;
};

const resolveSelector = (source: unknown, selector: string): unknown => {
  if (!selector.startsWith("/") || selector.includes("..") || selector.includes("*") || selector.includes("#")) {
    return undefined;
  }
  let current = source;
  for (const encoded of selector.slice(1).split("/")) {
    const token = encoded.replaceAll("~1", "/").replaceAll("~0", "~");
    if (Array.isArray(current)) {
      if (!/^(0|[1-9]\d*)$/.test(token)) return undefined;
      current = current[Number(token)];
    } else if (isRecord(current) && Object.hasOwn(current, token)) {
      current = current[token];
    } else return undefined;
  }
  return current;
};

const valueType = (value: unknown): string => {
  if (Array.isArray(value)) return "array";
  if (value === null) return "null";
  return typeof value;
};

const observationKeys = Object.freeze([
  "schema_version", "observation_id", "plane", "kind", "mode", "correlation_id",
  "attributes", "attribute_allowlist", "cardinality", "telemetry", "deployment_effect",
  "independently_observed", "observed_at", "invalidation_key_digest",
]);

export const validateToolEvidenceProfileNormalizerOutput = (
  candidate: unknown,
  profile: ToolEvidenceProfile,
  fixture: ToolEvidenceProfileReplayFixture,
  replayId: string,
): ToolProfileNormalizerCandidateValidation => {
  const findings: ToolEvidenceProfileReplayFinding[] = [];
  const add: AddFinding = (code, path, detail) => findings.push(finding(code, path, detail));
  let rawObservation: unknown;
  let selectedDigest: unknown;
  if (Array.isArray(candidate)) {
    if (candidate.length === 0) add("NORMALIZER_ZERO_OBSERVATIONS", "$normalizer_output", "normalizer emitted no observation");
    else {
      if (candidate.length > 1) add("NORMALIZER_MULTIPLE_OBSERVATIONS", "$normalizer_output", "normalizer emitted more than one observation");
      const ids = candidate.filter(isRecord).map((item) => item.observation_id).filter((id): id is string => typeof id === "string");
      if (new Set(ids).size !== ids.length) add("DUPLICATE_OBSERVATION_ID", "$normalizer_output", "observation IDs are duplicated");
    }
  } else if (!isRecord(candidate)) {
    const code = typeof candidate === "string" && /^(?:file:|https?:|\/|\.\.?\/)/i.test(candidate)
      ? "PATH_URL_DISCOVERY_PAYLOAD"
      : typeof candidate === "function" || typeof candidate === "string"
        ? "DYNAMIC_LOADER_PAYLOAD" : "NORMALIZER_OUTPUT_SHAPE_INVALID";
    add(code, "$normalizer_output", "normalizer output must be a closed object");
  } else {
    exactKeys(candidate, ["observation", "selected_value_sha256"], "$normalizer_output", add);
    rawObservation = candidate.observation;
    selectedDigest = candidate.selected_value_sha256;
  }
  if (!isRecord(rawObservation)) {
    if (findings.length === 0) add("NORMALIZER_ZERO_OBSERVATIONS", "$normalizer_output/observation", "normalizer emitted no observation");
    return Object.freeze({ observation: null, findings: orderedFindings(findings) });
  }
  exactKeys(rawObservation, observationKeys, "$normalizer_output/observation", add);
  if (selectedDigest !== digestJson(resolveSelector(
    parseExactJson(fixture.source_bytes_utf8, "/fixture/source_bytes_utf8", add),
    profile.mapping.selector,
  ))) add("SELECTED_VALUE_DIGEST_MISMATCH", "$normalizer_output/selected_value_sha256", "selected value digest is not canonical");
  if (rawObservation.schema_version !== "domainspec.orodi.observation/v1" ||
      rawObservation.correlation_id !== replayId || rawObservation.observed_at !== fixture.replayed_at ||
      rawObservation.invalidation_key_digest !== profile.invalidation_key_digest) {
    add("NORMALIZER_OUTPUT_BINDING_MISMATCH", "$normalizer_output/observation", "observation identity does not bind the replay inputs");
  }
  if (rawObservation.plane !== "product") add("WORKFLOW_PLANE_OBSERVATION", "$normalizer_output/observation/plane", "workflow plane is forbidden");
  if (rawObservation.mode !== "simulation") add("LIVE_MODE_OBSERVATION", "$normalizer_output/observation/mode", "live mode is forbidden");
  if (rawObservation.independently_observed !== false) add("INDEPENDENT_OBSERVATION_CLAIM", "$normalizer_output/observation/independently_observed", "independent observation is forbidden");
  if (rawObservation.deployment_effect !== false) add("DEPLOYMENT_EFFECT_CLAIM", "$normalizer_output/observation/deployment_effect", "deployment effect is forbidden");
  const registryEntry = selectToolEvidenceProfileNormalizer(profile);
  if (registryEntry === null || rawObservation.kind !== registryEntry.observation_kind) {
    add("NORMALIZER_OUTPUT_KIND_MISMATCH", "$normalizer_output/observation/kind", "observation kind does not match the static family projection");
  }
  if (typeof rawObservation.observation_id !== "string" || rawObservation.observation_id.length === 0) {
    add("NORMALIZER_OUTPUT_ID_INVALID", "$normalizer_output/observation/observation_id", "observation ID must be non-empty");
  }
  const telemetryKeys = ["offered", "queued", "exported", "rejected", "dropped", "pending", "partial_success"];
  const telemetry = rawObservation.telemetry;
  if (!isRecord(telemetry)) {
    add("NONZERO_TELEMETRY_CLAIM", "$normalizer_output/observation/telemetry", "zero telemetry accounting is required");
  } else {
    exactKeys(telemetry, telemetryKeys, "$normalizer_output/observation/telemetry", add);
    if (telemetryKeys.some((key) => telemetry[key] !== 0)) {
      add("NONZERO_TELEMETRY_CLAIM", "$normalizer_output/observation/telemetry", "all telemetry counters must remain zero");
    }
  }
  const expectedAttributes = Object.keys(profile.mapping.attribute_value_templates).sort();
  const attributes = rawObservation.attributes;
  if (!isRecord(attributes)) {
    add("NORMALIZER_OUTPUT_ATTRIBUTES_INVALID", "$normalizer_output/observation/attributes", "attributes must be an object");
  } else {
    const actual = Object.keys(attributes).sort();
    if (actual.some((key) => /secret|token|password|credential/i.test(key))) {
      add("UNSAFE_ATTRIBUTE_KEY", "$normalizer_output/observation/attributes", "secret-bearing attribute keys are forbidden");
    }
    if (canonicalJson(actual) !== canonicalJson(expectedAttributes) ||
        actual.some((key) => attributes[key] !== profile.mapping.attribute_value_templates[key])) {
      add("NORMALIZER_OUTPUT_ATTRIBUTES_INVALID", "$normalizer_output/observation/attributes", "attributes must equal the validated templates");
    }
  }
  if (!Array.isArray(rawObservation.attribute_allowlist) ||
      canonicalJson([...rawObservation.attribute_allowlist].sort()) !== canonicalJson(expectedAttributes)) {
    add("NORMALIZER_OUTPUT_ALLOWLIST_MISMATCH", "$normalizer_output/observation/attribute_allowlist", "allowlist must equal the attribute keys");
  }
  if (!isRecord(rawObservation.cardinality) ||
      rawObservation.cardinality.budget !== profile.mapping.output_constraints.cardinality_budget ||
      typeof rawObservation.cardinality.observed !== "number" ||
      rawObservation.cardinality.observed > profile.mapping.output_constraints.cardinality_budget) {
    add("ATTRIBUTE_CARDINALITY_EXCEEDED", "$normalizer_output/observation/cardinality", "cardinality must remain within the declared budget");
  }
  const finalFindings = orderedFindings(findings);
  return Object.freeze({
    observation: finalFindings.length === 0
      ? rawObservation as unknown as NonNullable<ToolProfileNormalizerCandidateValidation["observation"]>
      : null,
    findings: finalFindings,
  });
};

const safeIdentity = (result: ToolEvidenceProfileValidationResult): Readonly<{
  profileId: string;
  profileVersion: string;
  familyId: "telemetry" | "health-failure" | "workload" | "fault" | "canary-analysis" | "deployment-observation" | "rollback-observation";
}> => {
  const families = ["telemetry", "health-failure", "workload", "fault", "canary-analysis", "deployment-observation", "rollback-observation"] as const;
  return Object.freeze({
    profileId: result.profile_id || "invalid-profile",
    profileVersion: result.profile_version || "invalid-version",
    familyId: families.includes(result.family_id as (typeof families)[number])
      ? result.family_id as (typeof families)[number] : "telemetry",
  });
};

const rejectedNormalization = (
  inputs: ToolEvidenceProfileReplayInputs,
  wp5: ToolEvidenceProfileValidationResult,
  fixtureId: string,
  findings: readonly ToolEvidenceProfileReplayFinding[],
): ToolEvidenceProfileNormalizationResult => {
  const identity = safeIdentity(wp5);
  return Object.freeze({
    schema_version: "domainspec.orodi.tool-evidence-profile-normalization-result/v1",
    normalizer_id: "domainspec.orodi.tool-profile-normalizer.rejected",
    normalizer_version: "1.0.0-candidate-local",
    registry_entry: null,
    replay_id: inputs.replay_id || "invalid-replay",
    profile_id: identity.profileId,
    profile_version: identity.profileVersion,
    family_id: identity.familyId,
    fixture_id: fixtureId || "invalid-fixture",
    descriptor_sha256: digest(inputs.descriptor),
    wp5_result_sha256: digest(inputs.wp5_validation_result),
    source_sha256: sha256Pattern.test(digest(inputs.fixture)) ? digest(inputs.fixture) : "0".repeat(64),
    selected_value_sha256: null,
    invalidation_key_digest: isRecord(parseExactJson(inputs.descriptor, "/descriptor-rejection", () => undefined)) &&
      typeof (parseExactJson(inputs.descriptor, "/descriptor-rejection", () => undefined) as JsonRecord).invalidation_key_digest === "string"
      ? String((parseExactJson(inputs.descriptor, "/descriptor-rejection", () => undefined) as JsonRecord).invalidation_key_digest)
      : "0".repeat(64),
    replayed_at: inputs.evaluated_at,
    verdict: "rejected",
    observations: Object.freeze([]),
    findings: orderedFindings(findings),
    runtime_admission: "denied",
    referent_trust: "unverified",
    authority_effect: "none",
  });
};

const rejectedReplay = (
  inputs: ToolEvidenceProfileReplayInputs,
  wp5: ToolEvidenceProfileValidationResult,
  fixtureId: string,
  findings: readonly ToolEvidenceProfileReplayFinding[],
): ToolEvidenceProfileReplayResult => Object.freeze({
  schema_version: "domainspec.orodi.tool-evidence-profile-replay-result/v1",
  replayer_id: "domainspec.orodi.tool-evidence-profile-replayer",
  replayer_version: "1.0.0-candidate-local",
  evidence_lane: "candidate-local-prototype",
  replay_id: inputs.replay_id || "invalid-replay",
  evaluated_at: inputs.evaluated_at,
  input_digests: Object.freeze({
    descriptor_sha256: digest(inputs.descriptor),
    family_inventory_sha256: digest(inputs.family_inventory),
    attribute_policy_sha256: digest(inputs.attribute_policy),
    referent_inventory_sha256: digest(inputs.referent_inventory),
    wp5_result_sha256: digest(inputs.wp5_validation_result),
    fixture_sha256: digest(inputs.fixture),
    evaluation_context_sha256: digest(inputs.evaluation_context),
  }),
  wp5_validation: wp5,
  normalization: rejectedNormalization(inputs, wp5, fixtureId, findings),
  eligibility: null,
  verdict: "rejected",
  runtime_admission: "denied",
  referent_trust: "unverified",
  findings: orderedFindings(findings),
  authority_effect: "none",
});

const translatedWp5Finding = (item: ToolEvidenceProfileFinding): ToolEvidenceProfileReplayFinding => {
  const aliases: Readonly<Record<string, string>> = Object.freeze({
    PROFILE_PRODUCER_NORMALIZER_ROLE_COLLAPSE: "NORMALIZER_ROLE_COLLAPSE",
    PROFILE_NORMALIZER_ROLE_INVALID: "NORMALIZER_ROLE_COLLAPSE",
    PROFILE_SELECTOR_MISSING: "SELECTOR_MISSING",
    PROFILE_SELECTOR_TYPE_MISMATCH: "SELECTOR_TYPE_MISMATCH",
    PROFILE_BINDING_EXPIRED: "PROFILE_EXPIRED_AT_EQUALITY",
  });
  return finding(aliases[item.code] ?? item.code, item.path, item.detail);
};

export const replayToolEvidenceProfile = (
  inputs: ToolEvidenceProfileReplayInputs,
): ToolEvidenceProfileReplayResult => {
  const findings: ToolEvidenceProfileReplayFinding[] = [];
  const add: AddFinding = (code, path, detail) => findings.push(finding(code, path, detail));
  const wp5 = validateToolEvidenceProfile({
    descriptor: inputs.descriptor,
    family_inventory: inputs.family_inventory,
    attribute_policy: inputs.attribute_policy,
    referent_inventory: inputs.referent_inventory,
    evaluated_at: inputs.evaluated_at,
  });
  const decoded = decodeInputs(inputs, add);
  const suppliedRaw = parseExactJson(inputs.wp5_validation_result, "/wp5_validation_result", add);
  const fixtureId = decoded?.fixture.fixture_id ?? "invalid-fixture";

  if (!rfc3339UtcPattern.test(inputs.evaluated_at) || !Number.isFinite(Date.parse(inputs.evaluated_at))) {
    add("REPLAY_EVALUATION_TIME_INVALID", "/evaluated_at", "evaluation time must be explicit RFC3339 UTC");
  }
  const registryFindings = validateToolEvidenceProfileNormalizerRegistry(
    TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY,
  );
  findings.push(...registryFindings);
  if (!isRecord(suppliedRaw)) {
    add("WP5_RESULT_ABSENT", "/wp5_validation_result", "a closed WP5 result is required");
  }
  if (wp5.verdict !== "pass" || wp5.profile_state !== "structurally-valid" ||
      wp5.runtime_admission !== "denied" || wp5.referent_trust !== "unverified" ||
      wp5.findings.length !== 0) {
    findings.push(...wp5.findings.map(translatedWp5Finding));
    add("WP5_RESULT_REJECTED", "/wp5_validation", "recomputed WP5 validation did not pass");
  }
  if (isRecord(suppliedRaw)) {
    const supplied = suppliedRaw as unknown as ToolEvidenceProfileValidationResult;
    if (supplied.verdict !== "pass") add("WP5_RESULT_REJECTED", "/wp5_validation_result/verdict", "supplied WP5 result is not a pass");
    const driftChecks: ReadonlyArray<readonly [unknown, string, string]> = [
      [supplied.descriptor_sha256, digest(inputs.descriptor), "DESCRIPTOR_DIGEST_DRIFT"],
      [supplied.family_inventory_sha256, digest(inputs.family_inventory), "FAMILY_INVENTORY_DRIFT"],
      [supplied.attribute_policy_sha256, digest(inputs.attribute_policy), "ATTRIBUTE_POLICY_DRIFT"],
      [supplied.referent_inventory_sha256, digest(inputs.referent_inventory), "REFERENT_INVENTORY_DRIFT"],
    ];
    driftChecks.forEach(([actual, expected, code]) => {
      if (actual !== expected) add(code, "/wp5_validation_result", "supplied source digest does not match exact input bytes");
    });
    if (canonicalJson(suppliedRaw) !== canonicalJson(wp5)) {
      add("WP5_RESULT_DIGEST_DRIFT", "/wp5_validation_result", "supplied WP5 result differs from recomputation");
    }
  }
  if (decoded === null || findings.length > 0) return rejectedReplay(inputs, wp5, fixtureId, findings);

  const profile = decoded.descriptor;
  const source = validateFixture(decoded.fixture, profile, decoded, inputs.evaluated_at, add);
  const registryEntry = selectToolEvidenceProfileNormalizer(profile);
  if (registryEntry === null) {
    add("NORMALIZER_REGISTRY_TUPLE_UNKNOWN", "/descriptor/normalizer", "no exact static registry tuple exists");
  }
  if (profile.normalizer.role !== "offline-normalizer" || profile.producer.role !== "producer" ||
      profile.normalizer.ref === profile.producer.ref) {
    add("NORMALIZER_ROLE_COLLAPSE", "/descriptor/normalizer", "producer and normalizer roles must remain separate");
  }
  const selectedValue = resolveSelector(source, profile.mapping.selector);
  if (selectedValue === undefined) {
    add("SELECTOR_MISSING", "/descriptor/mapping/selector", "selector does not resolve in fixture bytes");
  } else if (valueType(selectedValue) !== profile.mapping.selector_value_type) {
    add("SELECTOR_TYPE_MISMATCH", "/descriptor/mapping/selector_value_type", "selected value type does not match the profile");
  }
  if (registryEntry === null || selectedValue === undefined || findings.length > 0) {
    return rejectedReplay(inputs, wp5, fixtureId, findings);
  }
  const selectedValueSha256 = digestJson(selectedValue);
  const normalizerOutput = runToolEvidenceProfileNormalizer({
    replay_id: inputs.replay_id,
    profile,
    fixture: decoded.fixture,
    selected_value: selectedValue,
    selected_value_sha256: selectedValueSha256,
    registry_entry: registryEntry,
  });
  const candidate = validateToolEvidenceProfileNormalizerOutput(
    normalizerOutput,
    profile,
    decoded.fixture,
    inputs.replay_id,
  );
  findings.push(...candidate.findings);
  if (candidate.observation === null || findings.length > 0) {
    return rejectedReplay(inputs, wp5, fixtureId, findings);
  }

  const normalization: ToolEvidenceProfileNormalizationResult = Object.freeze({
    schema_version: "domainspec.orodi.tool-evidence-profile-normalization-result/v1",
    normalizer_id: registryEntry.normalizer_id,
    normalizer_version: "1.0.0-candidate-local",
    registry_entry: registryEntry,
    replay_id: inputs.replay_id,
    profile_id: profile.profile_id,
    profile_version: profile.profile_version,
    family_id: registryEntry.family_id,
    fixture_id: decoded.fixture.fixture_id,
    descriptor_sha256: digest(inputs.descriptor),
    wp5_result_sha256: digest(inputs.wp5_validation_result),
    source_sha256: decoded.fixture.source_sha256,
    selected_value_sha256: selectedValueSha256,
    invalidation_key_digest: profile.invalidation_key_digest,
    replayed_at: decoded.fixture.replayed_at,
    verdict: "normalized",
    observations: Object.freeze([candidate.observation]),
    findings: Object.freeze([]),
    runtime_admission: "denied",
    referent_trust: "unverified",
    authority_effect: "none",
  });
  const eligibility = evaluateToolProfileEvidenceEligibility({
    normalization,
    evaluation_context: decoded.evaluation_context,
    evaluated_at: inputs.evaluated_at,
  });
  if (eligibility.decision !== "replay-only") {
    findings.push(...eligibility.findings.map((item) => finding(item.code, item.path, item.detail)));
    return rejectedReplay(inputs, wp5, fixtureId, findings);
  }
  return Object.freeze({
    schema_version: "domainspec.orodi.tool-evidence-profile-replay-result/v1",
    replayer_id: "domainspec.orodi.tool-evidence-profile-replayer",
    replayer_version: "1.0.0-candidate-local",
    evidence_lane: "candidate-local-prototype",
    replay_id: inputs.replay_id,
    evaluated_at: inputs.evaluated_at,
    input_digests: Object.freeze({
      descriptor_sha256: digest(inputs.descriptor),
      family_inventory_sha256: digest(inputs.family_inventory),
      attribute_policy_sha256: digest(inputs.attribute_policy),
      referent_inventory_sha256: digest(inputs.referent_inventory),
      wp5_result_sha256: digest(inputs.wp5_validation_result),
      fixture_sha256: digest(inputs.fixture),
      evaluation_context_sha256: digest(inputs.evaluation_context),
    }),
    wp5_validation: wp5,
    normalization,
    eligibility,
    verdict: "replayed",
    runtime_admission: "denied",
    referent_trust: "unverified",
    findings: Object.freeze([]),
    authority_effect: "none",
  });
};
