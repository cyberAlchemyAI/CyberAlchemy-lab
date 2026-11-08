import {createHash} from "node:crypto";

export const RUST_ENTITY_EXPECTED_SOURCE_SHA256 =
  "0df0f880a5a2a01fd06185030f9bcf5e9396cf493fdd8c27a272b9ad4fd208bb";

export const RUST_ENTITY_SOURCE_CONTROL_IDS = Object.freeze([
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
] as const);

export type RustEntitySourceControlId =
  (typeof RUST_ENTITY_SOURCE_CONTROL_IDS)[number];

export type RustEntityClosedSubsetProofV1 = Readonly<{
  schema_version: "RustEntityClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  form: "private-field-struct-manual-identity-eq-hash-bound-factory";
  route_contract: "three-executing-routes-one-pipeline-plus-private-constructor";
  extension_contract: "one-way-additive-composition-no-trait-authority";
  mechanism: "exact-source-byte-closed-subset-plus-native-execution";
  authority_effect: "none";
}>;

const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectRustEntityClosedSubset = (
  source: string,
): RustEntityClosedSubsetProofV1 => {
  if (!/^[\x00-\x7F]*$/u.test(source)) {
    return fail("RUST_ENTITY_CLOSED_SUBSET_NON_ASCII");
  }
  if (sha256(source) !== RUST_ENTITY_EXPECTED_SOURCE_SHA256) {
    return fail("RUST_ENTITY_CLOSED_SUBSET_SOURCE_MISMATCH");
  }
  if (source.includes("pub fn new(") || source.includes("unsafe") ||
      source.includes("trait SettlementEntityFactory")) {
    return fail("RUST_ENTITY_CLOSED_SUBSET_AUTHORITY_BYPASS");
  }
  return Object.freeze({
    schema_version: "RustEntityClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: RUST_ENTITY_EXPECTED_SOURCE_SHA256,
    form: "private-field-struct-manual-identity-eq-hash-bound-factory" as const,
    route_contract:
      "three-executing-routes-one-pipeline-plus-private-constructor" as const,
    extension_contract:
      "one-way-additive-composition-no-trait-authority" as const,
    mechanism:
      "exact-source-byte-closed-subset-plus-native-execution" as const,
    authority_effect: "none" as const,
  });
};

const replaceOnce = (
  source: string,
  search: string,
  replacement: string,
): string => {
  if (source.split(search).length !== 2) {
    return fail("RUST_ENTITY_SOURCE_CONTROL_SENTINEL_INVALID");
  }
  return source.replace(search, replacement);
};

export const rustEntitySourceControl = (
  source: string,
  controlId: RustEntitySourceControlId,
): string => {
  inspectRustEntityClosedSubset(source);
  const sources: Readonly<Record<RustEntitySourceControlId, string>> =
    Object.freeze({
      "per-call-validator-bypass": replaceOnce(source,
        "if !input.owner_matches {",
        "if false && !input.owner_matches {"),
      "remove-base-validator": replaceOnce(source,
        "validator_trace.push(trace_entry(BASE_VALIDATORS[0], 1, if input.owner_matches {",
        "validator_trace.push(trace_entry(BASE_VALIDATORS[1], 1, if input.owner_matches {"),
      "validator-order-swap": replaceOnce(source,
        "validator_trace.push(trace_entry(BASE_VALIDATORS[1], 2, if input.amount_valid {",
        "validator_trace.insert(0, trace_entry(BASE_VALIDATORS[1], 2, if input.amount_valid {"),
      "replace-identity-resolver": replaceOnce(source,
        "organization_id: OrganizationId::resolve(&input.organization_id_sha256),",
        "organization_id: OrganizationId::resolve(&input.settlement_id_sha256),"),
      "allow-extension-cycle": replaceOnce(source,
        "FactoryMode::WithDuplicateBlocked => None,",
        "FactoryMode::WithDuplicateBlocked => Some(*self),"),
      "invalid-input-forms-snapshot": replaceOnce(source,
        "if !input.amount_valid {",
        "if false && !input.amount_valid {"),
      "mutable-snapshot-field": replaceOnce(source,
        "    state_sha256: String,\n}",
        "    pub state_sha256: String,\n}"),
      "complete-field-equality": replaceOnce(source,
        "self.identity == other.identity",
        "self.identity == other.identity && self.state_sha256 == other.state_sha256"),
      "stateful-hash": replaceOnce(source,
        "        self.identity.hash(state);",
        "        self.identity.hash(state);\n        self.state_sha256.hash(state);"),
      "reconstruction-bypass": replaceOnce(source,
        "self.execute_route(ConstructionRoute::DeserializationReconstruction, input)",
        "self.execute_route(ConstructionRoute::Factory, input)"),
      "transition-identity-replacement": replaceOnce(source,
        ".organization_id\n                .normalized_value_sha256()",
        ".settlement_id\n                .normalized_value_sha256()"),
      "public-direct-constructor": replaceOnce(source,
        "    fn new(input: &SettlementEntityInput, identity: SettlementIdentity) -> Self {",
        "    pub fn new(input: &SettlementEntityInput, identity: SettlementIdentity) -> Self {"),
    });
  const hostile = sources[controlId];
  if (hostile === source) return fail("RUST_ENTITY_SOURCE_CONTROL_NOOP");
  return hostile;
};
