import {
  canonicalSfolJson,
  digestSfolValue,
  type PureFixture,
} from "../cases/index.js";
import { evaluateTerm } from "../evaluator/index.js";
import type {
  LogicClause,
  LogicTerm,
  NodeLogicModuleV1,
  SourceSpan,
} from "../language/ast.js";
import {
  typecheckLogicModule,
  type TypedLogicModule,
} from "../language/typecheck.js";

export const SFOL_MUTATION_CATALOG_VERSION =
  "domainspec-sfol-mutation-catalog/v1" as const;

export interface MutationAdequacyInput {
  readonly typed: TypedLogicModule;
  readonly clause_id: string;
  readonly fixtures: readonly PureFixture[];
  readonly catalog_version: typeof SFOL_MUTATION_CATALOG_VERSION;
  readonly evaluation_domain:
    | { readonly kind: "exhaustive-finite"; readonly domain_digest: string }
    | { readonly kind: "bounded-sample"; readonly domain_digest: string };
}

export interface SfolMutantResult {
  readonly mutant_id: string;
  readonly operator: string;
  readonly replacement: string;
  readonly source_span: SourceSpan;
  readonly status:
    | "killed"
    | "equivalent-bounded"
    | "survived"
    | "invalid-mutant";
  readonly kill_fixture_ids: readonly string[];
  readonly mutant_clause_digest: string;
}

export interface MutationAdequacyReceipt {
  readonly schema_version: "domainspec-sfol-mutation-adequacy/v1";
  readonly catalog_version: typeof SFOL_MUTATION_CATALOG_VERSION;
  readonly clause_id: string;
  readonly clause_digest: string;
  readonly fixture_set_digest: string;
  readonly fixture_count: number;
  readonly evaluation_domain: MutationAdequacyInput["evaluation_domain"];
  readonly mutant_count: number;
  readonly killed_count: number;
  readonly equivalent_bounded_count: number;
  readonly invalid_mutant_count: number;
  readonly surviving_supported_count: number;
  readonly result: "pass" | "fail";
  readonly mutants: readonly SfolMutantResult[];
  readonly receipt_digest: string;
}

export interface MutationAdequacyDiagnostic {
  readonly code:
    | "SFOL_MUTATION_CATALOG_UNSUPPORTED"
    | "SFOL_MUTATION_CLAUSE_UNAVAILABLE"
    | "SFOL_MUTATION_FIXTURE_EMPTY"
    | "SFOL_MUTATION_ORIGINAL_INDETERMINATE";
  readonly stage: "mutation-adequacy";
  readonly subject: string;
  readonly detail: string;
}

export type MutationAdequacyResult =
  | { readonly ok: true; readonly value: MutationAdequacyReceipt }
  | {
      readonly ok: false;
      readonly diagnostics: readonly MutationAdequacyDiagnostic[];
    };

interface MutationSite {
  readonly path: readonly (string | number)[];
  readonly operator: string;
  readonly replacement: string;
  readonly span: SourceSpan;
  readonly replace: (term: LogicTerm) => LogicTerm;
}

class MutationAbort extends Error {
  constructor(readonly diagnostic: MutationAdequacyDiagnostic) {
    super(diagnostic.detail);
    this.name = "MutationAbort";
  }
}

export function deriveMutationAdequacy(
  input: MutationAdequacyInput,
): MutationAdequacyResult {
  try {
    if (input.catalog_version !== SFOL_MUTATION_CATALOG_VERSION) {
      abort(
        "SFOL_MUTATION_CATALOG_UNSUPPORTED",
        "catalog_version",
        `expected ${SFOL_MUTATION_CATALOG_VERSION}`,
      );
    }
    if (input.fixtures.length === 0) {
      abort(
        "SFOL_MUTATION_FIXTURE_EMPTY",
        "fixtures",
        "mutation adequacy requires a nonempty bounded fixture domain",
      );
    }
    const clause = input.typed.source.clauses.find(
      (candidate) => candidate.clause_id === input.clause_id,
    );
    if (clause === undefined) {
      abort(
        "SFOL_MUTATION_CLAUSE_UNAVAILABLE",
        input.clause_id,
        "selected clause is absent from the typed module",
      );
    }

    const original = new Map<string, string>();
    for (const fixture of input.fixtures) {
      const result = evaluateTerm(input.typed, clause.expression, {
        variables: fixture.inputs,
        universes: fixture.universes,
      });
      if (result.status === "indeterminate") {
        abort(
          "SFOL_MUTATION_ORIGINAL_INDETERMINATE",
          fixture.fixture_id,
          result.diagnostic.detail,
        );
      }
      original.set(fixture.fixture_id, digestSfolValue(result.value));
    }

    const sites: MutationSite[] = [];
    collectSites(clause.expression, [], sites);
    const mutants = sites.map((site) =>
      evaluateMutant(
        input.typed.source,
        clause,
        site,
        input.fixtures,
        original,
        input.evaluation_domain.kind,
      ),
    );
    mutants.sort((left, right) => left.mutant_id.localeCompare(right.mutant_id));
    const unsigned = {
      schema_version: "domainspec-sfol-mutation-adequacy/v1" as const,
      catalog_version: SFOL_MUTATION_CATALOG_VERSION,
      clause_id: clause.clause_id,
      clause_digest: digestSfolValue(clause),
      fixture_set_digest: digestSfolValue(input.fixtures),
      fixture_count: input.fixtures.length,
      evaluation_domain: input.evaluation_domain,
      mutant_count: mutants.length,
      killed_count: mutants.filter(({ status }) => status === "killed").length,
      equivalent_bounded_count: mutants.filter(
        ({ status }) => status === "equivalent-bounded",
      ).length,
      invalid_mutant_count: mutants.filter(
        ({ status }) => status === "invalid-mutant",
      ).length,
      surviving_supported_count: mutants.filter(
        ({ status }) => status === "survived",
      ).length,
      result: mutants.some(({ status }) => status === "survived")
        ? ("fail" as const)
        : ("pass" as const),
      mutants: deepFreeze(mutants),
    };
    return Object.freeze({
      ok: true,
      value: deepFreeze({
        ...unsigned,
        receipt_digest: digestSfolValue(unsigned),
      }),
    });
  } catch (error: unknown) {
    if (error instanceof MutationAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_MUTATION_ORIGINAL_INDETERMINATE" as const,
          stage: "mutation-adequacy" as const,
          subject: "mutation",
          detail: "mutation derivation received structurally invalid input",
        }),
      ]),
    });
  }
}

function evaluateMutant(
  source: NodeLogicModuleV1,
  clause: LogicClause,
  site: MutationSite,
  fixtures: readonly PureFixture[],
  original: ReadonlyMap<string, string>,
  domainKind: MutationAdequacyInput["evaluation_domain"]["kind"],
): SfolMutantResult {
  const expression = replaceAtPath(clause.expression, site.path, site.replace);
  const mutatedClause = { ...clause, expression };
  const mutatedSource: NodeLogicModuleV1 = {
    ...source,
    clauses: source.clauses.map((candidate) =>
      candidate.clause_id === clause.clause_id ? mutatedClause : candidate,
    ),
  };
  const identity = {
    catalog_version: SFOL_MUTATION_CATALOG_VERSION,
    clause_id: clause.clause_id,
    path: site.path,
    operator: site.operator,
    replacement: site.replacement,
    source_span: site.span,
  };
  const mutantId = `mutant:${digestSfolValue(identity)}`;
  const mutantClauseDigest = digestSfolValue(mutatedClause);
  const typed = typecheckLogicModule(mutatedSource);
  if (!typed.ok) {
    return deepFreeze({
      mutant_id: mutantId,
      operator: site.operator,
      replacement: site.replacement,
      source_span: site.span,
      status: "invalid-mutant",
      kill_fixture_ids: [],
      mutant_clause_digest: mutantClauseDigest,
    });
  }

  const kills: string[] = [];
  let indeterminate = false;
  for (const fixture of fixtures) {
    const result = evaluateTerm(typed.value, mutatedClause.expression, {
      variables: fixture.inputs,
      universes: fixture.universes,
    });
    if (
      result.status === "value" &&
      digestSfolValue(result.value) !== original.get(fixture.fixture_id)
    ) {
      kills.push(fixture.fixture_id);
    } else if (result.status === "indeterminate") {
      indeterminate = true;
    }
  }
  kills.sort();
  return deepFreeze({
    mutant_id: mutantId,
    operator: site.operator,
    replacement: site.replacement,
    source_span: site.span,
    status: indeterminate
      ? "invalid-mutant"
      : kills.length > 0
        ? "killed"
        : domainKind === "exhaustive-finite"
          ? "equivalent-bounded"
          : "survived",
    kill_fixture_ids: kills,
    mutant_clause_digest: mutantClauseDigest,
  });
}

function collectSites(
  term: LogicTerm,
  path: readonly (string | number)[],
  output: MutationSite[],
): void {
  if (term.tag === "boolean") {
    output.push({
      path,
      operator: term.operator,
      replacement: term.operator === "and" ? "or" : "and",
      span: term.span,
      replace: (value) =>
        value.tag === "boolean"
          ? {
              ...value,
              operator: value.operator === "and" ? "or" : "and",
            }
          : value,
    });
  } else if (term.tag === "variable") {
    output.push({
      path,
      operator: "identity",
      replacement: "not",
      span: term.span,
      replace: (value) => ({ tag: "not", operand: value, span: value.span }),
    });
  } else if (term.tag === "literal" && term.value.tag === "boolean") {
    output.push({
      path,
      operator: String(term.value.value),
      replacement: String(!term.value.value),
      span: term.span,
      replace: (value) =>
        value.tag === "literal" && value.value.tag === "boolean"
          ? { ...value, value: { ...value.value, value: !value.value.value } }
          : value,
    });
  } else if (term.tag === "comparison") {
    const replacement = comparisonReplacement(term.operator);
    output.push({
      path,
      operator: term.operator,
      replacement,
      span: term.span,
      replace: (value) =>
        value.tag === "comparison" ? { ...value, operator: replacement } : value,
    });
  } else if (term.tag === "quantifier") {
    output.push({
      path,
      operator: term.operator,
      replacement: term.operator === "exists" ? "forall" : "exists",
      span: term.span,
      replace: (value) =>
        value.tag === "quantifier"
          ? {
              ...value,
              operator: value.operator === "exists" ? "forall" : "exists",
            }
          : value,
    });
  }

  for (const [key, child] of childTerms(term)) {
    collectSites(child, [...path, ...key], output);
  }
}

function childTerms(
  term: LogicTerm,
): readonly [readonly (string | number)[], LogicTerm][] {
  switch (term.tag) {
    case "field":
      return [[['target'], term.target]];
    case "record":
      return term.fields.map((field, index) => [
        ["fields", index, "value"],
        field.value,
      ] as const);
    case "list":
    case "set":
      return term.items.map((item, index) => [["items", index], item] as const);
    case "arithmetic":
    case "comparison":
      return [
        [["left"], term.left],
        [["right"], term.right],
      ];
    case "negate":
      return [[['operand'], term.operand]];
    case "boolean":
      return term.operands.map((operand, index) => [
        ["operands", index],
        operand,
      ] as const);
    case "not":
      return [[['operand'], term.operand]];
    case "conditional":
      return [
        [["condition"], term.condition],
        [["when_true"], term.when_true],
        [["when_false"], term.when_false],
      ];
    case "fold":
      return term.expression === null
        ? [[['collection'], term.collection]]
        : [[['collection'], term.collection], [['expression'], term.expression]];
    case "quantifier":
      return [[['predicate'], term.predicate]];
    case "call":
      return term.arguments.map((argument, index) => [
        ["arguments", index],
        argument,
      ] as const);
    default:
      return [];
  }
}

function replaceAtPath(
  root: LogicTerm,
  path: readonly (string | number)[],
  replace: (term: LogicTerm) => LogicTerm,
): LogicTerm {
  const clone = JSON.parse(canonicalSfolJson(root)) as LogicTerm;
  if (path.length === 0) return replace(clone);
  let parent: any = clone;
  for (const segment of path.slice(0, -1)) parent = parent[segment];
  const leaf = path[path.length - 1]!;
  parent[leaf] = replace(parent[leaf] as LogicTerm);
  return clone;
}

function comparisonReplacement(
  operator: "eq" | "neq" | "lt" | "lte" | "gt" | "gte",
) {
  switch (operator) {
    case "eq": return "neq" as const;
    case "neq": return "eq" as const;
    case "lt": return "lte" as const;
    case "lte": return "lt" as const;
    case "gt": return "gte" as const;
    case "gte": return "gt" as const;
  }
}

function abort(
  code: "SFOL_MUTATION_CATALOG_UNSUPPORTED" | "SFOL_MUTATION_CLAUSE_UNAVAILABLE" | "SFOL_MUTATION_FIXTURE_EMPTY" | "SFOL_MUTATION_ORIGINAL_INDETERMINATE",
  subject: string,
  detail: string,
): never {
  throw new MutationAbort({ code, stage: "mutation-adequacy", subject, detail });
}

function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) deepFreeze(child);
  }
  return value;
}
