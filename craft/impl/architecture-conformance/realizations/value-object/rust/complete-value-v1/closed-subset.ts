import {createHash} from "node:crypto";

export const RUST_VALUE_OBJECT_EXPECTED_SOURCE_SHA256 =
  "7ca45e0d5c38a60cb274fdb6658679a58d1019bb719a24addebc5ea1fbe736fb";

export const RUST_VALUE_OBJECT_STATIC_CONTROL_IDS = Object.freeze([
  "reference-identity",
  "partial-currency",
  "partial-minor-units",
  "incongruent-hash",
  "mutable-nested",
  "validator-bypass",
  "protocol-bypass",
  "invalid-forms-object",
] as const);

export type RustValueObjectStaticControlId =
  (typeof RUST_VALUE_OBJECT_STATIC_CONTROL_IDS)[number];

export type RustValueObjectClosedSubsetProofV1 = Readonly<{
  schema_version: "RustValueObjectClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  form: "private-owned-structs-manual-eq-hash-owner-bound-factory";
  trait_contract: "clone-debug-partial-eq-eq-hash";
  extension_contract: "one-way-additive-validation-only";
  mechanism: "exact-source-byte-closed-subset-plus-native-execution";
  authority_effect: "none";
}>;

const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const inspectRustValueObjectClosedSubset = (
  source: string,
): RustValueObjectClosedSubsetProofV1 => {
  if (!/^[\x00-\x7F]*$/u.test(source)) {
    return fail("RUST_VALUE_OBJECT_CLOSED_SUBSET_NON_ASCII");
  }
  if (sha256(source) !== RUST_VALUE_OBJECT_EXPECTED_SOURCE_SHA256) {
    return fail("RUST_VALUE_OBJECT_CLOSED_SUBSET_SOURCE_MISMATCH");
  }
  return Object.freeze({
    schema_version: "RustValueObjectClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: RUST_VALUE_OBJECT_EXPECTED_SOURCE_SHA256,
    form: "private-owned-structs-manual-eq-hash-owner-bound-factory" as const,
    trait_contract: "clone-debug-partial-eq-eq-hash" as const,
    extension_contract: "one-way-additive-validation-only" as const,
    mechanism: "exact-source-byte-closed-subset-plus-native-execution" as const,
    authority_effect: "none" as const,
  });
};

export const rustValueObjectStaticControlSource = (
  source: string,
  controlId: RustValueObjectStaticControlId,
): string => {
  inspectRustValueObjectClosedSubset(source);
  const sources: Readonly<Record<RustValueObjectStaticControlId, string>> =
    Object.freeze({
      "reference-identity": source.replace(
        "self.settlement_account == other.settlement_account",
        "std::ptr::eq(&self.settlement_account, &other.settlement_account)",
      ),
      "partial-currency": source.replace(
        "self.currency_sha256 == other.currency_sha256",
        "true",
      ),
      "partial-minor-units": source.replace(
        "self.minor_units_sha256 == other.minor_units_sha256",
        "true",
      ),
      "incongruent-hash": source.replace(
        "self.settlement_account.hash(state);",
        '"foreign-component".hash(state);',
      ),
      "mutable-nested": source.replace(
        "pub struct SettlementAccountValue {\n    protocol_id: String,",
        "pub struct SettlementAccountValue {\n    pub protocol_id: String,",
      ),
      "validator-bypass": source.replace(
        "let mut validator_trace = vec![trace_entry(BASE_VALIDATORS[0])];",
        "let mut validator_trace = vec![];",
      ),
      "protocol-bypass": source.replace(
        "input.protocol_id == id && input.protocol_sha256 == digest",
        "true",
      ),
      "invalid-forms-object": source.replace(
        "if input.minor_units_negative {",
        "if false && input.minor_units_negative {",
      ),
    });
  const mutated = sources[controlId];
  if (mutated === source) {
    return fail("RUST_VALUE_OBJECT_STATIC_CONTROL_NOOP");
  }
  return mutated;
};
