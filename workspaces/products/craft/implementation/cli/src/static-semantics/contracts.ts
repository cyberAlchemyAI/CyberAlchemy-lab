const LOCAL_ID = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const SELECTOR = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const MAX_DEPTH = 16;

export type CalculationExpression =
  | Readonly<{ op: "literal"; value: number }>
  | Readonly<{ op: "input"; name: string }>
  | Readonly<{ op: "add" | "multiply" | "min" | "max"; terms: readonly CalculationExpression[] }>
  | Readonly<{ op: "subtract" | "divide"; left: CalculationExpression; right: CalculationExpression }>;

export interface CalculationSemantics {
  readonly schema_version: "domainspec.calculation-semantics/v1";
  readonly result: "number";
  readonly expression: CalculationExpression;
  readonly rounding: Readonly<{ readonly mode: "none" | "floor" | "ceil" | "toward-zero" | "half-away-from-zero"; readonly scale: number }>;
}

export interface PolicyDecision {
  readonly rule_ref: string;
  readonly strategy: string;
}

export interface MappingField {
  readonly target_field: string;
  readonly source_field: string | null;
  readonly default_value: string | number | boolean | null;
  readonly required: boolean;
  readonly conversion: "identity" | "string" | "number" | "boolean";
}

export class StaticSemanticsError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "StaticSemanticsError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new StaticSemanticsError(code, pointer, message);
}

function object(value: unknown, pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("MTCLI_STATIC_SCHEMA", pointer, "expected object");
  return value as Record<string, unknown>;
}

function exact(value: Record<string, unknown>, keys: readonly string[], pointer: string): void {
  if (JSON.stringify(Object.keys(value).sort()) !== JSON.stringify([...keys].sort())) fail("MTCLI_STATIC_SCHEMA", pointer, "unexpected or missing member");
}

function id(value: unknown, pointer: string): string {
  if (typeof value !== "string" || !LOCAL_ID.test(value)) fail("MTCLI_STATIC_ID", pointer, "expected lowercase kebab-case identifier");
  return value;
}

function scalar(value: unknown, pointer: string): string | number | boolean | null {
  if (value === null || typeof value === "string" || typeof value === "boolean" || (typeof value === "number" && Number.isFinite(value))) return value;
  return fail("MTCLI_MAPPING_DEFAULT", pointer, "default must be a finite JSON scalar or null");
}

function expression(value: unknown, inputs: ReadonlySet<string>, pointer: string, depth: number): CalculationExpression {
  if (depth > MAX_DEPTH) fail("MTCLI_CALCULATION_DEPTH", pointer, "calculation expression exceeds maximum depth");
  const row = object(value, pointer);
  if (typeof row.op !== "string") fail("MTCLI_CALCULATION_EXPRESSION", `${pointer}/op`, "calculation expression requires op");
  if (row.op === "literal") {
    exact(row, ["op", "value"], pointer);
    if (typeof row.value !== "number" || !Number.isFinite(row.value)) fail("MTCLI_CALCULATION_NUMBER", `${pointer}/value`, "literal must be finite");
    return Object.freeze({ op: "literal", value: row.value });
  }
  if (row.op === "input") {
    exact(row, ["op", "name"], pointer);
    const name = id(row.name, `${pointer}/name`);
    if (!inputs.has(name)) fail("MTCLI_CALCULATION_INPUT", `${pointer}/name`, `unknown calculation input:${name}`);
    return Object.freeze({ op: "input", name });
  }
  if (["add", "multiply", "min", "max"].includes(row.op)) {
    exact(row, ["op", "terms"], pointer);
    if (!Array.isArray(row.terms) || row.terms.length === 0) fail("MTCLI_CALCULATION_EXPRESSION", `${pointer}/terms`, "n-ary calculation requires terms");
    return Object.freeze({ op: row.op as "add" | "multiply" | "min" | "max", terms: Object.freeze(row.terms.map((term, index) => expression(term, inputs, `${pointer}/terms/${index}`, depth + 1))) });
  }
  if (row.op === "subtract" || row.op === "divide") {
    exact(row, ["op", "left", "right"], pointer);
    return Object.freeze({ op: row.op, left: expression(row.left, inputs, `${pointer}/left`, depth + 1), right: expression(row.right, inputs, `${pointer}/right`, depth + 1) });
  }
  return fail("MTCLI_CALCULATION_EXPRESSION", `${pointer}/op`, `unsupported calculation operator:${row.op}`);
}

export function decodeCalculationSemantics(value: unknown, inputs: readonly string[], pointer = "/semantics"): CalculationSemantics {
  const row = object(value, pointer);
  exact(row, ["schema_version", "result", "expression", "rounding"], pointer);
  if (row.schema_version !== "domainspec.calculation-semantics/v1" || row.result !== "number") fail("MTCLI_CALCULATION_SCHEMA", pointer, "expected numeric calculation semantics v1");
  const rounding = object(row.rounding, `${pointer}/rounding`);
  exact(rounding, ["mode", "scale"], `${pointer}/rounding`);
  if (!["none", "floor", "ceil", "toward-zero", "half-away-from-zero"].includes(String(rounding.mode))) fail("MTCLI_CALCULATION_ROUNDING", `${pointer}/rounding/mode`, "unsupported rounding mode");
  if (!Number.isInteger(rounding.scale) || Number(rounding.scale) < 0 || Number(rounding.scale) > 12) fail("MTCLI_CALCULATION_ROUNDING", `${pointer}/rounding/scale`, "rounding scale must be an integer from 0 through 12");
  const inputSet = new Set(inputs.map((entry, index) => id(entry, `${pointer}/inputs/${index}`)));
  if (inputSet.size !== inputs.length || inputs.length === 0) fail("MTCLI_CALCULATION_INPUT", `${pointer}/inputs`, "calculation inputs must be nonempty and unique");
  return Object.freeze({ schema_version: "domainspec.calculation-semantics/v1", result: "number", expression: expression(row.expression, inputSet, `${pointer}/expression`, 0), rounding: Object.freeze({ mode: rounding.mode as CalculationSemantics["rounding"]["mode"], scale: rounding.scale as number }) });
}

export function decodePolicyDecisions(value: unknown, strategies: readonly string[], pointer = "/decisions"): readonly PolicyDecision[] {
  if (!Array.isArray(value) || value.length === 0) fail("MTCLI_POLICY_DECISIONS", pointer, "Policy requires at least one decision");
  const strategySet = new Set(strategies);
  const decisions = value.map((entry, index): PolicyDecision => {
    const entryPointer = `${pointer}/${index}`;
    const row = object(entry, entryPointer);
    exact(row, ["rule_ref", "strategy"], entryPointer);
    if (typeof row.rule_ref !== "string" || !SELECTOR.test(row.rule_ref)) fail("MTCLI_POLICY_RULE", `${entryPointer}/rule_ref`, "Policy rule_ref must be a selector");
    const strategy = id(row.strategy, `${entryPointer}/strategy`);
    if (!strategySet.has(strategy)) fail("MTCLI_POLICY_STRATEGY", `${entryPointer}/strategy`, `undeclared strategy:${strategy}`);
    return Object.freeze({ rule_ref: row.rule_ref, strategy });
  });
  if (new Set(decisions.map(({ rule_ref }) => rule_ref)).size !== decisions.length) fail("MTCLI_POLICY_DECISIONS", pointer, "Policy decision rule refs must be unique");
  return Object.freeze(decisions);
}

export function decodeMappingFields(value: unknown, pointer = "/fields"): readonly MappingField[] {
  if (!Array.isArray(value) || value.length === 0) fail("MTCLI_MAPPING_FIELDS", pointer, "Mapping requires at least one field transform");
  const fields = value.map((entry, index): MappingField => {
    const entryPointer = `${pointer}/${index}`;
    const row = object(entry, entryPointer);
    exact(row, ["target_field", "source_field", "default_value", "required", "conversion"], entryPointer);
    const targetField = id(row.target_field, `${entryPointer}/target_field`);
    const sourceField = row.source_field === null ? null : id(row.source_field, `${entryPointer}/source_field`);
    const defaultValue = scalar(row.default_value, `${entryPointer}/default_value`);
    if (typeof row.required !== "boolean") fail("MTCLI_MAPPING_FIELDS", `${entryPointer}/required`, "required must be Boolean");
    if (!["identity", "string", "number", "boolean"].includes(String(row.conversion))) fail("MTCLI_MAPPING_CONVERSION", `${entryPointer}/conversion`, "unsupported Mapping conversion");
    if (sourceField === null && defaultValue === null) fail("MTCLI_MAPPING_FIELDS", entryPointer, "constant mapping requires a non-null default");
    return Object.freeze({ target_field: targetField, source_field: sourceField, default_value: defaultValue, required: row.required, conversion: row.conversion as MappingField["conversion"] });
  });
  if (new Set(fields.map(({ target_field }) => target_field)).size !== fields.length) fail("MTCLI_MAPPING_FIELDS", pointer, "Mapping target fields must be unique");
  return Object.freeze(fields);
}
