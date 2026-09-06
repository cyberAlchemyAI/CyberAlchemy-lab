import { createHash } from "node:crypto";

import {
  createValidatedHandle,
  readValidatedHandle,
  type ValidatedHandle,
} from "../../../kernel/contracts/validated-handle.js";
import type {
  RuleMutationCatalogueV1,
  RuleObligationCatalogueV1,
} from "../contracts/rule-contracts.js";
import {
  computeRuleDocumentDigest,
  type NormalizedRulePackageV1,
} from "./decode-rule-contracts.js";

type JsonObject = Record<string, unknown>;
const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};
const isRecord = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const exactKeys = (value: JsonObject, expected: readonly string[]): boolean => {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
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
const SHA256 = /^[a-f0-9]{64}$/u;

export const decodeRuleObligationCatalogueV1 = (
  bytes: string,
  packageHandle: ValidatedHandle<NormalizedRulePackageV1>,
): ValidatedHandle<RuleObligationCatalogueV1> => {
  const rule = readValidatedHandle(packageHandle);
  const value = parse(bytes, "RULE_OBLIGATION_CATALOGUE_SCHEMA_INVALID");
  if (!exactKeys(value, [
    "schema_version", "rule_ref", "case_catalogue_sha256", "obligations",
    "catalogue_sha256", "owner_ref", "authority_effect",
  ]) || value.schema_version !== "RuleObligationCatalogue/v1" ||
      !isRecord(value.rule_ref) ||
      !exactKeys(value.rule_ref, ["rule_id", "definition_sha256"]) ||
      !Array.isArray(value.obligations) || value.obligations.length === 0 ||
      typeof value.case_catalogue_sha256 !== "string" ||
      !SHA256.test(value.case_catalogue_sha256) ||
      typeof value.catalogue_sha256 !== "string" ||
      !SHA256.test(value.catalogue_sha256) ||
      value.owner_ref !== "rule-obligation-owner" || value.authority_effect !== "none") {
    return fail("RULE_OBLIGATION_CATALOGUE_SCHEMA_INVALID");
  }
  if (value.rule_ref.rule_id !== rule.definition.rule_id ||
      value.rule_ref.definition_sha256 !== rule.definition.definition_sha256 ||
      value.case_catalogue_sha256 !== rule.cases.catalogue_sha256) {
    return fail("RULE_OBLIGATION_CATALOGUE_REF_STALE");
  }
  const caseIds = new Set(rule.cases.cases.map(({ case_id: id }) => id));
  const obligationIds = new Set<string>();
  const binding: string[] = [];
  const outcomes = new Map<string, number>();
  const effects = new Map<string, number>();
  for (const raw of value.obligations) {
    if (!isRecord(raw) || !exactKeys(raw, [
      "obligation_id", "kind", "case_id", "expected_outcome", "failure_code",
    ]) || typeof raw.obligation_id !== "string" || raw.obligation_id.length === 0) {
      return fail("RULE_OBLIGATION_SCHEMA_INVALID");
    }
    if (obligationIds.has(raw.obligation_id)) {
      return fail("RULE_OBLIGATION_DUPLICATE");
    }
    obligationIds.add(raw.obligation_id);
    if (raw.kind === "binding-current") {
      if (raw.case_id !== null || raw.expected_outcome !== null ||
          raw.failure_code !== "RULE_BINDING_MISSING") {
        return fail("RULE_OBLIGATION_SCHEMA_INVALID");
      }
      binding.push(raw.obligation_id);
      continue;
    }
    if (typeof raw.case_id !== "string" || !caseIds.has(raw.case_id)) {
      return fail("RULE_OBLIGATION_CASE_UNKNOWN");
    }
    if (raw.kind === "case-outcome-exact") {
      if (typeof raw.expected_outcome !== "boolean" ||
          raw.failure_code !== "RULE_OUTCOME_MISMATCH") {
        return fail("RULE_OBLIGATION_SCHEMA_INVALID");
      }
      outcomes.set(raw.case_id, (outcomes.get(raw.case_id) ?? 0) + 1);
    } else if (raw.kind === "effect-free") {
      if (raw.expected_outcome !== null || raw.failure_code !== "RULE_EFFECT_OBSERVED") {
        return fail("RULE_OBLIGATION_SCHEMA_INVALID");
      }
      effects.set(raw.case_id, (effects.get(raw.case_id) ?? 0) + 1);
    } else {
      return fail("RULE_OBLIGATION_SCHEMA_INVALID");
    }
  }
  if (binding.length !== 1 || [...caseIds].some((id) =>
    outcomes.get(id) !== 1 || effects.get(id) !== 1)) {
    return fail("RULE_OBLIGATION_COVERAGE_INCOMPLETE");
  }
  if (computeRuleDocumentDigest(value, "catalogue_sha256") !==
      value.catalogue_sha256) {
    return fail("RULE_OBLIGATION_CATALOGUE_DIGEST_STALE");
  }
  return createValidatedHandle({
    value: value as RuleObligationCatalogueV1,
    source_sha256: sha256(bytes),
    validated_refs: [
      { id: rule.definition.rule_id, sha256: rule.definition.definition_sha256 },
      { id: "rule-cases", sha256: rule.cases.catalogue_sha256 },
    ],
  });
};

export const decodeRuleMutationCatalogueV1 = (
  bytes: string,
  packageHandle: ValidatedHandle<NormalizedRulePackageV1>,
): ValidatedHandle<RuleMutationCatalogueV1> => {
  const rule = readValidatedHandle(packageHandle);
  const value = parse(bytes, "RULE_MUTATION_CATALOGUE_SCHEMA_INVALID");
  if (!exactKeys(value, [
    "schema_version", "rule_ref", "mutations", "catalogue_sha256", "owner_ref",
    "authority_effect",
  ]) || value.schema_version !== "RuleMutationCatalogue/v1" ||
      !isRecord(value.rule_ref) ||
      !exactKeys(value.rule_ref, ["rule_id", "definition_sha256"]) ||
      !Array.isArray(value.mutations) || value.mutations.length === 0 ||
      typeof value.catalogue_sha256 !== "string" ||
      !SHA256.test(value.catalogue_sha256) ||
      value.owner_ref !== "rule-mutation-owner" || value.authority_effect !== "none") {
    return fail("RULE_MUTATION_CATALOGUE_SCHEMA_INVALID");
  }
  if (value.rule_ref.rule_id !== rule.definition.rule_id ||
      value.rule_ref.definition_sha256 !== rule.definition.definition_sha256) {
    return fail("RULE_MUTATION_CATALOGUE_REF_STALE");
  }
  const caseIds = new Set(rule.cases.cases.map(({ case_id: id }) => id));
  const mutationIds = new Set<string>();
  const defects = new Set<string>();
  for (const raw of value.mutations) {
    if (!isRecord(raw) || !exactKeys(raw, [
      "mutation_id", "defect", "case_id", "expected_finding_code",
    ]) || typeof raw.mutation_id !== "string" || raw.mutation_id.length === 0 ||
        typeof raw.case_id !== "string" || !caseIds.has(raw.case_id) ||
        !["wrong-result", "bypass-check", "observable-effect"].includes(
          raw.defect as string,
        )) {
      return fail("RULE_MUTATION_SCHEMA_INVALID");
    }
    const expectedCode = raw.defect === "observable-effect"
      ? "RULE_EFFECT_OBSERVED"
      : "RULE_OUTCOME_MISMATCH";
    if (raw.expected_finding_code !== expectedCode) {
      return fail("RULE_MUTATION_EXPECTATION_INVALID");
    }
    if (mutationIds.has(raw.mutation_id) || defects.has(raw.defect as string)) {
      return fail("RULE_MUTATION_DUPLICATE");
    }
    mutationIds.add(raw.mutation_id);
    defects.add(raw.defect as string);
  }
  if (!["wrong-result", "bypass-check", "observable-effect"].every((defect) =>
    defects.has(defect))) {
    return fail("RULE_MUTATION_COVERAGE_INCOMPLETE");
  }
  if (computeRuleDocumentDigest(value, "catalogue_sha256") !==
      value.catalogue_sha256) {
    return fail("RULE_MUTATION_CATALOGUE_DIGEST_STALE");
  }
  return createValidatedHandle({
    value: value as RuleMutationCatalogueV1,
    source_sha256: sha256(bytes),
    validated_refs: [{
      id: rule.definition.rule_id,
      sha256: rule.definition.definition_sha256,
    }],
  });
};
