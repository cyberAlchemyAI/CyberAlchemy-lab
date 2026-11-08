import path from 'node:path';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCheckedOperationAction,type CheckedOperationAction} from '../typed-operation/action-bindings.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {planConfiguredRules,STRUCTURED_RULE_VERSION,type RuleConfigurationSources} from './configured-rules.js';
import {planConfiguredFactories,STRUCTURED_FACTORY_VERSION,STRUCTURED_FACTORY_CONTRACT_SHA256,type FactoryBinding} from './configured-factories.js';
import {planConfiguredAlgebraicEnums,ALGEBRAIC_ENUM_VERSION} from './configured-algebraic-enums.js';
import {ENUM_PROVIDER_SHA256} from './configured-enums.js';
import {getReconciledSource,MINIMAL_VALUE_CONTEXT_SHA256} from './reconciled-sources.js';
import {planConfiguredEvents,CONFIGURED_EVENT_VERSION,EVENT_VALUE_PROFILE,type EventConfigurationSources} from './configured-events.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {renderConfiguredOperation} from './configured-operation-source.js';
import type {PlannedArtifact} from './contracts.js';

export const CONFIGURED_OPERATION_VERSION='domainspec.configured-operations-selection/v1-candidate';
export const OPERATION_GENERATION_CONTRACT_SHA256='0c5119558515283157e574deab19d937a54d32d967bc9ce7ec5cbb470fc4d6e2';
export interface ConfiguredOperationSelection {
  readonly schema_version:typeof CONFIGURED_OPERATION_VERSION;
  readonly language:'typescript';
  readonly module_root:string;
  readonly actions:readonly CheckedOperationAction[];
  readonly factories:readonly FactoryBinding[];
}
export interface OperationConfigurationSources {
  readonly operation_contract:string;
  readonly factory_contract:string;
  readonly enum_provider:string;
  readonly rules:RuleConfigurationSources;
  readonly events:EventConfigurationSources;
}
const fail=(message:string):never=>{throw Error('DS_CONFIGURED_OPERATION:'+message);};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>'com'+(i+1)+' lpt'+(i+1)).join(' ')).split(' '));
const portable=(s:string)=>typeof s==='string'&&/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(s)?.[0]===s&&!reserved.has(s);
function keys(v:unknown,expected:readonly string[]):void{
  if(!v||typeof v!=='object'||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))fail('plain object required');
  const d=Object.getOwnPropertyDescriptors(v);
  if(Reflect.ownKeys(d).length!==expected.length||Reflect.ownKeys(d).some(k=>typeof k!=='string'||!expected.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))fail('closed inert object required');
}
function frozenLiteral(v:unknown):string{
  if(Array.isArray(v))return 'Object.freeze(['+v.map(frozenLiteral).join(',')+'])';
  if(v&&typeof v==='object')return 'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+JSON.stringify(k)+']:'+frozenLiteral(x)).join(',')+'})';
  return JSON.stringify(v);
}

/** Compose checked action meaning into native code with an explicit atomic port.
 * This plans files only. Provider durability is not established by a descriptor.
 */
export function planConfiguredOperations(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,selection:ConfiguredOperationSelection,sources:OperationConfigurationSources){
  assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);if(fields!==null)assertCompiledProjectFields(fields);
  keys(selection,['schema_version','language','module_root','actions','factories']);
  keys(sources,['operation_contract','factory_contract','enum_provider','rules','events']);
  keys(sources.rules,['configuration','base','typescript','rule_contract','collection_contract','predicate_contract','numeric_contract','exact_contract','literal_contract','structured_contract','field_contract']);
  keys(sources.events,['configuration','base','typescript','event_contract']);
  if(selection.schema_version!==CONFIGURED_OPERATION_VERSION||selection.language!=='typescript')fail('unsupported selection');
  if(typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable))fail('unsafe module root');
  if(typeof sources.operation_contract!=='string'||sha256(sources.operation_contract)!==OPERATION_GENERATION_CONTRACT_SHA256)fail('operation contract drift');
  for(const key of ['configuration','base','typescript'] as const)if(sources.rules[key]!==sources.events[key])fail('dependency source mismatch:'+key);
  if(!Array.isArray(selection.actions)||Object.getPrototypeOf(selection.actions)!==Array.prototype)fail('plain action array required');
  const d:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(selection.actions),length=d.length!.value;
  if(!Number.isSafeInteger(length)||length<1||length>128||Reflect.ownKeys(d).length!==length+1)fail('bounded dense actions required');
  const certificate=createCompiledProjectCertificate(graph),actions:CheckedOperationAction[]=[];
  for(let i=0;i<length;i++){
    const p=d[String(i)];if(!p||!Object.hasOwn(p,'value')||!p.enumerable)fail('inert action required');
    const action=p!.value;assertCheckedOperationAction(action);
    if(action.certificate.graph_sha256!==certificate.graph_sha256||action.boundary_sha256!==boundary.boundary_sha256||action.field_compilation_sha256!==(fields?.compilation_sha256??null))fail('stale or cross-graph action');
    if(!action.bindings.selector.split(':').every(portable))fail('unsafe selector');actions.push(action);
  }
  if(new Set(actions.map(a=>a.bindings.selector)).size!==actions.length)fail('duplicate action');
  actions.sort((a,b)=>a.bindings.selector<b.bindings.selector?-1:1);
  const ruleRoots=[...new Set(actions.flatMap(a=>a.guards.map(g=>g.selector)))].sort();
  const rules=planConfiguredRules(graph,{schema_version:STRUCTURED_RULE_VERSION,language:'typescript',module_root:selection.module_root,value_profile:EXACT_UINT64_PROFILE,roots:ruleRoots},sources.rules);
  const enumOnly=fields!==null&&fields.model.declarations.every(d=>d.kind==='Enum');
  if(fields===null){
    if(!Array.isArray(selection.factories)||Object.getPrototypeOf(selection.factories)!==Array.prototype||Reflect.ownKeys(selection.factories).length!==1||selection.factories.length!==0)fail('no factories in absent field context');
    if(typeof sources.factory_contract!=='string'||sha256(sources.factory_contract)!==STRUCTURED_FACTORY_CONTRACT_SHA256||typeof sources.enum_provider!=='string'||sha256(sources.enum_provider)!==ENUM_PROVIDER_SHA256)fail('unused factory source drift');
  }
  const factorySources={...sources.rules,factory_contract:sources.factory_contract,enum_provider:sources.enum_provider};
  const factories=fields&&!enumOnly?planConfiguredFactories(graph,fields,{schema_version:STRUCTURED_FACTORY_VERSION,language:'typescript',module_root:selection.module_root,field_compilation_sha256:fields.compilation_sha256,rule_selection:{schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE},factories:selection.factories},factorySources):null;
  const algebraic=fields&&enumOnly?planConfiguredAlgebraicEnums(graph,fields,{schema_version:ALGEBRAIC_ENUM_VERSION,language:'typescript',module_root:selection.module_root,field_compilation_sha256:fields.compilation_sha256,factories:selection.factories},{standalone_contract:getReconciledSource('standalone_sum'),factories:factorySources}):null;
  const valueProviders=factories??{modules:[],sum_modules:algebraic?.sum_modules??[],enum_components:algebraic?.components??[]};
  const eventRoots=[...new Set(actions.flatMap(a=>a.events.map(e=>e.target)))].sort();
  const events=eventRoots.length?planConfiguredEvents(graph,boundary,{schema_version:CONFIGURED_EVENT_VERSION,language:'typescript',module_root:selection.module_root,value_profile:EVENT_VALUE_PROFILE,boundary_sha256:boundary.boundary_sha256,roots:eventRoots},sources.events):null;
  const config=JSON.parse(sources.rules.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='Operation');
  if(cell?.role!=='application/operations'||canonicalJson(cell.blocked_by)!=='["DSR-011"]')fail('unexpected Operation configuration');
  const profile=JSON.parse(sources.rules.typescript),overlay=profile.representation_overlays.find((p:{contract_id:string})=>p.contract_id==='operation.profile-representation'),protocol=overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='typescript.bound-operation/v1');
  if(protocol?.form_id!=='typescript.bound-operation-function')fail('missing Operation protocol');
  const artifacts:PlannedArtifact[]=[];
  const add=(relative_path:string,content:string)=>{
    const previous=artifacts.find(a=>a.relative_path===relative_path);if(previous){if(previous.content!==content)fail('artifact collision:'+relative_path);return previous;}
    const artifact={relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)};artifacts.push(artifact);return artifact;
  };
  for(const artifact of [...rules.artifacts,...(factories?.artifacts??algebraic?.artifacts??[]),...(events?.artifacts??[])])add(artifact.relative_path,artifact.content);
  const modules=actions.map(action=>{
    // A module's identity belongs to this action, not to sibling requests in
    // the batch. Workflow and project composition must emit identical bytes.
    const ownRuleRoots=[...new Set(action.guards.map(g=>g.selector))].sort();
    const ownRules=canonicalJson(ownRuleRoots)===canonicalJson(ruleRoots)?rules:planConfiguredRules(graph,{schema_version:STRUCTURED_RULE_VERSION,language:'typescript',module_root:selection.module_root,value_profile:EXACT_UINT64_PROFILE,roots:ownRuleRoots},sources.rules);
    const ownEventRoots=[...new Set(action.events.map(e=>e.target))].sort();
    const ownEvents=canonicalJson(ownEventRoots)===canonicalJson(eventRoots)?events:ownEventRoots.length?planConfiguredEvents(graph,boundary,{schema_version:CONFIGURED_EVENT_VERSION,language:'typescript',module_root:selection.module_root,value_profile:EVENT_VALUE_PROFILE,boundary_sha256:boundary.boundary_sha256,roots:ownEventRoots},sources.events):null;
    const selector=action.bindings.selector,[feature,id]=selector.split(':') as [string,string];
    const relative_path=selection.module_root+'/features/'+feature+'/src/'+cell.role+'/'+id+'.ts',provider_path=relative_path.replace(/\.ts$/,'.provider.ts'),callable='operation'+id.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
    const rel=(target:string)=>{const p=path.posix.relative(path.posix.dirname(provider_path),target).replace(/\.ts$/,'.js');return p.startsWith('.')?p:'./'+p;};
    const ruleImports=action.guards.map((g,i)=>{const m=rules.modules.find(m=>m.selector===g.selector)??fail('missing Rule');return {selector:g.selector,path:rel(m.relative_path),symbol:m.callable,local:'guard'+i};});
    const eventImports=[...new Set(action.events.map(e=>e.target))].sort().map((selector,i)=>{const m=events?.modules.find(m=>m.selector===selector)??fail('missing Event');return {selector,path:rel(m.relative_path),symbol:m.callable,local:'makeEvent'+i};});
    const provider=add(provider_path,renderConfiguredOperation(action,fields?.model??null,valueProviders,provider_path,ruleImports,eventImports));
    const descriptorBody={schema_version:'domainspec.generated-operation-descriptor/v1-candidate',protocol_id:'typescript.bound-operation/v1',selector,source:action.source,action_sha256:action.action_sha256,bindings:action.bindings,
      source_compatibility:'explicit-action-bindings-not-legacy-typed-v1',value_profile:EXACT_UINT64_PROFILE,return_semantics:'awaited-explicit-outcome',effect_contract:'state-and-outbox',continuation:'awaited-settlement',
      rule_plan_sha256:ownRules.plan_sha256,factory_plan_sha256:factories?.plan_sha256??null,event_plan_sha256:ownEvents?.plan_sha256??null,field_model_sha256:fields?.model.model_sha256??null,
      ...(factories?{}:{minimal_context_sha256:MINIMAL_VALUE_CONTEXT_SHA256,...(algebraic?{algebraic_plan_sha256:algebraic.plan_sha256}:{})}),
      execution_obligations:action.execution_obligations,transaction_provider:'explicit-external-dependency',provider_durability_claim:false,publication:false,primary_callable_count:1,provider:{sha256:provider.sha256},authority_effect:'none'};
    const descriptor={...descriptorBody,descriptor_sha256:sha256(canonicalJson(descriptorBody))};
    add(relative_path,'import {execute} from '+JSON.stringify('./'+id+'.provider.js')+';\nexport type {OperationInput,OperationValue,OperationOutcome,OperationDependencies,OperationBatch,Transaction,CommitReceipt,ReadRequest,WriteIntent,EventIntent} from '+JSON.stringify('./'+id+'.provider.js')+';\nexport const '+callable+'=Object.freeze(Object.assign(execute,{descriptor:'+frozenLiteral(descriptor)+'}));\n');
    return {selector,relative_path,provider_path,callable,rule_imports:ruleImports,event_imports:eventImports,descriptor};
  });
  artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  const body={schema_version:'domainspec.configured-operations-plan/v1-candidate' as const,selection:{...selection,actions,factories:factories?.selection.factories??algebraic?.selection.factories??[]},certificate,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null,
    operation_contract_sha256:OPERATION_GENERATION_CONTRACT_SHA256,rule_plan:rules,factory_plan:factories,...(algebraic?{algebraic_plan:algebraic}:{}),event_plan:events,modules,artifacts,authority_effect:'none' as const};
  return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
