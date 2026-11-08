import {
  canonicalSfolJson,
  digestSfolValue,
} from "../cases/index.js";
import type {
  DerivedEffectCase,
  EffectContractAdmission,
  RawEffectObservation,
} from "../cases/effect.js";
import type {
  ResolvedEffectBinding,
} from "../bindings/effect.js";
import type { ClauseDenominator } from "../denominator/index.js";
import {
  evaluateEffectRelation,
} from "../evaluator/effect.js";
import type { TypedLogicModule } from "../language/typecheck.js";
import type {
  EffectTraceContract,
} from "../runners/effect/contracts.js";

export interface EffectCaseEvaluation {
  readonly schema_version: "domainspec-sfol-effect-case-evaluation/v1";
  readonly case_id: string;
  readonly case_digest: string;
  readonly binding_digest: string;
  readonly observation_digest: string;
  readonly trace_digest: string | null;
  readonly trace_contract_digest: string;
  readonly contract_admission_digest: string;
  readonly source_proposal_digest: string;
  readonly status: "pass" | "fail" | "indeterminate";
  readonly detail: string;
  readonly evaluation_digest: string;
}

export interface EffectProofStageSet {
  readonly stage:
    | "C_spec"
    | "C_projected"
    | "C_validated"
    | "C_typed"
    | "T_generated"
    | "C_bound"
    | "O_run"
    | "R_evaluated";
  readonly case_ids: readonly string[];
}

export interface EffectProofReceipt {
  readonly schema_version: "domainspec-sfol-effect-proof-receipt/v1";
  readonly status: "pass";
  readonly proof_context: ClauseDenominator["proof_context"];
  readonly source_proposal_digest: string;
  readonly contract_admission_digest: string;
  readonly trace_contract_digests: readonly string[];
  readonly artifact_digests: {
    readonly denominator: string;
    readonly typed: string;
    readonly cases: string;
    readonly bindings: string;
    readonly observations: string;
    readonly evaluations: string;
    readonly trace_contracts: string;
    readonly contract_admission: string;
    readonly tool: string;
  };
  readonly stage_sets: readonly EffectProofStageSet[];
  readonly case_count: number;
  readonly receipt_digest: string;
}

export interface EffectProofBuildInput {
  readonly denominator: ClauseDenominator;
  readonly typed_artifact_digest: string;
  readonly upstream_case_sets: {
    readonly C_spec: readonly string[];
    readonly C_projected: readonly string[];
    readonly C_validated: readonly string[];
    readonly C_typed: readonly string[];
  };
  readonly cases: readonly DerivedEffectCase[];
  readonly bindings: readonly ResolvedEffectBinding[];
  readonly observations: readonly RawEffectObservation[];
  readonly evaluations: readonly EffectCaseEvaluation[];
  readonly trace_contracts: readonly EffectTraceContract[];
  readonly contract_admission: EffectContractAdmission;
  readonly source_proposal_digest: string;
  readonly tool_digest: string;
}

export interface EffectReplayAllowlist {
  readonly receipt_digest: string;
  readonly denominator_digest: string;
  readonly typed_artifact_digest: string;
  readonly contract_admission_digest: string;
  readonly source_proposal_digest: string;
  readonly tool_digest: string;
}

export type EffectProofDiagnosticCode =
  | "SFOL_EFFECT_PROOF_CASE_STALE"
  | "SFOL_EFFECT_PROOF_BINDING_STALE"
  | "SFOL_EFFECT_PROOF_OBSERVATION_STALE"
  | "SFOL_EFFECT_PROOF_EVALUATION_STALE"
  | "SFOL_EFFECT_PROOF_CONTRACT_STALE"
  | "SFOL_EFFECT_PROOF_SET_MISMATCH"
  | "SFOL_EFFECT_PROOF_DUPLICATE_ID"
  | "SFOL_EFFECT_PROOF_NONPASS_STATE"
  | "SFOL_EFFECT_PROOF_INVALID_DIGEST"
  | "SFOL_EFFECT_REPLAY_NOT_ALLOWLISTED"
  | "SFOL_EFFECT_REPLAY_ARTIFACT_MUTATED"
  | "SFOL_EFFECT_REPLAY_REBUILD_FAILED";

export interface EffectProofDiagnostic {
  readonly code: EffectProofDiagnosticCode;
  readonly stage: "effect-proof" | "effect-replay";
  readonly subject: string;
  readonly detail: string;
}

export type EffectProofBuildResult =
  | {
      readonly ok: true;
      readonly value: EffectProofReceipt;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly EffectProofDiagnostic[];
    };

export type EffectReplayResult =
  | {
      readonly ok: true;
      readonly value: {
        readonly status: "pass";
        readonly receipt_digest: string;
        readonly replay_digest: string;
      };
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly EffectProofDiagnostic[];
    };

const SHA256 = /^[0-9a-f]{64}$/;

class EffectProofAbort extends Error {
  readonly diagnostic: EffectProofDiagnostic;

  constructor(diagnostic: EffectProofDiagnostic) {
    super(
      `${diagnostic.code}:${diagnostic.subject}:${diagnostic.detail}`,
    );
    this.name = "EffectProofAbort";
    this.diagnostic = diagnostic;
  }
}

export function evaluateEffectObservation(
  typed: TypedLogicModule,
  derived: DerivedEffectCase,
  binding: ResolvedEffectBinding,
  observation: RawEffectObservation,
  contract: EffectTraceContract,
): EffectCaseEvaluation {
  const finish = (
    status: EffectCaseEvaluation["status"],
    detail: string,
    traceDigest: string | null,
  ): EffectCaseEvaluation => {
    const unsigned = {
      schema_version:
        "domainspec-sfol-effect-case-evaluation/v1" as const,
      case_id: derived.case_id,
      case_digest: derived.case_digest,
      binding_digest: binding.binding_digest,
      observation_digest: observation.observation_digest,
      trace_digest: traceDigest,
      trace_contract_digest: derived.trace_contract_digest,
      contract_admission_digest:
        derived.contract_admission_digest,
      source_proposal_digest: derived.source_proposal_digest,
      status,
      detail,
    };
    return deepFreeze({
      ...unsigned,
      evaluation_digest: digestSfolValue(unsigned),
    });
  };

  if (
    binding.selector.case_id !== derived.case_id ||
    binding.selector.case_digest !== derived.case_digest ||
    observation.case_id !== derived.case_id ||
    observation.case_digest !== derived.case_digest ||
    observation.binding_id !== binding.binding.binding_id ||
    observation.adapter_id !== binding.binding.target.adapter_id ||
    observation.adapter_digest !==
      binding.binding.target.adapter_digest
  ) {
    return finish(
      "indeterminate",
      "case, binding, adapter, and observation identities are incompatible",
      null,
    );
  }
  if (
    binding.selector.trace_contract_digest !==
      derived.trace_contract_digest ||
    observation.trace_contract_digest !==
      derived.trace_contract_digest ||
    binding.selector.contract_admission_digest !==
      derived.contract_admission_digest ||
    observation.contract_admission_digest !==
      derived.contract_admission_digest ||
    binding.selector.source_proposal_digest !==
      derived.source_proposal_digest ||
    observation.source_proposal_digest !==
      derived.source_proposal_digest
  ) {
    return finish(
      "indeterminate",
      "contract admission or source proposal digest chain is incompatible",
      null,
    );
  }
  if (
    contract.contract_id !== derived.contract_id ||
    digestSfolValue(contract) !== derived.trace_contract_digest
  ) {
    return finish(
      "indeterminate",
      "effect trace contract identity or digest is stale",
      null,
    );
  }
  if (
    observation.status !== "observed" ||
    observation.trace === null
  ) {
    return finish(
      "indeterminate",
      observation.diagnostics[0]?.detail ??
        "contained harness did not produce a validated trace",
      null,
    );
  }
  const evaluation = evaluateEffectRelation(
    typed,
    derived.clause_id,
    contract,
    observation.trace,
    derived.inputs,
  );
  return finish(
    evaluation.status,
    evaluation.detail,
    observation.trace.trace_digest,
  );
}

export function buildEffectProofReceipt(
  input: EffectProofBuildInput,
): EffectProofBuildResult {
  try {
    for (const [subject, digest] of [
      ["denominator", input.denominator.digest],
      ["typed", input.typed_artifact_digest],
      ["source-proposal", input.source_proposal_digest],
      ["tool", input.tool_digest],
    ] as const) {
      requireDigest(digest, subject, "effect-proof");
    }
    if (input.cases.length === 0) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_SET_MISMATCH",
        "cases",
        "a passing effect proof requires at least one case",
      );
    }
    validateContractAdmission(input);
    validateCases(input.cases);
    validateBindings(input.bindings);
    validateObservations(input.observations);
    validateEvaluations(input.evaluations);
    const contracts = validateContracts(input.trace_contracts);

    const caseIds = sortedUnique(
      input.cases.map((derived) => derived.case_id),
      "T_generated",
    );
    const caseCoverage = [
      ...new Set(input.cases.map((derived) => derived.coverage_key)),
    ].sort();
    requireSameSet(
      [...input.denominator.coverage_keys].sort(),
      caseCoverage,
      "C_spec.coverage=T_generated.coverage",
    );
    const sourceIds = sortedUnique(
      input.upstream_case_sets.C_spec,
      "C_spec",
    );
    const projectedIds = sortedUnique(
      input.upstream_case_sets.C_projected,
      "C_projected",
    );
    const validatedIds = sortedUnique(
      input.upstream_case_sets.C_validated,
      "C_validated",
    );
    const typedIds = sortedUnique(
      input.upstream_case_sets.C_typed,
      "C_typed",
    );
    const boundIds = sortedUnique(
      input.bindings.map((binding) => binding.selector.case_id),
      "C_bound",
    );
    const observedIds = sortedUnique(
      input.observations.map(
        (observation) => observation.case_id,
      ),
      "O_run",
    );
    const evaluatedIds = sortedUnique(
      input.evaluations.map(
        (evaluation) => evaluation.case_id,
      ),
      "R_evaluated",
    );
    for (const [subject, actual] of [
      ["T_generated=C_spec", sourceIds],
      ["T_generated=C_projected", projectedIds],
      ["T_generated=C_validated", validatedIds],
      ["T_generated=C_typed", typedIds],
      ["T_generated=C_bound", boundIds],
      ["T_generated=O_run", observedIds],
      ["T_generated=R_evaluated", evaluatedIds],
    ] as const) {
      requireSameSet(caseIds, actual, subject);
    }
    validateJoins(input, contracts);

    const stageSets: readonly EffectProofStageSet[] =
      Object.freeze([
        Object.freeze({
          stage: "C_spec",
          case_ids: Object.freeze(sourceIds),
        }),
        Object.freeze({
          stage: "C_projected",
          case_ids: Object.freeze(projectedIds),
        }),
        Object.freeze({
          stage: "C_validated",
          case_ids: Object.freeze(validatedIds),
        }),
        Object.freeze({
          stage: "C_typed",
          case_ids: Object.freeze(typedIds),
        }),
        Object.freeze({
          stage: "T_generated",
          case_ids: Object.freeze([...caseIds]),
        }),
        Object.freeze({
          stage: "C_bound",
          case_ids: Object.freeze(boundIds),
        }),
        Object.freeze({
          stage: "O_run",
          case_ids: Object.freeze(observedIds),
        }),
        Object.freeze({
          stage: "R_evaluated",
          case_ids: Object.freeze(evaluatedIds),
        }),
      ]);
    const traceContractDigests = Object.freeze(
      contracts.map(({ digest }) => digest).sort(),
    );
    const unsigned = {
      schema_version:
        "domainspec-sfol-effect-proof-receipt/v1" as const,
      status: "pass" as const,
      proof_context: input.denominator.proof_context,
      source_proposal_digest: input.source_proposal_digest,
      contract_admission_digest:
        input.contract_admission.admission_digest,
      trace_contract_digests: traceContractDigests,
      artifact_digests: {
        denominator: input.denominator.digest,
        typed: input.typed_artifact_digest,
        cases: digestSfolValue(input.cases),
        bindings: digestSfolValue(input.bindings),
        observations: digestSfolValue(input.observations),
        evaluations: digestSfolValue(input.evaluations),
        trace_contracts: digestSfolValue(
          contracts.map(({ contract }) => contract),
        ),
        contract_admission: digestSfolValue(
          input.contract_admission,
        ),
        tool: input.tool_digest,
      },
      stage_sets: stageSets,
      case_count: caseIds.length,
    };
    return Object.freeze({
      ok: true,
      value: deepFreeze({
        ...unsigned,
        receipt_digest: digestSfolValue(unsigned),
      }),
    });
  } catch (error: unknown) {
    if (error instanceof EffectProofAbort) {
      return proofFailure(error.diagnostic);
    }
    return proofFailure({
      code: "SFOL_EFFECT_PROOF_NONPASS_STATE",
      stage: "effect-proof",
      subject: "proof",
      detail: "effect proof input is structurally invalid",
    });
  }
}

export function replayEffectProofReceipt(
  receipt: EffectProofReceipt,
  input: EffectProofBuildInput,
  allowlist: EffectReplayAllowlist,
): EffectReplayResult {
  if (
    receipt.receipt_digest !== allowlist.receipt_digest ||
    receipt.artifact_digests.denominator !==
      allowlist.denominator_digest ||
    receipt.artifact_digests.typed !==
      allowlist.typed_artifact_digest ||
    receipt.contract_admission_digest !==
      allowlist.contract_admission_digest ||
    receipt.source_proposal_digest !==
      allowlist.source_proposal_digest ||
    receipt.artifact_digests.tool !== allowlist.tool_digest
  ) {
    return replayFailure({
      code: "SFOL_EFFECT_REPLAY_NOT_ALLOWLISTED",
      stage: "effect-replay",
      subject: "allowlist",
      detail:
        "receipt or immutable dependency digest is not allowlisted",
    });
  }
  const rebuilt = buildEffectProofReceipt(input);
  if (!rebuilt.ok) {
    return replayFailure({
      code: "SFOL_EFFECT_REPLAY_REBUILD_FAILED",
      stage: "effect-replay",
      subject: "proof",
      detail:
        rebuilt.diagnostics[0]?.detail ?? "effect proof rebuild failed",
    });
  }
  if (
    rebuilt.value.receipt_digest !== receipt.receipt_digest ||
    canonicalSfolJson(rebuilt.value.artifact_digests) !==
      canonicalSfolJson(receipt.artifact_digests)
  ) {
    return replayFailure({
      code: "SFOL_EFFECT_REPLAY_ARTIFACT_MUTATED",
      stage: "effect-replay",
      subject: "artifacts",
      detail: "replayed raw artifact bytes do not match the receipt",
    });
  }
  const replayUnsigned = {
    status: "pass" as const,
    receipt_digest: receipt.receipt_digest,
  };
  return Object.freeze({
    ok: true,
    value: Object.freeze({
      ...replayUnsigned,
      replay_digest: digestSfolValue(replayUnsigned),
    }),
  });
}

function validateContractAdmission(
  input: EffectProofBuildInput,
): void {
  const admission = input.contract_admission;
  const { admission_digest: _digest, ...unsigned } = admission;
  if (
    admission.schema_version !==
      "domainspec-sfol-effect-contract-admission/v1" ||
    digestSfolValue(unsigned) !== admission.admission_digest
  ) {
    effectProofFail(
      "SFOL_EFFECT_PROOF_CONTRACT_STALE",
      "contract-admission",
      "contract admission digest is stale",
    );
  }
  if (
    admission.source_proposal_digest !==
      input.source_proposal_digest ||
    canonicalSfolJson(admission.proof_context) !==
      canonicalSfolJson(input.denominator.proof_context)
  ) {
    effectProofFail(
      "SFOL_EFFECT_PROOF_CONTRACT_STALE",
      "contract-admission",
      "contract admission source or proof context is incompatible",
    );
  }
}

function validateCases(cases: readonly DerivedEffectCase[]): void {
  for (const derived of cases) {
    const { case_digest: _digest, ...unsigned } = derived;
    if (
      derived.status !== "ready" ||
      derived.role !== "effects" ||
      digestSfolValue(unsigned) !== derived.case_digest
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_CASE_STALE",
        derived.case_id,
        "effect case status, role, or digest is stale",
      );
    }
  }
}

function validateBindings(
  bindings: readonly ResolvedEffectBinding[],
): void {
  for (const resolved of bindings) {
    const {
      binding_digest: _digest,
      ...unsigned
    } = resolved;
    if (
      resolved.binding.target.adapter_kind !== "effect-harness" ||
      canonicalSfolJson(resolved.selector) !==
        canonicalSfolJson(resolved.binding.selector) ||
      digestSfolValue(unsigned) !== resolved.binding_digest
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_BINDING_STALE",
        resolved.binding.binding_id,
        "only exact contained-harness bindings are proof eligible",
      );
    }
  }
}

function validateObservations(
  observations: readonly RawEffectObservation[],
): void {
  for (const observation of observations) {
    const { observation_digest: _digest, ...unsigned } = observation;
    if (
      digestSfolValue(unsigned) !== observation.observation_digest
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_OBSERVATION_STALE",
        observation.case_id,
        "observation digest does not match its raw content",
      );
    }
    if (
      observation.status !== "observed" ||
      observation.trace === null ||
      observation.containment === null ||
      !observation.containment.setup_completed ||
      !observation.containment.teardown_completed ||
      observation.containment.open_resources.length !== 0 ||
      observation.containment.timed_out
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_NONPASS_STATE",
        observation.case_id,
        "proof requires one contained, validated raw trace",
      );
    }
  }
}

function validateEvaluations(
  evaluations: readonly EffectCaseEvaluation[],
): void {
  for (const evaluation of evaluations) {
    const { evaluation_digest: _digest, ...unsigned } = evaluation;
    if (
      digestSfolValue(unsigned) !== evaluation.evaluation_digest
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_EVALUATION_STALE",
        evaluation.case_id,
        "evaluation digest does not match its content",
      );
    }
    if (evaluation.status !== "pass") {
      effectProofFail(
        "SFOL_EFFECT_PROOF_NONPASS_STATE",
        evaluation.case_id,
        `evaluation status ${evaluation.status} is not pass`,
      );
    }
  }
}

function validateContracts(
  contracts: readonly EffectTraceContract[],
): readonly {
  readonly contract: EffectTraceContract;
  readonly digest: string;
}[] {
  const normalized = contracts
    .map((contract) => ({
      contract,
      digest: digestSfolValue(contract),
    }))
    .sort((left, right) =>
      left.contract.contract_id.localeCompare(
        right.contract.contract_id,
      ),
    );
  const contractIds = normalized.map(
    ({ contract }) => contract.contract_id,
  );
  if (new Set(contractIds).size !== contractIds.length) {
    effectProofFail(
      "SFOL_EFFECT_PROOF_DUPLICATE_ID",
      "trace-contracts",
      "trace contract identities must be unique",
    );
  }
  return Object.freeze(normalized);
}

function validateJoins(
  input: EffectProofBuildInput,
  contracts: readonly {
    readonly contract: EffectTraceContract;
    readonly digest: string;
  }[],
): void {
  const bindingByCase = uniqueMap(
    input.bindings,
    (binding) => binding.selector.case_id,
    "bindings",
  );
  const observationByCase = uniqueMap(
    input.observations,
    (observation) => observation.case_id,
    "observations",
  );
  const evaluationByCase = uniqueMap(
    input.evaluations,
    (evaluation) => evaluation.case_id,
    "evaluations",
  );
  const contractById = new Map(
    contracts.map((entry) => [
      entry.contract.contract_id,
      entry,
    ]),
  );
  for (const derived of input.cases) {
    const binding = bindingByCase.get(derived.case_id);
    const observation = observationByCase.get(derived.case_id);
    const evaluation = evaluationByCase.get(derived.case_id);
    const contract = contractById.get(derived.contract_id);
    if (
      binding === undefined ||
      observation === undefined ||
      evaluation === undefined ||
      contract === undefined
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_SET_MISMATCH",
        derived.case_id,
        "one or more exact effect join members are absent",
      );
    }
    if (
      binding.selector.case_digest !== derived.case_digest ||
      binding.selector.fixture_digest !== derived.fixture_digest ||
      binding.selector.clause_digest !== derived.clause_digest ||
      binding.selector.module_digest !== derived.module_digest ||
      binding.selector.trace_contract_digest !==
        derived.trace_contract_digest ||
      binding.selector.contract_admission_digest !==
        derived.contract_admission_digest ||
      binding.selector.source_proposal_digest !==
        derived.source_proposal_digest ||
      observation.case_digest !== derived.case_digest ||
      observation.binding_id !== binding.binding.binding_id ||
      observation.adapter_id !== binding.binding.target.adapter_id ||
      observation.adapter_digest !==
        binding.binding.target.adapter_digest ||
      observation.trace_contract_digest !==
        derived.trace_contract_digest ||
      observation.contract_admission_digest !==
        derived.contract_admission_digest ||
      observation.source_proposal_digest !==
        derived.source_proposal_digest ||
      observation.trace?.trace_digest !== evaluation.trace_digest ||
      evaluation.case_digest !== derived.case_digest ||
      evaluation.binding_digest !== binding.binding_digest ||
      evaluation.observation_digest !==
        observation.observation_digest ||
      evaluation.trace_contract_digest !==
        derived.trace_contract_digest ||
      evaluation.contract_admission_digest !==
        derived.contract_admission_digest ||
      evaluation.source_proposal_digest !==
        derived.source_proposal_digest ||
      contract.digest !== derived.trace_contract_digest
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_SET_MISMATCH",
        derived.case_id,
        "identity or digest equality failed at the effect proof join",
      );
    }
  }
  const admittedDigests = new Map(
    input.contract_admission.contract_bindings.map((binding) => [
      binding.contract_id,
      binding,
    ]),
  );
  requireSameSet(
    [...new Set(input.cases.map((item) => item.contract_id))].sort(),
    [...contractById.keys()].sort(),
    "cases=trace-contracts",
  );
  for (const { contract, digest } of contracts) {
    const admitted = admittedDigests.get(contract.contract_id);
    if (
      admitted === undefined ||
      admitted.contract_digest !== digest ||
      admitted.source_proposal_digest !==
        input.source_proposal_digest
    ) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_CONTRACT_STALE",
        contract.contract_id,
        "trace contract is not exactly bound by the admission",
      );
    }
  }
}

function uniqueMap<T>(
  values: readonly T[],
  key: (value: T) => string,
  subject: string,
): Map<string, T> {
  const result = new Map<string, T>();
  for (const value of values) {
    const identity = key(value);
    if (result.has(identity)) {
      effectProofFail(
        "SFOL_EFFECT_PROOF_DUPLICATE_ID",
        subject,
        `duplicate case identity ${identity}`,
      );
    }
    result.set(identity, value);
  }
  return result;
}

function sortedUnique(
  values: readonly string[],
  subject: string,
): string[] {
  if (new Set(values).size !== values.length) {
    effectProofFail(
      "SFOL_EFFECT_PROOF_DUPLICATE_ID",
      subject,
      "stage contains a duplicate identity",
    );
  }
  return [...values].sort();
}

function requireSameSet(
  expected: readonly string[],
  actual: readonly string[],
  subject: string,
): void {
  if (
    expected.length !== actual.length ||
    expected.some((value, index) => value !== actual[index])
  ) {
    effectProofFail(
      "SFOL_EFFECT_PROOF_SET_MISMATCH",
      subject,
      `expected [${expected.join(",")}]; received [${actual.join(",")}]`,
    );
  }
}

function requireDigest(
  value: string,
  subject: string,
  stage: EffectProofDiagnostic["stage"],
): void {
  if (!SHA256.test(value)) {
    effectProofFail(
      "SFOL_EFFECT_PROOF_INVALID_DIGEST",
      subject,
      `invalid ${stage} SHA-256 digest`,
    );
  }
}

function effectProofFail(
  code: EffectProofDiagnosticCode,
  subject: string,
  detail: string,
): never {
  throw new EffectProofAbort({
    code,
    stage: "effect-proof",
    subject,
    detail,
  });
}

function proofFailure(
  diagnostic: EffectProofDiagnostic,
): EffectProofBuildResult {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze([Object.freeze(diagnostic)]),
  });
}

function replayFailure(
  diagnostic: EffectProofDiagnostic,
): EffectReplayResult {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze([Object.freeze(diagnostic)]),
  });
}

function deepFreeze<T>(value: T): T {
  if (
    typeof value === "object" &&
    value !== null &&
    !Object.isFrozen(value)
  ) {
    Object.freeze(value);
    for (const child of Object.values(value)) {
      deepFreeze(child);
    }
  }
  return value;
}
