import {
  canonicalSfolJson,
  digestSfolValue,
} from "./index.js";
import type {
  ClauseDenominator,
  ClauseDenominatorMember,
  ProofContextHandle,
} from "../denominator/index.js";
import type {
  EvaluationEnvironment,
  SemanticValue,
} from "../evaluator/index.js";
import type { TypedLogicModule } from "../language/typecheck.js";
import {
  runEffectHarness,
  type EffectHarnessAdapter,
  type EffectHarnessContainment,
  type EffectHarnessDiagnostic,
  type EffectHarnessPolicy,
} from "../runners/effect/harness.js";
import type {
  EffectTraceContract,
  ValidatedEffectTrace,
} from "../runners/effect/contracts.js";
import type { ResolvedEffectBinding } from "../bindings/effect.js";

export interface EffectContractAdmissionBinding {
  readonly contract_id: string;
  readonly contract_digest: string;
  readonly source_proposal_digest: string;
}

export interface EffectContractAdmission {
  readonly schema_version: "domainspec-sfol-effect-contract-admission/v1";
  readonly admission_id: string;
  readonly proof_context: ProofContextHandle;
  readonly source_proposal_digest: string;
  readonly contract_bindings: readonly EffectContractAdmissionBinding[];
  readonly admission_digest: string;
}

export interface EffectFixture {
  readonly fixture_id: string;
  readonly coverage_key: string;
  readonly contract_id: string;
  readonly inputs: Readonly<Record<string, SemanticValue>>;
  readonly universes: NonNullable<EvaluationEnvironment["universes"]>;
  readonly fixture_digest: string;
}

export interface DerivedEffectCase {
  readonly schema_version: "domainspec-sfol-effect-case/v1";
  readonly status: "ready";
  readonly case_id: string;
  readonly case_digest: string;
  readonly coverage_key: string;
  readonly role: "effects";
  readonly module_id: string;
  readonly module_digest: string;
  readonly clause_id: string;
  readonly clause_digest: string;
  readonly fixture_id: string;
  readonly fixture_digest: string;
  readonly contract_id: string;
  readonly trace_contract_digest: string;
  readonly contract_admission_digest: string;
  readonly source_proposal_digest: string;
  readonly proof_context_digest: string;
  readonly inputs: Readonly<Record<string, SemanticValue>>;
  readonly universes: NonNullable<EvaluationEnvironment["universes"]>;
}

export interface EffectCaseDerivationInput {
  readonly typed: TypedLogicModule;
  readonly typed_module_digest: string;
  readonly typed_clause_digests: Readonly<Record<string, string>>;
  readonly denominator: ClauseDenominator;
  readonly fixtures: readonly EffectFixture[];
  readonly contracts: readonly EffectTraceContract[];
  readonly contract_admission: EffectContractAdmission;
  readonly source_proposal_digest: string;
}

export interface RawEffectObservation {
  readonly schema_version: "domainspec-sfol-raw-effect-observation/v1";
  readonly case_id: string;
  readonly case_digest: string;
  readonly binding_id: string;
  readonly adapter_id: string;
  readonly adapter_digest: string;
  readonly contract_id: string;
  readonly trace_contract_digest: string;
  readonly contract_admission_digest: string;
  readonly source_proposal_digest: string;
  readonly status: "observed" | "indeterminate";
  readonly trace: ValidatedEffectTrace | null;
  readonly containment: EffectHarnessContainment | null;
  readonly diagnostics: readonly EffectHarnessDiagnostic[];
  readonly observation_digest: string;
}

export type EffectCaseDiagnosticCode =
  | "SFOL_EFFECT_CASE_EMPTY"
  | "SFOL_EFFECT_CASE_DUPLICATE_FIXTURE"
  | "SFOL_EFFECT_CASE_FIXTURE_DIGEST_MISMATCH"
  | "SFOL_EFFECT_CASE_DENOMINATOR_MISMATCH"
  | "SFOL_EFFECT_CASE_TYPED_MODULE_MISMATCH"
  | "SFOL_EFFECT_CASE_TYPED_CLAUSE_MISMATCH"
  | "SFOL_EFFECT_CASE_CLAUSE_UNAVAILABLE"
  | "SFOL_EFFECT_CASE_ROLE_UNSUPPORTED"
  | "SFOL_EFFECT_CASE_CONTRACT_UNADMITTED"
  | "SFOL_EFFECT_CASE_CONTRACT_STALE"
  | "SFOL_EFFECT_CASE_SOURCE_MISMATCH"
  | "SFOL_EFFECT_CASE_ADMISSION_STALE"
  | "SFOL_EFFECT_CASE_ORACLE_FIELD"
  | "SFOL_EFFECT_CASE_DUPLICATE_ID"
  | "SFOL_EFFECT_CASE_INDETERMINATE";

export interface EffectCaseDiagnostic {
  readonly code: EffectCaseDiagnosticCode;
  readonly stage: "effect-case-derivation";
  readonly subject: string;
  readonly detail: string;
}

export type EffectCaseDerivationResult =
  | {
      readonly ok: true;
      readonly value: readonly DerivedEffectCase[];
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly EffectCaseDiagnostic[];
    };

const SHA256 = /^[0-9a-f]{64}$/;
const ORACLE_FIELD =
  /^(?:expected(?:_|$)|oracle(?:_|$)|acceptance(?:_|$)|assert(?:_|$)|verdict(?:_|$))/i;

class EffectCaseAbort extends Error {
  readonly diagnostic: EffectCaseDiagnostic;

  constructor(diagnostic: EffectCaseDiagnostic) {
    super(
      `${diagnostic.code}:${diagnostic.subject}:${diagnostic.detail}`,
    );
    this.name = "EffectCaseAbort";
    this.diagnostic = diagnostic;
  }
}

export function effectFixtureDigest(
  fixture: Omit<EffectFixture, "fixture_digest">,
): string {
  return digestSfolValue(fixture);
}

export function effectContractAdmissionDigest(
  admission: Omit<EffectContractAdmission, "admission_digest">,
): string {
  return digestSfolValue(admission);
}

export function deriveEffectCases(
  input: EffectCaseDerivationInput,
): EffectCaseDerivationResult {
  try {
    validateDerivationFrontier(input);
    const cases = input.denominator.members.flatMap((member) => {
      const fixtures = input.fixtures.filter(
        (fixture) => fixture.coverage_key === member.coverage_key,
      );
      if (fixtures.length === 0) {
        effectCaseFail(
          "SFOL_EFFECT_CASE_DENOMINATOR_MISMATCH",
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
      effectCaseFail(
        "SFOL_EFFECT_CASE_DUPLICATE_ID",
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
    if (error instanceof EffectCaseAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_EFFECT_CASE_INDETERMINATE",
          stage: "effect-case-derivation",
          subject: "cases",
          detail: "effect case derivation received structurally invalid input",
        }),
      ]),
    });
  }
}

export async function runDerivedEffectCase<Resource>(
  derived: DerivedEffectCase,
  binding: ResolvedEffectBinding,
  contract: EffectTraceContract,
  adapter: EffectHarnessAdapter<Resource>,
  policy: EffectHarnessPolicy,
): Promise<RawEffectObservation> {
  const fail = (
    detail: string,
    diagnostics: readonly EffectHarnessDiagnostic[] = [],
    containment: EffectHarnessContainment | null = null,
  ): RawEffectObservation =>
    freezeObservation({
      schema_version: "domainspec-sfol-raw-effect-observation/v1",
      case_id: derived.case_id,
      case_digest: derived.case_digest,
      binding_id: binding.binding.binding_id,
      adapter_id: adapter.adapter_id,
      adapter_digest: adapter.adapter_digest,
      contract_id: derived.contract_id,
      trace_contract_digest: derived.trace_contract_digest,
      contract_admission_digest: derived.contract_admission_digest,
      source_proposal_digest: derived.source_proposal_digest,
      status: "indeterminate",
      trace: null,
      containment,
      diagnostics:
        diagnostics.length > 0
          ? diagnostics
          : [
              {
                code: "SFOL_HARNESS_ADAPTER_INVALID",
                stage: "effect-harness",
                phase: "preflight",
                detail,
              },
            ],
    });

  if (
    binding.selector.case_id !== derived.case_id ||
    binding.selector.case_digest !== derived.case_digest ||
    binding.selector.trace_contract_digest !==
      derived.trace_contract_digest ||
    binding.selector.contract_admission_digest !==
      derived.contract_admission_digest ||
    binding.selector.source_proposal_digest !==
      derived.source_proposal_digest
  ) {
    return fail(
      "derived case and resolved effect binding identities are incompatible",
    );
  }
  if (
    digestSfolValue(contract) !== derived.trace_contract_digest ||
    contract.contract_id !== derived.contract_id
  ) {
    return fail("effect trace contract identity or digest is stale");
  }
  if (
    binding.binding.target.adapter_id !== adapter.adapter_id ||
    binding.binding.target.adapter_digest !== adapter.adapter_digest ||
    adapter.contract_id !== contract.contract_id
  ) {
    return fail("resolved effect adapter identity or contract is incompatible");
  }

  const result = await runEffectHarness(
    derived.case_id,
    contract,
    adapter,
    policy,
  );
  if (!result.ok) {
    return fail(
      result.diagnostics[0]?.detail ?? "contained effect harness failed",
      result.diagnostics,
      result.containment,
    );
  }
  return freezeObservation({
    schema_version: "domainspec-sfol-raw-effect-observation/v1",
    case_id: derived.case_id,
    case_digest: derived.case_digest,
    binding_id: binding.binding.binding_id,
    adapter_id: adapter.adapter_id,
    adapter_digest: adapter.adapter_digest,
    contract_id: derived.contract_id,
    trace_contract_digest: derived.trace_contract_digest,
    contract_admission_digest: derived.contract_admission_digest,
    source_proposal_digest: derived.source_proposal_digest,
    status: "observed",
    trace: result.trace,
    containment: result.containment,
    diagnostics: [],
  });
}

function validateDerivationFrontier(
  input: EffectCaseDerivationInput,
): void {
  requireDigest(input.typed_module_digest, "typed_module_digest");
  requireDigest(input.source_proposal_digest, "source_proposal_digest");
  if (input.fixtures.length === 0) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_EMPTY",
      "fixtures",
      "at least one finite effect fixture is required",
    );
  }
  rejectOracleFields(input.fixtures, "fixtures");
  const fixtureIds = input.fixtures.map(
    (fixture) => `${fixture.coverage_key}|${fixture.fixture_id}`,
  );
  if (new Set(fixtureIds).size !== fixtureIds.length) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_DUPLICATE_FIXTURE",
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
    effectCaseFail(
      "SFOL_EFFECT_CASE_DENOMINATOR_MISMATCH",
      "fixtures",
      `fixture coverage [${fixtureCoverage.join(",")}] does not equal denominator coverage [${denominatorCoverage.join(",")}]`,
    );
  }
  const admission = input.contract_admission;
  if (
    admission.schema_version !==
    "domainspec-sfol-effect-contract-admission/v1"
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_ADMISSION_STALE",
      "contract_admission",
      "unsupported effect contract admission schema",
    );
  }
  const { admission_digest: _digest, ...unsignedAdmission } = admission;
  if (
    !SHA256.test(admission.admission_digest) ||
    effectContractAdmissionDigest(unsignedAdmission) !==
      admission.admission_digest
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_ADMISSION_STALE",
      "contract_admission",
      "contract admission digest does not match its exact content",
    );
  }
  if (
    admission.source_proposal_digest !==
      input.source_proposal_digest
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_SOURCE_MISMATCH",
      "contract_admission",
      "contract admission and derivation source proposal digests differ",
    );
  }
  if (
    canonicalSfolJson(admission.proof_context) !==
    canonicalSfolJson(input.denominator.proof_context)
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_ADMISSION_STALE",
      "contract_admission",
      "contract admission proof context differs from the denominator",
    );
  }
  const bindingIds = admission.contract_bindings.map(
    (binding) => binding.contract_id,
  );
  if (new Set(bindingIds).size !== bindingIds.length) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_CONTRACT_UNADMITTED",
      "contract_admission",
      "contract admission contains duplicate contract identities",
    );
  }
}

function deriveMemberCase(
  member: ClauseDenominatorMember,
  fixture: EffectFixture,
  input: EffectCaseDerivationInput,
): DerivedEffectCase {
  if (member.role !== "effects" || member.kind !== "effect-relation") {
    effectCaseFail(
      "SFOL_EFFECT_CASE_ROLE_UNSUPPORTED",
      member.coverage_key,
      `effect derivation requires effect-relation#effects, not ${member.kind}#${member.role}`,
    );
  }
  if (
    member.module_id !== input.typed.source.module_id ||
    member.module_digest !== input.typed_module_digest
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_TYPED_MODULE_MISMATCH",
      member.coverage_key,
      "typed module identity or digest does not match the denominator",
    );
  }
  const typedClauseDigest =
    input.typed_clause_digests[member.clause_id];
  if (
    typedClauseDigest === undefined ||
    typedClauseDigest !== member.clause_digest
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_TYPED_CLAUSE_MISMATCH",
      member.coverage_key,
      "typed clause digest does not match the denominator",
    );
  }
  requireDigest(typedClauseDigest, `${member.clause_id}.digest`);
  const clause = input.typed.source.clauses.find(
    (candidate) => candidate.clause_id === member.clause_id,
  );
  if (
    clause === undefined ||
    clause.kind !== "effect-relation"
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_CLAUSE_UNAVAILABLE",
      member.coverage_key,
      "one typed effect-relation clause admitted by the independent denominator is required",
    );
  }

  const { fixture_digest: _fixtureDigest, ...unsignedFixture } = fixture;
  if (
    !SHA256.test(fixture.fixture_digest) ||
    effectFixtureDigest(unsignedFixture) !== fixture.fixture_digest
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_FIXTURE_DIGEST_MISMATCH",
      member.coverage_key,
      `fixture ${fixture.fixture_id} digest is stale or invalid`,
    );
  }
  const contract = input.contracts.find(
    (candidate) => candidate.contract_id === fixture.contract_id,
  );
  if (contract === undefined) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_CONTRACT_UNADMITTED",
      member.coverage_key,
      `fixture contract ${fixture.contract_id} is unavailable`,
    );
  }
  const contractDigest = digestSfolValue(contract);
  const admitted = input.contract_admission.contract_bindings.filter(
    (binding) => binding.contract_id === contract.contract_id,
  );
  if (admitted.length !== 1) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_CONTRACT_UNADMITTED",
      member.coverage_key,
      `contract ${contract.contract_id} requires one independent admission`,
    );
  }
  const contractBinding = admitted[0];
  if (
    contractBinding === undefined ||
    contractBinding.contract_digest !== contractDigest
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_CONTRACT_STALE",
      member.coverage_key,
      "admitted contract digest differs from the supplied trace contract",
    );
  }
  if (
    contractBinding.source_proposal_digest !==
      input.source_proposal_digest
  ) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_SOURCE_MISMATCH",
      member.coverage_key,
      "contract binding and derivation source proposal digests differ",
    );
  }

  const caseId = `${member.coverage_key}@${fixture.fixture_id}`;
  const unsigned = {
    schema_version: "domainspec-sfol-effect-case/v1" as const,
    status: "ready" as const,
    case_id: caseId,
    coverage_key: member.coverage_key,
    role: "effects" as const,
    module_id: member.module_id,
    module_digest: member.module_digest,
    clause_id: member.clause_id,
    clause_digest: member.clause_digest,
    fixture_id: fixture.fixture_id,
    fixture_digest: fixture.fixture_digest,
    contract_id: contract.contract_id,
    trace_contract_digest: contractDigest,
    contract_admission_digest:
      input.contract_admission.admission_digest,
    source_proposal_digest: input.source_proposal_digest,
    proof_context_digest: digestSfolValue(
      input.denominator.proof_context,
    ),
    inputs: fixture.inputs,
    universes: fixture.universes,
  };
  return deepFreeze({
    ...unsigned,
    case_digest: digestSfolValue(unsigned),
  });
}

function freezeObservation(
  unsigned: Omit<RawEffectObservation, "observation_digest">,
): RawEffectObservation {
  return deepFreeze({
    ...unsigned,
    observation_digest: digestSfolValue(unsigned),
  });
}

function rejectOracleFields(value: unknown, subject: string): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) =>
      rejectOracleFields(item, `${subject}[${index}]`),
    );
    return;
  }
  if (!isRecord(value)) {
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    if (ORACLE_FIELD.test(key)) {
      effectCaseFail(
        "SFOL_EFFECT_CASE_ORACLE_FIELD",
        `${subject}.${key}`,
        "effect fixtures must remain input-only",
      );
    }
    rejectOracleFields(child, `${subject}.${key}`);
  }
}

function requireDigest(value: string, subject: string): void {
  if (!SHA256.test(value)) {
    effectCaseFail(
      "SFOL_EFFECT_CASE_TYPED_CLAUSE_MISMATCH",
      subject,
      "expected a lowercase SHA-256 digest",
    );
  }
}

function effectCaseFail(
  code: EffectCaseDiagnosticCode,
  subject: string,
  detail: string,
): never {
  throw new EffectCaseAbort({
    code,
    stage: "effect-case-derivation",
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
