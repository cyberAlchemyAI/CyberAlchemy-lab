import {createHash} from "node:crypto";

import {
  canonicalConstructionObservationJson,
  decodeEntityLifecycleConstructionObservationV1,
  ENTITY_CONSTRUCTION_ROUTES,
} from "../../../kernel/evidence/construction-observation/index.js";
import {
  IDENTITY_LIFECYCLE_HOSTILE_CLASSES,
  IDENTITY_LIFECYCLE_MUTATION_BLUEPRINT,
  IDENTITY_LIFECYCLE_POSITIVE_OBLIGATIONS,
  type IdentityLifecycleDefinitionV1,
  type IdentityLifecycleDenominatorV1,
  type IdentityLifecycleFindingCode,
  type IdentityLifecycleMutationCatalogueV1,
  type IdentityLifecycleMutationV1,
  type IdentityLifecycleObservationV1,
} from "../contracts/identity-lifecycle-contracts.js";

type JsonObject = Record<string, unknown>;
const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,511}$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isRecord = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string): never => {
  const error = Object.assign(new Error(code), {code});
  error.name = "IdentityLifecycleDecodeError";
  throw error;
};
const object = (value: unknown, code: string): JsonObject =>
  isRecord(value) ? value : fail(code);
const array = (value: unknown, code: string): readonly unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = (value: unknown, code: string): string =>
  typeof value === "string" && IDENTIFIER.test(value) ? value : fail(code);
const sha = (value: unknown, code: string): string =>
  typeof value === "string" && SHA256.test(value) ? value : fail(code);
const exactKeys = (
  source: JsonObject,
  expected: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const sortedExpected = [...expected].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(sortedExpected)) fail(code);
};
const parse = (bytes: string, code: string): JsonObject => {
  try {
    return object(JSON.parse(bytes), code);
  } catch (error) {
    if (error instanceof Error && error.name === "IdentityLifecycleDecodeError") {
      throw error;
    }
    return fail(code);
  }
};
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left)
    === canonicalConstructionObservationJson(right);
const exactSet = (actual: readonly string[], expected: readonly string[]): boolean =>
  new Set(actual).size === actual.length
    && same([...actual].sort(compareUtf8), [...expected].sort(compareUtf8));
const bytesSha256 = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");
const canonicalSha256 = (value: unknown): string => bytesSha256(
  canonicalConstructionObservationJson(value),
);
const deepFreeze = <Value>(value: Value): Readonly<Value> => {
  if (value === null || typeof value !== "object" || Object.isFrozen(value)) {
    return value;
  }
  Object.freeze(value);
  for (const child of Object.values(value)) deepFreeze(child);
  return value;
};

const validateFactory = (value: unknown, conceptId: string): void => {
  const source = object(value, "FAMILY_ENTITY_DEFINITION_FACTORY_INVALID");
  exactKeys(source, ["factory_id", "factory_sha256", "concept_id"],
    "FAMILY_ENTITY_DEFINITION_FACTORY_SHAPE_INVALID");
  string(source.factory_id, "FAMILY_ENTITY_DEFINITION_FACTORY_INVALID");
  sha(source.factory_sha256, "FAMILY_ENTITY_DEFINITION_FACTORY_INVALID");
  if (string(source.concept_id, "FAMILY_ENTITY_DEFINITION_FACTORY_INVALID")
      !== conceptId) fail("FAMILY_ENTITY_DEFINITION_FACTORY_INVALID");
};

export const decodeIdentityLifecycleDefinitionV1 = (
  bytes: string,
  expectedDescriptorPath: string,
  descriptorBytes: string,
): IdentityLifecycleDefinitionV1 => {
  const source = parse(bytes, "FAMILY_ENTITY_DEFINITION_JSON_INVALID");
  exactKeys(source, ["schema_version", "definition_id", "status", "authorship",
    "derivation_policy", "descriptor_ref", "concept_id", "factories",
    "identity_components", "validators", "construction_routes",
    "direct_constructor_policy", "snapshots", "equality_probes",
    "validation_failure", "extension_policy", "authority_effect"],
  "FAMILY_ENTITY_DEFINITION_SHAPE_INVALID");
  if (source.schema_version !== "IdentityLifecycleDefinition/v1"
      || source.status !== "candidate-fixture"
      || source.authorship !== "owner-authored-admission-input"
      || source.derivation_policy
        !== "implementation-and-generated-results-forbidden-as-authority"
      || source.direct_constructor_policy
        !== "private-inaccessible-or-delegating-facade"
      || source.authority_effect !== "none") {
    return fail("FAMILY_ENTITY_DEFINITION_POLICY_INVALID");
  }
  string(source.definition_id, "FAMILY_ENTITY_DEFINITION_ID_INVALID");
  const descriptorRef = object(source.descriptor_ref,
    "FAMILY_ENTITY_DEFINITION_DESCRIPTOR_INVALID");
  exactKeys(descriptorRef, ["descriptor_id", "path", "sha256"],
    "FAMILY_ENTITY_DEFINITION_DESCRIPTOR_SHAPE_INVALID");
  const descriptor = parse(descriptorBytes,
    "FAMILY_ENTITY_DEFINITION_DESCRIPTOR_JSON_INVALID");
  if (descriptorRef.path !== expectedDescriptorPath
      || descriptorRef.sha256 !== bytesSha256(descriptorBytes)
      || descriptorRef.descriptor_id !== descriptor.descriptor_id) {
    return fail("FAMILY_ENTITY_DEFINITION_DESCRIPTOR_STALE");
  }
  const conceptId = string(source.concept_id,
    "FAMILY_ENTITY_DEFINITION_CONCEPT_INVALID");
  const factories = object(source.factories,
    "FAMILY_ENTITY_DEFINITION_FACTORIES_INVALID");
  exactKeys(factories, ["base", "extension"],
    "FAMILY_ENTITY_DEFINITION_FACTORIES_SHAPE_INVALID");
  validateFactory(factories.base, conceptId);
  validateFactory(factories.extension, conceptId);
  if (object(factories.base, "FAMILY_ENTITY_DEFINITION_FACTORY_INVALID").factory_id
      === object(factories.extension,
        "FAMILY_ENTITY_DEFINITION_FACTORY_INVALID").factory_id) {
    fail("FAMILY_ENTITY_DEFINITION_FACTORY_INVALID");
  }

  const identities = array(source.identity_components,
    "FAMILY_ENTITY_DEFINITION_IDENTITY_INVALID");
  if (identities.length < 1) fail("FAMILY_ENTITY_DEFINITION_IDENTITY_INVALID");
  const identityNames = identities.map((item) => {
    const component = object(item, "FAMILY_ENTITY_DEFINITION_IDENTITY_INVALID");
    exactKeys(component, ["component_name", "type_id", "type_sha256"],
      "FAMILY_ENTITY_DEFINITION_IDENTITY_SHAPE_INVALID");
    string(component.type_id, "FAMILY_ENTITY_DEFINITION_IDENTITY_INVALID");
    sha(component.type_sha256, "FAMILY_ENTITY_DEFINITION_IDENTITY_INVALID");
    return string(component.component_name,
      "FAMILY_ENTITY_DEFINITION_IDENTITY_INVALID");
  });
  if (new Set(identityNames).size !== identityNames.length) {
    fail("FAMILY_ENTITY_DEFINITION_IDENTITY_INVALID");
  }

  const validators = array(source.validators,
    "FAMILY_ENTITY_DEFINITION_VALIDATORS_INVALID");
  if (validators.length < 1) fail("FAMILY_ENTITY_DEFINITION_VALIDATORS_INVALID");
  const validatorIds: string[] = [];
  let extensionSeen = false;
  let hasBase = false;
  let hasExtension = false;
  for (const item of validators) {
    const validator = object(item, "FAMILY_ENTITY_DEFINITION_VALIDATOR_INVALID");
    exactKeys(validator, ["validator_id", "validator_sha256", "origin"],
      "FAMILY_ENTITY_DEFINITION_VALIDATOR_SHAPE_INVALID");
    validatorIds.push(string(validator.validator_id,
      "FAMILY_ENTITY_DEFINITION_VALIDATOR_INVALID"));
    sha(validator.validator_sha256, "FAMILY_ENTITY_DEFINITION_VALIDATOR_INVALID");
    if (validator.origin !== "base" && validator.origin !== "extension") {
      fail("FAMILY_ENTITY_DEFINITION_VALIDATOR_INVALID");
    }
    if (validator.origin === "extension") {
      extensionSeen = true;
      hasExtension = true;
    } else {
      hasBase = true;
      if (extensionSeen) fail("FAMILY_ENTITY_DEFINITION_VALIDATOR_ORDER_INVALID");
    }
  }
  if (!hasBase || !hasExtension || new Set(validatorIds).size !== validatorIds.length) {
    fail("FAMILY_ENTITY_DEFINITION_VALIDATORS_INVALID");
  }
  const routes = array(source.construction_routes,
    "FAMILY_ENTITY_DEFINITION_ROUTES_INVALID").map((item) =>
    string(item, "FAMILY_ENTITY_DEFINITION_ROUTES_INVALID"));
  if (!same(routes, ENTITY_CONSTRUCTION_ROUTES)) {
    fail("FAMILY_ENTITY_DEFINITION_ROUTES_INVALID");
  }

  const snapshots = array(source.snapshots,
    "FAMILY_ENTITY_DEFINITION_SNAPSHOTS_INVALID");
  const snapshotIds: string[] = [];
  const snapshotIdentityById = new Map<string, JsonObject>();
  const stateById = new Map<string, string>();
  for (const item of snapshots) {
    const snapshot = object(item, "FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID");
    exactKeys(snapshot, ["snapshot_id", "entity_case_id", "sequence", "route_id",
      "predecessor_snapshot_id", "identity_values", "state_sha256"],
    "FAMILY_ENTITY_DEFINITION_SNAPSHOT_SHAPE_INVALID");
    const snapshotId = string(snapshot.snapshot_id,
      "FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID");
    snapshotIds.push(snapshotId);
    string(snapshot.entity_case_id, "FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID");
    if (!Number.isSafeInteger(snapshot.sequence) || Number(snapshot.sequence) < 0) {
      fail("FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID");
    }
    if (!routes.includes(string(snapshot.route_id,
      "FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID"))) {
      fail("FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID");
    }
    if (snapshot.predecessor_snapshot_id !== null) {
      string(snapshot.predecessor_snapshot_id,
        "FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID");
    }
    const values = object(snapshot.identity_values,
      "FAMILY_ENTITY_DEFINITION_SNAPSHOT_IDENTITY_INVALID");
    if (!exactSet(Object.keys(values), identityNames)) {
      fail("FAMILY_ENTITY_DEFINITION_SNAPSHOT_IDENTITY_INVALID");
    }
    for (const value of Object.values(values)) {
      sha(value, "FAMILY_ENTITY_DEFINITION_SNAPSHOT_IDENTITY_INVALID");
    }
    snapshotIdentityById.set(snapshotId, values);
    stateById.set(snapshotId, sha(snapshot.state_sha256,
      "FAMILY_ENTITY_DEFINITION_SNAPSHOT_INVALID"));
  }
  if (snapshots.length < 3 || new Set(snapshotIds).size !== snapshotIds.length) {
    fail("FAMILY_ENTITY_DEFINITION_SNAPSHOTS_INVALID");
  }
  for (const item of snapshots) {
    const snapshot = item as JsonObject;
    if (snapshot.predecessor_snapshot_id !== null
        && (!snapshotIdentityById.has(String(snapshot.predecessor_snapshot_id))
          || !same(snapshotIdentityById.get(String(snapshot.predecessor_snapshot_id)),
            snapshot.identity_values))) {
      fail("FAMILY_ENTITY_DEFINITION_LIFECYCLE_IDENTITY_INVALID");
    }
  }

  const probes = array(source.equality_probes,
    "FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
  const relations: string[] = [];
  for (const item of probes) {
    const probe = object(item, "FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
    exactKeys(probe, ["probe_id", "left_snapshot_id", "right_snapshot_id",
      "relation", "expected_equal"], "FAMILY_ENTITY_DEFINITION_EQUALITY_SHAPE_INVALID");
    string(probe.probe_id, "FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
    const left = string(probe.left_snapshot_id,
      "FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
    const right = string(probe.right_snapshot_id,
      "FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
    if (!snapshotIdentityById.has(left) || !snapshotIdentityById.has(right)
        || typeof probe.expected_equal !== "boolean"
        || (probe.relation !== "same-identity-different-state"
          && probe.relation !== "distinct-identity")) {
      fail("FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
    }
    relations.push(String(probe.relation));
    const equalIdentity = same(snapshotIdentityById.get(left),
      snapshotIdentityById.get(right));
    if (probe.relation === "same-identity-different-state"
        && (!equalIdentity || stateById.get(left) === stateById.get(right)
          || probe.expected_equal !== true)) {
      fail("FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
    }
    if (probe.relation === "distinct-identity"
        && (equalIdentity || probe.expected_equal !== false)) {
      fail("FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
    }
  }
  if (!exactSet(relations,
    ["same-identity-different-state", "distinct-identity"])) {
    fail("FAMILY_ENTITY_DEFINITION_EQUALITY_INVALID");
  }
  const failure = object(source.validation_failure,
    "FAMILY_ENTITY_DEFINITION_FAILURE_INVALID");
  exactKeys(failure, ["probe_id", "expected_failure_codes"],
    "FAMILY_ENTITY_DEFINITION_FAILURE_SHAPE_INVALID");
  string(failure.probe_id, "FAMILY_ENTITY_DEFINITION_FAILURE_INVALID");
  const failures = array(failure.expected_failure_codes,
    "FAMILY_ENTITY_DEFINITION_FAILURE_INVALID");
  if (failures.length < 1) fail("FAMILY_ENTITY_DEFINITION_FAILURE_INVALID");
  failures.forEach((item) => string(item, "FAMILY_ENTITY_DEFINITION_FAILURE_INVALID"));
  const extension = object(source.extension_policy,
    "FAMILY_ENTITY_DEFINITION_EXTENSION_INVALID");
  exactKeys(extension, ["mode", "cycle_policy", "base_validators_preserved",
    "identity_resolver_preserved"], "FAMILY_ENTITY_DEFINITION_EXTENSION_SHAPE_INVALID");
  if (extension.mode !== "additive-only" || extension.cycle_policy !== "acyclic"
      || extension.base_validators_preserved !== true
      || extension.identity_resolver_preserved !== true) {
    fail("FAMILY_ENTITY_DEFINITION_EXTENSION_INVALID");
  }
  return deepFreeze(source as unknown as IdentityLifecycleDefinitionV1);
};

export const computeIdentityLifecycleDenominatorSha256 = (
  value: Omit<IdentityLifecycleDenominatorV1, "denominator_sha256">,
): string => canonicalSha256(value);

export const decodeIdentityLifecycleDenominatorV1 = (
  bytes: string,
  ownerDefinitionBytes: string,
  ownerDefinition: IdentityLifecycleDefinitionV1,
  expectedOwnerPath: string,
): IdentityLifecycleDenominatorV1 => {
  const source = parse(bytes, "FAMILY_ENTITY_DENOMINATOR_JSON_INVALID");
  exactKeys(source, ["schema_version", "denominator_id", "owner_definition_ref",
    "portable_contract", "positive_obligations", "semantic_hostile_classes",
    "construction_routes", "authority_effect", "denominator_sha256"],
  "FAMILY_ENTITY_DENOMINATOR_SHAPE_INVALID");
  if (source.schema_version !== "IdentityLifecycleDenominator/v1"
      || source.authority_effect !== "none") {
    fail("FAMILY_ENTITY_DENOMINATOR_POLICY_INVALID");
  }
  string(source.denominator_id, "FAMILY_ENTITY_DENOMINATOR_ID_INVALID");
  const ownerRef = object(source.owner_definition_ref,
    "FAMILY_ENTITY_DENOMINATOR_OWNER_INVALID");
  exactKeys(ownerRef, ["definition_id", "path", "sha256"],
    "FAMILY_ENTITY_DENOMINATOR_OWNER_SHAPE_INVALID");
  if (ownerRef.definition_id !== ownerDefinition.definition_id
      || ownerRef.path !== expectedOwnerPath
      || ownerRef.sha256 !== bytesSha256(ownerDefinitionBytes)) {
    fail("FAMILY_ENTITY_DENOMINATOR_OWNER_STALE");
  }
  const portable = object(source.portable_contract,
    "FAMILY_ENTITY_DENOMINATOR_POLICY_INVALID");
  exactKeys(portable, ["identity", "equality_and_hash", "validator_order",
    "formation_failure", "lifecycle", "extension", "routes", "evidence_origin"],
  "FAMILY_ENTITY_DENOMINATOR_POLICY_INVALID");
  if (portable.identity
      !== "one-or-more-exact-typed-components-stable-across-snapshots"
      || portable.equality_and_hash !== "canonical-identity-only"
      || portable.validator_order
        !== "owner-bound-base-then-extension-before-identity-and-construction"
      || portable.formation_failure !== "structured-failure-no-snapshot"
      || portable.lifecycle !== "ordered-immutable-snapshot-sequence"
      || portable.extension !== "additive-only-acyclic-preserves-base-and-identity"
      || portable.routes
        !== "exact-four-with-direct-constructor-inaccessible-or-delegating"
      || portable.evidence_origin !== "locked-independent-owner-not-provider") {
    fail("FAMILY_ENTITY_DENOMINATOR_POLICY_INVALID");
  }
  const obligations = array(source.positive_obligations,
    "FAMILY_ENTITY_DENOMINATOR_SCOPE_INVALID").map((item) =>
    string(item, "FAMILY_ENTITY_DENOMINATOR_SCOPE_INVALID"));
  const hostiles = array(source.semantic_hostile_classes,
    "FAMILY_ENTITY_DENOMINATOR_SCOPE_INVALID").map((item) =>
    string(item, "FAMILY_ENTITY_DENOMINATOR_SCOPE_INVALID"));
  const routes = array(source.construction_routes,
    "FAMILY_ENTITY_DENOMINATOR_SCOPE_INVALID").map((item) =>
    string(item, "FAMILY_ENTITY_DENOMINATOR_SCOPE_INVALID"));
  if (!exactSet(obligations, IDENTITY_LIFECYCLE_POSITIVE_OBLIGATIONS)
      || !exactSet(hostiles, IDENTITY_LIFECYCLE_HOSTILE_CLASSES)
      || !same(routes, ENTITY_CONSTRUCTION_ROUTES)) {
    fail("FAMILY_ENTITY_DENOMINATOR_SCOPE_INVALID");
  }
  const {denominator_sha256: digest, ...body} = source;
  if (sha(digest, "FAMILY_ENTITY_DENOMINATOR_DIGEST_INVALID")
      !== canonicalSha256(body)) fail("FAMILY_ENTITY_DENOMINATOR_DIGEST_STALE");
  return deepFreeze(source as unknown as IdentityLifecycleDenominatorV1);
};

const EXPECTED_CODES: Readonly<Record<string, readonly IdentityLifecycleFindingCode[]>>
  = Object.freeze({
    "per-call-validator-bypass": ["FAMILY_ENTITY_VALIDATOR_BYPASS"],
    "remove-base-validator": ["FAMILY_ENTITY_BASE_VALIDATOR_REMOVED"],
    "replace-identity-resolver": ["FAMILY_ENTITY_IDENTITY_RESOLVER_REPLACED"],
    "allow-extension-cycle": ["FAMILY_ENTITY_EXTENSION_CYCLE"],
    "invalid-input-forms-snapshot": ["FAMILY_ENTITY_INVALID_INPUT_FORMED_SNAPSHOT"],
    "mutate-constructed-snapshot": ["FAMILY_ENTITY_MUTABLE_SNAPSHOT"],
    "complete-field-equality": ["FAMILY_ENTITY_COMPLETE_FIELD_EQUALITY"],
  });

export const computeIdentityLifecycleCatalogueSha256 = (
  value: Omit<IdentityLifecycleMutationCatalogueV1, "catalogue_sha256">,
): string => canonicalSha256(value);

export const decodeIdentityLifecycleMutationCatalogueV1 = (
  bytes: string,
  denominator: IdentityLifecycleDenominatorV1,
): IdentityLifecycleMutationCatalogueV1 => {
  const source = parse(bytes, "FAMILY_ENTITY_MUTATIONS_JSON_INVALID");
  exactKeys(source, ["schema_version", "denominator_ref", "authorship",
    "target_code_may_read_expected_findings", "mutations", "authority_effect",
    "catalogue_sha256"], "FAMILY_ENTITY_MUTATIONS_SHAPE_INVALID");
  if (source.schema_version !== "IdentityLifecycleMutationCatalogue/v1"
      || source.authorship !== "independent-family-fixture"
      || source.target_code_may_read_expected_findings !== false
      || source.authority_effect !== "none") fail("FAMILY_ENTITY_MUTATIONS_POLICY_INVALID");
  const denominatorRef = object(source.denominator_ref,
    "FAMILY_ENTITY_MUTATIONS_DENOMINATOR_INVALID");
  exactKeys(denominatorRef, ["denominator_id", "denominator_sha256"],
    "FAMILY_ENTITY_MUTATIONS_DENOMINATOR_SHAPE_INVALID");
  if (denominatorRef.denominator_id !== denominator.denominator_id
      || denominatorRef.denominator_sha256 !== denominator.denominator_sha256) {
    fail("FAMILY_ENTITY_MUTATIONS_DENOMINATOR_STALE");
  }
  const mutations = array(source.mutations,
    "FAMILY_ENTITY_MUTATIONS_INVALID").map((item) => {
    const mutation = object(item, "FAMILY_ENTITY_MUTATION_INVALID");
    exactKeys(mutation, ["mutation_id", "hostile_class", "mutation_kind",
      "expected_finding_codes"], "FAMILY_ENTITY_MUTATION_SHAPE_INVALID");
    const decoded = {
      mutation_id: string(mutation.mutation_id, "FAMILY_ENTITY_MUTATION_INVALID"),
      hostile_class: string(mutation.hostile_class,
        "FAMILY_ENTITY_MUTATION_INVALID"),
      mutation_kind: string(mutation.mutation_kind,
        "FAMILY_ENTITY_MUTATION_INVALID"),
      expected_finding_codes: array(mutation.expected_finding_codes,
        "FAMILY_ENTITY_MUTATION_INVALID").map((code) =>
        string(code, "FAMILY_ENTITY_MUTATION_INVALID")),
    };
    if (!same(decoded.expected_finding_codes, EXPECTED_CODES[decoded.mutation_kind])) {
      fail("FAMILY_ENTITY_MUTATION_EXPECTATION_INVALID");
    }
    return decoded;
  });
  if (!same(mutations.map(({mutation_id, hostile_class, mutation_kind}) =>
    ({mutation_id, hostile_class, mutation_kind})),
  IDENTITY_LIFECYCLE_MUTATION_BLUEPRINT)) {
    fail("FAMILY_ENTITY_MUTATION_BLUEPRINT_INVALID");
  }
  const {catalogue_sha256: digest, ...body} = source;
  if (sha(digest, "FAMILY_ENTITY_MUTATIONS_DIGEST_INVALID")
      !== canonicalSha256(body)) fail("FAMILY_ENTITY_MUTATIONS_DIGEST_STALE");
  return deepFreeze(source as unknown as IdentityLifecycleMutationCatalogueV1);
};

export const decodeIdentityLifecycleObservationV1 = (
  bytes: string,
): IdentityLifecycleObservationV1 =>
  decodeEntityLifecycleConstructionObservationV1(bytes);
