import type { MetaTypeDescriptorV2 } from "../contracts/meta-type-descriptor-v2.js";

const json = (value: unknown): string => `${JSON.stringify(value, null, 2)}\n`;

export const emptyKitTemplates = (
  descriptor: MetaTypeDescriptorV2,
): Readonly<Record<string, string>> => Object.freeze({
  "kit.json": json({
    schema_version: "ExpectedRedKit/v1",
    descriptor_id: descriptor.descriptor_id,
    meta_type_ref: descriptor.meta_type_ref,
    architecture_type_ref: descriptor.architecture_type_ref,
    target_ref: descriptor.target_ref,
    status: "empty-awaiting-owner-input",
    authority_effect: "none",
  }),
  "definition/empty.json": json({
    schema_version: "EmptyDefinitionSlot/v1",
    status: "awaiting-owner-authored-definition",
    authority_effect: "none",
  }),
  "binding/empty.json": json({
    schema_version: "EmptyBindingSlot/v1",
    status: "awaiting-handwritten-candidate-binding",
    authority_effect: "none",
  }),
  "obligations/empty.json": json({
    schema_version: "EmptyObligationCatalogue/v1",
    obligations: [],
    status: "awaiting-independent-expectations",
    authority_effect: "none",
  }),
  "mutations/empty.json": json({
    schema_version: "EmptyMutationCatalogue/v1",
    mutations: [],
    status: "awaiting-causal-mutants",
    authority_effect: "none",
  }),
  "expected-red/manifest.json": json({
    schema_version: "ExpectedRedManifest/v1",
    expected_diagnostic: "FACTORY_KIT_INCOMPLETE",
    implementation_body: "absent",
    business_outcomes: "absent",
    authority_effect: "none",
  }),
});
