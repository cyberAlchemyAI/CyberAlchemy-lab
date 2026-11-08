import {createHash} from "node:crypto";

import {
  OPERATION_EXPECTED_DIAGNOSTIC,
  type OperationFindingCode,
  type OperationHostileFixtureV1,
  type OperationS1HostileFixtureV1,
  type StateChangingActionDefinitionV1,
  type StateChangingActionDenominatorV1,
  type StateChangingActionObservationV1,
} from "../../../../families/state-changing-action/contracts/state-changing-action-contracts.js";
import {evaluateOperationS1Residue, evaluateStateChangingAction} from
  "../../../../families/state-changing-action/evaluator/evaluate-state-changing-action.js";
import {applyOperationHostile, applyOperationS1Mutation} from
  "../../../../families/state-changing-action/mutations/apply-operation-hostile.js";
import {
  canonicalOperationJson,
  decodeOperationHostileFixtureV1,
  decodeStateChangingActionDefinitionV1,
  decodeStateChangingActionDenominatorV1,
  decodeStateChangingActionObservationSetV1,
  mintStateChangingActionObservationV1,
  sha256OperationBytes,
  sha256OperationValue,
} from "../../../../families/state-changing-action/providers/decode-state-changing-action.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const PYTHON_OPERATION_HOSTILE_PATHS = Object.freeze({
  hostile_01_undeclared_write:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/undeclared-write.json",
  hostile_02_undeclared_effect:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/undeclared-effect.json",
  hostile_03_guard_bypass:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/guard-bypass.json",
  hostile_04_order_swap:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/order-swap.json",
  hostile_05_atomicity_removed:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/atomicity-removed.json",
  hostile_06_success_failure_collapse:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/success-failure-collapse.json",
  hostile_07_emitted_before_commit:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/emitted-before-commit.json",
  hostile_08_continuation_mismatch:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/continuation-mismatch.json",
  hostile_09_read_set_drift:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/read-set-drift.json",
  hostile_10_output_contract_overclaim:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/output-contract-overclaim.json",
  hostile_11_relation_owner_evidence_stale:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/relation-owner-evidence-stale.json",
  hostile_12_relation_source_endpoint_mismatch:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/relation-source-endpoint-mismatch.json",
  hostile_13_relation_target_endpoint_mismatch:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/relation-target-endpoint-mismatch.json",
  hostile_14_materialized_without_exact_assertion:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/materialized-without-exact-assertion.json",
  hostile_15_before_state_write_failure:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/before-state-write-failure.json",
  hostile_16_between_state_and_outbox_failure:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/between-state-and-outbox-failure.json",
  hostile_17_missing_member:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/missing-member.json",
  hostile_18_mixed_commit:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/mixed-commit.json",
  hostile_19_rollback_after_commit:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/hostiles/rollback-after-commit.json",
});

const OPERATION_S1_CATALOGUE_BINDINGS = Object.freeze([
  Object.freeze({role: "hostile_15_before_state_write_failure",
    hostile_id: "s1/before-state-write-failure",
    expected_code: "RMT_S1_BEFORE_STATE_WRITE_FAILURE",
    category: "fault-matrix:S1-F01",
    required_observation: "state-write-attempt and transaction abort",
    required_outcome: "no durable state and no occurrence"}),
  Object.freeze({role: "hostile_16_between_state_and_outbox_failure",
    hostile_id: "s1/between-state-and-outbox-failure",
    expected_code: "RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH",
    category: "fault-matrix:S1-F02",
    required_observation: "state write plus missing outbox checkpoint",
    required_outcome: "atomic abort; no mixed commit"}),
  Object.freeze({role: "hostile_17_missing_member",
    hostile_id: "s1/missing-member", expected_code: "RMT_S1_MISSING_MEMBER",
    category: "decode-contract",
    required_observation: "missing transaction or occurrence member",
    required_outcome: "closed rejection with stable code"}),
  Object.freeze({role: "hostile_18_mixed_commit",
    hostile_id: "s1/mixed-commit", expected_code: "RMT_S1_MIXED_COMMIT",
    category: "atomicity-contract",
    required_observation: "state durable while outbox absent, or inverse",
    required_outcome: "reject mixed commit"}),
  Object.freeze({role: "hostile_19_rollback_after_commit",
    hostile_id: "s1/rollback-after-commit",
    expected_code: "RMT_S1_ROLLBACK_AFTER_COMMIT",
    category: "recovery-contract",
    required_observation:
      "attempt to erase committed state or outbox occurrence",
    required_outcome: "reject rollback and require forward recovery"}),
] as const);

export const PYTHON_OPERATION_RAW_PATHS = Object.freeze({
  admission:
    "projects/domainspec-v2/development/remaining-meta-types/active-types/operation/admission/admission.json",
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/fixtures/complete-settlement/operation-contract.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/fixtures/complete-settlement/denominator.json",
  positive_observations:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/fixtures/complete-settlement/positive-observation.json",
  family_contracts:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/contracts/state-changing-action-contracts.ts",
  family_decoder:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/providers/decode-state-changing-action.ts",
  family_evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/evaluator/evaluate-state-changing-action.ts",
  family_mutator:
    "projects/domainspec-v2/impl/architecture-conformance/families/state-changing-action/mutations/apply-operation-hostile.ts",
  hostile_catalogue:
    "projects/domainspec-v2/development/refinement-runs/20260814T193343Z-active-meta-type-implementations/refreshes/20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/HOSTILE-CATALOGUE.json",
  relation_contracts:
    "projects/domainspec-v2/development/refinement-runs/20260814T193343Z-active-meta-type-implementations/refreshes/20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/RELATION-CONTRACTS.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/operation_v1.py",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/python/state-changing-v1/observe_python_operation_case.py",
  supervisor:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/python/state-changing-v1/run_python_operation_proof.py",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/python/state-changing-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/operation-python-v1.ts",
  provider_contract:
    "projects/domainspec-v2/impl/architecture-conformance/factory/contracts/factory-node-provider-v1.ts",
  ...PYTHON_OPERATION_HOSTILE_PATHS,
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/python/state-changing-v1/python-binding.json",
});

type BoundRole = Exclude<keyof typeof PYTHON_OPERATION_RAW_PATHS, "binding">;
export type PythonOperationRawInputs = Readonly<Record<
keyof typeof PYTHON_OPERATION_RAW_PATHS,
string
>>;

export const PYTHON_OPERATION_SOURCE_CONTROLS = Object.freeze([
  Object.freeze({control_id: "py-op/undeclared-write", expected_code:
    "RMT_OP_UNDECLARED_WRITE", case_id: "committed-success"}),
  Object.freeze({control_id: "py-op/undeclared-effect", expected_code:
    "RMT_OP_UNDECLARED_EFFECT", case_id: "committed-success"}),
  Object.freeze({control_id: "py-op/guard-bypass", expected_code:
    "RMT_OP_GUARD_BYPASS", case_id: "guard-rejected"}),
  Object.freeze({control_id: "py-op/order-swap", expected_code:
    "RMT_OP_ORDER_SWAP", case_id: "committed-success"}),
  Object.freeze({control_id: "py-op/atomicity-removed", expected_code:
    "RMT_OP_ATOMICITY_REMOVED", case_id: "committed-success"}),
  Object.freeze({control_id: "py-op/success-failure-collapse", expected_code:
    "RMT_OP_SUCCESS_FAILURE_COLLAPSE", case_id: "guard-rejected"}),
  Object.freeze({control_id: "py-op/emitted-before-commit", expected_code:
    "RMT_OP_EMITTED_BEFORE_COMMIT", case_id: "committed-success"}),
  Object.freeze({control_id: "py-op/continuation-mismatch", expected_code:
    "RMT_OP_CONTINUATION_MISMATCH", case_id: "committed-success"}),
  Object.freeze({control_id: "py-op/read-set-drift", expected_code:
    "RMT_OP_READ_SET_DRIFT", case_id: "committed-success"}),
  Object.freeze({control_id: "py-op/output-contract-overclaim", expected_code:
    "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM", case_id: "committed-success"}),
] as const);

type PythonOperationBindingV1 = Readonly<{
  schema_version: "PythonOperationBinding/v1";
  binding_id: "python.complete-settlement.bound-operation/v1";
  target_id: "operation.python.complete-settlement/v1";
  protocol_id: "python.bound-operation/v1";
  symbol_name: "complete_settlement_operation";
  observer_id: "observer.python-operation-ports/v1";
  observer_owner_ref: "python-operation-proof-harness";
  proof_mechanism:
    "ast-bytecode-audit-plus-two-fresh-processes-per-owner-case";
  refs: Readonly<Record<BoundRole, ExactRef>>;
  authority_effect: "none";
  binding_sha256: string;
}>;

type NativeSourceProofV1 = Readonly<{
  schema_version: "PythonOperationClosedSubsetProof/v1";
  source_sha256: string;
  symbol_name: "complete_settlement_operation";
  lifecycle_basis: "synchronous-return-plus-injected-port-quiescence";
  proof_mechanism: "ast-bytecode-audit-plus-injected-port-trace";
  bytecode_opnames: readonly string[];
  authority_effect: "none";
}>;

type NativeCaseV1 = Readonly<{
  case_id: "committed-success" | "guard-rejected";
  input: Readonly<{settlement_id: string; expected_state_version: number}>;
  result: StateChangingActionObservationV1["outcome"];
  trace: readonly string[];
  reads: readonly string[];
  writes: readonly string[];
  effects: readonly string[];
  events: StateChangingActionObservationV1["emitted_events"];
  guards: readonly Readonly<{
    guard_id: string;
    invoked: boolean;
    decision: "pass" | "fail";
    current_state_version_observed: boolean;
  }>[];
  commit_mode: "all-or-nothing" | "best-effort";
  commit_count: number;
  rollback_count: number;
  begin_count: number;
  close_count: number;
  continuation_closure: string | null;
  source_proof: NativeSourceProofV1;
}>;

type NativeSourceControlV1 = Readonly<{
  control_id: string;
  expected_code: OperationFindingCode;
  case_id: "committed-success" | "guard-rejected";
  source_sha256: string;
  observation: NativeCaseV1;
}>;

type PythonOperationNativeProofV1 = Readonly<{
  schema_version: "PythonOperationNativeProof/v1";
  binding: Readonly<{binding_id: string; binding_sha256: string}>;
  source_proof: NativeSourceProofV1;
  owner_cases: readonly NativeCaseV1[];
  source_controls: readonly NativeSourceControlV1[];
  process_evidence: Readonly<{
    owner_cases: 2;
    fresh_processes: 4;
    distinct_pid_pairs: 2;
    process_pairs: readonly Readonly<{
      case_id: string;
      first_pid: number;
      second_pid: number;
      semantic_sha256: string;
    }>[];
    pids_redacted_from_semantic_observations: true;
  }>;
  accounting: Readonly<{
    positives: Readonly<{declared: 2; passed: 2}>;
    source_controls: Readonly<{declared: 10; executed: 10}>;
  }>;
  claim_ceiling: string;
  authority_effect: "none";
}>;

const SHA256 = /^[a-f0-9]{64}$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string | Uint8Array): string => createHash("sha256")
  .update(value)
  .digest("hex");
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail ? `${code}:${detail}` : code), {code});
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
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    const value: unknown = JSON.parse(bytes);
    return isObject(value) ? value : fail(code);
  } catch (error) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const bindingBody = (binding: PythonOperationBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};

export const validatePythonOperationRawInputs = (
  raw: PythonOperationRawInputs,
): PythonOperationBindingV1 => {
  const value = parseJson(raw.binding, "PY_OP_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "symbol_name", "observer_id", "observer_owner_ref",
    "proof_mechanism", "refs", "authority_effect", "binding_sha256",
  ], "PY_OP_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "PythonOperationBinding/v1" ||
      value.binding_id !== "python.complete-settlement.bound-operation/v1" ||
      value.target_id !== "operation.python.complete-settlement/v1" ||
      value.protocol_id !== "python.bound-operation/v1" ||
      value.symbol_name !== "complete_settlement_operation" ||
      value.observer_id !== "observer.python-operation-ports/v1" ||
      value.observer_owner_ref !== "python-operation-proof-harness" ||
      value.proof_mechanism !==
        "ast-bytecode-audit-plus-two-fresh-processes-per-owner-case" ||
      value.authority_effect !== "none" ||
      typeof value.binding_sha256 !== "string" ||
      !SHA256.test(value.binding_sha256) || !isObject(value.refs)) {
    return fail("PY_OP_BINDING_POLICY_INVALID");
  }
  const roles = Object.keys(PYTHON_OPERATION_RAW_PATHS)
    .filter((role): role is BoundRole => role !== "binding");
  exactKeys(value.refs, roles, "PY_OP_BINDING_REFS_INVALID");
  const refs = {} as Record<BoundRole, ExactRef>;
  for (const role of roles) {
    const ref = value.refs[role];
    if (!isObject(ref)) return fail("PY_OP_BINDING_REF_INVALID", role);
    exactKeys(ref, ["path", "sha256"], "PY_OP_BINDING_REF_INVALID");
    const path = PYTHON_OPERATION_RAW_PATHS[role];
    if (ref.path !== path || typeof ref.sha256 !== "string" ||
        !SHA256.test(ref.sha256)) {
      return fail("PY_OP_BINDING_REF_INVALID", role);
    }
    if (sha256(raw[role]) !== ref.sha256) {
      return fail("PY_OP_BINDING_INPUT_STALE", role);
    }
    refs[role] = Object.freeze({path, sha256: ref.sha256});
  }
  const binding = Object.freeze({
    schema_version: "PythonOperationBinding/v1" as const,
    binding_id: "python.complete-settlement.bound-operation/v1" as const,
    target_id: "operation.python.complete-settlement/v1" as const,
    protocol_id: "python.bound-operation/v1" as const,
    symbol_name: "complete_settlement_operation" as const,
    observer_id: "observer.python-operation-ports/v1" as const,
    observer_owner_ref: "python-operation-proof-harness" as const,
    proof_mechanism:
      "ast-bytecode-audit-plus-two-fresh-processes-per-owner-case" as const,
    refs: Object.freeze(refs),
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies PythonOperationBindingV1;
  if (sha256(canonicalOperationJson(bindingBody(binding))) !==
      binding.binding_sha256) {
    return fail("PY_OP_BINDING_DIGEST_STALE");
  }
  return binding;
};

const decodeSourceProof = (value: unknown): NativeSourceProofV1 => {
  if (!isObject(value)) return fail("PY_OP_NATIVE_SOURCE_PROOF_INVALID");
  exactKeys(value, [
    "schema_version", "source_sha256", "symbol_name", "lifecycle_basis",
    "proof_mechanism", "bytecode_opnames", "authority_effect",
  ], "PY_OP_NATIVE_SOURCE_PROOF_INVALID");
  if (value.schema_version !== "PythonOperationClosedSubsetProof/v1" ||
      typeof value.source_sha256 !== "string" ||
      !SHA256.test(value.source_sha256) ||
      value.symbol_name !== "complete_settlement_operation" ||
      value.lifecycle_basis !==
        "synchronous-return-plus-injected-port-quiescence" ||
      value.proof_mechanism !==
        "ast-bytecode-audit-plus-injected-port-trace" ||
      !Array.isArray(value.bytecode_opnames) ||
      !value.bytecode_opnames.every((item) => typeof item === "string") ||
      value.authority_effect !== "none") {
    return fail("PY_OP_NATIVE_SOURCE_PROOF_INVALID");
  }
  return Object.freeze(value as unknown as NativeSourceProofV1);
};

const stringArray = (value: unknown, code: string): readonly string[] => {
  if (!Array.isArray(value) ||
      !value.every((item) => typeof item === "string")) return fail(code);
  return Object.freeze([...value]);
};

const decodeNativeCase = (value: unknown): NativeCaseV1 => {
  if (!isObject(value)) return fail("PY_OP_NATIVE_CASE_INVALID");
  exactKeys(value, [
    "case_id", "input", "result", "trace", "reads", "writes", "effects",
    "events", "guards", "commit_mode", "commit_count", "rollback_count",
    "begin_count", "close_count", "continuation_closure", "source_proof",
  ], "PY_OP_NATIVE_CASE_INVALID");
  if (!isObject(value.input)) return fail("PY_OP_NATIVE_CASE_INVALID");
  exactKeys(value.input, [
    "settlement_id", "expected_state_version",
  ], "PY_OP_NATIVE_CASE_INVALID");
  if (!["committed-success", "guard-rejected"].includes(
    value.case_id as string,
  ) || typeof value.input.settlement_id !== "string" ||
      !Number.isSafeInteger(value.input.expected_state_version) ||
      !isObject(value.result)) return fail("PY_OP_NATIVE_CASE_INVALID");
  exactKeys(value.result, [
    "kind", "value", "failure_code",
    "exactly_once_distributed_delivery_claimed",
  ], "PY_OP_NATIVE_CASE_INVALID");
  stringArray(value.trace, "PY_OP_NATIVE_CASE_INVALID");
  stringArray(value.reads, "PY_OP_NATIVE_CASE_INVALID");
  stringArray(value.writes, "PY_OP_NATIVE_CASE_INVALID");
  stringArray(value.effects, "PY_OP_NATIVE_CASE_INVALID");
  if (!Array.isArray(value.events) || !Array.isArray(value.guards)) {
    return fail("PY_OP_NATIVE_CASE_INVALID");
  }
  for (const event of value.events) {
    if (!isObject(event)) return fail("PY_OP_NATIVE_CASE_INVALID");
    exactKeys(event, [
      "event_type", "tense", "trace_ordinal",
    ], "PY_OP_NATIVE_CASE_INVALID");
    if (typeof event.event_type !== "string" ||
        event.tense !== "past-tense" ||
        !Number.isSafeInteger(event.trace_ordinal)) {
      return fail("PY_OP_NATIVE_CASE_INVALID");
    }
  }
  for (const guard of value.guards) {
    if (!isObject(guard)) return fail("PY_OP_NATIVE_CASE_INVALID");
    exactKeys(guard, [
      "guard_id", "invoked", "decision", "current_state_version_observed",
    ], "PY_OP_NATIVE_CASE_INVALID");
    if (typeof guard.guard_id !== "string" || guard.invoked !== true ||
        !["pass", "fail"].includes(guard.decision as string) ||
        typeof guard.current_state_version_observed !== "boolean") {
      return fail("PY_OP_NATIVE_CASE_INVALID");
    }
  }
  if (!["all-or-nothing", "best-effort"].includes(
    value.commit_mode as string,
  ) ||
      ![value.commit_count, value.rollback_count, value.begin_count,
        value.close_count].every(Number.isSafeInteger) ||
      (value.continuation_closure !== null &&
        typeof value.continuation_closure !== "string")) {
    return fail("PY_OP_NATIVE_CASE_INVALID");
  }
  decodeSourceProof(value.source_proof);
  return Object.freeze(value as unknown as NativeCaseV1);
};

const decodeNativeProof = (value: unknown): PythonOperationNativeProofV1 => {
  if (!isObject(value)) return fail("PY_OP_NATIVE_PROOF_INVALID");
  exactKeys(value, [
    "schema_version", "binding", "source_proof", "owner_cases",
    "source_controls", "process_evidence", "accounting", "claim_ceiling",
    "authority_effect",
  ], "PY_OP_NATIVE_PROOF_INVALID");
  if (value.schema_version !== "PythonOperationNativeProof/v1" ||
      !isObject(value.binding) || !Array.isArray(value.owner_cases) ||
      !Array.isArray(value.source_controls) ||
      !isObject(value.process_evidence) || !isObject(value.accounting) ||
      typeof value.claim_ceiling !== "string" ||
      value.authority_effect !== "none") {
    return fail("PY_OP_NATIVE_PROOF_INVALID");
  }
  exactKeys(value.binding, [
    "binding_id", "binding_sha256",
  ], "PY_OP_NATIVE_PROOF_INVALID");
  const sourceProof = decodeSourceProof(value.source_proof);
  const ownerCases = value.owner_cases.map(decodeNativeCase);
  if (ownerCases.length !== 2 ||
      ownerCases[0]?.case_id !== "committed-success" ||
      ownerCases[1]?.case_id !== "guard-rejected") {
    return fail("PY_OP_NATIVE_OWNER_CASES_INVALID");
  }
  const controls = value.source_controls.map((entry, index) => {
    if (!isObject(entry)) return fail("PY_OP_NATIVE_CONTROLS_INVALID");
    exactKeys(entry, [
      "control_id", "expected_code", "case_id", "source_sha256",
      "observation",
    ], "PY_OP_NATIVE_CONTROLS_INVALID");
    const expected = PYTHON_OPERATION_SOURCE_CONTROLS[index];
    const observation = decodeNativeCase(entry.observation);
    if (!expected || entry.control_id !== expected.control_id ||
        entry.expected_code !== expected.expected_code ||
        entry.case_id !== expected.case_id ||
        observation.case_id !== expected.case_id ||
        typeof entry.source_sha256 !== "string" ||
        !SHA256.test(entry.source_sha256)) {
      return fail("PY_OP_NATIVE_CONTROLS_INVALID");
    }
    return Object.freeze({
      control_id: expected.control_id,
      expected_code: expected.expected_code,
      case_id: expected.case_id,
      source_sha256: entry.source_sha256,
      observation,
    }) as NativeSourceControlV1;
  });
  if (controls.length !== PYTHON_OPERATION_SOURCE_CONTROLS.length) {
    return fail("PY_OP_NATIVE_CONTROLS_INVALID");
  }
  exactKeys(value.process_evidence, [
    "owner_cases", "fresh_processes", "distinct_pid_pairs",
    "process_pairs", "pids_redacted_from_semantic_observations",
  ], "PY_OP_NATIVE_PROCESS_EVIDENCE_INVALID");
  if (value.process_evidence.owner_cases !== 2 ||
      value.process_evidence.fresh_processes !== 4 ||
      value.process_evidence.distinct_pid_pairs !== 2 ||
      value.process_evidence.pids_redacted_from_semantic_observations !== true ||
      !Array.isArray(value.process_evidence.process_pairs) ||
      value.process_evidence.process_pairs.length !== 2) {
    return fail("PY_OP_NATIVE_PROCESS_EVIDENCE_INVALID");
  }
  for (const pair of value.process_evidence.process_pairs) {
    if (!isObject(pair)) {
      return fail("PY_OP_NATIVE_PROCESS_EVIDENCE_INVALID");
    }
    exactKeys(pair, [
      "case_id", "first_pid", "second_pid", "semantic_sha256",
    ], "PY_OP_NATIVE_PROCESS_EVIDENCE_INVALID");
    if (typeof pair.first_pid !== "number" ||
        typeof pair.second_pid !== "number" ||
        pair.first_pid === pair.second_pid ||
        typeof pair.semantic_sha256 !== "string" ||
        !SHA256.test(pair.semantic_sha256)) {
      return fail("PY_OP_NATIVE_PROCESS_EVIDENCE_INVALID");
    }
  }
  exactKeys(value.accounting, [
    "positives", "source_controls",
  ], "PY_OP_NATIVE_ACCOUNTING_INVALID");
  if (!isObject(value.accounting.positives) ||
      !isObject(value.accounting.source_controls)) {
    return fail("PY_OP_NATIVE_ACCOUNTING_INVALID");
  }
  exactKeys(value.accounting.positives, [
    "declared", "passed",
  ], "PY_OP_NATIVE_ACCOUNTING_INVALID");
  exactKeys(value.accounting.source_controls, [
    "declared", "executed",
  ], "PY_OP_NATIVE_ACCOUNTING_INVALID");
  if (value.accounting.positives.declared !== 2 ||
      value.accounting.positives.passed !== 2 ||
      value.accounting.source_controls.declared !== 10 ||
      value.accounting.source_controls.executed !== 10) {
    return fail("PY_OP_NATIVE_ACCOUNTING_INVALID");
  }
  return Object.freeze({
    ...value,
    schema_version: "PythonOperationNativeProof/v1" as const,
    source_proof: sourceProof,
    owner_cases: Object.freeze(ownerCases),
    source_controls: Object.freeze(controls),
    authority_effect: "none" as const,
  }) as PythonOperationNativeProofV1;
};

const observationFromNative = (
  child: NativeCaseV1,
  definition: StateChangingActionDefinitionV1,
  definitionRaw: string,
  denominator: StateChangingActionDenominatorV1,
  denominatorRaw: string,
): StateChangingActionObservationV1 =>
  mintStateChangingActionObservationV1({
    schema_version: "StateChangingActionObservation/v1",
    observation_id:
      `observation.operation.python.complete-settlement.${child.case_id}/v1`,
    case_id: child.case_id,
    source_kind: "target-observation",
    definition_ref: Object.freeze({
      definition_id: definition.definition_id,
      path: PYTHON_OPERATION_RAW_PATHS.definition,
      sha256: sha256OperationBytes(definitionRaw),
    }),
    denominator_ref: Object.freeze({
      denominator_id: denominator.denominator_id,
      sha256: sha256OperationBytes(denominatorRaw),
    }),
    observer: Object.freeze({
      observer_id: "observer.python-operation-ports/v1",
      ownership: "independent-proof-harness",
    }),
    operation_id: definition.operation_id,
    transition_started: child.begin_count > 0 || child.writes.length > 0,
    inputs: child.input,
    read_attempts: Object.freeze([...child.reads]),
    write_attempts: Object.freeze([...child.writes]),
    external_effect_attempts: Object.freeze([...child.effects]),
    guard_evaluations: Object.freeze(child.guards.map((guard) =>
      Object.freeze({
        ...guard,
        controlled_effects: definition.guards.find(({guard_id}) =>
          guard_id === guard.guard_id)?.controlled_effects ?? [],
      }))),
    trace: Object.freeze([...child.trace]),
    atomicity: Object.freeze({
      mode: child.commit_mode,
      outcome: child.commit_count > 0 ? "committed" as const :
        "rolled-back" as const,
    }),
    outcome: child.result,
    emitted_events: Object.freeze([...child.events]),
    continuation: Object.freeze({
      closure: child.continuation_closure ?? "missing-continuation",
      closed: child.close_count === 1,
      pending_effect_count: 0,
    }),
    relation_assertions: Object.freeze(definition.relation_contracts.map(
      (contract) => Object.freeze({
        contract_id: contract.contract_id,
        architecture_relation_id: contract.architecture_relation_id,
        source_type: contract.source_types[0]!,
        target_type: contract.target_types[0]!,
        assertion_owner: contract.assertion_owner,
        owner_evidence_sha256: contract.owner_evidence_sha256,
        exact_assertion: true,
      }),
    )),
    authority_effect: "none",
  });

const verifyAuthoritativeCatalogues = (
  raw: PythonOperationRawInputs,
  definition: StateChangingActionDefinitionV1,
): readonly OperationHostileFixtureV1[] => {
  const hostileEntries = Object.entries(PYTHON_OPERATION_HOSTILE_PATHS)
    .map(([role, path]) => Object.freeze({role, path,
      fixture: decodeOperationHostileFixtureV1(
        raw[role as keyof PythonOperationRawInputs],
      )}));
  const baseEntries = hostileEntries.filter(({fixture}) =>
    fixture.schema_version === "StateChangingActionHostile/v1");
  const s1Entries = hostileEntries.filter(({fixture}) =>
    fixture.schema_version === "StateChangingActionS1Hostile/v1");
  const catalogue = parseJson(
    raw.hostile_catalogue,
    "PY_OP_HOSTILE_CATALOGUE_INVALID",
  );
  if (!Array.isArray(catalogue.groups) ||
      !Array.isArray(catalogue.cross_type_controls)) {
    return fail("PY_OP_HOSTILE_CATALOGUE_INVALID");
  }
  const group = catalogue.groups.find((entry) =>
    isObject(entry) && entry.type === "Operation");
  if (!isObject(group) || !Array.isArray(group.controls) ||
      group.controls.length !== 14 || baseEntries.length !== 14 ||
      s1Entries.length !== OPERATION_S1_CATALOGUE_BINDINGS.length) {
    return fail("PY_OP_HOSTILE_CATALOGUE_INVALID");
  }
  for (const [index, entry] of baseEntries.entries()) {
    const hostile = entry.fixture;
    const control = group.controls[index];
    if (!isObject(control) || control.hostile_id !== hostile.hostile_id ||
        control.expected_code !== hostile.expected_code ||
        control.fixture_path !== entry.path) {
      return fail("PY_OP_HOSTILE_CATALOGUE_MISMATCH", hostile.hostile_id);
    }
  }
  const s1Controls = catalogue.cross_type_controls.filter((entry) =>
    isObject(entry) && entry.fixture_owner_swu === "RMT-OP-002");
  if (s1Controls.length !== OPERATION_S1_CATALOGUE_BINDINGS.length) {
    return fail("PY_OP_S1_CATALOGUE_INVALID");
  }
  for (const [index, expected] of OPERATION_S1_CATALOGUE_BINDINGS.entries()) {
    const entry = s1Entries[index];
    const hostile = entry?.fixture as OperationS1HostileFixtureV1 | undefined;
    const control = s1Controls[index];
    if (entry?.role !== expected.role || !hostile || !isObject(control) ||
        hostile.hostile_id !== expected.hostile_id ||
        hostile.expected_code !== expected.expected_code ||
        hostile.category !== expected.category ||
        hostile.required_observation !== expected.required_observation ||
        hostile.required_outcome !== expected.required_outcome ||
        control.hostile_id !== expected.hostile_id ||
        control.hostile_class !== "s1-cross-boundary" ||
        control.expected_code !== expected.expected_code ||
        control.fixture_owner_swu !== "RMT-OP-002" ||
        control.proof_owner_swu !== "RMT-OP-006" ||
        control.fixture_path !== entry.path ||
        control.non_noop_required !== true ||
        control.category !== expected.category ||
        control.required_observation !== expected.required_observation ||
        control.required_outcome !== expected.required_outcome) {
      return fail("PY_OP_S1_CATALOGUE_MISMATCH", expected.hostile_id);
    }
  }
  const relations = parseJson(
    raw.relation_contracts,
    "PY_OP_RELATION_CONTRACTS_INVALID",
  );
  if (!Array.isArray(relations.type_contracts)) {
    return fail("PY_OP_RELATION_CONTRACTS_INVALID");
  }
  const operationRelations = relations.type_contracts.find((entry) =>
    isObject(entry) && entry.type === "Operation");
  if (!isObject(operationRelations) ||
      !Array.isArray(operationRelations.contracts) ||
      operationRelations.contracts.length !==
        definition.relation_contracts.length) {
    return fail("PY_OP_RELATION_CONTRACTS_INVALID");
  }
  for (const [index, contract] of definition.relation_contracts.entries()) {
    const authority = operationRelations.contracts[index];
    if (!isObject(authority) ||
        authority.contract_id !== contract.contract_id ||
        authority.architecture_relation_id !==
          contract.architecture_relation_id ||
        canonicalOperationJson(authority.source_types) !==
          canonicalOperationJson(contract.source_types) ||
        canonicalOperationJson(authority.target_types) !==
          canonicalOperationJson(contract.target_types) ||
        authority.assertion_owner_mapping !== contract.assertion_owner) {
      return fail("PY_OP_RELATION_CONTRACT_MISMATCH", contract.contract_id);
    }
  }
  return Object.freeze(hostileEntries.map(({fixture}) => fixture));
};

export const composePythonOperationProof = (input: Readonly<{
  raw_inputs: PythonOperationRawInputs;
  native_proof: unknown;
}>) => {
  const raw = input.raw_inputs;
  const binding = validatePythonOperationRawInputs(raw);
  const native = decodeNativeProof(input.native_proof);
  if (native.binding.binding_id !== binding.binding_id ||
      native.binding.binding_sha256 !== binding.binding_sha256 ||
      native.source_proof.source_sha256 !== binding.refs.source.sha256 ||
      native.source_proof.symbol_name !== binding.symbol_name) {
    return fail("PY_OP_NATIVE_BINDING_MISMATCH");
  }
  const definition = decodeStateChangingActionDefinitionV1(
    raw.definition,
    PYTHON_OPERATION_RAW_PATHS.admission,
    raw.admission,
  );
  const denominator = decodeStateChangingActionDenominatorV1(
    raw.denominator,
    PYTHON_OPERATION_RAW_PATHS.definition,
    raw.definition,
    definition,
  );
  const familyPositives = decodeStateChangingActionObservationSetV1(
    raw.positive_observations,
    definition,
    PYTHON_OPERATION_RAW_PATHS.definition,
    raw.definition,
    denominator,
    raw.denominator,
  );
  for (const positive of familyPositives.observations) {
    if (evaluateStateChangingAction(
      definition,
      denominator,
      positive,
    ).verdict !== "pass") {
      return fail("PY_OP_FAMILY_POSITIVE_BASELINE_BLOCKED");
    }
  }
  const hostiles = verifyAuthoritativeCatalogues(raw, definition);
  const observations = new Map<string, StateChangingActionObservationV1>();
  for (const child of native.owner_cases) {
    const observation = observationFromNative(
      child,
      definition,
      raw.definition,
      denominator,
      raw.denominator,
    );
    const evaluation = evaluateStateChangingAction(
      definition,
      denominator,
      observation,
    );
    if (evaluation.verdict !== "pass") {
      return fail(
        "PY_OP_TARGET_POSITIVE_BLOCKED",
        evaluation.findings.map(({code}) => code).join(","),
      );
    }
    observations.set(child.case_id, observation);
  }
  const sourceHashes = new Set<string>();
  const sourceControls = native.source_controls.map((control) => {
    if (control.source_sha256 === binding.refs.source.sha256 ||
        sourceHashes.has(control.source_sha256)) {
      return fail("PY_OP_SOURCE_CONTROL_NOOP", control.control_id);
    }
    sourceHashes.add(control.source_sha256);
    const observation = observationFromNative(
      control.observation,
      definition,
      raw.definition,
      denominator,
      raw.denominator,
    );
    const baseline = observations.get(control.case_id)!;
    if (sha256OperationValue(observation) ===
        sha256OperationValue(baseline)) {
      return fail("PY_OP_SOURCE_CONTROL_SEMANTIC_NOOP", control.control_id);
    }
    const evaluation = evaluateStateChangingAction(
      definition,
      denominator,
      observation,
    );
    const codes = Object.freeze(evaluation.findings.map(({code}) => code));
    if (evaluation.verdict !== "fail" ||
        !codes.includes(control.expected_code)) {
      return fail("PY_OP_SOURCE_CONTROL_SURVIVED", control.control_id);
    }
    return Object.freeze({
      control_id: control.control_id,
      expected_code: control.expected_code,
      finding_codes: codes,
      source_sha256: control.source_sha256,
      status: "killed" as const,
    });
  });
  const familyControls = hostiles.map((hostile) => {
    if (hostile.schema_version === "StateChangingActionS1Hostile/v1") {
      const observed = applyOperationS1Mutation(
        hostile.baseline,
        hostile.mutation,
      );
      const evaluation = evaluateOperationS1Residue(observed);
      const codes = evaluation.findings.map(({code}) => code);
      if (evaluation.verdict !== "reject" ||
          evaluation.required_residue_observed !== true ||
          codes.length !== 1 || codes[0] !== hostile.expected_code ||
          hostile.expected_code !==
            OPERATION_EXPECTED_DIAGNOSTIC[hostile.hostile_id]) {
        return fail("PY_OP_S1_FAMILY_CONTROL_SURVIVED", hostile.hostile_id);
      }
      return Object.freeze({
        hostile_id: hostile.hostile_id,
        finding_codes: Object.freeze(codes),
        required_residue_observed: true as const,
        status: "killed" as const,
      });
    }
    const base = hostile.hostile_id === "op/guard-bypass" ||
        hostile.hostile_id === "op/success-failure-collapse"
      ? observations.get("guard-rejected")!
      : observations.get("committed-success")!;
    const mutated = applyOperationHostile(base, hostile.hostile_id);
    if (sha256OperationValue(mutated) === sha256OperationValue(base)) {
      return fail("PY_OP_FAMILY_CONTROL_NOOP", hostile.hostile_id);
    }
    const evaluation = evaluateStateChangingAction(
      definition,
      denominator,
      mutated,
    );
    const codes = evaluation.findings.map(({code}) => code);
    if (evaluation.verdict !== "fail" || codes.length !== 1 ||
        codes[0] !== hostile.expected_code) {
      return fail("PY_OP_FAMILY_CONTROL_SURVIVED", hostile.hostile_id);
    }
    return Object.freeze({
      hostile_id: hostile.hostile_id,
      finding_codes: Object.freeze(codes),
      status: "killed" as const,
    });
  });
  const claimCeiling =
    "one candidate-local Python bound Operation proven for committed success " +
    "and guard rejection through an AST and bytecode audited injected-port " +
    "observer, two fresh processes per owner case, ten native source controls, " +
    "fourteen base portable family controls, and five frozen S1 " +
    "cross-boundary residue controls; not arbitrary Python, " +
    "exactly-once distributed delivery, cross-language parity, registry " +
    "admission, publication, deployment, or production";
  return Object.freeze({
    schema_version: "PythonOperationComposedProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      language: "python" as const,
      protocol_id: binding.protocol_id,
      symbol_name: binding.symbol_name,
      source_sha256: binding.refs.source.sha256,
    }),
    binding: Object.freeze({
      binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
      bound_role_count: Object.keys(binding.refs).length,
      observer_sha256: binding.refs.observer.sha256,
      supervisor_sha256: binding.refs.supervisor.sha256,
      proof_builder_sha256: binding.refs.proof_builder.sha256,
      provider_sha256: binding.refs.provider.sha256,
    }),
    native_process_evidence: native.process_evidence,
    observations: Object.freeze([...observations.values()]),
    source_controls: Object.freeze(sourceControls),
    family_controls: Object.freeze(familyControls),
    accounting: Object.freeze({
      positives: Object.freeze({declared: 2, passed: 2}),
      native_source_controls: Object.freeze({declared: 10, killed: 10}),
      family_controls: Object.freeze({declared: 19, killed: 19}),
      mutants: Object.freeze({declared: 29, killed: 29}),
    }),
    claim_ceiling: claimCeiling,
    authority_effect: "none" as const,
  });
};
