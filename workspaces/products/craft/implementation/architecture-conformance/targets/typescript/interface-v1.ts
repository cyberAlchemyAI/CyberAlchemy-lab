import type {InterfaceDescriptor, InterfaceObservation} from "../../families/effects-connections/contracts/w3-contracts.js";
import {evaluateW3} from "../../families/effects-connections/evaluator/evaluate-w3.js";
import type {
  VersionedInterfaceDescriptor,
  VersionedInterfaceObservation,
} from "../../families/versioned-interface-boundary/contracts/interface-contracts.js";
import {evaluateVersionedInterface} from "../../families/versioned-interface-boundary/evaluator/evaluate-interface.js";
import {settlementInterfaceDescriptor, settlementInterfaceObservation} from "../../families/versioned-interface-boundary/fixtures/settlement-interface.js";

export type InterfacePortableResult = Readonly<{
  schema_version: "domainspec.interface-portable-result/v1";
  result: "pass";
  meta_type: "Interface";
  contract_id: string;
  version: string;
  compatibility_direction: "consumer-to-provider";
  exposed_bindings: readonly string[];
  mapping_obligations: readonly string[];
  boundary: Readonly<{inside: string; outside: string}>;
  transport_domain_separated: true;
  authority_effect: "none";
}>;

export type InterfaceCase = Readonly<{
  w3_descriptor: InterfaceDescriptor;
  w3_observation: InterfaceObservation;
  descriptor: VersionedInterfaceDescriptor;
  observation: VersionedInterfaceObservation;
}>;

const ref = (id: string) => ({id, sha256: "a".repeat(64)});
export const makeSettlementInterfaceCase = (): InterfaceCase => ({
  w3_descriptor: {
    schema_version: "domainspec.w3-descriptor/v1",
    descriptor_id: "interface.settlement-port-v1",
    language: "typescript",
    binding: {
      protocol_id: "domainspec.w3-descriptor-binding/v1",
      concept_ref: ref("DS-D1.11"), decision_ref: ref("WP-RMT-002"), profile_ref: ref("typescript"),
      provider_ref: ref("typescript-w3-effects-connections-v1"), source_ref: ref("financial-settlement.ts"), fixture_ref: ref("interface-case"),
    },
    claim_ceiling: "candidate-local-exact-fixture",
    authority_effect: "none",
    kind: "Interface",
    boundary_kind: "internal",
    contract_id: "SettlementPort",
    exact_version: "1.2.0",
    compatibility_policy_id: "exact-major/v1",
    exposed_bindings: [{binding_id:"completeSettlement",kind:"Operation"},{binding_id:"findSettlement",kind:"Query"}],
    admission_status: "candidate",
  },
  w3_observation: {
    kind: "Interface", boundary_kind: "internal", contract_id: "SettlementPort", version: "1.2.0",
    compatibility_policy_id: "exact-major/v1",
    exposed_bindings: [{binding_id:"completeSettlement",kind:"Operation"},{binding_id:"findSettlement",kind:"Query"}],
    compatibility_checks: [
      {requested_version:"1.0.0",accepted:true}, {requested_version:"1.2.0",accepted:true}, {requested_version:"2.0.0",accepted:false},
    ],
  },
  descriptor: settlementInterfaceDescriptor,
  observation: settlementInterfaceObservation(),
});

export const evaluateInterfaceCase = (input: InterfaceCase): Readonly<{
  portable: InterfacePortableResult;
  native_evidence: Readonly<{language: "typescript"; mechanism: "readonly-type-and-frozen-boundary"}>;
}> => {
  const w3 = evaluateW3(input.w3_descriptor, input.w3_observation);
  const extension = evaluateVersionedInterface(input.descriptor, input.observation);
  if (w3.verdict !== "pass" || extension.verdict !== "pass") {
    throw new Error(`RMT_IFACE_TYPESCRIPT_REJECTED:${JSON.stringify({w3:w3.findings, extension:extension.findings})}`);
  }
  return Object.freeze({
    portable: Object.freeze({
      schema_version: "domainspec.interface-portable-result/v1",
      result: "pass",
      meta_type: "Interface",
      contract_id: input.descriptor.contract_id,
      version: input.descriptor.exact_version,
      compatibility_direction: input.descriptor.compatibility_direction,
      exposed_bindings: Object.freeze(input.descriptor.exposed_bindings.map(({binding_id, kind}) => `${kind}:${binding_id}`).sort()),
      mapping_obligations: Object.freeze(input.descriptor.mapping_obligations.map(({binding_id, direction, mapping_id}) => `${binding_id}:${direction}:${mapping_id}`).sort()),
      boundary: Object.freeze({inside: input.descriptor.inside_boundary, outside: input.descriptor.outside_boundary}),
      transport_domain_separated: true,
      authority_effect: "none",
    }),
    native_evidence: Object.freeze({language: "typescript", mechanism: "readonly-type-and-frozen-boundary"}),
  });
};
