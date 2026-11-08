import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { loadEvfS1Bundle } from "../minted-project/derive.js";
import {
  decodeBooleanEquality,
  evaluateBooleanEquality,
} from "../minted-project/typed-predicate.js";
import { EvfS1Error, type EvfFailureCode } from "../minted-project/types.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../../..", import.meta.url));

function expectEvfCode(action: () => unknown, code: EvfFailureCode): void {
  try {
    action();
  } catch (error) {
    expect(error).toBeInstanceOf(EvfS1Error);
    expect((error as EvfS1Error).code).toBe(code);
    return;
  }
  throw new Error(`expected EVF failure ${code}`);
}

describe("EVF S1 typed key-door predicate", () => {
  it("evaluates the admitted AST against fixture variables only", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const ast = decodeBooleanEquality(bundle.predicate.predicate.ast);

    expect(bundle.fixtures.cases.map((fixture) =>
      evaluateBooleanEquality(ast, fixture.vars),
    )).toEqual([true, false]);
  });

  it("rejects an unsupported predicate operator", () => {
    const ast = loadEvfS1Bundle(REPO_ROOT).predicate.predicate.ast;

    expectEvfCode(
      () => decodeBooleanEquality({ ...ast, kind: "ne" }),
      "PREDICATE_OPERATOR_UNSUPPORTED",
    );
  });

  it("rejects an AST outside the boolean equality grammar", () => {
    const ast = loadEvfS1Bundle(REPO_ROOT).predicate.predicate.ast;

    expectEvfCode(
      () => decodeBooleanEquality({
        ...ast,
        left: { ...ast.left, value_type: "string" },
      }),
      "PREDICATE_TYPE_INVALID",
    );
  });

  it("rejects fixture variables that carry an expected-value oracle", () => {
    const ast = loadEvfS1Bundle(REPO_ROOT).predicate.predicate.ast;

    expectEvfCode(
      () => evaluateBooleanEquality(ast, { has_key: true, expected: true }),
      "FIXTURE_INPUT_INVALID",
    );
  });
});
