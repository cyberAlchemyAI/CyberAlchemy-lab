import { createHash } from "node:crypto";

import {
  TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_ID,
  TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_VERSION,
  type ToolEvidenceReplayCampaignDerivedPartition,
  type ToolEvidenceReplayCampaignFinding,
  type ToolEvidenceReplayCampaignInputs,
  type ToolEvidenceReplayCampaignItemInput,
  type ToolEvidenceReplayCampaignItemReceipt,
  type ToolEvidenceReplayCampaignResult,
} from "../contracts/tool-evidence-replay-campaign.js";
import type {
  ToolEvidenceProfileReplayInputs,
  ToolEvidenceProfileReplayResult,
} from "../contracts/tool-evidence-profile-replay.js";
import type {
  ToolProfileEvidenceEligibilityReceipt,
  ToolProfileEvidenceEligibilityResult,
} from "../contracts/evidence-eligibility.js";
import type { OperationalObservation } from "../contracts/operational-evidence.js";
import { replayToolEvidenceProfile } from "./replay-tool-evidence-profile.js";

type JsonRecord = Record<string, unknown>;
type AddFinding = (code: string, path: string, detail: string) => void;

type CampaignCandidate = Readonly<{
  sort_key: readonly string[];
  item_receipt: ToolEvidenceReplayCampaignItemReceipt;
  replay_observation: OperationalObservation;
  eligibility_receipt: ToolProfileEvidenceEligibilityReceipt;
  derived_partition: ToolEvidenceReplayCampaignDerivedPartition;
}>;

const sha256Pattern = /^[0-9a-f]{64}$/;
const rfc3339UtcPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;
const replayInputKeys = Object.freeze([
  "replay_id", "descriptor", "family_inventory", "attribute_policy", "referent_inventory",
  "wp5_validation_result", "fixture", "evaluation_context", "evaluated_at",
] as const);
const replayByteKeys = Object.freeze([
  "descriptor", "family_inventory", "attribute_policy", "referent_inventory",
  "wp5_validation_result", "fixture", "evaluation_context",
] as const);

const isRecord = (value: unknown): value is JsonRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);

const isBytes = (value: unknown): value is Uint8Array | string =>
  typeof value === "string" || value instanceof Uint8Array;

const toBytes = (value: Uint8Array | string): Uint8Array =>
  typeof value === "string" ? new TextEncoder().encode(value) : value;

const digest = (value: Uint8Array | string): string =>
  createHash("sha256").update(toBytes(value)).digest("hex");

const canonicalJson = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (isRecord(value)) return `{${Object.keys(value).sort().map((key) =>
    `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  const encoded = JSON.stringify(value);
  return encoded === undefined ? "null" : encoded;
};

const digestJson = (value: unknown): string => digest(canonicalJson(value));

const cloneJson = <T>(value: T): T => JSON.parse(canonicalJson(value)) as T;

const deepFreeze = <T>(value: T): T => {
  if (value !== null && typeof value === "object") {
    Object.values(value as Record<string, unknown>).forEach((child) => deepFreeze(child));
    if (!Object.isFrozen(value)) Object.freeze(value);
  }
  return value;
};

const compareText = (left: string, right: string): number =>
  left < right ? -1 : left > right ? 1 : 0;

const compareTuple = (left: readonly string[], right: readonly string[]): number => {
  for (let index = 0; index < Math.max(left.length, right.length); index += 1) {
    const compared = compareText(left[index] ?? "", right[index] ?? "");
    if (compared !== 0) return compared;
  }
  return 0;
};

const campaignFinding = (
  code: string,
  path: string,
  detail: string,
): ToolEvidenceReplayCampaignFinding => ({ code, path, detail });

const orderedFindings = (
  findings: readonly ToolEvidenceReplayCampaignFinding[],
): readonly ToolEvidenceReplayCampaignFinding[] => Object.freeze(
  [...new Map(findings.map((item) => [
    `${item.path}\u0000${item.code}\u0000${item.detail}`,
    item,
  ])).values()].sort((left, right) =>
    compareText(left.path, right.path) || compareText(left.code, right.code) ||
    compareText(left.detail, right.detail)),
);

const exactKeys = (
  value: JsonRecord,
  expected: readonly string[],
  path: string,
  add: AddFinding,
): void => {
  const allowed = new Set(expected);
  expected.forEach((key) => {
    if (!(key in value)) add("CAMPAIGN_INPUT_INVALID", `${path}/${key}`, "required field is absent");
  });
  Object.keys(value).sort().forEach((key) => {
    if (!allowed.has(key)) add("CAMPAIGN_INPUT_INVALID", `${path}/${key}`, "field is outside the closed input contract");
  });
};

const scanForDuplicateKeys = (text: string, rootPath: string, add: AddFinding): void => {
  let cursor = 0;
  const whitespace = (): void => { while (/\s/.test(text[cursor] ?? "")) cursor += 1; };
  const readString = (): string => {
    const start = cursor;
    cursor += 1;
    while (cursor < text.length) {
      if (text[cursor] === "\\") cursor += 2;
      else {
        const character = text[cursor];
        cursor += 1;
        if (character === '"') break;
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
        if (keys.has(key)) {
          add("CAMPAIGN_RESULT_INVALID", `${path}/${key}`, "duplicate JSON object keys are forbidden");
        }
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

const parseSuppliedResult = (
  input: Uint8Array | string,
  path: string,
  add: AddFinding,
): JsonRecord | null => {
  let text: string;
  try {
    text = typeof input === "string" ? input : new TextDecoder("utf-8", { fatal: true }).decode(input);
  } catch {
    add("CAMPAIGN_RESULT_INVALID", path, "supplied result is not valid UTF-8");
    return null;
  }
  try {
    const value = JSON.parse(text) as unknown;
    scanForDuplicateKeys(text, path, add);
    if (!isRecord(value)) {
      add("CAMPAIGN_RESULT_INVALID", path, "supplied result must be one JSON object");
      return null;
    }
    return value;
  } catch {
    add("CAMPAIGN_RESULT_INVALID", path, "supplied result is not one complete JSON value");
    return null;
  }
};

const safeDigest = (value: unknown): string =>
  isBytes(value) ? digest(value) : digestJson(value);

const manifestEntry = (value: unknown): JsonRecord => {
  const item = isRecord(value) ? value : {};
  const replay = isRecord(item.replay_inputs) ? item.replay_inputs : {};
  return {
    item_id: typeof item.item_id === "string" ? item.item_id : "",
    replay_id: typeof replay.replay_id === "string" ? replay.replay_id : "",
    input_digests: {
      descriptor_sha256: safeDigest(replay.descriptor),
      family_inventory_sha256: safeDigest(replay.family_inventory),
      attribute_policy_sha256: safeDigest(replay.attribute_policy),
      referent_inventory_sha256: safeDigest(replay.referent_inventory),
      wp5_result_sha256: safeDigest(replay.wp5_validation_result),
      fixture_sha256: safeDigest(replay.fixture),
      evaluation_context_sha256: safeDigest(replay.evaluation_context),
    },
    supplied_result_sha256: safeDigest(item.supplied_result_bytes),
  };
};

const inputManifestDigest = (value: unknown): string => {
  const input = isRecord(value) ? value : {};
  const entries = (Array.isArray(input.items) ? input.items : [])
    .map(manifestEntry)
    .sort((left, right) => compareText(canonicalJson(left), canonicalJson(right)));
  return digestJson({
    campaign_id: typeof input.campaign_id === "string" ? input.campaign_id : "",
    evaluated_at: typeof input.evaluated_at === "string" ? input.evaluated_at : "",
    items: entries,
    authority_effect: input.authority_effect,
  });
};

const validEvaluationTime = (value: unknown): value is string =>
  typeof value === "string" && rfc3339UtcPattern.test(value) && Number.isFinite(Date.parse(value));

const validateReplayInputs = (
  value: unknown,
  path: string,
  add: AddFinding,
): value is ToolEvidenceProfileReplayInputs => {
  if (!isRecord(value)) {
    add("CAMPAIGN_ITEM_INPUT_INVALID", path, "replay inputs must be a closed object");
    return false;
  }
  exactKeys(value, replayInputKeys, path, (code, findingPath, detail) =>
    add(code === "CAMPAIGN_INPUT_INVALID" ? "CAMPAIGN_ITEM_INPUT_INVALID" : code, findingPath, detail));
  if (typeof value.replay_id !== "string" || value.replay_id.length === 0) {
    add("CAMPAIGN_ITEM_INPUT_INVALID", `${path}/replay_id`, "replay ID must be non-empty");
  }
  if (!validEvaluationTime(value.evaluated_at)) {
    add("CAMPAIGN_ITEM_INPUT_INVALID", `${path}/evaluated_at`, "evaluation time must be explicit RFC3339 UTC");
  }
  replayByteKeys.forEach((key) => {
    if (!isBytes(value[key])) {
      add("CAMPAIGN_ITEM_INPUT_INVALID", `${path}/${key}`, "replay input must be exact UTF-8 bytes or a string");
    }
  });
  return typeof value.replay_id === "string" && value.replay_id.length > 0 &&
    validEvaluationTime(value.evaluated_at) && replayByteKeys.every((key) => isBytes(value[key])) &&
    Object.keys(value).length === replayInputKeys.length;
};

const arrayRecord = (value: unknown): readonly JsonRecord[] =>
  Array.isArray(value) ? value.filter(isRecord) : [];

const validateObservationCeiling = (
  value: JsonRecord,
  path: string,
  add: AddFinding,
): void => {
  if (value.mode === "live") {
    add("CAMPAIGN_LIVE_OBSERVATION_FORGED", `${path}/mode`, "live observations are forbidden in replay campaigns");
  }
  if (value.deployment_effect !== false || value.kind === "deployment-effect" || value.kind === "rollback-effect") {
    add("CAMPAIGN_EFFECT_OBSERVATION_FORGED", `${path}/deployment_effect`, "effect observations are forbidden");
  }
  if (value.independently_observed !== false) {
    add("CAMPAIGN_INDEPENDENT_OBSERVATION_FORGED", `${path}/independently_observed`, "replay observations are not independently observed");
  }
  if (value.plane !== "product") {
    add("CAMPAIGN_RUNTIME_OBSERVATION_FORGED", `${path}/plane`, "replay observations must remain product-plane audit evidence");
  }
  const telemetry = isRecord(value.telemetry) ? value.telemetry : {};
  if (Object.values(telemetry).some((count) => typeof count !== "number" || count !== 0)) {
    add("CAMPAIGN_RUNTIME_OBSERVATION_FORGED", `${path}/telemetry`, "replay telemetry accounting must remain zero");
  }
};

const validateSuppliedCeiling = (
  result: JsonRecord,
  path: string,
  campaignEvaluatedAt: string,
  add: AddFinding,
): void => {
  const normalization = isRecord(result.normalization) ? result.normalization : null;
  const eligibility = isRecord(result.eligibility) ? result.eligibility : null;
  if (result.evaluated_at !== campaignEvaluatedAt ||
      (eligibility !== null && eligibility.evaluated_at !== campaignEvaluatedAt)) {
    add("CAMPAIGN_EVALUATION_TIME_MISMATCH", `${path}/evaluated_at`, "supplied result evaluation time differs from the campaign");
  }
  if (result.runtime_admission !== "denied" || normalization?.runtime_admission !== "denied" ||
      (eligibility !== null && eligibility.runtime_admission !== "denied")) {
    add("CAMPAIGN_RUNTIME_ADMISSION_FORGED", `${path}/runtime_admission`, "runtime admission must remain denied");
  }
  if (result.referent_trust !== "unverified" || normalization?.referent_trust !== "unverified" ||
      (eligibility !== null && eligibility.referent_trust !== "unverified")) {
    add("CAMPAIGN_REFERENT_TRUST_FORGED", `${path}/referent_trust`, "referent trust must remain unverified");
  }
  if (result.authority_effect !== "none" || normalization?.authority_effect !== "none" ||
      (eligibility !== null && eligibility.authority_effect !== "none")) {
    add("CAMPAIGN_AUTHORITY_EFFECT_FORGED", `${path}/authority_effect`, "authority effect must remain none");
  }
  if (eligibility === null) {
    add("CAMPAIGN_ELIGIBILITY_MISSING", `${path}/eligibility`, "supplied replay eligibility is absent");
    return;
  }
  if (eligibility.decision === "rejected") {
    add("CAMPAIGN_ELIGIBILITY_REJECTED", `${path}/eligibility/decision`, "supplied replay eligibility is rejected");
  } else if (eligibility.decision !== "replay-only") {
    add("CAMPAIGN_ELIGIBILITY_REJECTED", `${path}/eligibility/decision`, "supplied eligibility must remain replay-only");
  }
  if (!Array.isArray(eligibility.runtime_admitted_observations) || eligibility.runtime_admitted_observations.length !== 0) {
    add("CAMPAIGN_RUNTIME_OBSERVATION_FORGED", `${path}/eligibility/runtime_admitted_observations`, "runtime-admitted observations must remain empty");
  }
  arrayRecord(eligibility.eligibility_receipts).forEach((receipt, index) => {
    if (receipt.authority_effect !== "none") {
      add("CAMPAIGN_AUTHORITY_EFFECT_FORGED", `${path}/eligibility/eligibility_receipts/${index}/authority_effect`, "receipt authority effect must remain none");
    }
    if (!Array.isArray(receipt.eligible_controls) || receipt.eligible_controls.length !== 0) {
      add("CAMPAIGN_ELIGIBLE_CONTROLS_FORGED", `${path}/eligibility/eligibility_receipts/${index}/eligible_controls`, "replay-only receipts cannot make controls eligible");
    }
  });
  const observations = [
    ...arrayRecord(normalization?.observations),
    ...arrayRecord(eligibility.replay_observations),
    ...arrayRecord(eligibility.runtime_admitted_observations),
  ];
  observations.forEach((observation, index) =>
    validateObservationCeiling(observation, `${path}/observations/${index}`, add));
  const derived = isRecord(eligibility.derived_result) ? eligibility.derived_result : null;
  if (derived?.authority_effect !== "none") {
    add("CAMPAIGN_AUTHORITY_EFFECT_FORGED", `${path}/eligibility/derived_result/authority_effect`, "derived-result authority effect must remain none");
  }
};

const duplicateFindings = (
  candidates: readonly CampaignCandidate[],
  add: AddFinding,
): void => {
  const checks = [
    ["replay_id", "CAMPAIGN_REPLAY_ID_DUPLICATE"],
    ["family_id", "CAMPAIGN_FAMILY_DUPLICATE"],
    ["profile_identity", "CAMPAIGN_PROFILE_IDENTITY_DUPLICATE"],
    ["binding_id", "CAMPAIGN_BINDING_ID_DUPLICATE"],
    ["observation_id", "CAMPAIGN_OBSERVATION_ID_DUPLICATE"],
  ] as const;
  checks.forEach(([field, code]) => {
    const seen = new Set<string>();
    candidates.forEach(({ item_receipt: receipt }, index) => {
      const value = field === "profile_identity"
        ? `${receipt.profile_id}\u0000${receipt.profile_version}`
        : String(receipt[field]);
      if (seen.has(value)) add(code, `/items/${index}/${field}`, `${field.replaceAll("_", " ")} must be unique across the campaign`);
      seen.add(value);
    });
  });
};

const rejectedResult = (
  campaignId: string,
  evaluatedAt: string,
  manifestSha256: string,
  findings: readonly ToolEvidenceReplayCampaignFinding[],
): ToolEvidenceReplayCampaignResult => deepFreeze({
  schema_version: "domainspec.orodi.tool-evidence-replay-campaign-result/v1",
  composer_id: TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_ID,
  composer_version: TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_VERSION,
  evidence_lane: "candidate-local-prototype",
  campaign_id: campaignId,
  evaluated_at: evaluatedAt,
  input_manifest_sha256: manifestSha256,
  item_receipts: [],
  replay_observations: [],
  eligibility_receipts: [],
  per_binding_derived_results: [],
  runtime_admitted_observations: [],
  eligible_controls: [],
  verdict: "rejected",
  findings: orderedFindings(findings),
  runtime_admission: "denied",
  referent_trust: "unverified",
  authority_effect: "none",
});

const safeCampaignId = (value: unknown): string =>
  isRecord(value) && typeof value.campaign_id === "string" && value.campaign_id.length > 0
    ? value.campaign_id
    : "invalid-campaign";

const safeEvaluatedAt = (value: unknown): string =>
  isRecord(value) && validEvaluationTime(value.evaluated_at)
    ? value.evaluated_at
    : "1970-01-01T00:00:00Z";

export const composeToolEvidenceReplayCampaign = (
  inputs: ToolEvidenceReplayCampaignInputs,
): ToolEvidenceReplayCampaignResult => {
  const rawInput = inputs as unknown;
  const findings: ToolEvidenceReplayCampaignFinding[] = [];
  const add: AddFinding = (code, path, detail) => findings.push(campaignFinding(code, path, detail));
  const campaignId = safeCampaignId(rawInput);
  const evaluatedAt = safeEvaluatedAt(rawInput);
  const manifestSha256 = inputManifestDigest(rawInput);

  if (!isRecord(rawInput)) {
    add("CAMPAIGN_INPUT_INVALID", "$", "campaign input must be a closed object");
    return rejectedResult(campaignId, evaluatedAt, manifestSha256, findings);
  }
  exactKeys(rawInput, ["campaign_id", "evaluated_at", "items", "authority_effect"], "$", add);
  if (typeof rawInput.campaign_id !== "string" || rawInput.campaign_id.length === 0) {
    add("CAMPAIGN_INPUT_INVALID", "/campaign_id", "campaign ID must be non-empty");
  }
  if (!validEvaluationTime(rawInput.evaluated_at)) {
    add("CAMPAIGN_INPUT_INVALID", "/evaluated_at", "campaign evaluation time must be explicit RFC3339 UTC");
  }
  if (rawInput.authority_effect !== "none") {
    add("CAMPAIGN_AUTHORITY_EFFECT_FORGED", "/authority_effect", "campaign authority effect must remain none");
  }
  if (!Array.isArray(rawInput.items) || rawInput.items.length < 2 || rawInput.items.length > 7) {
    add("CAMPAIGN_ITEM_COUNT_INVALID", "/items", "campaign must contain between two and seven items");
  }

  const rawItems = Array.isArray(rawInput.items) ? rawInput.items : [];
  const items: ToolEvidenceReplayCampaignItemInput[] = [];
  const itemIds = new Set<string>();
  rawItems.forEach((rawItem, index) => {
    const path = `/items/${index}`;
    if (!isRecord(rawItem)) {
      add("CAMPAIGN_INPUT_INVALID", path, "campaign item must be a closed object");
      return;
    }
    exactKeys(rawItem, ["item_id", "replay_inputs", "supplied_result_bytes", "supplied_result_sha256"], path, add);
    if (typeof rawItem.item_id !== "string" || rawItem.item_id.length === 0) {
      add("CAMPAIGN_INPUT_INVALID", `${path}/item_id`, "item ID must be non-empty");
    } else if (itemIds.has(rawItem.item_id)) {
      add("CAMPAIGN_ITEM_ID_DUPLICATE", `${path}/item_id`, "item ID must be unique across the campaign");
    } else {
      itemIds.add(rawItem.item_id);
    }
    const replayValid = validateReplayInputs(rawItem.replay_inputs, `${path}/replay_inputs`, add);
    if (!isBytes(rawItem.supplied_result_bytes)) {
      add("CAMPAIGN_RESULT_INVALID", `${path}/supplied_result_bytes`, "supplied result bytes are absent or invalid");
    }
    if (typeof rawItem.supplied_result_sha256 !== "string" || !sha256Pattern.test(rawItem.supplied_result_sha256)) {
      add("CAMPAIGN_RESULT_INVALID", `${path}/supplied_result_sha256`, "supplied result SHA-256 is absent or invalid");
    }
    if (typeof rawItem.item_id === "string" && rawItem.item_id.length > 0 && replayValid &&
        isBytes(rawItem.supplied_result_bytes) && typeof rawItem.supplied_result_sha256 === "string" &&
        sha256Pattern.test(rawItem.supplied_result_sha256) && Object.keys(rawItem).length === 4) {
      items.push(rawItem as unknown as ToolEvidenceReplayCampaignItemInput);
    }
  });

  if (findings.length > 0 || items.length !== rawItems.length) {
    return rejectedResult(campaignId, evaluatedAt, manifestSha256, findings);
  }

  const candidates: CampaignCandidate[] = [];
  items.forEach((item, index) => {
    const path = `/items/${index}`;
    const recomputed = replayToolEvidenceProfile(item.replay_inputs);
    const rawResultSha256 = digest(item.supplied_result_bytes);
    const supplied = parseSuppliedResult(item.supplied_result_bytes, `${path}/supplied_result_bytes`, add);
    if (rawResultSha256 !== item.supplied_result_sha256) {
      add("CAMPAIGN_RESULT_DIGEST_MISMATCH", `${path}/supplied_result_sha256`, "supplied result raw-byte digest does not match");
    }
    if (item.replay_inputs.evaluated_at !== evaluatedAt || recomputed.evaluated_at !== evaluatedAt ||
        recomputed.eligibility?.evaluated_at !== evaluatedAt) {
      add("CAMPAIGN_EVALUATION_TIME_MISMATCH", `${path}/replay_inputs/evaluated_at`, "item evaluation time differs from the campaign");
    }
    if (supplied !== null) validateSuppliedCeiling(supplied, `${path}/supplied_result`, evaluatedAt, add);
    if (recomputed.verdict !== "replayed") {
      add("CAMPAIGN_ITEM_REPLAY_REJECTED", `${path}/replay_inputs`, "WP6 recomputation rejected the item");
    }
    if (supplied !== null && canonicalJson(supplied) !== canonicalJson(recomputed)) {
      add("CAMPAIGN_RESULT_MISMATCH", `${path}/supplied_result_bytes`, "supplied result is not semantically equal to WP6 recomputation");
    }

    const eligibility: ToolProfileEvidenceEligibilityResult | null = recomputed.eligibility;
    if (eligibility === null) {
      add("CAMPAIGN_ELIGIBILITY_MISSING", `${path}/recomputed/eligibility`, "recomputed replay eligibility is absent");
      return;
    }
    if (eligibility.decision !== "replay-only" || eligibility.findings.length !== 0) {
      add("CAMPAIGN_ELIGIBILITY_REJECTED", `${path}/recomputed/eligibility`, "recomputed eligibility is not replay-only");
      return;
    }
    if (recomputed.runtime_admission !== "denied" || eligibility.runtime_admission !== "denied") {
      add("CAMPAIGN_RUNTIME_ADMISSION_FORGED", `${path}/recomputed/runtime_admission`, "recomputed runtime admission is not denied");
      return;
    }
    if (recomputed.referent_trust !== "unverified" || eligibility.referent_trust !== "unverified") {
      add("CAMPAIGN_REFERENT_TRUST_FORGED", `${path}/recomputed/referent_trust`, "recomputed referent trust is not unverified");
      return;
    }
    if (recomputed.authority_effect !== "none" || eligibility.authority_effect !== "none") {
      add("CAMPAIGN_AUTHORITY_EFFECT_FORGED", `${path}/recomputed/authority_effect`, "recomputed authority effect is not none");
      return;
    }
    if (eligibility.runtime_admitted_observations.length !== 0) {
      add("CAMPAIGN_RUNTIME_OBSERVATION_FORGED", `${path}/recomputed/eligibility/runtime_admitted_observations`, "recomputed admitted observations are not empty");
      return;
    }
    if (eligibility.replay_observations.length !== 1 || eligibility.eligibility_receipts.length !== 1 ||
        eligibility.derived_result === null) {
      add("CAMPAIGN_ELIGIBILITY_REJECTED", `${path}/recomputed/eligibility`, "recomputed replay-only projections are incomplete");
      return;
    }
    const observation = eligibility.replay_observations[0]!;
    const receipt = eligibility.eligibility_receipts[0]!;
    const derived = eligibility.derived_result;
    if (receipt.eligible_controls.length !== 0) {
      add("CAMPAIGN_ELIGIBLE_CONTROLS_FORGED", `${path}/recomputed/eligibility/eligible_controls`, "recomputed eligible controls are not empty");
      return;
    }
    const itemReceipt: ToolEvidenceReplayCampaignItemReceipt = {
      schema_version: "domainspec.orodi.tool-evidence-replay-campaign-item-receipt/v1",
      item_id: item.item_id,
      replay_id: recomputed.replay_id,
      profile_id: recomputed.normalization.profile_id,
      profile_version: recomputed.normalization.profile_version,
      family_id: recomputed.normalization.family_id as ToolEvidenceReplayCampaignItemReceipt["family_id"],
      binding_id: derived.binding_id,
      invalidation_key_digest: observation.invalidation_key_digest,
      observation_id: observation.observation_id,
      supplied_result_sha256: rawResultSha256,
      recomputed_result_sha256: digestJson(recomputed),
      eligibility_decision: "replay-only",
      runtime_admission: "denied",
      referent_trust: "unverified",
      authority_effect: "none",
    };
    candidates.push({
      sort_key: [itemReceipt.family_id, itemReceipt.profile_id, itemReceipt.profile_version, itemReceipt.replay_id, itemReceipt.item_id],
      item_receipt: itemReceipt,
      replay_observation: cloneJson(observation),
      eligibility_receipt: cloneJson(receipt),
      derived_partition: {
        schema_version: "domainspec.orodi.tool-evidence-replay-campaign-derived-partition/v1",
        item_id: itemReceipt.item_id,
        replay_id: itemReceipt.replay_id,
        binding_id: itemReceipt.binding_id,
        invalidation_key_digest: itemReceipt.invalidation_key_digest,
        derived_result: cloneJson(derived),
        authority_effect: "none",
      },
    });
  });

  duplicateFindings(candidates, add);
  if (findings.length > 0 || candidates.length !== items.length) {
    return rejectedResult(campaignId, evaluatedAt, manifestSha256, findings);
  }

  const ordered = [...candidates].sort((left, right) => compareTuple(left.sort_key, right.sort_key));
  return deepFreeze({
    schema_version: "domainspec.orodi.tool-evidence-replay-campaign-result/v1",
    composer_id: TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_ID,
    composer_version: TOOL_EVIDENCE_REPLAY_CAMPAIGN_COMPOSER_VERSION,
    evidence_lane: "candidate-local-prototype",
    campaign_id: campaignId,
    evaluated_at: evaluatedAt,
    input_manifest_sha256: manifestSha256,
    item_receipts: ordered.map(({ item_receipt }) => cloneJson(item_receipt)),
    replay_observations: ordered.map(({ replay_observation }) => cloneJson(replay_observation)),
    eligibility_receipts: ordered.map(({ eligibility_receipt }) => cloneJson(eligibility_receipt)),
    per_binding_derived_results: ordered.map(({ derived_partition }) => cloneJson(derived_partition)),
    runtime_admitted_observations: [],
    eligible_controls: [],
    verdict: "composed",
    findings: [],
    runtime_admission: "denied",
    referent_trust: "unverified",
    authority_effect: "none",
  });
};
