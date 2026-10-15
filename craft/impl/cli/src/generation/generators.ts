import { canonicalJson } from "../input/source-manifest.js";
import type { FieldSpec, InterfaceOperationSpec, StateTransitionSpec, TypeRef } from "../input/project-model.js";
import { FROZEN_META_TYPE_CATALOG } from "../meta-types/catalog.js";
import type { SupportedLanguage } from "../meta-types/types.js";
import type { GeneratorInput, GeneratorRegistration } from "./contracts.js";
import { renderTypedRustCalculation, renderTypedRustOperation, renderTypedRustRule } from "../typed-operation/rust.js";
import type {
  BackendPredicate,
  BackendValue,
  NumericExpression,
  TypedNumericCalculationContract,
  TypedMappingContract,
  TypedPolicyContract,
  TypedQueryContract,
} from "../typed-backend/contracts.js";

const EXTENSIONS = Object.freeze({ typescript: "ts", python: "py", rust: "rs" } as const);
const LOWER_IDENTIFIER_KEYWORDS = new Set([
  "as", "async", "await", "break", "case", "catch", "class", "const", "continue", "crate", "def", "default", "del", "do", "else", "enum", "except", "export", "extends", "false", "finally", "fn", "for", "from", "function", "global", "if", "impl", "import", "in", "interface", "is", "lambda", "let", "loop", "match", "mod", "move", "mut", "new", "none", "nonlocal", "not", "null", "pass", "pub", "raise", "ref", "return", "self", "static", "struct", "super", "switch", "this", "throw", "trait", "true", "try", "type", "typeof", "unsafe", "use", "var", "while", "with", "yield",
]);

function words(value: string): string[] {
  return value.split(/[^A-Za-z0-9]+/).filter(Boolean);
}

function pascal(value: string): string {
  const raw = words(value).map((word) => `${word[0]?.toUpperCase() ?? ""}${word.slice(1)}`).join("");
  const result = raw || "DomainNode";
  return /^[A-Za-z_]/.test(result) ? result : `Domain${result}`;
}

function camel(value: string): string {
  const result = pascal(value);
  const candidate = `${result[0]?.toLowerCase() ?? "d"}${result.slice(1)}`;
  return LOWER_IDENTIFIER_KEYWORDS.has(candidate) ? `domain${result}` : candidate;
}

function snake(value: string): string {
  const raw = words(value).map((word) => word.toLowerCase()).join("_") || "domain_node";
  const candidate = /^[A-Za-z_]/.test(raw) ? raw : `domain_${raw}`;
  return LOWER_IDENTIFIER_KEYWORDS.has(candidate) ? `domain_${candidate}` : candidate;
}

function uniqueNames(values: readonly string[], transform: (value: string) => string, label: string): readonly string[] {
  const result = values.map(transform);
  if (new Set(result).size !== result.length) throw new Error(`${label} values collide after identifier normalization`);
  return result;
}

function strings(value: unknown): readonly string[] {
  return Array.isArray(value) && value.every((entry) => typeof entry === "string") ? value : [];
}

function text(value: unknown, fallback: string): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function stateTransitions(value: unknown): readonly StateTransitionSpec[] {
  return Array.isArray(value) ? value as readonly StateTransitionSpec[] : [];
}

function fieldSpecs(value: unknown): readonly FieldSpec[] {
  return Array.isArray(value) ? value as readonly FieldSpec[] : [];
}

function fieldSpec(value: unknown): FieldSpec {
  return value as FieldSpec;
}

function interfaceOperations(value: unknown): readonly InterfaceOperationSpec[] {
  return Array.isArray(value) ? value as readonly InterfaceOperationSpec[] : [];
}

function typescriptType(typeRef: TypeRef): string {
  if (typeRef.kind === "reference") return `DomainspecRef<${JSON.stringify(typeRef.selector)}>`;
  return ({ string: "string", boolean: "boolean", integer: "number", decimal: "number", timestamp: "string", uuid: "string" } as const)[typeRef.name];
}

function pythonType(typeRef: TypeRef): string {
  if (typeRef.kind === "reference") return `Annotated[str, ${JSON.stringify(`domainspec-ref:${typeRef.selector}`)}]`;
  return ({ string: "str", boolean: "bool", integer: "int", decimal: "float", timestamp: "str", uuid: "str" } as const)[typeRef.name];
}

function rustType(typeRef: TypeRef): string {
  if (typeRef.kind === "reference") return "String";
  return ({ string: "String", boolean: "bool", integer: "i64", decimal: "f64", timestamp: "String", uuid: "String" } as const)[typeRef.name];
}

function typescriptFields(fields: readonly FieldSpec[]): string {
  return fields.map((field) => `  readonly ${camel(field.field_id)}${field.required ? "" : "?"}: ${typescriptType(field.type_ref)};`).join("\n");
}

function pythonFields(fields: readonly FieldSpec[]): string {
  return [...fields].sort((left, right) => Number(right.required) - Number(left.required)).map((field) => `    ${snake(field.field_id)}: ${pythonType(field.type_ref)}${field.required ? "" : " | None = None"}`).join("\n");
}

function rustFields(fields: readonly FieldSpec[]): string {
  return fields.map((field) => `    pub ${snake(field.field_id)}: ${field.required ? rustType(field.type_ref) : `Option<${rustType(field.type_ref)}>`},`).join("\n");
}

function l1Marker(input: GeneratorInput, comment: "//" | "#"): string {
  return `${comment} domainspec-l1-contract: ${canonicalJson({ kind: input.kind, body: input.body })}\n`;
}

function pythonStateTransitions(values: readonly StateTransitionSpec[]): string {
  return values.map((transition) => `{${[
    `"transition_id": ${JSON.stringify(transition.transition_id)}`,
    `"source_state": ${JSON.stringify(transition.source_state)}`,
    `"target_state": ${JSON.stringify(transition.target_state)}`,
    `"guard_ref": ${transition.guard_ref === null ? "None" : JSON.stringify(transition.guard_ref)}`,
    `"effect_event_ref": ${transition.effect_event_ref === null ? "None" : JSON.stringify(transition.effect_event_ref)}`,
  ].join(", ")}}`).join(", ");
}

function rustOption(value: string | null): string {
  return value === null ? "None" : `Some(${JSON.stringify(value)})`;
}

function provenance(input: GeneratorInput, comment: "//" | "#"): string {
  const metadata = canonicalJson({
    baseline_id: FROZEN_META_TYPE_CATALOG.baseline_id,
    baseline_digest: FROZEN_META_TYPE_CATALOG.baseline_digest,
    meta_type_id: input.meta_type_id,
    meta_type_label: input.kind,
    language: input.realization.language,
    source_sha256: input.realization.source.sha256,
    provider_sha256: input.realization.provider.sha256,
    binding_sha256: input.realization.binding.sha256,
  });
  const relationships = canonicalJson(input.relationships);
  const body = canonicalJson(input.body);
  return `${comment} domainspec-meta: ${metadata}\n${comment} domainspec-body: ${body}\n${comment} domainspec-relationships: ${relationships}\n`;
}

function typedRuleProjection(input: GeneratorInput): Readonly<{
  root: string;
  properties: Readonly<Record<string, string>>;
  rules: Readonly<Record<string, unknown>>;
}> {
  const closure = input.typed_closure;
  if (closure?.schema_version !== "domainspec.typed-rule-closure/v1" && closure?.schema_version !== "domainspec.typed-calculation-closure/v1") throw new Error("typed predicate requires a Rule or Calculation semantic closure");
  return Object.freeze({
    root: closure.root_selector,
    properties: Object.freeze(Object.fromEntries(closure.properties.map((row) => {
      const field = row.domainspec_selector.split("#")[1];
      if (field === undefined) throw new Error(`typed Rule property binding lacks a field:${row.domainspec_selector}`);
      return [row.ontology_property, field];
    }))),
    rules: Object.freeze(Object.fromEntries(closure.nodes.flatMap((node) => node.typed_contract.schema_version === "domainspec.typed-rule/v1" ? [[node.selector, node.typed_contract]] : []))),
  });
}

function renderTypeScriptTypedRule(input: GeneratorInput, fn: string, header: string): string {
  const projection = typedRuleProjection(input);
  const closure = input.typed_closure!;
  const calculation = closure.schema_version === "domainspec.typed-calculation-closure/v1" ? closure.calculation : null;
  const marker = calculation === null ? '// domainspec-rule-semantics: "domainspec.typed-rule/v1"' : `// domainspec-calculation-semantics: "domainspec.typed-calculation/v2"\n// domainspec-typed-closure-sha256: ${JSON.stringify(closure.closure_sha256)}`;
  const entry = calculation === null
    ? `export function ${fn}(parameters: Readonly<Record<string, unknown>>): boolean { return domainspecEvaluate(domainspecRuleRoot, parameters); }`
    : `${renderTypeScriptCalculationInputs(input)}\nexport function ${fn}(inputs: Readonly<Record<string, unknown>>): Readonly<{ variant: string; payload: null }> {
  domainspecValidateCalculationInputs(inputs);
  const expression: any = ${canonicalJson(calculation.expression)};
  const branch = domainspecEvaluateExpression(expression.condition, inputs) ? expression.then : expression.else;
  return Object.freeze({ variant: branch.variant, payload: null });
}`;
  return `${header}${marker}
const domainspecRuleRoot = ${JSON.stringify(projection.root)};
const domainspecRuleProperties: Readonly<Record<string, string>> = Object.freeze(${canonicalJson(projection.properties)});
const domainspecRuleContracts: Readonly<Record<string, any>> = Object.freeze(${canonicalJson(projection.rules)});
function domainspecStable(value: unknown): string {
  if (value instanceof Set) return JSON.stringify([...value].map(domainspecStable).sort());
  if (Array.isArray(value)) return JSON.stringify(value.map(domainspecStable));
  if (value !== null && typeof value === "object") return JSON.stringify(Object.fromEntries(Object.entries(value as Record<string, unknown>).sort(([left], [right]) => left.localeCompare(right)).map(([key, child]) => [key, domainspecStable(child)])));
  return JSON.stringify(value) ?? "undefined";
}
function domainspecValue(expression: any, environment: Readonly<Record<string, unknown>>): any {
  if (expression.op === "literal") return expression.value;
  if (expression.op === "variant") return expression.selector;
  if (expression.op === "to_set") return new Set((domainspecValue(expression.value, environment) as readonly unknown[]).map(domainspecStable));
  let current: any = environment[expression.root];
  for (const property of expression.properties as readonly string[]) {
    const field = domainspecRuleProperties[property];
    if (field === undefined) throw new Error("unresolved Rule property:" + property);
    current = Array.isArray(current) ? current.map((entry) => entry?.[field]) : current?.[field];
  }
  return current;
}
function domainspecEqual(left: unknown, right: unknown): boolean { return domainspecStable(left) === domainspecStable(right); }
function domainspecCollection(value: unknown): readonly unknown[] { return value instanceof Set ? [...value] : Array.isArray(value) ? value : (() => { throw new Error("Rule quantifier requires a collection"); })(); }
function domainspecEvaluateExpression(expression: any, environment: Readonly<Record<string, unknown>>): boolean {
  if (expression.op === "all" || expression.op === "any") return expression.op === "all" ? expression.terms.every((term: any) => domainspecEvaluateExpression(term, environment)) : expression.terms.some((term: any) => domainspecEvaluateExpression(term, environment));
  if (expression.op === "not") return !domainspecEvaluateExpression(expression.term, environment);
  if (["eq", "lt", "set_equal", "contains"].includes(expression.op)) {
    const left = domainspecValue(expression.left, environment); const right = domainspecValue(expression.right, environment);
    if (expression.op === "lt") return typeof left === "number" && typeof right === "number" && left < right;
    if (expression.op === "contains") return (left instanceof Set && left.has(domainspecStable(right))) || (Array.isArray(left) && left.some((entry) => domainspecEqual(entry, right)));
    return domainspecEqual(left, right);
  }
  if (["exactly_one", "exists", "unique"].includes(expression.op)) {
    const values = domainspecCollection(domainspecValue(expression.collection, environment));
    if (expression.op === "unique") return new Set(values.map((value) => domainspecStable(domainspecValue(expression.where.left, { ...environment, [expression.binding]: value })))).size === values.length;
    const matches = values.filter((value) => domainspecEvaluateExpression(expression.where, { ...environment, [expression.binding]: value })).length;
    return expression.op === "exactly_one" ? matches === 1 : matches > 0;
  }
  if (expression.op === "rule_ref") return domainspecEvaluate(expression.selector, Object.fromEntries(expression.arguments.map((argument: any) => [argument.parameter, domainspecValue(argument.value, environment)])));
  throw new Error("unsupported Rule operator:" + String(expression.op));
}
function domainspecEvaluate(selector: string, environment: Readonly<Record<string, unknown>>): boolean {
  const contract = domainspecRuleContracts[selector];
  if (contract === undefined) throw new Error("unresolved Rule reference:" + selector);
  if (!contract.parameters.every((parameter: any) => Object.hasOwn(environment, parameter.name))) throw new Error("missing Rule parameter:" + selector);
  return domainspecEvaluateExpression(contract.expression, environment);
}
${entry}
`;
}

function renderPythonTypedRule(input: GeneratorInput, fn: string, header: string): string {
  const projection = typedRuleProjection(input);
  const closure = input.typed_closure!;
  const calculation = closure.schema_version === "domainspec.typed-calculation-closure/v1" ? closure.calculation : null;
  const marker = calculation === null ? '# domainspec-rule-semantics: "domainspec.typed-rule/v1"' : `# domainspec-calculation-semantics: "domainspec.typed-calculation/v2"\n# domainspec-typed-closure-sha256: ${JSON.stringify(closure.closure_sha256)}`;
  const entry = calculation === null
    ? `def ${fn}(parameters: dict[str, object]) -> bool:\n    return _domainspec_evaluate(_DOMAINSPEC_RULE_ROOT, parameters)`
    : `${renderPythonCalculationInputs(input)}\ndef ${fn}(inputs: dict[str, object]) -> dict[str, object]:
    _domainspec_validate_calculation_inputs(inputs)
    expression = json.loads(${JSON.stringify(canonicalJson(calculation.expression))})
    branch = expression["then"] if _domainspec_evaluate_expression(expression["condition"], inputs) else expression["else"]
    return {"variant": branch["variant"], "payload": None}`;
  return `${header}${marker}
import json

_DOMAINSPEC_RULE_ROOT = ${JSON.stringify(projection.root)}
_DOMAINSPEC_RULE_PROPERTIES = json.loads(${JSON.stringify(canonicalJson(projection.properties))})
_DOMAINSPEC_RULE_CONTRACTS = json.loads(${JSON.stringify(canonicalJson(projection.rules))})

def _domainspec_stable(value: object) -> str:
    if isinstance(value, set):
        return json.dumps(sorted(_domainspec_stable(item) for item in value), separators=(",", ":"))
    if isinstance(value, list):
        return json.dumps([_domainspec_stable(item) for item in value], separators=(",", ":"))
    if isinstance(value, dict):
        return json.dumps({key: _domainspec_stable(value[key]) for key in sorted(value)}, separators=(",", ":"))
    return json.dumps(value, separators=(",", ":"))

def _domainspec_value(expression: dict[str, object], environment: dict[str, object]) -> object:
    operation = expression["op"]
    if operation == "literal": return expression["value"]
    if operation == "variant": return expression["selector"]
    if operation == "to_set": return {_domainspec_stable(item) for item in _domainspec_value(expression["value"], environment)}
    current = environment[expression["root"]]
    for property_selector in expression["properties"]:
        field = _DOMAINSPEC_RULE_PROPERTIES[property_selector]
        current = [entry[field] for entry in current] if isinstance(current, list) else current[field]
    return current

def _domainspec_evaluate_expression(expression: dict[str, object], environment: dict[str, object]) -> bool:
    operation = expression["op"]
    if operation in ("all", "any"):
        values = (_domainspec_evaluate_expression(term, environment) for term in expression["terms"])
        return all(values) if operation == "all" else any(values)
    if operation == "not": return not _domainspec_evaluate_expression(expression["term"], environment)
    if operation in ("eq", "lt", "set_equal", "contains"):
        left = _domainspec_value(expression["left"], environment); right = _domainspec_value(expression["right"], environment)
        if operation == "lt": return isinstance(left, (int, float)) and isinstance(right, (int, float)) and left < right
        if operation == "contains": return _domainspec_stable(right) in left if isinstance(left, set) else any(_domainspec_stable(item) == _domainspec_stable(right) for item in left)
        return _domainspec_stable(left) == _domainspec_stable(right)
    if operation in ("exactly_one", "exists", "unique"):
        collection = _domainspec_value(expression["collection"], environment)
        if not isinstance(collection, (list, set, tuple)): raise ValueError("Rule quantifier requires a collection")
        if operation == "unique":
            keys = [_domainspec_stable(_domainspec_value(expression["where"]["left"], {**environment, expression["binding"]: item})) for item in collection]
            return len(set(keys)) == len(keys)
        matches = sum(1 for item in collection if _domainspec_evaluate_expression(expression["where"], {**environment, expression["binding"]: item}))
        return matches == 1 if operation == "exactly_one" else matches > 0
    if operation == "rule_ref": return _domainspec_evaluate(expression["selector"], {argument["parameter"]: _domainspec_value(argument["value"], environment) for argument in expression["arguments"]})
    raise ValueError(f"unsupported Rule operator:{operation}")

def _domainspec_evaluate(selector: str, environment: dict[str, object]) -> bool:
    contract = _DOMAINSPEC_RULE_CONTRACTS.get(selector)
    if contract is None: raise ValueError(f"unresolved Rule reference:{selector}")
    if any(parameter["name"] not in environment for parameter in contract["parameters"]): raise ValueError(f"missing Rule parameter:{selector}")
    return _domainspec_evaluate_expression(contract["expression"], environment)

${entry}
`;
}

function thinContract<T>(input: GeneratorInput, schema: string): T {
  const contract = input.body.typed_contract as { readonly schema_version?: string } | undefined;
  if (contract?.schema_version !== schema) throw new Error(`${input.kind} requires authored ${schema} semantics`);
  return contract as T;
}

function renderTypeScriptPredicateRuntime(): string {
  return `function domainspecValue(value: any, row: Readonly<Record<string, unknown>>, parameters: Readonly<Record<string, unknown>>): unknown {
  if (value.kind === "literal") return value.value;
  const source = value.kind === "field" ? row : parameters;
  if (!Object.hasOwn(source, value.name)) throw new Error("missing " + value.kind + ":" + value.name);
  return source[value.name];
}
function domainspecPredicate(predicate: any, row: Readonly<Record<string, unknown>>, parameters: Readonly<Record<string, unknown>>): boolean {
  if (predicate.op === "all" || predicate.op === "any") return predicate.op === "all" ? predicate.terms.every((term: any) => domainspecPredicate(term, row, parameters)) : predicate.terms.some((term: any) => domainspecPredicate(term, row, parameters));
  if (predicate.op === "not") return !domainspecPredicate(predicate.term, row, parameters);
  const left: any = domainspecValue(predicate.left, row, parameters); const right: any = domainspecValue(predicate.right, row, parameters);
  if (predicate.op === "eq") return Object.is(left, right);
  if ((typeof left !== "number" && typeof left !== "string") || typeof right !== typeof left) throw new Error("ordered comparison requires matching scalar values");
  if (predicate.op === "lt") return left < right;
  if (predicate.op === "lte") return left <= right;
  if (predicate.op === "gt") return left > right;
  if (predicate.op === "gte") return left >= right;
  throw new Error("unsupported predicate:" + predicate.op);
}
`;
}

function renderPythonPredicateRuntime(): string {
  return `def _domainspec_value(value: dict[str, object], row: dict[str, object], parameters: dict[str, object]) -> object:
    if value["kind"] == "literal": return value["value"]
    source = row if value["kind"] == "field" else parameters
    if value["name"] not in source: raise ValueError(f"missing {value['kind']}:{value['name']}")
    return source[value["name"]]

def _domainspec_predicate(predicate: dict[str, object], row: dict[str, object], parameters: dict[str, object]) -> bool:
    operation = predicate["op"]
    if operation in ("all", "any"):
        terms = (_domainspec_predicate(term, row, parameters) for term in predicate["terms"])
        return all(terms) if operation == "all" else any(terms)
    if operation == "not": return not _domainspec_predicate(predicate["term"], row, parameters)
    left = _domainspec_value(predicate["left"], row, parameters); right = _domainspec_value(predicate["right"], row, parameters)
    if operation == "eq": return type(left) is type(right) and left == right
    if type(left) is not type(right) or not isinstance(left, (int, str)): raise ValueError("ordered comparison requires matching scalar values")
    if operation == "lt": return left < right
    if operation == "lte": return left <= right
    if operation == "gt": return left > right
    if operation == "gte": return left >= right
    raise ValueError(f"unsupported predicate:{operation}")

`;
}

function renderTypeScriptQuery(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedQueryContract>(input, "domainspec.typed-query/v1");
  return `${header}// domainspec-query-semantics: "domainspec.typed-query/v1"
const domainspecContract: any = Object.freeze(${canonicalJson(contract)});
${renderTypeScriptPredicateRuntime()}export function ${fn}(rows: readonly Readonly<Record<string, unknown>>[], parameters: Readonly<Record<string, unknown>> = {}): readonly Readonly<Record<string, unknown>>[] {
  let selected = rows.filter((row) => domainspecContract.filter === null || domainspecPredicate(domainspecContract.filter, row, parameters));
  if (domainspecContract.order_by !== null) selected = [...selected].sort((left, right) => { const field = domainspecContract.order_by.field; const order = left[field] === right[field] ? 0 : (left[field] as any) < (right[field] as any) ? -1 : 1; return domainspecContract.order_by.direction === "asc" ? order : -order; });
  if (domainspecContract.limit !== null) selected = selected.slice(0, domainspecContract.limit);
  return Object.freeze(selected.map((row) => Object.freeze(Object.fromEntries(domainspecContract.projection.map((field: string) => [field, row[field]])))));
}
`;
}

function renderPythonQuery(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedQueryContract>(input, "domainspec.typed-query/v1");
  return `${header}# domainspec-query-semantics: "domainspec.typed-query/v1"
import json
_DOMAINSPEC_CONTRACT = json.loads(${JSON.stringify(canonicalJson(contract))})
${renderPythonPredicateRuntime()}def ${fn}(rows: list[dict[str, object]], parameters: dict[str, object] | None = None) -> list[dict[str, object]]:
    values = [row for row in rows if _DOMAINSPEC_CONTRACT["filter"] is None or _domainspec_predicate(_DOMAINSPEC_CONTRACT["filter"], row, parameters or {})]
    order = _DOMAINSPEC_CONTRACT["order_by"]
    if order is not None: values = sorted(values, key=lambda row: row[order["field"]], reverse=order["direction"] == "desc")
    if _DOMAINSPEC_CONTRACT["limit"] is not None: values = values[:_DOMAINSPEC_CONTRACT["limit"]]
    return [{field: row[field] for field in _DOMAINSPEC_CONTRACT["projection"]} for row in values]
`;
}

function rustValue(value: BackendValue): string {
  if (value.kind === "literal") return `Ok::<String, String>(${JSON.stringify(String(value.value))}.to_owned())`;
  const source = value.kind === "field" ? "row" : "parameters";
  return `domainspec_get(${source}, ${JSON.stringify(value.name)})`;
}

function rustPredicate(predicate: BackendPredicate): string {
  if (predicate.op === "all" || predicate.op === "any") {
    const operator = predicate.op === "all" ? "&&" : "||";
    return `(${predicate.terms.map((term) => `(${rustPredicate(term)})`).join(` ${operator} `)})`;
  }
  if (predicate.op === "not") return `!(${rustPredicate(predicate.term)})`;
  if (!("left" in predicate)) throw new Error("invalid backend predicate");
  return `domainspec_compare(${JSON.stringify(predicate.op)}, &(${rustValue(predicate.left)}?), &(${rustValue(predicate.right)}?))?`;
}

function renderRustPredicateRuntime(): string {
  return `use std::collections::BTreeMap;
fn domainspec_get(values: &BTreeMap<String, String>, key: &str) -> Result<String, String> { values.get(key).cloned().ok_or_else(|| format!("missing value:{}", key)) }
fn domainspec_compare(operation: &str, left: &str, right: &str) -> Result<bool, String> {
    if operation == "eq" { return Ok(left == right); }
    let left_number = left.parse::<u64>().map_err(|_| "ordered comparison requires UInt64".to_owned())?;
    let right_number = right.parse::<u64>().map_err(|_| "ordered comparison requires UInt64".to_owned())?;
    match operation { "lt" => Ok(left_number < right_number), "lte" => Ok(left_number <= right_number), "gt" => Ok(left_number > right_number), "gte" => Ok(left_number >= right_number), _ => Err("unsupported predicate".to_owned()) }
}
`;
}

function renderRustQuery(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedQueryContract>(input, "domainspec.typed-query/v1");
  const predicate = contract.filter === null ? "true" : rustPredicate(contract.filter);
  const projections = contract.projection.map((field) => `projected.insert(${JSON.stringify(field)}.to_owned(), domainspec_get(&row, ${JSON.stringify(field)})?);`).join(" ");
  const order = contract.order_by === null ? "" : `selected.sort_by(|left, right| left.get(${JSON.stringify(contract.order_by.field)}).cmp(&right.get(${JSON.stringify(contract.order_by.field)})));${contract.order_by.direction === "desc" ? " selected.reverse();" : ""}`;
  const limit = contract.limit === null ? "" : `selected.truncate(${contract.limit});`;
  return `${header}// domainspec-query-semantics: "domainspec.typed-query/v1"
${renderRustPredicateRuntime()}pub fn ${fn}(rows: &[BTreeMap<String, String>], parameters: &BTreeMap<String, String>) -> Result<Vec<BTreeMap<String, String>>, String> {
    let mut selected = Vec::new();
    for row in rows { if ${predicate} { selected.push(row.clone()); } }
    ${order} ${limit} let mut output = Vec::new(); for row in selected { let mut projected = BTreeMap::new(); ${projections} output.push(projected); } Ok(output)
}
`;
}

function calculationInputContract(input: GeneratorInput): Readonly<{ inputs: unknown; types: unknown }> {
  const closure = input.typed_closure;
  if (closure?.schema_version !== "domainspec.typed-calculation-closure/v1") throw new Error("conditional Calculation requires a bound closure");
  return { inputs: closure.calculation.inputs, types: Object.fromEntries(closure.nodes.map((node) => [node.selector, node.typed_contract])) };
}

function renderTypeScriptCalculationInputs(input: GeneratorInput): string {
  return `const domainspecCalculationTypes: any = ${canonicalJson(calculationInputContract(input))};
function domainspecValidateCalculationValue(type: any, value: any): void {
  if (type.kind === "scalar") {
    const valid = type.name === "String" ? typeof value === "string" : type.name === "Bool" ? typeof value === "boolean" : Number.isSafeInteger(value) && value >= 0;
    if (!valid) throw new Error("invalid Calculation scalar:" + type.name);
    return;
  }
  if (type.kind === "optional" && value === null) return;
  if (type.kind === "optional") return domainspecValidateCalculationValue(type.element, value);
  if (type.kind === "list" || type.kind === "set") {
    if (!Array.isArray(value)) throw new Error("Calculation collection requires an array");
    if (type.kind === "set" && new Set(value.map(domainspecStable)).size !== value.length) throw new Error("duplicate Calculation set member");
    value.forEach((child: any) => domainspecValidateCalculationValue(type.element, child)); return;
  }
  const contract = type.kind === "named" ? domainspecCalculationTypes.types[type.selector] : type;
  if (value === null || typeof value !== "object" || Array.isArray(value) || !contract) throw new Error("invalid Calculation named value");
  if (contract.schema_version === "domainspec.typed-record/v1") {
    const names = contract.properties.map((property: any) => property.name).sort();
    if (JSON.stringify(Object.keys(value).sort()) !== JSON.stringify(names)) throw new Error("Calculation record fields must match the contract");
    contract.properties.forEach((property: any) => domainspecValidateCalculationValue(property.type, value[property.name])); return;
  }
  const variant = contract.variants?.find((candidate: any) => candidate.name === value.variant);
  if (!variant || JSON.stringify(Object.keys(value).sort()) !== JSON.stringify(["payload", "variant"])) throw new Error("invalid Calculation variant");
  if (variant.payload === null) { if (value.payload !== null) throw new Error("unexpected Calculation variant payload"); }
  else domainspecValidateCalculationValue(variant.payload, value.payload);
}
function domainspecValidateCalculationInputs(inputs: Readonly<Record<string, unknown>>): void {
  if (inputs === null || typeof inputs !== "object" || Array.isArray(inputs)) throw new Error("Calculation inputs require an object");
  const names = domainspecCalculationTypes.inputs.map((parameter: any) => parameter.name).sort();
  if (JSON.stringify(Object.keys(inputs).sort()) !== JSON.stringify(names)) throw new Error("Calculation inputs must match the contract");
  domainspecCalculationTypes.inputs.forEach((parameter: any) => domainspecValidateCalculationValue(parameter.type, inputs[parameter.name]));
}`;
}

function renderPythonCalculationInputs(input: GeneratorInput): string {
  return `_DOMAINSPEC_CALCULATION_TYPES = json.loads(${JSON.stringify(canonicalJson(calculationInputContract(input)))})
def _domainspec_validate_calculation_value(type_spec: dict[str, object], value: object) -> None:
    kind = type_spec["kind"]
    if kind == "scalar":
        name = type_spec["name"]
        valid = isinstance(value, str) if name == "String" else type(value) is bool if name == "Bool" else type(value) is int and 0 <= value <= 9007199254740991
        if not valid: raise ValueError(f"invalid Calculation scalar:{name}")
        return
    if kind == "optional":
        if value is not None: _domainspec_validate_calculation_value(type_spec["element"], value)
        return
    if kind in ("list", "set"):
        if not isinstance(value, list): raise ValueError("Calculation collection requires a list")
        if kind == "set" and len({_domainspec_stable(child) for child in value}) != len(value): raise ValueError("duplicate Calculation set member")
        for child in value: _domainspec_validate_calculation_value(type_spec["element"], child)
        return
    contract = _DOMAINSPEC_CALCULATION_TYPES["types"].get(type_spec["selector"]) if kind == "named" else type_spec
    if not isinstance(value, dict) or contract is None: raise ValueError("invalid Calculation named value")
    if contract.get("schema_version") == "domainspec.typed-record/v1":
        if sorted(value) != sorted(prop["name"] for prop in contract["properties"]): raise ValueError("Calculation record fields must match the contract")
        for prop in contract["properties"]: _domainspec_validate_calculation_value(prop["type"], value[prop["name"]])
        return
    variant = next((candidate for candidate in contract.get("variants", []) if candidate["name"] == value.get("variant")), None)
    if variant is None or sorted(value) != ["payload", "variant"]: raise ValueError("invalid Calculation variant")
    if variant["payload"] is None:
        if value["payload"] is not None: raise ValueError("unexpected Calculation variant payload")
    else: _domainspec_validate_calculation_value(variant["payload"], value["payload"])

def _domainspec_validate_calculation_inputs(inputs: dict[str, object]) -> None:
    if not isinstance(inputs, dict) or sorted(inputs) != sorted(parameter["name"] for parameter in _DOMAINSPEC_CALCULATION_TYPES["inputs"]): raise ValueError("Calculation inputs must match the contract")
    for parameter in _DOMAINSPEC_CALCULATION_TYPES["inputs"]: _domainspec_validate_calculation_value(parameter["type"], inputs[parameter["name"]])
`;
}

function renderTypeScriptCalculation(input: GeneratorInput, fn: string, header: string): string {
  if (input.typed_closure?.schema_version === "domainspec.typed-calculation-closure/v1") return renderTypeScriptTypedRule(input, fn, header);
  const contract = thinContract<TypedNumericCalculationContract>(input, "domainspec.typed-calculation/v1");
  return `${header}// domainspec-calculation-semantics: "domainspec.typed-calculation/v1"
const domainspecContract: any = Object.freeze(${canonicalJson(contract)});
function domainspecNumeric(expression: any, inputs: Readonly<Record<string, number>>): number {
  if (expression.op === "literal") return expression.value;
  if (expression.op === "input") { const value = inputs[expression.name]; if (!Number.isSafeInteger(value) || value < 0) throw new Error("missing or invalid UInt64 input:" + expression.name); return value; }
  const left = domainspecNumeric(expression.left, inputs); const right = domainspecNumeric(expression.right, inputs);
  if (expression.op === "add") { const value = left + right; if (!Number.isSafeInteger(value)) throw new Error("Calculation overflow"); return value; }
  if (expression.op === "subtract") { if (left < right) throw new Error("Calculation underflow"); return left - right; }
  if (expression.op === "multiply") { const value = left * right; if (!Number.isSafeInteger(value)) throw new Error("Calculation overflow"); return value; }
  if (right === 0) throw new Error("Calculation division by zero");
  if (domainspecContract.division_rounding === "reject" && left % right !== 0) throw new Error("Calculation inexact division");
  return domainspecContract.division_rounding === "ceil" ? Math.ceil(left / right) : Math.floor(left / right);
}
export function ${fn}(inputs: Readonly<Record<string, number>>): number { return domainspecNumeric(domainspecContract.expression, inputs); }
`;
}

function renderPythonCalculation(input: GeneratorInput, fn: string, header: string): string {
  if (input.typed_closure?.schema_version === "domainspec.typed-calculation-closure/v1") return renderPythonTypedRule(input, fn, header);
  const contract = thinContract<TypedNumericCalculationContract>(input, "domainspec.typed-calculation/v1");
  return `${header}# domainspec-calculation-semantics: "domainspec.typed-calculation/v1"
import json
_DOMAINSPEC_CONTRACT = json.loads(${JSON.stringify(canonicalJson(contract))})
def _domainspec_numeric(expression: dict[str, object], inputs: dict[str, int]) -> int:
    operation = expression["op"]
    if operation == "literal": return expression["value"]
    if operation == "input":
        value = inputs.get(expression["name"])
        if type(value) is not int or value < 0: raise ValueError(f"missing or invalid UInt64 input:{expression['name']}")
        return value
    left = _domainspec_numeric(expression["left"], inputs); right = _domainspec_numeric(expression["right"], inputs)
    if operation == "add": return left + right
    if operation == "subtract":
        if left < right: raise ValueError("Calculation underflow")
        return left - right
    if operation == "multiply": return left * right
    if right == 0: raise ValueError("Calculation division by zero")
    if _DOMAINSPEC_CONTRACT["division_rounding"] == "reject" and left % right: raise ValueError("Calculation inexact division")
    return (left + right - 1) // right if _DOMAINSPEC_CONTRACT["division_rounding"] == "ceil" else left // right
def ${fn}(inputs: dict[str, int]) -> int: return _domainspec_numeric(_DOMAINSPEC_CONTRACT["expression"], inputs)
`;
}

function rustNumeric(expression: NumericExpression, rounding: TypedNumericCalculationContract["division_rounding"]): string {
  if (expression.op === "literal") return `Ok::<u64, String>(${expression.value}u64)`;
  if (expression.op === "input") return `inputs.get(${JSON.stringify(expression.name)}).copied().ok_or_else(|| "missing UInt64 input:${expression.name}".to_owned())`;
  const left = rustNumeric(expression.left, rounding); const right = rustNumeric(expression.right, rounding);
  const method = expression.op === "add" ? "checked_add" : expression.op === "subtract" ? "checked_sub" : expression.op === "multiply" ? "checked_mul" : null;
  if (method) return `(${left}?).${method}(${right}?).ok_or_else(|| "Calculation ${expression.op} range error".to_owned())`;
  return `domainspec_divide(${left}?, ${right}?, ${JSON.stringify(rounding)})`;
}

function renderRustCalculation(input: GeneratorInput, fn: string, header: string): string {
  if (input.typed_closure?.schema_version === "domainspec.typed-calculation-closure/v1") return `${header}// domainspec-calculation-semantics: "domainspec.typed-calculation/v2"\n${renderTypedRustCalculation(input.typed_closure)}`;
  const contract = thinContract<TypedNumericCalculationContract>(input, "domainspec.typed-calculation/v1");
  return `${header}// domainspec-calculation-semantics: "domainspec.typed-calculation/v1"
use std::collections::BTreeMap;
fn domainspec_divide(left: u64, right: u64, rounding: &str) -> Result<u64, String> { if right == 0 { return Err("Calculation division by zero".to_owned()); } if rounding == "reject" && left % right != 0 { return Err("Calculation inexact division".to_owned()); } Ok(if rounding == "ceil" { left.div_ceil(right) } else { left / right }) }
pub fn ${fn}(inputs: &BTreeMap<String, u64>) -> Result<u64, String> { ${rustNumeric(contract.expression, contract.division_rounding)} }
`;
}

function renderTypeScriptMapping(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedMappingContract>(input, "domainspec.typed-mapping/v1");
  return `${header}// domainspec-mapping-semantics: "domainspec.typed-mapping/v1"
const domainspecContract: any = Object.freeze(${canonicalJson(contract)});
export function ${fn}(source: Readonly<Record<string, unknown>>): Readonly<Record<string, unknown>> {
  const target: Record<string, unknown> = {};
  for (const field of domainspecContract.fields) { if (field.source !== null && Object.hasOwn(source, field.source)) target[field.target] = source[field.source]; else if (field.default !== null) target[field.target] = field.default.value; else if (domainspecContract.total) throw new Error("missing Mapping field:" + field.target); }
  return Object.freeze(target);
}
`;
}

function renderPythonMapping(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedMappingContract>(input, "domainspec.typed-mapping/v1");
  return `${header}# domainspec-mapping-semantics: "domainspec.typed-mapping/v1"
import json
_DOMAINSPEC_CONTRACT = json.loads(${JSON.stringify(canonicalJson(contract))})
def ${fn}(source: dict[str, object]) -> dict[str, object]:
    target = {}
    for field in _DOMAINSPEC_CONTRACT["fields"]:
        if field["source"] is not None and field["source"] in source: target[field["target"]] = source[field["source"]]
        elif field["default"] is not None: target[field["target"]] = field["default"]["value"]
        elif _DOMAINSPEC_CONTRACT["total"]: raise ValueError(f"missing Mapping field:{field['target']}")
    return target
`;
}

function renderRustMapping(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedMappingContract>(input, "domainspec.typed-mapping/v1");
  const fields = contract.fields.map((field) => {
    const fallback = field.default === null ? "None" : `Some(${JSON.stringify(String(field.default.value))}.to_owned())`;
    const source = field.source === null ? "None" : `source.get(${JSON.stringify(field.source)}).cloned()`;
    return `if let Some(value) = (${source}).or(${fallback}) { target.insert(${JSON.stringify(field.target)}.to_owned(), value); } else if ${contract.total} { return Err(${JSON.stringify(`missing Mapping field:${field.target}`)}.to_owned()); }`;
  }).join(" ");
  return `${header}// domainspec-mapping-semantics: "domainspec.typed-mapping/v1"
use std::collections::BTreeMap;
pub fn ${fn}(source: &BTreeMap<String, String>) -> Result<BTreeMap<String, String>, String> { let mut target = BTreeMap::new(); ${fields} Ok(target) }
`;
}

function renderTypeScriptPolicy(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedPolicyContract>(input, "domainspec.typed-policy/v1");
  return `${header}// domainspec-policy-semantics: "domainspec.typed-policy/v1"
const domainspecContract: any = Object.freeze(${canonicalJson(contract)});
${renderTypeScriptPredicateRuntime()}export function ${fn}(parameters: Readonly<Record<string, unknown>>): string { for (const candidate of domainspecContract.cases) if (domainspecPredicate(candidate.when, {}, parameters)) return candidate.target; return domainspecContract.default_target; }
`;
}

function renderPythonPolicy(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedPolicyContract>(input, "domainspec.typed-policy/v1");
  return `${header}# domainspec-policy-semantics: "domainspec.typed-policy/v1"
import json
_DOMAINSPEC_CONTRACT = json.loads(${JSON.stringify(canonicalJson(contract))})
${renderPythonPredicateRuntime()}def ${fn}(parameters: dict[str, object]) -> str:
    for candidate in _DOMAINSPEC_CONTRACT["cases"]:
        if _domainspec_predicate(candidate["when"], {}, parameters): return candidate["target"]
    return _DOMAINSPEC_CONTRACT["default_target"]
`;
}

function renderRustPolicy(input: GeneratorInput, fn: string, header: string): string {
  const contract = thinContract<TypedPolicyContract>(input, "domainspec.typed-policy/v1");
  const cases = contract.cases.map((candidate) => `if ${rustPredicate(candidate.when)} { return Ok(${JSON.stringify(candidate.target)}.to_owned()); }`).join(" ");
  return `${header}// domainspec-policy-semantics: "domainspec.typed-policy/v1"
${renderRustPredicateRuntime()}pub fn ${fn}(parameters: &BTreeMap<String, String>) -> Result<String, String> { let row: &BTreeMap<String, String> = &BTreeMap::new(); ${cases} Ok(${JSON.stringify(contract.default_target)}.to_owned()) }
`;
}

function workflowOperationIds(input: GeneratorInput): readonly string[] {
  return Object.freeze([...new Set(input.relationships
    .filter((relationship) => relationship.relationship === "orchestrates"
      && relationship.source.node_id === input.node_id
      && relationship.source.kind === "Workflow"
      && relationship.target.kind === "Operation")
    .map((relationship) => relationship.target.node_id))]);
}

function renderTypeScriptWorkflow(input: GeneratorInput, name: string, fn: string, header: string): string {
  const body = input.body;
  return `${header}// domainspec-workflow-recovery-results: ["not-required","recovery-required"]
// domainspec-recovery-intent-statuses: ["required","satisfied","unresolved"]
// domainspec-workflow-compensation-execution: false
// domainspec-compensation-contract: "forward-recovery-operation/v2"
// domainspec-compensation-order: "explicit-dependency-graph-with-reverse-completion-default"
// domainspec-compensation-executor-owner: "external-runtime"
// domainspec-compensation-operation-role: "Operation"
export const ${name}Steps = Object.freeze(${JSON.stringify(strings(body.steps))});
export const ${name}Compensations = Object.freeze(${JSON.stringify(strings(body.compensations))});
export const ${name}CompensationDependencies: readonly string[] = Object.freeze(${JSON.stringify(strings(body.compensation_dependencies))});
export const ${name}OrchestratedOperationIds: readonly string[] = Object.freeze(${JSON.stringify(workflowOperationIds(input))});
export type ${name}Digest = (material: string) => string;
export type ${name}RecoveryPlanEntry = Readonly<{ planOccurrenceId: string; stepId: string; operationId: string; dependsOn: readonly string[]; invocationIdentity: string }>;
export type ${name}RecoveryIntent = Readonly<{ schemaVersion: "domainspec.workflow-recovery-intent/v2"; intentId: string; workflowId: ${JSON.stringify(input.node_id)}; workflowExecutionId: string; failureOccurrenceId: string; failedStepId: string; completedStepJournalDigest: string; planDigest: string; semanticStatus: "required"; plan: readonly ${name}RecoveryPlanEntry[] }>;
export type ${name}RecoveryDecision = Readonly<{ schemaVersion: "domainspec.workflow-recovery-decision/v1"; workflowEvaluationResult: "not-required" | "recovery-required"; recoveryIntent: ${name}RecoveryIntent | null }>;
function ${fn}RequireIdentity(value: string, label: string): void {
  if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(value)) throw new Error("invalid recovery identity:" + label + ":" + value);
}
function ${fn}Digest(material: string, digest: ${name}Digest): string {
  const value = digest(material);
  if (!/^[0-9a-f]{64}$/.test(value)) throw new Error("digest callback must return lowercase SHA-256 hex");
  return value;
}
function ${fn}PlanMaterial(plan: readonly Omit<${name}RecoveryPlanEntry, "invocationIdentity">[]): string {
  return ["domainspec.workflow-recovery-plan/v1", ...plan.map((entry) => [entry.planOccurrenceId, entry.stepId, entry.operationId, entry.dependsOn.join(",")].join("|"))].join("\\n");
}
function ${fn}InvocationIdentity(intentId: string, planDigest: string, operationId: string, planOccurrenceId: string, digest: ${name}Digest): string {
  return ${fn}Digest(["domainspec.compensation-invocation-identity/v1", intentId, planDigest, operationId, planOccurrenceId].join("\\n"), digest);
}
export function plan${name}Recovery(completedStepIds: readonly string[], failedStepId: string, workflowExecutionId: string, failureOccurrenceId: string, digest: ${name}Digest): ${name}RecoveryDecision {
  ${fn}RequireIdentity(workflowExecutionId, "workflowExecutionId");
  ${fn}RequireIdentity(failureOccurrenceId, "failureOccurrenceId");
  ${fn}RequireIdentity(failedStepId, "failedStepId");
  if (new Set(completedStepIds).size !== completedStepIds.length) throw new Error("completed step IDs must be unique");
  const selected: Array<{ planOccurrenceId: string; stepId: string; operationId: string; dependencyOperationIds: readonly string[] }> = [];
  completedStepIds.forEach((stepId, completionIndex) => {
    ${fn}RequireIdentity(stepId, "completedStepId");
    const index = ${name}Steps.indexOf(stepId);
    if (index < 0) throw new Error("unknown completed step:" + stepId);
    const operationId = ${name}Compensations[index] ?? "none";
    if (operationId === "none") return;
    ${fn}RequireIdentity(operationId, "recoveryOperationId");
    if (!${name}OrchestratedOperationIds.includes(operationId)) throw new Error("recovery Operation is outside Workflow relation set:" + operationId);
    const dependencyOperationIds = ${name}CompensationDependencies.filter((entry) => entry.startsWith(operationId + ":depends-on:")).map((entry) => {
      const parts = entry.split(":depends-on:");
      if (parts.length !== 2 || !parts[1]) throw new Error("invalid compensation dependency:" + entry);
      return parts[1];
    });
    selected.push(Object.freeze({ planOccurrenceId: stepId + "-" + operationId + "-" + (completionIndex + 1), stepId, operationId, dependencyOperationIds: Object.freeze(dependencyOperationIds) }));
  });
  selected.reverse();
  if (selected.length === 0) return Object.freeze({ schemaVersion: "domainspec.workflow-recovery-decision/v1", workflowEvaluationResult: "not-required", recoveryIntent: null });
  const pending = selected.map((entry) => Object.freeze({
    planOccurrenceId: entry.planOccurrenceId,
    stepId: entry.stepId,
    operationId: entry.operationId,
    dependsOn: Object.freeze(entry.dependencyOperationIds.map((dependency) => {
      const occurrences = selected.filter(({ operationId }) => operationId === dependency);
      if (dependency === entry.operationId || occurrences.length !== 1) throw new Error("invalid or ambiguous compensation dependency:" + entry.operationId + ":" + dependency);
      return occurrences[0]!.planOccurrenceId;
    })),
  }));
  const ordered: Array<(typeof pending)[number]> = [];
  const remaining = [...pending];
  const emitted = new Set<string>();
  while (remaining.length > 0) {
    const index = remaining.findIndex((entry) => entry.dependsOn.every((dependency) => emitted.has(dependency)));
    if (index < 0) throw new Error("cyclic compensation dependency");
    const [next] = remaining.splice(index, 1);
    if (!next) throw new Error("missing recovery plan entry");
    ordered.push(next);
    emitted.add(next.planOccurrenceId);
  }
  const completedStepJournalDigest = ${fn}Digest(["domainspec.workflow-completed-step-journal/v1", ...completedStepIds].join("\\n"), digest);
  const planDigest = ${fn}Digest(${fn}PlanMaterial(ordered), digest);
  const intentId = ${fn}Digest(["domainspec.workflow-recovery-intent/v2", workflowExecutionId, failureOccurrenceId, failedStepId, completedStepJournalDigest, planDigest].join("\\n"), digest);
  const plan = Object.freeze(ordered.map((entry) => Object.freeze({ ...entry, invocationIdentity: ${fn}InvocationIdentity(intentId, planDigest, entry.operationId, entry.planOccurrenceId, digest) })));
  return Object.freeze({ schemaVersion: "domainspec.workflow-recovery-decision/v1", workflowEvaluationResult: "recovery-required", recoveryIntent: Object.freeze({ schemaVersion: "domainspec.workflow-recovery-intent/v2", intentId, workflowId: ${JSON.stringify(input.node_id)}, workflowExecutionId, failureOccurrenceId, failedStepId, completedStepJournalDigest, planDigest, semanticStatus: "required", plan }) });
}
export type ${name}Outcome = Readonly<{ ok: boolean; completed: readonly string[]; failedStep: string | null; workflowEvaluationResult: "not-required" | "recovery-required"; recoveryIntent: ${name}RecoveryIntent | null; compensationExecution: false; directEffectsExecuted: readonly string[] }>;
export async function ${fn}(run: (step: string) => Promise<void>, compensate: (operationId: string) => Promise<void>, workflowExecutionId: string, failureOccurrenceId: string, digest: ${name}Digest): Promise<${name}Outcome> {
  void compensate;
  const completed: string[] = [];
  for (const step of ${name}Steps) {
    try { await run(step); completed.push(step); }
    catch {
      const decision = plan${name}Recovery(completed, step, workflowExecutionId, failureOccurrenceId, digest);
      return Object.freeze({ ok: false, completed: Object.freeze([...completed]), failedStep: step, workflowEvaluationResult: decision.workflowEvaluationResult, recoveryIntent: decision.recoveryIntent, compensationExecution: false, directEffectsExecuted: Object.freeze([] as string[]) });
    }
  }
  return Object.freeze({ ok: true, completed: Object.freeze([...completed]), failedStep: null, workflowEvaluationResult: "not-required", recoveryIntent: null, compensationExecution: false, directEffectsExecuted: Object.freeze([] as string[]) });
}
export type ${name}RecoveryBinding = Readonly<{ workflowId: ${JSON.stringify(input.node_id)}; operationId: string; failureContinuation: "retry" | "escalate" | "terminal-failure"; invoke: (invocationIdentity: string) => Promise<Readonly<{ ok: true }> | Readonly<{ ok: false; reason: string }>> }>;
export type ${name}RecoveryInvocationReport = Readonly<{ schemaVersion: "domainspec.workflow-recovery-in-process-report/v1"; outcome: "succeeded" | "failed"; executedPlanOccurrenceIds: readonly string[]; failedPlanOccurrenceId: string | null; failureContinuation: "retry" | "escalate" | "terminal-failure" | null; reason: string | null; recoveryIntentSemanticStatus: "required"; durableTerminalDisposition: null }>;
function verify${name}RecoveryIntent(intent: ${name}RecoveryIntent, digest: ${name}Digest): void {
  if (intent.semanticStatus !== "required") throw new Error("Recovery Intent is not executable");
  if (intent.workflowId !== ${JSON.stringify(input.node_id)}) throw new Error("Recovery Intent Workflow mismatch");
  const emitted = new Set<string>();
  const planForDigest: Array<Omit<${name}RecoveryPlanEntry, "invocationIdentity">> = [];
  for (const entry of intent.plan) {
    if (!${name}OrchestratedOperationIds.includes(entry.operationId)) throw new Error("recovery target is outside Workflow relation set:" + entry.operationId);
    if (emitted.has(entry.planOccurrenceId) || entry.dependsOn.some((dependency) => !emitted.has(dependency))) throw new Error("invalid recovery plan order");
    emitted.add(entry.planOccurrenceId);
    planForDigest.push(Object.freeze({ planOccurrenceId: entry.planOccurrenceId, stepId: entry.stepId, operationId: entry.operationId, dependsOn: entry.dependsOn }));
  }
  const observedPlanDigest = ${fn}Digest(${fn}PlanMaterial(planForDigest), digest);
  if (observedPlanDigest !== intent.planDigest) throw new Error("Recovery Intent plan digest mismatch");
  const observedIntentId = ${fn}Digest(["domainspec.workflow-recovery-intent/v2", intent.workflowExecutionId, intent.failureOccurrenceId, intent.failedStepId, intent.completedStepJournalDigest, intent.planDigest].join("\\n"), digest);
  if (observedIntentId !== intent.intentId) throw new Error("Recovery Intent identity mismatch");
  for (const entry of intent.plan) if (entry.invocationIdentity !== ${fn}InvocationIdentity(intent.intentId, intent.planDigest, entry.operationId, entry.planOccurrenceId, digest)) throw new Error("Recovery Intent invocation identity mismatch:" + entry.planOccurrenceId);
}
export async function execute${name}Recovery(intent: ${name}RecoveryIntent, bindings: readonly ${name}RecoveryBinding[], digest: ${name}Digest): Promise<${name}RecoveryInvocationReport> {
  verify${name}RecoveryIntent(intent, digest);
  const requiredOperationIds = new Set(intent.plan.map(({ operationId }) => operationId));
  const registry = new Map<string, ${name}RecoveryBinding>();
  for (const binding of bindings) {
    if (!${name}OrchestratedOperationIds.includes(binding.operationId)) throw new Error("binding is outside Workflow relation set:" + binding.operationId);
    if (binding.workflowId !== intent.workflowId) throw new Error("binding Workflow mismatch:" + binding.operationId);
    if (!requiredOperationIds.has(binding.operationId)) throw new Error("undeclared recovery binding:" + binding.operationId);
    if (registry.has(binding.operationId)) throw new Error("duplicate recovery binding:" + binding.operationId);
    registry.set(binding.operationId, binding);
  }
  for (const operationId of requiredOperationIds) if (!registry.has(operationId)) throw new Error("missing recovery Operation:" + operationId);
  const executed: string[] = [];
  for (const entry of intent.plan) {
    const binding = registry.get(entry.operationId)!;
    let result: Awaited<ReturnType<${name}RecoveryBinding["invoke"]>>;
    try { result = await binding.invoke(entry.invocationIdentity); }
    catch (error) { result = Object.freeze({ ok: false, reason: error instanceof Error ? error.message : "recovery-operation-threw" }); }
    if (!result.ok) return Object.freeze({ schemaVersion: "domainspec.workflow-recovery-in-process-report/v1", outcome: "failed", executedPlanOccurrenceIds: Object.freeze([...executed]), failedPlanOccurrenceId: entry.planOccurrenceId, failureContinuation: binding.failureContinuation, reason: result.reason, recoveryIntentSemanticStatus: "required", durableTerminalDisposition: null });
    executed.push(entry.planOccurrenceId);
  }
  return Object.freeze({ schemaVersion: "domainspec.workflow-recovery-in-process-report/v1", outcome: "succeeded", executedPlanOccurrenceIds: Object.freeze(executed), failedPlanOccurrenceId: null, failureContinuation: null, reason: null, recoveryIntentSemanticStatus: "required", durableTerminalDisposition: null });
}
`;
}

function renderPythonWorkflow(input: GeneratorInput, name: string, fn: string, header: string): string {
  const body = input.body;
  const constant = name.toUpperCase();
  return `${header}# domainspec-workflow-recovery-results: ["not-required","recovery-required"]
# domainspec-recovery-intent-statuses: ["required","satisfied","unresolved"]
# domainspec-workflow-compensation-execution: false
# domainspec-compensation-contract: "forward-recovery-operation/v2"
# domainspec-compensation-order: "explicit-dependency-graph-with-reverse-completion-default"
# domainspec-compensation-executor-owner: "external-runtime"
# domainspec-compensation-operation-role: "Operation"
${constant}_STEPS = tuple(${JSON.stringify(strings(body.steps))})
${constant}_COMPENSATIONS = tuple(${JSON.stringify(strings(body.compensations))})
${constant}_COMPENSATION_DEPENDENCIES = tuple(${JSON.stringify(strings(body.compensation_dependencies))})
${constant}_ORCHESTRATED_OPERATION_IDS = tuple(${JSON.stringify(workflowOperationIds(input))})

def _${fn}_require_identity(value: str, label: str) -> None:
    if not value or not value[0].islower() or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in value) or "--" in value or value.endswith("-"):
        raise ValueError("invalid recovery identity:" + label + ":" + value)

def _${fn}_digest(material: str, digest) -> str:
    value = digest(material)
    if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError("digest callback must return lowercase SHA-256 hex")
    return value

def _${fn}_plan_material(plan: list[dict[str, object]]) -> str:
    rows = ["domainspec.workflow-recovery-plan/v1"]
    rows.extend("|".join((str(entry["plan_occurrence_id"]), str(entry["step_id"]), str(entry["operation_id"]), ",".join(str(value) for value in entry["depends_on"]))) for entry in plan)
    return "\\n".join(rows)

def _${fn}_invocation_identity(intent_id: str, plan_digest: str, operation_id: str, plan_occurrence_id: str, digest) -> str:
    return _${fn}_digest("\\n".join(("domainspec.compensation-invocation-identity/v1", intent_id, plan_digest, operation_id, plan_occurrence_id)), digest)

def plan_${fn}_recovery(completed_step_ids: list[str], failed_step_id: str, workflow_execution_id: str, failure_occurrence_id: str, digest) -> dict[str, object]:
    _${fn}_require_identity(workflow_execution_id, "workflow_execution_id")
    _${fn}_require_identity(failure_occurrence_id, "failure_occurrence_id")
    _${fn}_require_identity(failed_step_id, "failed_step_id")
    if len(set(completed_step_ids)) != len(completed_step_ids):
        raise ValueError("completed step IDs must be unique")
    selected: list[dict[str, object]] = []
    for completion_index, step_id in enumerate(completed_step_ids):
        _${fn}_require_identity(step_id, "completed_step_id")
        if step_id not in ${constant}_STEPS:
            raise ValueError("unknown completed step:" + step_id)
        index = ${constant}_STEPS.index(step_id)
        operation_id = ${constant}_COMPENSATIONS[index] if index < len(${constant}_COMPENSATIONS) else "none"
        if operation_id == "none":
            continue
        _${fn}_require_identity(operation_id, "recovery_operation_id")
        if operation_id not in ${constant}_ORCHESTRATED_OPERATION_IDS:
            raise ValueError("recovery Operation is outside Workflow relation set:" + operation_id)
        prefix = operation_id + ":depends-on:"
        dependency_operation_ids = [entry[len(prefix):] for entry in ${constant}_COMPENSATION_DEPENDENCIES if entry.startswith(prefix)]
        selected.append({"plan_occurrence_id": step_id + "-" + operation_id + "-" + str(completion_index + 1), "step_id": step_id, "operation_id": operation_id, "dependency_operation_ids": dependency_operation_ids})
    selected.reverse()
    if not selected:
        return {"schema_version": "domainspec.workflow-recovery-decision/v1", "workflow_evaluation_result": "not-required", "recovery_intent": None}
    pending: list[dict[str, object]] = []
    for entry in selected:
        depends_on: list[str] = []
        for dependency in entry["dependency_operation_ids"]:
            occurrences = [candidate for candidate in selected if candidate["operation_id"] == dependency]
            if dependency == entry["operation_id"] or len(occurrences) != 1:
                raise ValueError("invalid or ambiguous compensation dependency:" + str(entry["operation_id"]) + ":" + str(dependency))
            depends_on.append(str(occurrences[0]["plan_occurrence_id"]))
        pending.append({"plan_occurrence_id": entry["plan_occurrence_id"], "step_id": entry["step_id"], "operation_id": entry["operation_id"], "depends_on": depends_on})
    ordered: list[dict[str, object]] = []
    emitted: set[str] = set()
    while pending:
        index = next((index for index, entry in enumerate(pending) if all(str(dependency) in emitted for dependency in entry["depends_on"])), -1)
        if index < 0:
            raise ValueError("cyclic compensation dependency")
        next_entry = pending.pop(index)
        ordered.append(next_entry)
        emitted.add(str(next_entry["plan_occurrence_id"]))
    completed_step_journal_digest = _${fn}_digest("\\n".join(("domainspec.workflow-completed-step-journal/v1", *completed_step_ids)), digest)
    plan_digest = _${fn}_digest(_${fn}_plan_material(ordered), digest)
    intent_id = _${fn}_digest("\\n".join(("domainspec.workflow-recovery-intent/v2", workflow_execution_id, failure_occurrence_id, failed_step_id, completed_step_journal_digest, plan_digest)), digest)
    plan = [{**entry, "invocation_identity": _${fn}_invocation_identity(intent_id, plan_digest, str(entry["operation_id"]), str(entry["plan_occurrence_id"]), digest)} for entry in ordered]
    return {"schema_version": "domainspec.workflow-recovery-decision/v1", "workflow_evaluation_result": "recovery-required", "recovery_intent": {"schema_version": "domainspec.workflow-recovery-intent/v2", "intent_id": intent_id, "workflow_id": ${JSON.stringify(input.node_id)}, "workflow_execution_id": workflow_execution_id, "failure_occurrence_id": failure_occurrence_id, "failed_step_id": failed_step_id, "completed_step_journal_digest": completed_step_journal_digest, "plan_digest": plan_digest, "semantic_status": "required", "plan": plan}}

def ${fn}(run, compensate, workflow_execution_id: str, failure_occurrence_id: str, digest) -> dict[str, object]:
    _ = compensate
    completed: list[str] = []
    for step in ${constant}_STEPS:
        try:
            run(step)
            completed.append(step)
        except Exception:
            decision = plan_${fn}_recovery(completed, step, workflow_execution_id, failure_occurrence_id, digest)
            return {"ok": False, "completed": completed, "failed_step": step, "workflow_evaluation_result": decision["workflow_evaluation_result"], "recovery_intent": decision["recovery_intent"], "compensation_execution": False, "direct_effects_executed": []}
    return {"ok": True, "completed": completed, "failed_step": None, "workflow_evaluation_result": "not-required", "recovery_intent": None, "compensation_execution": False, "direct_effects_executed": []}

def _verify_${fn}_recovery_intent(intent: dict[str, object], digest) -> None:
    if intent["semantic_status"] != "required" or intent["workflow_id"] != ${JSON.stringify(input.node_id)}:
        raise ValueError("Recovery Intent is not executable for this Workflow")
    plan = list(intent["plan"])
    emitted: set[str] = set()
    plan_for_digest: list[dict[str, object]] = []
    for entry in plan:
        operation_id = str(entry["operation_id"])
        occurrence_id = str(entry["plan_occurrence_id"])
        if operation_id not in ${constant}_ORCHESTRATED_OPERATION_IDS:
            raise ValueError("recovery target is outside Workflow relation set:" + operation_id)
        if occurrence_id in emitted or any(str(dependency) not in emitted for dependency in entry["depends_on"]):
            raise ValueError("invalid recovery plan order")
        emitted.add(occurrence_id)
        plan_for_digest.append({"plan_occurrence_id": occurrence_id, "step_id": entry["step_id"], "operation_id": operation_id, "depends_on": entry["depends_on"]})
    if _${fn}_digest(_${fn}_plan_material(plan_for_digest), digest) != intent["plan_digest"]:
        raise ValueError("Recovery Intent plan digest mismatch")
    observed_intent_id = _${fn}_digest("\\n".join(("domainspec.workflow-recovery-intent/v2", str(intent["workflow_execution_id"]), str(intent["failure_occurrence_id"]), str(intent["failed_step_id"]), str(intent["completed_step_journal_digest"]), str(intent["plan_digest"]))), digest)
    if observed_intent_id != intent["intent_id"]:
        raise ValueError("Recovery Intent identity mismatch")
    for entry in plan:
        expected = _${fn}_invocation_identity(str(intent["intent_id"]), str(intent["plan_digest"]), str(entry["operation_id"]), str(entry["plan_occurrence_id"]), digest)
        if entry["invocation_identity"] != expected:
            raise ValueError("Recovery Intent invocation identity mismatch")

def execute_${fn}_recovery(intent: dict[str, object], bindings: list[dict[str, object]], digest) -> dict[str, object]:
    _verify_${fn}_recovery_intent(intent, digest)
    plan = list(intent["plan"])
    required_operation_ids = {str(entry["operation_id"]) for entry in plan}
    registry: dict[str, dict[str, object]] = {}
    for binding in bindings:
        operation_id = str(binding["operation_id"])
        if operation_id not in ${constant}_ORCHESTRATED_OPERATION_IDS:
            raise ValueError("binding is outside Workflow relation set:" + operation_id)
        if binding["workflow_id"] != intent["workflow_id"]:
            raise ValueError("binding Workflow mismatch:" + operation_id)
        if operation_id not in required_operation_ids:
            raise ValueError("undeclared recovery binding:" + operation_id)
        if operation_id in registry:
            raise ValueError("duplicate recovery binding:" + operation_id)
        registry[operation_id] = binding
    for operation_id in required_operation_ids:
        if operation_id not in registry:
            raise ValueError("missing recovery Operation:" + operation_id)
    executed: list[str] = []
    for entry in plan:
        operation_id = str(entry["operation_id"])
        binding = registry[operation_id]
        try:
            result = binding["invoke"](str(entry["invocation_identity"]))
        except Exception as error:
            result = {"ok": False, "reason": str(error) or "recovery-operation-threw"}
        if not result["ok"]:
            return {"schema_version": "domainspec.workflow-recovery-in-process-report/v1", "outcome": "failed", "executed_plan_occurrence_ids": executed, "failed_plan_occurrence_id": entry["plan_occurrence_id"], "failure_continuation": binding["failure_continuation"], "reason": result.get("reason", "recovery-operation-failed"), "recovery_intent_semantic_status": "required", "durable_terminal_disposition": None}
        executed.append(str(entry["plan_occurrence_id"]))
    return {"schema_version": "domainspec.workflow-recovery-in-process-report/v1", "outcome": "succeeded", "executed_plan_occurrence_ids": executed, "failed_plan_occurrence_id": None, "failure_continuation": None, "reason": None, "recovery_intent_semantic_status": "required", "durable_terminal_disposition": None}
`;
}

function renderRustWorkflow(input: GeneratorInput, name: string, fn: string, header: string): string {
  const body = input.body;
  const constant = snake(name).toUpperCase();
  return `${header}// domainspec-workflow-recovery-results: ["not-required","recovery-required"]
// domainspec-recovery-intent-statuses: ["required","satisfied","unresolved"]
// domainspec-workflow-compensation-execution: false
// domainspec-compensation-contract: "forward-recovery-operation/v2"
// domainspec-compensation-order: "explicit-dependency-graph-with-reverse-completion-default"
// domainspec-compensation-executor-owner: "external-runtime"
// domainspec-compensation-operation-role: "Operation"
use std::collections::BTreeSet;
pub const ${constant}_STEPS: &[&str] = ${rustSlice(strings(body.steps))};
pub const ${constant}_COMPENSATIONS: &[&str] = ${rustSlice(strings(body.compensations))};
pub const ${constant}_COMPENSATION_DEPENDENCIES: &[&str] = ${rustSlice(strings(body.compensation_dependencies))};
pub const ${constant}_ORCHESTRATED_OPERATION_IDS: &[&str] = ${rustSlice(workflowOperationIds(input))};
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ${name}RecoveryPlanEntry { pub plan_occurrence_id: String, pub step_id: String, pub operation_id: String, pub depends_on: Vec<String>, pub invocation_identity: String }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ${name}RecoveryIntent { pub schema_version: &'static str, pub intent_id: String, pub workflow_id: &'static str, pub workflow_execution_id: String, pub failure_occurrence_id: String, pub failed_step_id: String, pub completed_step_journal_digest: String, pub plan_digest: String, pub semantic_status: &'static str, pub plan: Vec<${name}RecoveryPlanEntry> }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ${name}RecoveryDecision { pub schema_version: &'static str, pub workflow_evaluation_result: &'static str, pub recovery_intent: Option<${name}RecoveryIntent> }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ${name}Outcome { pub ok: bool, pub completed: Vec<String>, pub failed_step: Option<String>, pub workflow_evaluation_result: &'static str, pub recovery_intent: Option<${name}RecoveryIntent>, pub compensation_execution: bool, pub direct_effects_executed: Vec<String> }
fn ${fn}_identity_valid(value: &str) -> bool {
    let bytes = value.as_bytes();
    !bytes.is_empty() && bytes[0].is_ascii_lowercase() && bytes.iter().all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || *byte == b'-') && !value.contains("--") && !value.ends_with('-')
}
fn ${fn}_digest(material: &str, digest: &impl Fn(&str) -> String) -> Result<String, &'static str> {
    let value = digest(material);
    if value.len() != 64 || !value.bytes().all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte)) { return Err("digest callback must return lowercase SHA-256 hex"); }
    Ok(value)
}
fn ${fn}_plan_material(plan: &[${name}RecoveryPlanEntry]) -> String {
    let mut rows = vec!["domainspec.workflow-recovery-plan/v1".to_owned()];
    rows.extend(plan.iter().map(|entry| [&entry.plan_occurrence_id, &entry.step_id, &entry.operation_id, &entry.depends_on.join(",")].iter().map(|value| value.as_str()).collect::<Vec<_>>().join("|")));
    rows.join("\\n")
}
fn ${fn}_invocation_identity(intent_id: &str, plan_digest: &str, operation_id: &str, plan_occurrence_id: &str, digest: &impl Fn(&str) -> String) -> Result<String, &'static str> {
    ${fn}_digest(&["domainspec.compensation-invocation-identity/v1", intent_id, plan_digest, operation_id, plan_occurrence_id].join("\\n"), digest)
}
pub fn plan_${fn}_recovery(completed_step_ids: &[String], failed_step_id: &str, workflow_execution_id: &str, failure_occurrence_id: &str, digest: &impl Fn(&str) -> String) -> Result<${name}RecoveryDecision, &'static str> {
    if !${fn}_identity_valid(workflow_execution_id) || !${fn}_identity_valid(failure_occurrence_id) || !${fn}_identity_valid(failed_step_id) { return Err("invalid recovery identity"); }
    let completed_set: BTreeSet<&str> = completed_step_ids.iter().map(String::as_str).collect();
    if completed_set.len() != completed_step_ids.len() { return Err("completed step IDs must be unique"); }
    #[derive(Clone)]
    struct Selected { plan_occurrence_id: String, step_id: String, operation_id: String, dependency_operation_ids: Vec<String> }
    let mut selected: Vec<Selected> = Vec::new();
    for (completion_index, step_id) in completed_step_ids.iter().enumerate() {
        if !${fn}_identity_valid(step_id) { return Err("invalid completed step identity"); }
        let index = ${constant}_STEPS.iter().position(|candidate| *candidate == step_id).ok_or("unknown completed step")?;
        let operation_id = ${constant}_COMPENSATIONS.get(index).copied().unwrap_or("none");
        if operation_id == "none" { continue; }
        if !${fn}_identity_valid(operation_id) || !${constant}_ORCHESTRATED_OPERATION_IDS.contains(&operation_id) { return Err("recovery Operation is outside Workflow relation set"); }
        let prefix = operation_id.to_owned() + ":depends-on:";
        let dependency_operation_ids = ${constant}_COMPENSATION_DEPENDENCIES.iter().filter_map(|entry| entry.strip_prefix(&prefix).map(str::to_owned)).collect();
        selected.push(Selected { plan_occurrence_id: step_id.to_owned() + "-" + operation_id + "-" + &(completion_index + 1).to_string(), step_id: step_id.clone(), operation_id: operation_id.to_owned(), dependency_operation_ids });
    }
    selected.reverse();
    if selected.is_empty() { return Ok(${name}RecoveryDecision { schema_version: "domainspec.workflow-recovery-decision/v1", workflow_evaluation_result: "not-required", recovery_intent: None }); }
    let mut pending: Vec<${name}RecoveryPlanEntry> = Vec::new();
    for entry in &selected {
        let mut depends_on = Vec::new();
        for dependency in &entry.dependency_operation_ids {
            let occurrences: Vec<&Selected> = selected.iter().filter(|candidate| &candidate.operation_id == dependency).collect();
            if dependency == &entry.operation_id || occurrences.len() != 1 { return Err("invalid or ambiguous compensation dependency"); }
            depends_on.push(occurrences[0].plan_occurrence_id.clone());
        }
        pending.push(${name}RecoveryPlanEntry { plan_occurrence_id: entry.plan_occurrence_id.clone(), step_id: entry.step_id.clone(), operation_id: entry.operation_id.clone(), depends_on, invocation_identity: String::new() });
    }
    let mut ordered = Vec::new();
    let mut emitted: BTreeSet<String> = BTreeSet::new();
    while !pending.is_empty() {
        let index = pending.iter().position(|entry| entry.depends_on.iter().all(|dependency| emitted.contains(dependency))).ok_or("cyclic compensation dependency")?;
        let next = pending.remove(index);
        emitted.insert(next.plan_occurrence_id.clone());
        ordered.push(next);
    }
    let completed_step_journal_digest = ${fn}_digest(&[vec!["domainspec.workflow-completed-step-journal/v1".to_owned()], completed_step_ids.to_vec()].concat().join("\\n"), digest)?;
    let plan_digest = ${fn}_digest(&${fn}_plan_material(&ordered), digest)?;
    let intent_id = ${fn}_digest(&["domainspec.workflow-recovery-intent/v2", workflow_execution_id, failure_occurrence_id, failed_step_id, &completed_step_journal_digest, &plan_digest].join("\\n"), digest)?;
    for entry in &mut ordered { entry.invocation_identity = ${fn}_invocation_identity(&intent_id, &plan_digest, &entry.operation_id, &entry.plan_occurrence_id, digest)?; }
    Ok(${name}RecoveryDecision { schema_version: "domainspec.workflow-recovery-decision/v1", workflow_evaluation_result: "recovery-required", recovery_intent: Some(${name}RecoveryIntent { schema_version: "domainspec.workflow-recovery-intent/v2", intent_id, workflow_id: ${JSON.stringify(input.node_id)}, workflow_execution_id: workflow_execution_id.to_owned(), failure_occurrence_id: failure_occurrence_id.to_owned(), failed_step_id: failed_step_id.to_owned(), completed_step_journal_digest, plan_digest, semantic_status: "required", plan: ordered }) })
}
pub fn ${fn}(mut run: impl FnMut(&str) -> Result<(), &'static str>, mut compensate: impl FnMut(&str) -> Result<(), &'static str>, workflow_execution_id: &str, failure_occurrence_id: &str, digest: &impl Fn(&str) -> String) -> ${name}Outcome {
    let _ = &mut compensate;
    let mut completed = Vec::new();
    for step in ${constant}_STEPS {
        if run(step).is_err() {
            let decision = plan_${fn}_recovery(&completed, step, workflow_execution_id, failure_occurrence_id, digest).expect("validated recovery contract");
            return ${name}Outcome { ok: false, completed, failed_step: Some((*step).to_owned()), workflow_evaluation_result: decision.workflow_evaluation_result, recovery_intent: decision.recovery_intent, compensation_execution: false, direct_effects_executed: Vec::new() };
        }
        completed.push((*step).to_owned());
    }
    ${name}Outcome { ok: true, completed, failed_step: None, workflow_evaluation_result: "not-required", recovery_intent: None, compensation_execution: false, direct_effects_executed: Vec::new() }
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ${name}RecoveryBinding<'a> { pub workflow_id: &'a str, pub operation_id: &'a str, pub failure_continuation: &'a str }
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ${name}RecoveryInvocationReport { pub schema_version: &'static str, pub outcome: &'static str, pub executed_plan_occurrence_ids: Vec<String>, pub failed_plan_occurrence_id: Option<String>, pub failure_continuation: Option<String>, pub reason: Option<String>, pub recovery_intent_semantic_status: &'static str, pub durable_terminal_disposition: Option<String> }
fn verify_${fn}_recovery_intent(intent: &${name}RecoveryIntent, digest: &impl Fn(&str) -> String) -> Result<(), &'static str> {
    if intent.semantic_status != "required" || intent.workflow_id != ${JSON.stringify(input.node_id)} { return Err("Recovery Intent is not executable for this Workflow"); }
    let mut emitted: BTreeSet<String> = BTreeSet::new();
    for entry in &intent.plan {
        if !${constant}_ORCHESTRATED_OPERATION_IDS.contains(&entry.operation_id.as_str()) { return Err("recovery target is outside Workflow relation set"); }
        if emitted.contains(&entry.plan_occurrence_id) || entry.depends_on.iter().any(|dependency| !emitted.contains(dependency)) { return Err("invalid recovery plan order"); }
        emitted.insert(entry.plan_occurrence_id.clone());
    }
    if ${fn}_digest(&${fn}_plan_material(&intent.plan), digest)? != intent.plan_digest { return Err("Recovery Intent plan digest mismatch"); }
    let observed_intent_id = ${fn}_digest(&["domainspec.workflow-recovery-intent/v2", &intent.workflow_execution_id, &intent.failure_occurrence_id, &intent.failed_step_id, &intent.completed_step_journal_digest, &intent.plan_digest].join("\\n"), digest)?;
    if observed_intent_id != intent.intent_id { return Err("Recovery Intent identity mismatch"); }
    for entry in &intent.plan {
        if ${fn}_invocation_identity(&intent.intent_id, &intent.plan_digest, &entry.operation_id, &entry.plan_occurrence_id, digest)? != entry.invocation_identity { return Err("Recovery Intent invocation identity mismatch"); }
    }
    Ok(())
}
pub fn execute_${fn}_recovery(intent: &${name}RecoveryIntent, bindings: &[${name}RecoveryBinding<'_>], digest: &impl Fn(&str) -> String, mut invoke: impl FnMut(&str, &str) -> Result<(), String>) -> Result<${name}RecoveryInvocationReport, &'static str> {
    verify_${fn}_recovery_intent(intent, digest)?;
    let required_operation_ids: BTreeSet<&str> = intent.plan.iter().map(|entry| entry.operation_id.as_str()).collect();
    let mut registered = BTreeSet::new();
    for binding in bindings {
        if !${constant}_ORCHESTRATED_OPERATION_IDS.contains(&binding.operation_id) { return Err("binding is outside Workflow relation set"); }
        if binding.workflow_id != intent.workflow_id { return Err("binding Workflow mismatch"); }
        if !required_operation_ids.contains(binding.operation_id) { return Err("undeclared recovery binding"); }
        if !registered.insert(binding.operation_id) { return Err("duplicate recovery binding"); }
    }
    if required_operation_ids.iter().any(|operation_id| !registered.contains(operation_id)) { return Err("missing recovery Operation"); }
    let mut executed = Vec::new();
    for entry in &intent.plan {
        let binding = bindings.iter().find(|binding| binding.operation_id == entry.operation_id).ok_or("missing recovery Operation")?;
        if let Err(reason) = invoke(&entry.operation_id, &entry.invocation_identity) {
            return Ok(${name}RecoveryInvocationReport { schema_version: "domainspec.workflow-recovery-in-process-report/v1", outcome: "failed", executed_plan_occurrence_ids: executed, failed_plan_occurrence_id: Some(entry.plan_occurrence_id.clone()), failure_continuation: Some(binding.failure_continuation.to_owned()), reason: Some(reason), recovery_intent_semantic_status: "required", durable_terminal_disposition: None });
        }
        executed.push(entry.plan_occurrence_id.clone());
    }
    Ok(${name}RecoveryInvocationReport { schema_version: "domainspec.workflow-recovery-in-process-report/v1", outcome: "succeeded", executed_plan_occurrence_ids: executed, failed_plan_occurrence_id: None, failure_continuation: None, reason: None, recovery_intent_semantic_status: "required", durable_terminal_disposition: None })
}
`;
}

function renderTypeScript(input: GeneratorInput): string {
  const name = pascal(input.node_id);
  const fn = camel(input.node_id);
  const body = input.body;
  const header = provenance(input, "//");
  switch (input.kind) {
    case "Entity": {
      if (body.typed_contract !== undefined) return `${header}#[derive(Clone, Debug, PartialEq)]\npub struct ${name} { pub id: String, pub state: String }\n`;
      const fields = fieldSpecs(body.fields);
      const identity = camel(text(body.identity_field, "identity"));
      return `${header}${l1Marker(input, "//")}// domainspec-entity-identity: ${JSON.stringify(text(body.identity_field, ""))}
type DomainspecRef<Selector extends string> = string & { readonly __domainspecRef: Selector };
export interface ${name}Fields {
${typescriptFields(fields)}
}
export class ${name} {
  constructor(private readonly fields: Readonly<${name}Fields>) {}
  sameIdentity(other: ${name}): boolean { return this.fields.${identity} === other.fields.${identity}; }
  snapshot(): Readonly<${name}Fields> { return Object.freeze({ ...this.fields }); }
}
`;
    }
    case "Value Object": {
      if (body.typed_contract !== undefined) return `${header}#[derive(Clone, Debug, PartialEq, Eq)]\npub struct ${name}(pub String);\n`;
      const fields = fieldSpecs(body.fields);
      const comparisons = fields.map(({ field_id }) => `Object.is(this.fields.${camel(field_id)}, other.fields.${camel(field_id)})`).join(" && ") || "true";
      return `${header}${l1Marker(input, "//")}// domainspec-value-object-structural-equality: true
// domainspec-value-object-invariant-refs: ${canonicalJson(strings(body.invariant_refs))}
type DomainspecRef<Selector extends string> = string & { readonly __domainspecRef: Selector };
export interface ${name}Fields {
${typescriptFields(fields)}
}
export class ${name} {
  constructor(private readonly fields: Readonly<${name}Fields>) { this.fields = Object.freeze({ ...fields }); }
  equals(other: ${name}): boolean { return ${comparisons}; }
  value(): Readonly<${name}Fields> { return this.fields; }
}
`;
    }
    case "Enum": {
      const values = strings(body.values);
      const names = uniqueNames(values, pascal, "TypeScript Enum");
      return `${header}${l1Marker(input, "//")}// domainspec-enum-closed-values: ${canonicalJson(values)}\nexport const ${name} = Object.freeze({\n${values.map((value, index) => `  ${names[index]}: ${JSON.stringify(value)},`).join("\n")}\n} as const);\nexport type ${name} = (typeof ${name})[keyof typeof ${name}];\n`;
    }
    case "Operation": {
      const contract = canonicalJson({ reads: strings(body.reads), writes: strings(body.writes), effects: strings(body.effects) });
      return `${header}// domainspec-operation-sets: ${contract}\n// domainspec-operation-guard: ${JSON.stringify(text(body.guard, "guard"))}\n// domainspec-guard-before-mutation: true\n// domainspec-atomic-state-outbox: true\n// domainspec-failure-continuation: ${JSON.stringify(text(body.failure_continuation, "return-error"))}\n// domainspec-operation-core-instrumentation-free: true\n// domainspec-operation-instrumentation-owner: "outer-wrapper"\nexport const ${name}Contract = Object.freeze(${canonicalJson({ creation_targets: strings(body.creation_targets), reads: strings(body.reads), writes: strings(body.writes), effects: strings(body.effects), relationships: input.relationships })});\nexport function ${fn}(state: Readonly<Record<string, unknown>>, changes: Readonly<Record<string, unknown>>, guard: () => boolean) {\n  if (!guard()) return { ok: false as const, continuation: ${JSON.stringify(text(body.failure_continuation, "return-error"))} };\n  const readSet = Object.freeze(Object.fromEntries(${name}Contract.reads.map((key) => [key, state[key]])));\n  const nextState = Object.freeze(${name}Contract.writes.reduce<Record<string, unknown>>((next, key) => ({ ...next, [key]: changes[key] }), { ...state }));\n  const outbox = ${name}Contract.effects.map((type) => Object.freeze({ type, operation: ${JSON.stringify(input.node_id)} }));\n  return { ok: true as const, reads: readSet, state: nextState, outbox };\n}\nexport function ${fn}Observed(state: Readonly<Record<string, unknown>>, changes: Readonly<Record<string, unknown>>, guard: () => boolean, observe: (phase: "operation.enter" | "operation.success" | "operation.failure") => void) {\n  observe("operation.enter");\n  const outcome = ${fn}(state, changes, guard);\n  observe(outcome.ok ? "operation.success" : "operation.failure");\n  return outcome;\n}\n`;
    }
    case "Query":
      return (body.typed_contract as { schema_version?: string } | undefined)?.schema_version === "domainspec.typed-query/v1"
        ? renderTypeScriptQuery(input, fn, header)
        : `${header}export function ${fn}(_rows: readonly unknown[]): never { throw new Error("Query requires authored domainspec.typed-query/v1 semantics"); }\n`;
    case "Calculation":
      return body.typed_contract ? renderTypeScriptCalculation(input, fn, header) : `${header}export function ${fn}(_inputs: unknown): never { throw new Error("Calculation requires authored domainspec.typed-calculation/v1 semantics"); }\n`;
    case "Rule":
      return input.typed_closure?.schema_version === "domainspec.typed-rule-closure/v1"
        ? renderTypeScriptTypedRule(input, fn, header)
        : `${header}export function ${fn}(_candidate: unknown): boolean {\n  throw new Error("Rule requires authored domainspec.typed-rule/v1 semantics");\n}\n`;
    case "Policy":
      return body.typed_contract ? renderTypeScriptPolicy(input, fn, header) : `${header}export function ${fn}(_parameters: unknown): never { throw new Error("Policy requires authored domainspec.typed-policy/v1 semantics"); }\n`;
    case "Workflow":
      return renderTypeScriptWorkflow(input, name, fn, header);
    case "Interface": {
      const operations = interfaceOperations(body.operations);
      const signatures = operations.map((operation) => {
        const operationName = `${name}${pascal(operation.operation_id)}`;
        return `export interface ${operationName}Request {\n${typescriptFields(operation.request)}\n}\nexport interface ${operationName}Result {\n${typescriptFields(operation.result)}\n}`;
      }).join("\n");
      const methods = operations.map((operation) => `  ${camel(operation.operation_id)}(request: Readonly<${name}${pascal(operation.operation_id)}Request>): Promise<Readonly<${name}${pascal(operation.operation_id)}Result>>;`).join("\n");
      const version = text(body.version, "1");
      const compatibility = text(body.compatibility, "exact");
      const compatible = compatibility === "backward" ? `Number.isInteger(Number(candidateVersion)) && Number(candidateVersion) >= 1 && Number(candidateVersion) <= ${Number(version)}` : `candidateVersion === ${JSON.stringify(version)}`;
      return `${header}${l1Marker(input, "//")}// domainspec-interface-boundary: ${JSON.stringify(text(body.boundary_kind, ""))}
// domainspec-interface-compatibility: ${canonicalJson({ version, direction: compatibility })}
type DomainspecRef<Selector extends string> = string & { readonly __domainspecRef: Selector };
${signatures}
export interface ${name} {
  readonly version: ${JSON.stringify(version)};
${methods}
}
export function ${fn}AcceptsVersion(candidateVersion: string): boolean { return ${compatible}; }
`;
    }
    case "Event": {
      const occurrence = fieldSpec(body.occurrence_id);
      const payload = fieldSpecs(body.payload);
      const version = text(body.version, "1");
      return `${header}${l1Marker(input, "//")}// domainspec-event-compatibility: ${canonicalJson({ event_type: text(body.event_type, input.node_id), version })}
// domainspec-event-occurred-at-policy: ${JSON.stringify(text(body.occurred_at_policy, "required"))}
type DomainspecRef<Selector extends string> = string & { readonly __domainspecRef: Selector };
export interface ${name}Payload {
${typescriptFields(payload)}
}
export interface ${name} {
  readonly type: ${JSON.stringify(text(body.event_type, input.node_id))};
  readonly version: ${JSON.stringify(version)};
  readonly ${camel(occurrence.field_id)}: ${typescriptType(occurrence.type_ref)};
  readonly occurredAt: string;
  readonly payload: Readonly<${name}Payload>;
}
export function ${fn}Compatible(candidate: Readonly<{ type: string; version: string }>): boolean { return candidate.type === ${JSON.stringify(text(body.event_type, input.node_id))} && candidate.version === ${JSON.stringify(version)}; }
`;
    }
    case "Mapping":
      return body.typed_contract ? renderTypeScriptMapping(input, fn, header) : `${header}export function ${fn}(_source: unknown): never { throw new Error("Mapping requires authored domainspec.typed-mapping/v1 semantics"); }\n`;
    case "State Machine": {
      const transitions = stateTransitions(body.transitions);
      const rejectionCodes = ["invalid-current-state", "undeclared-transition", "source-mismatch", "guard-rejected"];
      return `${header}// domainspec-state-machine-initial: ${JSON.stringify(text(body.initial, ""))}
// domainspec-state-machine-transitions: ${canonicalJson(transitions)}
// domainspec-state-machine-event-intents-only: true
// domainspec-state-machine-guard-contract: "rule-reference-callback/v1"
// domainspec-state-machine-guard-required: true
// domainspec-state-machine-source-enforcement: true
// domainspec-state-machine-causal-rejections: ${JSON.stringify(rejectionCodes)}
export const ${name}States = Object.freeze(${JSON.stringify(strings(body.states))} as const);
export const ${name}Transitions = Object.freeze(${canonicalJson(transitions)}) as readonly Readonly<{ transition_id: string; source_state: string; target_state: string; guard_ref: string | null; effect_event_ref: string | null }>[];
export type ${name}TransitionResult =
  | Readonly<{ ok: true; transitionId: string; priorState: string; state: string; effectEventRef: string | null }>
  | Readonly<{ ok: false; transitionId: string; state: string; code: "invalid-current-state" | "undeclared-transition" | "source-mismatch" | "guard-rejected"; guardRef: string | null }>;
export function ${fn}Transition(current: string, transitionId: string, evaluateGuard: (guardRef: string) => boolean): ${name}TransitionResult {
  if (!((${name}States) as readonly string[]).includes(current)) return Object.freeze({ ok: false, transitionId, state: current, code: "invalid-current-state", guardRef: null });
  const transition = ${name}Transitions.find((candidate) => candidate.transition_id === transitionId);
  if (!transition) return Object.freeze({ ok: false, transitionId, state: current, code: "undeclared-transition", guardRef: null });
  if (transition.source_state !== current) return Object.freeze({ ok: false, transitionId, state: current, code: "source-mismatch", guardRef: transition.guard_ref });
  if (transition.guard_ref !== null && !evaluateGuard(transition.guard_ref)) return Object.freeze({ ok: false, transitionId, state: current, code: "guard-rejected", guardRef: transition.guard_ref });
  return Object.freeze({ ok: true, transitionId, priorState: current, state: transition.target_state, effectEventRef: transition.effect_event_ref });
}
`;
    }
    default:
      throw new Error(`unsupported TypeScript generator:${input.kind}`);
  }
}

function renderPython(input: GeneratorInput): string {
  const name = pascal(input.node_id);
  const fn = snake(input.node_id);
  const body = input.body;
  const header = provenance(input, "#");
  switch (input.kind) {
    case "Entity": {
      const fields = fieldSpecs(body.fields);
      const identity = snake(text(body.identity_field, "identity"));
      return `${header}${l1Marker(input, "#")}# domainspec-entity-identity: ${JSON.stringify(text(body.identity_field, ""))}
from dataclasses import dataclass
from typing import Annotated

@dataclass
class ${name}:
${pythonFields(fields)}

    def same_identity(self, other: "${name}") -> bool:
        return self.${identity} == other.${identity}

    def snapshot(self) -> dict[str, object]:
        return dict(self.__dict__)
`;
    }
    case "Value Object": {
      const fields = fieldSpecs(body.fields);
      return `${header}${l1Marker(input, "#")}# domainspec-value-object-structural-equality: true
# domainspec-value-object-invariant-refs: ${canonicalJson(strings(body.invariant_refs))}
from dataclasses import dataclass
from typing import Annotated

@dataclass(frozen=True)
class ${name}:
${pythonFields(fields)}

    def equals(self, other: "${name}") -> bool:
        return self == other
`;
    }
    case "Enum":
      return `${header}${l1Marker(input, "#")}# domainspec-enum-closed-values: ${canonicalJson(strings(body.values))}\nfrom enum import Enum\n\nclass ${name}(str, Enum):\n${strings(body.values).map((value, index, values) => `    ${uniqueNames(values, (entry) => snake(entry).toUpperCase(), "Python Enum")[index]} = ${JSON.stringify(value)}`).join("\n")}\n`;
    case "Operation":
      return `${header}# domainspec-operation-sets: ${canonicalJson({ reads: strings(body.reads), writes: strings(body.writes), effects: strings(body.effects) })}\n# domainspec-operation-guard: ${JSON.stringify(text(body.guard, "guard"))}\n# domainspec-guard-before-mutation: true\n# domainspec-atomic-state-outbox: true\n# domainspec-failure-continuation: ${JSON.stringify(text(body.failure_continuation, "return-error"))}\n# domainspec-operation-core-instrumentation-free: true\n# domainspec-operation-instrumentation-owner: "outer-wrapper"\n${fn.toUpperCase()}_CREATION_TARGETS = tuple(${JSON.stringify(strings(body.creation_targets))})\n${name.toUpperCase()}_RELATIONSHIPS = tuple(${canonicalJson(input.relationships)})\n\ndef ${fn}(state: dict[str, object], changes: dict[str, object], guard: bool) -> dict[str, object]:\n    if not guard:\n        return {"ok": False, "continuation": ${JSON.stringify(text(body.failure_continuation, "return-error"))}}\n    read_set = {key: state.get(key) for key in ${JSON.stringify(strings(body.reads))}}\n    next_state = dict(state)\n    for key in ${JSON.stringify(strings(body.writes))}:\n        next_state[key] = changes.get(key)\n    outbox = [{"type": effect, "operation": ${JSON.stringify(input.node_id)}} for effect in ${JSON.stringify(strings(body.effects))}]\n    return {"ok": True, "reads": read_set, "state": next_state, "outbox": outbox}\n\ndef ${fn}_observed(state: dict[str, object], changes: dict[str, object], guard: bool, observe):\n    observe("operation.enter")\n    outcome = ${fn}(state, changes, guard)\n    observe("operation.success" if outcome["ok"] else "operation.failure")\n    return outcome\n`;
    case "Query":
      return (body.typed_contract as { schema_version?: string } | undefined)?.schema_version === "domainspec.typed-query/v1"
        ? renderPythonQuery(input, fn, header)
        : `${header}def ${fn}(_rows: list[object]):\n    raise ValueError("Query requires authored domainspec.typed-query/v1 semantics")\n`;
    case "Calculation":
      return body.typed_contract ? renderPythonCalculation(input, fn, header) : `${header}def ${fn}(_inputs: object):\n    raise ValueError("Calculation requires authored domainspec.typed-calculation/v1 semantics")\n`;
    case "Rule":
      return input.typed_closure?.schema_version === "domainspec.typed-rule-closure/v1"
        ? renderPythonTypedRule(input, fn, header)
        : `${header}def ${fn}(_candidate: object) -> bool:\n    raise ValueError("Rule requires authored domainspec.typed-rule/v1 semantics")\n`;
    case "Policy":
      return body.typed_contract ? renderPythonPolicy(input, fn, header) : `${header}def ${fn}(_parameters: object):\n    raise ValueError("Policy requires authored domainspec.typed-policy/v1 semantics")\n`;
    case "Workflow":
      return renderPythonWorkflow(input, name, fn, header);
    case "Interface": {
      const operations = interfaceOperations(body.operations);
      const signatureTypes = operations.map((operation) => {
        const operationName = `${name}${pascal(operation.operation_id)}`;
        return `@dataclass(frozen=True)\nclass ${operationName}Request:\n${pythonFields(operation.request) || "    pass"}\n\n@dataclass(frozen=True)\nclass ${operationName}Result:\n${pythonFields(operation.result) || "    pass"}`;
      }).join("\n\n");
      const methods = operations.map((operation) => `    def ${snake(operation.operation_id)}(self, request: ${name}${pascal(operation.operation_id)}Request) -> ${name}${pascal(operation.operation_id)}Result: ...`).join("\n");
      const version = text(body.version, "1");
      const compatibility = text(body.compatibility, "exact");
      const compatible = compatibility === "backward" ? `candidate_version.isdigit() and 1 <= int(candidate_version) <= ${Number(version)}` : `candidate_version == ${JSON.stringify(version)}`;
      return `${header}${l1Marker(input, "#")}# domainspec-interface-boundary: ${JSON.stringify(text(body.boundary_kind, ""))}
# domainspec-interface-compatibility: ${canonicalJson({ version, direction: compatibility })}
from dataclasses import dataclass
from typing import Annotated, Protocol

${signatureTypes}

class ${name}(Protocol):
    version: str
${methods}

def ${fn}_accepts_version(candidate_version: str) -> bool:
    return ${compatible}
`;
    }
    case "Event": {
      const occurrence = fieldSpec(body.occurrence_id);
      const payload = fieldSpecs(body.payload);
      const version = text(body.version, "1");
      return `${header}${l1Marker(input, "#")}# domainspec-event-compatibility: ${canonicalJson({ event_type: text(body.event_type, input.node_id), version })}
# domainspec-event-occurred-at-policy: ${JSON.stringify(text(body.occurred_at_policy, "required"))}
from dataclasses import dataclass
from typing import Annotated, ClassVar

@dataclass(frozen=True)
class ${name}Payload:
${pythonFields(payload) || "    pass"}

@dataclass(frozen=True)
class ${name}:
    type: ClassVar[str] = ${JSON.stringify(text(body.event_type, input.node_id))}
    version: ClassVar[str] = ${JSON.stringify(version)}
    ${snake(occurrence.field_id)}: ${pythonType(occurrence.type_ref)}
    occurred_at: str
    payload: ${name}Payload

def ${fn}_compatible(candidate_type: str, candidate_version: str) -> bool:
    return candidate_type == ${JSON.stringify(text(body.event_type, input.node_id))} and candidate_version == ${JSON.stringify(version)}
`;
    }
    case "Mapping":
      return body.typed_contract ? renderPythonMapping(input, fn, header) : `${header}def ${fn}(_source: object):\n    raise ValueError("Mapping requires authored domainspec.typed-mapping/v1 semantics")\n`;
    case "State Machine": {
      const transitions = stateTransitions(body.transitions);
      const rejectionCodes = ["invalid-current-state", "undeclared-transition", "source-mismatch", "guard-rejected"];
      return `${header}# domainspec-state-machine-initial: ${JSON.stringify(text(body.initial, ""))}
# domainspec-state-machine-transitions: ${canonicalJson(transitions)}
# domainspec-state-machine-event-intents-only: true
# domainspec-state-machine-guard-contract: "rule-reference-callback/v1"
# domainspec-state-machine-guard-required: true
# domainspec-state-machine-source-enforcement: true
# domainspec-state-machine-causal-rejections: ${JSON.stringify(rejectionCodes)}
${name.toUpperCase()}_STATES = tuple(${JSON.stringify(strings(body.states))})
${name.toUpperCase()}_TRANSITIONS = (${pythonStateTransitions(transitions)}${transitions.length === 1 ? "," : ""})

def ${fn}_transition(current: str, transition_id: str, evaluate_guard) -> dict[str, object]:
    if current not in ${name.toUpperCase()}_STATES:
        return {"ok": False, "transition_id": transition_id, "state": current, "code": "invalid-current-state", "guard_ref": None}
    transition = next((candidate for candidate in ${name.toUpperCase()}_TRANSITIONS if candidate["transition_id"] == transition_id), None)
    if transition is None:
        return {"ok": False, "transition_id": transition_id, "state": current, "code": "undeclared-transition", "guard_ref": None}
    if transition["source_state"] != current:
        return {"ok": False, "transition_id": transition_id, "state": current, "code": "source-mismatch", "guard_ref": transition["guard_ref"]}
    if transition["guard_ref"] is not None and not evaluate_guard(transition["guard_ref"]):
        return {"ok": False, "transition_id": transition_id, "state": current, "code": "guard-rejected", "guard_ref": transition["guard_ref"]}
    return {"ok": True, "transition_id": transition_id, "prior_state": current, "state": transition["target_state"], "effect_event_ref": transition["effect_event_ref"]}
`;
    }
    default:
      throw new Error(`unsupported Python generator:${input.kind}`);
  }
}

function rustSlice(values: readonly string[]): string {
  return `&[${values.map((value) => JSON.stringify(value)).join(", ")}]`;
}

function rustArray(values: readonly string[]): string {
  return `[${values.map((value) => JSON.stringify(value)).join(", ")}]`;
}

function renderRust(input: GeneratorInput): string {
  const name = pascal(input.node_id);
  const fn = snake(input.node_id);
  const body = input.body;
  const header = provenance(input, "//");
  switch (input.kind) {
    case "Entity": {
      const fields = fieldSpecs(body.fields);
      const identity = snake(text(body.identity_field, "identity"));
      return `${header}${l1Marker(input, "//")}// domainspec-entity-identity: ${JSON.stringify(text(body.identity_field, ""))}
#[derive(Clone, Debug, PartialEq)]
pub struct ${name} {
${rustFields(fields)}
}
impl ${name} {
    pub fn same_identity(&self, other: &Self) -> bool { self.${identity} == other.${identity} }
}
`;
    }
    case "Value Object": {
      const fields = fieldSpecs(body.fields);
      return `${header}${l1Marker(input, "//")}// domainspec-value-object-structural-equality: true
// domainspec-value-object-invariant-refs: ${canonicalJson(strings(body.invariant_refs))}
#[derive(Clone, Debug, PartialEq)]
pub struct ${name} {
${rustFields(fields)}
}
impl ${name} {
    pub fn equals(&self, other: &Self) -> bool { self == other }
}
`;
    }
    case "Enum":
      return `${header}${l1Marker(input, "//")}// domainspec-enum-closed-values: ${canonicalJson(strings(body.values))}\n#[derive(Clone, Debug, PartialEq, Eq)]\npub enum ${name} { ${uniqueNames(strings(body.values), pascal, "Rust Enum").join(", ")} }\n`;
    case "Operation":
      if (input.typed_closure?.schema_version === "domainspec.typed-operation-closure/v1") {
        return `${header}// domainspec-operation-sets: ${canonicalJson({ reads: strings(body.reads), writes: strings(body.writes), effects: strings(body.effects) })}\n// domainspec-operation-guard: ${JSON.stringify(text(body.guard, "guard"))}\n// domainspec-guard-before-mutation: true\n// domainspec-atomic-state-outbox: true\n// domainspec-failure-continuation: ${JSON.stringify(text(body.failure_continuation, "return-error"))}\n// domainspec-operation-core-instrumentation-free: true\n// domainspec-operation-instrumentation-owner: "outer-wrapper"\npub const ${snake(name).toUpperCase()}_CREATION_TARGETS: &[&str] = ${rustSlice(strings(body.creation_targets))};\n${renderTypedRustOperation(input.typed_closure)}`;
      }
      return `${header}// domainspec-operation-sets: ${canonicalJson({ reads: strings(body.reads), writes: strings(body.writes), effects: strings(body.effects) })}\n// domainspec-operation-guard: ${JSON.stringify(text(body.guard, "guard"))}\n// domainspec-guard-before-mutation: true\n// domainspec-atomic-state-outbox: true\n// domainspec-failure-continuation: ${JSON.stringify(text(body.failure_continuation, "return-error"))}\n// domainspec-operation-core-instrumentation-free: true\n// domainspec-operation-instrumentation-owner: "outer-wrapper"\nuse std::collections::BTreeMap;\npub const ${snake(name).toUpperCase()}_CREATION_TARGETS: &[&str] = ${rustSlice(strings(body.creation_targets))};\npub const ${snake(name).toUpperCase()}_RELATIONSHIPS_JSON: &str = ${JSON.stringify(canonicalJson(input.relationships))};\n#[derive(Clone, Debug, PartialEq)]\npub struct ${name}Outcome { pub reads: BTreeMap<String, String>, pub state: BTreeMap<String, String>, pub outbox: Vec<String> }\npub fn ${fn}(state: &BTreeMap<String, String>, changes: &BTreeMap<String, String>, guard: bool) -> Result<${name}Outcome, &'static str> {\n    if !guard { return Err(${JSON.stringify(text(body.failure_continuation, "return-error"))}); }\n    let reads = ${rustArray(strings(body.reads))}.iter().filter_map(|key| state.get(*key).map(|value| ((*key).to_owned(), value.clone()))).collect();\n    let mut next_state = state.clone();\n    for key in ${rustArray(strings(body.writes))} { if let Some(value) = changes.get(key) { next_state.insert(key.to_owned(), value.clone()); } }\n    let outbox: Vec<String> = ${rustArray(strings(body.effects))}.iter().map(|value| (*value).to_owned()).collect();\n    Ok(${name}Outcome { reads, state: next_state, outbox })\n}\npub fn ${fn}_observed(state: &BTreeMap<String, String>, changes: &BTreeMap<String, String>, guard: bool, observe: &mut impl FnMut(&str)) -> Result<${name}Outcome, &'static str> {\n    observe("operation.enter");\n    let outcome = ${fn}(state, changes, guard);\n    observe(if outcome.is_ok() { "operation.success" } else { "operation.failure" });\n    outcome\n}\n`;
    case "Query":
      if (input.typed_closure?.schema_version === "domainspec.typed-operation-closure/v1") {
        return `${header}// domainspec-query-reads: ${canonicalJson(strings(body.reads))}\n// domainspec-query-effects: []\n// domainspec-query-provider-neutral: true\n${renderTypedRustOperation(input.typed_closure)}`;
      }
      return body.typed_contract ? renderRustQuery(input, fn, header) : `${header}pub fn ${fn}() { panic!("Query requires authored domainspec.typed-query/v1 semantics") }\n`;
    case "Calculation":
      return body.typed_contract ? renderRustCalculation(input, fn, header) : `${header}pub fn ${fn}() { panic!("Calculation requires authored domainspec.typed-calculation/v1 semantics") }\n`;
    case "Rule":
      return input.typed_closure?.schema_version === "domainspec.typed-rule-closure/v1"
        ? `${header}${renderTypedRustRule(input.typed_closure)}`
        : `${header}pub fn ${fn}(_candidate: bool) -> bool { panic!("Rule requires authored domainspec.typed-rule/v1 semantics") }\n`;
    case "Policy":
      return body.typed_contract ? renderRustPolicy(input, fn, header) : `${header}pub fn ${fn}() { panic!("Policy requires authored domainspec.typed-policy/v1 semantics") }\n`;
    case "Workflow":
      return renderRustWorkflow(input, name, fn, header);
    case "Interface": {
      const operations = interfaceOperations(body.operations);
      const signatureTypes = operations.map((operation) => {
        const operationName = `${name}${pascal(operation.operation_id)}`;
        return `#[derive(Clone, Debug, PartialEq)]\npub struct ${operationName}Request {\n${rustFields(operation.request)}\n}\n#[derive(Clone, Debug, PartialEq)]\npub struct ${operationName}Result {\n${rustFields(operation.result)}\n}`;
      }).join("\n");
      const methods = operations.map((operation) => `    fn ${snake(operation.operation_id)}(&self, request: ${name}${pascal(operation.operation_id)}Request) -> ${name}${pascal(operation.operation_id)}Result;`).join("\n");
      const version = text(body.version, "1");
      const compatibility = text(body.compatibility, "exact");
      const compatible = compatibility === "backward" ? `candidate_version.parse::<u64>().is_ok_and(|candidate| candidate >= 1 && candidate <= ${Number(version)})` : `candidate_version == ${JSON.stringify(version)}`;
      return `${header}${l1Marker(input, "//")}// domainspec-interface-boundary: ${JSON.stringify(text(body.boundary_kind, ""))}
// domainspec-interface-compatibility: ${canonicalJson({ version, direction: compatibility })}
${signatureTypes}
pub trait ${name} {
    fn version(&self) -> &'static str { ${JSON.stringify(version)} }
${methods}
}
pub fn ${fn}_accepts_version(candidate_version: &str) -> bool { ${compatible} }
`;
    }
    case "Event": {
      const occurrence = fieldSpec(body.occurrence_id);
      const payload = fieldSpecs(body.payload);
      const version = text(body.version, "1");
      return `${header}${l1Marker(input, "//")}// domainspec-event-compatibility: ${canonicalJson({ event_type: text(body.event_type, input.node_id), version })}
// domainspec-event-occurred-at-policy: ${JSON.stringify(text(body.occurred_at_policy, "required"))}
#[derive(Clone, Debug, PartialEq)]
pub struct ${name}Payload {
${rustFields(payload)}
}
#[derive(Clone, Debug, PartialEq)]
pub struct ${name} {
    pub ${snake(occurrence.field_id)}: ${rustType(occurrence.type_ref)},
    pub occurred_at: String,
    pub payload: ${name}Payload,
}
pub const ${snake(name).toUpperCase()}_TYPE: &str = ${JSON.stringify(text(body.event_type, input.node_id))};
pub const ${snake(name).toUpperCase()}_VERSION: &str = ${JSON.stringify(version)};
pub fn ${fn}_compatible(candidate_type: &str, candidate_version: &str) -> bool { candidate_type == ${snake(name).toUpperCase()}_TYPE && candidate_version == ${snake(name).toUpperCase()}_VERSION }
`;
    }
    case "Mapping":
      return body.typed_contract ? renderRustMapping(input, fn, header) : `${header}pub fn ${fn}() { panic!("Mapping requires authored domainspec.typed-mapping/v1 semantics") }\n`;
    case "State Machine": {
      const transitions = stateTransitions(body.transitions);
      const constant = snake(name).toUpperCase();
      const rejectionCodes = ["invalid-current-state", "undeclared-transition", "source-mismatch", "guard-rejected"];
      return `${header}// domainspec-state-machine-initial: ${JSON.stringify(text(body.initial, ""))}
// domainspec-state-machine-transitions: ${canonicalJson(transitions)}
// domainspec-state-machine-event-intents-only: true
// domainspec-state-machine-guard-contract: "rule-reference-callback/v1"
// domainspec-state-machine-guard-required: true
// domainspec-state-machine-source-enforcement: true
// domainspec-state-machine-causal-rejections: ${JSON.stringify(rejectionCodes)}
pub const ${constant}_STATES: &[&str] = ${rustSlice(strings(body.states))};
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ${name}Transition { pub transition_id: &'static str, pub source_state: &'static str, pub target_state: &'static str, pub guard_ref: Option<&'static str>, pub effect_event_ref: Option<&'static str> }
pub const ${constant}_TRANSITIONS: &[${name}Transition] = &[${transitions.map((transition) => `${name}Transition { transition_id: ${JSON.stringify(transition.transition_id)}, source_state: ${JSON.stringify(transition.source_state)}, target_state: ${JSON.stringify(transition.target_state)}, guard_ref: ${rustOption(transition.guard_ref)}, effect_event_ref: ${rustOption(transition.effect_event_ref)} }`).join(", ")}];
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum ${name}TransitionResult { Applied { transition_id: String, prior_state: String, state: String, effect_event_ref: Option<String> }, Rejected { transition_id: String, state: String, code: &'static str, guard_ref: Option<String> } }
pub fn ${fn}_transition(current: &str, transition_id: &str, evaluate_guard: impl Fn(&str) -> bool) -> ${name}TransitionResult {
    if !${constant}_STATES.contains(&current) { return ${name}TransitionResult::Rejected { transition_id: transition_id.to_owned(), state: current.to_owned(), code: "invalid-current-state", guard_ref: None }; }
    let Some(transition) = ${constant}_TRANSITIONS.iter().find(|candidate| candidate.transition_id == transition_id) else { return ${name}TransitionResult::Rejected { transition_id: transition_id.to_owned(), state: current.to_owned(), code: "undeclared-transition", guard_ref: None }; };
    if transition.source_state != current { return ${name}TransitionResult::Rejected { transition_id: transition_id.to_owned(), state: current.to_owned(), code: "source-mismatch", guard_ref: transition.guard_ref.map(str::to_owned) }; }
    if transition.guard_ref.is_some_and(|guard_ref| !evaluate_guard(guard_ref)) { return ${name}TransitionResult::Rejected { transition_id: transition_id.to_owned(), state: current.to_owned(), code: "guard-rejected", guard_ref: transition.guard_ref.map(str::to_owned) }; }
    ${name}TransitionResult::Applied { transition_id: transition_id.to_owned(), prior_state: current.to_owned(), state: transition.target_state.to_owned(), effect_event_ref: transition.effect_event_ref.map(str::to_owned) }
}
`;
    }
    default:
      throw new Error(`unsupported Rust generator:${input.kind}`);
  }
}

export const GENERATOR_REGISTRY: readonly GeneratorRegistration[] = Object.freeze(
  FROZEN_META_TYPE_CATALOG.realization_rows.map((row) => Object.freeze({
    generator_id: generatorIdFor(row.meta_type_id, row.language),
    meta_type_id: row.meta_type_id,
    language: row.language,
    extension: EXTENSIONS[row.language],
  })),
);

export function generatorIdFor(metaTypeId: string, language: SupportedLanguage): string {
  const version = metaTypeId === "DS-D1.9" ? "v3" : ["DS-D1.1", "DS-D1.2", "DS-D1.3", "DS-D1.4", "DS-D1.11", "DS-D1.12", "DS-D1.14"].includes(metaTypeId) ? "v2" : "v1";
  return `domainspec.generator/${metaTypeId}/${language}/${version}`;
}

export function renderImplementation(input: GeneratorInput): { readonly generator_id: string; readonly extension: "ts" | "py" | "rs"; readonly content: string } {
  const registration = GENERATOR_REGISTRY.find((row) => row.meta_type_id === input.meta_type_id && row.language === input.realization.language);
  if (!registration) throw new Error(`generator is not registered:${input.meta_type_id}/${input.realization.language}`);
  const renderers: Readonly<Record<SupportedLanguage, (value: GeneratorInput) => string>> = {
    typescript: renderTypeScript,
    python: renderPython,
    rust: renderRust,
  };
  return Object.freeze({ generator_id: registration.generator_id, extension: registration.extension, content: renderers[input.realization.language](input) });
}
