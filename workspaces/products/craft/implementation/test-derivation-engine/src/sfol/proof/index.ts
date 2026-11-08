import {
  canonicalSfolJson,
  digestSfolValue,
  type DerivedPureCase,
} from "../cases/index.js";
import type { ClauseDenominator } from "../denominator/index.js";
import {
  evaluateTerm,
  integerValue,
  rationalValue,
  type SemanticValue,
} from "../evaluator/index.js";
import type { TypedLogicModule } from "../language/typecheck.js";
import type { ResolvedPureBinding } from "../bindings/index.js";
import type {
  RawJsonValue,
  RawPureObservation,
} from "../runners/pure/index.js";

export interface PureEvaluation {
  readonly schema_version: "domainspec-sfol-pure-evaluation/v1";
  readonly case_id: string;
  readonly case_digest: string;
  readonly observation_digest: string;
  readonly status: "pass" | "fail" | "indeterminate";
  readonly expected_digest: string;
  readonly observed_digest: string | null;
  readonly detail: string;
  readonly evaluation_digest: string;
}

export interface PureProofStageSet {
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

export interface PureProofReceipt {
  readonly schema_version: "domainspec-sfol-pure-proof-receipt/v1";
  readonly status: "pass";
  readonly proof_context: ClauseDenominator["proof_context"];
  readonly artifact_digests: {
    readonly denominator: string;
    readonly typed: string;
    readonly cases: string;
    readonly bindings: string;
    readonly observations: string;
    readonly evaluations: string;
    readonly tool: string;
  };
  readonly stage_sets: readonly PureProofStageSet[];
  readonly case_count: number;
  readonly receipt_digest: string;
}

export interface PureProofBuildInput {
  readonly denominator: ClauseDenominator;
  readonly typed_artifact_digest: string;
  readonly upstream_case_sets: {
    readonly C_spec: readonly string[];
    readonly C_projected: readonly string[];
    readonly C_validated: readonly string[];
    readonly C_typed: readonly string[];
  };
  readonly cases: readonly DerivedPureCase[];
  readonly bindings: readonly ResolvedPureBinding[];
  readonly observations: readonly RawPureObservation[];
  readonly evaluations: readonly PureEvaluation[];
  readonly tool_digest: string;
}

export interface PureReplayAllowlist {
  readonly receipt_digest: string;
  readonly denominator_digest: string;
  readonly typed_artifact_digest: string;
  readonly tool_digest: string;
}

export type PureProofDiagnosticCode =
  | "SFOL_PROOF_CASE_STALE"
  | "SFOL_PROOF_OBSERVATION_STALE"
  | "SFOL_PROOF_EVALUATION_STALE"
  | "SFOL_PROOF_SET_MISMATCH"
  | "SFOL_PROOF_DUPLICATE_ID"
  | "SFOL_PROOF_NONPASS_STATE"
  | "SFOL_PROOF_INVALID_DIGEST"
  | "SFOL_REPLAY_NOT_ALLOWLISTED"
  | "SFOL_REPLAY_ARTIFACT_MUTATED"
  | "SFOL_REPLAY_REBUILD_FAILED";

export interface PureProofDiagnostic {
  readonly code: PureProofDiagnosticCode;
  readonly stage: "proof" | "replay";
  readonly subject: string;
  readonly detail: string;
}

export type PureProofBuildResult =
  | {
      readonly ok: true;
      readonly value: PureProofReceipt;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly PureProofDiagnostic[];
    };

export type PureReplayResult =
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
      readonly diagnostics: readonly PureProofDiagnostic[];
    };

const SHA256 = /^[0-9a-f]{64}$/;

class ProofAbort extends Error {
  readonly diagnostic: PureProofDiagnostic;

  constructor(diagnostic: PureProofDiagnostic) {
    super(`${diagnostic.code}:${diagnostic.subject}:${diagnostic.detail}`);
    this.name = "ProofAbort";
    this.diagnostic = diagnostic;
  }
}

export function evaluatePureObservation(
  typed: TypedLogicModule,
  derived: DerivedPureCase,
  binding: ResolvedPureBinding,
  observation: RawPureObservation,
): PureEvaluation {
  const failure = (
    status: "fail" | "indeterminate",
    detail: string,
    expectedDigest = derived.expected_digest,
    observedDigest: string | null = null,
  ): PureEvaluation =>
    freezeEvaluation({
      schema_version: "domainspec-sfol-pure-evaluation/v1",
      case_id: derived.case_id,
      case_digest: derived.case_digest,
      observation_digest: observation.observation_digest,
      status,
      expected_digest: expectedDigest,
      observed_digest: observedDigest,
      detail,
    });

  if (
    observation.case_id !== derived.case_id ||
    observation.case_digest !== derived.case_digest ||
    binding.selector.case_id !== derived.case_id ||
    binding.selector.case_digest !== derived.case_digest
  ) {
    return failure(
      "indeterminate",
      "case, binding, and observation identities are incompatible",
    );
  }
  if (observation.status === "indeterminate") {
    return failure(
      "indeterminate",
      `${observation.diagnostic.code}: ${observation.diagnostic.detail}`,
    );
  }
  if (observation.status === "threw") {
    return failure(
      "fail",
      `target threw ${observation.raw_error.name}: ${observation.raw_error.message}`,
    );
  }

  const clause = typed.source.clauses.find(
    (candidate) => candidate.clause_id === derived.clause_id,
  );
  if (clause === undefined) {
    return failure("indeterminate", "typed source clause is absent");
  }
  const expected = evaluateTerm(typed, clause.expression, {
    variables: derived.inputs,
    universes: derived.universes,
  });
  if (expected.status === "indeterminate") {
    return failure(
      "indeterminate",
      `${expected.diagnostic.code}: ${expected.diagnostic.detail}`,
    );
  }
  const expectedDigest = digestSfolValue(expected.value);
  if (expectedDigest !== derived.expected_digest) {
    return failure(
      "indeterminate",
      "derived expected digest is stale",
      expectedDigest,
    );
  }

  const projected = projectRawObservation(
    observation.raw_return,
    binding.binding.observation_map,
  );
  if (projected === null) {
    return failure(
      "indeterminate",
      "raw observation cannot be decoded as a semantic value",
      expectedDigest,
    );
  }
  const observedDigest = digestSfolValue(projected);
  if (observedDigest !== expectedDigest) {
    return failure(
      "fail",
      "semantic observation differs from the source clause",
      expectedDigest,
      observedDigest,
    );
  }
  return freezeEvaluation({
    schema_version: "domainspec-sfol-pure-evaluation/v1",
    case_id: derived.case_id,
    case_digest: derived.case_digest,
    observation_digest: observation.observation_digest,
    status: "pass",
    expected_digest: expectedDigest,
    observed_digest: observedDigest,
    detail: "semantic observation matches the source clause",
  });
}

export function buildPureProofReceipt(
  input: PureProofBuildInput,
): PureProofBuildResult {
  try {
    for (const [subject, digest] of [
      ["typed", input.typed_artifact_digest],
      ["tool", input.tool_digest],
      ["denominator", input.denominator.digest],
    ] as const) {
      requireDigest(digest, subject, "proof");
    }
    if (input.cases.length === 0) {
      proofFail(
        "SFOL_PROOF_SET_MISMATCH",
        "cases",
        "a passing pure proof requires at least one case",
      );
    }

    validateCases(input.cases);
    validateBindings(input.bindings);
    validateObservations(input.observations);
    validateEvaluations(input.evaluations);

    const caseIds = sortedUnique(
      input.cases.map((derived) => derived.case_id),
      "T_generated",
    );
    const denominatorCoverage = sortedUnique(
      input.denominator.coverage_keys,
      "C_spec",
    );
    const caseCoverage = [
      ...new Set(input.cases.map((derived) => derived.coverage_key)),
    ].sort();
    requireSameSet(
      denominatorCoverage,
      caseCoverage,
      "C_spec=T_generated.coverage",
    );
    const boundIds = sortedUnique(
      input.bindings.map((resolved) => resolved.selector.case_id),
      "C_bound",
    );
    const observedIds = sortedUnique(
      input.observations.map((observation) => observation.case_id),
      "O_run",
    );
    const evaluatedIds = sortedUnique(
      input.evaluations.map((evaluation) => evaluation.case_id),
      "R_evaluated",
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
    requireSameSet(caseIds, sourceIds, "T_generated=C_spec");
    requireSameSet(caseIds, projectedIds, "T_generated=C_projected");
    requireSameSet(caseIds, validatedIds, "T_generated=C_validated");
    requireSameSet(caseIds, typedIds, "T_generated=C_typed");
    requireSameSet(caseIds, boundIds, "T_generated=C_bound");
    requireSameSet(caseIds, observedIds, "T_generated=O_run");
    requireSameSet(caseIds, evaluatedIds, "T_generated=R_evaluated");

    validateJoins(input);
    const stageSets: readonly PureProofStageSet[] = Object.freeze([
      Object.freeze({ stage: "C_spec", case_ids: Object.freeze(sourceIds) }),
      Object.freeze({
        stage: "C_projected",
        case_ids: Object.freeze(projectedIds),
      }),
      Object.freeze({
        stage: "C_validated",
        case_ids: Object.freeze(validatedIds),
      }),
      Object.freeze({ stage: "C_typed", case_ids: Object.freeze(typedIds) }),
      Object.freeze({
        stage: "T_generated",
        case_ids: Object.freeze([...caseIds]),
      }),
      Object.freeze({ stage: "C_bound", case_ids: Object.freeze(boundIds) }),
      Object.freeze({ stage: "O_run", case_ids: Object.freeze(observedIds) }),
      Object.freeze({
        stage: "R_evaluated",
        case_ids: Object.freeze(evaluatedIds),
      }),
    ]);

    const unsigned = {
      schema_version: "domainspec-sfol-pure-proof-receipt/v1" as const,
      status: "pass" as const,
      proof_context: input.denominator.proof_context,
      artifact_digests: {
        denominator: input.denominator.digest,
        typed: input.typed_artifact_digest,
        cases: digestSfolValue(input.cases),
        bindings: digestSfolValue(input.bindings),
        observations: digestSfolValue(input.observations),
        evaluations: digestSfolValue(input.evaluations),
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
    if (error instanceof ProofAbort) {
      return proofFailure(error.diagnostic);
    }
    return proofFailure({
      code: "SFOL_PROOF_NONPASS_STATE",
      stage: "proof",
      subject: "proof",
      detail: "proof input is structurally invalid",
    });
  }
}

export function replayPureProofReceipt(
  receipt: PureProofReceipt,
  input: PureProofBuildInput,
  allowlist: PureReplayAllowlist,
): PureReplayResult {
  if (
    receipt.receipt_digest !== allowlist.receipt_digest ||
    receipt.artifact_digests.denominator !==
      allowlist.denominator_digest ||
    receipt.artifact_digests.typed !==
      allowlist.typed_artifact_digest ||
    receipt.artifact_digests.tool !== allowlist.tool_digest
  ) {
    return replayFailure({
      code: "SFOL_REPLAY_NOT_ALLOWLISTED",
      stage: "replay",
      subject: "allowlist",
      detail: "receipt or immutable dependency digest is not allowlisted",
    });
  }

  const rebuilt = buildPureProofReceipt(input);
  if (!rebuilt.ok) {
    return replayFailure({
      code: "SFOL_REPLAY_REBUILD_FAILED",
      stage: "replay",
      subject: "proof",
      detail: rebuilt.diagnostics[0]?.detail ?? "proof rebuild failed",
    });
  }
  if (
    rebuilt.value.receipt_digest !== receipt.receipt_digest ||
    canonicalSfolJson(rebuilt.value.artifact_digests) !==
      canonicalSfolJson(receipt.artifact_digests)
  ) {
    return replayFailure({
      code: "SFOL_REPLAY_ARTIFACT_MUTATED",
      stage: "replay",
      subject: "artifacts",
      detail: "replayed artifact bytes do not match the receipt",
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

function validateCases(cases: readonly DerivedPureCase[]): void {
  for (const derived of cases) {
    if (derived.status !== "ready") {
      proofFail(
        "SFOL_PROOF_NONPASS_STATE",
        derived.case_id,
        `case status ${String(derived.status)} is not ready`,
      );
    }
    const { case_digest: _digest, ...unsigned } = derived;
    if (digestSfolValue(unsigned) !== derived.case_digest) {
      proofFail(
        "SFOL_PROOF_CASE_STALE",
        derived.case_id,
        "case digest does not match its exact content",
      );
    }
  }
}

function validateBindings(bindings: readonly ResolvedPureBinding[]): void {
  for (const resolved of bindings) {
    if (
      resolved.binding.target.adapter_kind !== "pure-function" ||
      resolved.selector.case_id.length === 0 ||
      canonicalSfolJson(resolved.selector) !==
        canonicalSfolJson(resolved.binding.selector)
    ) {
      proofFail(
        "SFOL_PROOF_NONPASS_STATE",
        resolved.binding.binding_id,
        "only exact pure-function bindings are proof eligible",
      );
    }
  }
}

function validateObservations(
  observations: readonly RawPureObservation[],
): void {
  for (const observation of observations) {
    const { observation_digest: _digest, ...unsigned } = observation;
    if (digestSfolValue(unsigned) !== observation.observation_digest) {
      proofFail(
        "SFOL_PROOF_OBSERVATION_STALE",
        observation.case_id,
        "observation digest does not match its raw content",
      );
    }
    if (observation.status !== "returned") {
      proofFail(
        "SFOL_PROOF_NONPASS_STATE",
        observation.case_id,
        `observation status ${observation.status} is not returned`,
      );
    }
  }
}

function validateEvaluations(
  evaluations: readonly PureEvaluation[],
): void {
  for (const evaluation of evaluations) {
    const { evaluation_digest: _digest, ...unsigned } = evaluation;
    if (digestSfolValue(unsigned) !== evaluation.evaluation_digest) {
      proofFail(
        "SFOL_PROOF_EVALUATION_STALE",
        evaluation.case_id,
        "evaluation digest does not match its content",
      );
    }
    if (evaluation.status !== "pass") {
      proofFail(
        "SFOL_PROOF_NONPASS_STATE",
        evaluation.case_id,
        `evaluation status ${evaluation.status} is not pass`,
      );
    }
  }
}

function validateJoins(input: PureProofBuildInput): void {
  const bindingByCase = new Map(
    input.bindings.map((resolved) => [
      resolved.selector.case_id,
      resolved,
    ]),
  );
  const observationByCase = new Map(
    input.observations.map((observation) => [
      observation.case_id,
      observation,
    ]),
  );
  const evaluationByCase = new Map(
    input.evaluations.map((evaluation) => [
      evaluation.case_id,
      evaluation,
    ]),
  );
  for (const derived of input.cases) {
    const binding = bindingByCase.get(derived.case_id);
    const observation = observationByCase.get(derived.case_id);
    const evaluation = evaluationByCase.get(derived.case_id);
    if (
      binding === undefined ||
      observation === undefined ||
      evaluation === undefined
    ) {
      proofFail(
        "SFOL_PROOF_SET_MISMATCH",
        derived.case_id,
        "one or more exact join members are absent",
      );
    }
    if (
      binding.selector.case_digest !== derived.case_digest ||
      binding.selector.fixture_digest !== derived.fixture_digest ||
      binding.selector.clause_digest !== derived.clause_digest ||
      binding.selector.module_digest !== derived.module_digest ||
      observation.case_digest !== derived.case_digest ||
      observation.binding_id !== binding.binding.binding_id ||
      observation.target_digest !== binding.binding.target.target_digest ||
      observation.runtime_digest !== binding.binding.target.runtime_digest ||
      evaluation.case_digest !== derived.case_digest ||
      evaluation.observation_digest !== observation.observation_digest ||
      evaluation.expected_digest !== derived.expected_digest ||
      evaluation.observed_digest !== derived.expected_digest
    ) {
      proofFail(
        "SFOL_PROOF_SET_MISMATCH",
        derived.case_id,
        "identity or compatible digest equality failed at the proof join",
      );
    }
  }
}

function sortedUnique(values: readonly string[], subject: string): string[] {
  if (new Set(values).size !== values.length) {
    proofFail(
      "SFOL_PROOF_DUPLICATE_ID",
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
    proofFail(
      "SFOL_PROOF_SET_MISMATCH",
      subject,
      `expected [${expected.join(",")}]; received [${actual.join(",")}]`,
    );
  }
}

function freezeEvaluation(
  unsigned: Omit<PureEvaluation, "evaluation_digest">,
): PureEvaluation {
  return deepFreeze({
    ...unsigned,
    evaluation_digest: digestSfolValue(unsigned),
  });
}

function projectRawObservation(
  raw: RawJsonValue,
  projection: ResolvedPureBinding["binding"]["observation_map"],
): SemanticValue | null {
  const selected =
    projection.kind === "return"
      ? raw
      : selectField(raw, projection.field);
  return decodeSemanticValue(selected);
}

function selectField(raw: RawJsonValue, field: string): RawJsonValue | null {
  if (!isRecord(raw)) {
    return null;
  }
  if (
    raw.tag === "record" &&
    isRecord(raw.fields) &&
    Object.hasOwn(raw.fields, field)
  ) {
    return raw.fields[field] ?? null;
  }
  return raw[field] ?? null;
}

function decodeSemanticValue(raw: RawJsonValue | null): SemanticValue | null {
  if (!isRecord(raw) || typeof raw.tag !== "string") {
    return null;
  }
  switch (raw.tag) {
    case "boolean":
      return hasExactKeys(raw, ["tag", "value"]) &&
        typeof raw.value === "boolean"
        ? Object.freeze({ tag: "boolean", value: raw.value })
        : null;
    case "string":
      return hasExactKeys(raw, ["tag", "value"]) &&
        typeof raw.value === "string"
        ? Object.freeze({ tag: "string", value: raw.value })
        : null;
    case "integer":
      if (
        !hasExactKeys(raw, ["tag", "value"]) ||
        typeof raw.value !== "string"
      ) {
        return null;
      }
      try {
        return integerValue(raw.value);
      } catch {
        return null;
      }
    case "rational":
      if (
        !hasExactKeys(raw, ["tag", "numerator", "denominator"]) ||
        typeof raw.numerator !== "string" ||
        typeof raw.denominator !== "string"
      ) {
        return null;
      }
      try {
        return rationalValue(raw.numerator, raw.denominator);
      } catch {
        return null;
      }
    case "enum":
      return hasExactKeys(raw, ["tag", "declaration_id", "member"]) &&
        typeof raw.declaration_id === "string" &&
        typeof raw.member === "string"
        ? Object.freeze({
            tag: "enum",
            declaration_id: raw.declaration_id,
            member: raw.member,
          })
        : null;
    case "record": {
      if (
        !hasExactKeys(raw, ["tag", "declaration_id", "fields"]) ||
        typeof raw.declaration_id !== "string" ||
        !isRecord(raw.fields)
      ) {
        return null;
      }
      const fields: Record<string, SemanticValue> = {};
      for (const key of Object.keys(raw.fields).sort()) {
        const decoded = decodeSemanticValue(raw.fields[key] ?? null);
        if (decoded === null) {
          return null;
        }
        fields[key] = decoded;
      }
      return Object.freeze({
        tag: "record",
        declaration_id: raw.declaration_id,
        fields: Object.freeze(fields),
      });
    }
    case "list":
    case "set": {
      if (!hasExactKeys(raw, ["tag", "items"]) || !Array.isArray(raw.items)) {
        return null;
      }
      const items: SemanticValue[] = [];
      for (const item of raw.items) {
        const decoded = decodeSemanticValue(item);
        if (decoded === null) {
          return null;
        }
        items.push(decoded);
      }
      if (raw.tag === "list") {
        return Object.freeze({
          tag: "list",
          items: Object.freeze(items),
        });
      }
      const unique = new Map(
        items.map((item) => [digestSfolValue(item), item]),
      );
      return Object.freeze({
        tag: "set",
        items: Object.freeze(
          [...unique.entries()]
            .sort(([left], [right]) => left.localeCompare(right))
            .map(([, item]) => item),
        ),
      });
    }
    default:
      return null;
  }
}

function requireDigest(
  digest: string,
  subject: string,
  stage: "proof" | "replay",
): void {
  if (!SHA256.test(digest)) {
    proofFail(
      "SFOL_PROOF_INVALID_DIGEST",
      subject,
      `${stage} requires a lowercase SHA-256 digest`,
    );
  }
}

function proofFail(
  code: PureProofDiagnosticCode,
  subject: string,
  detail: string,
): never {
  throw new ProofAbort({
    code,
    stage: "proof",
    subject,
    detail,
  });
}

function proofFailure(
  diagnostic: PureProofDiagnostic,
): PureProofBuildResult {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze([Object.freeze(diagnostic)]),
  });
}

function replayFailure(
  diagnostic: PureProofDiagnostic,
): PureReplayResult {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze([Object.freeze(diagnostic)]),
  });
}

function isRecord(
  value: unknown,
): value is Readonly<Record<string, RawJsonValue>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(
  value: Readonly<Record<string, RawJsonValue>>,
  expected: readonly string[],
): boolean {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  return (
    actual.length === wanted.length &&
    actual.every((key, index) => key === wanted[index])
  );
}

function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) {
      deepFreeze(child);
    }
  }
  return value;
}
