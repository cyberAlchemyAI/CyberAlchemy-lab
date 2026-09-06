import { createHash } from "node:crypto";

import type {
  ArchitectureEvaluation,
  ArchitectureFinding,
  EvaluateEnumBijectionInput,
} from "../contracts/architecture-evaluation.js";
import { computeArchitectureObligationCatalogueV2Sha256 } from
  "../contracts/architecture-obligation-catalogue-v2.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const finding = (
  code: ArchitectureFinding["code"],
  details: Partial<Omit<ArchitectureFinding, "code">> = {},
): ArchitectureFinding => Object.freeze({
  code,
  member_id: details.member_id ?? null,
  target_identifier: details.target_identifier ?? null,
  expected_value: details.expected_value ?? null,
  observed_value: details.observed_value ?? null,
});

export const evaluateEnumBijection = (
  input: EvaluateEnumBijectionInput,
): ArchitectureEvaluation => {
  const {
    definition,
    catalogue,
    binding,
    sourceManifest,
    compileExpectation,
    compileResult,
    observation,
  } = input;
  const obligation = catalogue.obligations[0];
  const findings: ArchitectureFinding[] = [];
  if (computeArchitectureObligationCatalogueV2Sha256(catalogue)
      !== catalogue.catalogue_sha256) {
    findings.push(finding("ARCH_ENUM_CATALOGUE_DIGEST_STALE"));
  }
  const definitionMembers = definition.members
    .map(({ member_id: memberId, semantic_value: semanticValue }) =>
      `${memberId}\u0000${semanticValue}`)
    .sort(compareUtf8);
  const catalogueMembers = (obligation?.expected_payload.members ?? [])
    .map(({ member_id: memberId, semantic_value: semanticValue }) =>
      `${memberId}\u0000${semanticValue}`)
    .sort(compareUtf8);
  const catalogueDefinitionMismatch = catalogue.definition_ref.definition_id
      !== definition.definition_id
    || catalogue.definition_ref.definition_version !== definition.definition_version
    || catalogue.definition_ref.definition_sha256 !== definition.definition_sha256
    || obligation?.expected_payload.concept_id !== definition.concept_id
    || definitionMembers.length !== catalogueMembers.length
    || definitionMembers.some((member, index) => member !== catalogueMembers[index]);
  if (catalogueDefinitionMismatch) {
    findings.push(finding("ARCH_ENUM_CATALOGUE_DEFINITION_MISMATCH"));
  }
  const definitionMemberIds = definition.members
    .map(({ member_id: memberId }) => memberId)
    .sort(compareUtf8);
  const bindingMemberIds = Object.keys(binding.member_names).sort(compareUtf8);
  const catalogueBindingMismatch = binding.definition_ref.definition_id
      !== definition.definition_id
    || binding.definition_ref.definition_version !== definition.definition_version
    || binding.definition_ref.definition_sha256 !== definition.definition_sha256
    || definitionMemberIds.length !== bindingMemberIds.length
    || definitionMemberIds.some((memberId, index) => memberId !== bindingMemberIds[index]);
  if (catalogueBindingMismatch) {
    findings.push(finding("ARCH_ENUM_CATALOGUE_BINDING_MISMATCH"));
  }
  if (compileResult.schema_version !== "CompileResult/v1"
      || compileResult.exit_status !== 0
      || compileResult.diagnostics.length !== 0
      || compileResult.authority_effect !== "none"
      || compileResult.workspace.isolated !== true
      || compileResult.workspace.symlinks !== false
      || compileResult.workspace.cleaned !== true) {
    findings.push(finding("ARCH_ENUM_COMPILE_EXECUTION_INVALID"));
  }
  if (compileResult.compiler.name !== compileExpectation.compiler.name
      || compileResult.compiler.version !== compileExpectation.compiler.version
      || compileResult.compiler.tool_sha256 !== compileExpectation.compiler.tool_sha256
      || compileResult.compiler.config_sha256 !== compileExpectation.compiler.config_sha256) {
    findings.push(finding("ARCH_ENUM_COMPILE_TOOL_INVALID"));
  }
  const expectedDefinitionValues = definition.members
    .map(({ semantic_value: semanticValue }) => semanticValue)
    .sort(compareUtf8);
  const witnessValues = [...compileResult.type_witness.expected_union].sort(compareUtf8);
  const definitionExactWitness = compileResult.type_witness.mode === "definition-exact"
    && compileResult.type_witness.passed === true
    && typeof compileResult.type_witness.source_sha256 === "string"
    && /^[a-f0-9]{64}$/u.test(compileResult.type_witness.source_sha256)
    && witnessValues.length === expectedDefinitionValues.length
    && witnessValues.every((value, index) => value === expectedDefinitionValues[index]);
  const compileOnlyWitness = compileResult.type_witness.mode === "compile-only"
    && compileResult.type_witness.passed === true
    && compileResult.type_witness.source_sha256 === null
    && witnessValues.length === 0;
  if (!definitionExactWitness && !compileOnlyWitness) {
    findings.push(finding("ARCH_ENUM_COMPILE_TYPE_WITNESS_INVALID"));
  }
  const observedRuntimeValues = observation.facts
    .map(({ runtime_value: runtimeValue }) => runtimeValue)
    .sort(compareUtf8);
  const compiledRuntimeValues = [...compileResult.runtime_values].sort(compareUtf8);
  if (compiledRuntimeValues.length !== observedRuntimeValues.length
      || compiledRuntimeValues.some((value, index) => value !== observedRuntimeValues[index])) {
    findings.push(finding("ARCH_ENUM_COMPILE_RUNTIME_VALUES_INVALID"));
  }
  if (compileResult.runtime_frozen !== true) {
    findings.push(finding("ARCH_ENUM_COMPILE_RUNTIME_FREEZE_INVALID"));
  }
  const stale = catalogue.schema_version !== "ArchitectureObligationCatalogue/v2"
    || catalogue.authority_effect !== "none"
    || catalogue.obligations.length !== 1
    || obligation?.obligation_key !== "enum.member-bijection@1"
    || binding.authority_effect !== "none"
    || binding.definition_ref.definition_id !== catalogue.definition_ref.definition_id
    || binding.definition_ref.definition_version !== catalogue.definition_ref.definition_version
    || binding.definition_ref.definition_sha256 !== catalogue.definition_ref.definition_sha256
    || sourceManifest.source_sha256 !== compileResult.source_sha256
    || sourceManifest.source_sha256 !== observation.source_manifest_ref.source_sha256
    || sourceManifest.module_path !== observation.source_manifest_ref.module_path
    || binding.provider_ref.sha256 !== compileResult.provider_sha256
    || binding.provider_ref.sha256 !== observation.protocol_ref.provider_sha256
    || binding.protocol_ref !== observation.protocol_ref.protocol_id
    || observation.authority_effect !== "none"
    || observation.facts.some(({ semantic_member_id: semanticMemberId }) => semanticMemberId !== null);
  if (stale) findings.push(finding("ARCH_REALIZATION_HANDLE_STALE"));
  if (observation.unsupported.length > 0 || observation.diagnostics.length > 0) {
    findings.push(finding("ARCH_ENUM_OBSERVATION_UNSUPPORTED"));
  }

  const catalogueTrustBlocked = findings.some(({ code }) =>
    code === "ARCH_ENUM_CATALOGUE_DIGEST_STALE"
    || code === "ARCH_ENUM_CATALOGUE_DEFINITION_MISMATCH"
    || code === "ARCH_ENUM_CATALOGUE_BINDING_MISMATCH");
  if (!catalogueTrustBlocked) {
  const targetEntries = Object.entries(binding.member_names);
  const targetIdentifiers = targetEntries.map(([, identifier]) => identifier);
  if (new Set(targetIdentifiers).size !== targetIdentifiers.length) {
    findings.push(finding("ARCH_ENUM_BINDING_AMBIGUOUS"));
  }
  const semanticByTarget = new Map(targetEntries.map(([memberId, identifier]) =>
    [identifier, memberId] as const));
  const targetCounts = new Map<string, number>();
  const valueCounts = new Map<string, number>();
  for (const fact of observation.facts) {
    targetCounts.set(fact.target_identifier, (targetCounts.get(fact.target_identifier) ?? 0) + 1);
    valueCounts.set(fact.runtime_value, (valueCounts.get(fact.runtime_value) ?? 0) + 1);
  }
  for (const [targetIdentifier, count] of targetCounts) {
    if (count > 1) findings.push(finding("ARCH_ENUM_MEMBER_DUPLICATE", {
      member_id: semanticByTarget.get(targetIdentifier) ?? null,
      target_identifier: targetIdentifier,
    }));
  }
  for (const [runtimeValue, count] of valueCounts) {
    if (count > 1) findings.push(finding("ARCH_ENUM_MEMBER_DUPLICATE", {
      observed_value: runtimeValue,
    }));
  }
  for (const fact of observation.facts) {
    if (!semanticByTarget.has(fact.target_identifier)) {
      findings.push(finding("ARCH_ENUM_MEMBER_UNEXPECTED", {
        target_identifier: fact.target_identifier,
        observed_value: fact.runtime_value,
      }));
    }
  }
  if (obligation) {
    for (const expected of obligation.expected_payload.members) {
      const targetIdentifier = binding.member_names[expected.member_id];
      if (!targetIdentifier) {
        findings.push(finding("ARCH_ENUM_BINDING_AMBIGUOUS", {
          member_id: expected.member_id,
          expected_value: expected.semantic_value,
        }));
        continue;
      }
      const matched = observation.facts.filter((fact) => fact.target_identifier === targetIdentifier);
      if (matched.length === 0) {
        findings.push(finding("ARCH_ENUM_MEMBER_MISSING", {
          member_id: expected.member_id,
          target_identifier: targetIdentifier,
          expected_value: expected.semantic_value,
        }));
      } else if (matched.length === 1 && matched[0]?.runtime_value !== expected.semantic_value) {
        findings.push(finding("ARCH_ENUM_VALUE_MISMATCH", {
          member_id: expected.member_id,
          target_identifier: targetIdentifier,
          expected_value: expected.semantic_value,
          observed_value: matched[0]?.runtime_value ?? null,
        }));
      }
    }
  }
  }
  const normalizedFindings = [...findings].sort((left, right) => compareUtf8(
    `${left.code}:${left.member_id ?? ""}:${left.target_identifier ?? ""}:${left.observed_value ?? ""}`,
    `${right.code}:${right.member_id ?? ""}:${right.target_identifier ?? ""}:${right.observed_value ?? ""}`,
  ));
  const verdict = normalizedFindings.length === 0 ? "pass" as const : "fail" as const;
  const inputRefs = Object.freeze({
    catalogue_sha256: catalogue.catalogue_sha256,
    binding_sha256: binding.binding_sha256,
    source_sha256: sourceManifest.source_sha256,
    compile_config_sha256: compileResult.compiler.config_sha256,
    observation_sha256: observation.observation_sha256,
  });
  return Object.freeze({
    schema_version: "ArchitectureEvaluation/v1" as const,
    evaluation_id: `evaluation.enum.${sha256(JSON.stringify({ inputRefs, normalizedFindings }))}`,
    obligation_key: "enum.member-bijection@1" as const,
    input_refs: inputRefs,
    verdict,
    findings: Object.freeze(normalizedFindings),
    obligation_accounting: Object.freeze({
      declared: 1 as const,
      passed: (verdict === "pass" ? 1 : 0) as 0 | 1,
      failed: (verdict === "fail" ? 1 : 0) as 0 | 1,
      unaccounted: 0 as const,
    }),
    authority_effect: "none" as const,
  });
};
