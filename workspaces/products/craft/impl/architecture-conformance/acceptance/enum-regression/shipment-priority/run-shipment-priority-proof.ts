import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { ArchitectureObligationCatalogueV2 } from "../../../realization/contracts/architecture-obligation-catalogue-v2.js";
import {
  computeEnumDefinitionSha256,
  type EnumDefinitionSnapshot,
} from "../../../realization/contracts/enum-definition-snapshot.js";
import {
  computeTypeScriptTargetBindingSha256,
  type TypeScriptTargetBinding,
} from "../../../realization/contracts/typescript-target-binding.js";
import { createEnumTypeScriptRegistrationV2 } from "../../../realizations/enum/typescript/owned-const-object-v1/registration.js";

const here = dirname(fileURLToPath(import.meta.url));
export const repositoryRoot = resolve(here, "../../../../../../..");
const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

export const shipmentPriorityRawPaths = Object.freeze({
  case: "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-regression/shipment-priority/case.json",
  expected: "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-regression/shipment-priority/expected-evidence.json",
  ontology: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json",
  base_profile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json",
  typescript_profile: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
  provider: "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
});

export type ShipmentPriorityRawInputs = Readonly<Record<keyof typeof shipmentPriorityRawPaths, string>>;

type AcceptanceCase = Readonly<{
  case_id: string;
  definition: Readonly<{
    definition_id: string;
    definition_version: string;
    concept_id: string;
    members: readonly Readonly<{ member_id: string; semantic_value: string }>[];
  }>;
  binding: Readonly<{
    module_path: string;
    export_name: string;
    type_name: string;
    member_names: Readonly<Record<string, string>>;
  }>;
  mutation_member_id: string;
  claim_ceiling: string;
}>;

type ExpectedEvidence = Readonly<{
  expected_values: readonly string[];
  expected_module_path: string;
  expected_positive_verdict: "pass";
  expected_mutation: Readonly<{ member_id: string; finding_code: string; finding_count: number }>;
}>;

export const loadShipmentPriorityRawInputs = async (
  root = repositoryRoot,
): Promise<ShipmentPriorityRawInputs> => Object.fromEntries(await Promise.all(
  Object.entries(shipmentPriorityRawPaths).map(async ([name, path]) =>
    [name, await readFile(resolve(root, path), "utf8")] as const),
)) as ShipmentPriorityRawInputs;

export const buildShipmentPriorityProof = async (input?: ShipmentPriorityRawInputs) => {
  const raw = input ?? await loadShipmentPriorityRawInputs();
  const caseValue = JSON.parse(raw.case) as AcceptanceCase;
  const expected = JSON.parse(raw.expected) as ExpectedEvidence;
  const registration = await createEnumTypeScriptRegistrationV2(repositoryRoot);
  const { family, target, realization, projector, definition_or_binding: definitions,
    obligations } = registration.providers;
  const spec = projector.derive({
    spec_id: "shipment-priority.typescript.direct/v1",
    ontology_json: raw.ontology,
    base_profile_json: raw.base_profile,
    typescript_profile_json: raw.typescript_profile,
    expected_source_digests: {
      ontology_sha256: sha256(raw.ontology),
      base_profile_sha256: sha256(raw.base_profile),
      typescript_profile_sha256: sha256(raw.typescript_profile),
    },
  });
  const definitionBody = {
    schema_version: "EnumDefinitionSnapshot/v1" as const,
    ...caseValue.definition,
    composition_kind: "direct" as const,
    order_semantics: "none" as const,
    authority_ref: "candidate://shipment-priority@1",
    authority_status: "candidate-fixture" as const,
    authority_effect: "none" as const,
  };
  const definition = definitions.definition({
    ...definitionBody,
    definition_sha256: computeEnumDefinitionSha256(definitionBody),
  }) as EnumDefinitionSnapshot;
  const bindingBody = {
    schema_version: "TypeScriptTargetBinding/v1" as const,
    binding_id: "shipment-priority.typescript/v1",
    definition_ref: {
      definition_id: definition.definition_id,
      definition_version: definition.definition_version,
      definition_sha256: definition.definition_sha256,
    },
    language: "typescript" as const,
    ...caseValue.binding,
    provider_module_specifier: "../runtime/enum/index.js",
    protocol_ref: "typescript.owned-const-object-enum/v1" as const,
    profile_ref: {
      path: shipmentPriorityRawPaths.typescript_profile,
      sha256: sha256(raw.typescript_profile),
    },
    provider_ref: {
      path: shipmentPriorityRawPaths.provider,
      sha256: sha256(raw.provider),
    },
    emitter_version: "1.0.0",
    emitter_config_digest: "592290a173e728bbcbfbdae5ca014ab6034026118d574d99d31458a155de1346",
    format_version: "typescript-printer/v1" as const,
    authority_effect: "none" as const,
  };
  const binding = definitions.binding({
    ...bindingBody,
    binding_sha256: computeTypeScriptTargetBindingSha256(bindingBody),
  }, definition) as TypeScriptTargetBinding;
  const predecessorBytes = JSON.stringify({
    schema_version: "ArchitectureObligationCatalogue/v1",
    catalogue_id: "shipment-priority.member-bijection",
    catalogue_version: "1",
    expected_members: definition.members,
    authority_effect: "none",
  });
  const catalogueBody = {
    schema_version: "ArchitectureObligationCatalogue/v2" as const,
    catalogue_id: "shipment-priority.member-bijection",
    catalogue_version: "2" as const,
    supersedes_ref: {
      catalogue_id: "shipment-priority.member-bijection",
      catalogue_version: "1" as const,
      path: "fixture://shipment-priority/catalogue.v1.json",
      sha256: sha256(predecessorBytes),
    },
    definition_ref: {
      definition_id: definition.definition_id,
      definition_version: definition.definition_version,
      definition_sha256: definition.definition_sha256,
      authority_status: definition.authority_status,
      path: "fixture://shipment-priority/definition.snapshot.json",
      sha256: sha256(JSON.stringify(definition)),
    },
    ontology_ref: { ...spec.ontology_ref, path: shipmentPriorityRawPaths.ontology },
    profile_ref: {
      ...spec.profile_ref,
      path: shipmentPriorityRawPaths.typescript_profile,
      extends: spec.profile_ref.extends.map((profile) => ({
        ...profile,
        path: shipmentPriorityRawPaths.base_profile,
      })),
    },
    obligations: [{
      obligation_key: "enum.member-bijection@1" as const,
      contract_version: "1" as const,
      subject_ref: `${definition.concept_id}@1`,
      operator: "member-bijection" as const,
      expected_payload: {
        concept_id: definition.concept_id,
        composition_kind: "direct" as const,
        order_semantics: "none" as const,
        members: definition.members,
      },
      failure_codes: [
        "ARCH_ENUM_BINDING_AMBIGUOUS",
        "ARCH_ENUM_MEMBER_DUPLICATE",
        "ARCH_ENUM_MEMBER_MISSING",
        "ARCH_ENUM_MEMBER_UNEXPECTED",
        "ARCH_ENUM_OBSERVATION_UNSUPPORTED",
        "ARCH_ENUM_VALUE_MISMATCH",
        "ARCH_REALIZATION_HANDLE_STALE",
      ],
    }],
    owner_ref: "architecture-obligation-catalogue-owner" as const,
    authority_effect: "none" as const,
  };
  const catalogue = {
    ...catalogueBody,
    catalogue_sha256: obligations.canonicalDigest({
      ...catalogueBody,
      catalogue_sha256: "",
    }),
  } as ArchitectureObligationCatalogueV2;
  const ir = family.normalize(definition, spec);
  const generated = realization.emit(ir, binding);
  const compileExpectation = await target.compileExpectation();
  const compilePositive = await target.compile({
    repositoryRoot,
    generated,
    binding,
    expectedTypeValues: definition.members.map(({ semantic_value: value }) => value),
  });
  const observationPositive = realization.observe({
    source: generated.source,
    manifest: generated.manifest,
    providerSource: raw.provider,
    admittedProviderSha256: binding.provider_ref.sha256,
  });
  const evaluationPositive = family.evaluate({
    definition,
    catalogue,
    binding,
    sourceManifest: generated.manifest,
    compileExpectation,
    compileResult: compilePositive,
    observation: observationPositive,
  });
  const mutation = realization.mutate(generated, binding, caseValue.mutation_member_id);
  const compileMutation = await target.compile({ repositoryRoot, generated: mutation.child, binding });
  const observationMutation = realization.observe({
    source: mutation.child.source,
    manifest: mutation.child.manifest,
    providerSource: raw.provider,
    admittedProviderSha256: binding.provider_ref.sha256,
  });
  const evaluationMutation = family.evaluate({
    definition,
    catalogue,
    binding,
    sourceManifest: mutation.child.manifest,
    compileExpectation,
    compileResult: compileMutation,
    observation: observationMutation,
  });
  const exactMutation = evaluationMutation.findings.length === expected.expected_mutation.finding_count &&
    evaluationMutation.findings[0]?.code === expected.expected_mutation.finding_code &&
    evaluationMutation.findings[0]?.member_id === expected.expected_mutation.member_id;
  if (generated.manifest.module_path !== expected.expected_module_path ||
      JSON.stringify(compilePositive.runtime_values) !== JSON.stringify(expected.expected_values) ||
      evaluationPositive.verdict !== expected.expected_positive_verdict || !exactMutation ||
      mutation.mutation.delta.member_id !== expected.expected_mutation.member_id) {
    throw Object.assign(new Error("SHIPMENT_PRIORITY_PROOF_BLOCKED"), {
      code: "SHIPMENT_PRIORITY_PROOF_BLOCKED",
    });
  }
  return Object.freeze({
    schema_version: "ShipmentPriorityProof/v1" as const,
    result: "pass" as const,
    case_id: caseValue.case_id,
    module_path: generated.manifest.module_path,
    values: Object.freeze([...compilePositive.runtime_values]),
    positive_verdict: evaluationPositive.verdict,
    mutation: Object.freeze({
      member_id: expected.expected_mutation.member_id,
      finding_code: expected.expected_mutation.finding_code,
      status: "killed" as const,
    }),
    source_sha256: generated.manifest.source_sha256,
    claim_ceiling: caseValue.claim_ceiling,
    authority_effect: "none" as const,
  });
};
