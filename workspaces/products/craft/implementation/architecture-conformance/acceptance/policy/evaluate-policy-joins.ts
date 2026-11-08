import {createHash} from "node:crypto";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {
  applyStrategyMembershipMutant,
  decodeStrategyMembershipDenominatorV1,
  decodeStrategyMembershipMutationCatalogueV1,
  decodeStrategySelectionDenominatorV1,
  decodeStrategySelectionMutationCatalogueV1,
  evaluateStrategyMembership,
  mintStrategyMembershipObservationV1,
  sha256SelectedStrategyIdentity,
  sha256StrategySelectionInputs,
} from "../../families/strategy-selection/index.js";
import {EFFECT_CHANNELS} from
  "../../kernel/evidence/effect-observation/index.js";

type JsonObject = Record<string, unknown>;
type Owner = ReturnType<typeof decodeOwner>;
type MembershipOwner = ReturnType<typeof decodeMembershipOwner>;

export const POLICY_DIRECT_HANDLES = Object.freeze([
  Object.freeze({
    node_id: "policy.typescript.settlement-routing",
    provider_id: "typescript-policy-v1",
    language: "typescript",
    proof_schema: "TypeScriptPolicyComposedProof/v1",
    target_id: "policy.typescript.settlement-routing/v1",
    protocol_id: "typescript.bound-policy/v1",
  }),
  Object.freeze({
    node_id: "policy.python.settlement-routing",
    provider_id: "python-policy-v1",
    language: "python",
    proof_schema: "PythonPolicyComposedProof/v1",
    target_id: "policy.python.settlement-routing/v1",
    protocol_id: "python.bound-policy/v1",
  }),
  Object.freeze({
    node_id: "policy.rust.settlement-routing",
    provider_id: "rust-policy-v1",
    language: "rust",
    proof_schema: "RustPolicyComposedProof/v1",
    target_id: "policy.rust.settlement-routing/v1",
    protocol_id: "rust.bound-policy/v1",
  }),
] as const);

export const POLICY_PARITY_HANDLE = Object.freeze({
  node_id: "policy.parity.settlement-routing",
  provider_id: "policy-parity-v1",
});

export const POLICY_JOIN_RAW_PATHS = Object.freeze({
  catalogue:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/catalogue.json",
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/selector-definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/selector-denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/selector-mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/policy/cross-language-realization-descriptor.json",
});

export const POLICY_RELATION_RAW_PATHS = Object.freeze({
  catalogue:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/catalogue.json",
  membership_denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/denominator.json",
  membership_mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/policy/cross-language-realization-descriptor.json",
});

const PARITY_OBLIGATIONS = Object.freeze([
  "exact-direct-handle-set",
  "exact-provider-target-language-protocol",
  "shared-owner-definition-and-catalogue",
  "shared-descriptor-binding",
  "exact-owner-case-order",
  "exact-input-sensitive-strategy-identities",
  "strategy-identity-not-boolean",
  "family-proof-accounting-complete",
  "independent-effect-observer-binding",
  "complete-effect-perimeter",
  "zero-forbidden-effects",
  "complete-consumption-and-quiescence",
  "zero-selected-strategy-execution",
  "portable-three-target-parity",
] as const);

const RELATION_OBLIGATIONS = Object.freeze([
  "exact-parity-handle",
  "owner-catalogue-provenance",
  "exact-content-addressed-current-set",
  "data-only-members",
  "exact-owner-case-relation",
  "every-selection-is-current-member",
  "all-owner-strategy-identities-covered",
  "selection-does-not-execute-strategy",
] as const);

type PolicyJoinFindingCode =
  | "POLICY_JOIN_OWNER_INPUT_INVALID"
  | "POLICY_PARITY_HANDLE_SET_MISMATCH"
  | "POLICY_PARITY_PROVIDER_MISMATCH"
  | "POLICY_PARITY_PROOF_INVALID"
  | "POLICY_PARITY_TARGET_MISMATCH"
  | "POLICY_PARITY_OWNER_BINDING_MISMATCH"
  | "POLICY_PARITY_CASE_SET_MISMATCH"
  | "POLICY_PARITY_SELECTED_IDENTITY_INVALID"
  | "POLICY_PARITY_FAMILY_PROOF_INVALID"
  | "POLICY_PARITY_EFFECT_EVIDENCE_INVALID"
  | "POLICY_PARITY_EXECUTION_OBSERVED"
  | "POLICY_PARITY_NATIVE_EVIDENCE_MISSING"
  | "POLICY_PARITY_PORTABLE_DRIFT"
  | "POLICY_RELATION_HANDLE_SET_MISMATCH"
  | "POLICY_RELATION_PROVIDER_MISMATCH"
  | "POLICY_RELATION_PROOF_INVALID"
  | "POLICY_RELATION_CATALOGUE_MISMATCH"
  | "POLICY_RELATION_MEMBERSHIP_PROOF_INVALID"
  | "POLICY_RELATION_CASE_SET_MISMATCH"
  | "POLICY_RELATION_UNKNOWN_STRATEGY"
  | "POLICY_RELATION_COVERAGE_INCOMPLETE"
  | "POLICY_RELATION_EXECUTION_OBSERVED";

const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const object = (value: unknown, code: PolicyJoinFindingCode): JsonObject =>
  isObject(value) ? value : fail(code);
const array = (value: unknown, code: PolicyJoinFindingCode): unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = (value: unknown, code: PolicyJoinFindingCode): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const fail = (code: PolicyJoinFindingCode, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`), {code});
};
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8")
  .digest("hex");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const same = (left: unknown, right: unknown): boolean =>
  JSON.stringify(left) === JSON.stringify(right);
const clone = <T>(value: T): T => structuredClone(value);

const decodeOwner = (raw: Readonly<Record<string, string>>) => {
  const expectedRoles = Object.keys(POLICY_JOIN_RAW_PATHS).sort(compareUtf8);
  if (!same(Object.keys(raw).sort(compareUtf8), expectedRoles)) {
    return fail("POLICY_JOIN_OWNER_INPUT_INVALID", "roles");
  }
  try {
    const decoded = decodeStrategySelectionDenominatorV1(
      raw.denominator!,
      raw.definition!,
      POLICY_JOIN_RAW_PATHS.definition,
      raw.catalogue!,
      POLICY_JOIN_RAW_PATHS.catalogue,
      POLICY_JOIN_RAW_PATHS.descriptor,
      raw.descriptor!,
    );
    const mutationCatalogue = decodeStrategySelectionMutationCatalogueV1(raw.mutations!);
    if (mutationCatalogue.mutations.length !== 16 ||
        decoded.definition.cases.length !== 5 ||
        decoded.denominator.positive_decisions.length !== 14 ||
        decoded.catalogue.members.length !== 3) {
      return fail("POLICY_JOIN_OWNER_INPUT_INVALID", "counts");
    }
    return Object.freeze({
      ...decoded,
      mutationCatalogue,
      raw_sha256: Object.freeze({
        catalogue: sha256(raw.catalogue!),
        definition: sha256(raw.definition!),
        denominator: sha256(raw.denominator!),
        mutations: sha256(raw.mutations!),
        descriptor: sha256(raw.descriptor!),
      }),
    });
  } catch (error: unknown) {
    if (isObject(error) && typeof error.code === "string" &&
        String(error.code).startsWith("POLICY_JOIN_")) throw error;
    return fail("POLICY_JOIN_OWNER_INPUT_INVALID",
      error instanceof Error ? error.message : String(error));
  }
};

const decodeMembershipOwner = (raw: Readonly<Record<string, string>>) => {
  const expectedRoles = Object.keys(POLICY_RELATION_RAW_PATHS).sort(compareUtf8);
  if (!same(Object.keys(raw).sort(compareUtf8), expectedRoles)) {
    return fail("POLICY_JOIN_OWNER_INPUT_INVALID", "membership-roles");
  }
  try {
    const decoded = decodeStrategyMembershipDenominatorV1(
      raw.membership_denominator!,
      raw.catalogue!,
      POLICY_RELATION_RAW_PATHS.catalogue,
      POLICY_RELATION_RAW_PATHS.descriptor,
      raw.descriptor!,
    );
    const mutationCatalogue = decodeStrategyMembershipMutationCatalogueV1(
      raw.membership_mutations!,
    );
    if (decoded.catalogue.members.length !== 3 ||
        decoded.denominator.positive_decisions.length !== 8 ||
        mutationCatalogue.mutations.length !== 10 ||
        mutationCatalogue.denominator_ref.denominator_id !==
          decoded.denominator.denominator_id ||
        mutationCatalogue.denominator_ref.denominator_sha256 !==
          decoded.denominator.denominator_sha256) {
      return fail("POLICY_JOIN_OWNER_INPUT_INVALID", "membership-counts-or-binding");
    }
    return Object.freeze({
      ...decoded,
      mutationCatalogue,
      raw_sha256: Object.freeze({
        catalogue: sha256(raw.catalogue!),
        membership_denominator: sha256(raw.membership_denominator!),
        membership_mutations: sha256(raw.membership_mutations!),
        descriptor: sha256(raw.descriptor!),
      }),
    });
  } catch (error: unknown) {
    if (isObject(error) && typeof error.code === "string" &&
        String(error.code).startsWith("POLICY_JOIN_")) throw error;
    return fail("POLICY_JOIN_OWNER_INPUT_INVALID",
      error instanceof Error ? error.message : String(error));
  }
};

const nativeEvidence = (proof: JsonObject, language: string): JsonObject => {
  if (language === "typescript") {
    return Object.freeze({
      closed_subset_proof: object(
        proof.closed_subset_proof,
        "POLICY_PARITY_NATIVE_EVIDENCE_MISSING",
      ),
      runtime_proof: object(
        proof.runtime_proof,
        "POLICY_PARITY_NATIVE_EVIDENCE_MISSING",
      ),
    });
  }
  return object(proof.native_mechanism, "POLICY_PARITY_NATIVE_EVIDENCE_MISSING");
};

const projectDirect = (
  upstream: FactoryUpstreamResultV1,
  handle: (typeof POLICY_DIRECT_HANDLES)[number],
  owner: Owner,
) => {
  if (upstream.node_id !== handle.node_id || upstream.provider_id !== handle.provider_id) {
    return fail("POLICY_PARITY_PROVIDER_MISMATCH", handle.node_id);
  }
  if (!/^[a-f0-9]{64}$/u.test(upstream.semantic_sha256)) {
    return fail("POLICY_PARITY_PROOF_INVALID", "semantic-sha256");
  }
  const output = object(upstream.semantic_output, "POLICY_PARITY_PROOF_INVALID");
  const proof = object(output.proof, "POLICY_PARITY_PROOF_INVALID");
  const target = object(proof.target, "POLICY_PARITY_TARGET_MISMATCH");
  const binding = object(proof.binding, "POLICY_PARITY_OWNER_BINDING_MISMATCH");
  const observation = object(proof.observation, "POLICY_PARITY_PROOF_INVALID");
  const definitionRef = object(
    observation.definition_ref,
    "POLICY_PARITY_OWNER_BINDING_MISMATCH",
  );
  const catalogueRef = object(
    observation.catalogue_ref,
    "POLICY_PARITY_OWNER_BINDING_MISMATCH",
  );
  const observationBinding = object(
    observation.binding,
    "POLICY_PARITY_OWNER_BINDING_MISMATCH",
  );
  if (proof.schema_version !== handle.proof_schema || proof.result !== "pass" ||
      proof.authority_effect !== "none") {
    return fail("POLICY_PARITY_PROOF_INVALID", handle.language);
  }
  if (target.target_id !== handle.target_id || target.language !== handle.language ||
      target.protocol_id !== handle.protocol_id ||
      typeof target.source_sha256 !== "string") {
    return fail("POLICY_PARITY_TARGET_MISMATCH", handle.language);
  }
  if (definitionRef.definition_id !== owner.definition.definition_id ||
      definitionRef.sha256 !== owner.raw_sha256.definition ||
      catalogueRef.catalogue_id !== owner.catalogue.catalogue_id ||
      catalogueRef.catalogue_sha256 !== owner.catalogue.catalogue_sha256 ||
      binding.descriptor_sha256 !== owner.raw_sha256.descriptor ||
      observationBinding.descriptor_id !== owner.definition.descriptor_ref.descriptor_id ||
      observationBinding.descriptor_sha256 !== owner.raw_sha256.descriptor ||
      observationBinding.provider_id !== handle.provider_id ||
      observationBinding.provider_sha256 !== binding.provider_sha256) {
    return fail("POLICY_PARITY_OWNER_BINDING_MISMATCH", handle.language);
  }
  const family = object(proof.family_evaluation, "POLICY_PARITY_FAMILY_PROOF_INVALID");
  const familyAccounting = object(
    family.positive_decision_accounting,
    "POLICY_PARITY_FAMILY_PROOF_INVALID",
  );
  const mutations = array(proof.mutations, "POLICY_PARITY_FAMILY_PROOF_INVALID");
  if (family.verdict !== "pass" || familyAccounting.declared !== 14 ||
      familyAccounting.passed !== 14 || familyAccounting.failed !== 0 ||
      mutations.length !== 16 || mutations.some((value) =>
        !isObject(value) || value.status !== "killed")) {
    return fail("POLICY_PARITY_FAMILY_PROOF_INVALID", handle.language);
  }
  const observedCases = array(observation.cases, "POLICY_PARITY_CASE_SET_MISMATCH");
  if (observedCases.length !== owner.definition.cases.length) {
    return fail("POLICY_PARITY_CASE_SET_MISMATCH", handle.language);
  }
  const portableCases = owner.definition.cases.map((expected, index) => {
    const observed = object(observedCases[index], "POLICY_PARITY_CASE_SET_MISMATCH");
    if (observed.case_id !== expected.case_id ||
        observed.input_sha256 !== sha256StrategySelectionInputs(expected.inputs) ||
        observed.selected_kind !== "strategy-id" ||
        typeof observed.selected_strategy_id !== "string" ||
        observed.selected_strategy_id !== expected.expected_strategy_id ||
        observed.selected_sha256 !==
          sha256SelectedStrategyIdentity(expected.expected_strategy_id) ||
        observed.branch_id !== expected.expected_branch_id ||
        !same(observed.consumed_input_facts,
          owner.definition.input_facts.map(({name}) => name))) {
      return fail("POLICY_PARITY_SELECTED_IDENTITY_INVALID", expected.case_id);
    }
    return Object.freeze({
      case_id: expected.case_id,
      input_sha256: observed.input_sha256 as string,
      selected_strategy_id: expected.expected_strategy_id,
      selected_sha256: observed.selected_sha256 as string,
      branch_id: expected.expected_branch_id,
    });
  });
  const effect = object(
    observation.effect_observation,
    "POLICY_PARITY_EFFECT_EVIDENCE_INVALID",
  );
  const effectTarget = object(effect.target_ref, "POLICY_PARITY_TARGET_MISMATCH");
  const effectObserver = object(
    effect.observer_ref,
    "POLICY_PARITY_EFFECT_EVIDENCE_INVALID",
  );
  const effectResult = object(effect.result, "POLICY_PARITY_EFFECT_EVIDENCE_INVALID");
  const quiescence = object(
    effect.quiescence,
    "POLICY_PARITY_EFFECT_EVIDENCE_INVALID",
  );
  const channels = array(effect.channels, "POLICY_PARITY_EFFECT_EVIDENCE_INVALID");
  if (effectTarget.target_id !== handle.target_id ||
      effectTarget.target_sha256 !== target.source_sha256 ||
      effectObserver.role !== "independent-effect-observer" ||
      effectObserver.provider_id !== handle.provider_id ||
      effectObserver.provider_sha256 !== binding.provider_sha256 ||
      channels.length !== EFFECT_CHANNELS.length ||
      !same(channels.map((value) => object(
        value,
        "POLICY_PARITY_EFFECT_EVIDENCE_INVALID",
      ).channel), EFFECT_CHANNELS) ||
      channels.some((value) => {
        const channel = object(value, "POLICY_PARITY_EFFECT_EVIDENCE_INVALID");
        return channel.coverage !== "supported" || channel.read_count !== 0 ||
          channel.write_count !== 0 || channel.escape_count !== 0 ||
          channel.deferred_count !== 0;
      }) || effectResult.consumption !== "complete" ||
      effectResult.mutable_alias_observed !== false ||
      quiescence.observed !== true || quiescence.pending_count !== 0) {
    return fail("POLICY_PARITY_EFFECT_EVIDENCE_INVALID", handle.language);
  }
  const execution = object(
    observation.strategy_execution_observation,
    "POLICY_PARITY_EXECUTION_OBSERVED",
  );
  const executionObserver = object(
    execution.observer_ref,
    "POLICY_PARITY_EXECUTION_OBSERVED",
  );
  const executionTarget = object(execution.target_ref, "POLICY_PARITY_TARGET_MISMATCH");
  if (executionTarget.target_id !== handle.target_id ||
      executionTarget.target_sha256 !== target.source_sha256 ||
      executionObserver.role !== "independent-strategy-execution-observer" ||
      executionObserver.provider_id !== handle.provider_id ||
      executionObserver.provider_sha256 !== binding.provider_sha256 ||
      execution.coverage !== "all-owner-declared-strategies" ||
      execution.attempt_count !== 0 || execution.completion_count !== 0 ||
      !same(execution.attempted_strategy_ids, [])) {
    return fail("POLICY_PARITY_EXECUTION_OBSERVED", handle.language);
  }
  return Object.freeze({
    composed_from: Object.freeze({
      node_id: handle.node_id,
      provider_id: handle.provider_id,
      semantic_sha256: upstream.semantic_sha256,
      target_id: handle.target_id,
      language: handle.language,
      protocol_id: handle.protocol_id,
    }),
    portable: Object.freeze({cases: Object.freeze(portableCases)}),
    native: nativeEvidence(proof, handle.language),
    non_execution: Object.freeze({
      language: handle.language,
      attempt_count: 0,
      completion_count: 0,
    }),
  });
};

export const evaluatePolicyParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const expected = POLICY_DIRECT_HANDLES.map(({node_id: nodeId}) => nodeId)
    .sort(compareUtf8);
  if (!same(Object.keys(upstream).sort(compareUtf8), expected)) {
    return fail("POLICY_PARITY_HANDLE_SET_MISMATCH");
  }
  const owner = decodeOwner(rawInputs);
  const projections = POLICY_DIRECT_HANDLES.map((handle) =>
    projectDirect(upstream[handle.node_id]!, handle, owner));
  const portable = projections[0]!.portable;
  for (const projection of projections.slice(1)) {
    if (!same(projection.portable, portable)) {
      return fail("POLICY_PARITY_PORTABLE_DRIFT", projection.composed_from.language);
    }
  }
  return Object.freeze({
    owner,
    composed_from: Object.freeze(projections.map(({composed_from}) => composed_from)),
    portable_projection: portable,
    native_evidence_by_language: Object.freeze(projections.map(({composed_from, native}) =>
      Object.freeze({language: composed_from.language, evidence: native}))),
    non_execution_by_language: Object.freeze(projections.map(({non_execution}) =>
      non_execution)),
  });
};

const parityHostiles = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const cases: readonly Readonly<{
    mutation_id: string;
    finding_code: PolicyJoinFindingCode;
    apply: () => void;
  }>[] = [
    {mutation_id: "policy-parity.missing-handle/v1",
      finding_code: "POLICY_PARITY_HANDLE_SET_MISMATCH", apply: () => {
        const value = clone(upstream) as Record<string, FactoryUpstreamResultV1>;
        delete value[POLICY_DIRECT_HANDLES[0].node_id];
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.provider-drift/v1",
      finding_code: "POLICY_PARITY_PROVIDER_MISMATCH", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[0].node_id].provider_id = "foreign-provider";
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.proof-shape/v1",
      finding_code: "POLICY_PARITY_PROOF_INVALID", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[0].node_id].semantic_output.proof.result = "fail";
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.target-drift/v1",
      finding_code: "POLICY_PARITY_TARGET_MISMATCH", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[1].node_id].semantic_output.proof.target.target_id =
          "policy.foreign/v1";
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.owner-binding-drift/v1",
      finding_code: "POLICY_PARITY_OWNER_BINDING_MISMATCH", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[2].node_id]
          .semantic_output.proof.observation.catalogue_ref.catalogue_sha256 = "0".repeat(64);
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.case-missing/v1",
      finding_code: "POLICY_PARITY_CASE_SET_MISMATCH", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[0].node_id]
          .semantic_output.proof.observation.cases.pop();
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.selected-identity-drift/v1",
      finding_code: "POLICY_PARITY_SELECTED_IDENTITY_INVALID", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[1].node_id]
          .semantic_output.proof.observation.cases[0].selected_strategy_id = true;
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.family-verdict-drift/v1",
      finding_code: "POLICY_PARITY_FAMILY_PROOF_INVALID", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[2].node_id]
          .semantic_output.proof.family_evaluation.verdict = "fail";
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.effect-perimeter-missing/v1",
      finding_code: "POLICY_PARITY_EFFECT_EVIDENCE_INVALID", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[0].node_id]
          .semantic_output.proof.observation.effect_observation.channels.pop();
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.effect-read/v1",
      finding_code: "POLICY_PARITY_EFFECT_EVIDENCE_INVALID", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[1].node_id]
          .semantic_output.proof.observation.effect_observation.channels[0].read_count = 1;
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.strategy-execution/v1",
      finding_code: "POLICY_PARITY_EXECUTION_OBSERVED", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[2].node_id]
          .semantic_output.proof.observation
          .strategy_execution_observation.attempt_count = 1;
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.native-evidence-missing/v1",
      finding_code: "POLICY_PARITY_NATIVE_EVIDENCE_MISSING", apply: () => {
        const value = clone(upstream) as any;
        delete value[POLICY_DIRECT_HANDLES[1].node_id]
          .semantic_output.proof.native_mechanism;
        evaluatePolicyParity(value, rawInputs);
      }},
    {mutation_id: "policy-parity.stale-owner-input/v1",
      finding_code: "POLICY_JOIN_OWNER_INPUT_INVALID", apply: () =>
        evaluatePolicyParity(upstream, {...rawInputs, descriptor: `${rawInputs.descriptor}\n`})},
  ];
  return Object.freeze(cases.map((testCase) => {
    try {
      testCase.apply();
      return fail("POLICY_PARITY_PROOF_INVALID", testCase.mutation_id);
    } catch (error: unknown) {
      if (!isObject(error) || error.code !== testCase.finding_code) throw error;
    }
    return Object.freeze({
      mutation_id: testCase.mutation_id,
      status: "killed" as const,
      finding_code: testCase.finding_code,
    });
  }));
};

export const provePolicyParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const evaluated = evaluatePolicyParity(upstream, rawInputs);
  return Object.freeze({
    schema_version: "PolicyParityProof/v1" as const,
    result: "pass" as const,
    composed_from: evaluated.composed_from,
    owner_refs: Object.freeze({
      catalogue_id: evaluated.owner.catalogue.catalogue_id,
      catalogue_sha256: evaluated.owner.catalogue.catalogue_sha256,
      catalogue_raw_sha256: evaluated.owner.raw_sha256.catalogue,
      definition_id: evaluated.owner.definition.definition_id,
      definition_sha256: evaluated.owner.definition.definition_sha256,
      definition_raw_sha256: evaluated.owner.raw_sha256.definition,
      denominator_id: evaluated.owner.denominator.denominator_id,
      denominator_sha256: evaluated.owner.denominator.denominator_sha256,
      descriptor_id: evaluated.owner.definition.descriptor_ref.descriptor_id,
      descriptor_sha256: evaluated.owner.raw_sha256.descriptor,
    }),
    portable_projection: evaluated.portable_projection,
    native_evidence_by_language: evaluated.native_evidence_by_language,
    non_execution_by_language: evaluated.non_execution_by_language,
    obligations: Object.freeze(PARITY_OBLIGATIONS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: parityHostiles(upstream, rawInputs),
    claim_ceiling: "same-host same-oracle portable Policy selection parity over exact TypeScript, Python, and Rust handles and five owner-authored inert cases, retaining native mechanism and zero-strategy-execution evidence separately; not business-routing correctness, selected-strategy correctness, strategy execution correctness, arbitrary-runtime equivalence, promotion, or production readiness",
    authority_effect: "none" as const,
  });
};

const evaluateRelation = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const expectedHandles = [
    ...POLICY_DIRECT_HANDLES.map(({node_id: nodeId}) => nodeId),
    POLICY_PARITY_HANDLE.node_id,
  ].sort(compareUtf8);
  if (!same(Object.keys(upstream).sort(compareUtf8), expectedHandles)) {
    return fail("POLICY_RELATION_HANDLE_SET_MISMATCH");
  }
  const parityHandle = upstream[POLICY_PARITY_HANDLE.node_id]!;
  if (parityHandle.node_id !== POLICY_PARITY_HANDLE.node_id ||
      parityHandle.provider_id !== POLICY_PARITY_HANDLE.provider_id) {
    return fail("POLICY_RELATION_PROVIDER_MISMATCH");
  }
  const output = object(parityHandle.semantic_output, "POLICY_RELATION_PROOF_INVALID");
  const proof = object(output.proof, "POLICY_RELATION_PROOF_INVALID");
  if (proof.schema_version !== "PolicyParityProof/v1" || proof.result !== "pass" ||
      proof.authority_effect !== "none") {
    return fail("POLICY_RELATION_PROOF_INVALID");
  }
  const composedFrom = array(proof.composed_from, "POLICY_RELATION_PROOF_INVALID");
  if (composedFrom.length !== POLICY_DIRECT_HANDLES.length) {
    return fail("POLICY_RELATION_PROOF_INVALID", "composed-from");
  }
  for (const [index, directHandle] of POLICY_DIRECT_HANDLES.entries()) {
    const direct = upstream[directHandle.node_id]!;
    const composed = object(composedFrom[index], "POLICY_RELATION_PROOF_INVALID");
    if (direct.node_id !== directHandle.node_id ||
        direct.provider_id !== directHandle.provider_id ||
        composed.node_id !== direct.node_id ||
        composed.provider_id !== direct.provider_id ||
        composed.semantic_sha256 !== direct.semantic_sha256) {
      return fail("POLICY_RELATION_PROOF_INVALID", directHandle.node_id);
    }
  }
  const owner = decodeMembershipOwner(rawInputs);
  const ownerRefs = object(proof.owner_refs, "POLICY_RELATION_CATALOGUE_MISMATCH");
  if (ownerRefs.catalogue_id !== owner.catalogue.catalogue_id ||
      ownerRefs.catalogue_sha256 !== owner.catalogue.catalogue_sha256 ||
      ownerRefs.catalogue_raw_sha256 !== owner.raw_sha256.catalogue) {
    return fail("POLICY_RELATION_CATALOGUE_MISMATCH");
  }
  const portable = object(proof.portable_projection, "POLICY_RELATION_PROOF_INVALID");
  const cases = array(portable.cases, "POLICY_RELATION_CASE_SET_MISMATCH");
  if (cases.length !== 5 || new Set(cases.map((value) =>
    string(object(value, "POLICY_RELATION_CASE_SET_MISMATCH").case_id,
      "POLICY_RELATION_CASE_SET_MISMATCH"))).size !== 5) {
    return fail("POLICY_RELATION_CASE_SET_MISMATCH");
  }
  const members = new Map(owner.catalogue.members.map((member) =>
    [member.strategy_id, member] as const));
  if ([...members.values()].some(({executable}) => executable !== false)) {
    return fail("POLICY_RELATION_CATALOGUE_MISMATCH", "executable-member");
  }
  const relations = cases.map((value) => {
    const observed = object(value, "POLICY_RELATION_CASE_SET_MISMATCH");
    const strategyId = string(
      observed.selected_strategy_id,
      "POLICY_RELATION_UNKNOWN_STRATEGY",
    );
    const member = members.get(strategyId);
    if (!member) return fail("POLICY_RELATION_UNKNOWN_STRATEGY", strategyId);
    return Object.freeze({
      relation: "selects_strategy" as const,
      case_id: string(observed.case_id, "POLICY_RELATION_CASE_SET_MISMATCH"),
      selector_definition_id: string(
        ownerRefs.definition_id,
        "POLICY_RELATION_PROOF_INVALID",
      ),
      strategy_id: member.strategy_id,
      catalogue_id: owner.catalogue.catalogue_id,
      member_executable: false as const,
    });
  });
  const covered = [...new Set(relations.map(({strategy_id: strategyId}) => strategyId))]
    .sort(compareUtf8);
  const expectedMembers = [...members.keys()].sort(compareUtf8);
  if (!same(covered, expectedMembers)) {
    return fail("POLICY_RELATION_COVERAGE_INCOMPLETE");
  }
  const nonExecution = array(
    proof.non_execution_by_language,
    "POLICY_RELATION_EXECUTION_OBSERVED",
  );
  if (nonExecution.length !== 3 || nonExecution.some((value) => {
    const item = object(value, "POLICY_RELATION_EXECUTION_OBSERVED");
    return item.attempt_count !== 0 || item.completion_count !== 0;
  })) return fail("POLICY_RELATION_EXECUTION_OBSERVED");
  const membershipEvaluations = covered.map((strategyId) => {
    const observation = mintStrategyMembershipObservationV1({
      schema_version: "StrategyMembershipObservation/v1",
      observation_id: `observation.relation-membership.${strategyId}/v1`,
      source_kind: "independent-owner-membership",
      catalogue_ref: {
        catalogue_id: owner.catalogue.catalogue_id,
        catalogue_sha256: owner.catalogue.catalogue_sha256,
      },
      strategy_id: strategyId,
      membership: "member",
      selection_claim: "none",
      execution_claim: "none",
      authority_effect: "none",
    });
    const evaluation = evaluateStrategyMembership({
      catalogue: owner.catalogue,
      denominator: owner.denominator,
      observation,
    });
    if (evaluation.verdict !== "pass" ||
        evaluation.positive_decision_accounting.declared !== 8 ||
        evaluation.positive_decision_accounting.passed !== 8) {
      return fail("POLICY_RELATION_MEMBERSHIP_PROOF_INVALID", strategyId);
    }
    return Object.freeze({strategy_id: strategyId, observation, evaluation});
  });
  const representative = membershipEvaluations[0]!;
  const membershipMutations = owner.mutationCatalogue.mutations.map((mutation) => {
    const evaluation = evaluateStrategyMembership(applyStrategyMembershipMutant({
      catalogue: owner.catalogue,
      denominator: owner.denominator,
      observation: representative.observation,
    }, mutation));
    const codes = evaluation.findings.map(({code}) => code);
    if (evaluation.verdict !== "fail" ||
        !mutation.expected_finding_codes.every((code) => codes.includes(code))) {
      return fail("POLICY_RELATION_MEMBERSHIP_PROOF_INVALID", mutation.mutation_id);
    }
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      status: "killed" as const,
      finding_codes: Object.freeze(codes),
    });
  });
  return Object.freeze({
    owner,
    relation_rows: Object.freeze(relations),
    membership_evaluations: Object.freeze(membershipEvaluations),
    membership_mutations: Object.freeze(membershipMutations),
  });
};

const relationHostiles = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const cases: readonly Readonly<{
    mutation_id: string;
    finding_code: PolicyJoinFindingCode;
    apply: () => void;
  }>[] = [
    {mutation_id: "policy-relation.missing-parity/v1",
      finding_code: "POLICY_RELATION_HANDLE_SET_MISMATCH", apply: () => {
        const value = clone(upstream) as Record<string, FactoryUpstreamResultV1>;
        delete value[POLICY_PARITY_HANDLE.node_id];
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.missing-direct/v1",
      finding_code: "POLICY_RELATION_HANDLE_SET_MISMATCH", apply: () => {
        const value = clone(upstream) as Record<string, FactoryUpstreamResultV1>;
        delete value[POLICY_DIRECT_HANDLES[0].node_id];
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.provider-drift/v1",
      finding_code: "POLICY_RELATION_PROVIDER_MISMATCH", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_PARITY_HANDLE.node_id].provider_id = "foreign-provider";
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.direct-handle-drift/v1",
      finding_code: "POLICY_RELATION_PROOF_INVALID", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_DIRECT_HANDLES[0].node_id].semantic_sha256 = "0".repeat(64);
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.proof-drift/v1",
      finding_code: "POLICY_RELATION_PROOF_INVALID", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_PARITY_HANDLE.node_id].semantic_output.proof.result = "fail";
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.catalogue-drift/v1",
      finding_code: "POLICY_RELATION_CATALOGUE_MISMATCH", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_PARITY_HANDLE.node_id]
          .semantic_output.proof.owner_refs.catalogue_sha256 = "0".repeat(64);
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.case-missing/v1",
      finding_code: "POLICY_RELATION_CASE_SET_MISMATCH", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_PARITY_HANDLE.node_id]
          .semantic_output.proof.portable_projection.cases.pop();
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.unknown-strategy/v1",
      finding_code: "POLICY_RELATION_UNKNOWN_STRATEGY", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_PARITY_HANDLE.node_id]
          .semantic_output.proof.portable_projection.cases[0]
          .selected_strategy_id = "settlement.route.unknown";
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.execution-attempt/v1",
      finding_code: "POLICY_RELATION_EXECUTION_OBSERVED", apply: () => {
        const value = clone(upstream) as any;
        value[POLICY_PARITY_HANDLE.node_id]
          .semantic_output.proof.non_execution_by_language[0].attempt_count = 1;
        evaluateRelation(value, rawInputs);
      }},
    {mutation_id: "policy-relation.stale-owner-input/v1",
      finding_code: "POLICY_JOIN_OWNER_INPUT_INVALID", apply: () =>
        evaluateRelation(upstream, {...rawInputs, catalogue: `${rawInputs.catalogue}\n`})},
  ];
  return Object.freeze(cases.map((testCase) => {
    try {
      testCase.apply();
      return fail("POLICY_RELATION_PROOF_INVALID", testCase.mutation_id);
    } catch (error: unknown) {
      if (!isObject(error) || error.code !== testCase.finding_code) throw error;
    }
    return Object.freeze({
      mutation_id: testCase.mutation_id,
      status: "killed" as const,
      finding_code: testCase.finding_code,
    });
  }));
};

export const provePolicySelectsStrategyRelation = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const evaluated = evaluateRelation(upstream, rawInputs);
  return Object.freeze({
    schema_version: "PolicySelectsStrategyProof/v1" as const,
    result: "pass" as const,
    composed_from: Object.freeze([
      ...POLICY_DIRECT_HANDLES.map((handle) => Object.freeze({
        node_id: handle.node_id,
        provider_id: handle.provider_id,
        semantic_sha256: upstream[handle.node_id]!.semantic_sha256,
      })),
      Object.freeze({
        node_id: POLICY_PARITY_HANDLE.node_id,
        provider_id: POLICY_PARITY_HANDLE.provider_id,
        semantic_sha256: upstream[POLICY_PARITY_HANDLE.node_id]!.semantic_sha256,
      }),
    ]),
    catalogue_ref: Object.freeze({
      catalogue_id: evaluated.owner.catalogue.catalogue_id,
      catalogue_sha256: evaluated.owner.catalogue.catalogue_sha256,
      raw_sha256: evaluated.owner.raw_sha256.catalogue,
    }),
    membership_denominator_ref: Object.freeze({
      denominator_id: evaluated.owner.denominator.denominator_id,
      denominator_sha256: evaluated.owner.denominator.denominator_sha256,
      raw_sha256: evaluated.owner.raw_sha256.membership_denominator,
    }),
    relation_rows: evaluated.relation_rows,
    membership_evaluations: evaluated.membership_evaluations,
    membership_mutations: evaluated.membership_mutations,
    obligations: Object.freeze(RELATION_OBLIGATIONS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: relationHostiles(upstream, rawInputs),
    claim_ceiling: "exact candidate-local selects_strategy relation from the proven five owner cases to current data-only members of one independently decoded membership denominator, with three 8/8 membership evaluations, 10/10 membership mutations, and preserved three-language zero-execution evidence; not strategy execution correctness, business-routing correctness, promotion, publication, release, deployment, or production readiness",
    authority_effect: "none" as const,
  });
};
