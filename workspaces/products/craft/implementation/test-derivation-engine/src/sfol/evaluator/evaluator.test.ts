import { describe, expect, it } from "vitest";

import type {
  LogicClause,
  LogicDeclaration,
  LogicTerm,
  LogicTermTag,
  NodeLogicModuleV1,
  ParameterDeclaration,
  SortRef,
} from "../language/ast.js";
import {
  type TypedLogicModule,
  typecheckLogicModule,
} from "../language/typecheck.js";
import {
  evaluatePredicate,
  evaluateTerm,
  integerValue,
  rationalValue,
  type RecordValue,
} from "./index.js";

const SOURCE_ID = "framework.SemanticCorpus";
const boolSort = { tag: "primitive", name: "boolean" } as const;
const intSort = { tag: "primitive", name: "integer" } as const;
const rationalSort = { tag: "primitive", name: "rational" } as const;
const stateSort = {
  tag: "named",
  declaration_id: "framework.State",
} as const;
const itemSort = {
  tag: "named",
  declaration_id: "framework.Item",
} as const;

function span(path: string) {
  return {
    source_id: SOURCE_ID,
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 10 },
  };
}

function integer(value: string, path: string): LogicTerm {
  return {
    tag: "literal",
    value: { tag: "integer", value },
    span: span(path),
  };
}

function rational(
  numerator: string,
  denominator: string,
  path: string,
): LogicTerm {
  return {
    tag: "literal",
    value: { tag: "rational", numerator, denominator },
    span: span(path),
  };
}

function bool(value: boolean, path: string): LogicTerm {
  return {
    tag: "literal",
    value: { tag: "boolean", value },
    span: span(path),
  };
}

function variable(
  name: string,
  path: string,
): LogicTerm {
  return { tag: "variable", name, span: span(path) };
}

function parameter(
  name: string,
  sort: SortRef,
  path: string,
): ParameterDeclaration {
  return { name, sort, span: span(path) };
}

function clause(
  clauseId: string,
  expression: LogicTerm,
  resultSort: SortRef,
  inputs: readonly ParameterDeclaration[] = [],
  kind: LogicClause["kind"] = "function",
): LogicClause {
  return {
    clause_id: clauseId,
    kind,
    status: "admitted",
    inputs,
    result_sort: resultSort,
    expression,
    observation_sort: null,
    span: span(`body.logic.clauses.${clauseId}`),
  };
}

function semanticModule(): NodeLogicModuleV1 {
  const declarations: readonly LogicDeclaration[] = [
    {
      tag: "enum",
      declaration_id: "framework.State",
      members: ["OPEN", "CLOSED"],
      span: span("body.logic.declarations.state"),
    },
    {
      tag: "record",
      declaration_id: "framework.Item",
      fields: [
        {
          name: "amount",
          sort: rationalSort,
          required: true,
          span: span("body.logic.declarations.item.amount"),
        },
        {
          name: "state",
          sort: stateSort,
          required: true,
          span: span("body.logic.declarations.item.state"),
        },
      ],
      span: span("body.logic.declarations.item"),
    },
    {
      tag: "fixture-universe",
      declaration_id: "framework.items",
      element_sort: itemSort,
      admits_empty: false,
      span: span("body.logic.declarations.items"),
    },
    {
      tag: "function",
      declaration_id: "framework.increment",
      parameters: [
        parameter(
          "x",
          rationalSort,
          "body.logic.declarations.increment.x",
        ),
      ],
      result: rationalSort,
      body: {
        tag: "arithmetic",
        operator: "add",
        left: variable(
          "x",
          "body.logic.declarations.increment.body.x",
        ),
        right: integer(
          "1",
          "body.logic.declarations.increment.body.one",
        ),
        span: span("body.logic.declarations.increment.body"),
      },
      span: span("body.logic.declarations.increment"),
    },
    {
      tag: "predicate",
      declaration_id: "framework.is-positive",
      parameters: [
        parameter(
          "x",
          rationalSort,
          "body.logic.declarations.is-positive.x",
        ),
      ],
      body: {
        tag: "comparison",
        operator: "gt",
        left: variable(
          "x",
          "body.logic.declarations.is-positive.body.x",
        ),
        right: integer(
          "0",
          "body.logic.declarations.is-positive.body.zero",
        ),
        span: span("body.logic.declarations.is-positive.body"),
      },
      span: span("body.logic.declarations.is-positive"),
    },
  ];

  const recordTerm: LogicTerm = {
    tag: "record",
    declaration_id: "framework.Item",
    fields: [
      {
        name: "amount",
        value: {
          tag: "negate",
          operand: rational(
            "3",
            "2",
            "body.logic.corpus.record.amount.value",
          ),
          span: span("body.logic.corpus.record.amount"),
        },
      },
      {
        name: "state",
        value: {
          tag: "enum",
          declaration_id: "framework.State",
          member: "OPEN",
          span: span("body.logic.corpus.record.state"),
        },
      },
    ],
    span: span("body.logic.corpus.record"),
  };

  return {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: "framework.semantic-corpus",
    source: {
      feature_id: "framework",
      node_id: SOURCE_ID,
      source_id: SOURCE_ID,
      source_path: "nodes/semantic-corpus.yaml",
    },
    declarations,
    clauses: [
      clause(
        "exact-arithmetic",
        {
          tag: "arithmetic",
          operator: "divide",
          left: {
            tag: "arithmetic",
            operator: "add",
            left: rational(
              "1",
              "2",
              "body.logic.corpus.exact.half",
            ),
            right: integer("1", "body.logic.corpus.exact.one"),
            span: span("body.logic.corpus.exact.sum"),
          },
          right: integer("3", "body.logic.corpus.exact.three"),
          span: span("body.logic.corpus.exact"),
        },
        rationalSort,
      ),
      clause(
        "record-field",
        {
          tag: "field",
          target: recordTerm,
          field: "amount",
          span: span("body.logic.corpus.field"),
        },
        rationalSort,
      ),
      clause(
        "deterministic-set",
        {
          tag: "set",
          items: [
            integer("2", "body.logic.corpus.set.two-first"),
            integer("1", "body.logic.corpus.set.one"),
            integer("2", "body.logic.corpus.set.two-second"),
          ],
          span: span("body.logic.corpus.set"),
        },
        { tag: "set", element: intSort },
      ),
      clause(
        "boolean-connectives",
        {
          tag: "boolean",
          operator: "and",
          operands: [
            {
              tag: "comparison",
              operator: "gt",
              left: integer("3", "body.logic.corpus.boolean.three"),
              right: integer("2", "body.logic.corpus.boolean.two"),
              span: span("body.logic.corpus.boolean.comparison"),
            },
            {
              tag: "not",
              operand: bool(
                false,
                "body.logic.corpus.boolean.false",
              ),
              span: span("body.logic.corpus.boolean.not"),
            },
          ],
          span: span("body.logic.corpus.boolean"),
        },
        boolSort,
        [],
        "predicate",
      ),
      clause(
        "conditional",
        {
          tag: "conditional",
          condition: bool(true, "body.logic.corpus.conditional.condition"),
          when_true: integer(
            "4",
            "body.logic.corpus.conditional.true",
          ),
          when_false: rational(
            "9",
            "2",
            "body.logic.corpus.conditional.false",
          ),
          span: span("body.logic.corpus.conditional"),
        },
        rationalSort,
      ),
      clause(
        "fold-sum",
        {
          tag: "fold",
          operator: "sum",
          collection: {
            tag: "list",
            items: [
              rational("1", "2", "body.logic.corpus.fold.half"),
              rational("3", "2", "body.logic.corpus.fold.three-halves"),
            ],
            span: span("body.logic.corpus.fold.collection"),
          },
          item_name: "item",
          expression: variable(
            "item",
            "body.logic.corpus.fold.expression",
          ),
          span: span("body.logic.corpus.fold"),
        },
        rationalSort,
      ),
      clause(
        "fold-count",
        {
          tag: "fold",
          operator: "count",
          collection: {
            tag: "list",
            items: [
              integer("7", "body.logic.corpus.count.seven"),
              integer("8", "body.logic.corpus.count.eight"),
            ],
            span: span("body.logic.corpus.count.collection"),
          },
          item_name: "ignored",
          expression: null,
          span: span("body.logic.corpus.count"),
        },
        intSort,
      ),
      clause(
        "finite-quantifier",
        {
          tag: "quantifier",
          operator: "forall",
          universe_id: "framework.items",
          variable_name: "item",
          variable_sort: itemSort,
          predicate: {
            tag: "comparison",
            operator: "gt",
            left: {
              tag: "field",
              target: variable(
                "item",
                "body.logic.corpus.quantifier.item",
              ),
              field: "amount",
              span: span("body.logic.corpus.quantifier.amount"),
            },
            right: variable(
              "threshold",
              "body.logic.corpus.quantifier.threshold",
            ),
            span: span("body.logic.corpus.quantifier.predicate"),
          },
          span: span("body.logic.corpus.quantifier"),
        },
        boolSort,
        [
          parameter(
            "threshold",
            rationalSort,
            "body.logic.corpus.quantifier.input.threshold",
          ),
        ],
        "invariant",
      ),
      clause(
        "function-call",
        {
          tag: "call",
          declaration_id: "framework.increment",
          arguments: [
            rational("1", "2", "body.logic.corpus.call.function.argument"),
          ],
          span: span("body.logic.corpus.call.function"),
        },
        rationalSort,
      ),
      clause(
        "predicate-call",
        {
          tag: "call",
          declaration_id: "framework.is-positive",
          arguments: [
            rational("1", "3", "body.logic.corpus.call.predicate.argument"),
          ],
          span: span("body.logic.corpus.call.predicate"),
        },
        boolSort,
        [],
        "predicate",
      ),
      clause(
        "unbound-variable",
        variable("missing", "body.logic.corpus.unbound"),
        intSort,
        [
          parameter(
            "missing",
            intSort,
            "body.logic.corpus.unbound.input",
          ),
        ],
      ),
      clause(
        "division-by-zero",
        {
          tag: "arithmetic",
          operator: "divide",
          left: integer("1", "body.logic.corpus.zero.one"),
          right: integer("0", "body.logic.corpus.zero.zero"),
          span: span("body.logic.corpus.zero"),
        },
        rationalSort,
      ),
      clause(
        "invalid-integer",
        integer("01", "body.logic.corpus.invalid-integer"),
        intSort,
      ),
    ],
  };
}

function typedCorpus(): TypedLogicModule {
  const result = typecheckLogicModule(semanticModule());
  if (!result.ok) {
    throw new Error(JSON.stringify(result.diagnostics));
  }
  return result.value;
}

function expression(
  typed: TypedLogicModule,
  clauseId: string,
): LogicTerm {
  const found = typed.source.clauses.find(
    (candidate) => candidate.clause_id === clauseId,
  );
  if (found === undefined) {
    throw new Error(`missing corpus clause ${clauseId}`);
  }
  return found.expression;
}

function item(amount: string): RecordValue {
  return {
    tag: "record",
    declaration_id: "framework.Item",
    fields: {
      amount: rationalValue(amount, "1"),
      state: {
        tag: "enum",
        declaration_id: "framework.State",
        member: "OPEN",
      },
    },
  };
}

function collectTermTags(term: LogicTerm, tags: Set<LogicTermTag>): void {
  tags.add(term.tag);
  switch (term.tag) {
    case "literal":
    case "variable":
    case "enum":
      return;
    case "field":
      collectTermTags(term.target, tags);
      return;
    case "record":
      term.fields.forEach((field) => collectTermTags(field.value, tags));
      return;
    case "list":
    case "set":
      term.items.forEach((item) => collectTermTags(item, tags));
      return;
    case "arithmetic":
    case "comparison":
      collectTermTags(term.left, tags);
      collectTermTags(term.right, tags);
      return;
    case "negate":
    case "not":
      collectTermTags(term.operand, tags);
      return;
    case "boolean":
      term.operands.forEach((operand) => collectTermTags(operand, tags));
      return;
    case "conditional":
      collectTermTags(term.condition, tags);
      collectTermTags(term.when_true, tags);
      collectTermTags(term.when_false, tags);
      return;
    case "fold":
      collectTermTags(term.collection, tags);
      if (term.expression !== null) {
        collectTermTags(term.expression, tags);
      }
      return;
    case "quantifier":
      collectTermTags(term.predicate, tags);
      return;
    case "call":
      term.arguments.forEach((argument) => collectTermTags(argument, tags));
      return;
  }
}

describe("DS-SFOL independent evaluator", () => {
  it("binds the semantic corpus to all 16 DS-SFOL v1 term formations", () => {
    const module = semanticModule();
    const tags = new Set<LogicTermTag>();
    for (const declaration of module.declarations) {
      if (declaration.tag === "function" || declaration.tag === "predicate") {
        collectTermTags(declaration.body, tags);
      }
    }
    module.clauses.forEach((entry) =>
      collectTermTags(entry.expression, tags),
    );

    expect([...tags].sort()).toEqual([
      "arithmetic",
      "boolean",
      "call",
      "comparison",
      "conditional",
      "enum",
      "field",
      "fold",
      "list",
      "literal",
      "negate",
      "not",
      "quantifier",
      "record",
      "set",
      "variable",
    ]);
  });

  it("retains exact normalized rational arithmetic", () => {
    const typed = typedCorpus();

    expect(evaluateTerm(typed, expression(typed, "exact-arithmetic"))).toEqual({
      status: "value",
      value: { tag: "rational", numerator: "1", denominator: "2" },
    });
  });

  it("evaluates records, fields, enums, and deterministic sets", () => {
    const typed = typedCorpus();
    const field = expression(typed, "record-field");
    if (field.tag !== "field") {
      throw new Error("corpus field clause changed shape");
    }

    expect(evaluateTerm(typed, field.target)).toEqual({
      status: "value",
      value: {
        tag: "record",
        declaration_id: "framework.Item",
        fields: {
          amount: {
            tag: "rational",
            numerator: "-3",
            denominator: "2",
          },
          state: {
            tag: "enum",
            declaration_id: "framework.State",
            member: "OPEN",
          },
        },
      },
    });
    expect(evaluateTerm(typed, field)).toEqual({
      status: "value",
      value: {
        tag: "rational",
        numerator: "-3",
        denominator: "2",
      },
    });
    expect(
      evaluateTerm(typed, expression(typed, "deterministic-set")),
    ).toEqual({
      status: "value",
      value: {
        tag: "set",
        items: [integerValue("1"), integerValue("2")],
      },
    });
  });

  it("evaluates Boolean connectives, conditionals, and both callable kinds", () => {
    const typed = typedCorpus();

    expect(
      evaluatePredicate(
        typed,
        expression(typed, "boolean-connectives"),
      ),
    ).toEqual({ status: "value", value: true });
    expect(evaluateTerm(typed, expression(typed, "conditional"))).toEqual({
      status: "value",
      value: { tag: "rational", numerator: "4", denominator: "1" },
    });
    expect(evaluateTerm(typed, expression(typed, "function-call"))).toEqual({
      status: "value",
      value: { tag: "rational", numerator: "3", denominator: "2" },
    });
    expect(
      evaluatePredicate(typed, expression(typed, "predicate-call")),
    ).toEqual({ status: "value", value: true });
  });

  it("evaluates deterministic folds without floating-point coercion", () => {
    const typed = typedCorpus();

    expect(evaluateTerm(typed, expression(typed, "fold-sum"))).toEqual({
      status: "value",
      value: { tag: "rational", numerator: "2", denominator: "1" },
    });
    expect(evaluateTerm(typed, expression(typed, "fold-count"))).toEqual({
      status: "value",
      value: { tag: "integer", value: "2" },
    });
  });

  it("quantifies only over the supplied named finite universe", () => {
    const typed = typedCorpus();
    const term = expression(typed, "finite-quantifier");

    expect(
      evaluatePredicate(typed, term, {
        variables: { threshold: rationalValue("0", "1") },
        universes: {
          "framework.items": [item("1"), item("2")],
        },
      }),
    ).toEqual({ status: "value", value: true });
    expect(
      evaluatePredicate(typed, term, {
        variables: { threshold: rationalValue("1", "1") },
        universes: {
          "framework.items": [item("1"), item("2")],
        },
      }),
    ).toEqual({ status: "value", value: false });
  });

  it("returns typed indeterminate data for absent variables and universes", () => {
    const typed = typedCorpus();

    expect(
      evaluateTerm(typed, expression(typed, "unbound-variable")),
    ).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_EVAL_UNBOUND_VARIABLE" },
    });
    expect(
      evaluateTerm(typed, expression(typed, "finite-quantifier"), {
        variables: { threshold: rationalValue("0", "1") },
      }),
    ).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_EVAL_UNBOUND_UNIVERSE" },
    });
    expect(
      evaluateTerm(typed, expression(typed, "finite-quantifier"), {
        variables: { threshold: rationalValue("0", "1") },
        universes: { "framework.items": [] },
      }),
    ).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_EVAL_EMPTY_UNIVERSE" },
    });
  });

  it("returns typed indeterminate data for invalid exact numerics", () => {
    const typed = typedCorpus();

    expect(
      evaluateTerm(typed, expression(typed, "division-by-zero")),
    ).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_EVAL_DIVISION_BY_ZERO" },
    });
    expect(
      evaluateTerm(typed, expression(typed, "invalid-integer")),
    ).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_EVAL_INVALID_NUMERIC" },
    });
  });

  it("is total at predicate and deterministic resource boundaries", () => {
    const typed = typedCorpus();

    expect(
      evaluatePredicate(typed, expression(typed, "exact-arithmetic")),
    ).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_EVAL_EXPECTED_BOOLEAN" },
    });
    expect(
      evaluateTerm(
        typed,
        expression(typed, "boolean-connectives"),
        {},
        { max_steps: 1 },
      ),
    ).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_EVAL_RESOURCE_LIMIT" },
    });
  });
});
