import { createCompiledProjectCertificate } from "../compilation/certificate.js";
import { createCheckedInterchange } from "../assurance/checked-interchange.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { loadCompiledProjectGraph, type CompiledProjectGraphNode, type FieldSpec, type StateTransitionSpec } from "../input/project-model.js";
import type { BackendPredicate, BackendValue, NumericExpression, TypedCalculationContract, TypedMappingContract, TypedPolicyContract, TypedQueryContract } from "../typed-backend/contracts.js";
import type { RuleExpression, TypedOperationContract, TypedParameter, TypedRecordContract, TypedResultConstructor, TypedRuleContract, TypedSumContract, TypedType, ValueExpression } from "../typed-operation/contracts.js";
import { decodeRuntimeInvocation, runtimeRequestSha256, RuntimeContractError, type RuntimeInvocationV1, type RuntimeReceiptV1 } from "./contracts.js";

const BACKEND_TYPES = 13;
const BACKEND_RELATIONSHIPS = 17;
function fail(code: string, pointer: string, message: string): never { throw new RuntimeContractError(code, pointer, message); }
function record(value: unknown, pointer: string): Record<string, unknown> { if (value === null || typeof value !== "object" || Array.isArray(value)) fail("MTCLI_RUNTIME_INPUT", pointer, "expected object"); return value as Record<string, unknown>; }
function array(value: unknown, pointer: string): unknown[] { if (!Array.isArray(value)) fail("MTCLI_RUNTIME_INPUT", pointer, "expected array"); return value; }
function string(value: unknown, pointer: string): string { if (typeof value !== "string") fail("MTCLI_RUNTIME_INPUT", pointer, "expected string"); return value; }
function bool(value: unknown, pointer: string): boolean { if (typeof value !== "boolean") fail("MTCLI_RUNTIME_INPUT", pointer, "expected Boolean"); return value; }
function u64(value: unknown, pointer: string): number { if (!Number.isSafeInteger(value) || Number(value) < 0) fail("MTCLI_RUNTIME_INPUT", pointer, "expected safe UInt64"); return Number(value); }
function exactInput(input: Readonly<Record<string, unknown>>, keys: readonly string[], pointer: string): void { if (JSON.stringify(Object.keys(input).sort()) !== JSON.stringify([...keys].sort())) fail("MTCLI_RUNTIME_INPUT", pointer, "unexpected or missing runtime input member"); }
function nodeContract(nodes: readonly CompiledProjectGraphNode[], selector: string): TypedRecordContract | TypedSumContract | undefined {
  const contract = nodes.find((node) => node.selector === selector)?.body.typed_contract as TypedRecordContract | TypedSumContract | undefined;
  return contract?.schema_version === "domainspec.typed-record/v1" || contract?.schema_version === "domainspec.typed-sum/v1" ? contract : undefined;
}
function typedRecordValue(contract: TypedRecordContract, value: unknown, pointer: string, nodes: readonly CompiledProjectGraphNode[], depth: number): Record<string, unknown> {
  const selected = record(value, pointer); const allowed = new Set(contract.properties.map(({ name }) => name));
  if (Object.keys(selected).some((key) => !allowed.has(key))) fail("MTCLI_RUNTIME_INPUT", pointer, "typed record contains an undeclared property");
  for (const property of contract.properties) {
    if (!Object.hasOwn(selected, property.name) && property.cardinality !== "optional") fail("MTCLI_RUNTIME_INPUT", `${pointer}/${property.name}`, "typed record is missing a required property");
    typedValue(property.type, selected[property.name], `${pointer}/${property.name}`, nodes, depth + 1);
  }
  return selected;
}
function typedValue(type: TypedType, value: unknown, pointer: string, nodes: readonly CompiledProjectGraphNode[], depth = 0): void {
  if (depth > 16) fail("MTCLI_RUNTIME_TYPE", pointer, "runtime type nesting exceeds maximum depth");
  if (type.kind === "scalar") {
    if (type.name === "String" && typeof value === "string") return;
    if (type.name === "Bool" && typeof value === "boolean") return;
    if (type.name === "UInt64" && Number.isSafeInteger(value) && Number(value) >= 0) return;
    fail("MTCLI_RUNTIME_TYPE", pointer, `expected ${type.name}`);
  }
  if (type.kind === "named") {
    const contract = nodeContract(nodes, type.selector);
    if (!contract) { if (value !== null && (typeof value === "object" || typeof value === "string")) return; fail("MTCLI_RUNTIME_TYPE", pointer, `expected named value:${type.selector}`); }
    if (contract.schema_version === "domainspec.typed-record/v1") {
      typedRecordValue(contract, value, pointer, nodes, depth);
      return;
    }
    const selected = record(value, pointer); exactInput(selected, ["variant", "payload"], pointer); const variantName = string(selected.variant, `${pointer}/variant`); const variant = contract.variants.find(({ name }) => name === variantName);
    if (!variant) fail("MTCLI_RUNTIME_TYPE", `${pointer}/variant`, `unknown sum variant:${variantName}`);
    if (variant.payload === null && selected.payload !== null) fail("MTCLI_RUNTIME_TYPE", `${pointer}/payload`, "payloadless sum variant received a payload");
    if (variant.payload !== null) typedValue(variant.payload, selected.payload, `${pointer}/payload`, nodes, depth + 1);
    return;
  }
  if (type.kind === "optional") { if (value === null || value === undefined) return; return typedValue(type.element, value, pointer, nodes, depth + 1); }
  if (type.kind === "sum") {
    const selected = record(value, pointer); exactInput(selected, ["variant", "payload"], pointer); const variantName = string(selected.variant, `${pointer}/variant`); const variant = type.variants.find(({ name }) => name === variantName);
    if (!variant) fail("MTCLI_RUNTIME_TYPE", `${pointer}/variant`, `unknown sum variant:${variantName}`);
    if (variant.payload === null && selected.payload !== null) fail("MTCLI_RUNTIME_TYPE", `${pointer}/payload`, "payloadless sum variant received a payload");
    if (variant.payload !== null) typedValue(variant.payload, selected.payload, `${pointer}/payload`, nodes, depth + 1);
    return;
  }
  const values = array(value, pointer); for (const [index, entry] of values.entries()) typedValue(type.element, entry, `${pointer}/${index}`, nodes, depth + 1);
  if (type.kind === "set" && new Set(values.map(stable)).size !== values.length) fail("MTCLI_RUNTIME_TYPE", pointer, "set input contains duplicates");
}
function typedParameters(parameters: readonly TypedParameter[], value: unknown, pointer: string, nodes: readonly CompiledProjectGraphNode[]): Record<string, unknown> {
  const input = record(value, pointer); const names = parameters.map(({ name }) => name).sort();
  if (JSON.stringify(Object.keys(input).sort()) !== JSON.stringify(names)) fail("MTCLI_RUNTIME_INPUT", pointer, "runtime parameters must exactly match the authored contract");
  for (const parameter of parameters) typedValue(parameter.type, input[parameter.name], `${pointer}/${parameter.name}`, nodes);
  return input;
}

function backendValue(value: BackendValue, row: Readonly<Record<string, unknown>>, parameters: Readonly<Record<string, unknown>>): unknown {
  if (value.kind === "literal") return value.value;
  const source = value.kind === "field" ? row : parameters;
  if (!Object.hasOwn(source, value.name)) fail("MTCLI_RUNTIME_VALUE", "/input", `missing ${value.kind}:${value.name}`);
  return source[value.name];
}
function predicate(value: BackendPredicate, row: Readonly<Record<string, unknown>>, parameters: Readonly<Record<string, unknown>>): boolean {
  if (value.op === "all" || value.op === "any") return value.op === "all" ? value.terms.every((term) => predicate(term, row, parameters)) : value.terms.some((term) => predicate(term, row, parameters));
  if (value.op === "not") return !predicate(value.term, row, parameters);
  if (!("left" in value)) return fail("MTCLI_RUNTIME_COMPARISON", "/input", "invalid comparison predicate");
  const left = backendValue(value.left, row, parameters); const right = backendValue(value.right, row, parameters);
  if (value.op === "eq") return Object.is(left, right);
  if ((typeof left !== "number" && typeof left !== "string") || typeof right !== typeof left) fail("MTCLI_RUNTIME_COMPARISON", "/input", "ordered comparison requires matching scalar values");
  const comparableRight = right as string | number;
  if (value.op === "lt") return left < comparableRight;
  if (value.op === "lte") return left <= comparableRight;
  if (value.op === "gt") return left > comparableRight;
  return left >= comparableRight;
}
function numeric(value: NumericExpression, inputs: Readonly<Record<string, unknown>>, rounding: string): number {
  if (value.op === "literal") return u64(value.value, "/input");
  if (value.op === "input") return u64(inputs[value.name], `/input/inputs/${value.name}`);
  const left = numeric(value.left, inputs, rounding); const right = numeric(value.right, inputs, rounding);
  if (value.op === "add") { const result = left + right; return u64(result, "/output"); }
  if (value.op === "subtract") { if (left < right) fail("MTCLI_RUNTIME_CALCULATION", "/input", "Calculation underflow"); return left - right; }
  if (value.op === "multiply") { const result = left * right; return u64(result, "/output"); }
  if (right === 0) fail("MTCLI_RUNTIME_CALCULATION", "/input", "Calculation division by zero");
  if (rounding === "reject" && left % right !== 0) fail("MTCLI_RUNTIME_CALCULATION", "/input", "Calculation inexact division");
  return rounding === "ceil" ? Math.ceil(left / right) : Math.floor(left / right);
}

function stable(value: unknown): string { return canonicalJson(value instanceof Set ? [...value].sort() : value); }
function ruleValue(value: ValueExpression, environment: Readonly<Record<string, unknown>>, properties: Readonly<Record<string, string>>): unknown {
  if (value.op === "literal") return value.value;
  if (value.op === "variant") return value.selector;
  if (value.op === "to_set") return new Set(array(ruleValue(value.value, environment, properties), "/input").map(stable));
  let current = environment[value.root];
  for (const property of value.properties) {
    const field = properties[property]; if (!field) fail("MTCLI_RUNTIME_RULE", "/input", `unresolved Rule property:${property}`);
    current = Array.isArray(current) ? current.map((entry) => record(entry, "/input")[field]) : record(current, "/input")[field];
  }
  return current;
}
function ruleExpression(value: RuleExpression, environment: Readonly<Record<string, unknown>>, properties: Readonly<Record<string, string>>, rules: ReadonlyMap<string, TypedRuleContract>): boolean {
  if (value.op === "all" || value.op === "any") return value.op === "all" ? value.terms.every((term) => ruleExpression(term, environment, properties, rules)) : value.terms.some((term) => ruleExpression(term, environment, properties, rules));
  if (value.op === "not") return !ruleExpression(value.term, environment, properties, rules);
  if (["eq", "lt", "set_equal", "contains"].includes(value.op)) {
    const binary = value as Extract<RuleExpression, { left: ValueExpression }>;
    const left = ruleValue(binary.left, environment, properties); const right = ruleValue(binary.right, environment, properties);
    if (value.op === "lt") return typeof left === "number" && typeof right === "number" && left < right;
    if (value.op === "contains") return left instanceof Set ? left.has(stable(right)) : array(left, "/input").some((entry) => stable(entry) === stable(right));
    return stable(left) === stable(right);
  }
  if (value.op === "rule_ref") {
    const contract = rules.get(value.selector); if (!contract) fail("MTCLI_RUNTIME_RULE", "/input", `unresolved Rule reference:${value.selector}`);
    return ruleExpression(contract.expression, Object.fromEntries(value.arguments.map((argument) => [argument.parameter, ruleValue(argument.value, environment, properties)])), properties, rules);
  }
  if (value.op === "exactly_one" || value.op === "exists" || value.op === "unique") {
    const collection = array(ruleValue(value.collection, environment, properties), "/input");
    if (value.op === "unique") {
      if (!("left" in value.where)) fail("MTCLI_RUNTIME_RULE", "/input", "unique requires a key expression");
      const keyExpression = value.where.left;
      return new Set(collection.map((entry) => stable(ruleValue(keyExpression, { ...environment, [value.binding]: entry }, properties)))).size === collection.length;
    }
    const count = collection.filter((entry) => ruleExpression(value.where, { ...environment, [value.binding]: entry }, properties, rules)).length;
    return value.op === "exactly_one" ? count === 1 : count > 0;
  }
  return fail("MTCLI_RUNTIME_RULE", "/input", "unsupported Rule expression");
}

function typedProperties(nodes: readonly CompiledProjectGraphNode[]): Readonly<Record<string, string>> {
  const properties: Record<string, string> = {};
  for (const candidate of nodes) {
    const typed = candidate.body.typed_contract as TypedRecordContract | undefined;
    if (typed?.schema_version === "domainspec.typed-record/v1") for (const property of typed.properties) properties[property.ontology_property] = property.name;
  }
  return properties;
}
function typedRules(nodes: readonly CompiledProjectGraphNode[]): ReadonlyMap<string, TypedRuleContract> {
  return new Map(nodes.flatMap((candidate) => {
    const typed = candidate.body.typed_contract as TypedRuleContract | undefined;
    return typed?.schema_version === "domainspec.typed-rule/v1" ? [[candidate.selector, typed] as const] : [];
  }));
}
function constructResult(constructor: TypedResultConstructor, environment: Readonly<Record<string, unknown>>, properties: Readonly<Record<string, string>>): Readonly<Record<string, unknown>> {
  if ("payload" in constructor) return Object.freeze({ variant: constructor.variant, payload: constructor.payload === null ? null : ruleValue(constructor.payload, environment, properties) });
  return Object.freeze({ variant: constructor.variant, payload: constructor.payload_variant === null ? null : Object.freeze({ variant: constructor.payload_variant, payload: null }) });
}

function validateField(field: FieldSpec, value: unknown, pointer: string): void {
  if (value === undefined) { if (field.required) fail("MTCLI_RUNTIME_FIELD", pointer, `missing required field:${field.field_id}`); return; }
  if (field.type_ref.kind === "reference") { if (typeof value !== "string" && (value === null || typeof value !== "object")) fail("MTCLI_RUNTIME_FIELD", pointer, "invalid reference value"); return; }
  const name = field.type_ref.name;
  const valid = name === "boolean" ? typeof value === "boolean" : name === "integer" || name === "decimal" ? typeof value === "number" && Number.isFinite(value) : typeof value === "string";
  if (!valid) fail("MTCLI_RUNTIME_FIELD", pointer, `invalid ${name} field:${field.field_id}`);
}

function execute(node: CompiledProjectGraphNode, input: Readonly<Record<string, unknown>>, allNodes: readonly CompiledProjectGraphNode[]): unknown {
  const body = node.body;
  if (node.kind === "Entity") { exactInput(input, ["record"], "/input"); const value = record(input.record, "/input/record"); const typed = body.typed_contract as TypedRecordContract | undefined; if (typed?.schema_version === "domainspec.typed-record/v1") { typedRecordValue(typed, value, "/input/record", allNodes, 0); const identity = typed.properties.find((property) => property.identity); if (!identity) fail("MTCLI_RUNTIME_IDENTITY", "/input/record", "typed Entity has no identity property"); return Object.freeze({ identity: value[identity.name], record: Object.freeze({ ...value }) }); } for (const field of body.fields as readonly FieldSpec[]) validateField(field, value[field.field_id], `/input/record/${field.field_id}`); return Object.freeze({ identity: value[String(body.identity_field)], record: Object.freeze({ ...value }) }); }
  if (node.kind === "Value Object") { exactInput(input, ["left", "right"], "/input"); const left = record(input.left, "/input/left"); const right = record(input.right, "/input/right"); const typed = body.typed_contract as TypedRecordContract | undefined; if (typed?.schema_version === "domainspec.typed-record/v1") { typedRecordValue(typed, left, "/input/left", allNodes, 0); typedRecordValue(typed, right, "/input/right", allNodes, 0); } else for (const field of body.fields as readonly FieldSpec[]) { validateField(field, left[field.field_id], `/input/left/${field.field_id}`); validateField(field, right[field.field_id], `/input/right/${field.field_id}`); } return Object.freeze({ equal: stable(left) === stable(right) }); }
  if (node.kind === "Enum") { exactInput(input, ["value"], "/input"); const value = string(input.value, "/input/value"); return Object.freeze({ value, admitted: (body.values as readonly string[]).includes(value) }); }
  if (node.kind === "Operation") { const typed = body.typed_contract as TypedOperationContract | undefined; if (typed?.schema_version === "domainspec.typed-operation/v1") { exactInput(input, ["parameters"], "/input"); const parameters = typedParameters(typed.inputs, input.parameters, "/input/parameters", allNodes); const properties = typedProperties(allNodes); const rules = typedRules(allNodes); const guard = rules.get(typed.guard); if (!guard) fail("MTCLI_RUNTIME_OPERATION", "/input", `unresolved Operation guard:${typed.guard}`); const accepted = ruleExpression(guard.expression, parameters, properties, rules); const result = constructResult(accepted ? typed.success_result : typed.failure_result, parameters, properties); typedValue(typed.output, result, "/output", allNodes); return Object.freeze({ ok: accepted, result, continuation: accepted ? null : typed.failure_continuation }); } exactInput(input, ["state", "changes", "guard"], "/input"); const state = record(input.state, "/input/state"); const changes = record(input.changes, "/input/changes"); if (!bool(input.guard, "/input/guard")) return Object.freeze({ ok: false, continuation: body.failure_continuation }); const reads = Object.fromEntries((body.reads as readonly string[]).map((key) => [key, state[key]])); const next = { ...state }; for (const key of body.writes as readonly string[]) next[key] = changes[key]; return Object.freeze({ ok: true, reads: Object.freeze(reads), state: Object.freeze(next), outbox: Object.freeze((body.effects as readonly string[]).map((type) => Object.freeze({ type, operation: node.node_id }))) }); }
  if (node.kind === "Query") { exactInput(input, ["rows", "parameters"], "/input"); const contract = body.typed_contract as TypedQueryContract; const parameters = typedParameters(contract.inputs, input.parameters, "/input/parameters", allNodes); let rows = array(input.rows, "/input/rows").map((row, index) => record(row, `/input/rows/${index}`)).filter((row) => contract.filter === null || predicate(contract.filter, row, parameters)); if (contract.order_by) rows = [...rows].sort((left, right) => { const a = left[contract.order_by!.field] as string | number; const b = right[contract.order_by!.field] as string | number; const order = a === b ? 0 : a < b ? -1 : 1; return contract.order_by!.direction === "asc" ? order : -order; }); if (contract.limit !== null) rows = rows.slice(0, contract.limit); return Object.freeze(rows.map((row) => Object.freeze(Object.fromEntries(contract.projection.map((field) => [field, row[field]]))))); }
  if (node.kind === "Calculation") { exactInput(input, ["inputs"], "/input"); const contract = body.typed_contract as TypedCalculationContract; const inputs = typedParameters(contract.inputs, input.inputs, "/input/inputs", allNodes); return numeric(contract.expression, inputs, contract.division_rounding); }
  if (node.kind === "Rule") { exactInput(input, ["parameters"], "/input"); const contract = body.typed_contract as TypedRuleContract | undefined; if (!contract) fail("MTCLI_RUNTIME_RULE", "/input", "Rule requires typed semantics for runtime execution"); return ruleExpression(contract.expression, typedParameters(contract.parameters, input.parameters, "/input/parameters", allNodes), typedProperties(allNodes), typedRules(allNodes)); }
  if (node.kind === "Policy") { exactInput(input, ["parameters"], "/input"); const contract = body.typed_contract as TypedPolicyContract; const parameters = typedParameters(contract.inputs, input.parameters, "/input/parameters", allNodes); return contract.cases.find((candidate) => predicate(candidate.when, {}, parameters))?.target ?? contract.default_target; }
  if (node.kind === "Workflow") { exactInput(input, [], "/input"); return Object.freeze({ steps: body.steps, compensations: body.compensations, compensation_dependencies: body.compensation_dependencies }); }
  if (node.kind === "Interface") { exactInput(input, ["requested_version"], "/input"); const requestedText = string(input.requested_version, "/input/requested_version"); if (!/^[1-9][0-9]*$/.test(requestedText)) fail("MTCLI_RUNTIME_INPUT", "/input/requested_version", "requested Interface version must be positive"); const requested = Number(requestedText); const current = Number(body.version); return Object.freeze({ compatible: body.compatibility === "exact" ? requested === current : requested <= current, boundary_kind: body.boundary_kind }); }
  if (node.kind === "Event") { exactInput(input, ["occurrence_id", "occurred_at", "payload"], "/input"); const payload = record(input.payload, "/input/payload"); validateField(body.occurrence_id as FieldSpec, input.occurrence_id, "/input/occurrence_id"); for (const field of body.payload as readonly FieldSpec[]) validateField(field, payload[field.field_id], `/input/payload/${field.field_id}`); const occurredAt = string(input.occurred_at, "/input/occurred_at"); if (Number.isNaN(Date.parse(occurredAt))) fail("MTCLI_RUNTIME_INPUT", "/input/occurred_at", "Event occurred_at must be an ISO timestamp"); return Object.freeze({ event_type: body.event_type, version: body.version, occurrence_id: input.occurrence_id, occurred_at: occurredAt, payload: Object.freeze({ ...payload }) }); }
  if (node.kind === "Mapping") { exactInput(input, ["source"], "/input"); const contract = body.typed_contract as TypedMappingContract; const source = record(input.source, "/input/source"); return Object.freeze(Object.fromEntries(contract.fields.map((field) => { const selected = field.source === null ? undefined : source[field.source]; if (selected === undefined && field.default === null) fail("MTCLI_RUNTIME_MAPPING", "/input/source", `missing Mapping source:${field.source}`); return [field.target, selected ?? field.default?.value]; }))); }
  if (node.kind === "State Machine") { exactInput(input, ["current_state", "transition_id", "guards"], "/input"); const current = string(input.current_state, "/input/current_state"); const transitionId = string(input.transition_id, "/input/transition_id"); if (!(body.states as readonly string[]).includes(current)) fail("MTCLI_RUNTIME_STATE", "/input/current_state", "invalid current state"); const transition = (body.transitions as readonly StateTransitionSpec[]).find(({ transition_id }) => transition_id === transitionId); if (!transition) fail("MTCLI_RUNTIME_STATE", "/input/transition_id", "undeclared transition"); if (transition.source_state !== current) fail("MTCLI_RUNTIME_STATE", "/input/current_state", "transition source mismatch"); const guards = record(input.guards, "/input/guards"); if (transition.guard_ref !== null && guards[transition.guard_ref] !== true) fail("MTCLI_RUNTIME_STATE", "/input/guards", "transition guard rejected"); return Object.freeze({ state: transition.target_state, event: transition.effect_event_ref }); }
  fail("MTCLI_RUNTIME_META_TYPE", `/nodes/${node.selector}`, `unsupported runtime meta-type:${node.kind}`);
}

export function runInMemoryProject(sourceRoot: string, requestValue: unknown): RuntimeReceiptV1 {
  const request: RuntimeInvocationV1 = decodeRuntimeInvocation(requestValue);
  const graph = loadCompiledProjectGraph(sourceRoot); const certificate = createCompiledProjectCertificate(graph); const interchange = createCheckedInterchange(graph);
  const executed = new Set<string>();
  const outcomes = request.steps.map((step) => {
    const node = graph.nodes.find(({ selector }) => selector === step.selector); if (!node) fail("MTCLI_RUNTIME_ENTRY", `/steps/${step.step_id}/selector`, `unknown runtime node:${step.selector}`);
    const output = execute(node, step.input, graph.nodes); executed.add(node.selector);
    return Object.freeze({ step_id: step.step_id, selector: node.selector, meta_type_id: node.meta_type_id, kind: node.kind, output, output_sha256: sha256(canonicalJson(output)) });
  });
  const edges = graph.relationships.filter(({ source, target }) => executed.has(`${source.feature_id}:${source.node_id}`) || executed.has(`${target.feature_id}:${target.node_id}`));
  const nodeSelectors = [...executed].sort(); const metaTypes = [...new Set(outcomes.map(({ meta_type_id }) => meta_type_id))].sort(); const relationshipIds = [...new Set(edges.map(({ relationship }) => relationship))].sort();
  const coverage = Object.freeze({ node_selectors: Object.freeze(nodeSelectors), meta_type_ids: Object.freeze(metaTypes), relationship_edge_ids: Object.freeze(edges.map(({ edge_id }) => edge_id).sort()), relationship_ids: Object.freeze(relationshipIds), complete_backend_types: metaTypes.length === BACKEND_TYPES && nodeSelectors.length === graph.nodes.length, complete_backend_relationships: relationshipIds.length === BACKEND_RELATIONSHIPS && edges.length === graph.relationships.length });
  const body = { schema_version: "domainspec.runtime-receipt/v1" as const, invocation_id: request.invocation_id, provider: request.provider, project_id: graph.project_id, source_manifest_sha256: graph.source_manifest.manifest_sha256, compiled_certificate_sha256: certificate.certificate_sha256, checked_interchange_sha256: interchange.interchange_sha256, request_sha256: runtimeRequestSha256(request), outcomes: Object.freeze(outcomes), coverage, authority_effect: "none" as const };
  return Object.freeze({ ...body, receipt_sha256: sha256(canonicalJson(body)) });
}
