import type { ToolEvidenceProfile } from "../contracts/tool-evidence-profile.js";
import {
  TOOL_EVIDENCE_PROFILE_REPLAY_FAMILIES,
  type ToolEvidenceProfileNormalizerInput,
  type ToolEvidenceProfileNormalizerOutput,
  type ToolEvidenceProfileNormalizerRegistryEntry,
  type ToolEvidenceProfileReplayFinding,
  type ToolEvidenceProfileReplayFamily,
} from "../contracts/tool-evidence-profile-replay.js";

const NORMALIZER_REF = "orodi://normalizer/pure-profile/v1" as const;
const NORMALIZER_VERSION = "1.0.0" as const;
const NORMALIZER_SHA256 =
  "d6a45d4e99806fca19e5d683d9fc0c7b216f9d57706a87ae5112b32dbabe92ca" as const;

const kindByFamily = Object.freeze({
  telemetry: "metric",
  "health-failure": "health",
  workload: "metric",
  fault: "log",
  "canary-analysis": "metric",
  "deployment-observation": "log",
  "rollback-observation": "log",
} as const);

const entry = (familyId: ToolEvidenceProfileReplayFamily): ToolEvidenceProfileNormalizerRegistryEntry =>
  Object.freeze({
    family_id: familyId,
    normalizer: Object.freeze({
      ref: NORMALIZER_REF,
      version: NORMALIZER_VERSION,
      sha256: NORMALIZER_SHA256,
    }),
    normalizer_id: `domainspec.orodi.tool-profile-normalizer.${familyId}`,
    normalizer_version: "1.0.0-candidate-local",
    observation_kind: kindByFamily[familyId],
  });

export const TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY = Object.freeze(
  TOOL_EVIDENCE_PROFILE_REPLAY_FAMILIES.map(entry),
);

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const finding = (code: string, path: string, detail: string): ToolEvidenceProfileReplayFinding =>
  Object.freeze({ code, path, detail });

const ordered = (
  findings: readonly ToolEvidenceProfileReplayFinding[],
): readonly ToolEvidenceProfileReplayFinding[] => Object.freeze([...findings].sort((left, right) =>
  left.path.localeCompare(right.path) || left.code.localeCompare(right.code) ||
  left.detail.localeCompare(right.detail)));

export const validateToolEvidenceProfileNormalizerRegistry = (
  candidate: unknown,
): readonly ToolEvidenceProfileReplayFinding[] => {
  const findings: ToolEvidenceProfileReplayFinding[] = [];
  if (!Array.isArray(candidate)) {
    return Object.freeze([finding("NORMALIZER_REGISTRY_SHAPE_INVALID", "$registry", "expected an array")]);
  }
  if (candidate.length !== TOOL_EVIDENCE_PROFILE_REPLAY_FAMILIES.length) {
    findings.push(finding(
      "NORMALIZER_REGISTRY_CARDINALITY_INVALID",
      "$registry",
      "registry must contain exactly seven entries",
    ));
  }

  const tuples = new Set<string>();
  const families = new Set<string>();
  candidate.forEach((rawEntry, index) => {
    const path = `$registry[${index}]`;
    if (!isRecord(rawEntry)) {
      findings.push(finding("NORMALIZER_REGISTRY_SHAPE_INVALID", path, "expected an object"));
      return;
    }
    const keys = ["family_id", "normalizer", "normalizer_id", "normalizer_version", "observation_kind"];
    if (Object.keys(rawEntry).some((key) => !keys.includes(key)) || keys.some((key) => !(key in rawEntry))) {
      findings.push(finding("NORMALIZER_REGISTRY_ENTRY_OPEN", path, "entry must use the closed registry shape"));
    }
    if (!TOOL_EVIDENCE_PROFILE_REPLAY_FAMILIES.includes(rawEntry.family_id as ToolEvidenceProfileReplayFamily)) {
      findings.push(finding("NORMALIZER_REGISTRY_FAMILY_UNKNOWN", `${path}.family_id`, "family is not registered"));
    }
    if (!isRecord(rawEntry.normalizer)) {
      findings.push(finding("NORMALIZER_REGISTRY_TUPLE_UNKNOWN", `${path}.normalizer`, "normalizer tuple is absent"));
      return;
    }
    const normalizer = rawEntry.normalizer;
    const tuple = [rawEntry.family_id, normalizer.ref, normalizer.version, normalizer.sha256].join("|");
    if (tuples.has(tuple)) {
      findings.push(finding("NORMALIZER_REGISTRY_TUPLE_DUPLICATE", path, "normalizer tuple is duplicated"));
    }
    tuples.add(tuple);
    if (families.has(String(rawEntry.family_id))) {
      findings.push(finding("NORMALIZER_REGISTRY_FAMILY_DUPLICATE", `${path}.family_id`, "family entry is duplicated"));
    }
    families.add(String(rawEntry.family_id));
    if (normalizer.ref !== NORMALIZER_REF || normalizer.version !== NORMALIZER_VERSION ||
        normalizer.sha256 !== NORMALIZER_SHA256) {
      findings.push(finding("NORMALIZER_REGISTRY_TUPLE_UNKNOWN", `${path}.normalizer`, "tuple is not pinned"));
    }
    const family = rawEntry.family_id as ToolEvidenceProfileReplayFamily;
    if (kindByFamily[family] !== rawEntry.observation_kind) {
      findings.push(finding("NORMALIZER_REGISTRY_KIND_MISMATCH", `${path}.observation_kind`, "kind does not match family projection"));
    }
    if (rawEntry.normalizer_version !== "1.0.0-candidate-local" ||
        typeof rawEntry.normalizer_id !== "string" || rawEntry.normalizer_id.length === 0) {
      findings.push(finding("NORMALIZER_REGISTRY_IDENTITY_INVALID", path, "compiled normalizer identity is invalid"));
    }
  });

  for (const familyId of TOOL_EVIDENCE_PROFILE_REPLAY_FAMILIES) {
    if (!families.has(familyId)) {
      findings.push(finding("NORMALIZER_REGISTRY_FAMILY_MISSING", "$registry", `${familyId} is missing`));
    }
  }
  return ordered(findings);
};

export const selectToolEvidenceProfileNormalizer = (
  profile: ToolEvidenceProfile,
): ToolEvidenceProfileNormalizerRegistryEntry | null => {
  const matches = TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY.filter((candidate) =>
    candidate.family_id === profile.family_id &&
    candidate.normalizer.ref === profile.normalizer.ref &&
    candidate.normalizer.version === profile.normalizer.version &&
    candidate.normalizer.sha256 === profile.normalizer.sha256);
  return matches.length === 1 ? matches[0] : null;
};

export const runToolEvidenceProfileNormalizer = (
  input: ToolEvidenceProfileNormalizerInput,
): ToolEvidenceProfileNormalizerOutput => {
  const attributes = Object.freeze(Object.fromEntries(
    Object.entries(input.profile.mapping.attribute_value_templates)
      .sort(([left], [right]) => left.localeCompare(right)),
  ));
  const attributeAllowlist = Object.freeze(Object.keys(attributes));
  const observation = Object.freeze({
    schema_version: "domainspec.orodi.observation/v1" as const,
    observation_id: `orodi.profile-replay.${input.replay_id}.${input.profile.family_id}`,
    plane: "product" as const,
    kind: input.registry_entry.observation_kind,
    mode: "simulation" as const,
    correlation_id: input.replay_id,
    attributes,
    attribute_allowlist: attributeAllowlist,
    cardinality: Object.freeze({
      observed: new Set(Object.values(attributes)).size,
      budget: input.profile.mapping.output_constraints.cardinality_budget,
    }),
    telemetry: Object.freeze({
      offered: 0,
      queued: 0,
      exported: 0,
      rejected: 0,
      dropped: 0,
      pending: 0,
      partial_success: 0,
    }),
    deployment_effect: false,
    independently_observed: false,
    observed_at: input.fixture.replayed_at,
    invalidation_key_digest: input.fixture.invalidation_key_digest,
  });
  return Object.freeze({ observation, selected_value_sha256: input.selected_value_sha256 });
};
