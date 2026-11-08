import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { CompilationRejected, compileCarrier, evaluateRule, parseDomainSource } from "../src/index.js";

const source = readFileSync(new URL("../examples/typed-backend.md", import.meta.url), "utf8");
const original = parseDomainSource(source).carrier;
const literal = (value_type: string, value: unknown) => ({ node: "literal", value_type, value });
function carrier(condition: unknown): any {
  const copy: any = structuredClone(original);
  copy.rules.push({ rule_id: "MembershipRule", owner_route: copy.owners[0].owner_route, condition, source_refs: ["test:membership"] });
  return copy;
}
function rejects(operator: string, operands: unknown[]): void {
  assert.throws(() => compileCarrier(carrier({ operator, operands })),
    (error: unknown) => error instanceof CompilationRejected && error.issues.some(issue =>
      issue.code === "TYPE_MISMATCH" && issue.path === "$.rules[0].condition"));
}

test("legacy Rule membership rejects non-container receivers before execution", () => {
  rejects("contains", [literal("integer", 7), literal("integer", 1)]);
  rejects("contains", [literal("boolean", true), literal("boolean", true)]);
  rejects("contains", [literal("string", "123"), literal("integer", 2)]);
  rejects("in", [literal("integer", 1), literal("integer", 7)]);
  rejects("in", [literal("string", "a"), literal("string", "abc")]);
  rejects("contains", [literal("list", 7), literal("integer", 1)]);
  rejects("in", [literal("integer", 1), literal("list", "123")]);
  rejects("contains", [literal("string", 123), literal("string", "2")]);
  rejects("contains", [literal("string", "123"), literal("string", 2)]);
});

test("legacy string containment and list membership preserve true and false results", () => {
  for (const [operator, operands, expected] of [
    ["contains", [literal("string", "abc"), literal("string", "b")], true],
    ["contains", [literal("string", "abc"), literal("string", "z")], false],
    ["contains", [literal("list", [1, 2]), literal("integer", 2)], true],
    ["contains", [literal("list", [1, 2]), literal("integer", 3)], false],
    ["in", [literal("integer", 2), literal("list", [1, 2])], true],
    ["in", [literal("integer", 3), literal("list", [1, 2])], false],
  ] as const) {
    const compiled = compileCarrier(carrier({ operator, operands }));
    assert.equal(evaluateRule(compiled.plan.model.rules[0]!, {}), expected);
  }
});

test("fact types participate in membership rejection and unknown operators fail closed", () => {
  const copy = carrier({ operator: "contains", operands: [{ node: "fact_ref", ref: "amount" }, literal("integer", 1)] });
  assert.throws(() => compileCarrier(copy), (error: unknown) => error instanceof CompilationRejected && error.issues.some(issue => issue.code === "TYPE_MISMATCH"));
  assert.throws(() => compileCarrier(carrier({ operator: "invented", operands: [literal("integer", 1), literal("integer", 2)] })),
    (error: unknown) => error instanceof CompilationRejected && error.issues.some(issue => issue.code === "UNKNOWN_OPERATOR"));
});
