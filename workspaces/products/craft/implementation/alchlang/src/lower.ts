import type { CompilationPlan, NormalizedDomain } from "./model.js";

export function lower(model: NormalizedDomain): CompilationPlan {
  const subjects = model.terms.filter((term) => term.kind === "entity");
  const stateSubjectIds = new Set([...model.states.map((state) => state.subject_ref), ...model.transitions.map((transition) => transition.subject_ref)]);
  const nodeCandidates = [
    ...model.terms.map((term) => ({ id: term.id, kind: term.kind })),
    ...model.facts.map((fact) => ({ id: fact.id, kind: "fact" })),
    ...model.rules.map((rule) => ({ id: rule.id, kind: "rule" })),
    ...model.events.map((event) => ({ id: event.id, kind: "event" })),
    ...model.effects.map((effect) => ({ id: effect.id, kind: "effect" })),
    ...model.actions.map((action) => ({ id: action.id, kind: action.declaration_kind })),
    ...model.queries.map((query) => ({ id: query.id, kind: "query" })),
    ...model.calculations.map((calculation) => ({ id: calculation.id, kind: "calculation" })),
    ...model.mappings.map((mapping) => ({ id: mapping.id, kind: "mapping" })),
    ...model.policies.map((policy) => ({ id: policy.id, kind: "policy" })),
  ];
  const nodeById = new Map<string, { id: string; kind: string }>();
  for (const node of nodeCandidates) {
    // Specialized normalized collections follow generic terms, so they win
    // when a legacy carrier uses one ID for both views of the same concept.
    nodeById.set(node.id, node);
  }
  const nodes = [...nodeById.values()].sort((a, b) => a.id.localeCompare(b.id));
  return {
    model,
    type_model: subjects.map((subject) => ({ id: subject.id, fields: model.facts.filter((fact) => fact.subject_ref === subject.id) })),
    value_object_contracts: model.value_objects,
    enum_contracts: model.enums,
    sfol_logic_model: { profile: model.logic_profile, formulas: model.rules, terms: model.calculations },
    predicate_model: model.rules,
    event_contracts: model.events,
    state_machines: subjects.filter((subject) => stateSubjectIds.has(subject.id)).map((subject) => ({ subject_ref: subject.id, states: model.states.filter((state) => state.subject_ref === subject.id).map((state) => state.id), transitions: model.transitions.filter((transition) => transition.subject_ref === subject.id) })),
    effect_contracts: model.effects,
    action_ports: model.actions,
    operation_contracts: model.actions.filter((action) => action.declaration_kind === "operation"),
    permission_guards: model.permissions,
    query_contracts: model.queries,
    calculation_contracts: model.calculations,
    mapping_contracts: model.mappings,
    policy_contracts: model.policies,
    workflow_contracts: model.workflows,
    interface_contracts: model.interfaces,
    test_obligations: model.examples.map((example) => ({ id: example.id, kind: example.kind, expected: example.expected, rule_refs: example.affected_rule_refs })),
    documentation_model: { title: model.title, term_count: model.terms.length, rule_count: model.rules.length, claim_ceiling: "Target-neutral candidate output; no acceptance, execution, or effect authority." },
    graph_model: { nodes, edges: [...model.edges].sort((a, b) => a.id.localeCompare(b.id)) },
    trace_ledger: [
      ...model.rules.map((rule) => ({ output_ref: `predicate_model:${rule.id}`, source_refs: rule.source_refs.length ? rule.source_refs : [`rule:${rule.id}`] })),
      ...model.actions.map((action) => ({ output_ref: `action_port:${action.id}`, source_refs: [`action:${action.id}`, ...action.precondition_rule_refs.map((id) => `rule:${id}`)] })),
      ...model.effects.map((effect) => ({ output_ref: `effect_contract:${effect.id}`, source_refs: [`effect:${effect.id}`, `pattern:${effect.pattern_ref}`, `binding:${effect.integration_binding_ref}`] })),
      ...model.events.map((event) => ({ output_ref: `event_contract:${event.id}`, source_refs: [`event:${event.id}`] })),
      ...model.queries.map((query) => ({ output_ref: `query_contract:${query.id}`, source_refs: query.source_refs.length ? query.source_refs : [`query:${query.id}`] })),
      ...model.calculations.map((calculation) => ({ output_ref: `calculation_contract:${calculation.id}`, source_refs: calculation.source_refs.length ? calculation.source_refs : [`calculation:${calculation.id}`] })),
      ...model.mappings.map((mapping) => ({ output_ref: `mapping_contract:${mapping.id}`, source_refs: mapping.source_refs.length ? mapping.source_refs : [`mapping:${mapping.id}`] })),
      ...model.policies.map((policy) => ({ output_ref: `policy_contract:${policy.id}`, source_refs: policy.source_refs.length ? policy.source_refs : [`policy:${policy.id}`] })),
      ...model.value_objects.map((valueObject) => ({ output_ref: `value_object_contract:${valueObject.id}`, source_refs: valueObject.source_refs.length ? valueObject.source_refs : [`value-object:${valueObject.id}`] })),
      ...model.enums.map((enumContract) => ({ output_ref: `enum_contract:${enumContract.id}`, source_refs: enumContract.source_refs.length ? enumContract.source_refs : [`enum:${enumContract.id}`] })),
      ...model.workflows.map((workflow) => ({ output_ref: `workflow_contract:${workflow.id}`, source_refs: workflow.source_refs.length ? workflow.source_refs : [`workflow:${workflow.id}`] })),
      ...model.interfaces.map((interfaceContract) => ({ output_ref: `interface_contract:${interfaceContract.id}`, source_refs: interfaceContract.source_refs.length ? interfaceContract.source_refs : [`interface:${interfaceContract.id}`] })),
    ].sort((a, b) => a.output_ref.localeCompare(b.output_ref)),
    unsupported_residue: model.residue,
  };
}
