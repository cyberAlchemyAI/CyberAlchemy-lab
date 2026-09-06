import { createHash } from "node:crypto";

import type {
  ClauseDenominator,
  ClauseDenominatorMember,
  ExecutionRole,
} from "../denominator/index.js";
import {
  evaluateTerm,
  type EvaluationEnvironment,
  type SemanticValue,
} from "../evaluator/index.js";
import type { LogicClause } from "../language/ast.js";
import type { TypedLogicModule } from "../language/typecheck.js";
import type { PureBindingSelector } from "../bindings/index.js";

export interface PureFixture {
  readonly fixture_id: string;
  readonly coverage_key: string;
  readonly inputs: Readonly<Record<string, SemanticValue>>;
  readonly universes: NonNullable<EvaluationEnvironment["universes"]>;
  readonly fixture_digest: string;
}

export interface DerivedPureCase {
  readonly schema_version: "domainspec-sfol-pure-case/v1";
  readonly status: "ready";
  readonly case_id: string;
  readonly case_digest: string;
  readonly coverage_key: string;
  readonly role: ExecutionRole;
  readonly module_id: string;
  readonly module_digest: string;
  readonly clause_id: string;
  readonly clause_digest: string;
  readonly fixture_id: string;
  readonly fixture_digest: string;
  readonly inputs: Readonly<Record<string, SemanticValue>>;
  readonly universes: NonNullable<EvaluationEnvironment["universes"]>;
  readonly expected_digest: string;
}

export interface PureInvocation {
  readonly case_id: string;
  readonly case_digest: string;
  readonly coverage_key: string;
  readonly role: ExecutionRole;
  readonly module_id: string;
  readonly module_digest: string;
  readonly clause_id: string;
  readonly clause_digest: string;
  readonly fixture_digest: string;
  readonly inputs: Readonly<Record<string, SemanticValue>>;
}

export interface PureCaseDerivationInput {
  readonly typed: TypedLogicModule;
  readonly typed_module_digest: string;
  readonly typed_clause_digests: Readonly<Record<string, string>>;
  readonly denominator: ClauseDenominator;
  readonly fixtures: readonly PureFixture[];
}

export type PureCaseDiagnosticCode =
  | "SFOL_CASE_EMPTY"
  | "SFOL_CASE_DUPLICATE_FIXTURE"
  | "SFOL_CASE_FIXTURE_DIGEST_MISMATCH"
  | "SFOL_CASE_DENOMINATOR_MISMATCH"
  | "SFOL_CASE_TYPED_MODULE_MISMATCH"
  | "SFOL_CASE_TYPED_CLAUSE_MISMATCH"
  | "SFOL_CASE_CLAUSE_UNAVAILABLE"
  | "SFOL_CASE_ROLE_UNSUPPORTED"
  | "SFOL_CASE_INDETERMINATE"
  | "SFOL_CASE_DUPLICATE_ID";

export interface PureCaseDiagnostic {
  readonly code: PureCaseDiagnosticCode;
  readonly stage: "case-derivation";
  readonly subject: string;
  readonly detail: string;
}

export type PureCaseDerivationResult =
  | {
      readonly ok: true;
      readonly value: readonly DerivedPureCase[];
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly PureCaseDiagnostic[];
    };

const SHA256 = /^[0-9a-f]{64}$/;

class CaseAbort extends Error {
  readonly diagnostic: PureCaseDiagnostic;

  constructor(diagnostic: PureCaseDiagnostic) {
    super(`${diagnostic.code}:${diagnostic.subject}:${diagnostic.detail}`);
    this.name = "CaseAbort";
    this.diagnostic = diagnostic;
  }
}

export function fixtureDigest(
  fixture: Omit<PureFixture, "fixture_digest">,
): string {
  return digestSfolValue(fixture);
}

export function derivePureCases(
  input: PureCaseDerivationInput,
): PureCaseDerivationResult {
  try {
    validateDigest(input.typed_module_digest, "typed_module_digest");
    if (input.fixtures.length === 0) {
      caseFail(
        "SFOL_CASE_EMPTY",
        "fixtures",
        "at least one finite pure fixture is required",
      );
    }
    const fixtureIds = input.fixtures.map(
      (fixture) => `${fixture.coverage_key}|${fixture.fixture_id}`,
    );
    if (new Set(fixtureIds).size !== fixtureIds.length) {
      caseFail(
        "SFOL_CASE_DUPLICATE_FIXTURE",
        "fixtures",
        "coverage_key and fixture_id pairs must be unique",
      );
    }
    const fixtureCoverage = [
      ...new Set(input.fixtures.map((fixture) => fixture.coverage_key)),
    ].sort();
    const denominatorCoverage = [...input.denominator.coverage_keys].sort();
    if (
      fixtureCoverage.length !== denominatorCoverage.length ||
      fixtureCoverage.some(
        (coverageKey, index) =>
          coverageKey !== denominatorCoverage[index],
      )
    ) {
      caseFail(
        "SFOL_CASE_DENOMINATOR_MISMATCH",
        "fixtures",
        `fixture coverage [${fixtureCoverage.join(",")}] does not equal denominator coverage [${denominatorCoverage.join(",")}]`,
      );
    }

    const cases = input.denominator.members.flatMap((member) => {
      const fixtures = input.fixtures.filter(
        (fixture) => fixture.coverage_key === member.coverage_key,
      );
      if (fixtures.length === 0) {
        caseFail(
          "SFOL_CASE_DENOMINATOR_MISMATCH",
          member.coverage_key,
          "at least one finite fixture is required for every admitted clause role",
        );
      }
      return fixtures.map((fixture) =>
        deriveMemberCase(member, fixture, input),
      );
    });
    const caseIds = cases.map((derived) => derived.case_id);
    if (new Set(caseIds).size !== caseIds.length) {
      caseFail(
        "SFOL_CASE_DUPLICATE_ID",
        "cases",
        "derived case IDs must be unique",
      );
    }
    return Object.freeze({
      ok: true,
      value: Object.freeze(
        cases.sort((left, right) =>
          left.case_id.localeCompare(right.case_id),
        ),
      ),
    });
  } catch (error: unknown) {
    if (error instanceof CaseAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_CASE_INDETERMINATE",
          stage: "case-derivation",
          subject: "cases",
          detail: "case derivation received structurally invalid input",
        }),
      ]),
    });
  }
}

export function bindingSelectorForCase(
  derived: DerivedPureCase,
): PureBindingSelector {
  return Object.freeze({
    module_id: derived.module_id,
    clause_id: derived.clause_id,
    case_id: derived.case_id,
    role: derived.role,
    module_digest: derived.module_digest,
    clause_digest: derived.clause_digest,
    case_digest: derived.case_digest,
    fixture_digest: derived.fixture_digest,
  });
}

export function toPureInvocation(
  derived: DerivedPureCase,
): PureInvocation {
  return Object.freeze({
    case_id: derived.case_id,
    case_digest: derived.case_digest,
    coverage_key: derived.coverage_key,
    role: derived.role,
    module_id: derived.module_id,
    module_digest: derived.module_digest,
    clause_id: derived.clause_id,
    clause_digest: derived.clause_digest,
    fixture_digest: derived.fixture_digest,
    inputs: derived.inputs,
  });
}

export function digestSfolValue(value: unknown): string {
  return createHash("sha256")
    .update(canonicalSfolJson(value))
    .digest("hex");
}

export function canonicalSfolJson(value: unknown): string {
  if (
    value === null ||
    typeof value === "boolean" ||
    typeof value === "string"
  ) {
    return JSON.stringify(value);
  }
  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new Error("non-finite numbers are not canonical DS-SFOL JSON");
    }
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(canonicalSfolJson).join(",")}]`;
  }
  if (isRecord(value)) {
    return `{${Object.keys(value)
      .sort()
      .map(
        (key) =>
          `${JSON.stringify(key)}:${canonicalSfolJson(value[key])}`,
      )
      .join(",")}}`;
  }
  throw new Error(`unsupported canonical value type ${typeof value}`);
}

function deriveMemberCase(
  member: ClauseDenominatorMember,
  fixture: PureFixture,
  input: PureCaseDerivationInput,
): DerivedPureCase {
  if (member.role !== "return" && member.role !== "predicate") {
    caseFail(
      "SFOL_CASE_ROLE_UNSUPPORTED",
      member.coverage_key,
      `pure derivation cannot handle ${member.role}`,
    );
  }
  if (
    member.module_id !== input.typed.source.module_id ||
    member.module_digest !== input.typed_module_digest
  ) {
    caseFail(
      "SFOL_CASE_TYPED_MODULE_MISMATCH",
      member.coverage_key,
      "typed module identity or digest does not match the denominator",
    );
  }
  const declaredClauseDigest =
    input.typed_clause_digests[member.clause_id];
  if (
    declaredClauseDigest === undefined ||
    declaredClauseDigest !== member.clause_digest
  ) {
    caseFail(
      "SFOL_CASE_TYPED_CLAUSE_MISMATCH",
      member.coverage_key,
      "typed clause digest does not match the denominator",
    );
  }
  validateDigest(declaredClauseDigest, `${member.clause_id}.digest`);

  const clause = input.typed.source.clauses.find(
    (candidate) => candidate.clause_id === member.clause_id,
  );
  if (clause === undefined) {
    caseFail(
      "SFOL_CASE_CLAUSE_UNAVAILABLE",
      member.coverage_key,
      "one typed clause admitted by the independent denominator is required",
    );
  }
  validatePureRole(clause, member);

  const unsignedFixture = {
    fixture_id: fixture.fixture_id,
    coverage_key: fixture.coverage_key,
    inputs: fixture.inputs,
    universes: fixture.universes,
  };
  if (
    !SHA256.test(fixture.fixture_digest) ||
    fixture.fixture_digest !== fixtureDigest(unsignedFixture)
  ) {
    caseFail(
      "SFOL_CASE_FIXTURE_DIGEST_MISMATCH",
      member.coverage_key,
      `fixture ${fixture.fixture_id} digest is stale or invalid`,
    );
  }

  const evaluation = evaluateTerm(input.typed, clause.expression, {
    variables: fixture.inputs,
    universes: fixture.universes,
  });
  if (evaluation.status === "indeterminate") {
    caseFail(
      "SFOL_CASE_INDETERMINATE",
      member.coverage_key,
      `${evaluation.diagnostic.code}: ${evaluation.diagnostic.detail}`,
    );
  }

  const caseId = `${member.coverage_key}@${fixture.fixture_id}`;
  const unsigned = {
    schema_version: "domainspec-sfol-pure-case/v1" as const,
    status: "ready" as const,
    case_id: caseId,
    coverage_key: member.coverage_key,
    role: member.role,
    module_id: member.module_id,
    module_digest: member.module_digest,
    clause_id: member.clause_id,
    clause_digest: member.clause_digest,
    fixture_id: fixture.fixture_id,
    fixture_digest: fixture.fixture_digest,
    inputs: fixture.inputs,
    universes: fixture.universes,
    expected_digest: digestSfolValue(evaluation.value),
  };
  return deepFreeze({
    ...unsigned,
    case_digest: digestSfolValue(unsigned),
  });
}

function validatePureRole(
  clause: LogicClause,
  member: ClauseDenominatorMember,
): void {
  const expectedRole =
    clause.kind === "function" ? "return" : "predicate";
  if (member.role !== expectedRole) {
    caseFail(
      "SFOL_CASE_ROLE_UNSUPPORTED",
      member.coverage_key,
      `${clause.kind} requires pure role ${expectedRole}`,
    );
  }
}

function validateDigest(value: string, subject: string): void {
  if (!SHA256.test(value)) {
    caseFail(
      "SFOL_CASE_TYPED_CLAUSE_MISMATCH",
      subject,
      "expected a lowercase SHA-256 digest",
    );
  }
}

function caseFail(
  code: PureCaseDiagnosticCode,
  subject: string,
  detail: string,
): never {
  throw new CaseAbort({
    code,
    stage: "case-derivation",
    subject,
    detail,
  });
}

function isRecord(
  value: unknown,
): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
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
