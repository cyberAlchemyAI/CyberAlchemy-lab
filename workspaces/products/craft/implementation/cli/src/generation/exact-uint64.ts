import type { GeneratorInput } from "./contracts.js";
import { canonicalJson } from "../input/source-manifest.js";

export const EXACT_UINT64_PROFILE = "domainspec.typescript-exact-uint64/v1" as const;
export type RealizationProfile = typeof EXACT_UINT64_PROFILE;
export function validateRealizationProfile(value: unknown, language: string): RealizationProfile | undefined {
  if (value === undefined) return undefined;
  if (value !== EXACT_UINT64_PROFILE || language !== "typescript") throw new Error("MTCLI_REALIZATION_PROFILE: unsupported profile or language");
  return value;
}

const runtime = `
function required(record: Readonly<Record<string, unknown>>, name: string): any {
  const descriptor = Object.getOwnPropertyDescriptor(record, name);
  if (!descriptor || !("value" in descriptor)) throw new Error("MISSING_TYPED_VALUE:" + name);
  return descriptor.value;
}
function uint64(value: unknown): bigint {
  let result: bigint;
  if (typeof value === "bigint") result = value;
  else if (typeof value === "number" && Number.isSafeInteger(value)) result = BigInt(value);
  else if (typeof value === "string" && /^(0|[1-9][0-9]*)$/.test(value)) result = BigInt(value);
  else throw new Error("CALCULATION_INPUT_TYPE");
  if (result < 0n || result > 18446744073709551615n) throw new Error("CALCULATION_RANGE");
  return result;
}
function numeric(e: any, inputs: Readonly<Record<string, unknown>>): bigint {
  if (e.op === "literal") return uint64(e.value);
  if (e.op === "input") return uint64(required(inputs, e.name));
  const left = numeric(e.left, inputs), right = numeric(e.right, inputs);
  let result: bigint;
  if (e.op === "add") result = left + right;
  else if (e.op === "subtract") { if (left < right) throw new Error("CALCULATION_UNDERFLOW"); result = left - right; }
  else if (e.op === "multiply") result = left * right;
  else if (e.op === "divide") {
    if (right === 0n) throw new Error("CALCULATION_DIVIDE_BY_ZERO");
    if (left % right !== 0n && contract.division_rounding === "reject") throw new Error("CALCULATION_INEXACT");
    result = left / right + (contract.division_rounding === "ceil" && left % right !== 0n ? 1n : 0n);
  } else throw new Error("CALCULATION_OPERATOR");
  if (result > 18446744073709551615n) throw new Error("CALCULATION_OVERFLOW");
  return result;
}
function value(e: any, row: Readonly<Record<string, unknown>>, inputs: Readonly<Record<string, unknown>>): any {
  return e.kind === "literal" ? e.value : required(e.kind === "field" ? row : inputs, e.name);
}
function predicate(e: any, row: Readonly<Record<string, unknown>>, inputs: Readonly<Record<string, unknown>>): boolean {
  if (e.op === "all") return e.terms.every((term: any) => predicate(term, row, inputs));
  if (e.op === "any") return e.terms.some((term: any) => predicate(term, row, inputs));
  if (e.op === "not") return !predicate(e.term, row, inputs);
  const left = value(e.left, row, inputs), right = value(e.right, row, inputs);
  if (e.op === "eq") return left === right;
  if (e.op === "lt") return left < right;
  if (e.op === "lte") return left <= right;
  if (e.op === "gt") return left > right;
  if (e.op === "gte") return left >= right;
  throw new Error("PREDICATE_OPERATOR");
}
function predicateFields(e: any): string[] {
  if (e === null) return [];
  if (e.op === "all" || e.op === "any") return e.terms.flatMap(predicateFields);
  if (e.op === "not") return predicateFields(e.term);
  return [e.left, e.right].filter(v => v.kind === "field").map(v => v.name);
}
`;

/** Explicit realization only; never changes the default generator's bytes. */
export function renderExactUInt64(input: GeneratorInput): string | null {
  const contract = input.body.typed_contract as any;
  const name = input.node_id.replace(/-([a-z0-9])/g, (_, c: string) => c.toUpperCase());
  // Bracket-free generated identifier, also safe for JavaScript reserved words.
  const fn = `evaluate_${name}`;
  const header = `// ${EXACT_UINT64_PROFILE}\n// ${input.feature_id}:${input.node_id}\n`;
  if ((input.kind === "Entity" || input.kind === "Value Object") && contract?.schema_version === "domainspec.typed-record/v1") {
    const fields = contract.properties.map((p: any) => {
      if (p.type.kind !== "scalar") throw new Error("MTCLI_EXACT_RECORD: scalar properties required");
      const type = p.type.name === "UInt64" ? "bigint | number" : p.type.name === "Bool" ? "boolean" : "string";
      return `  readonly ${JSON.stringify(p.name)}${p.cardinality === "optional" ? "?" : ""}: ${type};`;
    });
    return `${header}export interface ExactRecord {\n${fields.join("\n")}\n}\n`;
  }
  if (!["Query", "Calculation", "Mapping", "Policy"].includes(input.kind)) return null;
  if (contract?.schema_version !== `domainspec.typed-${input.kind.toLowerCase()}/v1`) throw new Error("MTCLI_EXACT_CONTRACT: typed backend contract required");
  const prefix = `${header}const contract: any = ${canonicalJson(contract)};\n${runtime}`;
  if (input.kind === "Calculation") return `${prefix}
export function ${fn}(inputs: Readonly<Record<string, unknown>>): bigint {
  for (const p of contract.inputs) { if (!Object.hasOwn(inputs,p.name)) throw new Error("MISSING_CALCULATION_INPUT:" + p.name); uint64(required(inputs,p.name)); }
  return numeric(contract.expression, inputs);
}\n`;
  if (input.kind === "Query") return `${prefix}
export function ${fn}(rows: readonly Readonly<Record<string, unknown>>[], inputs: Readonly<Record<string, unknown>> = {}): readonly Readonly<Record<string, unknown>>[] {
  for (const p of contract.inputs) required(inputs,p.name);
  let selected = rows.filter(row => { for (const field of predicateFields(contract.filter)) required(row,field); return contract.filter === null || predicate(contract.filter,row,inputs); });
  if (contract.order_by !== null) selected = [...selected].sort((a,b) => {
    const left = required(a,contract.order_by.field), right = required(b,contract.order_by.field);
    const order = left < right ? -1 : left > right ? 1 : 0;
    return contract.order_by.direction === "asc" ? order : -order;
  });
  if (contract.limit !== null) selected = selected.slice(0,contract.limit);
  return Object.freeze(selected.map(row => Object.freeze(Object.fromEntries(contract.projection.map((field: string) => [field,required(row,field)])))));
}\n`;
  if (input.kind === "Mapping") return `${prefix}
export function ${fn}(source: Readonly<Record<string, unknown>>): Readonly<Record<string, unknown>> {
  const result: Record<string, unknown> = {};
  for (const field of contract.fields) {
    if (field.source !== null && Object.hasOwn(source,field.source)) result[field.target] = required(source,field.source);
    else if (field.default !== null) result[field.target] = field.default.value;
    else if (contract.total) throw new Error("MAPPING_REQUIRED_VALUE:" + field.target);
  }
  return Object.freeze(result);
}\n`;
  return `${prefix}
export function ${fn}(inputs: Readonly<Record<string, unknown>>): string {
  for (const p of contract.inputs) required(inputs,p.name);
  for (const candidate of contract.cases) if (predicate(candidate.when,{},inputs)) return candidate.target;
  return contract.default_target;
}\n`;
}
