import { CompilationRejected } from "./model.js";
import {assertDerivedDirectBusinessBindingsV2Current,type DerivedDirectBusinessBindingsV2} from './business-application-bindings.js';
import {assertDirectOperationActionsV2Current,type DirectOperationActionsV2} from './business-application-actions.js';
import type {AuthoringBusinessInputV2,BusinessInputOwnerV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessDirectApplicationOwnerV2,CheckedDirectApplicationV2} from './business-authoring-stages-v2.js';
import {businessCanonical,businessHash,businessReject} from './business-authoring-model.js';

/** Injected public SDK owner surfaces, never a source/project-config callback.
 * Production callers supply the selected Core SDK. Seam fixtures are not Core admission.
 * Open Questions: actual public owners at L02 and original joined witness at G01. */
export interface DirectBusinessCoreSurfaceV2 {readonly input:BusinessInputOwnerV2;readonly application:BusinessDirectApplicationOwnerV2}
export interface PreparedDirectExecutableV2 {
 readonly kind:'prepared-direct-executable-v2';readonly bindings:DerivedDirectBusinessBindingsV2;
 readonly actions:DirectOperationActionsV2;readonly input:AuthoringBusinessInputV2;readonly authority_effect:'none';
}
export interface CompiledDirectExecutableV2 {
 readonly kind:'compiled-direct-executable-v2';readonly prepared:PreparedDirectExecutableV2;
 readonly checked:CheckedDirectApplicationV2;
 readonly lineage:Readonly<{source_sha256:string;executable_sha256:string;assurance_sha256:string;input_sha256:string;graph_sha256:string;condition_sha256:string;plan_sha256:string}>;
 readonly authority_effect:'none';
}
type DirectPreparationState={core:DirectBusinessCoreSurfaceV2;inputOwner:BusinessInputOwnerV2;applicationOwner:BusinessDirectApplicationOwnerV2;assertInput:BusinessInputOwnerV2['assertCurrent'];check:BusinessDirectApplicationOwnerV2['check'];assertApplication:BusinessDirectApplicationOwnerV2['assertCurrent'];assertCondition:BusinessDirectApplicationOwnerV2['assertConditionCurrent']};
const directPrepared=new WeakMap<object,DirectPreparationState>();
const directCompiled=new WeakMap<object,{prepared:PreparedDirectExecutableV2;checked:CheckedDirectApplicationV2;fingerprint:string}>();
const directFail=(message:string):never=>businessReject('BUSINESS_DIRECT_CORE_JOIN','business.alch',1,1,message);
function assertDirectCoreSurface(state:DirectPreparationState):void {
 if(state.core.input!==state.inputOwner||state.core.application!==state.applicationOwner||state.core.input.assertCurrent!==state.assertInput||state.core.application.check!==state.check||state.core.application.assertCurrent!==state.assertApplication||state.core.application.assertConditionCurrent!==state.assertCondition)directFail('Core owner surface changed; prepare again in the current epoch');
}
export function prepareDirectApplicationExecutableV2(bindings:DerivedDirectBusinessBindingsV2,actions:DirectOperationActionsV2,input:AuthoringBusinessInputV2,core:DirectBusinessCoreSurfaceV2):PreparedDirectExecutableV2 {
 assertDerivedDirectBusinessBindingsV2Current(bindings);assertDirectOperationActionsV2Current(actions);
 if(actions.bindings!==bindings)directFail('actions must retain the same original source bindings');
 core.input.assertCurrent(input);
 const business=bindings.lowered.business;
 if(input.kind!=='authoring-business-input-v2'||input.model_id!==business.data.identity.namespace||businessCanonical(input.spec)!==businessCanonical(business.data)||input.capture.source.path!==business.source.path||input.capture.source.sha256!==business.source.sha256||input.capture.source.bytes!==business.source.bytes)directFail('original checked input differs from exact captured frontend source');
 const result=Object.freeze({kind:'prepared-direct-executable-v2' as const,bindings,actions,input,authority_effect:'none' as const});
 directPrepared.set(result,{core,inputOwner:core.input,applicationOwner:core.application,assertInput:core.input.assertCurrent,check:core.application.check,assertApplication:core.application.assertCurrent,assertCondition:core.application.assertConditionCurrent});
 assertPreparedDirectApplicationExecutableV2Current(result);return result;
}
export function assertPreparedDirectApplicationExecutableV2Current(value:PreparedDirectExecutableV2):void {
 const state=value&&typeof value==='object'?directPrepared.get(value):undefined;
 if(!state)directFail('original direct executable preparation required');
 assertDirectCoreSurface(state!);state!.core.input.assertCurrent(value.input);
 assertDerivedDirectBusinessBindingsV2Current(value.bindings);assertDirectOperationActionsV2Current(value.actions);
 if(value.actions.bindings!==value.bindings)directFail('direct source/actions owners differ');
}
export interface DirectGraphCorrespondenceDataV2 {
 readonly operation_ref:string;readonly plan_sha256:string;
 readonly graph:Pick<CheckedDirectApplicationV2['graph'],'graph_sha256'|'closures'>;
 readonly condition:Pick<CheckedDirectApplicationV2['condition'],'rule_ref'|'entity_ref'|'parameter'|'field_name'|'property_selector'|'condition_sha256'>;
}
/** Data correspondence check only. Returns no handle, acceptance or graph custody. */
export function validateDirectGraphCorrespondenceDataV2(bindings:DerivedDirectBusinessBindingsV2,data:DirectGraphCorrespondenceDataV2):void {
 assertDerivedDirectBusinessBindingsV2Current(bindings);
 const formation=bindings.formation,rule=bindings.rule,graph=data.graph,condition=data.condition;
 if(data.operation_ref!==formation.selectors.operation||condition.rule_ref!==rule.selector||condition.entity_ref!==rule.entity_selector||condition.parameter!==rule.parameter||condition.field_name!==rule.field_name||condition.property_selector!==rule.property_selector)directFail('Core condition/Operation/graph differs from original source selection');
 const expected=[['Entity',formation.selectors.entity],['Rule',formation.selectors.rule],['Operation',formation.selectors.operation],['Interface',formation.selectors.entry],['Mapping',formation.selectors.input_mapping],['Mapping',formation.selectors.output_mapping]] as const;
 if(graph.closures.length!==expected.length||new Set(graph.closures.map(row=>row.selector)).size!==expected.length)directFail('complete nonempty selected role inventory required');
 for(const [role,selector] of expected){const closure=graph.closures.find(row=>row.role===role&&row.selector===selector);if(!closure||!/^[a-f0-9]{64}$/.test(closure.typed_closure_sha256))directFail('actual typed role closure required: '+selector);}
 const ruleClosure=graph.closures.find(row=>row.role==='Rule'&&row.selector===rule.selector)!;
 if(!ruleClosure.origins.some(origin=>origin.source===rule.source.source&&origin.selector===rule.source.selector&&origin.sha256===rule.source.source_sha256))directFail('Core Rule closure lacks the original direct condition source');
 for(const hash of [graph.graph_sha256,condition.condition_sha256,data.plan_sha256])if(!/^[a-f0-9]{64}$/.test(hash))directFail('actual checked subject identities required');
}
function assertDirectGraphCorrespondence(prepared:PreparedDirectExecutableV2,checked:CheckedDirectApplicationV2,state:DirectPreparationState):void {
 state.core.application.assertCurrent(checked);state.core.application.assertConditionCurrent(checked.condition);
 if(checked.input!==prepared.input||checked.graph.input!==prepared.input||checked.condition.graph!==checked.graph)directFail('Core input/condition/graph must retain original owner correspondence');
 validateDirectGraphCorrespondenceDataV2(prepared.bindings,checked);
}
/** Calls the original direct Core owner, never compileFormalConditionBindings with
 * an empty Rule inventory. Actual genuine accepted-input qualification is G01. */
export function compileDirectApplicationExecutableV2(prepared:PreparedDirectExecutableV2):CompiledDirectExecutableV2 {
 assertPreparedDirectApplicationExecutableV2Current(prepared);const state=directPrepared.get(prepared)!;
 const checked=state.core.application.check(prepared.input);assertDirectGraphCorrespondence(prepared,checked,state);
 const business=prepared.bindings.lowered.business;
 const lineage=Object.freeze({source_sha256:business.source.sha256,executable_sha256:business.executable_sha256,assurance_sha256:business.assurance_sha256,input_sha256:prepared.input.input_sha256,graph_sha256:checked.graph.graph_sha256,condition_sha256:checked.condition.condition_sha256,plan_sha256:checked.plan_sha256});
 const result=Object.freeze({kind:'compiled-direct-executable-v2' as const,prepared,checked,lineage,authority_effect:'none' as const});
 directCompiled.set(result,{prepared,checked,fingerprint:businessHash(businessCanonical(lineage))});assertCompiledDirectApplicationExecutableV2Current(result);return result;
}
export function assertCompiledDirectApplicationExecutableV2Current(value:CompiledDirectExecutableV2):void {
 const saved=value&&typeof value==='object'?directCompiled.get(value):undefined;
 if(!saved)directFail('original direct Core join required');
 assertPreparedDirectApplicationExecutableV2Current(saved!.prepared);
 assertDirectGraphCorrespondence(saved!.prepared,saved!.checked,directPrepared.get(saved!.prepared)!);
 if(value.prepared!==saved!.prepared||value.checked!==saved!.checked||businessHash(businessCanonical(value.lineage))!==saved!.fingerprint)directFail('direct Core join changed');
}
import { digest, json } from "./domainspec-profile.js";
import { lowerApplicationRuleProjections } from "./application-rule-projection.js";
import { deriveApplicationRealizationActions, deriveApplicationRealizationCompositions } from "./application-realization-actions.js";
import type { DomainSpecCompiler, DomainSpecGraph } from "./domainspec-cli.js";
import type { ApplicationPersistenceContext, ApplicationMessagingContext, ApplicationExternalApiContext, ApplicationRuntimeContext } from "./application-domain-lowering.js";

const fail = (code: string, message: string): never => { throw new CompilationRejected([{ code, path: "$execution", message }]); };
const equal = (a: unknown, b: unknown) => json(a) === json(b);
function sameSet(a: string[], b: string[], role: string): void {
  if (new Set(a).size !== a.length || !equal([...a].sort(), [...b].sort())) fail("APPLICATION_EXECUTION_COVERAGE", `${role} differs from authored source`);
}
function freeze<T>(value: T): T {
  if (value && typeof value === "object" && !Object.isFrozen(value)) { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}
const prepared = new WeakSet<object>();

/** Validate authored realization choices; no files, providers or operations execute. */
export function prepareApplicationExecutable(source: string, bindings: unknown, sources: ReadonlyMap<string, Buffer>, interpretation: unknown, execution: unknown, compiler: DomainSpecCompiler, persistenceContext?: ApplicationPersistenceContext, messagingContext?: ApplicationMessagingContext, externalApiContext?: ApplicationExternalApiContext, runtimeContext?: ApplicationRuntimeContext) {
  const projection = lowerApplicationRuleProjections(source, bindings, sources, interpretation, persistenceContext, messagingContext, externalApiContext, runtimeContext);
  if (!execution || typeof execution !== "object" || Array.isArray(execution)) fail("APPLICATION_EXECUTION_SCHEMA", "expected execution binding");
  const input = execution as Record<string, unknown>;
  const authored = !!projection.formation.model.realizations?.length;
  const version = authored ? "alchlang.application-execution/v2-candidate" : "alchlang.application-execution/v1-candidate";
  if (!equal(Object.keys(input).sort(), ["projection_sha256", "schema_version", "selection"]) || input.schema_version !== version) fail("APPLICATION_EXECUTION_SCHEMA", "closed execution binding required; authored realizations require v2 without operation overrides");
  if (input.projection_sha256 !== digest(json(projection))) fail("APPLICATION_EXECUTION_STALE", "execution must bind exact current Rule projection");
  let selected = input.selection;
  if (authored) {
    if (!selected || typeof selected !== "object" || Array.isArray(selected) || Object.hasOwn(selected, "operations") || Object.hasOwn(selected,"value_compositions")) fail("APPLICATION_REALIZATION_OVERRIDE", "authored selection must omit operations and value_compositions; bindings are derived exclusively from realizations");
    const descriptors=Object.getOwnPropertyDescriptors(selected);
    if(![Object.prototype,null].includes(Object.getPrototypeOf(selected))||Reflect.ownKeys(descriptors).some(k=>typeof k!=='string')||Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')||!d.enumerable))fail('APPLICATION_EXECUTION_SCHEMA','inert selection required');
    if(descriptors.schema_version?.value==='domainspec.reconciled-compilation/v2-candidate'){
      const derived=deriveApplicationRealizationCompositions(projection);
      selected={...(selected as Record<string,unknown>),operations:derived.map(row=>row.action),value_compositions:derived.map(({composition,absence_failures})=>({composition,absence_failures}))};
    }else selected = { ...(selected as Record<string, unknown>), operations: deriveApplicationRealizationActions(projection) };
  }
  const selection = compiler.decodeReconciledCompilationSelection(selected);
  const formation = projection.formation;
  if (formation.runtime && selection.language !== formation.runtime.selected.selection.language) fail("APPLICATION_RUNTIME_TARGET", "selected runtime and executable target differ");
  const shapes = formation.operationShapes.operations;
  sameSet(selection.operations.map((o: any) => o.selector), shapes.map(o => String(o.operation_ref)), "operation coverage");
  const projectFiles = { ...projection.projectFiles };
  const featurePath = `specs/${formation.feature}/feature.json`;
  const feature = JSON.parse(projectFiles[featurePath]!);
  const addEdge = (from: string, relationship: string, to: string) => {
    const sourceId = from.split(":")[1]!; const targetId = to.split(":")[1]!;
    const id = `${sourceId}-${relationship}-${targetId}`;
    const relative = `specs/${formation.feature}/edges/${id}.json`;
    const bytes = json({ schema_version: "domainspec.edge/v1", feature_id: formation.feature, edge_id: id,
      relationship, source_node_id: sourceId, target_node_id: targetId, scope: "feature" });
    if (projectFiles[relative] && projectFiles[relative] !== bytes) fail("APPLICATION_EXECUTION_COLLISION", relative);
    projectFiles[relative] = bytes;
    if (!feature.edges.includes(id)) feature.edges.push(id);
  };
  for (const operation of selection.operations) {
    const shape = shapes.find(o => o.operation_ref === operation.selector)!;
    if (operation.inputs.length !== 1 || !equal(operation.inputs[0].type, shape.input) || !equal(operation.result.type, shape.output)) {
      fail("APPLICATION_EXECUTION_SHAPE", "action input/output differs from authored operation");
    }
    sameSet(operation.guards.map((g: any) => g.selector), shape.guard_rule_refs as string[], "guards");
    const nodePath = `specs/${formation.feature}/nodes/${operation.selector.split(":")[1]}.json`;
    const body = JSON.parse(projectFiles[nodePath]!).body;
    const valueComposition=selection.value_compositions?.find((row:any)=>row.composition.operation_ref===operation.selector)?.composition;
    const queryReads=(valueComposition?.bindings??[]).filter((row:any)=>row.kind==='query').map((row:any)=>{
      const [feature,id]=row.selector.split(':');
      const source=JSON.parse(projectFiles[`specs/${feature}/nodes/${id}.json`]!).body.typed_contract.source;
      if(row.source_slot!==source)fail('APPLICATION_EXECUTION_SLOT','Query collection slots must retain the authored qualified source Entity');
      return source as string;
    });
    for (const lane of ["reads", "writes"] as const) {
      const targets=operation[lane].map((r:any)=>r.target);
      sameSet(lane==='reads'&&valueComposition?[...new Set([...targets,...queryReads])] as string[]:targets, body[lane], lane);
      for (const row of operation[lane]) if (row.slot !== row.target) fail("APPLICATION_EXECUTION_SLOT", "L0 slots must retain their authored qualified Entity reference");
    }
    sameSet(operation.events.map((event: any) => event.target), body.effects, "events");
    for (const event of operation.events) if (event.slot !== event.target) fail("APPLICATION_EXECUTION_SLOT", "Event slots must retain their authored qualified Event reference");
    operation.reads.forEach((r: any) => addEdge(operation.selector, "reads", r.target));
    [...new Set(queryReads)].forEach(target=>addEdge(operation.selector,'reads',target as string));
    operation.writes.filter((w: any) => w.mode === "create").forEach((w: any) => addEdge(operation.selector, "creates", w.target));
  }
  feature.edges.sort(); projectFiles[featurePath] = json(feature);
  const trace = { schema_version: "alchlang.application-executable-trace/v1-candidate", projection_sha256: digest(json(projection)),
    execution_sha256: digest(json(execution)), selection_sha256: digest(json(selection)),
    project_files: Object.fromEntries(Object.entries(projectFiles).map(([p, bytes]) => [p, { sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes) }])),
    execution: "not-performed", authority_effect: "none" };
  const result = freeze({ projection, projectFiles, selection, trace }); prepared.add(result); return result;
}

/** Join the exact generated source graph through existing public DomainSpec APIs. */
export function compileApplicationExecutable(candidate: ReturnType<typeof prepareApplicationExecutable>, graph: DomainSpecGraph, compiler: DomainSpecCompiler) {
  if (!prepared.has(candidate)) fail("APPLICATION_EXECUTION_UNVALIDATED", "use the current prepared candidate");
  const rows = graph.source_manifest.sources;
  if (!rows) return fail("APPLICATION_EXECUTION_GRAPH", "graph source manifest is unavailable");
  if (!equal(rows.map(r => r.relative_path).sort(), Object.keys(candidate.projectFiles).sort())) fail("APPLICATION_EXECUTION_GRAPH", "graph source coverage differs");
  for (const row of rows) {
    const expected = candidate.trace.project_files[row.relative_path];
    if (!expected || expected.sha256 !== row.sha256 || expected.size_bytes !== row.size_bytes) fail("APPLICATION_EXECUTION_GRAPH", "graph source bytes differ");
  }
  const formation = candidate.projection.formation;
  if (formation.persistence) {
    for (const reference of formation.persistence.trace.references) {
      for (const query of reference.queries) {
        const body = graph.nodes.find(n => n.selector === query.selector && n.kind === "Query")?.body as any;
        const contract = body?.typed_contract;
        const cardinality = contract?.schema_version === "domainspec.typed-query/v1" ? "list" : contract?.result_cardinality;
        if (contract?.source !== reference.entity || cardinality !== query.result_cardinality) fail("APPLICATION_PERSISTENCE_QUERY_JOIN", "compiled Query differs from the authored persistence consumer");
      }
      for (const operation of reference.operations) {
        const selected = candidate.selection.operations.find((o: any) => o.selector === operation.selector);
        if (!selected?.writes.some((w: any) => w.target === reference.entity && w.slot === reference.entity)) fail("APPLICATION_PERSISTENCE_WRITE_JOIN", "executable Operation lacks the authored persistence write slot");
      }
    }
  }
  const messagingJoin = formation.messaging ? compiler.compileMessagingRuntimeBindings(graph, formation.messaging.sourceComposition, candidate.selection) : undefined;
  const externalApiJoin = formation.externalApi ? compiler.compileExternalApiRuntimeBindings(graph, formation.externalApi.sourceComposition, candidate.selection) : undefined;
  const join = compiler.compileFormalConditionBindings(graph, formation.conditions, new Map(Object.entries(formation.files).map(([p, bytes]) => [p, Buffer.from(bytes)])));
  const generated = compiler.planApplicationRealization(graph, candidate.selection);
  return { ...generated, join, ...(formation.persistence ? { persistence: formation.persistence } : {}), ...(formation.messaging ? { messaging: formation.messaging, messagingJoin } : {}), ...(formation.externalApi ? { externalApi: formation.externalApi, externalApiJoin } : {}), ...(formation.runtime ? { runtime: formation.runtime } : {}), trace: { ...candidate.trace, domain_manifest_sha256: graph.source_manifest.manifest_sha256,
    ...(externalApiJoin ? { external_api_composition_sha256: formation.externalApi!.trace.composition_sha256, external_api_join_sha256: digest(json(externalApiJoin)) } : {}),
    ...(messagingJoin ? { messaging_composition_sha256: formation.messaging!.trace.composition_sha256, messaging_join_sha256: digest(json(messagingJoin)) } : {}),
    ...(formation.persistence ? { persistence_composition_sha256: formation.persistence.trace.composition_sha256 } : {}),
    generated_files: Object.fromEntries(generated.view.artifacts.map(a => [a.relative_path, { sha256: a.sha256, size_bytes: a.size_bytes }])) } };
}
