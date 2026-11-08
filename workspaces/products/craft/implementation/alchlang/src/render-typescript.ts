import type { CompilationPlan, NormalizedFact } from "./model.js";
import { requireGeneratablePattern } from "./pattern-registry.js";
import { renderSqliteTransactionalOutbox } from "./sqlite-outbox-generator.js";

const identifier = (value: string): string => value.replace(/[^A-Za-z0-9_$]/g, "_").replace(/^[^A-Za-z_$]/, "_$&");
const pascal = (value: string): string => identifier(value).split("_").filter(Boolean).map((part) => part[0].toUpperCase() + part.slice(1)).join("") || "Anonymous";
const tsType = (fact: NormalizedFact): string => ({ integer: "number", decimal: "number", boolean: "boolean", list: "readonly unknown[]", record: "Readonly<Record<string, unknown>>" } as Record<string, string>)[fact.type] ?? "string";
const json = (value: unknown): string => JSON.stringify(value, null, 2) + "\n";
const literal = (value: unknown): string => JSON.stringify(value, null, 2) + " as const;\n";

function renderTypedBackend(plan: CompilationPlan): string {
  const contracts = JSON.stringify({ queries: plan.query_contracts, calculations: plan.calculation_contracts, mappings: plan.mapping_contracts, policies: plan.policy_contracts }, null, 2);
  return `export const typedBackendContracts = ${contracts};
const MAX = (1n << 64n) - 1n;
const fail = (code, message) => { const error = new Error(code + ":" + message); error.code = code; throw error; };
const required = (value, field) => field in value ? value[field] : fail("MISSING_TYPED_VALUE", field);
const predicateValue = (expression, facts) => {
  if (expression.node) return expression.node === "literal" ? expression.value : expression.node === "fact_ref" ? facts[expression.ref] : expression.ref;
  const values = expression.operands.map((operand) => predicateValue(operand, facts));
  switch (expression.operator) {
    case "not": return !Boolean(values[0]); case "exists": return values[0] !== undefined && values[0] !== null; case "absent": return values[0] === undefined || values[0] === null;
    case "eq": return values[0] === values[1]; case "neq": return values[0] !== values[1]; case "lt": return values[0] < values[1]; case "lte": return values[0] <= values[1]; case "gt": return values[0] > values[1]; case "gte": return values[0] >= values[1];
    case "and": return Boolean(values[0]) && Boolean(values[1]); case "or": return Boolean(values[0]) || Boolean(values[1]); default: return fail("UNKNOWN_OPERATOR", expression.operator);
  }
};
const uint64 = (value) => { let result; try { result = typeof value === "bigint" ? value : typeof value === "number" && Number.isSafeInteger(value) ? BigInt(value) : typeof value === "string" && /^(0|[1-9]\\d*)$/.test(value) ? BigInt(value) : fail("CALCULATION_INPUT_TYPE", String(value)); } catch (error) { if (error.code) throw error; return fail("CALCULATION_INPUT_TYPE", String(value)); } if (result < 0n || result > MAX) return fail("CALCULATION_RANGE", String(value)); return result; };
const calculationValue = (expression, inputs, rounding) => { if (expression.node === "uint64_literal") return uint64(expression.value); if (expression.node === "input_ref") return expression.ref in inputs ? uint64(inputs[expression.ref]) : fail("MISSING_CALCULATION_INPUT", expression.ref); const left = calculationValue(expression.operands[0], inputs, rounding); const right = calculationValue(expression.operands[1], inputs, rounding); let result; switch (expression.operator) { case "add": result = left + right; break; case "subtract": if (right > left) return fail("CALCULATION_UNDERFLOW", "subtract"); result = left - right; break; case "multiply": result = left * right; break; case "divide": if (right === 0n) return fail("CALCULATION_DIVIDE_BY_ZERO", "divide"); if (left % right !== 0n && rounding === "reject") return fail("CALCULATION_INEXACT", "divide"); result = left / right + (rounding === "ceil" && left % right !== 0n ? 1n : 0n); break; } if (result > MAX) return fail("CALCULATION_OVERFLOW", expression.operator); return result; };
export const evaluateCalculation = (id, inputs) => { const contract = typedBackendContracts.calculations.find((item) => item.id === id); if (!contract) return fail("CALCULATION_NOT_FOUND", id); for (const input of contract.input_facts) required(inputs, input); return calculationValue(contract.expression, inputs, contract.rounding); };
const predicateRefs = (expression) => !expression ? [] : expression.node ? expression.node === "fact_ref" ? [expression.ref] : [] : expression.operands.flatMap(predicateRefs);
export const evaluateQuery = (id, rows, inputs = {}) => { const contract = typedBackendContracts.queries.find((item) => item.id === id); if (!contract) return fail("QUERY_NOT_FOUND", id); for (const input of contract.input_facts) required(inputs, input); const refs = predicateRefs(contract.predicate); let selected = rows.filter((row) => { const facts = { ...inputs, ...row }; for (const ref of refs) required(facts, ref); return !contract.predicate || predicateValue(contract.predicate, facts); }); if (contract.order_by.length) selected = [...selected].sort((a, b) => { for (const order of contract.order_by) { const left = required(a, order.field_ref), right = required(b, order.field_ref); if (left < right) return order.direction === "asc" ? -1 : 1; if (left > right) return order.direction === "asc" ? 1 : -1; } return 0; }); if (contract.limit !== null) selected = selected.slice(0, contract.limit); return selected.map((row) => Object.fromEntries(contract.projection.map((field) => [field, required(row, field)]))); };
export const evaluateMapping = (id, source) => { const contract = typedBackendContracts.mappings.find((item) => item.id === id); if (!contract) return fail("MAPPING_NOT_FOUND", id); const target = {}; for (const clause of contract.clauses) { if (clause.source_field !== null && clause.source_field in source) target[clause.target_field] = source[clause.source_field]; else if (clause.default_value !== null) target[clause.target_field] = clause.default_value.value; else if (contract.total) fail("MAPPING_REQUIRED_VALUE", clause.target_field); } return target; };
export const evaluatePolicy = (id, inputs) => { const contract = typedBackendContracts.policies.find((item) => item.id === id); if (!contract) return fail("POLICY_NOT_FOUND", id); for (const input of contract.input_facts) required(inputs, input); for (const item of contract.cases) if (predicateValue(item.predicate, inputs)) return item.target_ref; return contract.default_target_ref; };
export const authorityEffect = "none";
`;
}

export function renderTypeScript(plan: CompilationPlan): Record<string, string> {
  const entities = plan.type_model.map((type) => `export interface ${pascal(type.id)} {\n${type.fields.map((field) => `  ${JSON.stringify(field.id)}${field.required ? "" : "?"}: ${tsType(field)};`).join("\n")}\n}`);
  const valueObjects = plan.value_object_contracts.map((type) => `export interface ${pascal(type.id)} {\n${type.fields.map((field) => `  readonly ${JSON.stringify(field.id)}${field.required ? "" : "?"}: ${tsType(field)};`).join("\n")}\n}\nexport const ${identifier(type.id)}EqualityFields = ${JSON.stringify(type.equality_fields)} as const;`);
  const enums = plan.enum_contracts.map((type) => `export type ${pascal(type.id)} = ${type.values.map((value) => JSON.stringify(value.id)).join(" | ")};\nexport const ${identifier(type.id)}Values = ${JSON.stringify(type.values)} as const;`);
  const types = [...entities, ...valueObjects, ...enums].join("\n\n") + "\n";
  const ports = plan.action_ports.map((action) => {
    const name = pascal(action.id);
    return `export interface ${name}Request { readonly facts: Readonly<Record<string, unknown>>; }\nexport interface ${name}Result { readonly outcome: string; readonly emittedEvents: readonly string[]; }\nexport interface ${name}Port { execute(request: ${name}Request): Promise<${name}Result>; }`;
  }).join("\n\n") + "\n";
  const base: Record<string, string> = { "domain.graph.json": json(plan.graph_model) };
  if (plan.type_model.length + plan.value_object_contracts.length + plan.enum_contracts.length > 0) base["domain.types.ts"] = types;
  if (plan.type_model.length > 0) base["domain.schema.ts"] = `export const factModel = ${literal(plan.type_model)}`;
  if (plan.state_machines.some((machine) => machine.states.length + machine.transitions.length > 0)) base["domain.machine.ts"] = `export const stateMachines = ${literal(plan.state_machines)}`;
  if (plan.event_contracts.length > 0) base["domain.events.ts"] = `export const eventContracts = ${literal(plan.event_contracts)}`;
  if (plan.action_ports.length > 0) base["domain.tools.ts"] = ports;
  if (plan.operation_contracts.length > 0) base["domain.operations.ts"] = `export const operationContracts = ${literal(plan.operation_contracts)}`;
  if (plan.workflow_contracts.length > 0) base["domain.workflows.ts"] = `export const workflowContracts = ${literal(plan.workflow_contracts)}`;
  if (plan.interface_contracts.length > 0) base["domain.interfaces.ts"] = `export const interfaceContracts = ${literal(plan.interface_contracts)}`;
  if (plan.test_obligations.length > 0) base["domain.test-obligations.json"] = json(plan.test_obligations);
  if (plan.trace_ledger.length > 0) base["traceability.json"] = json(plan.trace_ledger);
  if (plan.unsupported_residue.length > 0) base["unsupported-residue.json"] = json(plan.unsupported_residue);
  const hasTypedBackend = plan.query_contracts.length + plan.calculation_contracts.length + plan.mapping_contracts.length + plan.policy_contracts.length > 0;
  const typedFiles: Record<string, string> = hasTypedBackend ? { "domain.typed-backend.ts": renderTypedBackend(plan) } : {};
  if (!plan.effect_contracts.length) return { ...base, ...typedFiles };
  const effectFiles: Record<string, string> = { "domain.effects.ts": `export const effectContracts = ${literal(plan.effect_contracts)}` };
  for (const effect of plan.effect_contracts) {
    const pattern = requireGeneratablePattern(effect.pattern_ref);
    if (pattern.integration_binding.id !== effect.integration_binding_ref) throw new Error(`EFFECT_BINDING_NOT_AVAILABLE:${effect.id}:${effect.integration_binding_ref}`);
    if (effect.pattern_ref === "transactional-outbox") Object.assign(effectFiles, renderSqliteTransactionalOutbox(effect));
    else throw new Error(`EFFECT_GENERATOR_NOT_IMPLEMENTED:${effect.pattern_ref}`);
  }
  return { ...base, ...typedFiles, ...effectFiles };
}
