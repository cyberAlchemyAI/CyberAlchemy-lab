import {createHash} from "node:crypto";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {
  decodeIdentityLifecycleDefinitionV1,
  decodeIdentityLifecycleDenominatorV1,
  decodeIdentityLifecycleMutationCatalogueV1,
  decodeIdentityLifecycleObservationV1,
  type IdentityLifecycleDefinitionV1,
} from "../../families/identity-lifecycle/index.js";
import {canonicalConstructionObservationJson} from
  "../../kernel/evidence/construction-observation/index.js";

type JsonObject = Record<string, unknown>;

export const ENTITY_DIRECT_HANDLES = Object.freeze([
  Object.freeze({
    node_id: "entity.typescript.settlement",
    provider_id: "typescript-entity-v1",
    language: "typescript",
    proof_schema: "TypeScriptEntityProof/v1",
    target_id: "entity.typescript.settlement/v1",
    target_sha256: "c174f82e19e72b30f9305f005809bf8a63b52d102e708a9739a3d898b704b197",
    protocol_id: "typescript.validated-extensible-entity-factory/v1",
    binding_id: "typescript.settlement-entity.identity-lifecycle/v1",
    binding_sha256: "4a109b1b2e9fbf3ce499f96e9160e0c31f4fdd400b7897c1752192b4fba32d56",
    binding_file_sha256: "4c5b4d8f9e6febb255117a7a3e207b30dc369bfe61d8dc1933d792a7bbadb6e8",
    observer_sha256: "0470ff6eefec1979f0c0b28fa43a61b5363b8197090827a30714ec71cd919d0b",
    provider_sha256: "b53128e807f734043019e75e6b892900b83c320b909d859644f6a820a9c960f1",
    observer_provider_id: "typescript-entity-v1",
    observer_provider_sha256: "b53128e807f734043019e75e6b892900b83c320b909d859644f6a820a9c960f1",
    target_control_count: 10,
  }),
  Object.freeze({
    node_id: "entity.python.settlement",
    provider_id: "python-entity-v1",
    language: "python",
    proof_schema: "PythonEntityProof/v1",
    target_id: "entity.python.settlement/v1",
    target_sha256: "a5cdabfe72a86c1c8afb29f6f94bac6e69fb819db02d70681b825c76eba10f3b",
    protocol_id: "python.validated-extensible-entity-factory/v1",
    binding_id: "python.settlement-entity.identity-lifecycle/v1",
    binding_sha256: "5e488d1d8c76c50aa2a7bb87937353e9d005238a320925ca1fdea68a36ef90d1",
    binding_file_sha256: "1789d0e056283043d04ebe1511374ec917322f0b90984e4457ea185cdc5ce69e",
    observer_sha256: "3de380c1cdc08d5d3e510570da68757cc10d355db7ed65013310afc683e5bc73",
    provider_sha256: "ff73fc4b9ce1c8831d352346530b6f111c8714f2a12781566e4ead429128a80b",
    observer_provider_id: "python-entity-v1",
    observer_provider_sha256: "ff73fc4b9ce1c8831d352346530b6f111c8714f2a12781566e4ead429128a80b",
    target_control_count: 11,
  }),
  Object.freeze({
    node_id: "entity.rust.settlement",
    provider_id: "rust-entity-v1",
    language: "rust",
    proof_schema: "RustEntityProof/v1",
    target_id: "entity.rust.settlement/v1",
    target_sha256: "0df0f880a5a2a01fd06185030f9bcf5e9396cf493fdd8c27a272b9ad4fd208bb",
    protocol_id: "rust.validated-extensible-entity-factory/v1",
    binding_id: "rust.settlement-entity.identity-lifecycle/v1",
    binding_sha256: "62fda2eb661bb5740f0172df84aa7c21f85bcff64d58aaf8ee9e5e15dab934a9",
    binding_file_sha256: "d852bd6aec19e8e720dc3ae7b17f6e3b7b52b99dbdb13560ea279afeb2a995f3",
    observer_sha256: "351525da684ec273e68cc0e9a24d0321e701c2da446e90711e5a4ee8064854b4",
    provider_sha256: "ac36027b3bd2678ef92929ce655f2904304321dbdc896da4d444eb7bd82bca85",
    observer_provider_id: "observer.rustc-subprocess/v1",
    observer_provider_sha256: "4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10",
    target_control_count: 12,
  }),
] as const);

export const ENTITY_PARITY_HANDLE = Object.freeze({
  node_id: "entity.parity.settlement",
  provider_id: "entity-parity-v1",
  proof_schema: "EntityParityProof/v1",
});

const DEFINITION_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/definition.json";
const DENOMINATOR_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/denominator.json";
const MUTATIONS_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/identity-lifecycle/fixtures/settlement-entity/mutants.json";
const DESCRIPTOR_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/entity/cross-language-realization-descriptor.json";
const ADMISSION_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/entity/protocol-admission.json";
const ONTOLOGY_PATH =
  "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json";
const TYPESCRIPT_RECEIPT_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-ENTITY-003.json";
const PYTHON_RECEIPT_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-ENTITY-004.json";
const RUST_RECEIPT_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-ENTITY-005.json";
const ENTITY_DECISION_PATH =
  "projects/domainspec-v2/development/ontology-form-decisions/decisions/W1-ENTITY-001.json";
const VALUE_OBJECT_RECEIPT_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-VO-007.json";
const VALUE_OBJECT_CANDIDATE_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/candidates/value-object.json";

export const ENTITY_PARITY_RAW_PATHS = Object.freeze({
  definition: DEFINITION_PATH,
  denominator: DENOMINATOR_PATH,
  mutations: MUTATIONS_PATH,
  descriptor: DESCRIPTOR_PATH,
});

export const ENTITY_RELATION_RAW_PATHS = Object.freeze({
  ...ENTITY_PARITY_RAW_PATHS,
  protocol_admission: ADMISSION_PATH,
  ontology: ONTOLOGY_PATH,
  typescript_receipt: TYPESCRIPT_RECEIPT_PATH,
  python_receipt: PYTHON_RECEIPT_PATH,
  rust_receipt: RUST_RECEIPT_PATH,
  entity_decision: ENTITY_DECISION_PATH,
  value_object_receipt: VALUE_OBJECT_RECEIPT_PATH,
  value_object_candidate: VALUE_OBJECT_CANDIDATE_PATH,
});

const TARGET_CONTROL_IDS = Object.freeze({
  typescript: Object.freeze([
    "validator-loop-bypass",
    "base-validator-removal",
    "identity-resolver-replacement",
    "extension-cycle",
    "invalid-snapshot",
    "freeze-removal",
    "complete-field-equality",
    "stateful-hash",
    "reconstruction-bypass",
    "transition-identity-replacement",
  ]),
  python: Object.freeze([
    "per-call-validator-bypass",
    "remove-base-validator",
    "replace-identity-resolver",
    "allow-extension-cycle",
    "invalid-input-forms-snapshot",
    "mutable-snapshot",
    "complete-field-equality",
    "reconstruction-bypass",
    "transition-identity-replacement",
    "constructor-exposure",
    "route-whitelist-bypass",
  ]),
  rust: Object.freeze([
    "per-call-validator-bypass",
    "remove-base-validator",
    "validator-order-swap",
    "replace-identity-resolver",
    "allow-extension-cycle",
    "invalid-input-forms-snapshot",
    "mutable-snapshot-field",
    "complete-field-equality",
    "stateful-hash",
    "reconstruction-bypass",
    "transition-identity-replacement",
    "public-direct-constructor",
  ]),
} as const);

const FAMILY_CONTROL_IDS = Object.freeze([
  "validators/per-call-always-true",
  "extension/remove-base-validator",
  "identity/replace-resolver",
  "extension/allow-cycle",
  "formation/invalid-forms-snapshot",
  "lifecycle/mutate-snapshot",
  "equality/complete-fields",
] as const);

const PROOF_KEYS = Object.freeze({
  typescript: Object.freeze([
    "schema_version", "result", "target", "binding", "observation",
    "family_evaluation", "closed_subset", "toolchain", "process_evidence",
    "accounting", "source_controls", "predecessor_family_controls",
    "claim_ceiling", "authority_effect",
  ]),
  python: Object.freeze([
    "schema_version", "result", "target", "binding",
    "native_runtime_observation", "observation", "family_evaluation",
    "process_evidence", "toolchain", "accounting", "target_source_controls",
    "predecessor_family_controls", "claim_ceiling", "authority_effect",
  ]),
  rust: Object.freeze([
    "schema_version", "result", "target", "native_runtime", "observation",
    "evaluation", "source_controls", "predecessor_family_controls",
    "accounting", "binding", "claim_ceiling", "authority_effect",
  ]),
} as const);

const ENTITY_PROPERTIES = Object.freeze({
  "creation.extension_policy": "additive-only",
  "creation.validator_count": "integer-minimum-one-by-entity-profile",
  "creation.base_invariants_preserved": true,
  "identity.stable_across_lifecycle": true,
  "lifecycle.observation_mode": "immutable-snapshot-sequence",
});

const ENTITY_ROUTES = Object.freeze([
  "factory",
  "deserialization-reconstruction",
  "lifecycle-transition",
  "language-visible-direct-constructor",
] as const);

const ENTITY_PIPELINE = Object.freeze([
  "normalize-and-apply-declared-defaults",
  "run-base-validators",
  "run-extension-validators",
  "resolve-stable-identity",
  "construct-entity-snapshot",
  "enforce-native-immutability",
] as const);

const ENTITY_MATERIAL_REFS = Object.freeze([
  Object.freeze({path: ONTOLOGY_PATH,
    sha256: "2b36051d46aae3c730bd8af1b12c26f9718756e347dc068e7d4ff5a6e5c36003"}),
  Object.freeze({path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/domain-meta-types.projection.json",
    sha256: "1999767ae7c552639278ee71985a98ac2ae3b80c08435ed7ada681f0cc096cc5"}),
  Object.freeze({path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
    sha256: "89efdcbe88a88254d48a891578f26c7b1cd13887ab6786b07a9c7c576a0c1129"}),
  Object.freeze({path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json",
    sha256: "43c81463d36eb8d7a3cb420edef0a6534e8dd1a4752cac9f4df0fac7959c4f63"}),
  Object.freeze({path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/rust-strict.profile.json",
    sha256: "d37801130be50841f528ff1f4abf56fae9dc4a0b3f7013836e2174aa6c27863c"}),
] as const);

const ENTITY_PROTOCOLS = Object.freeze([
  Object.freeze({language: "typescript",
    form_id: "typescript.entity-factory-record",
    protocol_id: "typescript.validated-extensible-entity-factory/v1",
    status: "admitted-candidate-protocol", implementation_status: "provider-absent",
    profile_ref: ENTITY_MATERIAL_REFS[2]}),
  Object.freeze({language: "python", form_id: "python.entity-dataclass",
    protocol_id: "python.validated-extensible-entity-factory/v1",
    status: "admitted-candidate-protocol", implementation_status: "provider-absent",
    profile_ref: ENTITY_MATERIAL_REFS[3]}),
  Object.freeze({language: "rust", form_id: "rust.entity-struct",
    protocol_id: "rust.validated-extensible-entity-factory/v1",
    status: "admitted-candidate-protocol", implementation_status: "provider-absent",
    profile_ref: ENTITY_MATERIAL_REFS[4]}),
] as const);

type EntityReceiptSpec = Readonly<{
  raw_role: "typescript_receipt" | "python_receipt" | "rust_receipt";
  raw_sha256: string;
  raw_size_bytes: number;
  swu_id: "RMT-ENTITY-003" | "RMT-ENTITY-004" | "RMT-ENTITY-005";
  handle_index: 0 | 1 | 2;
  artifact_roles: readonly string[];
  provider_role: string;
  provider_path: string;
  target_role: string;
  target_path: string;
  binding_role: string;
  binding_path: string;
  observer_role: string;
  observer_path: string;
}>;

const ENTITY_RECEIPT_SPECS: readonly EntityReceiptSpec[] = Object.freeze([
  Object.freeze({raw_role: "typescript_receipt",
    raw_sha256: "ab0e994b80b841283656fc5c626cba5f48411c991b0d28507c1f41c20f6f91be",
    raw_size_bytes: 19109, swu_id: "RMT-ENTITY-003", handle_index: 0,
    artifact_roles: Object.freeze(["typescript-entity-provider",
      "typescript-entity-closed-subset-observer", "typescript-entity-proof-builder",
      "typescript-entity-provider-test", "typescript-entity-binding",
      "typescript-entity-target-test", "typescript-entity-target"]),
    provider_role: "typescript-entity-provider",
    provider_path: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-entity-v1.ts",
    target_role: "typescript-entity-target",
    target_path: "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/entity-v1.ts",
    binding_role: "typescript-entity-binding",
    binding_path: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/typescript/identity-lifecycle-v1/typescript-binding.json",
    observer_role: "typescript-entity-closed-subset-observer",
    observer_path: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/typescript/identity-lifecycle-v1/closed-subset.ts"}),
  Object.freeze({raw_role: "python_receipt",
    raw_sha256: "7c2676edfc8e38f8aca0232d68e3913075e9c04833b78d3827a48457f65963ef",
    raw_size_bytes: 15369, swu_id: "RMT-ENTITY-004", handle_index: 1,
    artifact_roles: Object.freeze(["python-entity-provider",
      "python-entity-proof-builder", "python-entity-observer",
      "python-entity-provider-tests", "python-entity-binding",
      "python-entity-native-supervisor", "python-entity-target",
      "python-entity-target-tests"]),
    provider_role: "python-entity-provider",
    provider_path: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-entity-v1.ts",
    target_role: "python-entity-target",
    target_path: "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/entity_v1.py",
    binding_role: "python-entity-binding",
    binding_path: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/python/identity-lifecycle-v1/python-binding.json",
    observer_role: "python-entity-observer",
    observer_path: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/python/identity-lifecycle-v1/observe_python_entity.py"}),
  Object.freeze({raw_role: "rust_receipt",
    raw_sha256: "a6170042bacd5381b0a6467a138840ce19f6b5ce6e6cd2372301a4a8c64d9ea4",
    raw_size_bytes: 15979, swu_id: "RMT-ENTITY-005", handle_index: 2,
    artifact_roles: Object.freeze(["rust-entity-provider",
      "rust-entity-closed-subset-observer", "rust-entity-proof-builder",
      "rust-entity-provider-tests", "rust-entity-binding", "rust-entity-target",
      "rust-remaining-types-additive-index", "rust-entity-native-tests"]),
    provider_role: "rust-entity-provider",
    provider_path: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-entity-v1.ts",
    target_role: "rust-entity-target",
    target_path: "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/entity_v1.rs",
    binding_role: "rust-entity-binding",
    binding_path: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/rust/identity-lifecycle-v1/rust-binding.json",
    observer_role: "rust-entity-closed-subset-observer",
    observer_path: "projects/domainspec-v2/impl/architecture-conformance/realizations/entity/rust/identity-lifecycle-v1/closed-subset.ts"}),
]);

const ENTITY_DECISION_REF = Object.freeze({path: ENTITY_DECISION_PATH,
  sha256: "de9c159ea4b65ab6d3508e94a731770724c87cdef5dd6333c41f231746438a9f"});
const VALUE_OBJECT_RECEIPT_REF = Object.freeze({path: VALUE_OBJECT_RECEIPT_PATH,
  sha256: "45de2a6f7fe7ef168697c5909251e44aaf17cc58e5ff2ac39bb4dc8b88a71387"});
const VALUE_OBJECT_CANDIDATE_REF = Object.freeze({path: VALUE_OBJECT_CANDIDATE_PATH,
  sha256: "c171dab764a6a31e961d38c13986b7b56142e532d46758217e0ebd8a782c073f"});
const ENTITY_002_RECEIPT_REF = Object.freeze({swu_id: "RMT-ENTITY-002",
  path: "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-ENTITY-002.json",
  sha256: "a36c993453f3fcccd01416b94698c139347ac1a2c474a3f352e737dadf7c2530",
  size_bytes: 14971, result: "pass"});

const exactRawObject = (
  rawInputs: Readonly<Record<string, string>>,
  role: string,
  digest: string,
  size: number,
): JsonObject => {
  const raw = rawInputs[role];
  if (raw === undefined || Buffer.byteLength(raw, "utf8") !== size ||
      sha256Bytes(raw) !== digest) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID", `${role}:bytes`);
  }
  return parseObject(raw, "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
};

const PARITY_OBLIGATION_IDS = Object.freeze([
  "exact-direct-handle-set",
  "exact-provider-target-language-protocol-schema",
  "exact-binding-observer-and-provider-locks",
  "shared-owner-definition",
  "shared-descriptor-denominator-and-mutation-catalogue",
  "exact-construction-route-set",
  "base-before-extension-validators-before-identity-and-construction",
  "structured-failure-no-snapshot",
  "exact-snapshot-ledger",
  "typed-composite-identity",
  "lifecycle-identity-stability",
  "same-identity-different-state-equal",
  "distinct-identities-remain-distinct",
  "own-language-equality-hash-congruence",
  "cross-language-hash-bytes-not-compared",
  "immutable-snapshots",
  "additive-terminal-extension-preserves-base-and-identity",
  "family-five-seven-four-accounting",
  "native-target-source-and-family-evidence-retained",
  "authority-effect-none",
] as const);

const RELATION_OBLIGATION_IDS = Object.freeze([
  "exact-direct-plus-parity-closure",
  "parity-proof-recomputed-not-totals-only",
  "descriptor-and-admission-bound",
  "ontology-same-family-relation-definitions-bound",
  "constructed-by-exact-endpoints",
  "validated-by-exact-endpoints",
  "owner-validator-identities-and-order",
  "extends-factory-exact-endpoints",
  "additive-only-policy",
  "stable-identity-preservation",
  "acyclic-terminal-extension",
  "authority-effect-none",
] as const);

export type EntityParityFindingCode =
  | "ENTITY_PARITY_HANDLE_SET_MISMATCH"
  | "ENTITY_PARITY_PROVIDER_MISMATCH"
  | "ENTITY_PARITY_PROOF_INVALID"
  | "ENTITY_PARITY_TARGET_MISMATCH"
  | "ENTITY_PARITY_OWNER_MATERIAL_INVALID"
  | "ENTITY_PARITY_ROUTE_INVALID"
  | "ENTITY_PARITY_VALIDATOR_INVALID"
  | "ENTITY_PARITY_FAILURE_INVALID"
  | "ENTITY_PARITY_SNAPSHOT_INVALID"
  | "ENTITY_PARITY_IDENTITY_INVALID"
  | "ENTITY_PARITY_LIFECYCLE_INVALID"
  | "ENTITY_PARITY_EQUALITY_INVALID"
  | "ENTITY_PARITY_HASH_CONGRUENCE_INVALID"
  | "ENTITY_PARITY_IMMUTABILITY_INVALID"
  | "ENTITY_PARITY_EXTENSION_INVALID"
  | "ENTITY_PARITY_FAMILY_INVALID"
  | "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING"
  | "ENTITY_PARITY_PORTABLE_DRIFT"
  | "ENTITY_PARITY_RAW_INPUT_INVALID";

export type EntityRelationFindingCode =
  | "ENTITY_RELATION_HANDLE_SET_MISMATCH"
  | "ENTITY_RELATION_PARITY_INVALID"
  | "ENTITY_RELATION_OWNER_MATERIAL_INVALID"
  | "ENTITY_RELATION_CONSTRUCTED_BY_INVALID"
  | "ENTITY_RELATION_VALIDATED_BY_INVALID"
  | "ENTITY_RELATION_EXTENDS_FACTORY_INVALID"
  | "ENTITY_RELATION_AUTHORITY_INVALID";

type Handle = (typeof ENTITY_DIRECT_HANDLES)[number];
type OwnerInputs = ReturnType<typeof decodeOwnerInputs>;
type DirectProjection = Readonly<{
  handle: Handle;
  semantic_sha256: string;
  portable: JsonObject;
  native_evidence: JsonObject;
}>;

export type EntityParityProofV1 = Readonly<{
  schema_version: "EntityParityProof/v1";
  result: "pass";
  composed_from: readonly Readonly<{
    node_id: string;
    provider_id: string;
    semantic_sha256: string;
    target_id: string;
    target_sha256: string;
    language: string;
    protocol_id: string;
    binding_sha256: string;
  }>[];
  owner_refs: Readonly<{
    definition_id: string;
    definition_sha256: string;
    denominator_id: string;
    denominator_sha256: string;
    descriptor_id: string;
    descriptor_sha256: string;
    mutation_catalogue_sha256: string;
  }>;
  portable_projection: JsonObject;
  native_evidence_by_language: readonly Readonly<{
    language: string;
    evidence: JsonObject;
  }>[];
  obligations: readonly Readonly<{
    obligation_id: (typeof PARITY_OBLIGATION_IDS)[number];
    status: "passed";
  }>[];
  hostile_mutations: readonly Readonly<{
    mutation_id: string;
    status: "killed";
    finding_code: EntityParityFindingCode;
  }>[];
  claim_ceiling: string;
  authority_effect: "none";
}>;

export type EntityRelationsProofV1 = Readonly<{
  schema_version: "EntityRelationsProof/v1";
  result: "pass";
  composed_from: readonly Readonly<{
    node_id: string;
    provider_id: string;
    semantic_sha256: string;
  }>[];
  relation_rows: readonly Readonly<{
    language: string;
    relation_id: "architecture.constructed_by" |
      "architecture.validated_by" | "architecture.extends_factory";
    source_id: string;
    source_type: string;
    target_id: string;
    target_type: string;
    ordinal: number | null;
    cycle_policy: "not-applicable" | "acyclic";
  }>[];
  obligations: readonly Readonly<{
    obligation_id: (typeof RELATION_OBLIGATION_IDS)[number];
    status: "passed";
  }>[];
  hostile_mutations: readonly Readonly<{
    mutation_id: string;
    status: "killed";
    finding_code: EntityRelationFindingCode;
  }>[];
  claim_ceiling: string;
  authority_effect: "none";
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = <Code extends string>(code: Code, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`),
    {code});
};
const object = <Code extends string>(value: unknown, code: Code): JsonObject =>
  isObject(value) ? value : fail(code);
const array = <Code extends string>(value: unknown, code: Code): unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = <Code extends string>(value: unknown, code: Code): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const sha256String = <Code extends string>(value: unknown, code: Code): string => {
  const digest = string(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const sha256Bytes = (bytes: string): string => createHash("sha256")
  .update(bytes, "utf8").digest("hex");
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left) ===
    canonicalConstructionObservationJson(right);
const exactSet = (observed: readonly string[], expected: readonly string[]):
boolean => new Set(observed).size === observed.length &&
  same([...observed].sort(compareUtf8), [...expected].sort(compareUtf8));
const parseObject = <Code extends string>(raw: string | undefined, code: Code):
JsonObject => {
  if (raw === undefined) return fail(code);
  try {
    return object(JSON.parse(raw), code);
  } catch (error: unknown) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const clone = <T>(value: T): T => structuredClone(value);

const decodeOwnerInputs = (rawInputs: Readonly<Record<string, string>>) => {
  if (!exactSet(Object.keys(rawInputs), Object.keys(ENTITY_PARITY_RAW_PATHS))) {
    return fail("ENTITY_PARITY_RAW_INPUT_INVALID", "roles");
  }
  const descriptor = parseObject(rawInputs.descriptor,
    "ENTITY_PARITY_RAW_INPUT_INVALID");
  try {
    const definition = decodeIdentityLifecycleDefinitionV1(
      rawInputs.definition!, DESCRIPTOR_PATH, rawInputs.descriptor!);
    const denominator = decodeIdentityLifecycleDenominatorV1(
      rawInputs.denominator!, rawInputs.definition!, definition, DEFINITION_PATH);
    const mutations = decodeIdentityLifecycleMutationCatalogueV1(
      rawInputs.mutations!, denominator);
    const portable = object(descriptor.portable_architecture,
      "ENTITY_PARITY_RAW_INPUT_INVALID");
    const proofContract = object(descriptor.proof_contract,
      "ENTITY_PARITY_RAW_INPUT_INVALID");
    if (descriptor.descriptor_id !== definition.descriptor_ref.descriptor_id ||
        descriptor.descriptor_protocol_id !==
          "domainspec.validated-extensible-entity-factory/v1" ||
        descriptor.authority_effect !== "none" ||
        portable.type_id !== "architecture.EntityImplementation" ||
        portable.factory_provider_type_id !==
          "architecture.EntityFactoryProvider" ||
        definition.identity_components.length !== 2 ||
        definition.validators.length !== 3 || definition.snapshots.length !== 4 ||
        definition.equality_probes.length !== 2 ||
        definition.construction_routes.length !== 4 ||
        denominator.positive_obligations.length !== 5 ||
        denominator.semantic_hostile_classes.length !== 7 ||
        mutations.mutations.length !== 7 ||
        array(proofContract.positive_obligations,
          "ENTITY_PARITY_RAW_INPUT_INVALID").length !== 5 ||
        array(proofContract.semantic_hostiles,
          "ENTITY_PARITY_RAW_INPUT_INVALID").length !== 7 ||
        array(proofContract.construction_route_obligations,
          "ENTITY_PARITY_RAW_INPUT_INVALID").length !== 4) {
      return fail("ENTITY_PARITY_RAW_INPUT_INVALID", "owner-shape");
    }
    return Object.freeze({
      definition,
      denominator,
      mutations,
      descriptor,
      definition_sha256: sha256Bytes(rawInputs.definition!),
      descriptor_sha256: sha256Bytes(rawInputs.descriptor!),
      mutation_catalogue_sha256: sha256Bytes(rawInputs.mutations!),
    });
  } catch (error: unknown) {
    if (isObject(error) && typeof error.code === "string" &&
        String(error.code).startsWith("ENTITY_PARITY_")) throw error;
    return fail("ENTITY_PARITY_RAW_INPUT_INVALID",
      error instanceof Error ? error.message : String(error));
  }
};

const expectedValidatorTrace = (
  definition: IdentityLifecycleDefinitionV1,
  count = definition.validators.length,
): readonly JsonObject[] => Object.freeze(definition.validators.slice(0, count)
  .map((validator, index) => Object.freeze({...validator, ordinal: index + 1,
    outcome: index === count - 1 && count < definition.validators.length
      ? "fail" as const : "pass" as const})));

const portableObservation = (
  proof: JsonObject,
  handle: Handle,
  owner: OwnerInputs,
): JsonObject => {
  const observation = object(proof.observation, "ENTITY_PARITY_PROOF_INVALID");
  const definitionRef = object(observation.definition_ref,
    "ENTITY_PARITY_OWNER_MATERIAL_INVALID");
  const factoryRef = object(observation.factory_ref,
    "ENTITY_PARITY_OWNER_MATERIAL_INVALID");
  const observer = object(observation.observer_ref,
    "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  if (observation.schema_version !== "EntityLifecycleConstructionObservation/v1" ||
      observation.source_kind !== "target-observation" ||
      observation.authority_effect !== "none" ||
      observation.collision_freedom_claim !== false ||
      observation.per_call_validator_supplied !== false ||
      definitionRef.definition_id !== owner.definition.definition_id ||
      definitionRef.path !== DEFINITION_PATH ||
      definitionRef.sha256 !== owner.definition_sha256 ||
      !same(factoryRef, owner.definition.factories.base)) {
    return fail("ENTITY_PARITY_OWNER_MATERIAL_INVALID", handle.language);
  }
  if (observer.role !== "independent-construction-observer" ||
      observer.provider_id !== handle.observer_provider_id ||
      observer.owner_ref === handle.provider_id ||
      observer.observer_sha256 !== handle.observer_sha256 ||
      observer.provider_sha256 !== handle.observer_provider_sha256) {
    return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING",
      `${handle.language}:observer`);
  }

  const routes = array(observation.route_traces, "ENTITY_PARITY_ROUTE_INVALID")
    .map((item) => object(item, "ENTITY_PARITY_ROUTE_INVALID"));
  if (!exactSet(routes.map((row) => string(row.route_id,
    "ENTITY_PARITY_ROUTE_INVALID")), owner.definition.construction_routes)) {
    return fail("ENTITY_PARITY_ROUTE_INVALID", handle.language);
  }
  for (const routeId of owner.definition.construction_routes) {
    const route = routes.find((row) => row.route_id === routeId)!;
    const trace = array(route.validator_trace, "ENTITY_PARITY_VALIDATOR_INVALID");
    if (routeId === "language-visible-direct-constructor") {
      if (trace.length !== 0 || route.normalization_ordinal !== null ||
          route.identity_resolution_ordinal !== null ||
          route.construction_ordinal !== null ||
          route.immutability_ordinal !== null ||
          route.direct_constructor_policy !== "private-inaccessible" ||
          !same(route.result, {status: "constructor-inaccessible",
            snapshot_created: false, snapshot_id: null})) {
        return fail("ENTITY_PARITY_ROUTE_INVALID", `${handle.language}:direct`);
      }
      continue;
    }
    const snapshot = owner.definition.snapshots.find((candidate) =>
      candidate.route_id === routeId)!;
    if (!same(trace, expectedValidatorTrace(owner.definition)) ||
        route.normalization_ordinal !== 0 ||
        route.identity_resolution_ordinal !== 4 ||
        route.construction_ordinal !== 5 || route.immutability_ordinal !== 6 ||
        route.direct_constructor_policy !== "not-applicable" ||
        !same(route.result, {status: "formed", snapshot_created: true,
          snapshot_id: snapshot.snapshot_id})) {
      return fail("ENTITY_PARITY_VALIDATOR_INVALID", `${handle.language}:${routeId}`);
    }
  }

  const failure = object(observation.validation_failure_probe,
    "ENTITY_PARITY_FAILURE_INVALID");
  const failureTrace = array(failure.validator_trace,
    "ENTITY_PARITY_FAILURE_INVALID");
  if (failure.probe_id !== owner.definition.validation_failure.probe_id ||
      failure.route_id !== "factory" ||
      !same(failureTrace, expectedValidatorTrace(owner.definition, 2)) ||
      failure.identity_resolution_ordinal !== null ||
      failure.construction_ordinal !== null ||
      !same(failure.result, {status: "validation-failure",
        snapshot_created: false,
        failure_codes: owner.definition.validation_failure.expected_failure_codes})) {
    return fail("ENTITY_PARITY_FAILURE_INVALID", handle.language);
  }

  const snapshots = array(observation.snapshots, "ENTITY_PARITY_SNAPSHOT_INVALID")
    .map((item) => object(item, "ENTITY_PARITY_SNAPSHOT_INVALID"));
  if (snapshots.length !== owner.definition.snapshots.length ||
      !exactSet(snapshots.map((snapshot) => string(snapshot.snapshot_id,
        "ENTITY_PARITY_SNAPSHOT_INVALID")),
      owner.definition.snapshots.map(({snapshot_id: id}) => id))) {
    return fail("ENTITY_PARITY_SNAPSHOT_INVALID", handle.language);
  }
  const portableSnapshots = owner.definition.snapshots.map((expected) => {
    const observed = snapshots.find((snapshot) =>
      snapshot.snapshot_id === expected.snapshot_id)!;
    if (observed.entity_case_id !== expected.entity_case_id ||
        observed.sequence !== expected.sequence ||
        observed.route_id !== expected.route_id ||
        observed.state_sha256 !== expected.state_sha256) {
      return fail("ENTITY_PARITY_SNAPSHOT_INVALID", expected.snapshot_id);
    }
    const expectedIdentity = owner.definition.identity_components.map(
      (component) => ({...component,
        normalized_value_sha256:
          expected.identity_values[component.component_name]}));
    if (!same(observed.identity, expectedIdentity)) {
      return fail("ENTITY_PARITY_IDENTITY_INVALID", expected.snapshot_id);
    }
    if (observed.predecessor_snapshot_id !== expected.predecessor_snapshot_id) {
      return fail("ENTITY_PARITY_LIFECYCLE_INVALID", expected.snapshot_id);
    }
    if (observed.frozen !== true || observed.mutation_observed !== false) {
      return fail("ENTITY_PARITY_IMMUTABILITY_INVALID", expected.snapshot_id);
    }
    return Object.freeze({...expected, identity: Object.freeze(expectedIdentity),
      frozen: true, mutation_observed: false});
  });

  const probes = array(observation.equality_probes,
    "ENTITY_PARITY_EQUALITY_INVALID")
    .map((item) => object(item, "ENTITY_PARITY_EQUALITY_INVALID"));
  if (probes.length !== owner.definition.equality_probes.length) {
    return fail("ENTITY_PARITY_EQUALITY_INVALID", handle.language);
  }
  const equality = owner.definition.equality_probes.map((expected) => {
    const observed = probes.find((probe) => probe.probe_id === expected.probe_id);
    if (observed === undefined ||
        observed.left_snapshot_id !== expected.left_snapshot_id ||
        observed.right_snapshot_id !== expected.right_snapshot_id ||
        observed.relation !== expected.relation ||
        observed.comparison_basis !== "canonical-identity-only" ||
        observed.observed_equal !== expected.expected_equal) {
      return fail("ENTITY_PARITY_EQUALITY_INVALID", expected.probe_id);
    }
    const left = sha256String(observed.left_hash_sha256,
      "ENTITY_PARITY_HASH_CONGRUENCE_INVALID");
    const right = sha256String(observed.right_hash_sha256,
      "ENTITY_PARITY_HASH_CONGRUENCE_INVALID");
    if (expected.expected_equal && left !== right) {
      return fail("ENTITY_PARITY_HASH_CONGRUENCE_INVALID", expected.probe_id);
    }
    return Object.freeze({...expected,
      comparison_basis: "canonical-identity-only" as const,
      observed_equal: expected.expected_equal,
      own_language_hash_congruent: expected.expected_equal ? true : null,
      native_hash_bytes_compared_cross_language: false});
  });

  const extension = object(observation.extension,
    "ENTITY_PARITY_EXTENSION_INVALID");
  const expectedExtension = {
    base_factory_ref: owner.definition.factories.base,
    extension_factory_ref: owner.definition.factories.extension,
    base_validators_preserved: true,
    added_validators: owner.definition.validators.filter(({origin}) =>
      origin === "extension"),
    identity_resolver_preserved: true,
    altered_facets: [],
    cycle_detected: false,
  };
  if (!same(extension, expectedExtension)) {
    return fail("ENTITY_PARITY_EXTENSION_INVALID", handle.language);
  }

  try {
    decodeIdentityLifecycleObservationV1(
      canonicalConstructionObservationJson(observation));
  } catch (error: unknown) {
    return fail("ENTITY_PARITY_PROOF_INVALID",
      error instanceof Error ? error.message : String(error));
  }
  return Object.freeze({
    definition_id: owner.definition.definition_id,
    definition_sha256: owner.definition_sha256,
    descriptor_id: owner.definition.descriptor_ref.descriptor_id,
    descriptor_sha256: owner.descriptor_sha256,
    concept_id: owner.definition.concept_id,
    base_factory: owner.definition.factories.base,
    extension_factory: owner.definition.factories.extension,
    identity_components: owner.definition.identity_components,
    validators: owner.definition.validators,
    construction_routes: owner.definition.construction_routes,
    route_traces: Object.freeze(routes),
    validation_failure_probe: failure,
    snapshots: Object.freeze(portableSnapshots),
    equality: Object.freeze(equality),
    extension: Object.freeze(expectedExtension),
    authority_effect: "none" as const,
  });
};

const familyEvaluation = (proof: JsonObject, handle: Handle): JsonObject => {
  const family = object(handle.language === "rust" ? proof.evaluation :
    proof.family_evaluation, "ENTITY_PARITY_FAMILY_INVALID");
  const positive = object(family.positive_obligation_accounting,
    "ENTITY_PARITY_FAMILY_INVALID");
  const hostiles = object(family.hostile_class_accounting,
    "ENTITY_PARITY_FAMILY_INVALID");
  const routes = object(family.construction_route_accounting,
    "ENTITY_PARITY_FAMILY_INVALID");
  if (family.schema_version !== "IdentityLifecycleEvaluation/v1" ||
      family.verdict !== "pass" || family.authority_effect !== "none" ||
      family.native_runtime_claim !== false ||
      family.collision_freedom_claim !== false ||
      array(family.findings, "ENTITY_PARITY_FAMILY_INVALID").length !== 0 ||
      !same(positive, {declared: 5, passed: 5, failed: 0, unaccounted: 0}) ||
      !same(hostiles, {declared: 7, represented: 7, unrepresented: 0}) ||
      !same(routes, {declared: 4, observed: 4, conforming: 4,
        unaccounted: 0})) {
    return fail("ENTITY_PARITY_FAMILY_INVALID", handle.language);
  }
  return family;
};

const nativeEvidence = (
  proof: JsonObject,
  handle: Handle,
  owner: OwnerInputs,
): JsonObject => {
  const sourceControls = array(handle.language === "python" ?
    proof.target_source_controls : proof.source_controls,
  "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  const sourceIds = sourceControls.map((item) => {
    const control = object(item, "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
    const controlId = string(control.control_id,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
    const pythonError = controlId === "per-call-validator-bypass" ?
      "PY_ENTITY_PER_CALL_VALIDATOR_SURFACE" : "PY_ENTITY_REQUIRED_SEMANTIC";
    const expectedKeys = handle.language === "typescript" ?
      ["control_id", "evidence_kind", "status"] :
      handle.language === "python" ?
        ["control_id", "evidence_kind", "status", "error_code"] :
        ["control_id", "status", "mechanism", "hostile_sha256"];
    const valid = handle.language === "typescript" ?
      control.status === "rejected" &&
        control.evidence_kind === "target-source-control" :
      handle.language === "python" ? control.status === "rejected" &&
        control.evidence_kind === "python-target-source-control" &&
        control.error_code === pythonError :
      control.status === "killed" && control.mechanism ===
        "non-noop-source-mutation-exact-byte-static-rejection" &&
        /^[a-f0-9]{64}$/u.test(String(control.hostile_sha256)) &&
        control.hostile_sha256 !== handle.target_sha256;
    if (!exactSet(Object.keys(control), expectedKeys) || !valid) {
      return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING",
        `${handle.language}:source-control`);
    }
    return controlId;
  });
  const familyControls = array(proof.predecessor_family_controls,
    "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  const familyIds = familyControls.map((item, index) => {
    const control = object(item, "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
    const expectedMutation = owner.mutations.mutations[index]!;
    const expectedKeys = handle.language === "rust" ?
      ["mutation_id", "hostile_class", "expected_finding_codes",
        "actual_finding_codes", "status", "mechanism"] :
      ["mutation_id", "status"];
    if (!exactSet(Object.keys(control), expectedKeys) ||
        control.status !== "killed" ||
        (handle.language === "rust" &&
          (control.mechanism !== "portable-observation-mutation" ||
           control.mutation_id !== expectedMutation.mutation_id ||
           control.hostile_class !== expectedMutation.hostile_class ||
           !same(control.expected_finding_codes,
             expectedMutation.expected_finding_codes) ||
           !same(control.actual_finding_codes,
             expectedMutation.expected_finding_codes)))) {
      return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING",
        `${handle.language}:family-control`);
    }
    return string(control.mutation_id,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  });
  if (sourceControls.length !== handle.target_control_count ||
      !same(sourceIds, TARGET_CONTROL_IDS[handle.language]) ||
      familyControls.length !== 7 || !same(familyIds, FAMILY_CONTROL_IDS)) {
    return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING",
      `${handle.language}:control-count`);
  }
  let process: JsonObject;
  if (handle.language === "rust") {
    process = object(proof.native_runtime,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
    if (process.compiled !== true || process.executed !== true ||
        process.process_count !== 2 || process.distinct_processes !== true ||
        process.pid_and_workspace_redacted_from_semantic_digest !== true ||
        process.direct_constructor_inaccessible !== true) {
      return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING", "rust:process");
    }
    sha256String(process.replay_semantic_digest_sha256,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  } else {
    process = object(proof.process_evidence,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
    if (process.executions !== 2 || process.distinct_pids !== 2 ||
        (handle.language === "typescript" &&
          process.process_ids_excluded_from_semantic_digest !== true) ||
        (handle.language === "python" &&
          (process.pids_redacted_from_semantic_proof !== true ||
           process.semantic_replay_equal !== true))) {
      return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING",
        `${handle.language}:process`);
    }
    sha256String(process.semantic_replay_sha256,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  }
  return Object.freeze({
    process_evidence: process,
    toolchain: handle.language === "rust" ? object(proof.binding,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING") : object(proof.toolchain,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING"),
    native_runtime_observation: handle.language === "python" ?
      object(proof.native_runtime_observation,
        "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING") : null,
    closed_subset: handle.language === "typescript" ? object(proof.closed_subset,
      "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING") : null,
    native_runtime: handle.language === "rust" ? process : null,
    target_source_controls: Object.freeze(sourceControls),
    predecessor_family_controls: Object.freeze(familyControls),
    target_source_control_count: handle.target_control_count,
    predecessor_family_control_count: 7,
    evidence_classes_kept_distinct: true,
  });
};

const projectDirect = (
  upstream: FactoryUpstreamResultV1,
  handle: Handle,
  owner: OwnerInputs,
): DirectProjection => {
  if (upstream.node_id !== handle.node_id ||
      upstream.provider_id !== handle.provider_id) {
    return fail("ENTITY_PARITY_PROVIDER_MISMATCH", handle.node_id);
  }
  const semanticSha256 = sha256String(upstream.semantic_sha256,
    "ENTITY_PARITY_PROOF_INVALID");
  const output = object(upstream.semantic_output, "ENTITY_PARITY_PROOF_INVALID");
  const expectedOutputKeys = handle.language === "typescript" ? ["proof"] :
    ["proof", "workspace"];
  if (!exactSet(Object.keys(output), expectedOutputKeys)) {
    return fail("ENTITY_PARITY_PROOF_INVALID", `${handle.language}:output-shape`);
  }
  if (handle.language !== "typescript" && !same(output.workspace,
    {isolated: true, cleaned: true, symlinks: false})) {
    return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING",
      `${handle.language}:workspace`);
  }
  const proof = object(output.proof, "ENTITY_PARITY_PROOF_INVALID");
  if (!exactSet(Object.keys(proof), PROOF_KEYS[handle.language])) {
    return fail("ENTITY_PARITY_PROOF_INVALID", `${handle.language}:proof-shape`);
  }
  const semanticJson = canonicalConstructionObservationJson(output);
  if (/"(?:pid|workspace_path|temp_path)"/u.test(semanticJson) ||
      semanticJson.includes("/tmp/")) {
    return fail("ENTITY_PARITY_NATIVE_EVIDENCE_MISSING",
      `${handle.language}:path-or-process-leak`);
  }
  if (proof.schema_version !== handle.proof_schema || proof.result !== "pass" ||
      proof.authority_effect !== "none") {
    return fail("ENTITY_PARITY_PROOF_INVALID", handle.language);
  }
  const target = object(proof.target, "ENTITY_PARITY_TARGET_MISMATCH");
  const observedTargetDigest = handle.language === "rust" ?
    target.source_sha256 : target.target_sha256;
  if (target.target_id !== handle.target_id ||
      observedTargetDigest !== handle.target_sha256 ||
      target.language !== handle.language ||
      target.protocol_id !== handle.protocol_id) {
    return fail("ENTITY_PARITY_TARGET_MISMATCH", handle.language);
  }
  const binding = object(proof.binding, "ENTITY_PARITY_PROOF_INVALID");
  if (binding.binding_id !== handle.binding_id ||
      binding.binding_sha256 !== handle.binding_sha256) {
    return fail("ENTITY_PARITY_PROOF_INVALID", `${handle.language}:binding`);
  }
  const portable = portableObservation(proof, handle, owner);
  const family = familyEvaluation(proof, handle);
  const native = nativeEvidence(proof, handle, owner);
  const accounting = object(proof.accounting, "ENTITY_PARITY_FAMILY_INVALID");
  const positives = object(accounting.positives, "ENTITY_PARITY_FAMILY_INVALID");
  const routes = object(accounting.construction_routes,
    "ENTITY_PARITY_FAMILY_INVALID");
  const source = object(handle.language === "typescript" ?
    accounting.source_controls : handle.language === "python" ?
      accounting.target_source_controls : accounting.source_hostiles,
  "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  const familyControls = object(accounting.predecessor_family_controls,
    "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING");
  const sourcePassed = handle.language === "typescript" ||
    handle.language === "python" ? source.rejected : source.killed;
  const routePassed = handle.language === "typescript" ? routes.observed :
    handle.language === "python" ? routes.passed : routes.conforming;
  if (positives.declared !== 5 || positives.passed !== 5 ||
      routes.declared !== 4 || routePassed !== 4 ||
      source.declared !== handle.target_control_count ||
      sourcePassed !== handle.target_control_count ||
      familyControls.declared !== 7 || familyControls.killed !== 7) {
    return fail("ENTITY_PARITY_FAMILY_INVALID", `${handle.language}:accounting`);
  }
  return Object.freeze({handle, semantic_sha256: semanticSha256,
    portable: Object.freeze({...portable,
      family: Object.freeze({verdict: family.verdict,
        positives: Object.freeze({declared: 5, passed: 5}),
        hostile_classes: Object.freeze({declared: 7, represented: 7}),
        construction_routes: Object.freeze({declared: 4, conforming: 4})})}),
    native_evidence: native});
};

export const evaluateEntityParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const expectedKeys = ENTITY_DIRECT_HANDLES.map(({node_id: nodeId}) => nodeId);
  if (!exactSet(Object.keys(upstream), expectedKeys)) {
    return fail("ENTITY_PARITY_HANDLE_SET_MISMATCH");
  }
  const owner = decodeOwnerInputs(rawInputs);
  const direct = ENTITY_DIRECT_HANDLES.map((handle) =>
    projectDirect(upstream[handle.node_id]!, handle, owner));
  const reference = direct[0]!.portable;
  for (const projection of direct.slice(1)) {
    if (!same(projection.portable, reference)) {
      return fail("ENTITY_PARITY_PORTABLE_DRIFT", projection.handle.language);
    }
  }
  return Object.freeze({owner, direct, portable_projection: reference});
};

const directProof = (upstream: any, index = 0): any =>
  upstream[ENTITY_DIRECT_HANDLES[index]!.node_id].semantic_output.proof;

const parityHostiles = Object.freeze([
  Object.freeze({id: "join/missing-handle", code: "ENTITY_PARITY_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[ENTITY_DIRECT_HANDLES[0]!.node_id]; }}),
  Object.freeze({id: "join/wrong-provider", code: "ENTITY_PARITY_PROVIDER_MISMATCH", apply: (u: any) => { u[ENTITY_DIRECT_HANDLES[0]!.node_id].provider_id = "wrong-provider"; }}),
  Object.freeze({id: "join/proof-schema", code: "ENTITY_PARITY_PROOF_INVALID", apply: (u: any) => { directProof(u).schema_version = "WrongProof/v1"; }}),
  Object.freeze({id: "join/wrong-target", code: "ENTITY_PARITY_TARGET_MISMATCH", apply: (u: any) => { directProof(u).target.target_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/wrong-protocol", code: "ENTITY_PARITY_TARGET_MISMATCH", apply: (u: any) => { directProof(u).target.protocol_id = "wrong-protocol/v1"; }}),
  Object.freeze({id: "join/wrong-binding", code: "ENTITY_PARITY_PROOF_INVALID", apply: (u: any) => { directProof(u).binding.binding_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/stale-definition", code: "ENTITY_PARITY_OWNER_MATERIAL_INVALID", apply: (u: any) => { directProof(u).observation.definition_ref.sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/wrong-observer", code: "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { directProof(u).observation.observer_ref.observer_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/wrong-provider-lock", code: "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { directProof(u).observation.observer_ref.provider_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/totals-only", code: "ENTITY_PARITY_PROOF_INVALID", apply: (u: any) => { u[ENTITY_DIRECT_HANDLES[0]!.node_id].semantic_output = {accounting: {positives_declared: 5, positives_passed: 5}}; }}),
  Object.freeze({id: "join/route-set", code: "ENTITY_PARITY_ROUTE_INVALID", apply: (u: any) => { directProof(u).observation.route_traces[0].route_id = "wrong-route"; }}),
  Object.freeze({id: "join/validator-order", code: "ENTITY_PARITY_VALIDATOR_INVALID", apply: (u: any) => { directProof(u).observation.route_traces[0].validator_trace.reverse(); }}),
  Object.freeze({id: "join/failure-forms-snapshot", code: "ENTITY_PARITY_FAILURE_INVALID", apply: (u: any) => { directProof(u).observation.validation_failure_probe.result.snapshot_created = true; }}),
  Object.freeze({id: "join/snapshot-ledger", code: "ENTITY_PARITY_SNAPSHOT_INVALID", apply: (u: any) => { directProof(u).observation.snapshots.pop(); }}),
  Object.freeze({id: "join/identity-component", code: "ENTITY_PARITY_IDENTITY_INVALID", apply: (u: any) => { directProof(u).observation.snapshots[0].identity[0].normalized_value_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/lifecycle-predecessor", code: "ENTITY_PARITY_LIFECYCLE_INVALID", apply: (u: any) => { directProof(u).observation.snapshots[2].predecessor_snapshot_id = null; }}),
  Object.freeze({id: "join/same-identity-equality", code: "ENTITY_PARITY_EQUALITY_INVALID", apply: (u: any) => { directProof(u).observation.equality_probes[0].observed_equal = false; }}),
  Object.freeze({id: "join/distinct-identity-equality", code: "ENTITY_PARITY_EQUALITY_INVALID", apply: (u: any) => { directProof(u).observation.equality_probes[1].observed_equal = true; }}),
  Object.freeze({id: "join/hash-incongruent", code: "ENTITY_PARITY_HASH_CONGRUENCE_INVALID", apply: (u: any) => { directProof(u).observation.equality_probes[0].right_hash_sha256 = "0".repeat(64); }}),
  Object.freeze({id: "join/mutable-snapshot", code: "ENTITY_PARITY_IMMUTABILITY_INVALID", apply: (u: any) => { directProof(u).observation.snapshots[0].frozen = false; }}),
  Object.freeze({id: "join/remove-base-validator", code: "ENTITY_PARITY_EXTENSION_INVALID", apply: (u: any) => { directProof(u).observation.extension.base_validators_preserved = false; }}),
  Object.freeze({id: "join/replace-identity-resolver", code: "ENTITY_PARITY_EXTENSION_INVALID", apply: (u: any) => { directProof(u).observation.extension.identity_resolver_preserved = false; }}),
  Object.freeze({id: "join/extension-cycle", code: "ENTITY_PARITY_EXTENSION_INVALID", apply: (u: any) => { directProof(u).observation.extension.cycle_detected = true; }}),
  Object.freeze({id: "join/family-count", code: "ENTITY_PARITY_FAMILY_INVALID", apply: (u: any) => { directProof(u).family_evaluation.positive_obligation_accounting.passed = 4; }}),
  Object.freeze({id: "join/source-control-renamed", code: "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { directProof(u).source_controls[0].control_id = "renamed-target-control"; }}),
  Object.freeze({id: "join/family-control-renamed", code: "ENTITY_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { directProof(u).predecessor_family_controls[0].mutation_id = "renamed-family-control"; }}),
] as const);

export const proveEntityParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
): EntityParityProofV1 => {
  const evaluated = evaluateEntityParity(upstream, rawInputs);
  const hostileMutations = parityHostiles.map(({id, code, apply}) => {
    const mutated = clone(upstream);
    apply(mutated);
    try {
      evaluateEntityParity(mutated, rawInputs);
    } catch (error: unknown) {
      if (isObject(error) && error.code === code) return Object.freeze({
        mutation_id: id, status: "killed" as const,
        finding_code: code as EntityParityFindingCode,
      });
      throw error;
    }
    return fail("ENTITY_PARITY_PORTABLE_DRIFT", `survived:${id}`);
  });
  return Object.freeze({
    schema_version: "EntityParityProof/v1" as const,
    result: "pass" as const,
    composed_from: Object.freeze(evaluated.direct.map(
      ({handle, semantic_sha256}) => Object.freeze({
        node_id: handle.node_id, provider_id: handle.provider_id,
        semantic_sha256, target_id: handle.target_id,
        target_sha256: handle.target_sha256, language: handle.language,
        protocol_id: handle.protocol_id,
        binding_sha256: handle.binding_sha256,
      }))),
    owner_refs: Object.freeze({
      definition_id: evaluated.owner.definition.definition_id,
      definition_sha256: evaluated.owner.definition_sha256,
      denominator_id: evaluated.owner.denominator.denominator_id,
      denominator_sha256: evaluated.owner.denominator.denominator_sha256,
      descriptor_id: string(evaluated.owner.descriptor.descriptor_id,
        "ENTITY_PARITY_RAW_INPUT_INVALID"),
      descriptor_sha256: evaluated.owner.descriptor_sha256,
      mutation_catalogue_sha256: evaluated.owner.mutation_catalogue_sha256,
    }),
    portable_projection: evaluated.portable_projection,
    native_evidence_by_language: Object.freeze(evaluated.direct.map(
      ({handle, native_evidence: evidence}) => Object.freeze({
        language: handle.language, evidence}))),
    obligations: Object.freeze(PARITY_OBLIGATION_IDS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: Object.freeze(hostileMutations),
    claim_ceiling: "same-host same-oracle portable Entity parity over the exact locked TypeScript, Python, and Rust Settlement Entity direct handles and owner fixtures; typed stable identity, immutable lifecycle snapshots, identity-only equality, own-language equal-identity hash congruence, owner-bound base-before-extension validation, structured no-snapshot failure, exact construction routes, additive acyclic extension, and distinct target-source versus predecessor-family controls are compared while native hash bytes and mechanisms remain separate; no arbitrary-language equivalence, cross-language hash-byte equality, collision freedom, candidate projection, promotion, publication, release, deployment, or production claim",
    authority_effect: "none" as const,
  });
};

const exactRelation = (
  value: unknown,
  relationId: string,
  sourceType: string,
  targetType: string,
  cyclePolicy: string,
): boolean => isObject(value) &&
  exactSet(Object.keys(value), ["relation_id", "source_type", "target_type",
    "cycle_policy"]) && value.relation_id === relationId &&
  value.source_type === sourceType && value.target_type === targetType &&
  value.cycle_policy === cyclePolicy;

const validateEntityReceipt = (
  rawInputs: Readonly<Record<string, string>>,
  spec: EntityReceiptSpec,
): JsonObject => {
  const raw = rawInputs[spec.raw_role];
  if (raw === undefined || Buffer.byteLength(raw, "utf8") !== spec.raw_size_bytes ||
      sha256Bytes(raw) !== spec.raw_sha256) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      `${spec.raw_role}:bytes`);
  }
  const receipt = parseObject(raw, "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const handle = ENTITY_DIRECT_HANDLES[spec.handle_index];
  if (receipt.schema_version !==
        "domainspec.remaining-meta-type-entity-receipt/v1" ||
      receipt.swu_id !== spec.swu_id || receipt.task_id !== "TASK-RMT-ENTITY" ||
      receipt.work_pack_id !== "WP-RMT-001" || receipt.result !== "pass" ||
      receipt.authority_effect !== "none") {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      `${spec.raw_role}:status`);
  }
  if (!same(receipt.dependency_receipt, ENTITY_002_RECEIPT_REF)) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      `${spec.raw_role}:dependency-receipt`);
  }
  const artifacts = array(receipt.material_artifacts,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID").map((item) =>
    object(item, "ENTITY_RELATION_OWNER_MATERIAL_INVALID"));
  if (artifacts.length !== spec.artifact_roles.length ||
      !exactSet(artifacts.map((artifact) => string(artifact.role,
        "ENTITY_RELATION_OWNER_MATERIAL_INVALID")), spec.artifact_roles) ||
      !exactSet(artifacts.map((artifact) => string(artifact.path,
        "ENTITY_RELATION_OWNER_MATERIAL_INVALID")), artifacts.map((artifact) =>
        string(artifact.path, "ENTITY_RELATION_OWNER_MATERIAL_INVALID")))) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      `${spec.raw_role}:artifacts`);
  }
  const rows = artifacts.map((artifact) => {
    if (!exactSet(Object.keys(artifact), ["role", "path", "sha256",
      "size_bytes"]) || !Number.isSafeInteger(artifact.size_bytes) ||
      Number(artifact.size_bytes) <= 0) {
      return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
        `${spec.raw_role}:artifact-row`);
    }
    const path = string(artifact.path, "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    const digest = sha256String(artifact.sha256,
      "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    return {path, digest, size: Number(artifact.size_bytes)};
  }).sort((left, right) => compareUtf8(left.path, right.path));
  const inventory = object(receipt.material_inventory,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const inventoryBytes = rows.map(({path, digest, size}) =>
    `${digest}\t${size}\t${path}\n`).join("");
  if (inventory.file_count !== artifacts.length ||
      inventory.sha256 !== sha256Bytes(inventoryBytes)) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      `${spec.raw_role}:inventory`);
  }
  const requireArtifact = (role: string, path: string, digest: string): void => {
    const matching = artifacts.filter((artifact) => artifact.role === role);
    if (matching.length !== 1 || matching[0]!.path !== path ||
        matching[0]!.sha256 !== digest) {
      return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
        `${spec.raw_role}:${role}`);
    }
  };
  requireArtifact(spec.provider_role, spec.provider_path, handle.provider_sha256);
  requireArtifact(spec.target_role, spec.target_path, handle.target_sha256);
  requireArtifact(spec.binding_role, spec.binding_path,
    handle.binding_file_sha256);
  requireArtifact(spec.observer_role, spec.observer_path, handle.observer_sha256);

  const target = object(spec.handle_index === 0 ? receipt.typescript_target :
    receipt.implemented_target, "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  if (target.target_id !== handle.target_id ||
      target.protocol_id !== handle.protocol_id ||
      (spec.handle_index !== 0 && target.language !== handle.language)) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      `${spec.raw_role}:target`);
  }
  const binding = object(spec.handle_index === 0 ? receipt.realization_binding :
    receipt.native_proof, "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const observedBinding = spec.handle_index === 1 ? binding.binding_self_sha256 :
    binding.binding_sha256;
  if (binding.binding_path !== spec.binding_path ||
      binding.binding_file_sha256 !== handle.binding_file_sha256 ||
      observedBinding !== handle.binding_sha256) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      `${spec.raw_role}:binding`);
  }
  if (spec.handle_index === 0) {
    const accounting = object(receipt.proof_accounting,
      "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    const source = object(accounting.target_source_controls,
      "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    const family = object(accounting.predecessor_family_observation_controls,
      "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    if (source.accounting !== "10/10" || family.accounting !== "7/7") {
      return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
        `${spec.raw_role}:accounting`);
    }
  } else if (spec.handle_index === 1) {
    if (!same(binding.semantic_accounting, {
      positive_obligations: "5/5", construction_routes: "4/4",
      target_source_controls: "11/11", predecessor_family_controls: "7/7",
    })) {
      return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
        `${spec.raw_role}:accounting`);
    }
  } else {
    const source = object(binding.rust_source_controls,
      "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    const family = object(binding.predecessor_family_controls,
      "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    if (binding.positive_obligations !== "5/5" ||
        binding.construction_routes !== "4/4" || source.accounting !== "12/12" ||
        source.mechanism !==
          "genuine non-noop Rust source mutations rejected by exact-source static binding" ||
        source.executed_mutant_behavior_claim !== false ||
        !same(source.scope, TARGET_CONTROL_IDS.rust) || family.accounting !== "7/7" ||
        family.mechanism !==
          "portable Entity lifecycle observation mutation and family evaluation" ||
        family.separate_from_rust_source_controls !== true) {
      return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
        `${spec.raw_role}:accounting`);
    }
  }
  return receipt;
};

const relationOwnerInputs = (
  rawInputs: Readonly<Record<string, string>>,
) => {
  if (!exactSet(Object.keys(rawInputs), Object.keys(ENTITY_RELATION_RAW_PATHS))) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID", "roles");
  }
  const parityRaw = Object.freeze(Object.fromEntries(
    Object.keys(ENTITY_PARITY_RAW_PATHS).map((role) =>
      [role, rawInputs[role]!]))) as Readonly<Record<string, string>>;
  let owner: OwnerInputs;
  try {
    owner = decodeOwnerInputs(parityRaw);
  } catch (error: unknown) {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID",
      error instanceof Error ? error.message : String(error));
  }
  const descriptor = owner.descriptor;
  const admission = parseObject(rawInputs.protocol_admission,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const ontology = parseObject(rawInputs.ontology,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const decision = exactRawObject(rawInputs, "entity_decision",
    ENTITY_DECISION_REF.sha256, 8428);
  const valueObjectReceipt = exactRawObject(rawInputs, "value_object_receipt",
    VALUE_OBJECT_RECEIPT_REF.sha256, 11040);
  const valueObjectCandidate = exactRawObject(rawInputs,
    "value_object_candidate", VALUE_OBJECT_CANDIDATE_REF.sha256, 16716);
  const portable = object(descriptor.portable_architecture,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const descriptorRelations = array(portable.relations,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const admissionRelations = array(admission.selected_relations,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const ontologyRelations = array(ontology.relation_definitions,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const expected = [
    ["architecture.constructed_by", "architecture.EntityImplementation",
      "architecture.EntityFactoryProvider", "not-applicable"],
    ["architecture.validated_by", "architecture.EntityFactoryProvider",
      "architecture.RuleImplementation", "not-applicable"],
    ["architecture.extends_factory", "architecture.EntityFactoryProvider",
      "architecture.EntityFactoryProvider", "acyclic"],
  ] as const;
  const exact = (relations: unknown[]) => relations.length === expected.length &&
    expected.every(
    ([id, source, target, cycle]) => relations.filter((row) =>
      exactRelation(row, id, source, target, cycle)).length === 1);
  const expectedOntology = [
    {id: "architecture.constructed_by",
      sourceTypes: ["architecture.ValueObjectImplementation",
        "architecture.EntityImplementation"],
      targetTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      pairs: [["architecture.ValueObjectImplementation",
        "architecture.ValueObjectFactoryProvider"],
      ["architecture.EntityImplementation",
        "architecture.EntityFactoryProvider"]], cycle: "not-applicable"},
    {id: "architecture.validated_by",
      sourceTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      targetTypes: ["architecture.RuleImplementation"],
      pairs: [["architecture.ValueObjectFactoryProvider",
        "architecture.RuleImplementation"],
      ["architecture.EntityFactoryProvider",
        "architecture.RuleImplementation"]], cycle: "not-applicable"},
    {id: "architecture.extends_factory",
      sourceTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      targetTypes: ["architecture.ValueObjectFactoryProvider",
        "architecture.EntityFactoryProvider"],
      pairs: [["architecture.ValueObjectFactoryProvider",
        "architecture.ValueObjectFactoryProvider"],
      ["architecture.EntityFactoryProvider",
        "architecture.EntityFactoryProvider"]], cycle: "acyclic"},
  ] as const;
  const exactStringSet = (value: unknown, expectedValues: readonly string[]):
  boolean => Array.isArray(value) &&
    value.every((item) => typeof item === "string") &&
    exactSet(value, expectedValues);
  const exactPairSet = (value: unknown, pairs: readonly (
  readonly [string, string])[]): boolean => {
    if (!Array.isArray(value)) return false;
    const observed = value.map((pair) => {
      if (!isObject(pair) || !exactSet(Object.keys(pair),
        ["source_type", "target_type"]) ||
        typeof pair.source_type !== "string" ||
        typeof pair.target_type !== "string") return null;
      return `${pair.source_type}\u0000${pair.target_type}`;
    });
    return observed.every((pair): pair is string => pair !== null) &&
      exactSet(observed, pairs.map(([source, target]) =>
        `${source}\u0000${target}`));
  };
  const exactOntology = expectedOntology.every(
    ({id, sourceTypes, targetTypes, pairs, cycle}) => {
      const matching = ontologyRelations.filter((row) =>
        isObject(row) && row.relation_id === id);
      if (matching.length !== 1 || !isObject(matching[0])) return false;
      const row = matching[0]!;
      return exactStringSet(row.source_types, sourceTypes) &&
        exactStringSet(row.target_types, targetTypes) &&
        exactPairSet(row.allowed_type_pairs, pairs) &&
        row.cycle_policy === cycle && row.authority_effect === "none";
    });
  const properties = object(portable.properties,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const extension = object(portable.extension_contract,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const descriptorProtocols = array(descriptor.language_bindings,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID").map((item) => {
    const binding = object(item, "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
    return {language: binding.language, form_id: binding.form_id,
      protocol_id: binding.protocol_id, status: binding.status,
      implementation_status: binding.implementation_status,
      profile_ref: binding.profile_ref};
  });
  const expectedProperties = Object.entries(ENTITY_PROPERTIES).map(
    ([propertyId, expectedValue]) =>
      ({property_id: propertyId, expected: expectedValue}));
  const descriptorProof = object(descriptor.proof_contract,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const admissionDenominator = object(admission.proof_denominator,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const descriptorRef = object(admission.descriptor_ref,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const candidateMetaType = object(valueObjectCandidate.meta_type,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const candidateArchitecture = object(
    valueObjectCandidate.architecture_implementation,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const candidateLifecycle = object(valueObjectCandidate.lifecycle,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const receiptCandidate = object(valueObjectReceipt.candidate_projection,
    "ENTITY_RELATION_OWNER_MATERIAL_INVALID");
  const expectedReceiptCandidate = {
    ...VALUE_OBJECT_CANDIDATE_REF, size_bytes: 16716,
    schema_version: "domainspec.meta-type-implementation-candidate/v1",
    candidate_id:
      "candidate.settlement.settlement-value.value-object-implementation/v1",
    candidate_kind: "MetaTypeImplementationSlice/v1", meta_type_id: "DS-D1.2",
    architecture_type_id: "architecture.ValueObjectImplementation",
    factory_provider_type_id: "architecture.ValueObjectFactoryProvider",
    canonical_maturity: "active", architecture_mapping_status: "candidate-mapped",
    implementation_evidence_status: "candidate", authority_effect: "none",
    publication_class: "internal",
  };
  const expectedSemanticContinuity = {
    value_object_receipt_id: "RMT-VO-007", value_object_meta_type_id: "DS-D1.2",
    value_object_architecture_type_id: "architecture.ValueObjectImplementation",
    value_object_candidate_id:
      "candidate.settlement.settlement-value.value-object-implementation/v1",
    value_object_result: "pass", entity_growth_is_monotonic: true,
    value_object_semantic_slices_preserved: true,
    prior_value_object_whole_file_ontology_projection_and_profile_hashes:
      "historical-admission-snapshots-after-monotonic-shared-material-growth",
    current_value_object_receipt_and_candidate_refs: "live-and-rehashable",
    stale_prior_shared_material_hashes_are_value_object_regression: false,
  };
  const receipts = ENTITY_RECEIPT_SPECS.map((spec) =>
    validateEntityReceipt(rawInputs, spec));
  if (descriptor.schema_version !==
        "domainspec.entity-cross-language-realization-descriptor/v1" ||
      descriptor.descriptor_id !==
        "domainspec.entity.stable-identity-lifecycle-factory/v1" ||
      descriptor.descriptor_protocol_id !==
        "domainspec.validated-extensible-entity-factory/v1" ||
      descriptor.descriptor_status !== "candidate-protocol-only" ||
      descriptor.meta_type_ref !== "DS-D1.1" ||
      descriptor.architecture_type_ref !== "architecture.EntityImplementation" ||
      descriptor.factory_provider_type_ref !==
        "architecture.EntityFactoryProvider" || descriptor.authority_effect !== "none" ||
      !same(descriptor.decision_ref, ENTITY_DECISION_REF) ||
      !same(descriptor.value_object_continuity_refs,
        [VALUE_OBJECT_RECEIPT_REF, VALUE_OBJECT_CANDIDATE_REF]) ||
      portable.type_id !== "architecture.EntityImplementation" ||
      portable.factory_provider_type_id !== "architecture.EntityFactoryProvider" ||
      portable.base_type_id !== "architecture.DomainConceptImplementation" ||
      admission.schema_version !== "domainspec.entity-protocol-admission/v1" ||
      admission.admission_id !== "RMT-ENTITY-001-candidate-protocol-admission" ||
      admission.admission_status !== "candidate-protocol-only" ||
      admission.result !== "pass" || admission.meta_type_id !== "DS-D1.1" ||
      admission.architecture_type_id !== "architecture.EntityImplementation" ||
      admission.factory_provider_type_id !==
        "architecture.EntityFactoryProvider" ||
      admission.descriptor_protocol_id !==
        "domainspec.validated-extensible-entity-factory/v1" ||
      admission.authority_effect !== "none" ||
      !same(admission.decision_ref, {...ENTITY_DECISION_REF,
        selected_option_id: "W1-ENTITY-A-VALIDATED-EXTENSIBLE-FACTORY"}) ||
      !same(admission.dependency_refs, [
        {...VALUE_OBJECT_RECEIPT_REF, required_result: "pass"},
        {...VALUE_OBJECT_CANDIDATE_REF, required_meta_type_id: "DS-D1.2"},
      ]) || !same(admission.semantic_continuity, expectedSemanticContinuity) ||
      descriptorRef.path !== DESCRIPTOR_PATH ||
      descriptorRef.sha256 !== owner.descriptor_sha256 ||
      !same(descriptor.material_refs, ENTITY_MATERIAL_REFS) ||
      !same(admission.material_refs, ENTITY_MATERIAL_REFS) ||
      sha256Bytes(rawInputs.ontology!) !== ENTITY_MATERIAL_REFS[0].sha256 ||
      !same(properties, ENTITY_PROPERTIES) ||
      !same(admission.selected_properties, expectedProperties) ||
      !same(descriptorProtocols, ENTITY_PROTOCOLS) ||
      !same(admission.selected_protocols, ENTITY_PROTOCOLS) ||
      !same(portable.construction_routes, ENTITY_ROUTES) ||
      !same(admission.construction_routes, ENTITY_ROUTES) ||
      !same(portable.construction_pipeline, ENTITY_PIPELINE) ||
      !same(admission.construction_pipeline, ENTITY_PIPELINE) ||
      array(descriptorProof.positive_obligations,
        "ENTITY_RELATION_OWNER_MATERIAL_INVALID").length !== 5 ||
      array(descriptorProof.semantic_hostiles,
        "ENTITY_RELATION_OWNER_MATERIAL_INVALID").length !== 7 ||
      array(descriptorProof.construction_route_obligations,
        "ENTITY_RELATION_OWNER_MATERIAL_INVALID").length !== 4 ||
      !same(admissionDenominator, {positive_obligations: "5/5",
        semantic_hostiles: "7/7", construction_routes: "4/4",
        structural_controls: "5/5"}) ||
      ontology.schema_version !== "domainspec-architecture-property-ontology/v1" ||
      ontology.ontology_id !== "implementation-conformance.architecture-properties" ||
      ontology.status !== "candidate" ||
      decision.schema_version !== "ArchitectureMappingDecision/v1" ||
      decision.decision_id !== "DS-OF-W1-ENTITY-001" ||
      decision.status !==
        "accepted-target-awaiting-ontology-and-profile-materialization" ||
      decision.meta_type_id !== "DS-D1.1" ||
      decision.selected_option_id !==
        "W1-ENTITY-A-VALIDATED-EXTENSIBLE-FACTORY" ||
      decision.authority_effect !== "none" ||
      valueObjectReceipt.schema_version !==
        "domainspec.meta-type-candidate-projection-receipt/v1" ||
      valueObjectReceipt.swu_id !== "RMT-VO-007" ||
      valueObjectReceipt.task_id !== "TASK-RMT-VO" ||
      valueObjectReceipt.work_pack_id !== "WP-RMT-001" ||
      valueObjectReceipt.result !== "pass" ||
      valueObjectReceipt.authority_effect !== "none" ||
      !same(receiptCandidate, expectedReceiptCandidate) ||
      valueObjectCandidate.schema_version !==
        "domainspec.meta-type-implementation-candidate/v1" ||
      valueObjectCandidate.candidate_id !==
        "candidate.settlement.settlement-value.value-object-implementation/v1" ||
      valueObjectCandidate.candidate_kind !== "MetaTypeImplementationSlice/v1" ||
      valueObjectCandidate.projection_swu_id !== "RMT-VO-007" ||
      valueObjectCandidate.task_id !== "TASK-RMT-VO" ||
      valueObjectCandidate.work_pack_id !== "WP-RMT-001" ||
      candidateMetaType.id !== "DS-D1.2" ||
      candidateArchitecture.type_id !== "architecture.ValueObjectImplementation" ||
      candidateArchitecture.factory_provider_type_id !==
        "architecture.ValueObjectFactoryProvider" ||
      candidateLifecycle.canonical_maturity !== "active" ||
      candidateLifecycle.architecture_mapping_status !== "candidate-mapped" ||
      candidateLifecycle.implementation_evidence_status !== "candidate" ||
      candidateLifecycle.authority_effect !== "none" ||
      valueObjectCandidate.publication_class !== "internal" ||
      !exact(descriptorRelations) || !exact(admissionRelations) ||
      !exactOntology || admission.result !== "pass" ||
      admission.authority_effect !== "none" || ontology.authority_effect !== "none" ||
      properties["creation.extension_policy"] !== "additive-only" ||
      properties["creation.base_invariants_preserved"] !== true ||
      properties["identity.stable_across_lifecycle"] !== true ||
      properties["lifecycle.observation_mode"] !==
        "immutable-snapshot-sequence" ||
      extension.policy !== "additive-only" ||
      extension.base_invariants_preserved !== true ||
      extension.cycle_policy !== "acyclic") {
    return fail("ENTITY_RELATION_OWNER_MATERIAL_INVALID", "relations");
  }
  return Object.freeze({owner, admission, ontology, decision,
    value_object_receipt: valueObjectReceipt,
    value_object_candidate: valueObjectCandidate, parityRaw,
    dependency_receipts: Object.freeze(receipts)});
};

export const evaluateEntityRelations = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const directKeys = ENTITY_DIRECT_HANDLES.map(({node_id: nodeId}) => nodeId);
  const expectedKeys = [...directKeys, ENTITY_PARITY_HANDLE.node_id];
  if (!exactSet(Object.keys(upstream), expectedKeys)) {
    return fail("ENTITY_RELATION_HANDLE_SET_MISMATCH");
  }
  const relationOwner = relationOwnerInputs(rawInputs);
  const directUpstream = Object.freeze(Object.fromEntries(directKeys.map(
    (nodeId) => [nodeId, upstream[nodeId]!]))) as Readonly<Record<string,
      FactoryUpstreamResultV1>>;
  const expectedParity = proveEntityParity(directUpstream,
    relationOwner.parityRaw);
  const parityUpstream = upstream[ENTITY_PARITY_HANDLE.node_id]!;
  if (parityUpstream.node_id !== ENTITY_PARITY_HANDLE.node_id ||
      parityUpstream.provider_id !== ENTITY_PARITY_HANDLE.provider_id ||
      !/^[a-f0-9]{64}$/u.test(parityUpstream.semantic_sha256)) {
    return fail("ENTITY_RELATION_PARITY_INVALID", "handle");
  }
  const parityOutput = object(parityUpstream.semantic_output,
    "ENTITY_RELATION_PARITY_INVALID");
  const parityProof = object(parityOutput.proof,
    "ENTITY_RELATION_PARITY_INVALID");
  if (!same(parityProof, expectedParity)) {
    return fail("ENTITY_RELATION_PARITY_INVALID", "proof");
  }
  const rows = ENTITY_DIRECT_HANDLES.flatMap((handle) => {
    const base = relationOwner.owner.definition.factories.base;
    const extension = relationOwner.owner.definition.factories.extension;
    return [
      Object.freeze({language: handle.language,
        relation_id: "architecture.constructed_by" as const,
        source_id: handle.target_id,
        source_type: "architecture.EntityImplementation",
        target_id: base.factory_id,
        target_type: "architecture.EntityFactoryProvider",
        ordinal: null, cycle_policy: "not-applicable" as const}),
      ...relationOwner.owner.definition.validators.map((validator, ordinal) =>
        Object.freeze({language: handle.language,
          relation_id: "architecture.validated_by" as const,
          source_id: validator.origin === "base" ? base.factory_id :
            extension.factory_id,
          source_type: "architecture.EntityFactoryProvider",
          target_id: validator.validator_id,
          target_type: "architecture.RuleImplementation",
          ordinal, cycle_policy: "not-applicable" as const})),
      Object.freeze({language: handle.language,
        relation_id: "architecture.extends_factory" as const,
        source_id: extension.factory_id,
        source_type: "architecture.EntityFactoryProvider",
        target_id: base.factory_id,
        target_type: "architecture.EntityFactoryProvider",
        ordinal: null, cycle_policy: "acyclic" as const}),
    ];
  });
  if (rows.filter(({relation_id: id}) => id ===
      "architecture.constructed_by").length !== 3) {
    return fail("ENTITY_RELATION_CONSTRUCTED_BY_INVALID");
  }
  if (rows.filter(({relation_id: id}) => id ===
      "architecture.validated_by").length !== 9) {
    return fail("ENTITY_RELATION_VALIDATED_BY_INVALID");
  }
  const extensions = rows.filter(({relation_id: id}) => id ===
    "architecture.extends_factory");
  if (extensions.length !== 3 || extensions.some(({source_id, target_id}) =>
    source_id === target_id)) {
    return fail("ENTITY_RELATION_EXTENDS_FACTORY_INVALID");
  }
  return Object.freeze({relationOwner, directUpstream, expectedParity,
    parityUpstream, relation_rows: Object.freeze(rows)});
};

const parityProofFrom = (upstream: any): any =>
  upstream[ENTITY_PARITY_HANDLE.node_id].semantic_output.proof;

type RelationHostile = Readonly<{
  id: string;
  code: EntityRelationFindingCode;
  apply: (upstream: any, raw: Record<string, string>) => void;
}>;

const relationHostiles: readonly RelationHostile[] = Object.freeze([
  Object.freeze({id: "relation/missing-direct", code: "ENTITY_RELATION_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[ENTITY_DIRECT_HANDLES[0]!.node_id]; }}),
  Object.freeze({id: "relation/missing-parity", code: "ENTITY_RELATION_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[ENTITY_PARITY_HANDLE.node_id]; }}),
  Object.freeze({id: "relation/wrong-parity-provider", code: "ENTITY_RELATION_PARITY_INVALID", apply: (u: any) => { u[ENTITY_PARITY_HANDLE.node_id].provider_id = "wrong-provider"; }}),
  Object.freeze({id: "relation/totals-only-parity", code: "ENTITY_RELATION_PARITY_INVALID", apply: (u: any) => { u[ENTITY_PARITY_HANDLE.node_id].semantic_output = {accounting: {positives: 20}}; }}),
  Object.freeze({id: "relation/parity-proof-drift", code: "ENTITY_RELATION_PARITY_INVALID", apply: (u: any) => { parityProofFrom(u).portable_projection.concept_id = "wrong.Concept"; }}),
  Object.freeze({id: "relation/descriptor-constructed-target", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.relations[0].target_type = "wrong.Factory"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/descriptor-validator-target", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.relations[1].target_type = "wrong.Rule"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/descriptor-extension-cycle", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.relations[2].cycle_policy = "not-applicable"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/descriptor-extension-policy", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.properties["creation.extension_policy"] = "replacement"; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/descriptor-identity-stability", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.descriptor!); x.portable_architecture.properties["identity.stable_across_lifecycle"] = false; r.descriptor = JSON.stringify(x); }}),
  Object.freeze({id: "relation/admission-missing-relation", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.protocol_admission!); x.selected_relations.pop(); r.protocol_admission = JSON.stringify(x); }}),
  Object.freeze({id: "relation/admission-authority", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.protocol_admission!); x.authority_effect = "promote"; r.protocol_admission = JSON.stringify(x); }}),
  Object.freeze({id: "relation/ontology-cross-family-pair", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.ontology!); x.relation_definitions.find((v: any) => v.relation_id === "architecture.extends_factory").allowed_type_pairs[1].target_type = "architecture.ValueObjectFactoryProvider"; r.ontology = JSON.stringify(x); }}),
  Object.freeze({id: "relation/dependency-receipt-result", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.typescript_receipt!); x.result = "fail"; r.typescript_receipt = JSON.stringify(x); }}),
  Object.freeze({id: "relation/ontology-extension-cycle", code: "ENTITY_RELATION_OWNER_MATERIAL_INVALID", apply: (_u: any, r: Record<string, string>) => { const x = JSON.parse(r.ontology!); x.relation_definitions.find((v: any) => v.relation_id === "architecture.extends_factory").cycle_policy = "not-applicable"; r.ontology = JSON.stringify(x); }}),
]);

export const proveEntityRelations = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
): EntityRelationsProofV1 => {
  const evaluated = evaluateEntityRelations(upstream, rawInputs);
  const hostileMutations = relationHostiles.map(({id, code, apply}) => {
    const mutatedUpstream = clone(upstream);
    const mutatedRaw = clone(rawInputs) as Record<string, string>;
    apply(mutatedUpstream, mutatedRaw);
    try {
      evaluateEntityRelations(mutatedUpstream, mutatedRaw);
    } catch (error: unknown) {
      if (isObject(error) && error.code === code) return Object.freeze({
        mutation_id: id, status: "killed" as const, finding_code: code,
      });
      throw error;
    }
    return fail("ENTITY_RELATION_AUTHORITY_INVALID", `survived:${id}`);
  });
  return Object.freeze({
    schema_version: "EntityRelationsProof/v1" as const,
    result: "pass" as const,
    composed_from: Object.freeze([
      ...ENTITY_DIRECT_HANDLES.map((handle) => Object.freeze({
        node_id: handle.node_id, provider_id: handle.provider_id,
        semantic_sha256: upstream[handle.node_id]!.semantic_sha256,
      })),
      Object.freeze({node_id: ENTITY_PARITY_HANDLE.node_id,
        provider_id: ENTITY_PARITY_HANDLE.provider_id,
        semantic_sha256: upstream[ENTITY_PARITY_HANDLE.node_id]!.semantic_sha256}),
    ]),
    relation_rows: evaluated.relation_rows,
    obligations: Object.freeze(RELATION_OBLIGATION_IDS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: Object.freeze(hostileMutations),
    claim_ceiling: "exact candidate-local constructed_by, validated_by, and acyclic extends_factory relation proof over the three locked Settlement Entity direct proofs and their recomputed parity proof, current owner descriptor, protocol admission, and exact combined same-family ontology pairs; this proves owner-bound base-before-extension validators and additive identity-preserving structure, not arbitrary factories, runtime interception, business correctness beyond the fixture, candidate projection, promotion, publication, release, deployment, or production",
    authority_effect: "none" as const,
  });
};
