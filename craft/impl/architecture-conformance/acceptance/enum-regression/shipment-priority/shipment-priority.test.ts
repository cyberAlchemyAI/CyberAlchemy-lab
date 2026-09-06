import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

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
const repositoryRoot = resolve(here, "../../../../../../..");
const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

type AcceptanceCase = Readonly<{
  schema_version: "EnumAcceptanceCase/v1";
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
  authority_effect: "none";
}>;

type ExpectedEvidence = Readonly<{
  expected_values: readonly string[];
  expected_module_path: string;
  expected_positive_verdict: "pass";
  expected_mutation: Readonly<{
    member_id: string;
    finding_code: "ARCH_ENUM_MEMBER_MISSING";
    finding_count: 1;
  }>;
  factory_implementation_changes_allowed: 0;
}>;

describe("second Enum case factory reuse", () => {
  it("proves ShipmentPriority and kills its distinct mutant through unchanged providers", async () => {
    const [caseValue, expected, ontologyJson, baseProfileJson, typescriptProfileJson,
      providerSource] = await Promise.all([
      readFile(resolve(here, "case.json"), "utf8")
        .then((value) => JSON.parse(value) as AcceptanceCase),
      readFile(resolve(here, "expected-evidence.json"), "utf8")
        .then((value) => JSON.parse(value) as ExpectedEvidence),
      readFile(resolve(repositoryRoot,
        "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json"), "utf8"),
      readFile(resolve(repositoryRoot,
        "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json"), "utf8"),
      readFile(resolve(repositoryRoot,
        "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json"), "utf8"),
      readFile(resolve(repositoryRoot,
        "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts"), "utf8"),
    ]);
    const registration = await createEnumTypeScriptRegistrationV2(repositoryRoot);
    const { family, target, realization, projector, definition_or_binding: definitions,
      obligations } = registration.providers;
    const spec = projector.derive({
      spec_id: "shipment-priority.typescript.direct/v1",
      ontology_json: ontologyJson,
      base_profile_json: baseProfileJson,
      typescript_profile_json: typescriptProfileJson,
      expected_source_digests: {
        ontology_sha256: sha256(ontologyJson),
        base_profile_sha256: sha256(baseProfileJson),
        typescript_profile_sha256: sha256(typescriptProfileJson),
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
        path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
        sha256: sha256(typescriptProfileJson),
      },
      provider_ref: {
        path: "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/enum/index.ts",
        sha256: sha256(providerSource),
      },
      emitter_version: "1.0.0",
      emitter_config_digest:
        "592290a173e728bbcbfbdae5ca014ab6034026118d574d99d31458a155de1346",
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
      ontology_ref: {
        ...spec.ontology_ref,
        path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json",
      },
      profile_ref: {
        ...spec.profile_ref,
        path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
        extends: spec.profile_ref.extends.map((profile) => ({
          ...profile,
          path: "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json",
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
      providerSource,
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
    const mutation = realization.mutate(
      generated,
      binding,
      caseValue.mutation_member_id,
    );
    const compileMutation = await target.compile({
      repositoryRoot,
      generated: mutation.child,
      binding,
    });
    const observationMutation = realization.observe({
      source: mutation.child.source,
      manifest: mutation.child.manifest,
      providerSource,
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

    expect(generated.manifest.module_path).toBe(expected.expected_module_path);
    expect(compilePositive.runtime_values).toEqual(expected.expected_values);
    expect(evaluationPositive.verdict).toBe(expected.expected_positive_verdict);
    expect(evaluationMutation.findings).toEqual([
      expect.objectContaining({
        code: expected.expected_mutation.finding_code,
        member_id: expected.expected_mutation.member_id,
      }),
    ]);
    expect(mutation.mutation.delta.member_id).toBe(
      expected.expected_mutation.member_id,
    );
    expect(generated.source).toContain("ShipmentPriority");
    expect([
      definition.definition_sha256,
      binding.binding_sha256,
      catalogue.catalogue_sha256,
      generated.manifest.source_sha256,
      evaluationPositive.evaluation_id.split(".").at(-1),
    ]).toEqual(expect.arrayContaining([
      expect.stringMatching(/^[a-f0-9]{64}$/u),
    ]));
  }, 30_000);
});
