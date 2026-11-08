import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import { finiteVocabularyFamilyProvider } from "../../../../families/finite-vocabulary/index.js";
import { admitMetaTypeDescriptorV2 } from "../../../../kernel/codecs/decode-meta-type-descriptor-v2.js";
import type { ExactRef } from "../../../../kernel/contracts/exact-ref.js";
import type {
  MetaTypeAdmissionV2,
  MetaTypeDescriptorV2,
} from "../../../../kernel/contracts/meta-type-descriptor-v2.js";
import type { ValidatedHandle } from "../../../../kernel/contracts/validated-handle.js";
import {
  createRealizationRegistryV2,
  registerRealizationV2,
  resolveRealizationV2,
  type ProviderImplementationsV2,
  type RealizationRegistryV2,
} from "../../../../kernel/registry/realization-registry-v2.js";
import {
  computeArchitectureObligationCatalogueV2Sha256,
} from "../../../../realization/contracts/architecture-obligation-catalogue-v2.js";
import { validateEnumDefinitionSnapshot } from "../../../../realization/contracts/enum-definition-snapshot.js";
import { validateTypeScriptTargetBinding } from "../../../../realization/contracts/typescript-target-binding.js";
import {
  deriveEnumArchitectureRealizationSpec,
  renderArchitectureRealizationSpec,
} from "../../../../realization/spec/derive-enum-realization-spec.js";
import { typescriptTargetProvider } from "../../../../targets/typescript/index.js";
import { ownedConstObjectRealizationProvider } from "./index.js";

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const bytes = (value: unknown): string => JSON.stringify(value);

const COMPONENT_PATHS = Object.freeze({
  projector:
    "projects/domainspec-v2/impl/architecture-conformance/realization/spec/derive-enum-realization-spec.ts",
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/realization/contracts/enum-definition-snapshot.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realization/contracts/typescript-target-binding.ts",
  obligations:
    "projects/domainspec-v2/impl/architecture-conformance/realization/contracts/architecture-obligation-catalogue-v2.ts",
  evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/realization/evaluator/evaluate-enum-bijection.ts",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/realization/mutation/remove-enum-member.ts",
  family:
    "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/index.ts",
  target:
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/index.ts",
  realization:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/typescript/owned-const-object-v1/index.ts",
  profile:
    "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json",
});

type EnumTypeScriptProviders = ProviderImplementationsV2 & Readonly<{
  projector: Readonly<{
    derive: typeof deriveEnumArchitectureRealizationSpec;
    render: typeof renderArchitectureRealizationSpec;
  }>;
  definition_or_binding: Readonly<{
    definition: typeof validateEnumDefinitionSnapshot;
    binding: typeof validateTypeScriptTargetBinding;
  }>;
  obligations: Readonly<{
    canonicalDigest: typeof computeArchitectureObligationCatalogueV2Sha256;
  }>;
  evaluator: typeof finiteVocabularyFamilyProvider;
  mutations: typeof ownedConstObjectRealizationProvider;
  family: typeof finiteVocabularyFamilyProvider;
  target: typeof typescriptTargetProvider;
  realization: typeof ownedConstObjectRealizationProvider;
}>;

export type EnumTypeScriptRegistrationV2 = Readonly<{
  registry: RealizationRegistryV2;
  descriptor: ValidatedHandle<MetaTypeDescriptorV2>;
  providers: EnumTypeScriptProviders;
  reference_documents: Readonly<Record<string, string>>;
}>;

const digestDocument = <
  T extends Record<string, unknown>,
  K extends string,
>(
  body: T,
  digestField: K,
): T & Record<K, string> => ({
  ...body,
  [digestField]: sha256(bytes(body)),
}) as T & Record<K, string>;

export const createEnumTypeScriptRegistrationV2 = async (
  repositoryRoot: string,
): Promise<EnumTypeScriptRegistrationV2> => {
  const componentDigests = Object.fromEntries(await Promise.all(
    Object.entries(COMPONENT_PATHS).map(async ([name, path]) => [
      name,
      { path, sha256: sha256(await readFile(resolve(repositoryRoot, path))) },
    ] as const),
  ));
  const document = (
    schemaVersion: string,
    id: string,
    components: readonly string[],
  ): string => bytes({
    schema_version: schemaVersion,
    id,
    components: components.map((name) => componentDigests[name]),
    authority_effect: "none",
  });
  const documents = Object.freeze({
    criterion: document("CriterionSchema/v1", "finite-vocabulary", ["family"]),
    profile: document("ArchitectureProfileSelection/v2", "typescript-strict", ["profile"]),
    projector: document("ProjectorProvider/v2", "enum-projector", ["projector"]),
    definition: document("DefinitionBindingProvider/v2", "enum-definition-binding", [
      "definition",
      "binding",
    ]),
    obligations: document("ObligationProvider/v2", "enum-obligations", ["obligations"]),
    evaluator: document("EvaluatorProvider/v2", "finite-vocabulary-evaluator", ["evaluator"]),
    mutations: document("MutationProvider/v2", "enum-member-removal", ["mutations"]),
    family: document("FamilyProvider/v2", "finite-vocabulary", ["family"]),
    target: document("TargetProvider/v2", "typescript", ["target"]),
    realization: document(
      "RealizationProvider/v2",
      "owned-const-object-v1",
      ["realization"],
    ),
  });
  const ref = (
    id: keyof typeof documents,
    schemaVersion: string,
  ): ExactRef => Object.freeze({
    id,
    schema_version: schemaVersion,
    sha256: sha256(documents[id]),
  });
  const refs = {
    criterion: ref("criterion", "CriterionSchema/v1"),
    profile: ref("profile", "ArchitectureProfileSelection/v2"),
    projector: ref("projector", "ProjectorProvider/v2"),
    definition: ref("definition", "DefinitionBindingProvider/v2"),
    obligations: ref("obligations", "ObligationProvider/v2"),
    evaluator: ref("evaluator", "EvaluatorProvider/v2"),
    mutations: ref("mutations", "MutationProvider/v2"),
    family: ref("family", "FamilyProvider/v2"),
    target: ref("target", "TargetProvider/v2"),
    realization: ref("realization", "RealizationProvider/v2"),
  } as const;
  const admission = digestDocument({
    schema_version: "MetaTypeAdmission/v2" as const,
    meta_type_ref: "DS-D1.3" as const,
    maturity: "active" as const,
    mapping_status: "candidate-mapped" as const,
    architecture_type_ref: "architecture.Enum",
    admitted_profile_ref: refs.profile,
    authority_effect: "none" as const,
  }, "admission_sha256") as MetaTypeAdmissionV2;
  const descriptor = digestDocument({
    schema_version: "MetaTypeDescriptor/v2" as const,
    descriptor_id: "finite-vocabulary.typescript.owned-const-object-v1",
    meta_type_ref: "DS-D1.3" as const,
    maturity: "active" as const,
    criterion_schema_ref: refs.criterion,
    architecture_type_ref: "architecture.Enum",
    admitted_profile_ref: refs.profile,
    modes: ["generate-and-observe" as const],
    supported_relation_refs: [],
    provider_refs: {
      projector: refs.projector,
      definition_or_binding: refs.definition,
      obligations: refs.obligations,
      evaluator: refs.evaluator,
      mutations: refs.mutations,
    },
    family_ref: refs.family,
    target_ref: refs.target,
    realization_ref: refs.realization,
    claim_ceiling: "one candidate-local direct TypeScript Enum proof",
    authority_effect: "none" as const,
  }, "descriptor_sha256") as MetaTypeDescriptorV2;
  const handle = await admitMetaTypeDescriptorV2(
    bytes(descriptor),
    bytes(admission),
    (exactRef) => documents[exactRef.id as keyof typeof documents] ?? "",
  );
  const providers: EnumTypeScriptProviders = Object.freeze({
    projector: Object.freeze({
      derive: deriveEnumArchitectureRealizationSpec,
      render: renderArchitectureRealizationSpec,
    }),
    definition_or_binding: Object.freeze({
      definition: validateEnumDefinitionSnapshot,
      binding: validateTypeScriptTargetBinding,
    }),
    obligations: Object.freeze({
      canonicalDigest: computeArchitectureObligationCatalogueV2Sha256,
    }),
    evaluator: finiteVocabularyFamilyProvider,
    mutations: ownedConstObjectRealizationProvider,
    family: finiteVocabularyFamilyProvider,
    target: typescriptTargetProvider,
    realization: ownedConstObjectRealizationProvider,
  });
  let registry = createRealizationRegistryV2();
  registry = registerRealizationV2(registry, { descriptor: handle, providers });
  const selected = resolveRealizationV2<EnumTypeScriptProviders>(
    registry,
    descriptor.descriptor_id,
  );
  return Object.freeze({
    registry,
    descriptor: selected.descriptor,
    providers: selected.providers,
    reference_documents: documents,
  });
};
