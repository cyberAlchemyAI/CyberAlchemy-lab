import type { PureFixture } from "../cases/index.js";
import {
  canonicalSfolJson,
  digestSfolValue,
  fixtureDigest,
} from "../cases/index.js";
import type { ClauseDenominator } from "../denominator/index.js";
import {
  evaluateTerm,
  rationalValue,
  type SemanticValue,
} from "../evaluator/index.js";
import type {
  EnumDeclaration,
  FixtureUniverseDeclaration,
  LogicClause,
  LogicTerm,
  ParameterDeclaration,
  SortRef,
} from "../language/ast.js";
import type { TypedLogicModule } from "../language/typecheck.js";

export const EXHAUSTIVE_FINITE_RULESET = Object.freeze({
  ruleset_id: "domainspec.sfol.partition.exhaustive-finite",
  ruleset_version: "1.0.0",
  mode: "exhaustive-finite" as const,
});

export const MCDC_RULESET = Object.freeze({
  ruleset_id: "domainspec.sfol.partition.mcdc",
  ruleset_version: "1.0.0",
  mode: "mcdc" as const,
});

export type PartitionRuleSet =
  | {
      readonly ruleset_id: typeof EXHAUSTIVE_FINITE_RULESET.ruleset_id;
      readonly ruleset_version: typeof EXHAUSTIVE_FINITE_RULESET.ruleset_version;
      readonly mode: typeof EXHAUSTIVE_FINITE_RULESET.mode;
      readonly max_cases: number;
    }
  | {
      readonly ruleset_id: typeof MCDC_RULESET.ruleset_id;
      readonly ruleset_version: typeof MCDC_RULESET.ruleset_version;
      readonly mode: typeof MCDC_RULESET.mode;
      readonly max_cases: number;
      readonly max_analysis_cases: number;
    };

export interface PartitionDomain {
  readonly inputs?: Readonly<Record<string, readonly SemanticValue[]>>;
  readonly collection_elements?: Readonly<
    Record<string, readonly SemanticValue[]>
  >;
  readonly universes?: Readonly<Record<string, readonly SemanticValue[]>>;
  readonly universe_variants?: Readonly<
    Record<string, readonly (readonly SemanticValue[])[]>
  >;
}

interface NormalizedPartitionDomain {
  readonly inputs: Readonly<Record<string, readonly SemanticValue[]>>;
  readonly collection_elements: Readonly<
    Record<string, readonly SemanticValue[]>
  >;
  readonly universes: Readonly<Record<string, readonly SemanticValue[]>>;
  readonly universe_variants: Readonly<
    Record<string, readonly (readonly SemanticValue[])[]>
  >;
}

export interface PureFixtureDerivationInput {
  readonly typed: TypedLogicModule;
  readonly typed_module_digest: string;
  readonly typed_clause_digests: Readonly<Record<string, string>>;
  readonly denominator: ClauseDenominator;
  readonly ruleset: PartitionRuleSet;
  readonly domain?: PartitionDomain;
}

export type PartitionDiagnosticCode =
  | "SFOL_PARTITION_INVALID_RULESET"
  | "SFOL_PARTITION_DENOMINATOR_MISMATCH"
  | "SFOL_PARTITION_CLAUSE_UNAVAILABLE"
  | "SFOL_PARTITION_STATUS_NOT_ADMITTED"
  | "SFOL_PARTITION_ROLE_UNSUPPORTED"
  | "SFOL_PARTITION_DUPLICATE_INPUT"
  | "SFOL_PARTITION_DOMAIN_REQUIRED"
  | "SFOL_PARTITION_DOMAIN_EMPTY"
  | "SFOL_PARTITION_DOMAIN_DUPLICATE"
  | "SFOL_PARTITION_DOMAIN_TYPE_MISMATCH"
  | "SFOL_PARTITION_BUDGET_EXCEEDED"
  | "SFOL_PARTITION_MCDC_UNSUPPORTED"
  | "SFOL_PARTITION_MCDC_INDEPENDENCE_UNSATISFIED"
  | "SFOL_PARTITION_EVALUATION_INDETERMINATE"
  | "SFOL_PARTITION_DUPLICATE_FIXTURE";

export interface PartitionDiagnostic {
  readonly code: PartitionDiagnosticCode;
  readonly stage: "partition-derivation";
  readonly subject: string;
  readonly detail: string;
}

export type PureFixtureDerivationResult =
  | {
      readonly ok: true;
      readonly value: readonly PureFixture[];
      readonly ruleset_digest: string;
      readonly domain_digest: string;
      readonly derivation_mode: PartitionRuleSet["mode"];
      readonly analyzed_case_count: number;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly PartitionDiagnostic[];
    };

class PartitionAbort extends Error {
  readonly diagnostic: PartitionDiagnostic;

  constructor(diagnostic: PartitionDiagnostic) {
    super(`${diagnostic.code}:${diagnostic.subject}:${diagnostic.detail}`);
    this.name = "PartitionAbort";
    this.diagnostic = diagnostic;
  }
}

export function derivePureFixtures(
  input: PureFixtureDerivationInput,
): PureFixtureDerivationResult {
  try {
    validateRuleSet(input.ruleset);
    if (
      input.typed.source.module_id !== input.denominator.members[0]?.module_id ||
      input.typed_module_digest !==
        input.denominator.members[0]?.module_digest
    ) {
      fail(
        "SFOL_PARTITION_DENOMINATOR_MISMATCH",
        "module",
        "typed module identity or digest does not match the denominator",
      );
    }

    const rulesetDigest = digestSfolValue(input.ruleset);
    const normalizedDomain = normalizeDomain(input.domain);
    const domainDigest = digestSfolValue(normalizedDomain);
    const fixtures: PureFixture[] = [];
    let analyzedCaseCount = 0;

    for (const member of input.denominator.members) {
      if (member.role !== "predicate" && member.role !== "return") {
        fail(
          "SFOL_PARTITION_ROLE_UNSUPPORTED",
          member.coverage_key,
          `finite pure partitioning cannot handle role ${member.role}`,
        );
      }
      const clause = input.typed.source.clauses.find(
        (candidate) => candidate.clause_id === member.clause_id,
      );
      if (clause === undefined) {
        fail(
          "SFOL_PARTITION_CLAUSE_UNAVAILABLE",
          member.clause_id,
          "denominator clause is absent from the typed module",
        );
      }
      if (clause.status !== "admitted") {
        fail(
          "SFOL_PARTITION_STATUS_NOT_ADMITTED",
          clause.clause_id,
          "only admitted clauses may produce proof fixtures",
        );
      }
      const clauseDigest = input.typed_clause_digests[clause.clause_id];
      if (clauseDigest === undefined || clauseDigest !== member.clause_digest) {
        fail(
          "SFOL_PARTITION_DENOMINATOR_MISMATCH",
          clause.clause_id,
          "typed clause digest does not match the denominator",
        );
      }
      const derived = deriveClauseFixtures(
        clause,
        member.coverage_key,
        clauseDigest,
        input.typed,
        input.ruleset,
        rulesetDigest,
        normalizedDomain,
        domainDigest,
      );
      analyzedCaseCount += derived.analyzedCaseCount;
      fixtures.push(...derived.fixtures);
    }

    fixtures.sort((left, right) =>
      `${left.coverage_key}|${left.fixture_id}`.localeCompare(
        `${right.coverage_key}|${right.fixture_id}`,
      ),
    );
    const identities = fixtures.map(
      (fixture) => `${fixture.coverage_key}|${fixture.fixture_id}`,
    );
    if (new Set(identities).size !== identities.length) {
      fail(
        "SFOL_PARTITION_DUPLICATE_FIXTURE",
        "fixtures",
        "partition derivation produced duplicate fixture identities",
      );
    }

    return Object.freeze({
      ok: true,
      value: deepFreeze(fixtures),
      ruleset_digest: rulesetDigest,
      domain_digest: domainDigest,
      derivation_mode: input.ruleset.mode,
      analyzed_case_count: analyzedCaseCount,
    });
  } catch (error: unknown) {
    if (error instanceof PartitionAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_PARTITION_DOMAIN_REQUIRED" as const,
          stage: "partition-derivation" as const,
          subject: "input",
          detail: "partition derivation received structurally invalid input",
        }),
      ]),
    });
  }
}

function deriveClauseFixtures(
  clause: LogicClause,
  coverageKey: string,
  clauseDigest: string,
  typed: TypedLogicModule,
  ruleset: PartitionRuleSet,
  rulesetDigest: string,
  domain: NormalizedPartitionDomain,
  domainDigest: string,
): { fixtures: PureFixture[]; analyzedCaseCount: number } {
  const inputNames = clause.inputs.map(({ name }) => name);
  if (new Set(inputNames).size !== inputNames.length) {
    fail(
      "SFOL_PARTITION_DUPLICATE_INPUT",
      clause.clause_id,
      "clause inputs must have unique names",
    );
  }
  const parameters = [...clause.inputs].sort((left, right) =>
    left.name.localeCompare(right.name),
  );
  const valueDomains = parameters.map((parameter) => ({
    parameter,
    values: valuesForParameter(parameter, typed, domain, clause.expression),
  }));
  const universeDomains = universeAssignments(clause, typed, domain);
  const inputCaseCount = valueDomains.reduce(
    (product, entry) => product * entry.values.length,
    1,
  );
  const universeCaseCount = universeDomains.reduce(
    (product, entry) => product * entry.variants.length,
    1,
  );
  const caseCount = inputCaseCount * universeCaseCount;
  const analysisLimit =
    ruleset.mode === "mcdc" ? ruleset.max_analysis_cases : ruleset.max_cases;
  if (!Number.isSafeInteger(caseCount) || caseCount > analysisLimit) {
    fail(
      "SFOL_PARTITION_BUDGET_EXCEEDED",
      clause.clause_id,
      `${ruleset.mode} analysis requires ${caseCount} cases; analysis budget is ${analysisLimit}`,
    );
  }

  const assignments: Readonly<Record<string, SemanticValue>>[] = [];
  enumerateAssignments(valueDomains, 0, {}, assignments);
  const universes: Readonly<Record<string, readonly SemanticValue[]>>[] = [];
  enumerateUniverses(universeDomains, 0, {}, universes);
  const candidates = assignments.flatMap((assignment) =>
    universes.map((universe) => ({ inputs: assignment, universes: universe })),
  );
  const selected =
    ruleset.mode === "exhaustive-finite"
      ? candidates
      : reduceMcdc(clause, typed, parameters, candidates, ruleset.max_cases);
  if (selected.length > ruleset.max_cases) {
    fail(
      "SFOL_PARTITION_BUDGET_EXCEEDED",
      clause.clause_id,
      `${ruleset.mode} selected ${selected.length} cases; output budget is ${ruleset.max_cases}`,
    );
  }

  return {
    analyzedCaseCount: candidates.length,
    fixtures: selected.map((candidate) => {
      const identity = {
        ruleset_digest: rulesetDigest,
        domain_digest: domainDigest,
        coverage_key: coverageKey,
        clause_digest: clauseDigest,
        inputs: candidate.inputs,
        universes: candidate.universes,
      };
      const unsigned = {
        fixture_id: `partition:${digestSfolValue(identity)}`,
        coverage_key: coverageKey,
        inputs: candidate.inputs,
        universes: candidate.universes,
      };
      return deepFreeze({
        ...unsigned,
        fixture_digest: fixtureDigest(unsigned),
      });
    }),
  };
}

function valuesForParameter(
  parameter: ParameterDeclaration,
  typed: TypedLogicModule,
  domain: NormalizedPartitionDomain,
  expression: LogicTerm,
): readonly SemanticValue[] {
  const explicit = domain.inputs[parameter.name];
  if (explicit !== undefined) {
    assertNoDuplicateValues(explicit, parameter.name);
  }
  const values =
    explicit ??
    automaticValues(parameter, typed, domain, expression);
  if (values === null) {
    fail(
      "SFOL_PARTITION_DOMAIN_REQUIRED",
      parameter.name,
      "a finite canonical witness domain is required for this sort",
    );
  }
  if (values.length === 0) {
    fail(
      "SFOL_PARTITION_DOMAIN_EMPTY",
      parameter.name,
      "finite witness domain cannot be empty",
    );
  }
  for (const value of values) {
    if (!matchesSort(value, parameter.sort, typed)) {
      fail(
        "SFOL_PARTITION_DOMAIN_TYPE_MISMATCH",
        parameter.name,
        `witness ${canonicalSfolJson(value)} does not match the declared sort`,
      );
    }
  }
  return normalizeValues(values, parameter.name);
}

function automaticValues(
  parameter: ParameterDeclaration,
  typed: TypedLogicModule,
  domain: NormalizedPartitionDomain,
  expression: LogicTerm,
): readonly SemanticValue[] | null {
  const sort = parameter.sort;
  if (sort.tag === "primitive" && sort.name === "boolean") {
    return Object.freeze([
      Object.freeze({ tag: "boolean" as const, value: false }),
      Object.freeze({ tag: "boolean" as const, value: true }),
    ]);
  }
  if (sort.tag === "named") {
    const declaration = typed.source.declarations.find(
      (candidate): candidate is EnumDeclaration =>
        candidate.tag === "enum" &&
        candidate.declaration_id === sort.declaration_id,
    );
    if (declaration !== undefined) {
      return Object.freeze(
        [...declaration.members].sort().map((member) =>
          Object.freeze({
            tag: "enum" as const,
            declaration_id: declaration.declaration_id,
            member,
          }),
        ),
      );
    }
  }
  if (sort.tag === "primitive") {
    if (sort.name === "boolean") return null;
    return comparisonWitnesses(parameter.name, sort.name, expression);
  }
  if (sort.tag === "list" || sort.tag === "set") {
    const elements = domain.collection_elements[parameter.name];
    if (elements === undefined || elements.length === 0) return null;
    for (const element of elements) {
      if (!matchesSort(element, sort.element, typed)) {
        fail(
          "SFOL_PARTITION_DOMAIN_TYPE_MISMATCH",
          parameter.name,
          "collection element witness does not match the element sort",
        );
      }
    }
    const normalized = normalizeValues(elements, parameter.name);
    const candidates: SemanticValue[] = [
      sort.tag === "list"
        ? { tag: "list", items: [] }
        : { tag: "set", items: [] },
      ...normalized.map((element) =>
        sort.tag === "list"
          ? ({ tag: "list", items: [element] } as const)
          : ({ tag: "set", items: [element] } as const),
      ),
    ];
    const first = normalized[0];
    if (sort.tag === "list" && first !== undefined) {
      candidates.push({ tag: "list", items: [first, first] });
    }
    candidates.push(
      sort.tag === "list"
        ? { tag: "list", items: normalized }
        : { tag: "set", items: normalized },
    );
    return normalizeValues(candidates, parameter.name);
  }
  return null;
}

function comparisonWitnesses(
  variableName: string,
  sort: "string" | "integer" | "rational",
  expression: LogicTerm,
): readonly SemanticValue[] | null {
  const literals: SemanticValue[] = [];
  collectComparisonLiterals(expression, variableName, literals);
  const matching = literals.filter((value) => value.tag === sort);
  if (matching.length === 0) return null;
  const values: SemanticValue[] = [];
  for (const value of matching) {
    if (value.tag === "integer") {
      const integer = BigInt(value.value);
      values.push(
        { tag: "integer", value: (integer - 1n).toString() },
        { tag: "integer", value: integer.toString() },
        { tag: "integer", value: (integer + 1n).toString() },
      );
    } else if (value.tag === "rational") {
      const numerator = BigInt(value.numerator);
      const denominator = BigInt(value.denominator);
      values.push(
        rationalValue((numerator - denominator).toString(), denominator.toString()),
        rationalValue(numerator.toString(), denominator.toString()),
        rationalValue((numerator + denominator).toString(), denominator.toString()),
      );
    } else if (value.tag === "string") {
      values.push(value, {
        tag: "string",
        value:
          value.value === "__domainspec_other__"
            ? "__domainspec_other_2__"
            : "__domainspec_other__",
      });
    }
  }
  return normalizeValues(values, variableName);
}

function collectComparisonLiterals(
  term: LogicTerm,
  variableName: string,
  output: SemanticValue[],
): void {
  if (term.tag === "comparison") {
    if (term.left.tag === "variable" && term.left.name === variableName) {
      const value = literalValue(term.right);
      if (value !== null) output.push(value);
    }
    if (term.right.tag === "variable" && term.right.name === variableName) {
      const value = literalValue(term.left);
      if (value !== null) output.push(value);
    }
  }
  for (const child of childTerms(term)) {
    collectComparisonLiterals(child, variableName, output);
  }
}

function literalValue(term: LogicTerm): SemanticValue | null {
  if (term.tag !== "literal") return null;
  if (term.value.tag === "rational") {
    return rationalValue(term.value.numerator, term.value.denominator);
  }
  return term.value;
}

function universeAssignments(
  clause: LogicClause,
  typed: TypedLogicModule,
  domain: NormalizedPartitionDomain,
): readonly {
  readonly universeId: string;
  readonly variants: readonly (readonly SemanticValue[])[];
}[] {
  const ids = [...collectUniverseIds(clause.expression)].sort();
  return ids.map((universeId) => {
    const declaration = typed.source.declarations.find(
      (candidate): candidate is FixtureUniverseDeclaration =>
        candidate.tag === "fixture-universe" &&
        candidate.declaration_id === universeId,
    );
    if (declaration === undefined) {
      fail(
        "SFOL_PARTITION_DOMAIN_REQUIRED",
        universeId,
        "quantifier universe declaration is unavailable",
      );
    }
    const variants =
      domain.universe_variants[universeId] ??
      (domain.universes[universeId] === undefined
        ? undefined
        : [domain.universes[universeId]]);
    if (variants === undefined || variants.length === 0) {
      fail(
        "SFOL_PARTITION_DOMAIN_REQUIRED",
        universeId,
        "quantifier universe variants are required",
      );
    }
    const normalized = variants.map((variant) => {
      assertNoDuplicateValues(variant, universeId);
      if (variant.length === 0 && !declaration.admits_empty) {
        fail(
          "SFOL_PARTITION_DOMAIN_EMPTY",
          universeId,
          "the declared universe does not admit an empty variant",
        );
      }
      for (const value of variant) {
        if (!matchesSort(value, declaration.element_sort, typed)) {
          fail(
            "SFOL_PARTITION_DOMAIN_TYPE_MISMATCH",
            universeId,
            "universe witness does not match its declared element sort",
          );
        }
      }
      return normalizeValues(variant, universeId);
    });
    const identities = normalized.map(canonicalSfolJson);
    if (new Set(identities).size !== identities.length) {
      fail(
        "SFOL_PARTITION_DOMAIN_DUPLICATE",
        universeId,
        "universe variants contain duplicate finite universes",
      );
    }
    return { universeId, variants: deepFreeze(normalized) };
  });
}

function reduceMcdc(
  clause: LogicClause,
  typed: TypedLogicModule,
  parameters: readonly ParameterDeclaration[],
  candidates: readonly {
    readonly inputs: Readonly<Record<string, SemanticValue>>;
    readonly universes: Readonly<Record<string, readonly SemanticValue[]>>;
  }[],
  maxCases: number,
): typeof candidates {
  if (
    parameters.some(
      ({ sort }) => sort.tag !== "primitive" || sort.name !== "boolean",
    )
  ) {
    fail(
      "SFOL_PARTITION_MCDC_UNSUPPORTED",
      clause.clause_id,
      "mcdc/v1 supports Boolean clause inputs only",
    );
  }
  const evaluated = candidates
    .map((candidate) => {
      const result = evaluateTerm(typed, clause.expression, {
        variables: candidate.inputs,
        universes: candidate.universes,
      });
      if (result.status === "indeterminate" || result.value.tag !== "boolean") {
        fail(
          "SFOL_PARTITION_EVALUATION_INDETERMINATE",
          clause.clause_id,
          "mcdc/v1 requires a determinate Boolean result for every analyzed valuation",
        );
      }
      return { candidate, result: result.value.value };
    })
    .sort((left, right) =>
      canonicalSfolJson(left.candidate).localeCompare(
        canonicalSfolJson(right.candidate),
      ),
    );
  const selected = new Map<string, (typeof candidates)[number]>();
  for (const parameter of parameters) {
    let chosen:
      | readonly [(typeof evaluated)[number], (typeof evaluated)[number]]
      | null = null;
    for (let leftIndex = 0; leftIndex < evaluated.length && chosen === null; leftIndex += 1) {
      const left = evaluated[leftIndex];
      if (left === undefined) continue;
      for (let rightIndex = leftIndex + 1; rightIndex < evaluated.length; rightIndex += 1) {
        const right = evaluated[rightIndex];
        if (
          right !== undefined &&
          left.result !== right.result &&
          differsOnlyAt(left.candidate, right.candidate, parameter.name)
        ) {
          chosen = [left, right];
          break;
        }
      }
    }
    if (chosen === null) {
      fail(
        "SFOL_PARTITION_MCDC_INDEPENDENCE_UNSATISFIED",
        parameter.name,
        "no valuation pair demonstrates independent decision influence",
      );
    }
    for (const entry of chosen) {
      selected.set(canonicalSfolJson(entry.candidate), entry.candidate);
    }
  }
  const result = [...selected.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([, candidate]) => candidate);
  if (result.length > maxCases) {
    fail(
      "SFOL_PARTITION_BUDGET_EXCEEDED",
      clause.clause_id,
      `mcdc/v1 requires ${result.length} selected cases; output budget is ${maxCases}`,
    );
  }
  return result;
}

function differsOnlyAt(
  left: {
    readonly inputs: Readonly<Record<string, SemanticValue>>;
    readonly universes: Readonly<Record<string, readonly SemanticValue[]>>;
  },
  right: {
    readonly inputs: Readonly<Record<string, SemanticValue>>;
    readonly universes: Readonly<Record<string, readonly SemanticValue[]>>;
  },
  parameterName: string,
): boolean {
  if (canonicalSfolJson(left.universes) !== canonicalSfolJson(right.universes)) {
    return false;
  }
  const names = [...new Set([...Object.keys(left.inputs), ...Object.keys(right.inputs)])].sort();
  return names.every((name) => {
    const equal =
      canonicalSfolJson(left.inputs[name]) === canonicalSfolJson(right.inputs[name]);
    return name === parameterName ? !equal : equal;
  });
}

function collectUniverseIds(term: LogicTerm, output = new Set<string>()): Set<string> {
  if (term.tag === "quantifier") output.add(term.universe_id);
  for (const child of childTerms(term)) collectUniverseIds(child, output);
  return output;
}

function childTerms(term: LogicTerm): readonly LogicTerm[] {
  switch (term.tag) {
    case "field":
      return [term.target];
    case "record":
      return term.fields.map(({ value }) => value);
    case "list":
    case "set":
      return term.items;
    case "arithmetic":
    case "comparison":
      return [term.left, term.right];
    case "negate":
    case "not":
      return [term.operand];
    case "boolean":
      return term.operands;
    case "conditional":
      return [term.condition, term.when_true, term.when_false];
    case "fold":
      return term.expression === null
        ? [term.collection]
        : [term.collection, term.expression];
    case "quantifier":
      return [term.predicate];
    case "call":
      return term.arguments;
    case "literal":
    case "variable":
    case "enum":
      return [];
  }
}

function matchesSort(
  value: SemanticValue,
  sort: SortRef,
  typed: TypedLogicModule,
): boolean {
  if (sort.tag === "primitive") return value.tag === sort.name;
  if (sort.tag === "list") {
    return (
      value.tag === "list" &&
      value.items.every((item) => matchesSort(item, sort.element, typed))
    );
  }
  if (sort.tag === "set") {
    return (
      value.tag === "set" &&
      value.items.every((item) => matchesSort(item, sort.element, typed))
    );
  }
  const declaration = typed.source.declarations.find(
    (candidate) => candidate.declaration_id === sort.declaration_id,
  );
  if (declaration?.tag === "enum") {
    return (
      value.tag === "enum" &&
      value.declaration_id === declaration.declaration_id &&
      declaration.members.includes(value.member)
    );
  }
  if (declaration?.tag === "record") {
    return value.tag === "record" && value.declaration_id === declaration.declaration_id;
  }
  return false;
}

function normalizeValues(
  values: readonly SemanticValue[],
  subject: string,
): readonly SemanticValue[] {
  const sorted = [...values].sort((left, right) =>
    canonicalSfolJson(left).localeCompare(canonicalSfolJson(right)),
  );
  const canonical = sorted.map(canonicalSfolJson);
  if (new Set(canonical).size !== canonical.length) {
    const deduplicated = [...new Map(sorted.map((value) => [canonicalSfolJson(value), value])).values()];
    if (deduplicated.length === 0) {
      fail(
        "SFOL_PARTITION_DOMAIN_DUPLICATE",
        subject,
        "finite witness domain contains only duplicate semantic values",
      );
    }
    return deepFreeze(deduplicated);
  }
  return deepFreeze(sorted);
}

function assertNoDuplicateValues(
  values: readonly SemanticValue[],
  subject: string,
): void {
  const identities = values.map(canonicalSfolJson);
  if (new Set(identities).size !== identities.length) {
    fail(
      "SFOL_PARTITION_DOMAIN_DUPLICATE",
      subject,
      "an explicitly supplied finite domain contains duplicate semantic values",
    );
  }
}

function enumerateAssignments(
  domains: readonly {
    readonly parameter: ParameterDeclaration;
    readonly values: readonly SemanticValue[];
  }[],
  index: number,
  current: Record<string, SemanticValue>,
  output: Readonly<Record<string, SemanticValue>>[],
): void {
  const entry = domains[index];
  if (entry === undefined) {
    output.push(deepFreeze({ ...current }));
    return;
  }
  for (const value of entry.values) {
    current[entry.parameter.name] = value;
    enumerateAssignments(domains, index + 1, current, output);
  }
  delete current[entry.parameter.name];
}

function enumerateUniverses(
  domains: readonly {
    readonly universeId: string;
    readonly variants: readonly (readonly SemanticValue[])[];
  }[],
  index: number,
  current: Record<string, readonly SemanticValue[]>,
  output: Readonly<Record<string, readonly SemanticValue[]>>[],
): void {
  const entry = domains[index];
  if (entry === undefined) {
    output.push(deepFreeze({ ...current }));
    return;
  }
  for (const variant of entry.variants) {
    current[entry.universeId] = variant;
    enumerateUniverses(domains, index + 1, current, output);
  }
  delete current[entry.universeId];
}

function normalizeDomain(
  domain: PartitionDomain | undefined,
): NormalizedPartitionDomain {
  return deepFreeze({
    inputs: normalizeRecordOfValues(domain?.inputs),
    collection_elements: normalizeRecordOfValues(domain?.collection_elements),
    universes: normalizeRecordOfValues(domain?.universes),
    universe_variants: Object.fromEntries(
      Object.entries(domain?.universe_variants ?? {})
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([name, variants]) => [
          name,
          Object.freeze(variants.map((variant) => Object.freeze([...variant]))),
        ]),
    ),
  });
}

function normalizeRecordOfValues(
  record: Readonly<Record<string, readonly SemanticValue[]>> | undefined,
): Readonly<Record<string, readonly SemanticValue[]>> {
  return Object.fromEntries(
    Object.entries(record ?? {})
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([name, values]) => [name, Object.freeze([...values])]),
  );
}

function validateRuleSet(ruleset: PartitionRuleSet): void {
  const commonValid =
    Number.isSafeInteger(ruleset.max_cases) && ruleset.max_cases >= 1;
  const exhaustiveValid =
    ruleset.ruleset_id === EXHAUSTIVE_FINITE_RULESET.ruleset_id &&
    ruleset.ruleset_version === EXHAUSTIVE_FINITE_RULESET.ruleset_version &&
    ruleset.mode === EXHAUSTIVE_FINITE_RULESET.mode;
  const mcdcValid =
    ruleset.ruleset_id === MCDC_RULESET.ruleset_id &&
    ruleset.ruleset_version === MCDC_RULESET.ruleset_version &&
    ruleset.mode === MCDC_RULESET.mode &&
    Number.isSafeInteger(ruleset.max_analysis_cases) &&
    ruleset.max_analysis_cases >= ruleset.max_cases;
  if (!commonValid || (!exhaustiveValid && !mcdcValid)) {
    fail(
      "SFOL_PARTITION_INVALID_RULESET",
      "ruleset",
      "expected exhaustive-finite/v1 or mcdc/v1 with positive safe integer bounds",
    );
  }
}

function fail(
  code: PartitionDiagnosticCode,
  subject: string,
  detail: string,
): never {
  throw new PartitionAbort({
    code,
    stage: "partition-derivation",
    subject,
    detail,
  });
}

function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) deepFreeze(child);
  }
  return value;
}
