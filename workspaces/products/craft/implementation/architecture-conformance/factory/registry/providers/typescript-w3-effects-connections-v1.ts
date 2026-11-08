import type {W3Descriptor, W3Observation} from "../../../families/effects-connections/contracts/w3-contracts.js";
import {evaluateW3} from "../../../families/effects-connections/evaluator/evaluate-w3.js";
import {buildW3Hostiles} from "../../../families/effects-connections/hostiles/w3-hostiles.js";
import type {FactoryNodeProviderV1} from "../../contracts/factory-node-provider-v1.js";
import {fail} from "../../shared/canonical.js";

const parseSet = <T>(bytes: string, member: string): readonly T[] => {
  const value = JSON.parse(bytes) as Record<string, unknown>;
  const items = value[member];
  return Array.isArray(items) ? items as T[] : fail("FACTORY_W3_INPUT_INVALID", member);
};

const W3_KINDS = Object.freeze(["Mapping", "Interface", "Event", "Operation"] as const);
type W3Kind = typeof W3_KINDS[number];
const parseSelector = (bytes: string): W3Kind => {
  const value = JSON.parse(bytes) as Record<string, unknown>;
  return value.schema_version === "DomainSpecMetaTypeSelector/v1" && W3_KINDS.includes(value.kind as W3Kind)
    ? value.kind as W3Kind
    : fail("FACTORY_W3_INPUT_INVALID", "selector");
};

export const typeScriptW3EffectsConnectionsV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-w3-effects-connections-v1",
  provider_version: "1.1.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(["descriptor_set", "observations", "selector"]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-w3-effects-connections-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/effects-connections/contracts/w3-contracts.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/effects-connections/evaluator/evaluate-w3.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/effects-connections/hostiles/w3-hostiles.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const descriptors = parseSet<W3Descriptor>(rawInputs.descriptor_set ?? "", "descriptors");
    const observations = parseSet<W3Observation>(rawInputs.observations ?? "", "observations");
    const selectedKind = parseSelector(rawInputs.selector ?? "");
    const selectedDescriptors = descriptors.filter(({kind}) => kind === selectedKind);
    const selectedObservations = observations.filter(({kind}) => kind === selectedKind);
    if (selectedDescriptors.length !== 1 || selectedObservations.length !== 1) fail("FACTORY_W3_INPUT_INVALID", `cardinality:${selectedKind}`);
    const descriptor = selectedDescriptors[0]!;
    const observation = selectedObservations[0]!;
    const evaluation = evaluateW3(descriptor, observation);
    if (evaluation.verdict !== "pass") fail("FACTORY_W3_PROOF_FAILED", selectedKind);
    const hostiles = buildW3Hostiles(descriptor, observation);
    if (hostiles.length === 0) fail("FACTORY_W3_INPUT_INVALID", `hostiles:${selectedKind}`);
    const hostileResults = hostiles.map((hostile) => {
      const result = evaluateW3(descriptor, hostile.observation);
      const killed = result.verdict === "reject" && hostile.expected_codes.every((code) => result.findings.some((item) => item.code === code));
      if (!killed) fail("FACTORY_W3_HOSTILE_SURVIVED", hostile.mutant_id);
      return Object.freeze({mutant_id: hostile.mutant_id, status: "killed" as const, finding_codes: Object.freeze(result.findings.map(({code}) => code))});
    });
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "typescript-w3-effects-connections-v1",
      semantic_output: Object.freeze({
        schema_version: "W3FactoryProof/v1",
        meta_type: selectedKind,
        descriptor: Object.freeze({descriptor_id: evaluation.descriptor_id, verdict: evaluation.verdict}),
        hostiles: Object.freeze(hostileResults),
        native_language_evidence: "external-validation-required",
        admission_status: "candidate",
        authority_effect: "none",
      }),
      accounting: Object.freeze({
        positives_declared: 1,
        positives_passed: 1,
        mutants_declared: hostileResults.length,
        mutants_killed: hostileResults.length,
      }),
      claim_ceiling: `candidate-local exact ${selectedKind} descriptor-to-observation reproduction with independent hostile accounting; native language tests remain external evidence`,
      authority_effect: "none",
    });
  },
});
