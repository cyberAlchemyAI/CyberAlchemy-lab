import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import { lowerApplicationDomain, type ApplicationPersistenceContext, type ApplicationMessagingContext, type ApplicationExternalApiContext, type ApplicationRuntimeContext } from "./application-domain-lowering.js";
import type { FormalProposition, FormalTerm } from "./formal-claim.js";
import { projectApplicationQueries } from "./application-query-projection.js";
import {assertDirectBusinessFormationV2Current,type DirectBusinessFormationV2} from './application-domain-lowering.js';
import type {BusinessSourceSpan} from './business-authoring-protocol.js';
import {businessCanonical,businessHash,businessReject,freezeBusinessData} from './business-authoring-model.js';

export interface DirectRuleSourceProjectionV2 {
 readonly kind:'direct-rule-source-projection-v2';readonly formation:DirectBusinessFormationV2;
 readonly selector:string;readonly source:BusinessSourceSpan;readonly parameter:string;
 readonly entity_selector:string;readonly field_name:string;readonly property_selector:string;
 readonly typed_contract:Readonly<{schema_version:'domainspec.typed-rule/v1';ontology_rule:string;parameters:readonly Readonly<{name:string;type:Readonly<{kind:'named';selector:string}>}>[];expression:Readonly<{op:'eq';left:Readonly<{op:'path';root:string;properties:readonly [string]}>;right:Readonly<{op:'literal';type:'Bool';value:true}>}>}>;
 readonly projection_sha256:string;readonly authority_effect:'none';
}
const directRules=new WeakMap<object,{formation:DirectBusinessFormationV2;fingerprint:string}>();
/** A direct typed projection never enters lowerApplicationRuleProjections' legacy
 * FormalClaim path. Open Questions: Core direct owner join at L02/G01. */
export function projectDirectBusinessRuleV2(formation:DirectBusinessFormationV2):DirectRuleSourceProjectionV2 {
 assertDirectBusinessFormationV2Current(formation);
 const rule=formation.lowered.business.data.rules[0]!,property=formation.properties.find(field=>field.name===rule.condition.value.path[0]);
 if(!property||property.type!=='Bool'||rule.condition.value.root!==rule.input.name)businessReject('BUSINESS_DIRECT_CONDITION',formation.lowered.business.source.path,formation.origins.condition.line,3,'explicit Bool field condition required');
 const [feature,id]=formation.selectors.rule.split(':'),node=JSON.parse(formation.projectFiles[`specs/${feature}/nodes/${id}.json`]!);
 const typed:DirectRuleSourceProjectionV2['typed_contract']={schema_version:'domainspec.typed-rule/v1',ontology_rule:'BUSINESS-'+feature!.toUpperCase()+'-'+id!.toUpperCase(),parameters:[{name:rule.input.name,type:{kind:'named',selector:formation.selectors.entity}}],expression:{op:'eq',left:{op:'path',root:rule.input.name,properties:[property.ontology_property]},right:{op:'literal',type:'Bool',value:true}}};
 if(businessCanonical(node.body.typed_contract)!==businessCanonical(typed))businessReject('BUSINESS_DIRECT_CONDITION',formation.lowered.business.source.path,formation.origins.condition.line,3,'typed Rule differs from original condition');
 const data={selector:formation.selectors.rule,source:formation.origins.condition,parameter:rule.input.name,entity_selector:formation.selectors.entity,field_name:property.name,property_selector:property.ontology_property,typed_contract:typed};
 const result=freezeBusinessData<DirectRuleSourceProjectionV2>({kind:'direct-rule-source-projection-v2',formation,...data,projection_sha256:businessHash(businessCanonical(data)),authority_effect:'none'},formation.lowered.business.source.path);
 directRules.set(result,{formation,fingerprint:businessHash(businessCanonical(result))});assertDirectRuleSourceProjectionV2Current(result);return result;
}
export function assertDirectRuleSourceProjectionV2Current(value:DirectRuleSourceProjectionV2):void {
 const state=value&&typeof value==='object'?directRules.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original direct Rule projection required');
 assertDirectBusinessFormationV2Current(state.formation);
 if(value.formation!==state.formation||businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',state.formation.lowered.business.source.path,1,1,'direct Rule projection changed');
}

type Obj = Record<string, unknown>;
const fail = (code: string, path: string, message: string): never => { throw new CompilationRejected([{ code, path, message }]); };
function object(value: unknown, path: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) return fail("RULE_PROJECTION_SCHEMA", path, "expected object");
  return value as Obj;
}
function exact(value: unknown, keys: string[], path: string): Obj {
  const row = object(value, path);
  if (json(Object.keys(row).sort()) !== json([...keys].sort())) fail("RULE_PROJECTION_SCHEMA", path, "unexpected or missing binding");
  return row;
}
function text(value: unknown, path: string): string {
  if (typeof value !== "string" || !value.trim()) return fail("RULE_PROJECTION_SCHEMA", path, "explicit text required");
  return value;
}

/** Ground property/scalar interpretation only. No quantifier narrowing or proof. */
export function lowerApplicationRuleProjections(source: string, bindings: unknown, sources: ReadonlyMap<string, Buffer>, interpretation: unknown, persistenceContext?: ApplicationPersistenceContext, messagingContext?: ApplicationMessagingContext, externalApiContext?: ApplicationExternalApiContext, runtimeContext?: ApplicationRuntimeContext) {
  const formation = lowerApplicationDomain(source, bindings, sources, persistenceContext, messagingContext, externalApiContext, runtimeContext);
  const root = exact(interpretation, ["schema_version", "formation_sha256", "rules"], "$interpretation");
  if (root.schema_version !== "alchlang.ground-rule-interpretation/v1-candidate" || root.formation_sha256 !== digest(json(formation))) {
    fail("RULE_PROJECTION_STALE", "$interpretation", "interpretation must bind the exact current formation");
  }
  const selected = exact(root.rules, formation.model.rules.map(r => r.id), "$interpretation/rules");
  const projectFiles = { ...formation.projectFiles };
  const declarationBindings = object(object(bindings, "$bindings").declarations, "$bindings/declarations");
  const projections: Obj[] = [];
  for (const rule of formation.model.rules) {
    const at = `$interpretation/rules/${rule.id}`;
    const row = exact(selected[rule.id], ["claim_identity_inputs_digest", "context_id", "ceiling", "sorts", "constants", "predicates"], at);
    const claim = formation.model.formal_claims.find(c => c.id === rule.claim_ref)!;
    const claimTrace = formation.trace.declarations.find(t => t.source_id === claim.id)!;
    if (row.claim_identity_inputs_digest !== claimTrace.identity_inputs_digest) fail("RULE_PROJECTION_STALE", at, "claim identity differs");
    const contextId = text(row.context_id, at); const ceiling = text(row.ceiling, at);
    if (claim.signature.functions.length) fail("RULE_PROJECTION_UNSUPPORTED", at, "function interpretations are not implemented by this ground property projection");
    const sorts = exact(row.sorts, claim.signature.sorts.map(s => s.name), at);
    const constants = exact(row.constants, claim.signature.constants.map(c => c.name), at);
    const predicates = exact(row.predicates, claim.signature.predicates.map(p => p.name), at);
    const sortEntities = new Map<string, string>();
    const sortTypes = new Map<string, Obj>();
    for (const sort of claim.signature.sorts) {
      const id = text(sorts[sort.name], at);
      if (["String", "Bool", "UInt64"].includes(id)) { sortTypes.set(sort.name, { kind: "scalar", name: id }); continue; }
      if (!formation.model.declarations.some(d => d.kind === "entity" && d.id === id)) fail("RULE_PROJECTION_SORT", at, "sort must explicitly select a declared Entity");
      sortEntities.set(sort.name, id);
      sortTypes.set(sort.name, { kind: "named", selector: `${formation.feature}:${formation.symbols[id]}` });
    }
    const parameters = claim.signature.constants.map(c => {
      const name = text(constants[c.name], at);
      if (!/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/.test(name)) fail("RULE_PROJECTION_PARAMETER", at, "expected portable parameter name");
      return { name, type: sortTypes.get(c.sort)! };
    });
    if (new Set(parameters.map(p => p.name)).size !== parameters.length) fail("RULE_PROJECTION_PARAMETER", at, "constant parameters must be distinct");
    const properties = new Map<string, string>();
    for (const predicate of claim.signature.predicates) {
      if (predicate.parameter_sorts.length !== 1) fail("RULE_PROJECTION_UNSUPPORTED", at, "property interpretation requires a unary predicate");
      const field = text(predicates[predicate.name], at);
      const entityId = sortEntities.get(predicate.parameter_sorts[0]!)!;
      if (!entityId) fail("RULE_PROJECTION_PREDICATE", at, "property predicates require an Entity sort");
      const entity = formation.model.declarations.find(d => d.id === entityId)!;
      if (entity.kind !== "entity") return fail("RULE_PROJECTION_SORT", at, "expected Entity");
      const property = entity.fields.find(f => f.name === field);
      if (property?.type.kind !== "scalar" || property.type.name !== "Bool") fail("RULE_PROJECTION_PREDICATE", at, "predicate interpretation must select an explicit Bool property");
      const node = JSON.parse(projectFiles[`specs/${formation.feature}/nodes/${formation.symbols[entityId]}.json`]!);
      properties.set(predicate.name, node.body.typed_contract.properties.find((p: { name: string }) => p.name === symbol(field, "_")).ontology_property);
    }
    let projectedNodes = 0;
    const scalarTerm = (term: FormalTerm): Obj => {
      if (term.kind !== "constant" || sortTypes.get(term.sort)?.kind !== "scalar") return fail("RULE_PROJECTION_UNSUPPORTED", at, "equality requires explicitly interpreted scalar constants");
      return { op: "path", root: constants[term.name], properties: [] };
    };
    const lower = (p: FormalProposition): Obj => {
      if (++projectedNodes > 1024) return fail("RULE_PROJECTION_LIMIT", at, "expanded Boolean projection exceeds 1024 nodes");
      switch (p.kind) {
        case "equal": return { op: "eq", left: scalarTerm(p.left), right: scalarTerm(p.right) };
        case "predicate": {
          const arg = p.arguments[0];
          if (p.arguments.length !== 1 || arg?.kind !== "constant") return fail("RULE_PROJECTION_UNSUPPORTED", at, "ground predicate requires an explicitly bound constant");
          return { op: "eq", left: { op: "path", root: constants[arg.name], properties: [properties.get(p.name)] }, right: { op: "literal", type: "Bool", value: true } };
        }
        case "not": return { op: "not", term: lower(p.operand) };
        case "and": case "or": return { op: p.kind === "and" ? "all" : "any", terms: [lower(p.left), lower(p.right)] };
        case "implies": return { op: "any", terms: [{ op: "not", term: lower(p.left) }, lower(p.right)] };
        case "iff": return { op: "all", terms: [
          { op: "any", terms: [{ op: "not", term: lower(p.left) }, lower(p.right)] },
          { op: "any", terms: [{ op: "not", term: lower(p.right) }, lower(p.left)] },
        ] };
        default: return fail("RULE_PROJECTION_UNSUPPORTED", at, `${p.kind} requires a separately supported interpretation; no implicit narrowing`);
      }
    };
    const targetPath = `specs/${formation.feature}/nodes/${formation.symbols[rule.id]}.json`;
    const node = JSON.parse(projectFiles[targetPath]!);
    const ontology = object(declarationBindings[rule.id], at).ontology;
    node.body.predicate = "structured:domainspec.typed-rule/v2";
    node.body.typed_contract = { schema_version: "domainspec.typed-rule/v2", ontology_rule: ontology, parameters, expression: lower(claim.proposition) };
    projectFiles[targetPath] = json(node);
    projections.push({ rule_ref: `${formation.feature}:${formation.symbols[rule.id]}`, claim_ref: claimTrace,
      context_id: contextId, ceiling, interpretation_sha256: digest(json(row)), target_path: targetPath,
      target_sha256: digest(projectFiles[targetPath]!), scope: "ground-proposition-under-explicit-property-and-scalar-interpretation",
      preservation: { direction: "equivalent-under-selected-interpretation", domain: "well-typed-ground-parameters",
        expanded_node_limit: 1024, known_losses: [], result_semantics: "boolean", unsupported_constructs: ["quantifiers", "functions", "non-unary-predicates", "non-scalar-equality"] }, proof: false });
  }
  const nodePath = (id: string) => `specs/${formation.feature}/nodes/${formation.symbols[id]}.json`;
  const ruleContract = (id: string, at: string): Obj => {
    const contract = JSON.parse(projectFiles[nodePath(id)]!).body.typed_contract;
    if (contract?.schema_version !== "domainspec.typed-rule/v2") return fail("FORMAL_CONSUMER_RULE", at, `consumer requires projected Rule ${id}`);
    return contract;
  };
  const typedInputs = (inputs: Array<{ name: string; type: Obj }>) => inputs.map(input => ({ name: symbol(input.name, "_"), type: input.type }));
  const traceInputs = (id: string): Array<{ name: string; type: Obj }> =>
    (formation.trace.declarations.find(item => item.source_id === id)?.inputs as Array<{ name: string; type: Obj }> | undefined) ?? [];
  const argumentBindings = (consumer: string, ruleId: string, inputs: Array<{ name: string; type: Obj }>,
    bindings: Array<{ parameter: string; path: string[]; source_line: number }>, allowExactNames: boolean): Obj[] => {
    const contract = ruleContract(ruleId, consumer); const parameters = contract.parameters as Array<{ name: string; type: Obj }>;
    const selected = bindings.length ? bindings : allowExactNames
      ? parameters.filter(parameter => inputs.some(input => symbol(input.name, "_") === parameter.name)).map(parameter => ({ parameter: parameter.name, path: [parameter.name], source_line: 0 }))
      : [];
    if (json(selected.map(item => symbol(item.parameter, "_")).sort()) !== json(parameters.map(item => item.name).sort())) {
      return fail("FORMAL_CONSUMER_ARGUMENTS", consumer, `Rule ${ruleId} arguments must be bound exactly`);
    }
    return parameters.map(parameter => {
      const binding = selected.find(item => symbol(item.parameter, "_") === parameter.name)!;
      const root = symbol(binding.path[0]!, "_"); const input = inputs.find(item => symbol(item.name, "_") === root);
      if (!input || binding.path.length !== 1) return fail("FORMAL_CONSUMER_ARGUMENTS", `$line:${binding.source_line}`, "consumer bindings currently require one explicit whole input");
      if (json(input.type) !== json(parameter.type)) return fail("FORMAL_CONSUMER_ARGUMENT_TYPE", `$line:${binding.source_line}`, `Rule ${ruleId} argument type differs from consumer input`);
      return { parameter: parameter.name, value: { op: "path", root, properties: [] } };
    });
  };
  const consumers: Obj[] = [];
  for (const invariant of formation.model.invariants) {
    const claim = invariant.claim_ref ?? formation.model.rules.find(rule => rule.id === invariant.rule_ref)!.claim_ref;
    consumers.push({ consumer_kind: "Invariant", consumer_id: invariant.id, rule_ref: invariant.rule_ref, claim_ref: claim,
      binding: invariant.rule_ref ? "declared-rule" : "declared-claim", source_line: invariant.source_line });
  }
  for (const declaration of formation.model.declarations) {
    if (declaration.kind === "policy") {
      const traced = traceInputs(declaration.id);
      const inputs = typedInputs(declaration.inputs.map(input => ({ name: input.name, type: traced.find(item => item.name === input.name)!.type })));
      if (declaration.inputs.length !== declaration.input_names.length) fail("FORMAL_CONSUMER_INPUT_TYPE", `$policy:${declaration.id}`, "executable Policy projection requires typed inputs");
      const cases = declaration.cases.map(item => ({ target: `${formation.feature}:${formation.symbols[item.target]}`, rule: {
        selector: `${formation.feature}:${formation.symbols[item.rule]}`,
        arguments: argumentBindings(`$policy:${declaration.id}`, item.rule, inputs, declaration.bindings.filter(binding => binding.rule === item.rule), true),
      } }));
      const node = JSON.parse(projectFiles[nodePath(declaration.id)]!);
      node.body = { description: node.body.description, typed_contract: { schema_version: "domainspec.typed-policy/v2",
        ontology_policy: object(declarationBindings[declaration.id], `$policy:${declaration.id}`).ontology, inputs, cases,
        default_target: `${formation.feature}:${formation.symbols[declaration.default_target]}` } };
      projectFiles[nodePath(declaration.id)] = json(node);
      consumers.push({ consumer_kind: "Policy", consumer_ref: `${formation.feature}:${formation.symbols[declaration.id]}`,
        rules: declaration.cases.map(item => `${formation.feature}:${formation.symbols[item.rule]}`), binding: "typed-exact-arguments" });
    } else if (declaration.kind === "state-machine") {
      const traced = traceInputs(declaration.id);
      const typed = declaration.inputs.map(input => ({ name: symbol(input.name, "_"), type: traced.find(item => item.name === input.name)!.type }));
      const targetSyntax = declaration.transitions.some(item => item.trigger_event !== null);
      if (targetSyntax && declaration.transitions.some(item => item.trigger_event === null)) {
        fail("FORMAL_CONSUMER_STATE_MACHINE", `$state-machine:${declaration.id}`, "target State Machine transitions require explicit trigger Events throughout");
      }
      const fullyTyped = targetSyntax;
      if (fullyTyped) {
        const transitions = declaration.transitions.map(item => ({ transition_id: symbol(item.id), source_state: symbol(item.from), target_state: symbol(item.to),
          trigger_event_ref: `${formation.feature}:${formation.symbols[item.trigger_event!]}`,
          guard: item.rule ? { selector: `${formation.feature}:${formation.symbols[item.rule]}`, arguments: argumentBindings(`$state-machine:${declaration.id}/${item.id}`, item.rule, typed, item.bindings, false) } : null,
          output_intents: item.result_event ? [{ slot: symbol(item.result_event), event_ref: `${formation.feature}:${formation.symbols[item.result_event]}` }] : [] }));
        const node = JSON.parse(projectFiles[nodePath(declaration.id)]!);
        const ontology = object(declarationBindings[declaration.id], `$state-machine:${declaration.id}`).ontology;
        node.body = { description: node.body.description, typed_contract: { schema_version: "domainspec.typed-state-machine/v1", ontology_state_machine: ontology,
          inputs: typed, states: declaration.states.map(state => symbol(state)), initial: symbol(declaration.initial), transitions } };
        projectFiles[nodePath(declaration.id)] = json(node);
        const featurePath = `specs/${formation.feature}/feature.json`; const feature = JSON.parse(projectFiles[featurePath]!);
        for (const edgeId of [...feature.edges] as string[]) {
          const relative = `specs/${formation.feature}/edges/${edgeId}.json`; const edge = JSON.parse(projectFiles[relative]!);
          if (edge.relationship === "transitions" && edge.target_node_id === formation.symbols[declaration.id]) { feature.edges.splice(feature.edges.indexOf(edgeId), 1); delete projectFiles[relative]; }
        }
        for (const trigger of [...new Set(declaration.transitions.map(item => item.trigger_event!))]) {
          const edgeId = `${formation.symbols[trigger]}-transitions-${formation.symbols[declaration.id]}`;
          feature.edges.push(edgeId); projectFiles[`specs/${formation.feature}/edges/${edgeId}.json`] = json({ schema_version: "domainspec.edge/v1", feature_id: formation.feature,
            edge_id: edgeId, relationship: "transitions", source_node_id: formation.symbols[trigger], target_node_id: formation.symbols[declaration.id], scope: "feature" });
        }
        feature.edges.sort(); projectFiles[featurePath] = json(feature);
      }
      consumers.push({ consumer_kind: "State Machine", consumer_ref: `${formation.feature}:${formation.symbols[declaration.id]}`,
        rules: declaration.transitions.flatMap(item => item.rule ? [`${formation.feature}:${formation.symbols[item.rule]}`] : []),
        binding: fullyTyped ? "typed-exact-arguments" : "declared-rule-static-only" });
    } else if (declaration.kind === "operation") {
      const rules = [...new Set([...declaration.requires, ...formation.model.rules.filter(rule => rule.enforces.includes(declaration.id)).map(rule => rule.id)])];
      consumers.push({ consumer_kind: "Operation", consumer_ref: `${formation.feature}:${formation.symbols[declaration.id]}`,
        rules: rules.map(rule => `${formation.feature}:${formation.symbols[rule]}`), binding: "runtime-realization-exact-arguments" });
    } else if (declaration.kind === "query") {
      consumers.push({ consumer_kind: "Query", consumer_ref: `${formation.feature}:${formation.symbols[declaration.id]}`,
        rules: [`${formation.feature}:${formation.symbols[declaration.rule]}`], binding: "typed-exact-arguments" });
    } else if (declaration.kind === "workflow") {
      const traced = traceInputs(declaration.id);
      const directInputs = declaration.inputs.map(input => ({ name: symbol(input.name, "_"), type: traced.find(item => item.name === input.name)!.type }));
      for (const rule of declaration.rules) argumentBindings(`$workflow:${declaration.id}`, rule, directInputs,
        declaration.bindings.filter(binding => binding.rule === rule), false);
      const stepRules = declaration.steps.flatMap(step => {
        const operation = formation.model.declarations.find(item => item.id === step);
        if (operation?.kind !== "operation") return fail("FORMAL_CONSUMER_WORKFLOW", `$workflow:${declaration.id}`, `${step} is not an Operation`);
        return [...operation.requires, ...formation.model.rules.filter(rule => rule.enforces.includes(step)).map(rule => rule.id)];
      });
      consumers.push({ consumer_kind: "Workflow", consumer_ref: `${formation.feature}:${formation.symbols[declaration.id]}`,
        direct_rules: declaration.rules.map(rule => `${formation.feature}:${formation.symbols[rule]}`),
        step_rules: [...new Set(stepRules)].map(rule => `${formation.feature}:${formation.symbols[rule]}`),
        binding: declaration.rules.length ? "typed-exact-arguments-plus-guarded-steps" : "guarded-steps" });
    }
  }
  const queries = projectApplicationQueries(formation, projectFiles);
  const trace = { schema_version: "alchlang.rule-projection-trace/v1-candidate", formation_sha256: digest(json(formation)),
    interpretation_sha256: digest(json(interpretation)), projections,
    query_projections: queries,
    formal_consumers: consumers,
    project_files: Object.fromEntries(Object.entries(projectFiles).map(([p, bytes]) => [p, digest(bytes)])),
    operation_realization: "required", authority_effect: "none" };
  return { formation, projectFiles, trace };
}

/** Exact currentness only, never a proof of the source proposition. */
export function assertApplicationRuleProjectionCurrent(source: string, bindings: unknown, sources: ReadonlyMap<string, Buffer>, interpretation: unknown, candidate: unknown, persistenceContext?: ApplicationPersistenceContext, messagingContext?: ApplicationMessagingContext, externalApiContext?: ApplicationExternalApiContext, runtimeContext?: ApplicationRuntimeContext): void {
  if (json(candidate) !== json(lowerApplicationRuleProjections(source, bindings, sources, interpretation, persistenceContext, messagingContext, externalApiContext, runtimeContext))) {
    fail("RULE_PROJECTION_STALE", "$projection", "projected source or trace differs from exact current inputs");
  }
}
