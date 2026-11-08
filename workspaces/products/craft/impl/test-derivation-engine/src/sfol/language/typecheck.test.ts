import { describe, expect, it } from "vitest";

import type {
  LogicClause,
  LogicDeclaration,
  LogicTerm,
  NodeLogicModuleV1,
  SortRef,
} from "./ast.js";
import {
  type SfolTypeDiagnosticCode,
  typecheckLogicModule,
} from "./typecheck.js";

const SOURCE_ID = "framework.CheckLimit";
const boolSort = { tag: "primitive", name: "boolean" } as const;
const intSort = { tag: "primitive", name: "integer" } as const;
const rationalSort = { tag: "primitive", name: "rational" } as const;
const inputSort = {
  tag: "named",
  declaration_id: "framework.Input",
} as const;
const statusSort = {
  tag: "named",
  declaration_id: "framework.Status",
} as const;

function span(path: string) {
  return {
    source_id: SOURCE_ID,
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 10 },
  };
}

function literalInteger(value: string, path: string): LogicTerm {
  return {
    tag: "literal",
    value: { tag: "integer", value },
    span: span(path),
  };
}

function literalBoolean(value: boolean, path: string): LogicTerm {
  return {
    tag: "literal",
    value: { tag: "boolean", value },
    span: span(path),
  };
}

function clause(
  clauseId: string,
  expression: LogicTerm,
  resultSort: SortRef,
  kind: LogicClause["kind"] = "function",
  observationSort: SortRef | null = null,
): LogicClause {
  return {
    clause_id: clauseId,
    kind,
    status: "admitted",
    inputs: [],
    result_sort: resultSort,
    expression,
    observation_sort: observationSort,
    span: span(`body.logic.clauses.${clauseId}`),
  };
}

function moduleFixture(): NodeLogicModuleV1 {
  const declarations: readonly LogicDeclaration[] = [
    {
      tag: "enum",
      declaration_id: "framework.Status",
      members: ["READY", "BLOCKED"],
      span: span("body.logic.declarations.status"),
    },
    {
      tag: "record",
      declaration_id: "framework.Input",
      fields: [
        {
          name: "amount",
          sort: rationalSort,
          required: true,
          span: span("body.logic.declarations.input.amount"),
        },
        {
          name: "status",
          sort: statusSort,
          required: true,
          span: span("body.logic.declarations.input.status"),
        },
      ],
      span: span("body.logic.declarations.input"),
    },
    {
      tag: "fixture-universe",
      declaration_id: "framework.inputs",
      element_sort: inputSort,
      admits_empty: false,
      span: span("body.logic.declarations.inputs"),
    },
    {
      tag: "function",
      declaration_id: "framework.increment",
      parameters: [
        {
          name: "x",
          sort: intSort,
          span: span("body.logic.declarations.increment.x"),
        },
      ],
      result: rationalSort,
      body: {
        tag: "arithmetic",
        operator: "add",
        left: {
          tag: "variable",
          name: "x",
          span: span("body.logic.declarations.increment.body.x"),
        },
        right: literalInteger(
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
        {
          name: "x",
          sort: rationalSort,
          span: span("body.logic.declarations.is-positive.x"),
        },
      ],
      body: {
        tag: "comparison",
        operator: "gt",
        left: {
          tag: "variable",
          name: "x",
          span: span("body.logic.declarations.is-positive.body.x"),
        },
        right: literalInteger(
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
    declaration_id: "framework.Input",
    fields: [
      {
        name: "amount",
        value: literalInteger("2", "body.logic.terms.record.amount"),
      },
      {
        name: "status",
        value: {
          tag: "enum",
          declaration_id: "framework.Status",
          member: "READY",
          span: span("body.logic.terms.record.status"),
        },
      },
    ],
    span: span("body.logic.terms.record"),
  };

  return {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: "framework.check-limit-logic",
    source: {
      feature_id: "framework",
      node_id: SOURCE_ID,
      source_id: SOURCE_ID,
      source_path: "nodes/check-limit.yaml",
    },
    declarations,
    clauses: [
      clause("record", recordTerm, inputSort),
      clause(
        "field",
        {
          tag: "field",
          target: recordTerm,
          field: "amount",
          span: span("body.logic.terms.field"),
        },
        rationalSort,
      ),
      clause(
        "list",
        {
          tag: "list",
          items: [
            literalInteger("1", "body.logic.terms.list.one"),
            literalInteger("2", "body.logic.terms.list.two"),
          ],
          span: span("body.logic.terms.list"),
        },
        { tag: "list", element: intSort },
      ),
      clause(
        "set",
        {
          tag: "set",
          items: [literalInteger("1", "body.logic.terms.set.one")],
          span: span("body.logic.terms.set"),
        },
        { tag: "set", element: intSort },
      ),
      clause(
        "negate",
        {
          tag: "negate",
          operand: literalInteger("1", "body.logic.terms.negate.one"),
          span: span("body.logic.terms.negate"),
        },
        intSort,
      ),
      clause(
        "conditional",
        {
          tag: "conditional",
          condition: literalBoolean(
            true,
            "body.logic.terms.conditional.condition",
          ),
          when_true: literalInteger(
            "1",
            "body.logic.terms.conditional.true",
          ),
          when_false: {
            tag: "literal",
            value: { tag: "rational", numerator: "3", denominator: "2" },
            span: span("body.logic.terms.conditional.false"),
          },
          span: span("body.logic.terms.conditional"),
        },
        rationalSort,
      ),
      clause(
        "fold",
        {
          tag: "fold",
          operator: "sum",
          collection: {
            tag: "list",
            items: [
              {
                tag: "literal",
                value: { tag: "rational", numerator: "1", denominator: "2" },
                span: span("body.logic.terms.fold.item"),
              },
            ],
            span: span("body.logic.terms.fold.collection"),
          },
          item_name: "item",
          expression: {
            tag: "variable",
            name: "item",
            span: span("body.logic.terms.fold.expression"),
          },
          span: span("body.logic.terms.fold"),
        },
        rationalSort,
      ),
      clause(
        "quantifier",
        {
          tag: "quantifier",
          operator: "forall",
          universe_id: "framework.inputs",
          variable_name: "item",
          variable_sort: inputSort,
          predicate: {
            tag: "comparison",
            operator: "gte",
            left: {
              tag: "field",
              target: {
                tag: "variable",
                name: "item",
                span: span("body.logic.terms.quantifier.item"),
              },
              field: "amount",
              span: span("body.logic.terms.quantifier.amount"),
            },
            right: literalInteger(
              "0",
              "body.logic.terms.quantifier.zero",
            ),
            span: span("body.logic.terms.quantifier.predicate"),
          },
          span: span("body.logic.terms.quantifier"),
        },
        boolSort,
        "invariant",
      ),
      clause(
        "call",
        {
          tag: "call",
          declaration_id: "framework.increment",
          arguments: [literalInteger("4", "body.logic.terms.call.argument")],
          span: span("body.logic.terms.call"),
        },
        rationalSort,
      ),
      clause(
        "boolean",
        {
          tag: "boolean",
          operator: "and",
          operands: [
            literalBoolean(true, "body.logic.terms.boolean.left"),
            {
              tag: "not",
              operand: literalBoolean(
                false,
                "body.logic.terms.boolean.not.value",
              ),
              span: span("body.logic.terms.boolean.not"),
            },
          ],
          span: span("body.logic.terms.boolean"),
        },
        boolSort,
        "predicate",
      ),
      clause(
        "effect",
        literalBoolean(true, "body.logic.terms.effect"),
        boolSort,
        "effect-relation",
        inputSort,
      ),
    ],
  };
}

function expectFailure(
  module: NodeLogicModuleV1,
  code: SfolTypeDiagnosticCode,
  path: string,
): void {
  expect(typecheckLogicModule(module)).toEqual({
    ok: false,
    diagnostics: [
      expect.objectContaining({
        code,
        stage: "type",
        path,
      }),
    ],
  });
}

function mutableModule(): NodeLogicModuleV1 & {
  declarations: LogicDeclaration[];
  clauses: LogicClause[];
} {
  return structuredClone(moduleFixture()) as NodeLogicModuleV1 & {
    declarations: LogicDeclaration[];
    clauses: LogicClause[];
  };
}

describe("closed DS-SFOL v1 type resolution", () => {
  it("fully resolves all v1 term families with explicit rational coercions", () => {
    const result = typecheckLogicModule(moduleFixture());
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(new Set(result.value.term_judgments.map(({ term_tag }) => term_tag))).toEqual(
      new Set([
        "literal",
        "variable",
        "field",
        "record",
        "list",
        "set",
        "enum",
        "arithmetic",
        "negate",
        "comparison",
        "boolean",
        "not",
        "conditional",
        "fold",
        "quantifier",
        "call",
      ]),
    );
    expect(
      result.value.term_judgments.find(
        ({ path }) => path === "body.logic.terms.record.amount",
      ),
    ).toEqual(
      expect.objectContaining({
        inferred_sort: intSort,
        effective_sort: rationalSort,
        coercion: "integer-to-rational",
      }),
    );
    expect(result.value.environment).toEqual({
      named_sorts: ["framework.Input", "framework.Status"],
      callables: ["framework.increment", "framework.is-positive"],
      fixture_universes: ["framework.inputs"],
    });
    expect(Object.isFrozen(result.value)).toBe(true);
  });

  it("rejects unknown variables and fields", () => {
    const unknownVariable = mutableModule();
    unknownVariable.clauses = [
      clause(
        "unknown-variable",
        {
          tag: "variable",
          name: "missing",
          span: span("body.logic.fail.variable"),
        },
        intSort,
      ),
    ];
    expectFailure(
      unknownVariable,
      "SFOL_TYPE_UNKNOWN_VARIABLE",
      "body.logic.fail.variable",
    );

    const unknownField = mutableModule();
    const target = moduleFixture().clauses[0]?.expression;
    if (target !== undefined) {
      unknownField.clauses = [
        clause(
          "unknown-field",
          {
            tag: "field",
            target,
            field: "missing",
            span: span("body.logic.fail.field"),
          },
          intSort,
        ),
      ];
    }
    expectFailure(
      unknownField,
      "SFOL_TYPE_UNKNOWN_FIELD",
      "body.logic.fail.field",
    );
  });

  it("rejects unknown named domains and ambiguous empty collections", () => {
    const unknownSort = mutableModule();
    unknownSort.clauses[0] = {
      ...unknownSort.clauses[0]!,
      result_sort: { tag: "named", declaration_id: "framework.Missing" },
    };
    expectFailure(
      unknownSort,
      "SFOL_TYPE_UNKNOWN_NAMED_SORT",
      unknownSort.clauses[0]!.span.path,
    );

    const empty = mutableModule();
    empty.declarations.push({
      tag: "function",
      declaration_id: "framework.empty",
      parameters: [],
      result: { tag: "list", element: intSort },
      body: {
        tag: "list",
        items: [],
        span: span("body.logic.fail.empty"),
      },
      span: span("body.logic.declarations.empty"),
    });
    const result = typecheckLogicModule(empty);
    expect(result.ok).toBe(true);

    const ambiguous = mutableModule();
    ambiguous.declarations.push({
      tag: "predicate",
      declaration_id: "framework.ambiguous",
      parameters: [],
      body: {
        tag: "comparison",
        operator: "eq",
        left: {
          tag: "list",
          items: [],
          span: span("body.logic.fail.ambiguous"),
        },
        right: {
          tag: "list",
          items: [],
          span: span("body.logic.fail.ambiguous-right"),
        },
        span: span("body.logic.fail.ambiguous-comparison"),
      },
      span: span("body.logic.declarations.ambiguous"),
    });
    expectFailure(
      ambiguous,
      "SFOL_TYPE_AMBIGUOUS_COLLECTION",
      "body.logic.fail.ambiguous",
    );
  });

  it("rejects incompatible comparisons and non-Boolean predicates", () => {
    const mismatch = mutableModule();
    mismatch.declarations.push({
      tag: "predicate",
      declaration_id: "framework.bad-comparison",
      parameters: [],
      body: {
        tag: "comparison",
        operator: "lt",
        left: literalBoolean(true, "body.logic.fail.compare.left"),
        right: literalInteger("1", "body.logic.fail.compare.right"),
        span: span("body.logic.fail.compare"),
      },
      span: span("body.logic.declarations.bad-comparison"),
    });
    expectFailure(
      mismatch,
      "SFOL_TYPE_INCOMPATIBLE_COMPARISON",
      "body.logic.fail.compare",
    );
  });

  it("requires declared finite universes with exact element sorts", () => {
    const unknown = mutableModule();
    const quantifier = structuredClone(
      moduleFixture().clauses.find(({ clause_id }) => clause_id === "quantifier")!,
    );
    if (quantifier.expression.tag === "quantifier") {
      unknown.clauses = [
        {
          ...quantifier,
          expression: {
            ...quantifier.expression,
            universe_id: "framework.unbounded",
          },
        },
      ];
    }
    expectFailure(
      unknown,
      "SFOL_TYPE_UNKNOWN_UNIVERSE",
      "body.logic.terms.quantifier",
    );

    const mismatch = mutableModule();
    const wrong = structuredClone(quantifier);
    if (wrong.expression.tag === "quantifier") {
      mismatch.clauses = [
        {
          ...wrong,
          expression: {
            ...wrong.expression,
            universe_id: "framework.inputs",
            variable_sort: intSort,
          },
        },
      ];
    }
    expectFailure(
      mismatch,
      "SFOL_TYPE_UNIVERSE_MISMATCH",
      "body.logic.terms.quantifier",
    );
  });

  it("rejects invalid effect contracts", () => {
    const invalid = mutableModule();
    invalid.clauses = [
      clause(
        "effect-missing-observation",
        literalBoolean(true, "body.logic.fail.effect"),
        boolSort,
        "effect-relation",
        null,
      ),
    ];
    expectFailure(
      invalid,
      "SFOL_TYPE_INVALID_EFFECT_CONTRACT",
      invalid.clauses[0]!.span.path,
    );
  });

  it("rejects recursive callable cycles before execution", () => {
    const recursive = mutableModule();
    recursive.declarations.push({
      tag: "function",
      declaration_id: "framework.loop",
      parameters: [],
      result: intSort,
      body: {
        tag: "call",
        declaration_id: "framework.loop",
        arguments: [],
        span: span("body.logic.declarations.loop.call"),
      },
      span: span("body.logic.declarations.loop"),
    });
    expectFailure(
      recursive,
      "SFOL_TYPE_RECURSION_FORBIDDEN",
      "body.logic.declarations.loop",
    );
  });

  it("rejects call arity and argument mismatch independently", () => {
    const arity = mutableModule();
    arity.clauses = [
      clause(
        "arity",
        {
          tag: "call",
          declaration_id: "framework.increment",
          arguments: [],
          span: span("body.logic.fail.arity"),
        },
        rationalSort,
      ),
    ];
    expectFailure(arity, "SFOL_TYPE_CALL_ARITY", "body.logic.fail.arity");

    const argument = mutableModule();
    argument.clauses = [
      clause(
        "argument",
        {
          tag: "call",
          declaration_id: "framework.increment",
          arguments: [
            literalBoolean(true, "body.logic.fail.argument.value"),
          ],
          span: span("body.logic.fail.argument"),
        },
        rationalSort,
      ),
    ];
    expectFailure(
      argument,
      "SFOL_TYPE_MISMATCH",
      "body.logic.fail.argument.value",
    );
  });
});
