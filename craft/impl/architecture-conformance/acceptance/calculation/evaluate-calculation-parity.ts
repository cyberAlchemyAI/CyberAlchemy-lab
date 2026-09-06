import {createHash} from "node:crypto";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {
  canonicalValueComputationJson,
  sha256CalculationInputs,
  sha256CalculationValue,
} from "../../families/value-computation/index.js";
import {EFFECT_CHANNELS} from
  "../../kernel/evidence/effect-observation/index.js";

type JsonObject = Record<string, unknown>;

export const CALCULATION_DIRECT_HANDLES = Object.freeze([
  Object.freeze({
    node_id: "calculation.typescript.net-settlement",
    provider_id: "typescript-calculation-v1",
    language: "typescript",
    proof_schema: "TypeScriptCalculationComposedProof/v1",
    target_id: "calculation.typescript.net-settlement/v1",
    protocol_id: "typescript.bound-calculation/v1",
  }),
  Object.freeze({
    node_id: "calculation.python.net-settlement",
    provider_id: "python-calculation-v1",
    language: "python",
    proof_schema: "PythonCalculationComposedProof/v1",
    target_id: "calculation.python.net-settlement/v1",
    protocol_id: "python.bound-calculation/v1",
  }),
  Object.freeze({
    node_id: "calculation.rust.net-settlement",
    provider_id: "rust-calculation-v1",
    language: "rust",
    proof_schema: "RustCalculationComposedProof/v1",
    target_id: "calculation.rust.net-settlement/v1",
    protocol_id: "rust.bound-calculation/v1",
  }),
] as const);

const OBLIGATION_IDS = Object.freeze([
  "exact-direct-handle-set",
  "exact-provider-target-language-protocol",
  "shared-owner-definition-provenance",
  "shared-descriptor-binding",
  "exact-owner-case-set",
  "safe-non-boolean-values",
  "exact-case-results",
  "fresh-process-determinism",
  "independent-observer-binding",
  "complete-effect-perimeter",
  "zero-forbidden-effects",
  "complete-consumption-and-quiescence",
  "portable-three-target-parity",
] as const);

type CalculationParityFindingCode =
  | "CALC_PARITY_HANDLE_SET_MISMATCH"
  | "CALC_PARITY_PROVIDER_MISMATCH"
  | "CALC_PARITY_PROOF_INVALID"
  | "CALC_PARITY_TARGET_MISMATCH"
  | "CALC_PARITY_DEFINITION_MISMATCH"
  | "CALC_PARITY_DESCRIPTOR_MISMATCH"
  | "CALC_PARITY_CASE_SET_MISMATCH"
  | "CALC_PARITY_VALUE_INVALID"
  | "CALC_PARITY_VALUE_MISMATCH"
  | "CALC_PARITY_NONDETERMINISTIC"
  | "CALC_PARITY_OBSERVER_INVALID"
  | "CALC_PARITY_EFFECT_PERIMETER_INVALID"
  | "CALC_PARITY_EFFECT_OBSERVED"
  | "CALC_PARITY_RESULT_NOT_CLOSED"
  | "CALC_PARITY_FAMILY_PROOF_INVALID"
  | "CALC_PARITY_NATIVE_EVIDENCE_MISSING"
  | "CALC_PARITY_PORTABLE_DRIFT"
  | "CALC_PARITY_RAW_INPUT_INVALID";

type DirectProjection = Readonly<{
  handle: (typeof CALCULATION_DIRECT_HANDLES)[number];
  semantic_sha256: string;
  portable: JsonObject;
  native_evidence: JsonObject;
}>;

export type CalculationParityProofV1 = Readonly<{
  schema_version: "CalculationParityProof/v1";
  result: "pass";
  composed_from: readonly Readonly<{
    node_id: string;
    provider_id: string;
    semantic_sha256: string;
    target_id: string;
    language: string;
    protocol_id: string;
  }>[];
  owner_refs: Readonly<{
    definition_id: string;
    definition_sha256: string;
    denominator_id: string;
    denominator_sha256: string;
    descriptor_id: string;
    descriptor_sha256: string;
    mutation_catalogue_sha256: string;
  }>;
  portable_projection: JsonObject;
  native_evidence_by_language: readonly Readonly<{
    language: string;
    evidence: JsonObject;
  }>[];
  obligations: readonly Readonly<{
    obligation_id: (typeof OBLIGATION_IDS)[number];
    status: "passed";
  }>[];
  hostile_mutations: readonly Readonly<{
    mutation_id: string;
    status: "killed";
    finding_code: CalculationParityFindingCode;
  }>[];
  claim_ceiling: string;
  authority_effect: "none";
}>;

const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: CalculationParityFindingCode, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`), {code});
};
const object = (
  value: unknown,
  code: CalculationParityFindingCode,
): JsonObject => isObject(value) ? value : fail(code);
const array = (
  value: unknown,
  code: CalculationParityFindingCode,
): unknown[] => Array.isArray(value) ? value : fail(code);
const string = (
  value: unknown,
  code: CalculationParityFindingCode,
): string => typeof value === "string" && value.length > 0 ? value : fail(code);
const parse = (raw: string | undefined): JsonObject => {
  if (raw === undefined) return fail("CALC_PARITY_RAW_INPUT_INVALID");
  try {
    return object(JSON.parse(raw), "CALC_PARITY_RAW_INPUT_INVALID");
  } catch {
    return fail("CALC_PARITY_RAW_INPUT_INVALID");
  }
};
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const same = (left: unknown, right: unknown): boolean =>
  canonicalValueComputationJson(left) === canonicalValueComputationJson(right);
const safeNumber = (value: unknown): value is number =>
  typeof value === "number"
  && Number.isSafeInteger(value)
  && !Object.is(value, -0);

const decodeOwnerInputs = (rawInputs: Readonly<Record<string, string>>) => {
  if (JSON.stringify(Object.keys(rawInputs)) !== JSON.stringify([
    "definition", "denominator", "mutations", "descriptor",
  ])) return fail("CALC_PARITY_RAW_INPUT_INVALID", "roles");
  const definition = parse(rawInputs.definition);
  const denominator = parse(rawInputs.denominator);
  const mutations = parse(rawInputs.mutations);
  const descriptor = parse(rawInputs.descriptor);
  const definitionSha256 = sha256(rawInputs.definition!);
  const descriptorSha256 = sha256(rawInputs.descriptor!);
  const definitionRef = object(denominator.owner_definition_ref,
    "CALC_PARITY_DEFINITION_MISMATCH");
  const descriptorRef = object(definition.descriptor_ref,
    "CALC_PARITY_DESCRIPTOR_MISMATCH");
  const mutationDenominator = object(mutations.denominator_ref,
    "CALC_PARITY_FAMILY_PROOF_INVALID");
  if (definition.schema_version !== "ValueComputationDefinition/v1"
      || definition.authorship !== "owner-authored-admission-input"
      || definition.derivation_policy
        !== "implementation-and-generated-results-forbidden-as-authority"
      || definition.authority_effect !== "none"
      || denominator.schema_version !== "ValueComputationDenominator/v1"
      || denominator.authority_effect !== "none"
      || definitionRef.definition_id !== definition.definition_id
      || definitionRef.sha256 !== definitionSha256
      || descriptor.schema_version
        !== "domainspec.calculation-cross-language-realization-descriptor/v1"
      || descriptorRef.descriptor_id !== descriptor.descriptor_id
      || descriptorRef.sha256 !== descriptorSha256
      || mutations.schema_version !== "ValueComputationMutationCatalogue/v1"
      || mutations.authorship !== "independent-family-fixture"
      || mutations.target_code_may_read_expected_findings !== false
      || mutationDenominator.denominator_id !== denominator.denominator_id
      || mutationDenominator.denominator_sha256 !== denominator.denominator_sha256) {
    return fail("CALC_PARITY_RAW_INPUT_INVALID", "binding");
  }
  const cases = array(definition.cases, "CALC_PARITY_RAW_INPUT_INVALID");
  const mutationList = array(mutations.mutations, "CALC_PARITY_RAW_INPUT_INVALID");
  const decisions = array(denominator.positive_decisions, "CALC_PARITY_RAW_INPUT_INVALID");
  if (cases.length !== 4 || mutationList.length !== 13 || decisions.length !== 11) {
    return fail("CALC_PARITY_RAW_INPUT_INVALID", "denominator-counts");
  }
  return Object.freeze({
    definition,
    denominator,
    mutations,
    descriptor,
    definitionSha256,
    descriptorSha256,
    cases,
    mutationList,
  });
};

const nativeEvidence = (
  proof: JsonObject,
  language: string,
): JsonObject => {
  if (language === "typescript") {
    const closed = object(proof.closed_subset_proof,
      "CALC_PARITY_NATIVE_EVIDENCE_MISSING");
    const runtime = object(proof.runtime_proof,
      "CALC_PARITY_NATIVE_EVIDENCE_MISSING");
    return Object.freeze({closed_subset_proof: closed, runtime_proof: runtime});
  }
  return object(proof.native_mechanism, "CALC_PARITY_NATIVE_EVIDENCE_MISSING");
};

const projectDirect = (
  upstream: FactoryUpstreamResultV1,
  handle: (typeof CALCULATION_DIRECT_HANDLES)[number],
  owner: ReturnType<typeof decodeOwnerInputs>,
): DirectProjection => {
  if (upstream.node_id !== handle.node_id || upstream.provider_id !== handle.provider_id) {
    return fail("CALC_PARITY_PROVIDER_MISMATCH", handle.node_id);
  }
  if (!/^[a-f0-9]{64}$/u.test(upstream.semantic_sha256)) {
    return fail("CALC_PARITY_PROOF_INVALID", "semantic-sha256");
  }
  const output = object(upstream.semantic_output, "CALC_PARITY_PROOF_INVALID");
  const proof = object(output.proof, "CALC_PARITY_PROOF_INVALID");
  const target = object(proof.target, "CALC_PARITY_TARGET_MISMATCH");
  const binding = object(proof.binding, "CALC_PARITY_DESCRIPTOR_MISMATCH");
  const observation = object(proof.observation, "CALC_PARITY_PROOF_INVALID");
  const definitionRef = object(observation.definition_ref,
    "CALC_PARITY_DEFINITION_MISMATCH");
  const observationBinding = object(observation.binding,
    "CALC_PARITY_DESCRIPTOR_MISMATCH");
  const effect = object(observation.effect_observation,
    "CALC_PARITY_EFFECT_PERIMETER_INVALID");
  const observer = object(effect.observer_ref, "CALC_PARITY_OBSERVER_INVALID");
  const effectTarget = object(effect.target_ref, "CALC_PARITY_TARGET_MISMATCH");
  const family = object(proof.family_evaluation,
    "CALC_PARITY_FAMILY_PROOF_INVALID");
  const accounting = object(family.positive_decision_accounting,
    "CALC_PARITY_FAMILY_PROOF_INVALID");
  if (proof.schema_version !== handle.proof_schema || proof.result !== "pass"
      || proof.authority_effect !== "none") {
    return fail("CALC_PARITY_PROOF_INVALID", handle.language);
  }
  if (target.target_id !== handle.target_id || target.language !== handle.language
      || target.protocol_id !== handle.protocol_id
      || typeof target.source_sha256 !== "string") {
    return fail("CALC_PARITY_TARGET_MISMATCH", handle.language);
  }
  if (definitionRef.definition_id !== owner.definition.definition_id
      || definitionRef.sha256 !== owner.definitionSha256) {
    return fail("CALC_PARITY_DEFINITION_MISMATCH", handle.language);
  }
  if (binding.descriptor_sha256 !== owner.descriptorSha256
      || observationBinding.descriptor_id !== owner.descriptor.descriptor_id
      || observationBinding.descriptor_sha256 !== owner.descriptorSha256
      || observationBinding.provider_id !== handle.provider_id
      || observationBinding.provider_sha256 !== binding.provider_sha256) {
    return fail("CALC_PARITY_DESCRIPTOR_MISMATCH", handle.language);
  }
  if (effectTarget.target_id !== handle.target_id
      || effectTarget.target_sha256 !== target.source_sha256) {
    return fail("CALC_PARITY_TARGET_MISMATCH", `${handle.language}:effect-target`);
  }
  if (observer.role !== "independent-effect-observer"
      || observer.provider_id !== handle.provider_id
      || observer.owner_ref === handle.provider_id
      || observer.provider_sha256 !== binding.provider_sha256
      || observer.observer_sha256 !== binding.observer_sha256) {
    return fail("CALC_PARITY_OBSERVER_INVALID", handle.language);
  }
  const cases = array(observation.cases, "CALC_PARITY_CASE_SET_MISMATCH");
  if (cases.length !== owner.cases.length) {
    return fail("CALC_PARITY_CASE_SET_MISMATCH", handle.language);
  }
  const portableCases = owner.cases.map((ownerCaseValue, index) => {
    const ownerCase = object(ownerCaseValue, "CALC_PARITY_CASE_SET_MISMATCH");
    const observed = object(cases[index], "CALC_PARITY_CASE_SET_MISMATCH");
    const ownerInputs = object(ownerCase.inputs, "CALC_PARITY_CASE_SET_MISMATCH");
    if (Object.values(ownerInputs).some((value) =>
      typeof value !== "string" && typeof value !== "number" && value !== null)) {
      return fail("CALC_PARITY_CASE_SET_MISMATCH", String(ownerCase.case_id));
    }
    if (observed.case_id !== ownerCase.case_id
        || observed.input_sha256 !== sha256CalculationInputs(
          ownerInputs as Readonly<Record<string, string | number | null>>,
        )) return fail("CALC_PARITY_CASE_SET_MISMATCH", String(ownerCase.case_id));
    if (!safeNumber(observed.result_value) || observed.result_kind !== "number") {
      return fail("CALC_PARITY_VALUE_INVALID", String(ownerCase.case_id));
    }
    if (observed.result_value !== ownerCase.expected_value
        || observed.result_sha256 !== sha256CalculationValue(ownerCase.expected_value)) {
      return fail("CALC_PARITY_VALUE_MISMATCH", String(ownerCase.case_id));
    }
    if (observed.process_isolation !== "separate-process"
        || observed.fresh_process_result_sha256 !== observed.result_sha256) {
      return fail("CALC_PARITY_NONDETERMINISTIC", String(ownerCase.case_id));
    }
    return Object.freeze({
      case_id: observed.case_id,
      input_sha256: observed.input_sha256,
      result_kind: observed.result_kind,
      result_value: observed.result_value,
      result_sha256: observed.result_sha256,
      fresh_process_result_sha256: observed.fresh_process_result_sha256,
      process_isolation: observed.process_isolation,
    });
  });
  const channels = array(effect.channels, "CALC_PARITY_EFFECT_PERIMETER_INVALID");
  if (channels.length !== EFFECT_CHANNELS.length) {
    return fail("CALC_PARITY_EFFECT_PERIMETER_INVALID", handle.language);
  }
  const portableChannels = EFFECT_CHANNELS.map((channel, index) => {
    const observed = object(channels[index], "CALC_PARITY_EFFECT_PERIMETER_INVALID");
    if (observed.channel !== channel || observed.coverage !== "supported") {
      return fail("CALC_PARITY_EFFECT_PERIMETER_INVALID", channel);
    }
    for (const count of ["read_count", "write_count", "escape_count", "deferred_count"]) {
      if (observed[count] !== 0) return fail("CALC_PARITY_EFFECT_OBSERVED", `${channel}:${count}`);
    }
    return Object.freeze({
      channel,
      coverage: "supported" as const,
      read_count: 0,
      write_count: 0,
      escape_count: 0,
      deferred_count: 0,
    });
  });
  const result = object(effect.result, "CALC_PARITY_RESULT_NOT_CLOSED");
  const quiescence = object(effect.quiescence, "CALC_PARITY_RESULT_NOT_CLOSED");
  if (result.consumption !== "complete" || result.mutable_alias_observed !== false
      || quiescence.observed !== true || quiescence.pending_count !== 0) {
    return fail("CALC_PARITY_RESULT_NOT_CLOSED", handle.language);
  }
  if (family.verdict !== "pass" || array(family.findings,
    "CALC_PARITY_FAMILY_PROOF_INVALID").length !== 0
      || accounting.declared !== 11 || accounting.passed !== 11
      || accounting.failed !== 0 || accounting.unaccounted !== 0) {
    return fail("CALC_PARITY_FAMILY_PROOF_INVALID", handle.language);
  }
  const proofMutations = array(proof.mutations, "CALC_PARITY_FAMILY_PROOF_INVALID");
  if (proofMutations.length !== owner.mutationList.length) {
    return fail("CALC_PARITY_FAMILY_PROOF_INVALID", "mutation-count");
  }
  const mutationProjection = proofMutations.map((value, index) => {
    const mutation = object(value, "CALC_PARITY_FAMILY_PROOF_INVALID");
    const ownerMutation = object(owner.mutationList[index],
      "CALC_PARITY_FAMILY_PROOF_INVALID");
    if (mutation.mutation_id !== ownerMutation.mutation_id || mutation.status !== "killed"
        || !same(mutation.finding_codes, ownerMutation.expected_finding_codes)) {
      return fail("CALC_PARITY_FAMILY_PROOF_INVALID", String(ownerMutation.mutation_id));
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: mutation.status,
      finding_codes: mutation.finding_codes,
    });
  });
  return Object.freeze({
    handle,
    semantic_sha256: upstream.semantic_sha256,
    portable: Object.freeze({
      definition_id: owner.definition.definition_id,
      definition_sha256: owner.definitionSha256,
      descriptor_id: owner.descriptor.descriptor_id,
      descriptor_sha256: owner.descriptorSha256,
      cases: Object.freeze(portableCases),
      effect: Object.freeze({
        channels: Object.freeze(portableChannels),
        result: Object.freeze({consumption: "complete", mutable_alias_observed: false}),
        quiescence: Object.freeze({observed: true, pending_count: 0}),
      }),
      family: Object.freeze({
        verdict: "pass",
        portable_claim:
          "owner-bound-deterministic-zero-effect-value-under-declared-perimeter",
        positive_decisions: Object.freeze({declared: 11, passed: 11}),
        mutations: Object.freeze(mutationProjection),
      }),
    }),
    native_evidence: nativeEvidence(proof, handle.language),
  });
};

export const evaluateCalculationParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const keys = Object.keys(upstream);
  const expectedKeys = CALCULATION_DIRECT_HANDLES.map(({node_id: nodeId}) => nodeId);
  if (JSON.stringify(keys) !== JSON.stringify(expectedKeys)) {
    return fail("CALC_PARITY_HANDLE_SET_MISMATCH");
  }
  const owner = decodeOwnerInputs(rawInputs);
  const direct = CALCULATION_DIRECT_HANDLES.map((handle) =>
    projectDirect(upstream[handle.node_id]!, handle, owner));
  const reference = direct[0]!.portable;
  for (const projection of direct.slice(1)) {
    if (!same(projection.portable, reference)) {
      return fail("CALC_PARITY_PORTABLE_DRIFT", projection.handle.language);
    }
  }
  return Object.freeze({owner, direct, portable_projection: reference});
};

const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

const hostileCases = Object.freeze([
  Object.freeze({mutation_id: "join/missing-handle", finding: "CALC_PARITY_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[CALCULATION_DIRECT_HANDLES[0].node_id]; }}),
  Object.freeze({mutation_id: "join/wrong-provider", finding: "CALC_PARITY_PROVIDER_MISMATCH", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].provider_id = "wrong-provider"; }}),
  Object.freeze({mutation_id: "join/wrong-target", finding: "CALC_PARITY_TARGET_MISMATCH", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.target.target_id = "wrong-target"; }}),
  Object.freeze({mutation_id: "join/stale-definition", finding: "CALC_PARITY_DEFINITION_MISMATCH", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.definition_ref.sha256 = "0".repeat(64); }}),
  Object.freeze({mutation_id: "join/stale-descriptor", finding: "CALC_PARITY_DESCRIPTOR_MISMATCH", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.binding.descriptor_sha256 = "0".repeat(64); }}),
  Object.freeze({mutation_id: "join/missing-case", finding: "CALC_PARITY_CASE_SET_MISMATCH", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.cases.pop(); }}),
  Object.freeze({mutation_id: "join/wrong-value", finding: "CALC_PARITY_VALUE_MISMATCH", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.cases[0].result_value += 1; }}),
  Object.freeze({mutation_id: "join/boolean-value", finding: "CALC_PARITY_VALUE_INVALID", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.cases[0].result_value = true; }}),
  Object.freeze({mutation_id: "join/unsafe-number", finding: "CALC_PARITY_VALUE_INVALID", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.cases[0].result_value = Number.MAX_SAFE_INTEGER + 1; }}),
  Object.freeze({mutation_id: "join/fresh-process-drift", finding: "CALC_PARITY_NONDETERMINISTIC", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.cases[0].fresh_process_result_sha256 = "0".repeat(64); }}),
  Object.freeze({mutation_id: "join/unsupported-channel", finding: "CALC_PARITY_EFFECT_PERIMETER_INVALID", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.effect_observation.channels[0].coverage = "unsupported"; }}),
  Object.freeze({mutation_id: "join/nonzero-effect", finding: "CALC_PARITY_EFFECT_OBSERVED", apply: (u: any) => { u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.observation.effect_observation.channels[0].read_count = 1; }}),
  Object.freeze({mutation_id: "join/native-evidence-erased", finding: "CALC_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { delete u[CALCULATION_DIRECT_HANDLES[0].node_id].semantic_output.proof.closed_subset_proof; }}),
] as const);

export const proveCalculationParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
): CalculationParityProofV1 => {
  const evaluated = evaluateCalculationParity(upstream, rawInputs);
  const hostileMutations = hostileCases.map(({mutation_id: mutationId, finding, apply}) => {
    const mutated = clone(upstream);
    apply(mutated);
    try {
      evaluateCalculationParity(mutated, rawInputs);
    } catch (error: unknown) {
      const code = isObject(error) ? error.code : undefined;
      if (code === finding) return Object.freeze({
        mutation_id: mutationId,
        status: "killed" as const,
        finding_code: finding as CalculationParityFindingCode,
      });
      throw error;
    }
    return fail("CALC_PARITY_PORTABLE_DRIFT", `mutant-survived:${mutationId}`);
  });
  return Object.freeze({
    schema_version: "CalculationParityProof/v1" as const,
    result: "pass" as const,
    composed_from: Object.freeze(evaluated.direct.map(({handle, semantic_sha256: sha}) =>
      Object.freeze({
        node_id: handle.node_id,
        provider_id: handle.provider_id,
        semantic_sha256: sha,
        target_id: handle.target_id,
        language: handle.language,
        protocol_id: handle.protocol_id,
      }))),
    owner_refs: Object.freeze({
      definition_id: string(evaluated.owner.definition.definition_id,
        "CALC_PARITY_RAW_INPUT_INVALID"),
      definition_sha256: evaluated.owner.definitionSha256,
      denominator_id: string(evaluated.owner.denominator.denominator_id,
        "CALC_PARITY_RAW_INPUT_INVALID"),
      denominator_sha256: string(evaluated.owner.denominator.denominator_sha256,
        "CALC_PARITY_RAW_INPUT_INVALID"),
      descriptor_id: string(evaluated.owner.descriptor.descriptor_id,
        "CALC_PARITY_RAW_INPUT_INVALID"),
      descriptor_sha256: evaluated.owner.descriptorSha256,
      mutation_catalogue_sha256: string(evaluated.owner.mutations.catalogue_sha256,
        "CALC_PARITY_RAW_INPUT_INVALID"),
    }),
    portable_projection: evaluated.portable_projection,
    native_evidence_by_language: Object.freeze(evaluated.direct.map(({handle, native_evidence: evidence}) =>
      Object.freeze({language: handle.language, evidence}))),
    obligations: Object.freeze(OBLIGATION_IDS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: Object.freeze(hostileMutations),
    claim_ceiling: "same-host same-oracle portable Calculation parity for the exact four owner-authored inert cases across the exact locked TypeScript, Python, and Rust handles; native mechanism evidence is retained but excluded from portable equality; this is not full-domain equivalence, cross-host equivalence, arbitrary-caller purity, operating-system interception, candidate projection, promotion, publication, release, deployment, or production",
    authority_effect: "none" as const,
  });
};
