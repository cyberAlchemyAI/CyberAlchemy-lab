import { BINARY_OPERATORS, CompilationRejected, LEAF_NODES, SFOL_PROFILE, UNARY_OPERATORS, type CompilerIssue, type NormalizedDomain, type ScalarType, type SfolFormula, type SfolUInt64Term } from "./model.js";

type Obj = Record<string, unknown>;
const SCALARS = new Set<ScalarType>(["string", "integer", "decimal", "boolean", "identifier", "timestamp", "duration", "enum", "reference", "list", "record"]);

function obj(value: unknown, path: string, issues: CompilerIssue[]): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path, message: "expected an object" });
    return {};
  }
  return value as Obj;
}

function text(value: unknown, path: string, issues: CompilerIssue[]): string {
  if (typeof value !== "string" || value.length === 0) {
    issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path, message: "expected a non-empty string" });
    return "";
  }
  return value;
}

function list(value: unknown, path: string, issues: CompilerIssue[]): unknown[] {
  if (!Array.isArray(value)) {
    issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path, message: "expected an array" });
    return [];
  }
  return value;
}

const strings = (value: unknown, path: string, issues: CompilerIssue[]): string[] => list(value, path, issues).map((item, index) => text(item, `${path}[${index}]`, issues));

function assertUnique(values: string[], path: string, issues: CompilerIssue[]): void {
  const seen = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) issues.push({ code: "DUPLICATE_IDENTIFIER", path, message: `duplicate identifier ${value}` });
    seen.add(value);
  }
}

function validateSfolFormula(value: unknown, path: string, facts: Map<string, ScalarType>, refs: Record<string, Set<string>>, issues: CompilerIssue[]): { expression: SfolFormula; type: ScalarType | "boolean" | "unknown" } {
  const node = obj(value, path, issues);
  if (typeof node.node === "string") {
    if (!(LEAF_NODES as readonly string[]).includes(node.node)) {
      issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path, message: `unknown leaf ${node.node}` });
      return { expression: { node: "literal", value_type: "boolean", value: false }, type: "unknown" };
    }
    if (node.node === "literal") {
      const valueType = text(node.value_type, `${path}.value_type`, issues) as ScalarType;
      if (!SCALARS.has(valueType)) issues.push({ code: "TYPE_MISMATCH", path, message: `unknown literal type ${valueType}` });
      return { expression: { node: "literal", value_type: valueType, value: node.value }, type: valueType };
    }
    const ref = text(node.ref, `${path}.ref`, issues);
    const group = node.node === "fact_ref" ? "facts" : node.node === "entity_ref" ? "entities" : node.node === "actor_ref" ? "actors" : "states";
    if (!refs[group].has(ref)) issues.push({ code: "UNRESOLVED_REFERENCE", path: `${path}.ref`, message: `${ref} is not a declared ${group.slice(0, -1)}` });
    const type = node.node === "fact_ref" ? (facts.get(ref) ?? "unknown") : "reference";
    return { expression: { node: node.node, ref } as SfolFormula, type };
  }
  const operator = text(node.operator, `${path}.operator`, issues);
  const unary = (UNARY_OPERATORS as readonly string[]).includes(operator);
  const binary = (BINARY_OPERATORS as readonly string[]).includes(operator);
  if (!unary && !binary) issues.push({ code: "UNKNOWN_OPERATOR", path: `${path}.operator`, message: `${operator} is not in the carrier contract` });
  const operands = list(node.operands, `${path}.operands`, issues).map((operand, index) => validateSfolFormula(operand, `${path}.operands[${index}]`, facts, refs, issues));
  const expected = unary ? 1 : 2;
  if (operands.length !== expected) issues.push({ code: "TYPE_MISMATCH", path: `${path}.operands`, message: `${operator} expects ${expected} operands` });
  const comparison = ["eq", "neq", "lt", "lte", "gt", "gte"].includes(operator);
  if (comparison && operands.length === 2 && operands[0].type !== "unknown" && operands[1].type !== "unknown" && operands[0].type !== operands[1].type) {
    issues.push({ code: "TYPE_MISMATCH", path, message: `${operator} cannot compare ${operands[0].type} with ${operands[1].type}` });
  }
  if (["and", "or", "not"].includes(operator) && operands.some((operand) => operand.type !== "boolean" && operand.type !== "unknown")) {
    issues.push({ code: "TYPE_MISMATCH", path, message: `${operator} requires boolean operands` });
  }
  // Membership must have a container. A numeric receiver used to compile and
  // silently evaluate false, hiding a malformed Rule rather than rejecting it.
  if (operands.length === 2 && operator === "contains") {
    const container = operands[0].type;
    const member = operands[1].type;
    if (container !== "unknown" && container !== "list" && container !== "string") {
      issues.push({ code: "TYPE_MISMATCH", path, message: "contains requires a list or string as its first operand" });
    } else if (container === "string" && (member !== "unknown" && member !== "string" ||
      "node" in operands[1].expression && operands[1].expression.node === "literal" && typeof operands[1].expression.value !== "string")) {
      issues.push({ code: "TYPE_MISMATCH", path, message: "string contains requires a string member" });
    }
  }
  if (operands.length === 2 && operator === "in" && operands[1].type !== "unknown" && operands[1].type !== "list") {
    issues.push({ code: "TYPE_MISMATCH", path, message: "in requires a list as its second operand" });
  }
  const container = operands.length === 2 ? operator === "contains" ? operands[0] : operator === "in" ? operands[1] : undefined : undefined;
  if (container && "node" in container.expression && container.expression.node === "literal" &&
      (container.type === "list" && !Array.isArray(container.expression.value) ||
       container.type === "string" && typeof container.expression.value !== "string")) {
    issues.push({ code: "TYPE_MISMATCH", path, message: "membership container literal does not match its declared type" });
  }
  return { expression: { operator, operands: operands.map((operand) => operand.expression) }, type: "boolean" };
}

function requireBooleanSfolFormula(value: unknown, path: string, facts: Map<string, ScalarType>, refs: Record<string, Set<string>>, issues: CompilerIssue[]): SfolFormula {
  const result = validateSfolFormula(value, path, facts, refs, issues);
  if (result.type !== "boolean" && result.type !== "unknown") issues.push({ code: "SFOL_FORMULA_TYPE", path, message: `formula must produce boolean, received ${result.type}` });
  return result.expression;
}

function requireRefs(items: string[], allowed: Set<string>, path: string, issues: CompilerIssue[]): void {
  for (const [index, item] of items.entries()) if (!allowed.has(item)) issues.push({ code: "UNRESOLVED_REFERENCE", path: `${path}[${index}]`, message: `${item} is not declared` });
}

function validateSfolUInt64Term(value: unknown, path: string, inputs: Set<string>, issues: CompilerIssue[], depth = 0): SfolUInt64Term {
  if (depth > 64) { issues.push({ code: "CALCULATION_DEPTH", path, message: "calculation nesting exceeds 64" }); return { node: "uint64_literal", value: "0" }; }
  const expression = obj(value, path, issues);
  if (expression.node === "uint64_literal") {
    const literal = text(expression.value, `${path}.value`, issues);
    try { if (!/^(0|[1-9]\d*)$/.test(literal) || BigInt(literal) > ((1n << 64n) - 1n)) issues.push({ code: "CALCULATION_RANGE", path: `${path}.value`, message: "literal is outside UInt64" }); } catch { issues.push({ code: "CALCULATION_RANGE", path: `${path}.value`, message: "literal is outside UInt64" }); }
    return { node: "uint64_literal", value: literal };
  }
  if (expression.node === "input_ref") {
    const ref = text(expression.ref, `${path}.ref`, issues);
    if (!inputs.has(ref)) issues.push({ code: "UNRESOLVED_REFERENCE", path: `${path}.ref`, message: `${ref} is not a declared calculation input` });
    return { node: "input_ref", ref };
  }
  const operator = text(expression.operator, `${path}.operator`, issues);
  if (!["add", "subtract", "multiply", "divide"].includes(operator)) issues.push({ code: "UNKNOWN_CALCULATION_OPERATOR", path: `${path}.operator`, message: `${operator} is not supported` });
  const operands = list(expression.operands, `${path}.operands`, issues);
  if (operands.length !== 2) issues.push({ code: "CALCULATION_ARITY", path: `${path}.operands`, message: `${operator} requires two operands` });
  return { operator: (["add", "subtract", "multiply", "divide"].includes(operator) ? operator : "add") as "add" | "subtract" | "multiply" | "divide", operands: [validateSfolUInt64Term(operands[0], `${path}.operands[0]`, inputs, issues, depth + 1), validateSfolUInt64Term(operands[1], `${path}.operands[1]`, inputs, issues, depth + 1)] };
}

function normalizeV2(root: Obj, issues: CompilerIssue[]): NormalizedDomain {
  const logicProfile = root.logic_profile === undefined ? SFOL_PROFILE : text(root.logic_profile, "$.logic_profile", issues);
  if (logicProfile !== SFOL_PROFILE) issues.push({ code: "SFOL_PROFILE", path: "$.logic_profile", message: `only ${SFOL_PROFILE} is supported` });
  const required = ["identity", "owners", "terms", "edges", "facts", "rules", "events", "states", "transitions", "actions", "permissions", "examples", "authority", "residue"];
  for (const key of required) if (!(key in root)) issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path: `$.${key}`, message: "required carrier-v2 section is missing" });
  const identity = obj(root.identity, "$.identity", issues);
  const domainId = text(identity.domain_id, "$.identity.domain_id", issues);
  const title = text(identity.title, "$.identity.title", issues);
  const ownerRows = list(root.owners, "$.owners", issues).map((value, index) => obj(value, `$.owners[${index}]`, issues));
  const owners = ownerRows.map((owner, index) => text(owner.owner_route, `$.owners[${index}].owner_route`, issues));
  if (owners.length === 0) issues.push({ code: "MISSING_OWNER", path: "$.owners", message: "at least one explicit owner route is required" });

  const termRows = list(root.terms, "$.terms", issues).map((value, index) => obj(value, `$.terms[${index}]`, issues));
  const terms = termRows.map((term, index) => ({ id: text(term.term_id, `$.terms[${index}].term_id`, issues), kind: text(term.kind, `$.terms[${index}].kind`, issues), meaning: text(term.meaning, `$.terms[${index}].meaning`, issues) }));
  const entityIds = new Set(terms.filter((term) => term.kind === "entity").map((term) => term.id));
  const actorIds = new Set(terms.filter((term) => term.kind === "actor").map((term) => term.id));
  const stateIds = new Set(terms.filter((term) => term.kind === "state").map((term) => term.id));

  const factRows = list(root.facts, "$.facts", issues).map((value, index) => obj(value, `$.facts[${index}]`, issues));
  const facts = factRows.map((fact, index) => {
    const type = text(fact.type, `$.facts[${index}].type`, issues) as ScalarType;
    if (!SCALARS.has(type)) issues.push({ code: "TYPE_MISMATCH", path: `$.facts[${index}].type`, message: `${type} is not a fact type` });
    const owner = text(fact.owner_route, `$.facts[${index}].owner_route`, issues);
    if (!owners.includes(owner)) issues.push({ code: "MISSING_OWNER", path: `$.facts[${index}].owner_route`, message: `${owner} is not declared in owners` });
    let subjectRef = "";
    if (fact.subject_ref === undefined && entityIds.size === 1) subjectRef = [...entityIds][0];
    else if (fact.subject_ref === undefined) issues.push({ code: "AMBIGUOUS_FACT_SUBJECT", path: `$.facts[${index}].subject_ref`, message: "subject_ref is required when the carrier declares more than one entity" });
    else subjectRef = text(fact.subject_ref, `$.facts[${index}].subject_ref`, issues);
    if (subjectRef && !entityIds.has(subjectRef)) issues.push({ code: "UNRESOLVED_REFERENCE", path: `$.facts[${index}].subject_ref`, message: `${subjectRef} is not a declared entity` });
    return { id: text(fact.fact_id, `$.facts[${index}].fact_id`, issues), subject_ref: subjectRef || null, type, required: fact.required === true, owner };
  });
  const factTypes = new Map(facts.map((fact) => [fact.id, fact.type]));
  const factIds = new Set(facts.map((fact) => fact.id));
  const valueObjectRows = list(root.value_objects ?? [], "$.value_objects", issues).map((value, index) => obj(value, `$.value_objects[${index}]`, issues));
  const valueObjects = valueObjectRows.map((valueObject, index) => {
    const fields = list(valueObject.fields, `$.value_objects[${index}].fields`, issues).map((value, fieldIndex) => {
      const field = obj(value, `$.value_objects[${index}].fields[${fieldIndex}]`, issues);
      const type = text(field.type, `$.value_objects[${index}].fields[${fieldIndex}].type`, issues) as ScalarType;
      if (!SCALARS.has(type)) issues.push({ code: "TYPE_MISMATCH", path: `$.value_objects[${index}].fields[${fieldIndex}].type`, message: `${type} is not a fact type` });
      return { id: text(field.fact_id, `$.value_objects[${index}].fields[${fieldIndex}].fact_id`, issues), subject_ref: null, type, required: field.required === true, owner: text(field.owner_route, `$.value_objects[${index}].fields[${fieldIndex}].owner_route`, issues) };
    });
    const equalityFields = strings(valueObject.equality_fields, `$.value_objects[${index}].equality_fields`, issues);
    const fieldIds = new Set(fields.map((field) => field.id));
    if (!fields.length) issues.push({ code: "VALUE_OBJECT_FIELDS", path: `$.value_objects[${index}].fields`, message: "value object requires typed fields" });
    requireRefs(equalityFields, fieldIds, `$.value_objects[${index}].equality_fields`, issues);
    assertUnique(equalityFields, `$.value_objects[${index}].equality_fields`, issues);
    if (!equalityFields.length) issues.push({ code: "VALUE_OBJECT_EQUALITY", path: `$.value_objects[${index}].equality_fields`, message: "value object requires an equality field set" });
    return { id: text(valueObject.value_object_id, `$.value_objects[${index}].value_object_id`, issues), fields, equality_fields: equalityFields, source_refs: strings(valueObject.source_refs ?? [], `$.value_objects[${index}].source_refs`, issues) };
  });
  const enumRows = list(root.enums ?? [], "$.enums", issues).map((value, index) => obj(value, `$.enums[${index}]`, issues));
  const enums = enumRows.map((enumRow, index) => {
    const values = list(enumRow.values, `$.enums[${index}].values`, issues).map((value, valueIndex) => { const item = obj(value, `$.enums[${index}].values[${valueIndex}]`, issues); return { id: text(item.value_id, `$.enums[${index}].values[${valueIndex}].value_id`, issues), description: text(item.description, `$.enums[${index}].values[${valueIndex}].description`, issues) }; });
    if (!values.length) issues.push({ code: "ENUM_VALUES", path: `$.enums[${index}].values`, message: "enum requires at least one described value" });
    assertUnique(values.map((value) => value.id), `$.enums[${index}].values`, issues);
    return { id: text(enumRow.enum_id, `$.enums[${index}].enum_id`, issues), values, source_refs: strings(enumRow.source_refs ?? [], `$.enums[${index}].source_refs`, issues) };
  });
  const authority = obj(root.authority, "$.authority", issues);
  const boundaryRows = list(authority.boundaries, "$.authority.boundaries", issues).map((value, index) => obj(value, `$.authority.boundaries[${index}]`, issues));
  const authorityBoundaries = boundaryRows.map((boundary, index) => text(boundary.boundary_id, `$.authority.boundaries[${index}].boundary_id`, issues));
  const boundaryIds = new Set(authorityBoundaries);
  if (authority.authority_effect !== "none") issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path: "$.authority.authority_effect", message: "compiler accepts only non-effectful carriers" });
  const refs = { facts: factIds, entities: entityIds, actors: actorIds, states: stateIds };

  const ruleRows = list(root.rules, "$.rules", issues).map((value, index) => obj(value, `$.rules[${index}]`, issues));
  const rules = ruleRows.map((rule, index) => {
    const owner = text(rule.owner_route, `$.rules[${index}].owner_route`, issues);
    if (!owners.includes(owner)) issues.push({ code: "MISSING_OWNER", path: `$.rules[${index}].owner_route`, message: `${owner} is not declared in owners` });
    return { id: text(rule.rule_id, `$.rules[${index}].rule_id`, issues), condition: requireBooleanSfolFormula(rule.condition, `$.rules[${index}].condition`, factTypes, refs, issues), owner, source_refs: strings(rule.source_refs, `$.rules[${index}].source_refs`, issues) };
  });
  const ruleIds = new Set(rules.map((rule) => rule.id));

  const eventRows = list(root.events, "$.events", issues).map((value, index) => obj(value, `$.events[${index}]`, issues));
  const events = eventRows.map((event, index) => {
    const payloadFacts = strings(event.payload_facts, `$.events[${index}].payload_facts`, issues);
    requireRefs(payloadFacts, factIds, `$.events[${index}].payload_facts`, issues);
    const boundary = event.authority_boundary_ref === null ? null : text(event.authority_boundary_ref, `$.events[${index}].authority_boundary_ref`, issues);
    if (boundary && !boundaryIds.has(boundary)) issues.push({ code: "MISSING_AUTHORITY_BOUNDARY", path: `$.events[${index}].authority_boundary_ref`, message: `${boundary} is not declared` });
    return { id: text(event.event_id, `$.events[${index}].event_id`, issues), payload_facts: payloadFacts, authority_boundary_ref: boundary };
  });
  const eventIds = new Set(events.map((event) => event.id));

  const stateRows = list(root.states, "$.states", issues).map((value, index) => obj(value, `$.states[${index}]`, issues));
  const states = stateRows.map((state, index) => ({ id: text(state.state_id, `$.states[${index}].state_id`, issues), subject_ref: text(state.subject_ref, `$.states[${index}].subject_ref`, issues) }));
  requireRefs(states.map((state) => state.subject_ref), entityIds, "$.states.subject_ref", issues);
  for (const state of states) stateIds.add(state.id);

  const permissionRows = list(root.permissions, "$.permissions", issues).map((value, index) => obj(value, `$.permissions[${index}]`, issues));
  const permissionIds = new Set(permissionRows.map((permission, index) => text(permission.permission_id, `$.permissions[${index}].permission_id`, issues)));
  const effectRows = list(root.effects ?? [], "$.effects", issues).map((value, index) => obj(value, `$.effects[${index}]`, issues));
  const effectIds = new Set(effectRows.map((effect, index) => text(effect.effect_id, `$.effects[${index}].effect_id`, issues)));
  const effects = effectRows.map((effect, index) => {
    const boundary = text(effect.authority_boundary_ref, `$.effects[${index}].authority_boundary_ref`, issues);
    if (!boundaryIds.has(boundary)) issues.push({ code: "MISSING_AUTHORITY_BOUNDARY", path: `$.effects[${index}].authority_boundary_ref`, message: `${boundary} is not declared` });
    const writeRefs = strings(effect.write_refs, `$.effects[${index}].write_refs`, issues);
    const eventRefs = strings(effect.event_refs, `$.effects[${index}].event_refs`, issues);
    requireRefs(writeRefs, entityIds, `$.effects[${index}].write_refs`, issues);
    requireRefs(eventRefs, eventIds, `$.effects[${index}].event_refs`, issues);
    const guarantee = text(effect.guarantee, `$.effects[${index}].guarantee`, issues);
    if (guarantee !== "atomic-state-and-outbox") issues.push({ code: "UNSUPPORTED_EFFECT_GUARANTEE", path: `$.effects[${index}].guarantee`, message: `${guarantee} is not supported` });
    const failure = text(effect.failure_continuation, `$.effects[${index}].failure_continuation`, issues);
    if (failure !== "rollback") issues.push({ code: "UNSUPPORTED_FAILURE_CONTINUATION", path: `$.effects[${index}].failure_continuation`, message: `${failure} is not supported` });
    return { id: text(effect.effect_id, `$.effects[${index}].effect_id`, issues), pattern_ref: text(effect.pattern_ref, `$.effects[${index}].pattern_ref`, issues), integration_binding_ref: text(effect.integration_binding_ref, `$.effects[${index}].integration_binding_ref`, issues), write_refs: writeRefs, event_refs: eventRefs, guarantee, failure_continuation: failure, authority_boundary_ref: boundary };
  });
  const actionRows = list(root.actions, "$.actions", issues).map((value, index) => obj(value, `$.actions[${index}]`, issues));
  const actionIds = new Set(actionRows.map((action, index) => text(action.action_id, `$.actions[${index}].action_id`, issues)));
  const actions = actionRows.map((action, index) => {
    const boundary = text(action.authority_boundary_ref, `$.actions[${index}].authority_boundary_ref`, issues);
    if (!boundaryIds.has(boundary)) issues.push({ code: "MISSING_AUTHORITY_BOUNDARY", path: `$.actions[${index}].authority_boundary_ref`, message: `${boundary} is not declared` });
    const actorRefs = strings(action.actor_refs, `$.actions[${index}].actor_refs`, issues);
    const subjectRefs = strings(action.subject_refs, `$.actions[${index}].subject_refs`, issues);
    const inputFacts = strings(action.input_facts, `$.actions[${index}].input_facts`, issues);
    const declarationKind = action.declaration_kind === undefined ? "action" : text(action.declaration_kind, `$.actions[${index}].declaration_kind`, issues);
    if (!['action', 'operation'].includes(declarationKind)) issues.push({ code: "OPERATION_KIND", path: `$.actions[${index}].declaration_kind`, message: "declaration kind must be action or operation" });
    const readRefs = strings(action.read_refs ?? subjectRefs, `$.actions[${index}].read_refs`, issues);
    const writeRefs = strings(action.write_refs ?? [], `$.actions[${index}].write_refs`, issues);
    const declaredEffectRefs = strings(action.effect_refs ?? [], `$.actions[${index}].effect_refs`, issues);
    const ruleRefs = strings(action.precondition_rule_refs, `$.actions[${index}].precondition_rule_refs`, issues);
    const permissionRefs = strings(action.permission_refs, `$.actions[${index}].permission_refs`, issues);
    const performs = list(action.performs ?? [], `$.actions[${index}].performs`, issues).map((value, performIndex) => {
      const row = obj(value, `$.actions[${index}].performs[${performIndex}]`, issues);
      const effectRef = text(row.effect_ref, `$.actions[${index}].performs[${performIndex}].effect_ref`, issues);
      const bindingRef = text(row.integration_binding_ref, `$.actions[${index}].performs[${performIndex}].integration_binding_ref`, issues);
      if (!effectIds.has(effectRef)) issues.push({ code: "UNRESOLVED_EFFECT", path: `$.actions[${index}].performs[${performIndex}].effect_ref`, message: `${effectRef} is not declared` });
      const effect = effects.find((candidate) => candidate.id === effectRef);
      if (effect && effect.integration_binding_ref !== bindingRef) issues.push({ code: "EFFECT_BINDING_MISMATCH", path: `$.actions[${index}].performs[${performIndex}].integration_binding_ref`, message: `${bindingRef} does not match ${effect.integration_binding_ref}` });
      return { effect_ref: effectRef, integration_binding_ref: bindingRef };
    });
    const outcomeRefs = strings(action.outcome_refs, `$.actions[${index}].outcome_refs`, issues);
    requireRefs(actorRefs, actorIds, `$.actions[${index}].actor_refs`, issues); requireRefs(subjectRefs, entityIds, `$.actions[${index}].subject_refs`, issues); requireRefs(inputFacts, factIds, `$.actions[${index}].input_facts`, issues); requireRefs(readRefs, entityIds, `$.actions[${index}].read_refs`, issues); requireRefs(writeRefs, entityIds, `$.actions[${index}].write_refs`, issues); requireRefs(declaredEffectRefs, effectIds, `$.actions[${index}].effect_refs`, issues); requireRefs(ruleRefs, ruleIds, `$.actions[${index}].precondition_rule_refs`, issues); requireRefs(permissionRefs, permissionIds, `$.actions[${index}].permission_refs`, issues); requireRefs(outcomeRefs, eventIds, `$.actions[${index}].outcome_refs`, issues);
    if (declarationKind === "operation" && !writeRefs.length) issues.push({ code: "OPERATION_WRITE_SET", path: `$.actions[${index}].write_refs`, message: "operation requires a declared write set" });
    const performedEffectRefs = performs.map((performed) => performed.effect_ref);
    if (declarationKind === "operation" && (declaredEffectRefs.length !== performedEffectRefs.length || declaredEffectRefs.some((ref) => !performedEffectRefs.includes(ref)))) issues.push({ code: "OPERATION_EFFECT_SET", path: `$.actions[${index}].effect_refs`, message: "operation effect set must exactly match performed effects" });
    for (const performed of performs) { const effect = effects.find((candidate) => candidate.id === performed.effect_ref); if (effect) for (const ref of effect.write_refs) if (!writeRefs.includes(ref) && declarationKind === "operation") issues.push({ code: "UNDECLARED_OPERATION_WRITE", path: `$.actions[${index}].write_refs`, message: `${ref} is written by ${effect.id} but not declared` }); }
    return { id: text(action.action_id, `$.actions[${index}].action_id`, issues), declaration_kind: declarationKind === "operation" ? "operation" as const : "action" as const, actor_refs: actorRefs, subject_refs: subjectRefs, input_facts: inputFacts, read_refs: readRefs, write_refs: writeRefs, effect_refs: declaredEffectRefs, precondition_rule_refs: ruleRefs, permission_refs: permissionRefs, outcome_refs: outcomeRefs, performs, authority_boundary_ref: boundary };
  });
  const permissions = permissionRows.map((permission, index) => {
    const boundary = text(permission.authority_boundary_ref, `$.permissions[${index}].authority_boundary_ref`, issues);
    if (!boundaryIds.has(boundary)) issues.push({ code: "MISSING_AUTHORITY_BOUNDARY", path: `$.permissions[${index}].authority_boundary_ref`, message: `${boundary} is not declared` });
    const actorRefs = strings(permission.actor_refs, `$.permissions[${index}].actor_refs`, issues);
    const permissionActionRefs = strings(permission.action_refs, `$.permissions[${index}].action_refs`, issues);
    requireRefs(actorRefs, actorIds, `$.permissions[${index}].actor_refs`, issues); requireRefs(permissionActionRefs, actionIds, `$.permissions[${index}].action_refs`, issues);
    return { id: text(permission.permission_id, `$.permissions[${index}].permission_id`, issues), actor_refs: actorRefs, action_refs: permissionActionRefs, condition: requireBooleanSfolFormula(permission.condition, `$.permissions[${index}].condition`, factTypes, refs, issues), authority_boundary_ref: boundary };
  });

  const transitionRows = list(root.transitions, "$.transitions", issues).map((value, index) => obj(value, `$.transitions[${index}]`, issues));
  const transitions = transitionRows.map((transition, index) => {
    const from = text(transition.from_state_ref, `$.transitions[${index}].from_state_ref`, issues); const to = text(transition.to_state_ref, `$.transitions[${index}].to_state_ref`, issues);
    requireRefs([from, to], stateIds, `$.transitions[${index}].state_refs`, issues);
    const trigger = transition.trigger_ref === null ? null : text(transition.trigger_ref, `$.transitions[${index}].trigger_ref`, issues);
    if (trigger && !actionIds.has(trigger) && !eventIds.has(trigger)) issues.push({ code: "UNRESOLVED_REFERENCE", path: `$.transitions[${index}].trigger_ref`, message: `${trigger} is neither action nor event` });
    const guardRefs = strings(transition.guard_rule_refs, `$.transitions[${index}].guard_rule_refs`, issues); const resultRefs = strings(transition.resulting_event_refs, `$.transitions[${index}].resulting_event_refs`, issues);
    requireRefs(guardRefs, ruleIds, `$.transitions[${index}].guard_rule_refs`, issues); requireRefs(resultRefs, eventIds, `$.transitions[${index}].resulting_event_refs`, issues);
    const boundary = transition.authority_boundary_ref === null ? null : text(transition.authority_boundary_ref, `$.transitions[${index}].authority_boundary_ref`, issues);
    if (boundary && !boundaryIds.has(boundary)) issues.push({ code: "MISSING_AUTHORITY_BOUNDARY", path: `$.transitions[${index}].authority_boundary_ref`, message: `${boundary} is not declared` });
    return { id: text(transition.transition_id, `$.transitions[${index}].transition_id`, issues), subject_ref: text(transition.subject_ref, `$.transitions[${index}].subject_ref`, issues), from_state_ref: from, to_state_ref: to, trigger_ref: trigger, guard_rule_refs: guardRefs, resulting_event_refs: resultRefs, authority_boundary_ref: boundary };
  });

  const queryRows = list(root.queries ?? [], "$.queries", issues).map((value, index) => obj(value, `$.queries[${index}]`, issues));
  const queries = queryRows.map((query, index) => {
    const sourceRef = text(query.source_ref, `$.queries[${index}].source_ref`, issues);
    if (!entityIds.has(sourceRef)) issues.push({ code: "UNRESOLVED_REFERENCE", path: `$.queries[${index}].source_ref`, message: `${sourceRef} is not a declared entity` });
    const inputFacts = strings(query.input_facts ?? [], `$.queries[${index}].input_facts`, issues); requireRefs(inputFacts, factIds, `$.queries[${index}].input_facts`, issues);
    const projection = strings(query.projection, `$.queries[${index}].projection`, issues); requireRefs(projection, factIds, `$.queries[${index}].projection`, issues); assertUnique(projection, `$.queries[${index}].projection`, issues);
    if (!projection.length) issues.push({ code: "QUERY_PROJECTION", path: `$.queries[${index}].projection`, message: "projection must be nonempty" });
    const orderBy = list(query.order_by ?? [], `$.queries[${index}].order_by`, issues).map((value, orderIndex) => { const order = obj(value, `$.queries[${index}].order_by[${orderIndex}]`, issues); const fieldRef = text(order.field_ref, `$.queries[${index}].order_by[${orderIndex}].field_ref`, issues); requireRefs([fieldRef], factIds, `$.queries[${index}].order_by[${orderIndex}]`, issues); const direction = text(order.direction, `$.queries[${index}].order_by[${orderIndex}].direction`, issues); if (!["asc", "desc"].includes(direction)) issues.push({ code: "QUERY_ORDER", path: `$.queries[${index}].order_by[${orderIndex}].direction`, message: "direction must be asc or desc" }); return { field_ref: fieldRef, direction: (direction === "desc" ? "desc" : "asc") as "asc" | "desc" }; });
    const limit = query.limit === null || query.limit === undefined ? null : Number(query.limit); if (limit !== null && (!Number.isSafeInteger(limit) || limit <= 0)) issues.push({ code: "QUERY_LIMIT", path: `$.queries[${index}].limit`, message: "limit must be a positive safe integer" });
    const predicate = query.predicate === null || query.predicate === undefined ? null : requireBooleanSfolFormula(query.predicate, `$.queries[${index}].predicate`, factTypes, refs, issues);
    return { id: text(query.query_id, `$.queries[${index}].query_id`, issues), source_ref: sourceRef, input_facts: inputFacts, predicate, order_by: orderBy, limit, projection, source_refs: strings(query.source_refs ?? [], `$.queries[${index}].source_refs`, issues) };
  });
  const calculationRows = list(root.calculations ?? [], "$.calculations", issues).map((value, index) => obj(value, `$.calculations[${index}]`, issues));
  const calculations = calculationRows.map((calculation, index) => {
    const inputFacts = strings(calculation.input_facts, `$.calculations[${index}].input_facts`, issues); requireRefs(inputFacts, factIds, `$.calculations[${index}].input_facts`, issues); assertUnique(inputFacts, `$.calculations[${index}].input_facts`, issues);
    for (const ref of inputFacts) if (factTypes.get(ref) !== "integer") issues.push({ code: "TYPE_MISMATCH", path: `$.calculations[${index}].input_facts`, message: `${ref} must have integer type` });
    const rounding = text(calculation.rounding, `$.calculations[${index}].rounding`, issues); if (!["floor", "ceil", "reject"].includes(rounding)) issues.push({ code: "CALCULATION_ROUNDING", path: `$.calculations[${index}].rounding`, message: "rounding must be floor, ceil, or reject" });
    return { id: text(calculation.calculation_id, `$.calculations[${index}].calculation_id`, issues), input_facts: inputFacts, expression: validateSfolUInt64Term(calculation.expression, `$.calculations[${index}].expression`, new Set(inputFacts), issues), rounding: (["floor", "ceil"].includes(rounding) ? rounding : "reject") as "floor" | "ceil" | "reject", source_refs: strings(calculation.source_refs ?? [], `$.calculations[${index}].source_refs`, issues) };
  });
  const calculationIds = new Set(calculations.map((item) => item.id));
  const mappingRows = list(root.mappings ?? [], "$.mappings", issues).map((value, index) => obj(value, `$.mappings[${index}]`, issues));
  const mappings = mappingRows.map((mapping, index) => {
    const sourceRef = text(mapping.source_ref, `$.mappings[${index}].source_ref`, issues); const targetRef = text(mapping.target_ref, `$.mappings[${index}].target_ref`, issues); requireRefs([sourceRef, targetRef], entityIds, `$.mappings[${index}]`, issues);
    const clauses = list(mapping.clauses, `$.mappings[${index}].clauses`, issues).map((value, clauseIndex) => { const clause = obj(value, `$.mappings[${index}].clauses[${clauseIndex}]`, issues); const targetField = text(clause.target_field, `$.mappings[${index}].clauses[${clauseIndex}].target_field`, issues); requireRefs([targetField], factIds, `$.mappings[${index}].clauses[${clauseIndex}].target_field`, issues); const sourceField = clause.source_field === null || clause.source_field === undefined ? null : text(clause.source_field, `$.mappings[${index}].clauses[${clauseIndex}].source_field`, issues); if (sourceField) { requireRefs([sourceField], factIds, `$.mappings[${index}].clauses[${clauseIndex}].source_field`, issues); if (factTypes.get(sourceField) !== factTypes.get(targetField)) issues.push({ code: "TYPE_MISMATCH", path: `$.mappings[${index}].clauses[${clauseIndex}]`, message: `${sourceField} and ${targetField} types differ` }); } const defaultRow = clause.default_value === null || clause.default_value === undefined ? null : obj(clause.default_value, `$.mappings[${index}].clauses[${clauseIndex}].default_value`, issues); const defaultValue = defaultRow ? { value_type: text(defaultRow.value_type, `$.mappings[${index}].clauses[${clauseIndex}].default_value.value_type`, issues) as ScalarType, value: defaultRow.value } : null; if (defaultValue && defaultValue.value_type !== factTypes.get(targetField)) issues.push({ code: "TYPE_MISMATCH", path: `$.mappings[${index}].clauses[${clauseIndex}].default_value`, message: "default type differs from target field" }); if (!sourceField && !defaultValue) issues.push({ code: "MAPPING_CLAUSE", path: `$.mappings[${index}].clauses[${clauseIndex}]`, message: "mapping clause needs a source or default" }); return { target_field: targetField, source_field: sourceField, default_value: defaultValue }; });
    assertUnique(clauses.map((item) => item.target_field), `$.mappings[${index}].clauses`, issues); if (!clauses.length) issues.push({ code: "MAPPING_CLAUSE", path: `$.mappings[${index}].clauses`, message: "mapping requires at least one clause" });
    return { id: text(mapping.mapping_id, `$.mappings[${index}].mapping_id`, issues), source_ref: sourceRef, target_ref: targetRef, total: mapping.total === true, clauses, source_refs: strings(mapping.source_refs ?? [], `$.mappings[${index}].source_refs`, issues) };
  });
  const policyRows = list(root.policies ?? [], "$.policies", issues).map((value, index) => obj(value, `$.policies[${index}]`, issues));
  const policyTargets = new Set([...actionIds, ...calculationIds]);
  const policies = policyRows.map((policy, index) => { const inputFacts = strings(policy.input_facts, `$.policies[${index}].input_facts`, issues); requireRefs(inputFacts, factIds, `$.policies[${index}].input_facts`, issues); const cases = list(policy.cases, `$.policies[${index}].cases`, issues).map((value, caseIndex) => { const item = obj(value, `$.policies[${index}].cases[${caseIndex}]`, issues); const targetRef = text(item.target_ref, `$.policies[${index}].cases[${caseIndex}].target_ref`, issues); requireRefs([targetRef], policyTargets, `$.policies[${index}].cases[${caseIndex}].target_ref`, issues); return { predicate: requireBooleanSfolFormula(item.predicate, `$.policies[${index}].cases[${caseIndex}].predicate`, factTypes, refs, issues), target_ref: targetRef }; }); if (!cases.length) issues.push({ code: "POLICY_CASE", path: `$.policies[${index}].cases`, message: "policy requires at least one ordered case" }); const defaultTarget = text(policy.default_target_ref, `$.policies[${index}].default_target_ref`, issues); requireRefs([defaultTarget], policyTargets, `$.policies[${index}].default_target_ref`, issues); return { id: text(policy.policy_id, `$.policies[${index}].policy_id`, issues), input_facts: inputFacts, cases, default_target_ref: defaultTarget, source_refs: strings(policy.source_refs ?? [], `$.policies[${index}].source_refs`, issues) }; });

  const workflowRows = list(root.workflows ?? [], "$.workflows", issues).map((value, index) => obj(value, `$.workflows[${index}]`, issues));
  const workflows = workflowRows.map((workflow, index) => { const scope = text(workflow.scope, `$.workflows[${index}].scope`, issues); if (!['intra-feature', 'cross-feature'].includes(scope)) issues.push({ code: "WORKFLOW_SCOPE", path: `$.workflows[${index}].scope`, message: "scope must be intra-feature or cross-feature" }); const stepRefs = strings(workflow.step_refs, `$.workflows[${index}].step_refs`, issues); if (stepRefs.length < 2) issues.push({ code: "WORKFLOW_STEPS", path: `$.workflows[${index}].step_refs`, message: "workflow requires at least two ordered steps" }); requireRefs(stepRefs, actionIds, `$.workflows[${index}].step_refs`, issues); return { id: text(workflow.workflow_id, `$.workflows[${index}].workflow_id`, issues), scope: scope === 'cross-feature' ? 'cross-feature' as const : 'intra-feature' as const, step_refs: stepRefs, source_refs: strings(workflow.source_refs ?? [], `$.workflows[${index}].source_refs`, issues) }; });
  const queryIds = new Set(queries.map((query) => query.id));
  const interfaceRows = list(root.interfaces ?? [], "$.interfaces", issues).map((value, index) => obj(value, `$.interfaces[${index}]`, issues));
  const interfaceTargets = new Set([...actionIds, ...queryIds]);
  const interfaces = interfaceRows.map((interfaceRow, index) => { const kind = text(interfaceRow.interface_kind, `$.interfaces[${index}].interface_kind`, issues); if (!['internal', 'external'].includes(kind)) issues.push({ code: "INTERFACE_KIND", path: `$.interfaces[${index}].interface_kind`, message: "interface kind must be internal or external" }); const exposureRefs = strings(interfaceRow.exposure_refs, `$.interfaces[${index}].exposure_refs`, issues); if (!exposureRefs.length) issues.push({ code: "INTERFACE_EXPOSURES", path: `$.interfaces[${index}].exposure_refs`, message: "interface requires at least one exposure" }); requireRefs(exposureRefs, interfaceTargets, `$.interfaces[${index}].exposure_refs`, issues); return { id: text(interfaceRow.interface_id, `$.interfaces[${index}].interface_id`, issues), interface_kind: kind === 'external' ? 'external' as const : 'internal' as const, exposure_refs: exposureRefs, source_refs: strings(interfaceRow.source_refs ?? [], `$.interfaces[${index}].source_refs`, issues) }; });

  const edgeRows = list(root.edges, "$.edges", issues).map((value, index) => obj(value, `$.edges[${index}]`, issues));
  const edges = edgeRows.map((edge, index) => ({ id: text(edge.edge_id, `$.edges[${index}].edge_id`, issues), type: text(edge.type, `$.edges[${index}].type`, issues), source: text(edge.source_ref, `$.edges[${index}].source_ref`, issues), target: text(edge.target_ref, `$.edges[${index}].target_ref`, issues) }));
  const semanticEdges = actions.flatMap((action) => [
    ...action.read_refs.map((target) => ({ id: `${action.id}-reads-${target}`, type: "reads", source: action.id, target })),
    ...action.write_refs.map((target) => ({ id: `${action.id}-mutates-${target}`, type: "mutates", source: action.id, target })),
    ...action.outcome_refs.map((target) => ({ id: `${action.id}-produces-${target}`, type: "produces", source: action.id, target })),
    ...action.performs.flatMap((performed) => {
    const effect = effects.find((candidate) => candidate.id === performed.effect_ref);
    if (!effect) return [];
    return [
      { id: `${action.id}-performs-${effect.id}`, type: "performs", source: action.id, target: effect.id },
      { id: `${effect.id}-instantiates-${effect.pattern_ref}`, type: "instantiates", source: effect.id, target: effect.pattern_ref },
      { id: `${effect.id}-uses-${effect.integration_binding_ref}`, type: "uses", source: effect.id, target: effect.integration_binding_ref },
      ...effect.write_refs.map((target) => ({ id: `${effect.id}-writes-${target}`, type: "writes", source: effect.id, target })),
      ...effect.event_refs.map((target) => ({ id: `${effect.id}-emits-${target}`, type: "emits", source: effect.id, target }))
    ];
    })
  ]).concat(workflows.flatMap((workflow) => workflow.step_refs.map((target, index) => ({ id: `${workflow.id}-orchestrates-${index}-${target}`, type: "orchestrates", source: workflow.id, target })))).concat(interfaces.flatMap((contract) => contract.exposure_refs.map((target) => ({ id: `${contract.id}-exposes-${target}`, type: "exposes", source: contract.id, target }))));
  const externalSemanticIds = new Set(effects.flatMap((effect) => [effect.pattern_ref, effect.integration_binding_ref]));
  const allSemanticIds = new Set([...terms.map((term) => term.id), ...facts.map((fact) => fact.id), ...rules.map((rule) => rule.id), ...events.map((event) => event.id), ...states.map((state) => state.id), ...effects.map((effect) => effect.id), ...actions.map((action) => action.id), ...permissions.map((permission) => permission.id), ...queries.map((item) => item.id), ...calculations.map((item) => item.id), ...mappings.map((item) => item.id), ...policies.map((item) => item.id), ...workflows.map((item) => item.id), ...interfaces.map((item) => item.id), ...authorityBoundaries, ...externalSemanticIds]);
  edges.push(...semanticEdges);
  for (const [index, edge] of edges.entries()) requireRefs([edge.source, edge.target], allSemanticIds, `$.edges[${index}]`, issues);

  const examples = list(root.examples, "$.examples", issues).map((value, index) => obj(value, `$.examples[${index}]`, issues)).map((example, index) => ({ id: text(example.example_id, `$.examples[${index}].example_id`, issues), kind: text(example.kind, `$.examples[${index}].kind`, issues), expected: text(example.expected_interpretation, `$.examples[${index}].expected_interpretation`, issues), affected_rule_refs: strings(example.affected_rule_refs, `$.examples[${index}].affected_rule_refs`, issues) }));
  for (const [index, example] of examples.entries()) requireRefs(example.affected_rule_refs, ruleIds, `$.examples[${index}].affected_rule_refs`, issues);

  for (const [name, ids] of Object.entries({ terms: terms.map((x) => x.id), facts: facts.map((x) => x.id), value_objects: valueObjects.map((x) => x.id), enums: enums.map((x) => x.id), rules: rules.map((x) => x.id), events: events.map((x) => x.id), states: states.map((x) => x.id), effects: effects.map((x) => x.id), actions: actions.map((x) => x.id), permissions: permissions.map((x) => x.id), queries: queries.map((x) => x.id), calculations: calculations.map((x) => x.id), mappings: mappings.map((x) => x.id), policies: policies.map((x) => x.id), workflows: workflows.map((x) => x.id), interfaces: interfaces.map((x) => x.id), boundaries: authorityBoundaries })) assertUnique(ids, `$.${name}`, issues);
  const residue = list(root.residue, "$.residue", issues).map((value, index) => obj(value, `$.residue[${index}]`, issues)).map((item, index) => ({ code: text(item.code, `$.residue[${index}].code`, issues), subject_ref: text(item.subject_ref, `$.residue[${index}].subject_ref`, issues), owner_route: text(item.owner_route, `$.residue[${index}].owner_route`, issues), detail: text(item.detail, `$.residue[${index}].detail`, issues) }));
  return { schema_version: text(root.schema_version, "$.schema_version", issues), logic_profile: SFOL_PROFILE, domain_id: domainId, title, owners, terms, edges, facts, value_objects: valueObjects, enums, rules, events, states, transitions, effects, actions, permissions, queries, calculations, mappings, policies, workflows, interfaces, examples, authority_boundaries: authorityBoundaries, authority_effect: "none", residue, metadata: {} };
}

function normalizeLegacy(root: Obj, issues: CompilerIssue[]): NormalizedDomain {
  const domainId = text(root.domain_id, "$.domain_id", issues); const owner = text(root.owner_route, "$.owner_route", issues);
  if (root.authority_effect !== "none") issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path: "$.authority_effect", message: "compiler accepts only non-effectful carriers" });
  const termRows = list(root.terms, "$.terms", issues).map((value, index) => obj(value, `$.terms[${index}]`, issues));
  const terms = termRows.map((term, index) => ({ id: text(term.id, `$.terms[${index}].id`, issues), kind: "concept", meaning: text(term.meaning, `$.terms[${index}].meaning`, issues) }));
  const subject = obj(root.primary_subject, "$.primary_subject", issues); const subjectId = text(subject.term_id, "$.primary_subject.term_id", issues);
  const subjectTerm = terms.find((term) => term.id === subjectId); if (subjectTerm) subjectTerm.kind = "entity"; else issues.push({ code: "UNRESOLVED_REFERENCE", path: "$.primary_subject.term_id", message: `${subjectId} is not a term` });
  const fields = list(subject.fields, "$.primary_subject.fields", issues).map((value, index) => obj(value, `$.primary_subject.fields[${index}]`, issues));
  const facts = fields.map((field, index) => { const rawType = text(field.type, `$.primary_subject.fields[${index}].type`, issues); const type: ScalarType = rawType === "uuid" ? "identifier" : rawType as ScalarType; if (!SCALARS.has(type)) issues.push({ code: "TYPE_MISMATCH", path: `$.primary_subject.fields[${index}].type`, message: `${rawType} is not supported` }); return { id: text(field.id, `$.primary_subject.fields[${index}].id`, issues), subject_ref: subjectId, type, required: field.required === true, owner }; });
  const boundaries = list(root.authority_boundaries, "$.authority_boundaries", issues).map((value, index) => obj(value, `$.authority_boundaries[${index}]`, issues)); const authorityBoundaries = boundaries.map((boundary, index) => text(boundary.id, `$.authority_boundaries[${index}].id`, issues)); const boundaryIds = new Set(authorityBoundaries);
  const ruleRows = list(root.rules, "$.rules", issues).map((value, index) => obj(value, `$.rules[${index}]`, issues)); const rules = ruleRows.map((rule, index) => ({ id: text(rule.id, `$.rules[${index}].id`, issues), condition: { legacy_predicate: text(rule.predicate, `$.rules[${index}].predicate`, issues) }, owner, source_refs: [] })); const ruleIds = new Set(rules.map((rule) => rule.id));
  const eventRows = list(root.events, "$.events", issues).map((value, index) => obj(value, `$.events[${index}]`, issues)); const events = eventRows.map((event, index) => ({ id: text(event.id, `$.events[${index}].id`, issues), payload_facts: strings(event.payload, `$.events[${index}].payload`, issues), authority_boundary_ref: null })); const eventIds = new Set(events.map((event) => event.id));
  const permissionRows = list(root.permissions, "$.permissions", issues).map((value, index) => obj(value, `$.permissions[${index}]`, issues)); const permissions = permissionRows.map((permission, index) => ({ id: text(permission.id, `$.permissions[${index}].id`, issues), actor_refs: [text(permission.actor, `$.permissions[${index}].actor`, issues)], action_refs: [text(permission.action_ref, `$.permissions[${index}].action_ref`, issues)], condition: { legacy_condition: text(permission.condition, `$.permissions[${index}].condition`, issues) }, authority_boundary_ref: "" }));
  const actionRows = list(root.actions, "$.actions", issues).map((value, index) => obj(value, `$.actions[${index}]`, issues)); const actions = actionRows.map((action, index) => { const boundary = text(action.authority_boundary_ref, `$.actions[${index}].authority_boundary_ref`, issues); if (!boundaryIds.has(boundary)) issues.push({ code: "MISSING_AUTHORITY_BOUNDARY", path: `$.actions[${index}].authority_boundary_ref`, message: `${boundary} is not declared` }); const ruleRefs = strings(action.rule_refs, `$.actions[${index}].rule_refs`, issues); requireRefs(ruleRefs, ruleIds, `$.actions[${index}].rule_refs`, issues); const outcomeRefs = strings(action.event_refs, `$.actions[${index}].event_refs`, issues); requireRefs(outcomeRefs, eventIds, `$.actions[${index}].event_refs`, issues); const subjectRefs = strings(action.reads, `$.actions[${index}].reads`, issues).filter((ref) => !ref.includes(".")); return { id: text(action.id, `$.actions[${index}].id`, issues), declaration_kind: "action" as const, actor_refs: [], subject_refs: subjectRefs, input_facts: [], read_refs: subjectRefs, write_refs: [], effect_refs: [], precondition_rule_refs: ruleRefs, permission_refs: permissions.filter((permission) => permission.action_refs.includes(String(action.id))).map((permission) => permission.id), outcome_refs: outcomeRefs, performs: [], authority_boundary_ref: boundary }; });
  const actionIds = new Set(actions.map((action) => action.id)); for (const [index, permission] of permissions.entries()) { requireRefs(permission.action_refs, actionIds, `$.permissions[${index}].action_ref`, issues); const action = actions.find((item) => item.id === permission.action_refs[0]); permission.authority_boundary_ref = action?.authority_boundary_ref ?? ""; }
  const machine = obj(root.state_machine, "$.state_machine", issues); const states = strings(machine.states, "$.state_machine.states", issues).map((id) => ({ id, subject_ref: subjectId })); const stateIds = new Set(states.map((state) => state.id));
  const transitions = list(machine.transitions, "$.state_machine.transitions", issues).map((value, index) => obj(value, `$.state_machine.transitions[${index}]`, issues)).map((transition, index) => { const from = text(transition.from, `$.state_machine.transitions[${index}].from`, issues); const to = text(transition.to, `$.state_machine.transitions[${index}].to`, issues); requireRefs([from, to], stateIds, `$.state_machine.transitions[${index}]`, issues); const ruleRef = transition.rule_ref === null ? null : text(transition.rule_ref, `$.state_machine.transitions[${index}].rule_ref`, issues); if (ruleRef) requireRefs([ruleRef], ruleIds, `$.state_machine.transitions[${index}].rule_ref`, issues); const eventRef = transition.event_ref === null ? null : text(transition.event_ref, `$.state_machine.transitions[${index}].event_ref`, issues); if (eventRef) requireRefs([eventRef], eventIds, `$.state_machine.transitions[${index}].event_ref`, issues); return { id: text(transition.id, `$.state_machine.transitions[${index}].id`, issues), subject_ref: subjectId, from_state_ref: from, to_state_ref: to, trigger_ref: null, guard_rule_refs: ruleRef ? [ruleRef] : [], resulting_event_refs: eventRef ? [eventRef] : [], authority_boundary_ref: null }; });
  const edges = list(root.ontology_edges, "$.ontology_edges", issues).map((value, index) => obj(value, `$.ontology_edges[${index}]`, issues)).map((edge, index) => ({ id: text(edge.id, `$.ontology_edges[${index}].id`, issues), type: text(edge.type, `$.ontology_edges[${index}].type`, issues), source: text(edge.source, `$.ontology_edges[${index}].source`, issues), target: text(edge.target, `$.ontology_edges[${index}].target`, issues) }));
  const examples = list(root.examples, "$.examples", issues).map((value, index) => obj(value, `$.examples[${index}]`, issues)).map((example, index) => ({ id: text(example.id, `$.examples[${index}].id`, issues), kind: text(example.kind, `$.examples[${index}].kind`, issues), expected: text(example.expected, `$.examples[${index}].expected`, issues), affected_rule_refs: [] }));
  const residue = rules.map((rule) => ({ code: "LEGACY_OPAQUE_PREDICATE", subject_ref: rule.id, owner_route: owner, detail: "Retained for traceability; not executable until migrated to the carrier-v2 typed AST." }));
  return { schema_version: text(root.schema_version, "$.schema_version", issues), logic_profile: "legacy-opaque-predicate", domain_id: domainId, title: text(root.title, "$.title", issues), owners: [owner], terms, edges, facts, value_objects: [], enums: [], rules, events, states, transitions, effects: [], actions, permissions, queries: [], calculations: [], mappings: [], policies: [], workflows: [], interfaces: [], examples, authority_boundaries: authorityBoundaries, authority_effect: "none", residue, metadata: { runtime_profile: root.runtime_profile, compatibility_mode: "v1-reference" } };
}

export function validateAndNormalize(input: unknown): NormalizedDomain {
  const issues: CompilerIssue[] = []; const root = obj(input, "$", issues); const version = text(root.schema_version, "$.schema_version", issues);
  const model = version === "cav2.alchlang.carrier/v2-candidate" ? normalizeV2(root, issues) : version === "alchlang.governed-domain-description/v1-candidate" ? normalizeLegacy(root, issues) : (() => { issues.push({ code: "UNSUPPORTED_SEMANTIC_CONSTRUCT", path: "$.schema_version", message: `${version} is not supported` }); return normalizeV2(root, issues); })();
  if (issues.length) throw new CompilationRejected(issues);
  return model;
}
