import { decodeTypedType, type ScalarName, type TypedParameter, type TypedType } from "../typed-operation/contracts.js";

const NODE_SELECTOR = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const ONTOLOGY_SELECTOR = /^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$/;
const LOCAL_NAME = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const MAX_DEPTH = 16;

export type BackendScalar = string | boolean | number;
export type BackendValue =
  | Readonly<{ kind: "literal"; type: ScalarName; value: BackendScalar }>
  | Readonly<{ kind: "parameter"; name: string }>
  | Readonly<{ kind: "field"; name: string }>;

export type BackendPredicate =
  | Readonly<{ op: "eq" | "lt" | "lte" | "gt" | "gte"; left: BackendValue; right: BackendValue }>
  | Readonly<{ op: "all" | "any"; terms: readonly BackendPredicate[] }>
  | Readonly<{ op: "not"; term: BackendPredicate }>;

export type NumericExpression =
  | Readonly<{ op: "literal"; value: number }>
  | Readonly<{ op: "input"; name: string }>
  | Readonly<{ op: "add" | "subtract" | "multiply" | "divide"; left: NumericExpression; right: NumericExpression }>;

export interface TypedQueryContract {
  readonly schema_version: "domainspec.typed-query/v1";
  readonly ontology_query: string;
  readonly source: string;
  readonly inputs: readonly TypedParameter[];
  readonly filter: BackendPredicate | null;
  readonly projection: readonly string[];
  readonly order_by: Readonly<{ field: string; direction: "asc" | "desc" }> | null;
  readonly limit: number | null;
}

export interface TypedCalculationContract {
  readonly schema_version: "domainspec.typed-calculation/v1";
  readonly ontology_calculation: string;
  readonly inputs: readonly TypedParameter[];
  readonly result: Readonly<{ kind: "scalar"; name: "UInt64" }>;
  readonly division_rounding: "floor" | "ceil" | "reject";
  readonly expression: NumericExpression;
}

export interface TypedMappingField {
  readonly target: string;
  readonly source: string | null;
  readonly default: Readonly<{ type: ScalarName; value: BackendScalar }> | null;
}

export interface TypedMappingContract {
  readonly schema_version: "domainspec.typed-mapping/v1";
  readonly ontology_mapping: string;
  readonly source: string;
  readonly target: string;
  readonly fields: readonly TypedMappingField[];
  readonly total: boolean;
}

export interface TypedPolicyCase {
  readonly target: string;
  readonly when: BackendPredicate;
}

export interface TypedPolicyContract {
  readonly schema_version: "domainspec.typed-policy/v1";
  readonly ontology_policy: string;
  readonly inputs: readonly TypedParameter[];
  readonly cases: readonly TypedPolicyCase[];
  readonly default_target: string;
}

export type TypedBackendContract = TypedQueryContract | TypedCalculationContract | TypedMappingContract | TypedPolicyContract;

export class TypedBackendContractError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "TypedBackendContractError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new TypedBackendContractError(code, pointer, message);
}

function object(value: unknown, pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("MTCLI_BACKEND_SCHEMA", pointer, "expected object");
  return value as Record<string, unknown>;
}

function exact(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> {
  const result = object(value, pointer);
  if (JSON.stringify(Object.keys(result).sort()) !== JSON.stringify([...keys].sort())) fail("MTCLI_BACKEND_SCHEMA", pointer, "unexpected or missing member");
  return result;
}

function text(value: unknown, pointer: string): string {
  if (typeof value !== "string" || value.length === 0) fail("MTCLI_BACKEND_SCHEMA", pointer, "expected nonempty string");
  return value;
}

function local(value: unknown, pointer: string): string {
  const result = text(value, pointer);
  if (!LOCAL_NAME.test(result)) fail("MTCLI_BACKEND_NAME", pointer, "expected lower snake-case name");
  return result;
}

function selector(value: unknown, pointer: string): string {
  const result = text(value, pointer);
  if (!NODE_SELECTOR.test(result)) fail("MTCLI_BACKEND_SELECTOR", pointer, "expected feature-id:node-id selector");
  return result;
}

function ontology(value: unknown, pointer: string): string {
  const result = text(value, pointer);
  if (!ONTOLOGY_SELECTOR.test(result)) fail("MTCLI_BACKEND_ONTOLOGY", pointer, "expected uppercase ontology selector");
  return result;
}

function unique(values: readonly string[], pointer: string): void {
  if (new Set(values).size !== values.length) fail("MTCLI_BACKEND_DUPLICATE", pointer, "duplicate member");
}

function scalar(value: unknown, type: ScalarName, pointer: string): BackendScalar {
  const valid = type === "String" ? typeof value === "string" : type === "Bool" ? typeof value === "boolean" : Number.isSafeInteger(value) && Number(value) >= 0;
  if (!valid) fail("MTCLI_BACKEND_LITERAL", pointer, `literal does not match ${type}`);
  return value as BackendScalar;
}

function parameters(value: unknown, pointer: string): readonly TypedParameter[] {
  if (!Array.isArray(value)) fail("MTCLI_BACKEND_SCHEMA", pointer, "expected parameter array");
  const result = value.map((entry, index): TypedParameter => {
    const item = exact(entry, ["name", "type"], `${pointer}/${index}`);
    const type = decodeTypedType(item.type, `${pointer}/${index}/type`);
    if (type.kind !== "scalar") fail("MTCLI_BACKEND_TYPE", `${pointer}/${index}/type`, "backend parameter must be scalar");
    return Object.freeze({ name: local(item.name, `${pointer}/${index}/name`), type });
  });
  unique(result.map(({ name }) => name), pointer);
  return Object.freeze(result);
}

function valueRef(value: unknown, pointer: string): BackendValue {
  const item = object(value, pointer);
  if (item.kind === "literal") {
    const literal = exact(item, ["kind", "type", "value"], pointer);
    if (!["String", "Bool", "UInt64"].includes(String(literal.type))) fail("MTCLI_BACKEND_LITERAL", `${pointer}/type`, "unsupported scalar literal");
    const type = literal.type as ScalarName;
    return Object.freeze({ kind: "literal", type, value: scalar(literal.value, type, `${pointer}/value`) });
  }
  if (item.kind === "parameter" || item.kind === "field") {
    const reference = exact(item, ["kind", "name"], pointer);
    return Object.freeze({ kind: item.kind, name: local(reference.name, `${pointer}/name`) });
  }
  return fail("MTCLI_BACKEND_VALUE", `${pointer}/kind`, "unsupported value reference");
}

export function decodeBackendPredicate(value: unknown, pointer = "/predicate", depth = 0): BackendPredicate {
  if (depth > MAX_DEPTH) fail("MTCLI_BACKEND_DEPTH", pointer, "predicate nesting exceeds maximum depth");
  const item = object(value, pointer);
  if (["eq", "lt", "lte", "gt", "gte"].includes(String(item.op))) {
    const comparison = exact(item, ["op", "left", "right"], pointer);
    return Object.freeze({ op: comparison.op as "eq" | "lt" | "lte" | "gt" | "gte", left: valueRef(comparison.left, `${pointer}/left`), right: valueRef(comparison.right, `${pointer}/right`) });
  }
  if (item.op === "all" || item.op === "any") {
    const logical = exact(item, ["op", "terms"], pointer);
    if (!Array.isArray(logical.terms) || logical.terms.length === 0) fail("MTCLI_BACKEND_PREDICATE", `${pointer}/terms`, "logical predicate requires terms");
    return Object.freeze({ op: item.op, terms: Object.freeze(logical.terms.map((term, index) => decodeBackendPredicate(term, `${pointer}/terms/${index}`, depth + 1))) });
  }
  if (item.op === "not") {
    const logical = exact(item, ["op", "term"], pointer);
    return Object.freeze({ op: "not", term: decodeBackendPredicate(logical.term, `${pointer}/term`, depth + 1) });
  }
  return fail("MTCLI_BACKEND_PREDICATE", `${pointer}/op`, "unsupported predicate operator");
}

function numeric(value: unknown, pointer: string, depth = 0): NumericExpression {
  if (depth > MAX_DEPTH) fail("MTCLI_BACKEND_DEPTH", pointer, "numeric expression nesting exceeds maximum depth");
  const item = object(value, pointer);
  if (item.op === "literal") {
    const literal = exact(item, ["op", "value"], pointer);
    if (!Number.isSafeInteger(literal.value) || Number(literal.value) < 0) fail("MTCLI_BACKEND_NUMBER", `${pointer}/value`, "expected UInt64 literal");
    return Object.freeze({ op: "literal", value: Number(literal.value) });
  }
  if (item.op === "input") {
    const input = exact(item, ["op", "name"], pointer);
    return Object.freeze({ op: "input", name: local(input.name, `${pointer}/name`) });
  }
  if (["add", "subtract", "multiply", "divide"].includes(String(item.op))) {
    const binary = exact(item, ["op", "left", "right"], pointer);
    return Object.freeze({ op: binary.op as "add" | "subtract" | "multiply" | "divide", left: numeric(binary.left, `${pointer}/left`, depth + 1), right: numeric(binary.right, `${pointer}/right`, depth + 1) });
  }
  return fail("MTCLI_BACKEND_NUMBER", `${pointer}/op`, "unsupported numeric operator");
}

export function decodeTypedQueryContract(value: unknown, pointer = "/typed_contract"): TypedQueryContract {
  const item = exact(value, ["schema_version", "ontology_query", "source", "inputs", "filter", "projection", "order_by", "limit"], pointer);
  if (item.schema_version !== "domainspec.typed-query/v1") fail("MTCLI_BACKEND_SCHEMA", `${pointer}/schema_version`, "unsupported typed Query schema");
  const projection = Array.isArray(item.projection) ? item.projection.map((entry, index) => local(entry, `${pointer}/projection/${index}`)) : fail("MTCLI_BACKEND_SCHEMA", `${pointer}/projection`, "expected projection array");
  if (projection.length === 0) fail("MTCLI_BACKEND_SCHEMA", `${pointer}/projection`, "projection cannot be empty");
  unique(projection, `${pointer}/projection`);
  let orderBy: TypedQueryContract["order_by"] = null;
  if (item.order_by !== null) {
    const order = exact(item.order_by, ["field", "direction"], `${pointer}/order_by`);
    if (order.direction !== "asc" && order.direction !== "desc") fail("MTCLI_BACKEND_QUERY", `${pointer}/order_by/direction`, "direction must be asc or desc");
    orderBy = Object.freeze({ field: local(order.field, `${pointer}/order_by/field`), direction: order.direction });
  }
  if (item.limit !== null && (!Number.isSafeInteger(item.limit) || Number(item.limit) <= 0)) fail("MTCLI_BACKEND_QUERY", `${pointer}/limit`, "limit must be a positive integer or null");
  return Object.freeze({
    schema_version: "domainspec.typed-query/v1",
    ontology_query: ontology(item.ontology_query, `${pointer}/ontology_query`),
    source: selector(item.source, `${pointer}/source`),
    inputs: parameters(item.inputs, `${pointer}/inputs`),
    filter: item.filter === null ? null : decodeBackendPredicate(item.filter, `${pointer}/filter`),
    projection: Object.freeze(projection),
    order_by: orderBy,
    limit: item.limit === null ? null : Number(item.limit),
  });
}

export function decodeTypedCalculationContract(value: unknown, pointer = "/typed_contract"): TypedCalculationContract {
  const item = exact(value, ["schema_version", "ontology_calculation", "inputs", "result", "division_rounding", "expression"], pointer);
  if (item.schema_version !== "domainspec.typed-calculation/v1") fail("MTCLI_BACKEND_SCHEMA", `${pointer}/schema_version`, "unsupported typed Calculation schema");
  const result = decodeTypedType(item.result, `${pointer}/result`);
  if (result.kind !== "scalar" || result.name !== "UInt64") fail("MTCLI_BACKEND_TYPE", `${pointer}/result`, "Calculation result must be UInt64");
  if (!["floor", "ceil", "reject"].includes(String(item.division_rounding))) fail("MTCLI_BACKEND_CALCULATION", `${pointer}/division_rounding`, "unsupported division rounding policy");
  return Object.freeze({ schema_version: "domainspec.typed-calculation/v1", ontology_calculation: ontology(item.ontology_calculation, `${pointer}/ontology_calculation`), inputs: parameters(item.inputs, `${pointer}/inputs`), result: Object.freeze({ kind: "scalar" as const, name: "UInt64" as const }), division_rounding: item.division_rounding as TypedCalculationContract["division_rounding"], expression: numeric(item.expression, `${pointer}/expression`) });
}

export function decodeTypedMappingContract(value: unknown, pointer = "/typed_contract"): TypedMappingContract {
  const item = exact(value, ["schema_version", "ontology_mapping", "source", "target", "fields", "total"], pointer);
  if (item.schema_version !== "domainspec.typed-mapping/v1") fail("MTCLI_BACKEND_SCHEMA", `${pointer}/schema_version`, "unsupported typed Mapping schema");
  if (!Array.isArray(item.fields) || item.fields.length === 0) fail("MTCLI_BACKEND_SCHEMA", `${pointer}/fields`, "Mapping requires fields");
  const fields = item.fields.map((entry, index): TypedMappingField => {
    const field = exact(entry, ["target", "source", "default"], `${pointer}/fields/${index}`);
    let fallback: TypedMappingField["default"] = null;
    if (field.default !== null) {
      const literal = exact(field.default, ["type", "value"], `${pointer}/fields/${index}/default`);
      if (!["String", "Bool", "UInt64"].includes(String(literal.type))) fail("MTCLI_BACKEND_LITERAL", `${pointer}/fields/${index}/default/type`, "unsupported default type");
      const type = literal.type as ScalarName;
      fallback = Object.freeze({ type, value: scalar(literal.value, type, `${pointer}/fields/${index}/default/value`) });
    }
    const source = field.source === null ? null : local(field.source, `${pointer}/fields/${index}/source`);
    if (source === null && fallback === null) fail("MTCLI_BACKEND_MAPPING", `${pointer}/fields/${index}`, "Mapping field requires source or default");
    return Object.freeze({ target: local(field.target, `${pointer}/fields/${index}/target`), source, default: fallback });
  });
  unique(fields.map(({ target }) => target), `${pointer}/fields`);
  if (typeof item.total !== "boolean") fail("MTCLI_BACKEND_MAPPING", `${pointer}/total`, "total must be Boolean");
  return Object.freeze({ schema_version: "domainspec.typed-mapping/v1", ontology_mapping: ontology(item.ontology_mapping, `${pointer}/ontology_mapping`), source: selector(item.source, `${pointer}/source`), target: selector(item.target, `${pointer}/target`), fields: Object.freeze(fields), total: item.total });
}

export function decodeTypedPolicyContract(value: unknown, pointer = "/typed_contract"): TypedPolicyContract {
  const item = exact(value, ["schema_version", "ontology_policy", "inputs", "cases", "default_target"], pointer);
  if (item.schema_version !== "domainspec.typed-policy/v1") fail("MTCLI_BACKEND_SCHEMA", `${pointer}/schema_version`, "unsupported typed Policy schema");
  if (!Array.isArray(item.cases) || item.cases.length === 0) fail("MTCLI_BACKEND_SCHEMA", `${pointer}/cases`, "Policy requires ordered cases");
  const cases = item.cases.map((entry, index): TypedPolicyCase => {
    const candidate = exact(entry, ["target", "when"], `${pointer}/cases/${index}`);
    return Object.freeze({ target: selector(candidate.target, `${pointer}/cases/${index}/target`), when: decodeBackendPredicate(candidate.when, `${pointer}/cases/${index}/when`) });
  });
  unique(cases.map(({ target }) => target), `${pointer}/cases`);
  return Object.freeze({ schema_version: "domainspec.typed-policy/v1", ontology_policy: ontology(item.ontology_policy, `${pointer}/ontology_policy`), inputs: parameters(item.inputs, `${pointer}/inputs`), cases: Object.freeze(cases), default_target: selector(item.default_target, `${pointer}/default_target`) });
}

export function decodeTypedBackendContract(kind: "Query" | "Calculation" | "Mapping" | "Policy", value: unknown, pointer = "/typed_contract"): TypedBackendContract {
  if (kind === "Query") return decodeTypedQueryContract(value, pointer);
  if (kind === "Calculation") return decodeTypedCalculationContract(value, pointer);
  if (kind === "Mapping") return decodeTypedMappingContract(value, pointer);
  return decodeTypedPolicyContract(value, pointer);
}

export function scalarTypeOf(type: TypedType): ScalarName | null {
  return type.kind === "scalar" ? type.name : null;
}
