import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {
  canonicalReadModelQueryJson,
  decodeReadModelQueryDefinitionV1,
  decodeReadModelQueryDenominatorV1,
  decodeReadModelQueryMutationCatalogueV1,
  decodeReadModelQueryObservationV1,
  sha256ReadModelQueryBytes,
  sha256ReadModelQueryValue,
} from "../../families/read-model/index.js";
import {
  DECLARED_READ_LIFECYCLE_PATHS,
  EFFECT_CHANNELS,
} from "../../kernel/evidence/effect-observation/index.js";

type JsonObject = Record<string, unknown>;

export const QUERY_DIRECT_HANDLES = Object.freeze([
  Object.freeze({
    node_id: "query.typescript.complete-settlement",
    provider_id: "typescript-query-v1",
    language: "typescript",
    proof_schema: "TypeScriptQueryProof/v1",
    target_id: "query.typescript.complete-settlement/v1",
    protocol_id: "typescript.bound-query/v1",
    binding_id: "typescript.complete-settlement.bound-query/v1",
  }),
  Object.freeze({
    node_id: "query.python.complete-settlement",
    provider_id: "python-query-v1",
    language: "python",
    proof_schema: "PythonQueryProof/v1",
    target_id: "query.python.complete-settlement/v1",
    protocol_id: "python.bound-query/v1",
    binding_id: "python.complete-settlement.bound-query/v1",
  }),
  Object.freeze({
    node_id: "query.rust.complete-settlement",
    provider_id: "rust-query-v1",
    language: "rust",
    proof_schema: "RustQueryProof/v1",
    target_id: "query.rust.complete-settlement/v1",
    protocol_id: "rust.bound-query/v1",
    binding_id: "rust.complete-settlement.bound-query/v1",
  }),
] as const);

const OBLIGATION_IDS = Object.freeze([
  "exact-direct-handle-set",
  "exact-provider-target-language-protocol-schema",
  "shared-owner-definition",
  "shared-descriptor-denominator-and-mutation-catalogue",
  "exact-owner-success-case-and-input",
  "exact-closed-output-shape-and-value",
  "exact-ordered-declared-read-trace",
  "complete-twelve-channel-perimeter",
  "exact-declared-reads-and-zero-forbidden-effects",
  "complete-seven-path-lifecycle",
  "complete-consumption-no-alias-and-quiescence",
  "independent-observer-and-provider-binding",
  "family-four-of-four",
  "native-evidence-retained",
  "portable-three-target-equality",
  "authority-effect-none",
] as const);

export type QueryParityFindingCode =
  | "QUERY_PARITY_HANDLE_SET_MISMATCH"
  | "QUERY_PARITY_PROVIDER_MISMATCH"
  | "QUERY_PARITY_PROOF_INVALID"
  | "QUERY_PARITY_TARGET_MISMATCH"
  | "QUERY_PARITY_OWNER_MATERIAL_INVALID"
  | "QUERY_PARITY_RESULT_INVALID"
  | "QUERY_PARITY_READ_LEDGER_INVALID"
  | "QUERY_PARITY_EFFECT_PERIMETER_INVALID"
  | "QUERY_PARITY_EFFECT_OBSERVED"
  | "QUERY_PARITY_LIFECYCLE_INVALID"
  | "QUERY_PARITY_OBSERVER_INVALID"
  | "QUERY_PARITY_FAMILY_INVALID"
  | "QUERY_PARITY_NATIVE_EVIDENCE_MISSING"
  | "QUERY_PARITY_PORTABLE_DRIFT"
  | "QUERY_PARITY_RAW_INPUT_INVALID";

type Handle = (typeof QUERY_DIRECT_HANDLES)[number];
type DirectProjection = Readonly<{
  handle: Handle;
  semantic_sha256: string;
  portable: JsonObject;
  native_evidence: JsonObject;
}>;

export type QueryParityProofV1 = Readonly<{
  schema_version: "QueryParityProof/v1";
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
    finding_code: QueryParityFindingCode;
  }>[];
  claim_ceiling: string;
  authority_effect: "none";
}>;

const DEFINITION_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/definition.json";
const DESCRIPTOR_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/query/cross-language-realization-descriptor.json";

const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: QueryParityFindingCode, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`), {
    code,
  });
};
const object = (value: unknown, code: QueryParityFindingCode): JsonObject =>
  isObject(value) ? value : fail(code);
const array = (value: unknown, code: QueryParityFindingCode): unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = (value: unknown, code: QueryParityFindingCode): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const sha256String = (value: unknown, code: QueryParityFindingCode): string => {
  const digest = string(value, code);
  return /^[a-f0-9]{64}$/u.test(digest) ? digest : fail(code);
};
const same = (left: unknown, right: unknown): boolean =>
  canonicalReadModelQueryJson(left) === canonicalReadModelQueryJson(right);
const parseObject = (raw: string | undefined): JsonObject => {
  if (raw === undefined) return fail("QUERY_PARITY_RAW_INPUT_INVALID");
  try {
    return object(JSON.parse(raw), "QUERY_PARITY_RAW_INPUT_INVALID");
  } catch {
    return fail("QUERY_PARITY_RAW_INPUT_INVALID");
  }
};

const decodeOwnerInputs = (rawInputs: Readonly<Record<string, string>>) => {
  if (!same(Object.keys(rawInputs), [
    "definition", "denominator", "mutations", "descriptor",
  ])) return fail("QUERY_PARITY_RAW_INPUT_INVALID", "roles");
  const descriptor = parseObject(rawInputs.descriptor);
  try {
    const definition = decodeReadModelQueryDefinitionV1(
      rawInputs.definition!,
      DESCRIPTOR_PATH,
      rawInputs.descriptor!,
    );
    const denominator = decodeReadModelQueryDenominatorV1(
      rawInputs.denominator!,
      rawInputs.definition!,
      definition,
      DEFINITION_PATH,
    );
    const mutations = decodeReadModelQueryMutationCatalogueV1(
      rawInputs.mutations!,
      denominator,
    );
    if (descriptor.schema_version !==
        "domainspec.query-cross-language-realization-descriptor/v1" ||
        descriptor.descriptor_id !== definition.descriptor_ref.descriptor_id ||
        descriptor.authority_effect !== "none" ||
        definition.cases.length !== 1 ||
        definition.read_targets.length !== 2 ||
        definition.output_concept.fields.length !== 5 ||
        denominator.positive_decisions.length !== 4 ||
        mutations.mutations.length !== 7) {
      return fail("QUERY_PARITY_RAW_INPUT_INVALID", "owner-shape");
    }
    return Object.freeze({
      definition,
      denominator,
      mutations,
      descriptor,
      definition_sha256: sha256ReadModelQueryBytes(rawInputs.definition!),
      descriptor_sha256: sha256ReadModelQueryBytes(rawInputs.descriptor!),
    });
  } catch (error: unknown) {
    if (isObject(error) && typeof error.code === "string" &&
        String(error.code).startsWith("QUERY_PARITY_")) throw error;
    return fail("QUERY_PARITY_RAW_INPUT_INVALID",
      error instanceof Error ? error.message : String(error));
  }
};

const exactNativeEvidence = (
  proof: JsonObject,
  handle: Handle,
): JsonObject => {
  const processEvidence = object(
    handle.language === "python"
      ? proof.native_process_evidence
      : proof.process_evidence,
    "QUERY_PARITY_NATIVE_EVIDENCE_MISSING",
  );
  if (processEvidence.executions !== 2 ||
      processEvidence.distinct_pids !== 2 ||
      sha256String(processEvidence.trace_sha256,
        "QUERY_PARITY_NATIVE_EVIDENCE_MISSING") === "" ||
      sha256String(processEvidence.result_sha256,
        "QUERY_PARITY_NATIVE_EVIDENCE_MISSING") === "") {
    return fail("QUERY_PARITY_NATIVE_EVIDENCE_MISSING", handle.language);
  }
  const sourceHostiles = array(proof.source_hostiles,
    "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  const familyControls = array(proof.predecessor_family_controls,
    "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  const hostileIds = sourceHostiles.map((value) => {
    const hostile = object(value, "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
    if (hostile.status !== "killed") {
      return fail("QUERY_PARITY_NATIVE_EVIDENCE_MISSING", handle.language);
    }
    return string(hostile.hostile_id, "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  });
  const controlIds = familyControls.map((value) => {
    const control = object(value, "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
    const variants = array(control.variants,
      "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
    if (variants.length === 0 || variants.some((variant) =>
      object(variant, "QUERY_PARITY_NATIVE_EVIDENCE_MISSING").status !==
        "killed")) {
      return fail("QUERY_PARITY_NATIVE_EVIDENCE_MISSING", handle.language);
    }
    return string(control.mutation_id,
      "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  });
  if (sourceHostiles.length !== 8 || new Set(hostileIds).size !== 8 ||
      familyControls.length !== 7 || new Set(controlIds).size !== 7 ||
      ("semantic_replay_equal" in processEvidence &&
        processEvidence.semantic_replay_equal !== true) ||
      ("pids_redacted_from_semantic_proof" in processEvidence &&
        processEvidence.pids_redacted_from_semantic_proof !== true)) {
    return fail("QUERY_PARITY_NATIVE_EVIDENCE_MISSING", handle.language);
  }
  const closedSubset = handle.language === "python"
    ? null
    : object(proof.closed_subset, "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  return Object.freeze({
    process_evidence: processEvidence,
    closed_subset: closedSubset,
    source_hostiles: Object.freeze(sourceHostiles),
    predecessor_family_controls: Object.freeze(familyControls),
  });
};

const projectDirect = (
  upstream: FactoryUpstreamResultV1,
  handle: Handle,
  owner: ReturnType<typeof decodeOwnerInputs>,
): DirectProjection => {
  if (upstream.node_id !== handle.node_id ||
      upstream.provider_id !== handle.provider_id) {
    return fail("QUERY_PARITY_PROVIDER_MISMATCH", handle.node_id);
  }
  const semanticSha256 = sha256String(upstream.semantic_sha256,
    "QUERY_PARITY_PROOF_INVALID");
  const output = object(upstream.semantic_output, "QUERY_PARITY_PROOF_INVALID");
  const proof = object(output.proof, "QUERY_PARITY_PROOF_INVALID");
  if (proof.schema_version !== handle.proof_schema ||
      proof.authority_effect !== "none") {
    return fail("QUERY_PARITY_PROOF_INVALID", handle.language);
  }
  const target = object(proof.target, "QUERY_PARITY_TARGET_MISMATCH");
  if (target.target_id !== handle.target_id ||
      target.language !== handle.language ||
      target.protocol_id !== handle.protocol_id ||
      target.output_concept_id !== owner.definition.output_concept.concept_id ||
      !/^[a-f0-9]{64}$/u.test(String(target.target_sha256))) {
    return fail("QUERY_PARITY_TARGET_MISMATCH", handle.language);
  }
  const binding = object(proof.binding, "QUERY_PARITY_PROOF_INVALID");
  if (binding.binding_id !== handle.binding_id ||
      !/^[a-f0-9]{64}$/u.test(String(binding.binding_sha256))) {
    return fail("QUERY_PARITY_PROOF_INVALID", `${handle.language}:binding`);
  }
  const observation = object(proof.observation, "QUERY_PARITY_PROOF_INVALID");
  const observationTarget = object(observation.target,
    "QUERY_PARITY_TARGET_MISMATCH");
  const definitionRef = object(observation.definition_ref,
    "QUERY_PARITY_OWNER_MATERIAL_INVALID");
  const observationBinding = object(observation.binding,
    "QUERY_PARITY_OWNER_MATERIAL_INVALID");
  if (observation.schema_version !== "ReadModelQueryObservation/v1" ||
      observation.source_kind !== "target-observation" ||
      observation.authority_effect !== "none" ||
      !same(observationTarget, {
        target_id: handle.target_id,
        target_sha256: target.target_sha256,
        language: handle.language,
        protocol_id: handle.protocol_id,
      })) {
    return fail("QUERY_PARITY_TARGET_MISMATCH", `${handle.language}:observation`);
  }
  if (definitionRef.definition_id !== owner.definition.definition_id ||
      definitionRef.path !== DEFINITION_PATH ||
      definitionRef.sha256 !== owner.definition_sha256 ||
      observationBinding.descriptor_id !== owner.definition.descriptor_ref.descriptor_id ||
      observationBinding.descriptor_sha256 !== owner.descriptor_sha256 ||
      observationBinding.provider_id !== handle.provider_id ||
      !/^[a-f0-9]{64}$/u.test(String(observationBinding.provider_sha256))) {
    return fail("QUERY_PARITY_OWNER_MATERIAL_INVALID", handle.language);
  }
  const ownerCase = owner.definition.cases[0]!;
  const observedResult = object(observation.observed_result,
    "QUERY_PARITY_RESULT_INVALID");
  const result = object(observedResult.result, "QUERY_PARITY_RESULT_INVALID");
  const expectedFields = owner.definition.output_concept.fields.map(({name}) => name);
  if (observedResult.case_id !== ownerCase.case_id ||
      observedResult.input_sha256 !== sha256ReadModelQueryValue(ownerCase.inputs) ||
      observedResult.declared_failure !== null ||
      !same([...Object.keys(result)].sort(), [...expectedFields].sort()) ||
      !same(result, ownerCase.expected_result) ||
      observedResult.result_sha256 !== sha256ReadModelQueryValue(result)) {
    return fail("QUERY_PARITY_RESULT_INVALID", handle.language);
  }
  const lifecycle = object(observation.read_lifecycle_observation,
    "QUERY_PARITY_LIFECYCLE_INVALID");
  const attempts = array(lifecycle.declared_read_attempts,
    "QUERY_PARITY_READ_LEDGER_INVALID");
  if (attempts.length !== owner.definition.read_targets.length) {
    return fail("QUERY_PARITY_READ_LEDGER_INVALID", handle.language);
  }
  const portableAttempts = owner.definition.read_targets.map((expected, index) => {
    const observed = object(attempts[index], "QUERY_PARITY_READ_LEDGER_INVALID");
    if (observed.ordinal !== index || observed.target_id !== expected.target_id ||
        observed.channel !== expected.channel || observed.outcome !== "success" ||
        !DECLARED_READ_LIFECYCLE_PATHS.includes(
          observed.lifecycle_path as (typeof DECLARED_READ_LIFECYCLE_PATHS)[number],
        )) {
      return fail("QUERY_PARITY_READ_LEDGER_INVALID", `${handle.language}:${index}`);
    }
    return Object.freeze({
      ordinal: index,
      target_id: expected.target_id,
      channel: expected.channel,
      outcome: "success" as const,
    });
  });
  const lifecyclePaths = array(lifecycle.lifecycle_paths,
    "QUERY_PARITY_LIFECYCLE_INVALID");
  if (lifecyclePaths.length !== DECLARED_READ_LIFECYCLE_PATHS.length) {
    return fail("QUERY_PARITY_LIFECYCLE_INVALID", handle.language);
  }
  const portableLifecycle = DECLARED_READ_LIFECYCLE_PATHS.map((path, index) => {
    const observed = object(lifecyclePaths[index],
      "QUERY_PARITY_LIFECYCLE_INVALID");
    if (observed.lifecycle_path !== path || observed.coverage !== "supported") {
      return fail("QUERY_PARITY_LIFECYCLE_INVALID", `${handle.language}:${path}`);
    }
    return Object.freeze({lifecycle_path: path, coverage: "supported" as const});
  });
  if (lifecycle.source_support !== "supported-static" ||
      lifecycle.write_then_restore_observed !== false ||
      lifecycle.authority_effect !== "none") {
    return fail(lifecycle.write_then_restore_observed === true
      ? "QUERY_PARITY_EFFECT_OBSERVED"
      : "QUERY_PARITY_LIFECYCLE_INVALID", handle.language);
  }
  const effect = object(lifecycle.effect_observation,
    "QUERY_PARITY_EFFECT_PERIMETER_INVALID");
  const channels = array(effect.channels,
    "QUERY_PARITY_EFFECT_PERIMETER_INVALID");
  if (channels.length !== EFFECT_CHANNELS.length) {
    return fail("QUERY_PARITY_EFFECT_PERIMETER_INVALID", handle.language);
  }
  const portableChannels = EFFECT_CHANNELS.map((channel, index) => {
    const observed = object(channels[index],
      "QUERY_PARITY_EFFECT_PERIMETER_INVALID");
    const expectedReads = channel === "filesystem" ? 2 : 0;
    if (observed.channel !== channel || observed.coverage !== "supported") {
      return fail("QUERY_PARITY_EFFECT_PERIMETER_INVALID",
        `${handle.language}:${channel}`);
    }
    if (observed.read_count !== expectedReads || observed.write_count !== 0 ||
        observed.escape_count !== 0 || observed.deferred_count !== 0) {
      return fail("QUERY_PARITY_EFFECT_OBSERVED", `${handle.language}:${channel}`);
    }
    return Object.freeze({
      channel,
      coverage: "supported" as const,
      read_count: expectedReads,
      write_count: 0,
      escape_count: 0,
      deferred_count: 0,
    });
  });
  const observer = object(lifecycle.observer_ref,
    "QUERY_PARITY_OBSERVER_INVALID");
  const effectObserver = object(effect.observer_ref,
    "QUERY_PARITY_OBSERVER_INVALID");
  const lifecycleTarget = object(lifecycle.target_ref,
    "QUERY_PARITY_TARGET_MISMATCH");
  const effectTarget = object(effect.target_ref,
    "QUERY_PARITY_TARGET_MISMATCH");
  if (!same(observer, effectObserver) ||
      observer.role !== "independent-effect-observer" ||
      observer.owner_ref === handle.provider_id ||
      observer.provider_id !== handle.provider_id ||
      observer.provider_sha256 !== observationBinding.provider_sha256 ||
      !/^[a-f0-9]{64}$/u.test(String(observer.observer_sha256)) ||
      !same(lifecycleTarget, {
        target_id: handle.target_id,
        target_sha256: target.target_sha256,
      }) || !same(effectTarget, lifecycleTarget)) {
    return fail("QUERY_PARITY_OBSERVER_INVALID", handle.language);
  }
  const effectResult = object(effect.result, "QUERY_PARITY_LIFECYCLE_INVALID");
  const quiescence = object(effect.quiescence,
    "QUERY_PARITY_LIFECYCLE_INVALID");
  if (effectResult.consumption !== "complete" ||
      effectResult.mutable_alias_observed !== false ||
      quiescence.observed !== true || quiescence.pending_count !== 0) {
    return fail("QUERY_PARITY_LIFECYCLE_INVALID", handle.language);
  }
  const family = object(proof.family_evaluation, "QUERY_PARITY_FAMILY_INVALID");
  const accounting = object(family.positive_decision_accounting,
    "QUERY_PARITY_FAMILY_INVALID");
  const familyDenominator = object(family.denominator_ref,
    "QUERY_PARITY_FAMILY_INVALID");
  const familyObservation = object(family.observation_ref,
    "QUERY_PARITY_FAMILY_INVALID");
  if (family.verdict !== "pass" || family.authority_effect !== "none" ||
      family.portable_claim !==
        "owner-bound-exact-read-model-under-declared-observed-lifecycle" ||
      familyDenominator.denominator_id !== owner.denominator.denominator_id ||
      familyDenominator.denominator_sha256 !== owner.denominator.denominator_sha256 ||
      familyObservation.observation_id !== observation.observation_id ||
      familyObservation.observation_sha256 !== observation.observation_sha256 ||
      accounting.declared !== 4 || accounting.passed !== 4 ||
      accounting.failed !== 0 || accounting.unaccounted !== 0) {
    return fail("QUERY_PARITY_FAMILY_INVALID", handle.language);
  }
  const proofAccounting = object(proof.accounting, "QUERY_PARITY_FAMILY_INVALID");
  const positives = object(proofAccounting.positives,
    "QUERY_PARITY_FAMILY_INVALID");
  const sourceHostileAccounting = object(proofAccounting.source_hostiles,
    "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  const familyControlAccounting = object(proofAccounting.predecessor_family_controls,
    "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  if (positives.declared !== 4 || positives.passed !== 4 ||
      sourceHostileAccounting.declared !== 8 ||
      sourceHostileAccounting.killed !== 8 ||
      familyControlAccounting.declared_classes !== 7 ||
      familyControlAccounting.killed_classes !== 7) {
    return fail("QUERY_PARITY_FAMILY_INVALID", `${handle.language}:accounting`);
  }
  const nativeEvidence = exactNativeEvidence(proof, handle);
  const nativeProcess = object(nativeEvidence.process_evidence,
    "QUERY_PARITY_NATIVE_EVIDENCE_MISSING");
  const nativeTraceProjection = portableAttempts.map(({
    target_id: targetId,
    channel,
    outcome,
  }) => ({target_id: targetId, channel, outcome}));
  if (nativeProcess.trace_sha256 !==
        sha256ReadModelQueryValue(nativeTraceProjection) ||
      nativeProcess.result_sha256 !== sha256ReadModelQueryValue(result)) {
    return fail("QUERY_PARITY_NATIVE_EVIDENCE_MISSING",
      `${handle.language}:digest-binding`);
  }
  try {
    decodeReadModelQueryObservationV1(canonicalReadModelQueryJson(observation));
  } catch (error: unknown) {
    return fail("QUERY_PARITY_PROOF_INVALID",
      error instanceof Error ? error.message : String(error));
  }
  const portable = Object.freeze({
    definition_id: owner.definition.definition_id,
    definition_sha256: owner.definition_sha256,
    descriptor_id: owner.definition.descriptor_ref.descriptor_id,
    descriptor_sha256: owner.descriptor_sha256,
    case_id: ownerCase.case_id,
    input_sha256: sha256ReadModelQueryValue(ownerCase.inputs),
    output_concept_id: owner.definition.output_concept.concept_id,
    result: Object.freeze({...result}),
    result_sha256: sha256ReadModelQueryValue(result),
    read_attempts: Object.freeze(portableAttempts),
    effect_channels: Object.freeze(portableChannels),
    lifecycle_paths: Object.freeze(portableLifecycle),
    result_consumption: Object.freeze({
      consumption: "complete" as const,
      mutable_alias_observed: false,
    }),
    quiescence: Object.freeze({observed: true, pending_count: 0}),
    family: Object.freeze({
      verdict: "pass" as const,
      positive_decisions: Object.freeze({declared: 4, passed: 4}),
    }),
    authority_effect: "none" as const,
  });
  return Object.freeze({
    handle,
    semantic_sha256: semanticSha256,
    portable,
    native_evidence: nativeEvidence,
  });
};

export const evaluateQueryParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
) => {
  const expectedKeys = QUERY_DIRECT_HANDLES.map(({node_id: nodeId}) => nodeId);
  if (!same(Object.keys(upstream), expectedKeys)) {
    return fail("QUERY_PARITY_HANDLE_SET_MISMATCH");
  }
  const owner = decodeOwnerInputs(rawInputs);
  const direct = QUERY_DIRECT_HANDLES.map((handle) =>
    projectDirect(upstream[handle.node_id]!, handle, owner));
  const reference = direct[0]!.portable;
  for (const projection of direct.slice(1)) {
    if (!same(projection.portable, reference)) {
      return fail("QUERY_PARITY_PORTABLE_DRIFT", projection.handle.language);
    }
  }
  return Object.freeze({owner, direct, portable_projection: reference});
};

const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const directProof = (upstream: any, index = 0): any =>
  upstream[QUERY_DIRECT_HANDLES[index]!.node_id].semantic_output.proof;

const hostileCases = Object.freeze([
  Object.freeze({mutation_id: "join/missing-handle", finding: "QUERY_PARITY_HANDLE_SET_MISMATCH", apply: (u: any) => { delete u[QUERY_DIRECT_HANDLES[0].node_id]; }}),
  Object.freeze({mutation_id: "join/wrong-provider", finding: "QUERY_PARITY_PROVIDER_MISMATCH", apply: (u: any) => { u[QUERY_DIRECT_HANDLES[0].node_id].provider_id = "wrong-provider"; }}),
  Object.freeze({mutation_id: "join/proof-schema", finding: "QUERY_PARITY_PROOF_INVALID", apply: (u: any) => { directProof(u).schema_version = "WrongProof/v1"; }}),
  Object.freeze({mutation_id: "join/wrong-target", finding: "QUERY_PARITY_TARGET_MISMATCH", apply: (u: any) => { directProof(u).target.target_id = "wrong-target"; }}),
  Object.freeze({mutation_id: "join/wrong-protocol", finding: "QUERY_PARITY_TARGET_MISMATCH", apply: (u: any) => { directProof(u).target.protocol_id = "wrong-protocol/v1"; }}),
  Object.freeze({mutation_id: "join/stale-owner-material", finding: "QUERY_PARITY_OWNER_MATERIAL_INVALID", apply: (u: any) => { directProof(u).observation.definition_ref.sha256 = "0".repeat(64); }}),
  Object.freeze({mutation_id: "join/totals-only", finding: "QUERY_PARITY_PROOF_INVALID", apply: (u: any) => { u[QUERY_DIRECT_HANDLES[0].node_id].semantic_output = {accounting: {positives_declared: 100, positives_passed: 100}}; }}),
  Object.freeze({mutation_id: "join/result-shape", finding: "QUERY_PARITY_RESULT_INVALID", apply: (u: any) => { directProof(u).observation.observed_result.result.extra = "leak"; }}),
  Object.freeze({mutation_id: "join/result-value", finding: "QUERY_PARITY_RESULT_INVALID", apply: (u: any) => { directProof(u).observation.observed_result.result.payout_status = "wrong"; }}),
  Object.freeze({mutation_id: "join/swapped-reads", finding: "QUERY_PARITY_READ_LEDGER_INVALID", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.declared_read_attempts.reverse(); }}),
  Object.freeze({mutation_id: "join/duplicate-read", finding: "QUERY_PARITY_READ_LEDGER_INVALID", apply: (u: any) => { const a = directProof(u).observation.read_lifecycle_observation.declared_read_attempts; a[1] = clone(a[0]); }}),
  Object.freeze({mutation_id: "join/undeclared-read", finding: "QUERY_PARITY_READ_LEDGER_INVALID", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.declared_read_attempts[1].target_id = "settlement.read.undeclared"; }}),
  Object.freeze({mutation_id: "join/missing-channel", finding: "QUERY_PARITY_EFFECT_PERIMETER_INVALID", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.effect_observation.channels.pop(); }}),
  Object.freeze({mutation_id: "join/unsupported-channel", finding: "QUERY_PARITY_EFFECT_PERIMETER_INVALID", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.effect_observation.channels[0].coverage = "unsupported"; }}),
  Object.freeze({mutation_id: "join/hidden-write", finding: "QUERY_PARITY_EFFECT_OBSERVED", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.effect_observation.channels[3].write_count = 1; }}),
  Object.freeze({mutation_id: "join/write-then-restore", finding: "QUERY_PARITY_EFFECT_OBSERVED", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.write_then_restore_observed = true; }}),
  Object.freeze({mutation_id: "join/deferred-effect", finding: "QUERY_PARITY_EFFECT_OBSERVED", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.effect_observation.channels[7].deferred_count = 1; }}),
  Object.freeze({mutation_id: "join/missing-lifecycle", finding: "QUERY_PARITY_LIFECYCLE_INVALID", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.lifecycle_paths.pop(); }}),
  Object.freeze({mutation_id: "join/unsupported-lifecycle", finding: "QUERY_PARITY_LIFECYCLE_INVALID", apply: (u: any) => { directProof(u).observation.read_lifecycle_observation.lifecycle_paths[0].coverage = "unsupported"; }}),
  Object.freeze({mutation_id: "join/native-evidence-erased", finding: "QUERY_PARITY_NATIVE_EVIDENCE_MISSING", apply: (u: any) => { delete directProof(u).closed_subset; }}),
] as const);

export const proveQueryParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  rawInputs: Readonly<Record<string, string>>,
): QueryParityProofV1 => {
  const evaluated = evaluateQueryParity(upstream, rawInputs);
  const hostileMutations = hostileCases.map(({mutation_id: mutationId, finding, apply}) => {
    const mutated = clone(upstream);
    apply(mutated);
    try {
      evaluateQueryParity(mutated, rawInputs);
    } catch (error: unknown) {
      const code = isObject(error) ? error.code : undefined;
      if (code === finding) return Object.freeze({
        mutation_id: mutationId,
        status: "killed" as const,
        finding_code: finding as QueryParityFindingCode,
      });
      throw error;
    }
    return fail("QUERY_PARITY_PORTABLE_DRIFT", `mutant-survived:${mutationId}`);
  });
  return Object.freeze({
    schema_version: "QueryParityProof/v1" as const,
    result: "pass" as const,
    composed_from: Object.freeze(evaluated.direct.map(({handle, semantic_sha256}) =>
      Object.freeze({
        node_id: handle.node_id,
        provider_id: handle.provider_id,
        semantic_sha256,
        target_id: handle.target_id,
        language: handle.language,
        protocol_id: handle.protocol_id,
      }))),
    owner_refs: Object.freeze({
      definition_id: evaluated.owner.definition.definition_id,
      definition_sha256: evaluated.owner.definition_sha256,
      denominator_id: evaluated.owner.denominator.denominator_id,
      denominator_sha256: evaluated.owner.denominator.denominator_sha256,
      descriptor_id: string(evaluated.owner.descriptor.descriptor_id,
        "QUERY_PARITY_RAW_INPUT_INVALID"),
      descriptor_sha256: evaluated.owner.descriptor_sha256,
      mutation_catalogue_sha256: evaluated.owner.mutations.catalogue_sha256,
    }),
    portable_projection: evaluated.portable_projection,
    native_evidence_by_language: Object.freeze(evaluated.direct.map(
      ({handle, native_evidence: evidence}) => Object.freeze({
        language: handle.language,
        evidence,
      }),
    )),
    obligations: Object.freeze(OBLIGATION_IDS.map((obligationId) =>
      Object.freeze({obligation_id: obligationId, status: "passed" as const}))),
    hostile_mutations: Object.freeze(hostileMutations),
    claim_ceiling: "same-host same-oracle portable Query parity for the exact owner-authored inert complete-settlement success fixture across the exact locked TypeScript, Python, and Rust handles; exact target, result, ordered read, complete lifecycle, zero forbidden effect, and quiescence evidence are compared while native mechanisms and direct source-hostile evidence are retained separately; this is not arbitrary-language equivalence, failure-path or business correctness beyond the fixture, universal runtime or operating-system interception, candidate projection, promotion, publication, release, deployment, or production",
    authority_effect: "none" as const,
  });
};
