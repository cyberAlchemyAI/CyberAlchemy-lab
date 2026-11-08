import {createHash} from "node:crypto";

import {OPERATION_EXPECTED_DIAGNOSTIC} from
  "../../../../families/state-changing-action/contracts/state-changing-action-contracts.js";

type JsonObject = Record<string, unknown>;
type Language = "typescript" | "python" | "rust";

const LANGUAGES = Object.freeze([
  "typescript", "python", "rust",
] as const);
const PROVIDERS = Object.freeze({
  typescript: Object.freeze({
    provider_id: "operation-typescript-v1",
    proof_schema: "TypeScriptOperationComposedProof/v1",
    semantic_output_keys: Object.freeze(["proof"]),
    proof_native_keys: Object.freeze([
      "closed_subset_proof", "runtime_proof",
    ]),
    target_id: "operation.typescript.complete-settlement/v1",
    protocol_id: "typescript.bound-operation/v1",
    symbol_name: "completeSettlementOperation",
    observer_id: "observer.typescript-operation-ports/v1",
    binding_id: "typescript.complete-settlement.bound-operation/v1",
    bound_role_count: 34,
    evidence_sha256:
      "f0657f7e5e457ff4d7d9e00ef5c36b6dca139a01e0d19c197bf69778c46363bf",
  }),
  python: Object.freeze({
    provider_id: "operation-python-v1",
    proof_schema: "PythonOperationComposedProof/v1",
    semantic_output_keys: Object.freeze(["proof", "workspace"]),
    proof_native_keys: Object.freeze(["native_process_evidence"]),
    target_id: "operation.python.complete-settlement/v1",
    protocol_id: "python.bound-operation/v1",
    symbol_name: "complete_settlement_operation",
    observer_id: "observer.python-operation-ports/v1",
    binding_id: "python.complete-settlement.bound-operation/v1",
    bound_role_count: 35,
    evidence_sha256:
      "6bd050443eaffa162811b4a46100ac76fa4600d89cfb99701247697eba325297",
  }),
  rust: Object.freeze({
    provider_id: "operation-rust-v1",
    proof_schema: "RustOperationComposedProof/v1",
    semantic_output_keys: Object.freeze(["proof", "workspace"]),
    proof_native_keys: Object.freeze([
      "closed_subset_proof", "runtime_proof",
    ]),
    target_id: "operation.rust.complete-settlement/v1",
    protocol_id: "rust.bound-operation/v1",
    symbol_name: "COMPLETE_SETTLEMENT_OPERATION",
    observer_id: "observer.rust-operation-ports/v1",
    binding_id: "rust.complete-settlement.bound-operation/v1",
    bound_role_count: 34,
    evidence_sha256:
      "f31f56e5f2a158b153b572bd5e0eccc8c9f806679ad323cec29cdc0ad17495ac",
  }),
} as const);
const SOURCE_CODES = Object.freeze([
  "RMT_OP_UNDECLARED_WRITE",
  "RMT_OP_UNDECLARED_EFFECT",
  "RMT_OP_GUARD_BYPASS",
  "RMT_OP_ORDER_SWAP",
  "RMT_OP_ATOMICITY_REMOVED",
  "RMT_OP_SUCCESS_FAILURE_COLLAPSE",
  "RMT_OP_EMITTED_BEFORE_COMMIT",
  "RMT_OP_CONTINUATION_MISMATCH",
  "RMT_OP_READ_SET_DRIFT",
  "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM",
] as const);
const FAMILY_HOSTILES = Object.freeze([
  "op/undeclared-write",
  "op/undeclared-effect",
  "op/guard-bypass",
  "op/order-swap",
  "op/atomicity-removed",
  "op/success-failure-collapse",
  "op/emitted-before-commit",
  "op/continuation-mismatch",
  "op/read-set-drift",
  "op/output-contract-overclaim",
  "op/relation-owner-evidence-stale",
  "op/relation-source-endpoint-mismatch",
  "op/relation-target-endpoint-mismatch",
  "op/materialized-without-exact-assertion",
  "s1/before-state-write-failure",
  "s1/between-state-and-outbox-failure",
  "s1/missing-member",
  "s1/mixed-commit",
  "s1/rollback-after-commit",
] as const);
const RELATION_ASSERTIONS = Object.freeze([
  Object.freeze({
    contract_id: "op/enforced-by-to-guards",
    architecture_relation_id: "architecture.guards",
    source_type: "architecture.RuleImplementation",
    target_type: "architecture.OperationImplementation",
    assertion_owner: "source Rule candidate",
    owner_evidence_sha256: "a".repeat(64),
    exact_assertion: true,
  }),
  Object.freeze({
    contract_id: "op/exposed-by-to-exposes",
    architecture_relation_id: "architecture.exposes",
    source_type: "architecture.InterfaceImplementation",
    target_type: "architecture.OperationImplementation",
    assertion_owner: "source Interface candidate",
    owner_evidence_sha256: "b".repeat(64),
    exact_assertion: true,
  }),
  Object.freeze({
    contract_id: "op/emitted-events-to-emits",
    architecture_relation_id: "architecture.emits",
    source_type: "architecture.OperationImplementation",
    target_type: "architecture.EventImplementation",
    assertion_owner: "source Operation candidate",
    owner_evidence_sha256: "c".repeat(64),
    exact_assertion: true,
  }),
  Object.freeze({
    contract_id: "op/workflow-step-to-binds-step",
    architecture_relation_id: "architecture.binds_step",
    source_type: "architecture.WorkflowStepContract",
    target_type: "architecture.OperationImplementation",
    assertion_owner: "Workflow candidate owning the step assertion",
    owner_evidence_sha256: "d".repeat(64),
    exact_assertion: true,
  }),
] as const);
const OBSERVATION_KEYS = Object.freeze([
  "schema_version", "observation_id", "case_id", "source_kind",
  "definition_ref", "denominator_ref", "observer", "operation_id",
  "transition_started", "inputs", "read_attempts", "write_attempts",
  "external_effect_attempts", "guard_evaluations", "trace", "atomicity",
  "outcome", "emitted_events", "continuation", "relation_assertions",
  "authority_effect", "observation_sha256",
]);
const PORTABLE_OBSERVATION_KEYS = Object.freeze([
  "schema_version", "case_id", "definition_ref", "denominator_ref",
  "operation_id", "transition_started", "inputs", "read_attempts",
  "write_attempts", "external_effect_attempts", "guard_evaluations",
  "trace", "atomicity", "outcome", "emitted_events", "continuation",
  "relation_assertions", "authority_effect",
] as const);
const SHA256 = /^[a-f0-9]{64}$/u;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const canonical = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonical)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonical(child)]))
    : value;
const canonicalJson = (value: unknown): string =>
  JSON.stringify(canonical(value));
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8").digest("hex");
const redactDynamicProcessIds = (value: unknown): unknown => Array.isArray(value)
  ? value.map(redactDynamicProcessIds)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value).map(([key, child]) => [
      key,
      key === "first_pid" || key === "second_pid"
        ? "<dynamic-process-id>" : redactDynamicProcessIds(child),
    ]))
    : value;

export const digestOperationProviderEvidenceForParity = (
  result: unknown,
): string => {
  const providerResult = object(
    result,
    "RMT_OP_PARITY_PROVIDER_RESULT_INVALID",
  );
  const semanticOutput = object(
    providerResult.semantic_output,
    "RMT_OP_PARITY_PROVIDER_RESULT_INVALID",
  );
  const proof = object(
    semanticOutput.proof,
    "RMT_OP_PARITY_PROVIDER_PROOF_INVALID",
  );
  const nativeEvidence = {
    ...providerResult,
    semantic_output: {
      ...semanticOutput,
      proof: {
        ...proof,
        observations: "<portable-observations-compared-separately>",
        family_controls: "<portable-family-controls-compared-separately>",
      },
    },
  };
  return sha256(canonicalJson(redactDynamicProcessIds(nativeEvidence)));
};
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(
    detail === undefined ? code : `${code}:${detail}`,
  ), {code, detail: detail ?? null});
};
const exactKeys = (
  value: JsonObject,
  expected: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) fail(code);
};
const object = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const array = (value: unknown, code: string): unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const exactStringSet = (
  values: readonly string[],
  expected: readonly string[],
): boolean => canonicalJson([...values].sort(compareUtf8)) ===
  canonicalJson([...expected].sort(compareUtf8));
const stringArray = (value: unknown, code: string): string[] => {
  const values = array(value, code);
  if (!values.every((entry) => typeof entry === "string")) fail(code);
  return values as string[];
};
const sha = (value: unknown, code: string): string => {
  const digest = string(value, code);
  if (!SHA256.test(digest)) fail(code);
  return digest;
};

const validateObservationShape = (
  observation: JsonObject,
  language: Language,
): void => {
  const code = "RMT_OP_PARITY_OBSERVATION_INVALID";
  const definitionRef = object(observation.definition_ref, code);
  const denominatorRef = object(observation.denominator_ref, code);
  const observer = object(observation.observer, code);
  const inputs = object(observation.inputs, code);
  const atomicity = object(observation.atomicity, code);
  const outcome = object(observation.outcome, code);
  const continuation = object(observation.continuation, code);
  exactKeys(definitionRef, ["definition_id", "path", "sha256"], code);
  exactKeys(denominatorRef, ["denominator_id", "sha256"], code);
  exactKeys(observer, ["observer_id", "ownership"], code);
  exactKeys(inputs, ["settlement_id", "expected_state_version"], code);
  exactKeys(atomicity, ["mode", "outcome"], code);
  exactKeys(outcome, [
    "kind", "value", "failure_code",
    "exactly_once_distributed_delivery_claimed",
  ], code);
  exactKeys(continuation, ["closure", "closed", "pending_effect_count"], code);
  string(definitionRef.definition_id, code);
  string(definitionRef.path, code);
  sha(definitionRef.sha256, code);
  string(denominatorRef.denominator_id, code);
  sha(denominatorRef.sha256, code);
  string(observer.observer_id, code);
  if (definitionRef.definition_id !==
        "state-changing-action.complete-settlement/v1" ||
      denominatorRef.denominator_id !==
        "state-changing-action.complete-settlement/v1" ||
      observer.observer_id !== PROVIDERS[language].observer_id ||
      observer.ownership !== "independent-proof-harness" ||
      observation.source_kind !== "target-observation" ||
      observation.operation_id !== "complete-settlement" ||
      observation.observation_id !==
        `observation.operation.${language}.complete-settlement.${String(
          observation.case_id,
        )}/v1` ||
      typeof observation.transition_started !== "boolean" ||
      typeof inputs.settlement_id !== "string" ||
      !Number.isSafeInteger(inputs.expected_state_version) ||
      !["all-or-nothing", "best-effort"].includes(String(atomicity.mode)) ||
      !["committed", "rolled-back", "partial"].includes(
        String(atomicity.outcome),
      ) || !["success", "failure"].includes(String(outcome.kind)) ||
      typeof outcome.exactly_once_distributed_delivery_claimed !== "boolean" ||
      typeof continuation.closure !== "string" ||
      typeof continuation.closed !== "boolean" ||
      !Number.isSafeInteger(continuation.pending_effect_count)) {
    fail(code);
  }
  if (outcome.kind === "success") {
    const value = object(outcome.value, code);
    exactKeys(value, ["settlement_id", "payout_id", "status"], code);
    if (outcome.failure_code !== null ||
        typeof value.settlement_id !== "string" ||
        typeof value.payout_id !== "string" || value.status !== "committed") {
      fail(code);
    }
  } else if (outcome.value !== null ||
      typeof outcome.failure_code !== "string") {
    fail(code);
  }
  for (const key of [
    "read_attempts", "write_attempts", "external_effect_attempts", "trace",
  ] as const) {
    const values = stringArray(observation[key], code);
    if (new Set(values).size !== values.length ||
        (key === "trace" && values.length === 0)) fail(code);
  }
  for (const guardValue of array(observation.guard_evaluations, code)) {
    const guard = object(guardValue, code);
    exactKeys(guard, [
      "guard_id", "invoked", "decision", "current_state_version_observed",
      "controlled_effects",
    ], code);
    string(guard.guard_id, code);
    if (typeof guard.invoked !== "boolean" ||
        !["pass", "fail"].includes(String(guard.decision)) ||
        typeof guard.current_state_version_observed !== "boolean") fail(code);
    stringArray(guard.controlled_effects, code);
  }
  for (const eventValue of array(observation.emitted_events, code)) {
    const event = object(eventValue, code);
    exactKeys(event, ["event_type", "tense", "trace_ordinal"], code);
    string(event.event_type, code);
    if (!["past-tense", "imperative"].includes(String(event.tense)) ||
        !Number.isSafeInteger(event.trace_ordinal)) fail(code);
  }
  const relationAssertions = array(observation.relation_assertions, code);
  for (const relationValue of relationAssertions) {
    const relation = object(relationValue, code);
    exactKeys(relation, [
      "contract_id", "architecture_relation_id", "source_type",
      "target_type", "assertion_owner", "owner_evidence_sha256",
      "exact_assertion",
    ], code);
    for (const key of [
      "contract_id", "architecture_relation_id", "source_type",
      "target_type", "assertion_owner",
    ] as const) string(relation[key], code);
    sha(relation.owner_evidence_sha256, code);
    if (typeof relation.exact_assertion !== "boolean") fail(code);
  }
  if (canonicalJson(relationAssertions) !== canonicalJson(RELATION_ASSERTIONS)) {
    fail(code);
  }
};

const normalizeObservation = (
  value: unknown,
  language: Language,
): JsonObject => {
  const observation = object(value, "RMT_OP_PARITY_OBSERVATION_INVALID");
  exactKeys(
    observation,
    OBSERVATION_KEYS,
    "RMT_OP_PARITY_OBSERVATION_INVALID",
  );
  if (observation.schema_version !== "StateChangingActionObservation/v1" ||
      !["committed-success", "guard-rejected"].includes(
        observation.case_id as string,
      ) || observation.authority_effect !== "none" ||
      typeof observation.observation_sha256 !== "string" ||
      !SHA256.test(observation.observation_sha256)) {
    return fail("RMT_OP_PARITY_OBSERVATION_INVALID");
  }
  const {observation_sha256: digest, ...body} = observation;
  if (sha256(canonicalJson(body)) !== digest) {
    return fail("RMT_OP_PARITY_OBSERVATION_DIGEST_STALE");
  }
  validateObservationShape(observation, language);
  return Object.freeze(Object.fromEntries(
    PORTABLE_OBSERVATION_KEYS.map((key) => [key, canonical(observation[key])]),
  ));
};

type NormalizedProvider = Readonly<{
  portable: Readonly<{
    observations: readonly JsonObject[];
    source_obligations: readonly Readonly<{
      expected_code: string;
      status: "killed";
    }>[];
    family_controls: readonly Readonly<{
      hostile_id: string;
      status: "killed";
      finding_codes: readonly [string];
    }>[];
  }>;
  native: JsonObject;
}>;

const normalizeProvider = (
  language: Language,
  entryValue: unknown,
): NormalizedProvider => {
  const entry = object(entryValue, "RMT_OP_PARITY_PROVIDER_ENTRY_INVALID");
  exactKeys(entry, ["provider_id", "result"],
    "RMT_OP_PARITY_PROVIDER_ENTRY_INVALID");
  const policy = PROVIDERS[language];
  if (entry.provider_id !== policy.provider_id) {
    return fail("RMT_OP_PARITY_PROVIDER_ID_INVALID", language);
  }
  const result = object(entry.result, "RMT_OP_PARITY_PROVIDER_RESULT_INVALID");
  exactKeys(result, [
    "schema_version", "result", "provider_id", "semantic_output",
    "accounting", "claim_ceiling", "authority_effect",
  ], "RMT_OP_PARITY_PROVIDER_RESULT_INVALID");
  if (result.schema_version !== "FactoryNodeSemanticResult/v1" ||
      result.result !== "pass" || result.provider_id !== policy.provider_id ||
      result.authority_effect !== "none" ||
      typeof result.claim_ceiling !== "string") {
    return fail("RMT_OP_PARITY_PROVIDER_RESULT_INVALID", language);
  }
  const accounting = object(
    result.accounting,
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID",
  );
  exactKeys(accounting, [
    "positives_declared", "positives_passed", "mutants_declared",
    "mutants_killed",
  ], "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID");
  if (accounting.positives_declared !== 2 ||
      accounting.positives_passed !== 2 ||
      accounting.mutants_declared !== 29 ||
      accounting.mutants_killed !== 29) {
    return fail("RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID", language);
  }
  const semanticOutput = object(
    result.semantic_output,
    "RMT_OP_PARITY_PROVIDER_RESULT_INVALID",
  );
  exactKeys(
    semanticOutput,
    policy.semantic_output_keys,
    "RMT_OP_PARITY_PROVIDER_RESULT_INVALID",
  );
  if (language !== "typescript") {
    const workspace = object(
      semanticOutput.workspace,
      "RMT_OP_PARITY_WORKSPACE_INVALID",
    );
    exactKeys(workspace, ["isolated", "cleaned", "symlinks"],
      "RMT_OP_PARITY_WORKSPACE_INVALID");
    if (workspace.isolated !== true || workspace.cleaned !== true ||
        workspace.symlinks !== false) {
      return fail("RMT_OP_PARITY_WORKSPACE_INVALID", language);
    }
  }
  const proof = object(
    semanticOutput.proof,
    "RMT_OP_PARITY_PROVIDER_PROOF_INVALID",
  );
  exactKeys(proof, [
    "schema_version", "result", "target", "binding",
    ...policy.proof_native_keys,
    "observations", "source_controls", "family_controls", "accounting",
    "claim_ceiling", "authority_effect",
  ], "RMT_OP_PARITY_PROVIDER_PROOF_INVALID");
  if (proof.schema_version !== policy.proof_schema || proof.result !== "pass" ||
      proof.authority_effect !== "none" ||
      typeof proof.claim_ceiling !== "string" ||
      proof.claim_ceiling !== result.claim_ceiling) {
    return fail("RMT_OP_PARITY_PROVIDER_PROOF_INVALID", language);
  }
  const target = object(proof.target, "RMT_OP_PARITY_TARGET_INVALID");
  const binding = object(proof.binding, "RMT_OP_PARITY_BINDING_INVALID");
  exactKeys(target, [
    "target_id", "protocol_id", "language", "symbol_name", "source_sha256",
  ], "RMT_OP_PARITY_TARGET_INVALID");
  exactKeys(binding, language === "python" ? [
    "binding_id", "binding_sha256", "bound_role_count", "observer_sha256",
    "supervisor_sha256", "proof_builder_sha256", "provider_sha256",
  ] : [
    "binding_id", "binding_sha256", "observer_sha256",
    "proof_builder_sha256", "provider_sha256", "bound_role_count",
  ], "RMT_OP_PARITY_BINDING_INVALID");
  if (target.language !== language || target.target_id !== policy.target_id ||
      target.protocol_id !== policy.protocol_id ||
      target.symbol_name !== policy.symbol_name ||
      binding.binding_id !== policy.binding_id ||
      binding.bound_role_count !== policy.bound_role_count) {
    return fail("RMT_OP_PARITY_TARGET_INVALID", language);
  }
  sha(target.source_sha256, "RMT_OP_PARITY_TARGET_INVALID");
  for (const key of Object.keys(binding).filter((key) =>
    key.endsWith("_sha256"))) {
    sha(binding[key], "RMT_OP_PARITY_BINDING_INVALID");
  }
  if (language !== "python") {
    const subset = object(
      proof.closed_subset_proof,
      "RMT_OP_PARITY_NATIVE_PROOF_INVALID",
    );
    exactKeys(subset, [
      "schema_version", "result", "symbol_name", "source_sha256",
      "observer_id", "admitted_form", "source_control_count",
      "ambient_dependencies", "authority_effect",
    ], "RMT_OP_PARITY_NATIVE_PROOF_INVALID");
    if (subset.schema_version !== (language === "typescript"
      ? "TypeScriptOperationClosedSubsetProof/v1"
      : "RustOperationClosedSubsetProof/v1") ||
        subset.result !== "pass" || subset.symbol_name !== policy.symbol_name ||
        subset.source_sha256 !== target.source_sha256 ||
        subset.source_control_count !== 10 ||
        array(subset.ambient_dependencies,
          "RMT_OP_PARITY_NATIVE_PROOF_INVALID").length !== 0 ||
        subset.authority_effect !== "none") {
      return fail("RMT_OP_PARITY_NATIVE_PROOF_INVALID", language);
    }
  }
  const processEvidence = object(
    proof[language === "python"
      ? "native_process_evidence" : "runtime_proof"],
    "RMT_OP_PARITY_NATIVE_PROOF_INVALID",
  );
  exactKeys(processEvidence, language === "python" ? [
    "owner_cases", "fresh_processes", "distinct_pid_pairs", "process_pairs",
    "pids_redacted_from_semantic_observations",
  ] : language === "rust" ? [
    "owner_cases", "fresh_processes", "distinct_pid_pairs",
    "globally_distinct_pids", "process_pairs", "observer_origin",
  ] : [
    "owner_cases", "fresh_processes", "distinct_pid_pairs", "process_pairs",
    "observer_origin",
  ], "RMT_OP_PARITY_NATIVE_PROOF_INVALID");
  if (processEvidence.owner_cases !== 2 ||
      processEvidence.fresh_processes !== 4 ||
      processEvidence.distinct_pid_pairs !== 2 ||
      (language === "python" &&
        processEvidence.pids_redacted_from_semantic_observations !== true) ||
      (language !== "python" && processEvidence.observer_origin !==
        "independent-injected-port-harness") ||
      (language === "rust" && processEvidence.globally_distinct_pids !== 4)) {
    return fail("RMT_OP_PARITY_NATIVE_PROOF_INVALID", language);
  }
  const processPairs = array(
    processEvidence.process_pairs,
    "RMT_OP_PARITY_NATIVE_PROOF_INVALID",
  );
  if (processPairs.length !== 2) {
    return fail("RMT_OP_PARITY_NATIVE_PROOF_INVALID", language);
  }
  const observedProcessIds: number[] = [];
  for (const pairValue of processPairs) {
    const pair = object(pairValue, "RMT_OP_PARITY_NATIVE_PROOF_INVALID");
    exactKeys(pair, [
      "case_id", "first_pid", "second_pid", "semantic_sha256",
    ], "RMT_OP_PARITY_NATIVE_PROOF_INVALID");
    if (!["committed-success", "guard-rejected"].includes(
      String(pair.case_id),
    ) || !Number.isSafeInteger(pair.first_pid) ||
        !Number.isSafeInteger(pair.second_pid) ||
        (pair.first_pid as number) <= 0 ||
        (pair.second_pid as number) <= 0 ||
        pair.first_pid === pair.second_pid) {
      return fail("RMT_OP_PARITY_NATIVE_PROOF_INVALID", language);
    }
    observedProcessIds.push(pair.first_pid as number, pair.second_pid as number);
    sha(pair.semantic_sha256, "RMT_OP_PARITY_NATIVE_PROOF_INVALID");
  }
  if (language === "rust" && new Set(observedProcessIds).size !== 4) {
    return fail("RMT_OP_PARITY_NATIVE_PROOF_INVALID", language);
  }
  const proofAccounting = object(
    proof.accounting,
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID",
  );
  exactKeys(proofAccounting, [
    "positives", language === "python"
      ? "native_source_controls" : "target_source_controls",
    "family_controls", "mutants",
  ], "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID");
  const positiveAccounting = object(
    proofAccounting.positives,
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID",
  );
  const sourceAccounting = object(
    proofAccounting[language === "python"
      ? "native_source_controls" : "target_source_controls"],
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID",
  );
  const familyAccounting = object(
    proofAccounting.family_controls,
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID",
  );
  const mutantAccounting = object(
    proofAccounting.mutants,
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID",
  );
  exactKeys(positiveAccounting, ["declared", "passed"],
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID");
  exactKeys(sourceAccounting, ["declared", "killed"],
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID");
  exactKeys(familyAccounting, ["declared", "killed"],
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID");
  exactKeys(mutantAccounting, ["declared", "killed"],
    "RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID");
  if (positiveAccounting.declared !== 2 || positiveAccounting.passed !== 2 ||
      sourceAccounting.declared !== 10 || sourceAccounting.killed !== 10 ||
      familyAccounting.declared !== 19 || familyAccounting.killed !== 19 ||
      mutantAccounting.declared !== 29 || mutantAccounting.killed !== 29) {
    return fail("RMT_OP_PARITY_PROVIDER_ACCOUNTING_INVALID", language);
  }
  const rawObservations = array(
    proof.observations,
    "RMT_OP_PARITY_OBSERVATIONS_INVALID",
  );
  const observations = rawObservations.map((observation) =>
    normalizeObservation(observation, language)).sort((left, right) => compareUtf8(
    string(left.case_id, "RMT_OP_PARITY_OBSERVATIONS_INVALID"),
    string(right.case_id, "RMT_OP_PARITY_OBSERVATIONS_INVALID"),
  ));
  const observationIdentities = rawObservations.map((observationValue) => {
    const observation = object(
      observationValue,
      "RMT_OP_PARITY_OBSERVATIONS_INVALID",
    );
    return Object.freeze({
      case_id: observation.case_id,
      observation_id: observation.observation_id,
      observation_sha256: observation.observation_sha256,
      source_kind: observation.source_kind,
      observer: canonical(observation.observer),
    });
  }).sort((left, right) => compareUtf8(
    string(left.case_id, "RMT_OP_PARITY_OBSERVATIONS_INVALID"),
    string(right.case_id, "RMT_OP_PARITY_OBSERVATIONS_INVALID"),
  ));
  if (observations.length !== 2 || !exactStringSet(
    observations.map(({case_id}) => String(case_id)),
    ["committed-success", "guard-rejected"],
  )) {
    return fail("RMT_OP_PARITY_OBSERVATIONS_INVALID", language);
  }

  const sourceControls = array(
    proof.source_controls,
    "RMT_OP_PARITY_SOURCE_CONTROLS_INVALID",
  );
  const sourceObligations = sourceControls.map((controlValue) => {
    const control = object(
      controlValue,
      "RMT_OP_PARITY_SOURCE_CONTROLS_INVALID",
    );
    exactKeys(control, [
      "control_id", "status", "expected_code", "finding_codes",
      "source_sha256",
    ], "RMT_OP_PARITY_SOURCE_CONTROLS_INVALID");
    string(control.control_id, "RMT_OP_PARITY_SOURCE_CONTROLS_INVALID");
    const expectedCode = string(
      control.expected_code,
      "RMT_OP_PARITY_SOURCE_CONTROLS_INVALID",
    );
    const findings = array(
      control.finding_codes,
      "RMT_OP_PARITY_SOURCE_CONTROLS_INVALID",
    );
    if (control.status !== "killed" ||
        !findings.includes(expectedCode) ||
        !SHA256.test(string(
          control.source_sha256,
          "RMT_OP_PARITY_SOURCE_CONTROLS_INVALID",
        ))) {
      return fail("RMT_OP_PARITY_SOURCE_CONTROLS_INVALID", language);
    }
    return Object.freeze({
      expected_code: expectedCode,
      status: "killed" as const,
    });
  }).sort((left, right) => compareUtf8(
    left.expected_code,
    right.expected_code,
  ));
  if (sourceObligations.length !== 10 || !exactStringSet(
    sourceObligations.map(({expected_code: code}) => code),
    SOURCE_CODES,
  )) {
    return fail("RMT_OP_PARITY_SOURCE_CONTROLS_INVALID", language);
  }

  const familyControls = array(
    proof.family_controls,
    "RMT_OP_PARITY_FAMILY_CONTROLS_INVALID",
  ).map((controlValue) => {
    const control = object(
      controlValue,
      "RMT_OP_PARITY_FAMILY_CONTROLS_INVALID",
    );
    const hostileId = string(
      control.hostile_id,
      "RMT_OP_PARITY_FAMILY_CONTROLS_INVALID",
    );
    const isS1 = hostileId.startsWith("s1/");
    exactKeys(control, isS1
      ? ["hostile_id", "status", "finding_codes",
        "required_residue_observed"]
      : ["hostile_id", "status", "finding_codes"],
      "RMT_OP_PARITY_FAMILY_CONTROLS_INVALID");
    const findings = array(
      control.finding_codes,
      "RMT_OP_PARITY_FAMILY_CONTROLS_INVALID",
    );
    if (control.status !== "killed" ||
        (isS1 && control.required_residue_observed !== true) ||
        findings.length !== 1 ||
        typeof findings[0] !== "string" ||
        OPERATION_EXPECTED_DIAGNOSTIC[
          hostileId as keyof typeof OPERATION_EXPECTED_DIAGNOSTIC
        ] !== findings[0]) {
      return fail("RMT_OP_PARITY_FAMILY_CONTROLS_INVALID", language);
    }
    return Object.freeze({
      hostile_id: hostileId,
      status: "killed" as const,
      finding_codes: Object.freeze([findings[0]] as [string]),
    });
  }).sort((left, right) => compareUtf8(left.hostile_id, right.hostile_id));
  if (familyControls.length !== 19 || !exactStringSet(
    familyControls.map(({hostile_id: id}) => id),
    FAMILY_HOSTILES,
  )) {
    return fail("RMT_OP_PARITY_FAMILY_CONTROLS_INVALID", language);
  }
  if (digestOperationProviderEvidenceForParity(result) !==
      policy.evidence_sha256) {
    return fail("RMT_OP_PARITY_PROVIDER_EVIDENCE_STALE", language);
  }

  return Object.freeze({
    portable: Object.freeze({
      observations: Object.freeze(observations),
      source_obligations: Object.freeze(sourceObligations),
      family_controls: Object.freeze(familyControls),
    }),
    native: Object.freeze({
      language,
      provider_id: policy.provider_id,
      target: canonical(target),
      binding: canonical(binding),
      closed_subset_proof: canonical(proof.closed_subset_proof ?? null),
      runtime_proof: canonical(proof.runtime_proof ?? null),
      native_process_evidence: canonical(
        proof.native_process_evidence ?? null,
      ),
      observation_identities: canonical(observationIdentities),
      source_controls: canonical(sourceControls),
      workspace: canonical(semanticOutput.workspace ?? null),
    }),
  });
};

export type OperationParityResultV1 = Readonly<{
  schema_version: "OperationSemanticParity/v1";
  result: "pass" | "block";
  providers: readonly [
    "operation-typescript-v1",
    "operation-python-v1",
    "operation-rust-v1",
  ];
  portable_projection: NormalizedProvider["portable"];
  native_evidence: Readonly<Record<Language, JsonObject>>;
  native_hash_byte_comparison: false;
  portable_semantics_compared: true;
  target_source_bytes_compared: false;
  native_evidence_hashes_compared_for_equality: false;
  native_evidence_retained_separately: true;
  native_source_hashes_all_distinct: boolean;
  excluded_native_fields: readonly string[];
  diagnostics: readonly string[];
  claim_ceiling: string;
  authority_effect: "none";
  parity_sha256: string;
}>;

export const evaluateOperationParity = (
  inputValue: unknown,
): OperationParityResultV1 => {
  const input = object(inputValue, "RMT_OP_PARITY_PROVIDER_SET_INVALID");
  exactKeys(input, LANGUAGES, "RMT_OP_PARITY_PROVIDER_SET_INVALID");
  const normalized = Object.fromEntries(LANGUAGES.map((language) => [
    language,
    normalizeProvider(language, input[language]),
  ])) as Record<Language, NormalizedProvider>;
  const baseline = normalized.typescript.portable;
  const diagnostics: string[] = [];
  for (const language of ["python", "rust"] as const) {
    if (canonicalJson(normalized[language].portable.observations) !==
        canonicalJson(baseline.observations)) {
      diagnostics.push(`RMT_OP_PARITY_OBSERVATION_MISMATCH:${language}`);
    }
    if (canonicalJson(normalized[language].portable.source_obligations) !==
        canonicalJson(baseline.source_obligations)) {
      diagnostics.push(`RMT_OP_PARITY_SOURCE_OBLIGATION_MISMATCH:${language}`);
    }
    if (canonicalJson(normalized[language].portable.family_controls) !==
        canonicalJson(baseline.family_controls)) {
      diagnostics.push(`RMT_OP_PARITY_FAMILY_CONTROL_MISMATCH:${language}`);
    }
  }
  diagnostics.sort(compareUtf8);
  const nativeEvidence = Object.freeze(Object.fromEntries(
    LANGUAGES.map((language) => [language, normalized[language].native]),
  )) as Readonly<Record<Language, JsonObject>>;
  const sourceHashes = LANGUAGES.map((language) => string(
    object(nativeEvidence[language].target, "RMT_OP_PARITY_TARGET_INVALID")
      .source_sha256,
    "RMT_OP_PARITY_TARGET_INVALID",
  ));
  const body = Object.freeze({
    schema_version: "OperationSemanticParity/v1" as const,
    result: diagnostics.length === 0 ? "pass" as const : "block" as const,
    providers: Object.freeze([
      "operation-typescript-v1",
      "operation-python-v1",
      "operation-rust-v1",
    ] as const),
    portable_projection: baseline,
    native_evidence: nativeEvidence,
    native_hash_byte_comparison: false as const,
    portable_semantics_compared: true as const,
    target_source_bytes_compared: false as const,
    native_evidence_hashes_compared_for_equality: false as const,
    native_evidence_retained_separately: true as const,
    native_source_hashes_all_distinct: new Set(sourceHashes).size === 3,
    excluded_native_fields: Object.freeze([
      "provider and target identities",
      "source and binding digests",
      "observer identities and closed-subset mechanisms",
      "process identifiers and workspace evidence",
      "language-specific source-control collateral diagnostics",
    ]),
    diagnostics: Object.freeze(diagnostics),
    claim_ceiling: "portable semantic parity for one candidate-local Operation across the exact TypeScript, Python, and Rust admitted subsets; native evidence remains separate and source-byte equality is not a parity criterion",
    authority_effect: "none" as const,
  });
  return Object.freeze({
    ...body,
    parity_sha256: sha256(canonicalJson(body)),
  });
};
