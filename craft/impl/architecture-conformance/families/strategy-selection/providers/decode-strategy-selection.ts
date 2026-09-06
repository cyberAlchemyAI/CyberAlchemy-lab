import {createHash} from "node:crypto";

import {
  STRATEGY_MEMBERSHIP_DECISIONS,
  STRATEGY_MEMBERSHIP_MUTATION_KINDS,
  type StrategyCatalogueV1,
  type StrategyMemberV1,
  type StrategyMembershipDenominatorV1,
  type StrategyMembershipMutationCatalogueV1,
  type StrategyMembershipMutationKind,
  type StrategyMembershipObservationV1,
} from "../contracts/strategy-selection-contracts.js";

type JsonObject = Record<string, unknown>;

export class StrategySelectionDecodeError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "StrategySelectionDecodeError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new StrategySelectionDecodeError(code);
};
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const object = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const string = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const sha = (value: unknown, code: string): string => {
  const result = string(value, code);
  return /^[a-f0-9]{64}$/u.test(result) ? result : fail(code);
};
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const exactKeys = (source: JsonObject, expected: readonly string[], code: string): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const keys = [...expected].sort(compareUtf8);
  if (actual.length !== keys.length
      || actual.some((value, index) => value !== keys[index])) fail(code);
};
const parse = (bytes: string, code: string): JsonObject => {
  try {
    return object(JSON.parse(bytes), code);
  } catch (error: unknown) {
    if (error instanceof StrategySelectionDecodeError) throw error;
    return fail(code);
  }
};
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;

export const canonicalStrategySelectionJson = (value: unknown): string =>
  JSON.stringify(canonicalize(value));
export const sha256StrategySelectionBytes = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");
const sha256Json = (value: unknown): string =>
  sha256StrategySelectionBytes(canonicalStrategySelectionJson(value));

const catalogueBody = (
  value: Omit<StrategyCatalogueV1, "catalogue_sha256">,
): unknown => ({
  ...value,
  members: [...value.members]
    .map((member) => ({...member, eligibility_facts: [...member.eligibility_facts].sort(compareUtf8)}))
    .sort((left, right) => compareUtf8(left.strategy_id, right.strategy_id)),
});
export const computeStrategyCatalogueSha256 = (
  value: Omit<StrategyCatalogueV1, "catalogue_sha256">,
): string => sha256Json(catalogueBody(value));

const decodeMember = (value: unknown): StrategyMemberV1 => {
  const source = object(value, "FAMILY_POLICY_MEMBER_SHAPE_INVALID");
  exactKeys(source, ["strategy_id", "purpose", "eligibility_facts", "executable"],
    "FAMILY_POLICY_MEMBER_SHAPE_INVALID");
  const rawEligibilityFacts = source.eligibility_facts;
  if (!Array.isArray(rawEligibilityFacts) || rawEligibilityFacts.length === 0
      || source.executable !== false) fail("FAMILY_POLICY_MEMBER_POLICY_INVALID");
  const eligibilityFacts = (rawEligibilityFacts as unknown[]).map((item: unknown) =>
    string(item, "FAMILY_POLICY_MEMBER_POLICY_INVALID"));
  if (new Set(eligibilityFacts).size !== eligibilityFacts.length) {
    fail("FAMILY_POLICY_MEMBER_POLICY_INVALID");
  }
  return Object.freeze({
    strategy_id: string(source.strategy_id, "FAMILY_POLICY_MEMBER_ID_INVALID"),
    purpose: string(source.purpose, "FAMILY_POLICY_MEMBER_POLICY_INVALID"),
    eligibility_facts: Object.freeze(eligibilityFacts),
    executable: false as const,
  });
};

export const decodeStrategyCatalogueV1 = (
  bytes: string,
  expectedDescriptorPath: string,
  descriptorBytes: string,
): StrategyCatalogueV1 => {
  const source = parse(bytes, "FAMILY_POLICY_CATALOGUE_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "catalogue_id", "catalogue_status", "authorship",
    "derivation_policy", "descriptor_ref", "set_id", "members",
    "member_order_semantics", "membership_contract", "authority_effect",
    "catalogue_sha256",
  ], "FAMILY_POLICY_CATALOGUE_SHAPE_INVALID");
  if (source.schema_version !== "StrategyCatalogue/v1"
      || source.catalogue_status !== "candidate-fixture"
      || source.authorship !== "owner-authored-admission-input"
      || source.derivation_policy
        !== "implementation-and-generated-members-forbidden-as-authority"
      || source.member_order_semantics !== "none"
      || source.authority_effect !== "none"
      || !Array.isArray(source.members) || source.members.length === 0) {
    return fail("FAMILY_POLICY_CATALOGUE_POLICY_INVALID");
  }
  const descriptor = object(source.descriptor_ref,
    "FAMILY_POLICY_DESCRIPTOR_REF_INVALID");
  exactKeys(descriptor, ["descriptor_id", "path", "sha256"],
    "FAMILY_POLICY_DESCRIPTOR_REF_INVALID");
  if (descriptor.path !== expectedDescriptorPath
      || sha(descriptor.sha256, "FAMILY_POLICY_DESCRIPTOR_REF_INVALID")
        !== sha256StrategySelectionBytes(descriptorBytes)) {
    return fail("FAMILY_POLICY_DESCRIPTOR_REF_STALE");
  }
  const contract = object(source.membership_contract,
    "FAMILY_POLICY_CATALOGUE_POLICY_INVALID");
  exactKeys(contract, ["identity", "set", "member_authority", "selection", "execution"],
    "FAMILY_POLICY_CATALOGUE_POLICY_INVALID");
  if (contract.identity !== "stable-strategy-id"
      || contract.set !== "closed-current-content-addressed"
      || contract.member_authority !== "data-only-no-callable-authority"
      || contract.selection !== "not-proven-by-membership"
      || contract.execution !== "not-proven-by-membership") {
    return fail("FAMILY_POLICY_CATALOGUE_POLICY_INVALID");
  }
  const members = source.members.map(decodeMember);
  if (new Set(members.map(({strategy_id: id}) => id)).size !== members.length) {
    return fail("FAMILY_POLICY_MEMBER_ID_DUPLICATE");
  }
  const withoutDigest = Object.freeze({
    schema_version: "StrategyCatalogue/v1" as const,
    catalogue_id: string(source.catalogue_id, "FAMILY_POLICY_CATALOGUE_ID_INVALID"),
    catalogue_status: "candidate-fixture" as const,
    authorship: "owner-authored-admission-input" as const,
    derivation_policy:
      "implementation-and-generated-members-forbidden-as-authority" as const,
    descriptor_ref: Object.freeze({
      descriptor_id: string(descriptor.descriptor_id,
        "FAMILY_POLICY_DESCRIPTOR_REF_INVALID"),
      path: expectedDescriptorPath,
      sha256: sha(descriptor.sha256, "FAMILY_POLICY_DESCRIPTOR_REF_INVALID"),
    }),
    set_id: string(source.set_id, "FAMILY_POLICY_CATALOGUE_ID_INVALID"),
    members: Object.freeze(members),
    member_order_semantics: "none" as const,
    membership_contract: Object.freeze({
      identity: "stable-strategy-id" as const,
      set: "closed-current-content-addressed" as const,
      member_authority: "data-only-no-callable-authority" as const,
      selection: "not-proven-by-membership" as const,
      execution: "not-proven-by-membership" as const,
    }),
    authority_effect: "none" as const,
  });
  const digest = sha(source.catalogue_sha256, "FAMILY_POLICY_CATALOGUE_DIGEST_INVALID");
  if (digest !== computeStrategyCatalogueSha256(withoutDigest)) {
    return fail("FAMILY_POLICY_CATALOGUE_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, catalogue_sha256: digest});
};

const denominatorBody = (
  value: Omit<StrategyMembershipDenominatorV1, "denominator_sha256">,
): unknown => ({...value, positive_decisions: [...value.positive_decisions].sort(compareUtf8)});
export const computeStrategyMembershipDenominatorSha256 = (
  value: Omit<StrategyMembershipDenominatorV1, "denominator_sha256">,
): string => sha256Json(denominatorBody(value));

export const decodeStrategyMembershipDenominatorV1 = (
  bytes: string,
  catalogueBytes: string,
  expectedCataloguePath: string,
  descriptorPath: string,
  descriptorBytes: string,
): Readonly<{
  catalogue: StrategyCatalogueV1;
  denominator: StrategyMembershipDenominatorV1;
}> => {
  const catalogue = decodeStrategyCatalogueV1(catalogueBytes, descriptorPath, descriptorBytes);
  const source = parse(bytes, "FAMILY_POLICY_DENOMINATOR_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_id", "owner_catalogue_ref", "portable_contract",
    "positive_decisions", "authority_effect", "denominator_sha256",
  ], "FAMILY_POLICY_DENOMINATOR_SHAPE_INVALID");
  if (source.schema_version !== "StrategyMembershipDenominator/v1"
      || source.authority_effect !== "none") fail("FAMILY_POLICY_DENOMINATOR_POLICY_INVALID");
  const owner = object(source.owner_catalogue_ref,
    "FAMILY_POLICY_DENOMINATOR_OWNER_REF_INVALID");
  exactKeys(owner, ["catalogue_id", "path", "sha256", "catalogue_sha256"],
    "FAMILY_POLICY_DENOMINATOR_OWNER_REF_INVALID");
  if (owner.catalogue_id !== catalogue.catalogue_id
      || owner.path !== expectedCataloguePath
      || sha(owner.sha256, "FAMILY_POLICY_DENOMINATOR_OWNER_REF_INVALID")
        !== sha256StrategySelectionBytes(catalogueBytes)
      || owner.catalogue_sha256 !== catalogue.catalogue_sha256) {
    return fail("FAMILY_POLICY_DENOMINATOR_OWNER_REF_STALE");
  }
  const contract = object(source.portable_contract,
    "FAMILY_POLICY_DENOMINATOR_POLICY_INVALID");
  exactKeys(contract, ["membership", "strategy_identity", "selection_claim", "execution_claim"],
    "FAMILY_POLICY_DENOMINATOR_POLICY_INVALID");
  if (contract.membership !== "exact-current-set-membership"
      || contract.strategy_identity !== "stable-data-only-id"
      || contract.selection_claim !== "none" || contract.execution_claim !== "none"
      || !Array.isArray(source.positive_decisions)) {
    return fail("FAMILY_POLICY_DENOMINATOR_POLICY_INVALID");
  }
  const decisions = source.positive_decisions.map((item) =>
    string(item, "FAMILY_POLICY_DENOMINATOR_DECISIONS_INVALID"));
  if (canonicalStrategySelectionJson([...decisions].sort(compareUtf8))
      !== canonicalStrategySelectionJson([...STRATEGY_MEMBERSHIP_DECISIONS]
        .sort(compareUtf8))) return fail("FAMILY_POLICY_DENOMINATOR_DECISIONS_INVALID");
  const withoutDigest = Object.freeze({
    schema_version: "StrategyMembershipDenominator/v1" as const,
    denominator_id: string(source.denominator_id, "FAMILY_POLICY_DENOMINATOR_ID_INVALID"),
    owner_catalogue_ref: Object.freeze({
      catalogue_id: catalogue.catalogue_id,
      path: expectedCataloguePath,
      sha256: sha(owner.sha256, "FAMILY_POLICY_DENOMINATOR_OWNER_REF_INVALID"),
      catalogue_sha256: catalogue.catalogue_sha256,
    }),
    portable_contract: Object.freeze({
      membership: "exact-current-set-membership" as const,
      strategy_identity: "stable-data-only-id" as const,
      selection_claim: "none" as const,
      execution_claim: "none" as const,
    }),
    positive_decisions: Object.freeze([...STRATEGY_MEMBERSHIP_DECISIONS]),
    authority_effect: "none" as const,
  });
  const digest = sha(source.denominator_sha256, "FAMILY_POLICY_DENOMINATOR_DIGEST_INVALID");
  if (digest !== computeStrategyMembershipDenominatorSha256(withoutDigest)) {
    return fail("FAMILY_POLICY_DENOMINATOR_DIGEST_STALE");
  }
  return Object.freeze({
    catalogue,
    denominator: Object.freeze({...withoutDigest, denominator_sha256: digest}),
  });
};

const observationBody = (
  value: Omit<StrategyMembershipObservationV1, "observation_sha256">,
): unknown => value;
export const computeStrategyMembershipObservationSha256 = (
  value: Omit<StrategyMembershipObservationV1, "observation_sha256">,
): string => sha256Json(observationBody(value));
export const mintStrategyMembershipObservationV1 = (
  value: Omit<StrategyMembershipObservationV1, "observation_sha256">,
): StrategyMembershipObservationV1 => Object.freeze({
  ...value,
  catalogue_ref: Object.freeze({...value.catalogue_ref}),
  observation_sha256: computeStrategyMembershipObservationSha256(value),
});

export const decodeStrategyMembershipObservationV1 = (
  bytes: string,
): StrategyMembershipObservationV1 => {
  const source = parse(bytes, "FAMILY_POLICY_OBSERVATION_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "observation_id", "source_kind", "catalogue_ref",
    "strategy_id", "membership", "selection_claim", "execution_claim",
    "authority_effect", "observation_sha256",
  ], "FAMILY_POLICY_OBSERVATION_SHAPE_INVALID");
  if (source.schema_version !== "StrategyMembershipObservation/v1"
      || !["independent-owner-membership", "mutated-family-observation"]
        .includes(String(source.source_kind))
      || !["member", "missing"].includes(String(source.membership))
      || !["none", "selected"].includes(String(source.selection_claim))
      || !["none", "executable"].includes(String(source.execution_claim))
      || source.authority_effect !== "none") fail("FAMILY_POLICY_OBSERVATION_POLICY_INVALID");
  const ref = object(source.catalogue_ref, "FAMILY_POLICY_OBSERVATION_REF_INVALID");
  exactKeys(ref, ["catalogue_id", "catalogue_sha256"],
    "FAMILY_POLICY_OBSERVATION_REF_INVALID");
  const withoutDigest = Object.freeze({
    schema_version: "StrategyMembershipObservation/v1" as const,
    observation_id: string(source.observation_id, "FAMILY_POLICY_OBSERVATION_ID_INVALID"),
    source_kind: source.source_kind as StrategyMembershipObservationV1["source_kind"],
    catalogue_ref: Object.freeze({
      catalogue_id: string(ref.catalogue_id, "FAMILY_POLICY_OBSERVATION_REF_INVALID"),
      catalogue_sha256: sha(ref.catalogue_sha256,
        "FAMILY_POLICY_OBSERVATION_REF_INVALID"),
    }),
    strategy_id: string(source.strategy_id, "FAMILY_POLICY_OBSERVATION_STRATEGY_INVALID"),
    membership: source.membership as StrategyMembershipObservationV1["membership"],
    selection_claim: source.selection_claim as StrategyMembershipObservationV1["selection_claim"],
    execution_claim: source.execution_claim as StrategyMembershipObservationV1["execution_claim"],
    authority_effect: "none" as const,
  });
  const digest = sha(source.observation_sha256, "FAMILY_POLICY_OBSERVATION_DIGEST_INVALID");
  if (digest !== computeStrategyMembershipObservationSha256(withoutDigest)) {
    return fail("FAMILY_POLICY_OBSERVATION_DIGEST_STALE");
  }
  return Object.freeze({...withoutDigest, observation_sha256: digest});
};

export const decodeStrategyMembershipMutationCatalogueV1 = (
  bytes: string,
): StrategyMembershipMutationCatalogueV1 => {
  const source = parse(bytes, "FAMILY_POLICY_MUTATIONS_JSON_INVALID");
  exactKeys(source, [
    "schema_version", "denominator_ref", "authorship",
    "target_code_may_read_expected_findings", "mutations", "authority_effect",
    "catalogue_sha256",
  ], "FAMILY_POLICY_MUTATIONS_SHAPE_INVALID");
  if (source.schema_version !== "StrategyMembershipMutationCatalogue/v1"
      || source.authorship !== "independent-family-fixture"
      || source.target_code_may_read_expected_findings !== false
      || source.authority_effect !== "none" || !Array.isArray(source.mutations)) {
    return fail("FAMILY_POLICY_MUTATIONS_POLICY_INVALID");
  }
  const ref = object(source.denominator_ref, "FAMILY_POLICY_MUTATIONS_REF_INVALID");
  exactKeys(ref, ["denominator_id", "denominator_sha256"],
    "FAMILY_POLICY_MUTATIONS_REF_INVALID");
  const mutations = source.mutations.map((item) => {
    const mutation = object(item, "FAMILY_POLICY_MUTATION_SHAPE_INVALID");
    exactKeys(mutation, ["mutation_id", "mutation_kind", "expected_finding_codes"],
      "FAMILY_POLICY_MUTATION_SHAPE_INVALID");
    if (!STRATEGY_MEMBERSHIP_MUTATION_KINDS.includes(mutation.mutation_kind as never)
        || !Array.isArray(mutation.expected_finding_codes)
        || mutation.expected_finding_codes.length === 0) {
      return fail("FAMILY_POLICY_MUTATION_POLICY_INVALID");
    }
    return Object.freeze({
      mutation_id: string(mutation.mutation_id, "FAMILY_POLICY_MUTATION_ID_INVALID"),
      mutation_kind: mutation.mutation_kind as StrategyMembershipMutationKind,
      expected_finding_codes: Object.freeze(mutation.expected_finding_codes.map((value) =>
        string(value, "FAMILY_POLICY_MUTATION_FINDING_INVALID"))) as any,
    });
  });
  if (mutations.length !== STRATEGY_MEMBERSHIP_MUTATION_KINDS.length
      || new Set(mutations.map(({mutation_kind: kind}) => kind)).size !== mutations.length) {
    return fail("FAMILY_POLICY_MUTATIONS_POLICY_INVALID");
  }
  const body = Object.freeze({
    schema_version: "StrategyMembershipMutationCatalogue/v1" as const,
    denominator_ref: Object.freeze({
      denominator_id: string(ref.denominator_id, "FAMILY_POLICY_MUTATIONS_REF_INVALID"),
      denominator_sha256: sha(ref.denominator_sha256,
        "FAMILY_POLICY_MUTATIONS_REF_INVALID"),
    }),
    authorship: "independent-family-fixture" as const,
    target_code_may_read_expected_findings: false as const,
    mutations: Object.freeze(mutations),
    authority_effect: "none" as const,
  });
  const digest = sha(source.catalogue_sha256, "FAMILY_POLICY_MUTATIONS_DIGEST_INVALID");
  if (digest !== sha256Json(body)) fail("FAMILY_POLICY_MUTATIONS_DIGEST_STALE");
  return Object.freeze({...body, catalogue_sha256: digest});
};
