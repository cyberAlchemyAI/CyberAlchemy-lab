import { createHash } from "node:crypto";
import { posix, win32 } from "node:path";

import {
  createValidatedHandle,
  readValidatedHandle,
  type ValidatedHandle,
} from "../../../kernel/contracts/validated-handle.js";
import type {
  RuleBindingV1,
  RuleCaseCatalogueV1,
  RuleCaseV1,
  RuleDefinitionV1,
  RuleInputValue,
} from "../contracts/rule-contracts.js";

type JsonObject = Record<string, unknown>;
export type RuleSourceResolver = (
  path: string,
) => string | Uint8Array | Promise<string | Uint8Array>;

export type NormalizedRulePackageV1 = Readonly<{
  schema_version: "NormalizedRulePackage/v1";
  definition: RuleDefinitionV1;
  binding: RuleBindingV1;
  cases: RuleCaseCatalogueV1;
  authority_effect: "none";
}>;

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};
const isRecord = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : isRecord(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;
export const canonicalRuleJson = (value: unknown): string =>
  JSON.stringify(canonicalize(value));
export const computeRuleDocumentDigest = (value: JsonObject, field: string): string => sha256(
  canonicalRuleJson(Object.fromEntries(Object.entries(value).filter(([key]) => key !== field))),
);
const exactKeys = (value: JsonObject, expected: readonly string[]): boolean => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  return actual.length === wanted.length &&
    actual.every((key, index) => key === wanted[index]);
};
const parse = (bytes: string, code: string): JsonObject => {
  let value: unknown;
  try {
    value = JSON.parse(bytes);
  } catch {
    return fail(code);
  }
  return isRecord(value) ? value : fail(code);
};
const string = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 &&
    !/[\u0000-\u001f\u007f]/u.test(value)
    ? value
    : fail(code);
const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z_][A-Za-z0-9_]*$/u;
const safePath = (value: string): boolean =>
  !posix.isAbsolute(value) && !win32.isAbsolute(value) && !value.includes("\\") &&
  !value.split("/").some((part) => part === "" || part === "." || part === "..");

const definitionValue = (value: JsonObject): RuleDefinitionV1 => {
  if (!exactKeys(value, [
    "schema_version", "rule_id", "concept_id", "input_fields", "output_type",
    "determinism", "effects", "definition_sha256", "authority_ref",
    "authority_status", "authority_effect",
  ]) || value.schema_version !== "RuleDefinition/v1" ||
      !Array.isArray(value.input_fields) || value.input_fields.length === 0 ||
      value.output_type !== "boolean" || value.determinism !== "required" ||
      value.effects !== "forbidden" || value.authority_effect !== "none" ||
      (value.authority_status !== "candidate-fixture" &&
       value.authority_status !== "owner-issued") ||
      typeof value.definition_sha256 !== "string" ||
      !SHA256.test(value.definition_sha256)) {
    return fail("RULE_DEFINITION_SCHEMA_INVALID");
  }
  const fields = value.input_fields.map((raw) => {
    if (!isRecord(raw) || !exactKeys(raw, ["name", "value_type"]) ||
        !["string", "number", "boolean", "nullable-string"].includes(
          raw.value_type as string,
        )) {
      return fail("RULE_DEFINITION_INPUT_SCHEMA_INVALID");
    }
    return {
      name: string(raw.name, "RULE_DEFINITION_INPUT_SCHEMA_INVALID"),
      value_type: raw.value_type,
    };
  });
  if (new Set(fields.map(({ name }) => name)).size !== fields.length) {
    return fail("RULE_DEFINITION_INPUT_DUPLICATE");
  }
  if (computeRuleDocumentDigest(value, "definition_sha256") !== value.definition_sha256) {
    return fail("RULE_DEFINITION_DIGEST_STALE");
  }
  return value as RuleDefinitionV1;
};

export const decodeRuleDefinitionV1 = (
  bytes: string,
): ValidatedHandle<RuleDefinitionV1> => {
  const value = definitionValue(parse(bytes, "RULE_DEFINITION_SCHEMA_INVALID"));
  return createValidatedHandle({
    value,
    source_sha256: sha256(bytes),
    validated_refs: [],
  });
};

export const decodeRuleBindingV1 = async (
  bytes: string,
  definitionHandle: ValidatedHandle<RuleDefinitionV1>,
  resolveSource: RuleSourceResolver,
): Promise<ValidatedHandle<RuleBindingV1>> => {
  const definition = readValidatedHandle(definitionHandle);
  const value = parse(bytes, "RULE_BINDING_SCHEMA_INVALID");
  if (!exactKeys(value, [
    "schema_version", "binding_id", "rule_ref", "target_id", "realization_id",
    "source_ref", "symbol_name", "current", "binding_sha256", "authority_effect",
  ]) || value.schema_version !== "RuleBinding/v1" ||
      !["typescript", "python", "rust"].includes(value.target_id as string) ||
      value.current !== true || value.authority_effect !== "none" ||
      !isRecord(value.rule_ref) ||
      !exactKeys(value.rule_ref, ["rule_id", "definition_sha256"]) ||
      !isRecord(value.source_ref) ||
      !exactKeys(value.source_ref, ["path", "sha256", "origin"]) ||
      value.source_ref.origin !== "handwritten-candidate-fixture" ||
      typeof value.binding_sha256 !== "string" ||
      !SHA256.test(value.binding_sha256)) {
    return fail(value.current === false
      ? "RULE_BINDING_NOT_CURRENT"
      : "RULE_BINDING_SCHEMA_INVALID");
  }
  if (value.rule_ref.rule_id !== definition.rule_id ||
      value.rule_ref.definition_sha256 !== definition.definition_sha256) {
    return fail("RULE_BINDING_DEFINITION_STALE");
  }
  const path = string(value.source_ref.path, "RULE_BINDING_SOURCE_REF_INVALID");
  const symbolName = string(value.symbol_name, "RULE_BINDING_SYMBOL_INVALID");
  if (!safePath(path) || !IDENTIFIER.test(symbolName) ||
      typeof value.source_ref.sha256 !== "string" ||
      !SHA256.test(value.source_ref.sha256)) {
    return fail(!IDENTIFIER.test(symbolName)
      ? "RULE_BINDING_SYMBOL_INVALID"
      : "RULE_BINDING_SOURCE_REF_INVALID");
  }
  let source: string | Uint8Array;
  try {
    source = await resolveSource(path);
  } catch {
    return fail("RULE_BINDING_SOURCE_MISSING");
  }
  if (sha256(source) !== value.source_ref.sha256) {
    return fail("RULE_BINDING_SOURCE_STALE");
  }
  if (computeRuleDocumentDigest(value, "binding_sha256") !== value.binding_sha256) {
    return fail("RULE_BINDING_DIGEST_STALE");
  }
  const binding = value as RuleBindingV1;
  return createValidatedHandle({
    value: binding,
    source_sha256: sha256(bytes),
    validated_refs: [{ id: path, sha256: binding.source_ref.sha256 }],
  });
};

const matchesType = (
  value: RuleInputValue,
  type: RuleDefinitionV1["input_fields"][number]["value_type"],
): boolean => type === "string"
  ? typeof value === "string"
  : type === "number"
    ? typeof value === "number" && Number.isFinite(value)
    : type === "boolean"
      ? typeof value === "boolean"
      : value === null || typeof value === "string";

export const decodeRuleCaseCatalogueV1 = (
  bytes: string,
  definitionHandle: ValidatedHandle<RuleDefinitionV1>,
): ValidatedHandle<RuleCaseCatalogueV1> => {
  const definition = readValidatedHandle(definitionHandle);
  const value = parse(bytes, "RULE_CASE_CATALOGUE_SCHEMA_INVALID");
  if (!exactKeys(value, [
    "schema_version", "rule_ref", "cases", "catalogue_sha256", "owner_ref",
    "authority_effect",
  ]) || value.schema_version !== "RuleCaseCatalogue/v1" ||
      !isRecord(value.rule_ref) ||
      !exactKeys(value.rule_ref, ["rule_id", "definition_sha256"]) ||
      !Array.isArray(value.cases) || value.cases.length === 0 ||
      value.owner_ref !== "rule-case-owner" || value.authority_effect !== "none" ||
      typeof value.catalogue_sha256 !== "string" ||
      !SHA256.test(value.catalogue_sha256)) {
    return fail("RULE_CASE_CATALOGUE_SCHEMA_INVALID");
  }
  if (value.rule_ref.rule_id !== definition.rule_id ||
      value.rule_ref.definition_sha256 !== definition.definition_sha256) {
    return fail("RULE_CASE_DEFINITION_STALE");
  }
  const expectedFields = [...definition.input_fields]
    .sort((left, right) => compareUtf8(left.name, right.name));
  const cases: RuleCaseV1[] = value.cases.map((raw) => {
    if (!isRecord(raw) || !exactKeys(raw, ["case_id", "input", "expected_outcome"]) ||
        !isRecord(raw.input)) {
      return fail("RULE_CASE_SCHEMA_INVALID");
    }
    if (typeof raw.expected_outcome !== "boolean") {
      return fail("RULE_CASE_OUTCOME_NON_BOOLEAN");
    }
    const inputNames = Object.keys(raw.input).sort(compareUtf8);
    if (inputNames.length !== expectedFields.length ||
        inputNames.some((name, index) => name !== expectedFields[index]?.name)) {
      return fail("RULE_CASE_INPUT_TOTALITY_INVALID");
    }
    for (const field of expectedFields) {
      if (!matchesType(raw.input[field.name] as RuleInputValue, field.value_type)) {
        return fail("RULE_CASE_INPUT_TYPE_INVALID");
      }
    }
    return {
      case_id: string(raw.case_id, "RULE_CASE_ID_INVALID"),
      input: raw.input as Record<string, RuleInputValue>,
      expected_outcome: raw.expected_outcome,
    };
  });
  if (new Set(cases.map(({ case_id: id }) => id)).size !== cases.length ||
      new Set(cases.map(({ input }) => canonicalRuleJson(input))).size !== cases.length) {
    return fail("RULE_CASE_DUPLICATE");
  }
  if (computeRuleDocumentDigest(value, "catalogue_sha256") !== value.catalogue_sha256) {
    return fail("RULE_CASE_CATALOGUE_DIGEST_STALE");
  }
  const catalogue = value as RuleCaseCatalogueV1;
  return createValidatedHandle({
    value: catalogue,
    source_sha256: sha256(bytes),
    validated_refs: [{ id: definition.rule_id, sha256: definition.definition_sha256 }],
  });
};

export const normalizeRulePackageV1 = (
  definitionHandle: ValidatedHandle<RuleDefinitionV1>,
  bindingHandle: ValidatedHandle<RuleBindingV1>,
  casesHandle: ValidatedHandle<RuleCaseCatalogueV1>,
): ValidatedHandle<NormalizedRulePackageV1> => {
  const definition = readValidatedHandle(definitionHandle);
  const binding = readValidatedHandle(bindingHandle);
  const cases = readValidatedHandle(casesHandle);
  const normalized: NormalizedRulePackageV1 = {
    schema_version: "NormalizedRulePackage/v1",
    definition: {
      ...definition,
      input_fields: [...definition.input_fields].sort((left, right) =>
        compareUtf8(left.name, right.name)),
    },
    binding,
    cases: {
      ...cases,
      cases: [...cases.cases].sort((left, right) =>
        compareUtf8(left.case_id, right.case_id)),
    },
    authority_effect: "none",
  };
  return createValidatedHandle({
    value: normalized,
    source_sha256: sha256(canonicalRuleJson(normalized)),
    validated_refs: [
      { id: definition.rule_id, sha256: definition.definition_sha256 },
      { id: binding.binding_id, sha256: binding.binding_sha256 },
      { id: "rule-cases", sha256: cases.catalogue_sha256 },
    ],
  });
};
