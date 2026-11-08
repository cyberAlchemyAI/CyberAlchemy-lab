import {
  fail,
  type BooleanEqualityNode,
  type JsonRecord,
} from "./types.js";

function record(value: unknown): JsonRecord | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonRecord)
    : null;
}

export function decodeBooleanEquality(value: unknown): BooleanEqualityNode {
  const ast = record(value);
  if (!ast) fail("PREDICATE_TYPE_INVALID", "predicate AST must be an object");
  if (ast.kind !== "eq") {
    fail("PREDICATE_OPERATOR_UNSUPPORTED", `unsupported predicate operator: ${String(ast.kind)}`);
  }
  const left = record(ast.left);
  const right = record(ast.right);
  if (
    !left ||
    left.kind !== "variable" ||
    left.name !== "has_key" ||
    left.value_type !== "boolean" ||
    !right ||
    right.kind !== "literal" ||
    right.value_type !== "boolean" ||
    typeof right.value !== "boolean"
  ) {
    fail(
      "PREDICATE_TYPE_INVALID",
      "EVF S1 admits only eq(variable has_key:boolean, literal:boolean)",
    );
  }
  return value as BooleanEqualityNode;
}

export function evaluateBooleanEquality(
  astValue: unknown,
  varsValue: unknown,
): boolean {
  const ast = decodeBooleanEquality(astValue);
  const vars = record(varsValue);
  if (!vars || Object.keys(vars).length !== 1 || typeof vars.has_key !== "boolean") {
    fail("FIXTURE_INPUT_INVALID", "fixture vars must contain only has_key:boolean");
  }
  return vars.has_key === ast.right.value;
}
