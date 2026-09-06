import { describe, expect, it } from "vitest";

import {
  DS_SFOL_LANGUAGE_VERSION,
  NODE_LOGIC_SCHEMA_VERSION,
  type LogicTerm,
  type NodeLogicModuleV1,
  type SourceSpan,
} from "./ast.js";
import {
  canonicalJson,
  logicTermTag,
  SfolLanguageContractError,
} from "./contracts.js";
import {
  DS_SFOL_PROFILE_REGISTRY,
  DS_SFOL_V1_PROFILE,
  resolveSfolLanguageProfile,
} from "./profiles.js";

const SPAN: SourceSpan = {
  source_id: "framework.CheckLimit",
  path: "body.logic.clauses[0]",
  start: { line: 1, column: 1 },
  end: { line: 1, column: 10 },
};

const literal: LogicTerm = {
  tag: "literal",
  value: { tag: "integer", value: "1" },
  span: SPAN,
};

function representativeTerms(): readonly LogicTerm[] {
  const variable: LogicTerm = { tag: "variable", name: "x", span: SPAN };
  return [
    literal,
    variable,
    { tag: "field", target: variable, field: "value", span: SPAN },
    {
      tag: "record",
      declaration_id: "framework.Input",
      fields: [{ name: "value", value: literal }],
      span: SPAN,
    },
    { tag: "list", items: [literal], span: SPAN },
    { tag: "set", items: [literal], span: SPAN },
    {
      tag: "enum",
      declaration_id: "framework.Status",
      member: "READY",
      span: SPAN,
    },
    {
      tag: "arithmetic",
      operator: "add",
      left: literal,
      right: literal,
      span: SPAN,
    },
    { tag: "negate", operand: literal, span: SPAN },
    {
      tag: "comparison",
      operator: "eq",
      left: literal,
      right: literal,
      span: SPAN,
    },
    {
      tag: "boolean",
      operator: "and",
      operands: [
        {
          tag: "literal",
          value: { tag: "boolean", value: true },
          span: SPAN,
        },
      ],
      span: SPAN,
    },
    { tag: "not", operand: literal, span: SPAN },
    {
      tag: "conditional",
      condition: literal,
      when_true: literal,
      when_false: literal,
      span: SPAN,
    },
    {
      tag: "fold",
      operator: "sum",
      collection: { tag: "list", items: [literal], span: SPAN },
      item_name: "item",
      expression: variable,
      span: SPAN,
    },
    {
      tag: "quantifier",
      operator: "forall",
      universe_id: "framework.inputs",
      variable_name: "item",
      variable_sort: { tag: "primitive", name: "integer" },
      predicate: literal,
      span: SPAN,
    },
    {
      tag: "call",
      declaration_id: "framework.is-valid",
      arguments: [literal],
      span: SPAN,
    },
  ];
}

function moduleFixture(): NodeLogicModuleV1 {
  return {
    schema_version: NODE_LOGIC_SCHEMA_VERSION,
    language_version: DS_SFOL_LANGUAGE_VERSION,
    module_id: "framework.check-limit-logic",
    source: {
      feature_id: "framework",
      node_id: "framework.CheckLimit",
      source_id: "framework.CheckLimit",
      source_path: "nodes/check-limit.yaml",
    },
    declarations: [],
    clauses: [
      {
        clause_id: "framework.limit-holds",
        kind: "invariant",
        status: "admitted",
        inputs: [],
        result_sort: { tag: "primitive", name: "boolean" },
        expression: {
          tag: "literal",
          value: { tag: "boolean", value: true },
          span: SPAN,
        },
        observation_sort: null,
        span: SPAN,
      },
    ],
  };
}

describe("DS-SFOL v1 language contracts", () => {
  it("closes the registered term-tag set through an exhaustive switch", () => {
    expect(representativeTerms().map(logicTermTag)).toEqual(
      DS_SFOL_V1_PROFILE.term_tags,
    );
  });

  it("rejects an unknown runtime term tag with a typed diagnostic", () => {
    const unknownTerm = {
      tag: "lambda",
      span: SPAN,
    } as unknown as LogicTerm;

    expect(() => logicTermTag(unknownTerm)).toThrowError(
      expect.objectContaining<Partial<SfolLanguageContractError>>({
        diagnostic: expect.objectContaining({
          code: "SFOL_LANGUAGE_UNKNOWN_TAG",
          path: "$.tag",
        }),
      }),
    );
  });

  it("resolves only the explicit v1 profile and fails closed on versions", () => {
    expect(resolveSfolLanguageProfile(DS_SFOL_LANGUAGE_VERSION)).toEqual({
      ok: true,
      value: DS_SFOL_V1_PROFILE,
    });
    expect(resolveSfolLanguageProfile("domainspec-sfol/v2")).toEqual({
      ok: false,
      diagnostics: [
        {
          code: "SFOL_LANGUAGE_UNKNOWN_VERSION",
          stage: "contract",
          path: "$.language_version",
          detail:
            "unsupported DS-SFOL language version domainspec-sfol/v2",
        },
      ],
    });
    expect(Object.keys(DS_SFOL_PROFILE_REGISTRY)).toEqual([
      DS_SFOL_LANGUAGE_VERSION,
    ]);
  });

  it("serializes one representative module deterministically with source identity", () => {
    const first = moduleFixture();
    const reordered = {
      clauses: first.clauses,
      declarations: first.declarations,
      source: first.source,
      module_id: first.module_id,
      language_version: first.language_version,
      schema_version: first.schema_version,
    };
    const serialized = canonicalJson(first);

    expect(canonicalJson(reordered)).toBe(serialized);
    expect(serialized).toContain(
      '"source_id":"framework.CheckLimit","source_path":"nodes/check-limit.yaml"',
    );
    expect(serialized).toBe(
      '{"clauses":[{"clause_id":"framework.limit-holds","expression":{"span":{"end":{"column":10,"line":1},"path":"body.logic.clauses[0]","source_id":"framework.CheckLimit","start":{"column":1,"line":1}},"tag":"literal","value":{"tag":"boolean","value":true}},"inputs":[],"kind":"invariant","observation_sort":null,"result_sort":{"name":"boolean","tag":"primitive"},"span":{"end":{"column":10,"line":1},"path":"body.logic.clauses[0]","source_id":"framework.CheckLimit","start":{"column":1,"line":1}},"status":"admitted"}],"declarations":[],"language_version":"domainspec-sfol/v1","module_id":"framework.check-limit-logic","schema_version":"domainspec-node-logic/v1","source":{"feature_id":"framework","node_id":"framework.CheckLimit","source_id":"framework.CheckLimit","source_path":"nodes/check-limit.yaml"}}',
    );
  });

  it("rejects non-JSON and cyclic values instead of producing unstable bytes", () => {
    expect(() => canonicalJson({ bad: undefined })).toThrowError(
      expect.objectContaining<Partial<SfolLanguageContractError>>({
        diagnostic: expect.objectContaining({
          code: "SFOL_LANGUAGE_NON_JSON_VALUE",
          path: "$.bad",
        }),
      }),
    );

    const cycle: { self?: unknown } = {};
    cycle.self = cycle;
    expect(() => canonicalJson(cycle)).toThrowError(
      expect.objectContaining<Partial<SfolLanguageContractError>>({
        diagnostic: expect.objectContaining({
          code: "SFOL_LANGUAGE_CYCLIC_VALUE",
          path: "$.self",
        }),
      }),
    );
  });
});
