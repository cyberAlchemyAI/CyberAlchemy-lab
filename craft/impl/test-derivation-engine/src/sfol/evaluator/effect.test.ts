import { describe, expect, it } from "vitest";

import type {
  LogicClause,
  LogicDeclaration,
  LogicTerm,
  NodeLogicModuleV1,
  SortRef,
} from "../language/ast.js";
import {
  type TypedLogicModule,
  typecheckLogicModule,
} from "../language/typecheck.js";
import {
  EFFECT_TRACE_CONTRACT_VERSION,
  EFFECT_TRACE_VERSION,
  validateEffectTrace,
  type EffectTraceContract,
  type ValidatedEffectTrace,
} from "../runners/effect/contracts.js";
import { evaluateEffectRelation } from "./effect.js";
import { evaluateTerm, integerValue } from "./index.js";

const SOURCE_ID = "framework.IncrementEffect";
const boolSort = { tag: "primitive", name: "boolean" } as const;
const intSort = { tag: "primitive", name: "integer" } as const;
const stringSort = { tag: "primitive", name: "string" } as const;
const stateSort = {
  tag: "named",
  declaration_id: "framework.State",
} as const;
const effectSort = {
  tag: "named",
  declaration_id: "framework.Effect",
} as const;
const effectsSort = { tag: "list", element: effectSort } as const;

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

function string(value: string, path: string): LogicTerm {
  return {
    tag: "literal",
    value: { tag: "string", value },
    span: span(path),
  };
}

function variable(name: string, path: string): LogicTerm {
  return { tag: "variable", name, span: span(path) };
}

function field(
  target: LogicTerm,
  name: string,
  path: string,
): LogicTerm {
  return { tag: "field", target, field: name, span: span(path) };
}

function effectRecord(
  sequence: number,
  kind: string,
  name: string,
  payload: string,
): LogicTerm {
  const root = `body.logic.expected-effects.${sequence}`;
  return {
    tag: "record",
    declaration_id: "framework.Effect",
    fields: [
      {
        name: "sequence",
        value: integer(sequence.toString(), `${root}.sequence`),
      },
      { name: "kind", value: string(kind, `${root}.kind`) },
      { name: "name", value: string(name, `${root}.name`) },
      {
        name: "payload",
        value: string(payload, `${root}.payload`),
      },
    ],
    span: span(root),
  };
}

function moduleFixture(): NodeLogicModuleV1 {
  const declarations: readonly LogicDeclaration[] = [
    {
      tag: "record",
      declaration_id: "framework.State",
      fields: [
        {
          name: "balance",
          sort: intSort,
          required: true,
          span: span("body.logic.declarations.state.balance"),
        },
      ],
      span: span("body.logic.declarations.state"),
    },
    {
      tag: "record",
      declaration_id: "framework.Effect",
      fields: [
        {
          name: "sequence",
          sort: intSort,
          required: true,
          span: span("body.logic.declarations.effect.sequence"),
        },
        {
          name: "kind",
          sort: stringSort,
          required: true,
          span: span("body.logic.declarations.effect.kind"),
        },
        {
          name: "name",
          sort: stringSort,
          required: true,
          span: span("body.logic.declarations.effect.name"),
        },
        {
          name: "payload",
          sort: stringSort,
          required: true,
          span: span("body.logic.declarations.effect.payload"),
        },
      ],
      span: span("body.logic.declarations.effect"),
    },
  ];

  const clause: LogicClause = {
    clause_id: "framework.increment-effect",
    kind: "effect-relation",
    status: "admitted",
    inputs: [
      { name: "pre", sort: stateSort, span: span("body.logic.inputs.pre") },
      {
        name: "post",
        sort: stateSort,
        span: span("body.logic.inputs.post"),
      },
      {
        name: "effects",
        sort: effectsSort,
        span: span("body.logic.inputs.effects"),
      },
    ],
    result_sort: boolSort,
    expression: {
      tag: "boolean",
      operator: "and",
      operands: [
        {
          tag: "comparison",
          operator: "eq",
          left: field(
            variable("post", "body.logic.relation.post"),
            "balance",
            "body.logic.relation.post.balance",
          ),
          right: {
            tag: "arithmetic",
            operator: "add",
            left: field(
              variable("pre", "body.logic.relation.pre"),
              "balance",
              "body.logic.relation.pre.balance",
            ),
            right: integer("1", "body.logic.relation.one"),
            span: span("body.logic.relation.increment"),
          },
          span: span("body.logic.relation.state"),
        },
        {
          tag: "comparison",
          operator: "eq",
          left: variable("effects", "body.logic.relation.effects"),
          right: {
            tag: "list",
            items: [
              effectRecord(0, "call", "authorize", "ok"),
              effectRecord(1, "write", "balance", "1"),
              effectRecord(2, "event", "incremented", "1"),
              effectRecord(3, "error", "none", "none"),
            ],
            span: span("body.logic.expected-effects"),
          },
          span: span("body.logic.relation.effect-order"),
        },
      ],
      span: span("body.logic.relation"),
    },
    observation_sort: effectsSort,
    span: span("body.logic.clauses.increment-effect"),
  };
  return {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: "framework.increment-effect-module",
    source: {
      feature_id: "framework",
      node_id: SOURCE_ID,
      source_id: SOURCE_ID,
      source_path: "nodes/increment-effect.yaml",
    },
    declarations,
    clauses: [clause],
  };
}

function typedFixture(): TypedLogicModule {
  const result = typecheckLogicModule(moduleFixture());
  if (!result.ok) {
    throw new Error(JSON.stringify(result.diagnostics));
  }
  return result.value;
}

function contractFixture(): EffectTraceContract {
  return {
    schema_version: EFFECT_TRACE_CONTRACT_VERSION,
    contract_id: "framework.increment-effect-contract",
    pre_record_declaration_id: "framework.State",
    post_record_declaration_id: "framework.State",
    effect_record_declaration_id: "framework.Effect",
    pre_fields: [{ name: "balance", value_tag: "integer" }],
    post_fields: [{ name: "balance", value_tag: "integer" }],
    effect_sequence: [
      { kind: "call", name: "authorize", payload_tag: "string" },
      { kind: "write", name: "balance", payload_tag: "string" },
      { kind: "event", name: "incremented", payload_tag: "string" },
      { kind: "error", name: "none", payload_tag: "string" },
    ],
    return_observation: null,
    max_effects: 4,
  };
}

function rawTrace(postBalance = "1") {
  return {
    schema_version: EFFECT_TRACE_VERSION,
    trace_id: "trace-001",
    contract_id: "framework.increment-effect-contract",
    pre_state: { balance: integerValue("0") },
    post_state: { balance: integerValue(postBalance) },
    effects: [
      {
        sequence: 0,
        kind: "call",
        name: "authorize",
        payload: { tag: "string", value: "ok" },
      },
      {
        sequence: 1,
        kind: "write",
        name: "balance",
        payload: { tag: "string", value: "1" },
      },
      {
        sequence: 2,
        kind: "event",
        name: "incremented",
        payload: { tag: "string", value: "1" },
      },
      {
        sequence: 3,
        kind: "error",
        name: "none",
        payload: { tag: "string", value: "none" },
      },
    ],
    return_value: null,
  };
}

function validatedTrace(postBalance = "1"): ValidatedEffectTrace {
  const result = validateEffectTrace(
    contractFixture(),
    rawTrace(postBalance),
  );
  if (!result.ok) {
    throw new Error(JSON.stringify(result.diagnostics));
  }
  return result.value;
}

describe("DS-SFOL finite effect trace algebra", () => {
  it("validates and freezes one complete deterministic effect trace", () => {
    const left = validatedTrace();
    const right = validatedTrace();

    expect(left.trace_digest).toBe(right.trace_digest);
    expect(left.effects.map((effect) => effect.kind)).toEqual([
      "call",
      "write",
      "event",
      "error",
    ]);
    expect(Object.isFrozen(left)).toBe(true);
    expect(Object.isFrozen(left.effects)).toBe(true);
  });

  it("evaluates an order-sensitive source relation over pre/post/effects", () => {
    const evaluation = evaluateEffectRelation(
      typedFixture(),
      "framework.increment-effect",
      contractFixture(),
      validatedTrace(),
    );

    expect(evaluation).toMatchObject({
      status: "pass",
      detail: "effect trace satisfies the source relation",
    });
  });

  it("rejects missing and extra observations", () => {
    const missing = rawTrace();
    missing.effects = missing.effects.slice(0, 3);
    expect(
      validateEffectTrace(contractFixture(), missing),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_MISSING_OBSERVATION" }],
    });

    const extra = rawTrace();
    extra.effects = [
      ...extra.effects,
      {
        sequence: 4,
        kind: "event",
        name: "undeclared",
        payload: { tag: "string", value: "extra" },
      },
    ];
    expect(validateEffectTrace(contractFixture(), extra)).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_RESOURCE_LIMIT" }],
    });
  });

  it("rejects reordered and duplicate sequence positions", () => {
    const reordered = rawTrace();
    const first = reordered.effects[0];
    const second = reordered.effects[1];
    if (first === undefined || second === undefined) {
      throw new Error("missing effect fixtures");
    }
    reordered.effects = [
      { ...second, sequence: 0 },
      { ...first, sequence: 1 },
      ...reordered.effects.slice(2),
    ];
    expect(
      validateEffectTrace(contractFixture(), reordered),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_ORDER_MISMATCH" }],
    });

    const duplicated = rawTrace();
    duplicated.effects[1] = { ...duplicated.effects[1]!, sequence: 0 };
    expect(
      validateEffectTrace(contractFixture(), duplicated),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_DUPLICATE_SEQUENCE" }],
    });
  });

  it("rejects wrong state and payload semantic types", () => {
    const wrongState: { pre_state: Record<string, unknown> } = rawTrace();
    wrongState.pre_state = {
      balance: { tag: "string", value: "zero" },
    };
    expect(
      validateEffectTrace(contractFixture(), wrongState),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_WRONG_TYPE" }],
    });

    const wrongPayload = rawTrace();
    wrongPayload.effects[0] = {
      ...wrongPayload.effects[0]!,
      payload: integerValue("1"),
    };
    expect(
      validateEffectTrace(contractFixture(), wrongPayload),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_WRONG_TYPE" }],
    });
  });

  it("rejects undeclared effect names and state projections", () => {
    const wrongName = rawTrace();
    wrongName.effects[2] = {
      ...wrongName.effects[2]!,
      name: "different-event",
    };
    expect(
      validateEffectTrace(contractFixture(), wrongName),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_ORDER_MISMATCH" }],
    });

    const extraState = {
      ...rawTrace(),
      post_state: {
        balance: integerValue("1"),
        hidden: integerValue("9"),
      },
    };
    expect(
      validateEffectTrace(contractFixture(), extraState),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_EXTRA_OBSERVATION" }],
    });
  });

  it("reports a complete but relation-violating trace as fail", () => {
    expect(
      evaluateEffectRelation(
        typedFixture(),
        "framework.increment-effect",
        contractFixture(),
        validatedTrace("2"),
      ),
    ).toMatchObject({
      status: "fail",
      detail: "effect trace violates the source relation",
    });
  });

  it("keeps invalid relations indeterminate without changing pure evaluation", () => {
    const typed = typedFixture();
    expect(
      evaluateEffectRelation(
        typed,
        "missing-clause",
        contractFixture(),
        validatedTrace(),
      ),
    ).toMatchObject({
      status: "indeterminate",
      detail: "effect relation clause is absent",
    });
    expect(
      evaluateTerm(
        typed,
        integer("7", "body.logic.pure-regression"),
      ),
    ).toEqual({
      status: "value",
      value: { tag: "integer", value: "7" },
    });
  });
});
