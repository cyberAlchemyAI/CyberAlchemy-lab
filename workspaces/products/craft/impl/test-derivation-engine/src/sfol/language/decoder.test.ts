import { describe, expect, it } from "vitest";

import type { LogicTermTag, NodeLogicModuleV1 } from "./ast.js";
import { canonicalJson } from "./contracts.js";
import {
  decodeNodeLogicModule,
  type SfolDecodeDiagnosticCode,
} from "./decoder.js";
import { DS_SFOL_V1_PROFILE } from "./profiles.js";

type MutableRecord = Record<string, unknown>;

const SOURCE_ID = "framework.CheckLimit";

function span(path: string) {
  return {
    source_id: SOURCE_ID,
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 10 },
  };
}

function integer(value = "1", path = "body.logic.term") {
  return {
    tag: "literal",
    value: { tag: "integer", value },
    span: span(path),
  };
}

function terms(): readonly MutableRecord[] {
  const variable = {
    tag: "variable",
    name: "x",
    span: span("body.logic.term.variable"),
  };
  return [
    integer(),
    variable,
    {
      tag: "field",
      target: variable,
      field: "value",
      span: span("body.logic.term.field"),
    },
    {
      tag: "record",
      declaration_id: "framework.Input",
      fields: [{ name: "value", value: integer() }],
      span: span("body.logic.term.record"),
    },
    {
      tag: "list",
      items: [integer()],
      span: span("body.logic.term.list"),
    },
    {
      tag: "set",
      items: [integer()],
      span: span("body.logic.term.set"),
    },
    {
      tag: "enum",
      declaration_id: "framework.Status",
      member: "READY",
      span: span("body.logic.term.enum"),
    },
    {
      tag: "arithmetic",
      operator: "add",
      left: integer(),
      right: integer(),
      span: span("body.logic.term.arithmetic"),
    },
    {
      tag: "negate",
      operand: integer(),
      span: span("body.logic.term.negate"),
    },
    {
      tag: "comparison",
      operator: "eq",
      left: integer(),
      right: integer(),
      span: span("body.logic.term.comparison"),
    },
    {
      tag: "boolean",
      operator: "and",
      operands: [
        {
          tag: "literal",
          value: { tag: "boolean", value: true },
          span: span("body.logic.term.boolean.literal"),
        },
      ],
      span: span("body.logic.term.boolean"),
    },
    {
      tag: "not",
      operand: {
        tag: "literal",
        value: { tag: "boolean", value: false },
        span: span("body.logic.term.not.literal"),
      },
      span: span("body.logic.term.not"),
    },
    {
      tag: "conditional",
      condition: {
        tag: "literal",
        value: { tag: "boolean", value: true },
        span: span("body.logic.term.conditional.condition"),
      },
      when_true: integer("1"),
      when_false: integer("0"),
      span: span("body.logic.term.conditional"),
    },
    {
      tag: "fold",
      operator: "sum",
      collection: {
        tag: "list",
        items: [integer()],
        span: span("body.logic.term.fold.collection"),
      },
      item_name: "item",
      expression: variable,
      span: span("body.logic.term.fold"),
    },
    {
      tag: "quantifier",
      operator: "forall",
      universe_id: "framework.inputs",
      variable_name: "item",
      variable_sort: { tag: "primitive", name: "integer" },
      predicate: {
        tag: "literal",
        value: { tag: "boolean", value: true },
        span: span("body.logic.term.quantifier.predicate"),
      },
      span: span("body.logic.term.quantifier"),
    },
    {
      tag: "call",
      declaration_id: "framework.is-valid",
      arguments: [integer()],
      span: span("body.logic.term.call"),
    },
  ];
}

function moduleFixture(): MutableRecord {
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
    declarations: [
      {
        tag: "record",
        declaration_id: "framework.Input",
        fields: [
          {
            name: "value",
            sort: { tag: "primitive", name: "integer" },
            required: true,
            span: span("body.logic.declarations.input.fields.value"),
          },
        ],
        span: span("body.logic.declarations.input"),
      },
      {
        tag: "enum",
        declaration_id: "framework.Status",
        members: ["READY", "BLOCKED"],
        span: span("body.logic.declarations.status"),
      },
      {
        tag: "function",
        declaration_id: "framework.next",
        parameters: [
          {
            name: "x",
            sort: { tag: "primitive", name: "integer" },
            span: span("body.logic.declarations.next.parameters.x"),
          },
        ],
        result: { tag: "primitive", name: "integer" },
        body: integer("1", "body.logic.declarations.next.body"),
        span: span("body.logic.declarations.next"),
      },
      {
        tag: "predicate",
        declaration_id: "framework.is-valid",
        parameters: [],
        body: {
          tag: "literal",
          value: { tag: "boolean", value: true },
          span: span("body.logic.declarations.is-valid.body"),
        },
        span: span("body.logic.declarations.is-valid"),
      },
      {
        tag: "fixture-universe",
        declaration_id: "framework.inputs",
        element_sort: { tag: "named", declaration_id: "framework.Input" },
        admits_empty: false,
        span: span("body.logic.declarations.inputs"),
      },
    ],
    clauses: terms().map((expression, index) => ({
      clause_id: `framework.term-${String(index).padStart(2, "0")}`,
      kind: "invariant",
      status: "admitted",
      inputs: [],
      result_sort: { tag: "primitive", name: "boolean" },
      expression,
      observation_sort: null,
      span: span(`body.logic.clauses[${index}]`),
    })),
  };
}

function expectFailure(
  input: unknown,
  code: SfolDecodeDiagnosticCode,
  path: string,
): void {
  expect(decodeNodeLogicModule(input)).toEqual({
    ok: false,
    diagnostics: [
      expect.objectContaining({
        code,
        stage: "decode",
        path,
      }),
    ],
  });
}

describe("structured DS-SFOL v1 decoder", () => {
  it("decodes every registered v1 term and declaration tag", () => {
    const result = decodeNodeLogicModule(moduleFixture());
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(
      result.value.clauses.map(({ expression }) => expression.tag),
    ).toEqual(DS_SFOL_V1_PROFILE.term_tags);
    expect(result.value.declarations.map(({ tag }) => tag).sort()).toEqual(
      [...DS_SFOL_V1_PROFILE.declaration_tags].sort(),
    );
    expect(Object.isFrozen(result.value)).toBe(true);
    expect(Object.isFrozen(result.value.clauses)).toBe(true);
  });

  it("normalizes declaration and clause order independently of object-key order", () => {
    const first = moduleFixture();
    const second = moduleFixture();
    second.declarations = [...(second.declarations as unknown[])].reverse();
    second.clauses = [...(second.clauses as unknown[])].reverse();
    const reordered = Object.fromEntries(Object.entries(second).reverse());

    const left = decodeNodeLogicModule(first);
    const right = decodeNodeLogicModule(reordered);
    expect(left.ok).toBe(true);
    expect(right.ok).toBe(true);
    if (!left.ok || !right.ok) return;

    expect(right.value).toEqual(left.value);
    expect(canonicalJson(right.value)).toBe(canonicalJson(left.value));
  });

  it("fails closed for prose, unknown versions, fields, and tags", () => {
    expectFailure(
      "forall x: business prose",
      "SFOL_DECODE_STRUCTURED_INPUT_REQUIRED",
      "$",
    );

    const badSchema = moduleFixture();
    badSchema.schema_version = "domainspec-node-logic/v2";
    expectFailure(
      badSchema,
      "SFOL_DECODE_UNKNOWN_SCHEMA_VERSION",
      "$.schema_version",
    );

    const badLanguage = moduleFixture();
    badLanguage.language_version = "domainspec-sfol/v2";
    expectFailure(
      badLanguage,
      "SFOL_DECODE_UNKNOWN_LANGUAGE_VERSION",
      "$.language_version",
    );

    const unknownField = moduleFixture();
    unknownField.oracle = "implementation";
    expectFailure(
      unknownField,
      "SFOL_DECODE_UNKNOWN_FIELD",
      "$.oracle",
    );

    const unknownTag = moduleFixture();
    const clause = (unknownTag.clauses as MutableRecord[])[0];
    if (clause !== undefined) {
      clause.expression = {
        tag: "lambda",
        span: span("body.logic.clauses[0].expression"),
      };
    }
    expectFailure(
      unknownTag,
      "SFOL_DECODE_UNKNOWN_TAG",
      "$.clauses[0].expression.tag",
    );
  });

  it("rejects duplicate identities without returning a partial module", () => {
    const duplicateDeclaration = moduleFixture();
    const declarations =
      duplicateDeclaration.declarations as MutableRecord[];
    const firstDeclaration = declarations[0];
    if (firstDeclaration !== undefined) {
      declarations.push(structuredClone(firstDeclaration));
    }
    const result = decodeNodeLogicModule(duplicateDeclaration);
    expect(result).toEqual({
      ok: false,
      diagnostics: [
        expect.objectContaining({
          code: "SFOL_DECODE_DUPLICATE_ID",
          path: "$.declarations[5]",
        }),
      ],
    });
    expect("value" in result).toBe(false);

    const duplicateClause = moduleFixture();
    const clauses = duplicateClause.clauses as MutableRecord[];
    const firstClause = clauses[0];
    if (firstClause !== undefined) {
      clauses.push(structuredClone(firstClause));
    }
    expectFailure(
      duplicateClause,
      "SFOL_DECODE_DUPLICATE_ID",
      "$.clauses[16]",
    );
  });

  it("preserves node-local source identity and rejects source/path drift", () => {
    const valid = decodeNodeLogicModule(moduleFixture());
    expect(valid.ok).toBe(true);
    if (valid.ok) {
      expect(valid.value.source).toEqual({
        feature_id: "framework",
        node_id: SOURCE_ID,
        source_id: SOURCE_ID,
        source_path: "nodes/check-limit.yaml",
      });
      expect(valid.value.clauses[0]?.span.path).toBe(
        "body.logic.clauses[0]",
      );
    }

    const wrongSource = moduleFixture();
    const wrongClause = (wrongSource.clauses as MutableRecord[])[0];
    if (wrongClause !== undefined) {
      const expression = wrongClause.expression as MutableRecord;
      const sourceSpan = expression.span as MutableRecord;
      sourceSpan.source_id = "other.Node";
    }
    expectFailure(
      wrongSource,
      "SFOL_DECODE_SOURCE_ID_MISMATCH",
      "$.clauses[0].expression.span.source_id",
    );

    const escapingSource = moduleFixture();
    (escapingSource.source as MutableRecord).source_path =
      "../external/node.yaml";
    expectFailure(
      escapingSource,
      "SFOL_DECODE_INVALID_SOURCE_PATH",
      "$.source.source_path",
    );
  });

  it("rejects malformed exact values and missing required fields deterministically", () => {
    const badRational = moduleFixture();
    const clause = (badRational.clauses as MutableRecord[])[0];
    if (clause !== undefined) {
      clause.expression = {
        tag: "literal",
        value: { tag: "rational", numerator: "1", denominator: "0" },
        span: span("body.logic.clauses[0].expression"),
      };
    }
    expectFailure(
      badRational,
      "SFOL_DECODE_INVALID_LITERAL",
      "$.clauses[0].expression.value",
    );

    const missing = moduleFixture();
    delete missing.module_id;
    expectFailure(missing, "SFOL_DECODE_MISSING_FIELD", "$.module_id");
  });
});

const _compileTimeModuleCheck: NodeLogicModuleV1 | null = null;
const _compileTimeTagCheck: LogicTermTag | null = null;
void _compileTimeModuleCheck;
void _compileTimeTagCheck;
