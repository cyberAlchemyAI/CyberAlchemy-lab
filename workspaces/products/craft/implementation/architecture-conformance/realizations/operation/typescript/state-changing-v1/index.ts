import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {promisify} from "node:util";
import ts from "typescript";

import {
  OPERATION_EXPECTED_DIAGNOSTIC,
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
} from "../../../../families/state-changing-action/providers/decode-state-changing-action.js";
import {
  applyTypeScriptOperationSourceControl,
  inspectTypeScriptOperationClosedSubset,
  TYPESCRIPT_OPERATION_OBSERVER_ID,
  TYPESCRIPT_OPERATION_SOURCE_CONTROLS,
} from "./closed-subset.js";
import type {CompleteSettlementOperationOutcome} from
  "../../../../targets/typescript/operation-v1.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const TYPESCRIPT_OPERATION_HOSTILE_PATHS = Object.freeze({
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

export const TYPESCRIPT_OPERATION_RAW_PATHS = Object.freeze({
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
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/operation-v1.ts",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/typescript/state-changing-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/typescript/state-changing-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/operation-typescript-v1.ts",
  provider_contract:
    "projects/domainspec-v2/impl/architecture-conformance/factory/contracts/factory-node-provider-v1.ts",
  ...TYPESCRIPT_OPERATION_HOSTILE_PATHS,
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/operation/typescript/state-changing-v1/typescript-binding.json",
});

export type TypeScriptOperationRawInputs = Readonly<Record<
  keyof typeof TYPESCRIPT_OPERATION_RAW_PATHS,
  string
>>;

type BoundRole = Exclude<keyof TypeScriptOperationRawInputs, "binding">;
type TypeScriptOperationBindingV1 = Readonly<{
  schema_version: "TypeScriptOperationBinding/v1";
  binding_id: "typescript.complete-settlement.bound-operation/v1";
  target_id: "operation.typescript.complete-settlement/v1";
  protocol_id: "typescript.bound-operation/v1";
  symbol_name: "completeSettlementOperation";
  observer_id: typeof TYPESCRIPT_OPERATION_OBSERVER_ID;
  observer_owner_ref: "typescript-operation-proof-harness";
  proof_mechanism:
    "injected-port-observation-plus-two-fresh-processes-per-owner-case";
  refs: Readonly<Record<BoundRole, ExactRef>>;
  authority_effect: "none";
  binding_sha256: string;
}>;

const executeFile = promisify(execFile);
const SHA256 = /^[a-f0-9]{64}$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string | Uint8Array): string => createHash("sha256")
  .update(value).digest("hex");
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const canonical = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonical)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonical(child)]))
    : value;
const fail = (code: string, detail?: string): never => {
  throw Object.assign(
    new Error(detail === undefined ? code : `${code}:${detail}`),
    {code},
  );
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
const bindingBody = (binding: TypeScriptOperationBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};

const decodeBinding = (
  bytes: string,
  raw: TypeScriptOperationRawInputs,
): TypeScriptOperationBindingV1 => {
  const value = parseJson(bytes, "TS_OP_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id", "symbol_name",
    "observer_id", "observer_owner_ref", "proof_mechanism", "refs",
    "authority_effect", "binding_sha256",
  ], "TS_OP_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "TypeScriptOperationBinding/v1" ||
      value.binding_id !==
        "typescript.complete-settlement.bound-operation/v1" ||
      value.target_id !== "operation.typescript.complete-settlement/v1" ||
      value.protocol_id !== "typescript.bound-operation/v1" ||
      value.symbol_name !== "completeSettlementOperation" ||
      value.observer_id !== TYPESCRIPT_OPERATION_OBSERVER_ID ||
      value.observer_owner_ref !== "typescript-operation-proof-harness" ||
      value.proof_mechanism !==
        "injected-port-observation-plus-two-fresh-processes-per-owner-case" ||
      value.authority_effect !== "none" ||
      typeof value.binding_sha256 !== "string" ||
      !SHA256.test(value.binding_sha256) || !isObject(value.refs)) {
    return fail("TS_OP_BINDING_POLICY_INVALID");
  }
  const boundRoles = Object.keys(TYPESCRIPT_OPERATION_RAW_PATHS)
    .filter((role): role is BoundRole => role !== "binding");
  exactKeys(value.refs, boundRoles, "TS_OP_BINDING_REFS_INVALID");
  const refs = {} as Record<BoundRole, ExactRef>;
  for (const role of boundRoles) {
    const ref = value.refs[role];
    if (!isObject(ref)) return fail("TS_OP_BINDING_REF_INVALID", role);
    exactKeys(ref, ["path", "sha256"], "TS_OP_BINDING_REF_INVALID");
    const expectedPath = TYPESCRIPT_OPERATION_RAW_PATHS[role];
    if (ref.path !== expectedPath || typeof ref.sha256 !== "string" ||
        !SHA256.test(ref.sha256)) {
      return fail("TS_OP_BINDING_REF_INVALID", role);
    }
    if (sha256(raw[role]) !== ref.sha256) {
      return fail("TS_OP_BINDING_INPUT_STALE", role);
    }
    refs[role] = Object.freeze({path: expectedPath, sha256: ref.sha256});
  }
  const binding = Object.freeze({
    ...value,
    schema_version: "TypeScriptOperationBinding/v1" as const,
    binding_id: "typescript.complete-settlement.bound-operation/v1" as const,
    target_id: "operation.typescript.complete-settlement/v1" as const,
    protocol_id: "typescript.bound-operation/v1" as const,
    symbol_name: "completeSettlementOperation" as const,
    observer_id: TYPESCRIPT_OPERATION_OBSERVER_ID,
    observer_owner_ref: "typescript-operation-proof-harness" as const,
    proof_mechanism:
      "injected-port-observation-plus-two-fresh-processes-per-owner-case" as const,
    refs: Object.freeze(refs),
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) as TypeScriptOperationBindingV1;
  if (sha256(JSON.stringify(canonical(bindingBody(binding)))) !==
      binding.binding_sha256) {
    return fail("TS_OP_BINDING_DIGEST_STALE");
  }
  return binding;
};

const CHILD_SCRIPT = `
const source = Buffer.from(process.env.DS_OP_SOURCE ?? "", "base64").toString("utf8");
const caseId = process.env.DS_OP_CASE;
const moduleUrl = "data:text/javascript;base64," + Buffer.from(source).toString("base64");
const target = await import(moduleUrl);
const trace = [];
const reads = [];
const writes = [];
const effects = [];
const events = [];
const guards = [];
let commitMode = "all-or-nothing";
let commitCount = 0;
let rollbackCount = 0;
let beginCount = 0;
let closeCount = 0;
let continuationClosure = null;
const allowed = caseId === "committed-success";
const input = {settlement_id: "settlement-001",
  expected_state_version: allowed ? 7 : 6};
const ports = {
  guard: async (guardId, guardInput) => {
    trace.push("guard:" + guardId);
    guards.push({guard_id: guardId, invoked: true,
      decision: allowed ? "pass" : "fail",
      current_state_version_observed:
        guardInput?.settlement_id === input.settlement_id &&
        guardInput?.expected_state_version === input.expected_state_version});
    return {allowed};
  },
  read: async (targetId, settlementId) => {
    reads.push(targetId);
    trace.push("read:" + targetId);
    return targetId === "settlement.read.settlement-by-id"
      ? {settlement_id: settlementId}
      : {account_id: "account-001"};
  },
  beginAtomic: async () => {
    beginCount += 1;
    trace.push("atomic:begin");
    return {
      write: async (targetId) => {
        writes.push(targetId);
        trace.push("write:" + targetId);
      },
      commit: async (mode = "all-or-nothing") => {
        commitMode = mode;
        commitCount += 1;
        trace.push("atomic:commit");
      },
      rollback: async () => {
        rollbackCount += 1;
        trace.push("atomic:rollback");
      },
    };
  },
  externalEffect: async (targetId, event) => {
    effects.push(targetId);
    trace.push("effect:" + targetId);
    trace.push("event:" + event.event_type);
    events.push({event_type: event.event_type, tense: "past-tense",
      trace_ordinal: trace.length - 1});
  },
  close: async (closure, failureCode) => {
    continuationClosure = closure;
    if (failureCode !== null) trace.push("outcome:failure");
    trace.push("continuation:close");
    closeCount += 1;
  },
};
const result = await target.completeSettlementOperation(input, ports);
if (result.kind === "success") trace.push("outcome:success");
process.stdout.write(JSON.stringify({pid: process.pid, case_id: caseId, input,
  result, trace, reads, writes, effects, events, guards, commitMode,
  commitCount, rollbackCount, beginCount, closeCount, continuationClosure}));
`;

type ChildResult = Readonly<{
  pid: number;
  case_id: "committed-success" | "guard-rejected";
  input: Readonly<{settlement_id: string; expected_state_version: number}>;
  result: CompleteSettlementOperationOutcome;
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
  commitMode: "all-or-nothing" | "best-effort";
  commitCount: number;
  rollbackCount: number;
  beginCount: number;
  closeCount: number;
  continuationClosure: string | null;
}>;

const compileTarget = (source: string): string => {
  inspectTypeScriptOperationClosedSubset(source);
  const result = ts.transpileModule(source, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
      strict: true,
      isolatedModules: true,
    },
    fileName: "operation-v1.ts",
    reportDiagnostics: true,
  });
  if ((result.diagnostics ?? []).some((diagnostic) =>
    diagnostic.category === ts.DiagnosticCategory.Error)) {
    return fail("TS_OP_COMPILE_FAILED");
  }
  return result.outputText;
};

const runFreshProcess = async (
  compiledSource: string,
  caseId: ChildResult["case_id"],
): Promise<ChildResult> => {
  const {stdout, stderr} = await executeFile(process.execPath, [
    "--input-type=module", "--eval", CHILD_SCRIPT,
  ], {
    env: {
      DS_OP_SOURCE: Buffer.from(compiledSource, "utf8").toString("base64"),
      DS_OP_CASE: caseId,
    },
    timeout: 10_000,
    maxBuffer: 1_048_576,
  }).catch((error: unknown) => fail(
    "TS_OP_FRESH_PROCESS_FAILED",
    error instanceof Error ? error.message : String(error),
  ));
  if (stderr.length > 0) return fail("TS_OP_FRESH_PROCESS_STDERR", stderr);
  const value = parseJson(stdout, "TS_OP_FRESH_PROCESS_OUTPUT_INVALID");
  if (!Number.isSafeInteger(value.pid) ||
      !["committed-success", "guard-rejected"].includes(
        value.case_id as string,
      ) || !isObject(value.input) || !isObject(value.result) ||
      !Array.isArray(value.trace) || !Array.isArray(value.reads) ||
      !Array.isArray(value.writes) || !Array.isArray(value.effects) ||
      !Array.isArray(value.events) || !Array.isArray(value.guards)) {
    return fail("TS_OP_FRESH_PROCESS_OUTPUT_INVALID");
  }
  return Object.freeze(value as unknown as ChildResult);
};

const observationFromChild = (
  child: ChildResult,
  definition: StateChangingActionDefinitionV1,
  definitionRaw: string,
  denominator: StateChangingActionDenominatorV1,
  denominatorRaw: string,
): StateChangingActionObservationV1 =>
  mintStateChangingActionObservationV1({
    schema_version: "StateChangingActionObservation/v1",
    observation_id:
      `observation.operation.typescript.complete-settlement.${child.case_id}/v1`,
    case_id: child.case_id,
    source_kind: "target-observation",
    definition_ref: Object.freeze({
      definition_id: definition.definition_id,
      path: TYPESCRIPT_OPERATION_RAW_PATHS.definition,
      sha256: sha256OperationBytes(definitionRaw),
    }),
    denominator_ref: Object.freeze({
      denominator_id: denominator.denominator_id,
      sha256: sha256OperationBytes(denominatorRaw),
    }),
    observer: Object.freeze({
      observer_id: TYPESCRIPT_OPERATION_OBSERVER_ID,
      ownership: "independent-proof-harness",
    }),
    operation_id: definition.operation_id,
    transition_started: child.beginCount > 0 || child.writes.length > 0,
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
      mode: child.commitMode,
      outcome: child.commitCount > 0 ? "committed" as const :
        "rolled-back" as const,
    }),
    outcome: child.result,
    emitted_events: Object.freeze([...child.events]),
    continuation: Object.freeze({
      closure: child.continuationClosure ?? "missing-continuation",
      closed: child.closeCount === 1,
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
  raw: TypeScriptOperationRawInputs,
  definition: StateChangingActionDefinitionV1,
): readonly OperationHostileFixtureV1[] => {
  const hostileEntries = Object.entries(TYPESCRIPT_OPERATION_HOSTILE_PATHS)
    .map(([role, path]) => Object.freeze({role, path,
      fixture: decodeOperationHostileFixtureV1(
        raw[role as keyof TypeScriptOperationRawInputs],
      )}));
  const baseEntries = hostileEntries.filter(({fixture}) =>
    fixture.schema_version === "StateChangingActionHostile/v1");
  const s1Entries = hostileEntries.filter(({fixture}) =>
    fixture.schema_version === "StateChangingActionS1Hostile/v1");
  const catalogue = parseJson(
    raw.hostile_catalogue,
    "TS_OP_HOSTILE_CATALOGUE_INVALID",
  );
  if (!Array.isArray(catalogue.groups) ||
      !Array.isArray(catalogue.cross_type_controls)) {
    return fail("TS_OP_HOSTILE_CATALOGUE_INVALID");
  }
  const group = catalogue.groups.find((entry) =>
    isObject(entry) && entry.type === "Operation");
  if (!isObject(group) || !Array.isArray(group.controls) ||
      group.controls.length !== 14 || baseEntries.length !== 14 ||
      s1Entries.length !== OPERATION_S1_CATALOGUE_BINDINGS.length) {
    return fail("TS_OP_HOSTILE_CATALOGUE_INVALID");
  }
  for (const [index, entry] of baseEntries.entries()) {
    const hostile = entry.fixture;
    const control = group.controls[index];
    if (!isObject(control) || control.hostile_id !== hostile.hostile_id ||
        control.expected_code !== hostile.expected_code ||
        control.fixture_path !== entry.path) {
      return fail("TS_OP_HOSTILE_CATALOGUE_MISMATCH", hostile.hostile_id);
    }
  }
  const s1Controls = catalogue.cross_type_controls.filter((entry) =>
    isObject(entry) && entry.fixture_owner_swu === "RMT-OP-002");
  if (s1Controls.length !== OPERATION_S1_CATALOGUE_BINDINGS.length) {
    return fail("TS_OP_S1_CATALOGUE_INVALID");
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
      return fail("TS_OP_S1_CATALOGUE_MISMATCH", expected.hostile_id);
    }
  }

  const relations = parseJson(
    raw.relation_contracts,
    "TS_OP_RELATION_CONTRACTS_INVALID",
  );
  if (!Array.isArray(relations.type_contracts)) {
    return fail("TS_OP_RELATION_CONTRACTS_INVALID");
  }
  const operationRelations = relations.type_contracts.find((entry) =>
    isObject(entry) && entry.type === "Operation");
  if (!isObject(operationRelations) ||
      !Array.isArray(operationRelations.contracts) ||
      operationRelations.contracts.length !==
        definition.relation_contracts.length) {
    return fail("TS_OP_RELATION_CONTRACTS_INVALID");
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
      return fail("TS_OP_RELATION_CONTRACT_MISMATCH", contract.contract_id);
    }
  }
  return Object.freeze(hostileEntries.map(({fixture}) => fixture));
};

export const buildTypeScriptOperationProof = async (
  raw: TypeScriptOperationRawInputs,
) => {
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeStateChangingActionDefinitionV1(
    raw.definition,
    TYPESCRIPT_OPERATION_RAW_PATHS.admission,
    raw.admission,
  );
  const denominator = decodeStateChangingActionDenominatorV1(
    raw.denominator,
    TYPESCRIPT_OPERATION_RAW_PATHS.definition,
    raw.definition,
    definition,
  );
  const familyPositives = decodeStateChangingActionObservationSetV1(
    raw.positive_observations,
    definition,
    TYPESCRIPT_OPERATION_RAW_PATHS.definition,
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
      return fail("TS_OP_FAMILY_POSITIVE_BASELINE_BLOCKED");
    }
  }
  const hostiles = verifyAuthoritativeCatalogues(raw, definition);
  const closedSubset = inspectTypeScriptOperationClosedSubset(raw.source);
  if (closedSubset.source_sha256 !== binding.refs.source.sha256 ||
      closedSubset.observer_id !== binding.observer_id) {
    return fail("TS_OP_CLOSED_SUBSET_BINDING_STALE");
  }

  const compiled = compileTarget(raw.source);
  const observations = new Map<
    ChildResult["case_id"],
    StateChangingActionObservationV1
  >();
  const processPairs = [];
  for (const caseId of [
    "committed-success", "guard-rejected",
  ] as const) {
    const first = await runFreshProcess(compiled, caseId);
    const second = await runFreshProcess(compiled, caseId);
    if (first.pid === second.pid) return fail("TS_OP_PROCESS_ISOLATION_FAILED");
    const {pid: _firstPid, ...firstSemantic} = first;
    const {pid: _secondPid, ...secondSemantic} = second;
    if (canonicalOperationJson(firstSemantic) !==
        canonicalOperationJson(secondSemantic)) {
      return fail("TS_OP_PROCESS_REPLAY_DRIFT", caseId);
    }
    const observation = observationFromChild(
      first,
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
        "TS_OP_TARGET_POSITIVE_BLOCKED",
        evaluation.findings.map(({code}) => code).join(","),
      );
    }
    observations.set(caseId, observation);
    processPairs.push(Object.freeze({
      case_id: caseId,
      first_pid: first.pid,
      second_pid: second.pid,
      semantic_sha256: sha256(canonicalOperationJson(firstSemantic)),
    }));
  }

  const sourceControlResults = [];
  for (const control of TYPESCRIPT_OPERATION_SOURCE_CONTROLS) {
    const mutatedSource = applyTypeScriptOperationSourceControl(
      raw.source,
      control.control_id,
    );
    const caseId = control.control_id === "ts-op/guard-bypass" ||
        control.control_id === "ts-op/success-failure-collapse"
      ? "guard-rejected" as const : "committed-success" as const;
    const child = await runFreshProcess(compileTarget(mutatedSource), caseId);
    const observation = observationFromChild(
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
    const codes = Object.freeze(evaluation.findings.map(({code}) => code));
    if (evaluation.verdict !== "fail" ||
        !codes.includes(control.expected_code)) {
      return fail("TS_OP_SOURCE_CONTROL_SURVIVED", control.control_id);
    }
    sourceControlResults.push(Object.freeze({
      control_id: control.control_id,
      status: "killed" as const,
      expected_code: control.expected_code,
      finding_codes: codes,
      source_sha256: sha256(mutatedSource),
    }));
  }

  const familyControlResults = [];
  for (const hostile of hostiles) {
    if (hostile.schema_version === "StateChangingActionS1Hostile/v1") {
      const observed = applyOperationS1Mutation(
        hostile.baseline,
        hostile.mutation,
      );
      const evaluation = evaluateOperationS1Residue(observed);
      const codes = evaluation.findings.map(({code}) => code);
      if (evaluation.verdict !== "reject" ||
          evaluation.required_residue_observed !== true ||
          canonicalOperationJson(codes) !==
            canonicalOperationJson([hostile.expected_code]) ||
          hostile.expected_code !==
            OPERATION_EXPECTED_DIAGNOSTIC[hostile.hostile_id]) {
        return fail("TS_OP_S1_FAMILY_CONTROL_SURVIVED", hostile.hostile_id);
      }
      familyControlResults.push(Object.freeze({
        hostile_id: hostile.hostile_id,
        status: "killed" as const,
        finding_codes: Object.freeze(codes),
        required_residue_observed: true as const,
      }));
      continue;
    }
    const base = hostile.hostile_id === "op/guard-bypass" ||
        hostile.hostile_id === "op/success-failure-collapse"
      ? observations.get("guard-rejected")!
      : observations.get("committed-success")!;
    const mutated = applyOperationHostile(base, hostile.hostile_id);
    const evaluation = evaluateStateChangingAction(
      definition,
      denominator,
      mutated,
    );
    const codes = evaluation.findings.map(({code}) => code);
    if (evaluation.verdict !== "fail" ||
        canonicalOperationJson(codes) !==
          canonicalOperationJson([hostile.expected_code]) ||
        hostile.expected_code !==
          OPERATION_EXPECTED_DIAGNOSTIC[hostile.hostile_id]) {
      return fail("TS_OP_FAMILY_CONTROL_SURVIVED", hostile.hostile_id);
    }
    familyControlResults.push(Object.freeze({
      hostile_id: hostile.hostile_id,
      status: "killed" as const,
      finding_codes: Object.freeze(codes),
    }));
  }

  return Object.freeze({
    schema_version: "TypeScriptOperationComposedProof/v1" as const,
    result: "pass" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      protocol_id: binding.protocol_id,
      language: "typescript" as const,
      symbol_name: binding.symbol_name,
      source_sha256: binding.refs.source.sha256,
    }),
    binding: Object.freeze({
      binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
      observer_sha256: binding.refs.observer.sha256,
      proof_builder_sha256: binding.refs.proof_builder.sha256,
      provider_sha256: binding.refs.provider.sha256,
      bound_role_count: Object.keys(binding.refs).length,
    }),
    closed_subset_proof: closedSubset,
    runtime_proof: Object.freeze({
      owner_cases: 2 as const,
      fresh_processes: 4 as const,
      distinct_pid_pairs: 2 as const,
      process_pairs: Object.freeze(processPairs),
      observer_origin: "independent-injected-port-harness" as const,
    }),
    observations: Object.freeze([...observations.values()]),
    source_controls: Object.freeze(sourceControlResults),
    family_controls: Object.freeze(familyControlResults),
    accounting: Object.freeze({
      positives: Object.freeze({declared: 2 as const, passed: 2 as const}),
      target_source_controls: Object.freeze({
        declared: 10 as const,
        killed: 10 as const,
      }),
      family_controls: Object.freeze({
        declared: 19 as const,
        killed: 19 as const,
      }),
      mutants: Object.freeze({declared: 29 as const, killed: 29 as const}),
    }),
    claim_ceiling: "one candidate-local TypeScript bound Operation target proven for committed success and guard rejection through independent injected-port observation, two fresh processes per owner case, ten target-source controls, fourteen base portable family controls, and five frozen S1 cross-boundary residue controls; not arbitrary TypeScript, exactly-once distributed delivery, cross-language parity, registry admission, publication, deployment, or production",
    authority_effect: "none" as const,
  });
};
