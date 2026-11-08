import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledProjectPlan,type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../input/composition-boundary.js';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../input/compiled-field-model.js';
import {compileOperationActionBindings} from '../typed-operation/action-bindings.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {planConfiguredRules,STRUCTURED_RULE_VERSION} from '../generation/configured-rules.js';
import {planConfiguredFactories,STRUCTURED_FACTORY_VERSION} from '../generation/configured-factories.js';
import {planConfiguredAlgebraicEnums,ALGEBRAIC_ENUM_VERSION} from '../generation/configured-algebraic-enums.js';
import {planConfiguredEvents,CONFIGURED_EVENT_VERSION,EVENT_VALUE_PROFILE} from '../generation/configured-events.js';
import {EXACT_UINT64_PROFILE} from '../generation/exact-uint64.js';
import {getReconciledSource,MINIMAL_VALUE_CONTEXT_SHA256} from '../generation/reconciled-sources.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createOperationValueReference} from './reconciled-operation-values.js';

const fail=(message:string):never=>{throw new TypeError('OPERATION_BINDING:'+message);};
/** Dependency plans supply metadata hashes only. No Operation renderer is an oracle. */
function dependencies(graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 const source=getReconciledSource,certificate=createCompiledProjectCertificate(graph);
 if(plan.resolved.certificate.graph_sha256!==certificate.graph_sha256)fail('cross-graph plan');
 const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},source('composition'));
 const roots=graph.nodes.filter(n=>['Entity','Value Object','Enum'].includes(n.kind)).map(n=>n.selector).sort();
 const fields=roots.length?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots,bindings:plan.selection.field_bindings},source('field')):null;
 const actions=plan.selection.operations.map(b=>compileOperationActionBindings(graph,boundary,fields,b,source('operation_action')));
 const common={configuration:source('configuration'),base:source('base'),typescript:source('typescript')};
 const ruleSources={...common,rule_contract:source('rule'),collection_contract:source('rule_collection'),predicate_contract:source('rule_predicate'),numeric_contract:source('rule_numeric'),exact_contract:source('rule_exact'),literal_contract:source('rule_literal'),structured_contract:source('rule_structured'),field_contract:source('field')};
 const layout={language:'typescript' as const,module_root:plan.selection.module_root};
 const factorySources={...ruleSources,factory_contract:source('factory'),enum_provider:source('enum_provider')};
 const enumOnly=fields!==null&&fields.model.declarations.every(d=>d.kind==='Enum');
 const factories=fields&&!enumOnly?planConfiguredFactories(graph,fields,{schema_version:STRUCTURED_FACTORY_VERSION,...layout,field_compilation_sha256:fields.compilation_sha256,rule_selection:{schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE},factories:plan.selection.factories},factorySources):null;
 const algebraic=fields&&enumOnly?planConfiguredAlgebraicEnums(graph,fields,{schema_version:ALGEBRAIC_ENUM_VERSION,...layout,field_compilation_sha256:fields.compilation_sha256,factories:plan.selection.factories},{standalone_contract:source('standalone_sum'),factories:factorySources}):null;
 const dependencies=new Map(actions.map(action=>{
  const roots=[...new Set(action.guards.map(g=>g.selector))].sort();
  const rules=planConfiguredRules(graph,{schema_version:STRUCTURED_RULE_VERSION,...layout,value_profile:EXACT_UINT64_PROFILE,roots},ruleSources);
  const eventRoots=[...new Set(action.events.map(e=>e.target))].sort();
  const events=eventRoots.length?planConfiguredEvents(graph,boundary,{schema_version:CONFIGURED_EVENT_VERSION,...layout,value_profile:EVENT_VALUE_PROFILE,boundary_sha256:boundary.boundary_sha256,roots:eventRoots},{...common,event_contract:source('event')}):null;
  return [action.bindings.selector,{rules,events}] as const;
 }));
 return {certificate,boundary,fields,actions,dependencies,factories,algebraic};
}
const contexts=new WeakMap<ReconciledProjectPlan,ReturnType<typeof dependencies>>();
export function createOperationBinding(node:CompiledProjectGraph['nodes'][number],graph:CompiledProjectGraph,plan:ReconciledProjectPlan){
 assertCompiledProjectSnapshot(graph);assertReconciledProjectPlan(plan);
 if(node.kind!=='Operation'||!graph.nodes.includes(node))fail('source Operation required');
 if(plan.resolved.certificate.graph_sha256!==createCompiledProjectCertificate(graph).graph_sha256)fail('cross-graph plan');
 let context=contexts.get(plan);if(!context){context=dependencies(graph,plan);contexts.set(plan,context);}
 const action=context.actions.find(a=>a.bindings.selector===node.selector)??fail('checked action missing');
 const ownDependencies=context.dependencies.get(node.selector)??fail('declared dependency plans missing');
 const selected=plan.resolved.requests.filter(r=>r.kind==='operations').flatMap(r=>(r.selection as {actions:readonly {action_sha256:string;bindings:{selector:string}}[]}).actions).filter(a=>a.bindings.selector===node.selector);
 if(selected.length!==1||selected[0]!.action_sha256!==action.action_sha256)fail('exact selected action mismatch');
 const role=JSON.parse(getReconciledSource('configuration')).types.find((t:any)=>t.kind==='Operation').role;
 const relative_path=plan.selection.module_root+'/features/'+node.feature_id+'/src/'+role+'/'+node.node_id+'.ts';
 const callable='operation'+node.node_id.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
 const module=plan.resolved.modules.find(m=>m.relative_path===relative_path)??fail('callable module missing');
 if(!module.qualified_selectors.includes(node.selector)||!module.exports.some(e=>e.name===callable&&e.kind==='value'))fail('callable identity mismatch');
 const reference=createOperationValueReference(graph),allowed=new Set([node.selector]),owned=new Set<string>();
 const rule=(selector:string):void=>{
  if(allowed.has(selector))return;allowed.add(selector);
  const n=graph.nodes.find(n=>n.selector===selector);if(n?.kind!=='Rule')fail('declared Rule missing');
  const walk=(v:any):void=>{if(!v||typeof v!=='object')return;if(v.op==='rule_ref')rule(v.selector);for(const x of Object.values(v))if(Array.isArray(x))x.forEach(walk);else walk(x);};walk(n!.body.typed_contract);
 };
 const own=(t:TypedType,depth=0):void=>{
  if(depth>64)fail('owned closure depth');
  if(t.kind==='scalar')return;
  if(t.kind==='optional'||t.kind==='list'||t.kind==='set'){own(t.element,depth+1);return;}
  if(t.kind==='sum'){for(const v of t.variants)if(v.payload)own(v.payload,depth+1);return;}
  if(owned.has(t.selector))return;owned.add(t.selector);allowed.add(t.selector);const d=reference.get(t);
  if(d.kind==='Enum'){own({kind:'sum',variants:d.variants},depth+1);return;}
  d.properties.forEach(p=>own(p.type as TypedType,depth+1));
  const f=plan.selection.factories.find(f=>f.selector===t.selector)??fail('owned factory binding missing');
  // Extensions are present in the selected module but are never implicitly adopted.
  [...f.base_validators,...f.extensions.flatMap(e=>e.validators)].forEach(v=>rule(v.rule));
 };
 action.guards.forEach(g=>rule(g.selector));action.writes.forEach(w=>own({kind:'named',selector:w.target}));own(action.bindings.result.type);
 action.events.forEach(e=>allowed.add(e.target));
 const runtime=plan.selection.module_root+'/runtime/enum.ts',paths=new Set<string>();
 const visit=(p:string):void=>{
  if(paths.has(p))return;paths.add(p);
  const m=plan.resolved.modules.find(m=>m.relative_path===p)??fail('native dependency missing');
  if(m.qualified_selectors.some(s=>!allowed.has(s)))fail('foreign native dependency:'+p);
  if(!m.qualified_selectors.length){const a=plan.resolved.artifacts.find(a=>a.relative_path===p);if(p!==runtime||a?.content!==getReconciledSource('enum_provider'))fail('unbound support module:'+p);}
  for(const i of m.imports){if(!i.target_path)fail('external native dependency');visit(i.target_path!);}
 };visit(relative_path);
 const provider=plan.resolved.artifacts.find(a=>a.relative_path===relative_path.replace(/\.ts$/,'.provider.ts'))??fail('provider missing');
 const descriptor={schema_version:'domainspec.generated-operation-descriptor/v1-candidate',protocol_id:'typescript.bound-operation/v1',selector:node.selector,source:action.source,action_sha256:action.action_sha256,bindings:action.bindings,
  source_compatibility:'explicit-action-bindings-not-legacy-typed-v1',value_profile:EXACT_UINT64_PROFILE,return_semantics:'awaited-explicit-outcome',effect_contract:'state-and-outbox',continuation:'awaited-settlement',
  rule_plan_sha256:ownDependencies.rules.plan_sha256,factory_plan_sha256:context.factories?.plan_sha256??null,event_plan_sha256:ownDependencies.events?.plan_sha256??null,field_model_sha256:context.fields?.model.model_sha256??null,
  ...(context.factories?{}:{minimal_context_sha256:MINIMAL_VALUE_CONTEXT_SHA256,...(context.algebraic?{algebraic_plan_sha256:context.algebraic.plan_sha256}:{})}),
  execution_obligations:action.execution_obligations,transaction_provider:'explicit-external-dependency',provider_durability_claim:false,publication:false,primary_callable_count:1,provider:{sha256:provider.sha256},authority_effect:'none'};
 return {action,fields:context.fields,descriptor:{...descriptor,descriptor_sha256:sha256(canonicalJson(descriptor))},callable,relative_path,module_paths:[...paths].sort(),
  native_imports:[...paths].sort().map(relative_path=>({relative_path,imports:plan.resolved.modules.find(m=>m.relative_path===relative_path)!.imports.map(i=>({specifier:i.specifier,target_path:i.target_path!}))}))};
}
