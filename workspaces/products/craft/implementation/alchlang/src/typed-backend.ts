import { CompilationRejected, type NormalizedCalculation, type NormalizedMapping, type NormalizedPolicy, type NormalizedQuery, type SfolFormula, type SfolUInt64Term } from "./model.js";
import { evaluateSfolFormula } from "./runtime.js";

const UINT64_MAX = (1n << 64n) - 1n;

function reject(code: string, path: string, message: string): never {
  throw new CompilationRejected([{ code, path, message }]);
}

function uint64(value: unknown, path: string): bigint {
  let result: bigint;
  try {
    if (typeof value === "bigint") result = value;
    else if (typeof value === "number" && Number.isSafeInteger(value)) result = BigInt(value);
    else if (typeof value === "string" && /^(0|[1-9]\d*)$/.test(value)) result = BigInt(value);
    else return reject("CALCULATION_INPUT_TYPE", path, "expected a UInt64 bigint, safe integer, or decimal string");
  } catch {
    return reject("CALCULATION_INPUT_TYPE", path, "expected a UInt64 value");
  }
  if (result < 0n || result > UINT64_MAX) reject("CALCULATION_RANGE", path, "value is outside UInt64");
  return result;
}

function calculationValue(expression: SfolUInt64Term, inputs: Readonly<Record<string, unknown>>, rounding: NormalizedCalculation["rounding"]): bigint {
  if ("node" in expression) {
    if (expression.node === "uint64_literal") return uint64(expression.value, "$.expression");
    if (!(expression.ref in inputs)) reject("MISSING_CALCULATION_INPUT", `$.inputs.${expression.ref}`, `${expression.ref} is required`);
    return uint64(inputs[expression.ref], `$.inputs.${expression.ref}`);
  }
  const left = calculationValue(expression.operands[0], inputs, rounding);
  const right = calculationValue(expression.operands[1], inputs, rounding);
  let result: bigint;
  switch (expression.operator) {
    case "add": result = left + right; break;
    case "subtract":
      if (right > left) reject("CALCULATION_UNDERFLOW", "$.expression", "UInt64 subtraction underflow");
      result = left - right; break;
    case "multiply": result = left * right; break;
    case "divide":
      if (right === 0n) reject("CALCULATION_DIVIDE_BY_ZERO", "$.expression", "division by zero");
      if (left % right !== 0n && rounding === "reject") reject("CALCULATION_INEXACT", "$.expression", "inexact division rejected by contract");
      result = left / right + (rounding === "ceil" && left % right !== 0n ? 1n : 0n); break;
  }
  if (result > UINT64_MAX) reject("CALCULATION_OVERFLOW", "$.expression", "UInt64 overflow");
  return result;
}

export function evaluateCalculation(contract: NormalizedCalculation, inputs: Readonly<Record<string, unknown>>): bigint {
  for (const input of contract.input_facts) if (!(input in inputs)) reject("MISSING_CALCULATION_INPUT", `$.inputs.${input}`, `${input} is required`);
  return calculationValue(contract.expression, inputs, contract.rounding);
}

function required(row: Readonly<Record<string, unknown>>, field: string, path: string): unknown {
  if (!(field in row)) reject("MISSING_TYPED_VALUE", path, `${field} is required`);
  return row[field];
}

export function evaluateQuery(contract: NormalizedQuery, rows: readonly Readonly<Record<string, unknown>>[], inputs: Readonly<Record<string, unknown>> = {}): ReadonlyArray<Readonly<Record<string, unknown>>> {
  for (const input of contract.input_facts) required(inputs, input, `$.inputs.${input}`);
  const predicateFields = (expression: SfolFormula | null): string[] => expression === null ? [] : "node" in expression ? expression.node === "fact_ref" ? [expression.ref] : [] : expression.operands.flatMap(predicateFields);
  const predicateRefs = predicateFields(contract.predicate);
  let selected = rows.filter((row) => { const facts = { ...inputs, ...row }; for (const ref of predicateRefs) required(facts, ref, `$.rows.${ref}`); return !contract.predicate || evaluateSfolFormula(contract.predicate, facts); });
  if (contract.order_by.length) selected = [...selected].sort((a, b) => {
    for (const order of contract.order_by) {
      const left = required(a, order.field_ref, `$.rows.${order.field_ref}`) as any;
      const right = required(b, order.field_ref, `$.rows.${order.field_ref}`) as any;
      if (left < right) return order.direction === "asc" ? -1 : 1;
      if (left > right) return order.direction === "asc" ? 1 : -1;
    }
    return 0;
  });
  if (contract.limit !== null) selected = selected.slice(0, contract.limit);
  return selected.map((row) => Object.fromEntries(contract.projection.map((field) => [field, required(row, field, `$.rows.${field}`)])));
}

export function evaluateMapping(contract: NormalizedMapping, source: Readonly<Record<string, unknown>>): Readonly<Record<string, unknown>> {
  const target: Record<string, unknown> = {};
  for (const clause of contract.clauses) {
    if (clause.source_field !== null && clause.source_field in source) target[clause.target_field] = source[clause.source_field];
    else if (clause.default_value !== null) target[clause.target_field] = clause.default_value.value;
    else if (contract.total) reject("MAPPING_REQUIRED_VALUE", `$.mapping.${clause.target_field}`, "total mapping could not produce target field");
  }
  return target;
}

export function evaluatePolicy(contract: NormalizedPolicy, inputs: Readonly<Record<string, unknown>>): string {
  for (const input of contract.input_facts) required(inputs, input, `$.inputs.${input}`);
  for (const item of contract.cases) if (evaluateSfolFormula(item.predicate, inputs)) return item.target_ref;
  return contract.default_target_ref;
}
