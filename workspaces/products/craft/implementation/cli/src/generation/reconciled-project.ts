import {assertCompiledProjectSnapshot,loadCompiledProjectGraph,type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../input/composition-boundary.js';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256,type ProjectFieldSelection} from '../input/compiled-field-model.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {decodeWorkflowOccurrences,workflowOperationRefs} from '../typed-backend/workflow-occurrences.js';
import {compileOperationActionBindings,decodeOperationActionBindings,type OperationActionBindings} from '../typed-operation/action-bindings.js';
import {compileWorkflowBindings,compileComposedWorkflowBindings,decodeWorkflowBindings,WORKFLOW_BINDINGS_VERSION,type WorkflowBindings} from '../typed-operation/workflow-bindings.js';
import {selectWorkflowRecoveryPolicy,WORKFLOW_RECOVERY_POLICY_VERSION,WORKFLOW_RECOVERY_CONTRACT_SHA256,type WorkflowRecoverySelection} from '../typed-operation/workflow-recovery.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {getReconciledSource as source,getReconciledSourceCapsule} from './reconciled-sources.js';
import {planResolvedArtifacts,planResolvedComposedArtifacts,COMPOSED_PROJECT_CONTRACT_SHA256,RESOLVED_COMPOSED_SELECTION_VERSION,RESOLVED_ARTIFACT_LAYOUT,RESOLVED_ARTIFACT_SELECTION_VERSION,type ResolvedGeneratorRequest} from './resolved-artifact-plan.js';
import {decodeOperationValueComposition,type OperationValueComposition} from '../typed-operation/value-composition.js';
import {compileComposedOperation,planComposedOperations} from './composed-operations-api.js';
import type {ComposedWorkflowAction} from '../typed-operation/composed-settlement.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {STRUCTURED_RULE_VERSION} from './configured-rules.js';
import type {FactoryBinding} from './configured-factories.js';
import {planResolvedCompositionBindings} from './resolved-composition-bindings.js';

export const PUBLIC_COMPOSITION_INTEGRATION_DEFINITION_SHA256='83a221975d11b41d34b578b5b848ff06e30cbaf0d8f651277f12b5cf55506080';

export const RECONCILED_COMPILATION_VERSION='domainspec.reconciled-compilation/v1-candidate';
export const RECONCILED_TYPESCRIPT_PROFILE='domainspec.reconciled-typescript/v1-candidate';
export const COMPOSED_RECONCILED_COMPILATION_VERSION='domainspec.reconciled-compilation/v2-candidate';
export const COMPOSED_RECONCILED_TYPESCRIPT_PROFILE='domainspec.reconciled-typescript/v2-candidate';
export const RECONCILED_COMPILATION_DEFINITION_SHA256='6cc96755be9bf59c409b0b3a7ae545f58f555997630f94271ad15b4508afbe08';
type AuthoredCall<T> = Omit<T,'action_sha256'>;
export interface ReconciledWorkflowBinding {
 readonly selector:string;
 readonly inputs:WorkflowBindings['inputs'];
 readonly event_inputs:WorkflowBindings['event_inputs'];
 readonly steps:readonly AuthoredCall<WorkflowBindings['steps'][number]>[];
 readonly compensations:readonly AuthoredCall<WorkflowBindings['compensations'][number]>[];
 readonly result:WorkflowBindings['result'];
 readonly recovery:Pick<WorkflowRecoverySelection,'dependency_semantics'|'tie_break'>;
}
export interface ReconciledCompilationSelection {
 readonly schema_version:typeof RECONCILED_COMPILATION_VERSION;
 readonly profile_id:typeof RECONCILED_TYPESCRIPT_PROFILE;
 readonly language:'typescript';
 readonly module_root:string;
 readonly layout_version:typeof RESOLVED_ARTIFACT_LAYOUT;
 readonly value_profile:typeof EXACT_UINT64_PROFILE;
 readonly field_bindings:ProjectFieldSelection['bindings'];
 readonly factories:readonly FactoryBinding[];
 readonly operations:readonly OperationActionBindings[];
 readonly workflows:readonly ReconciledWorkflowBinding[];
}
export interface ComposedReconciledCompilationSelection extends Omit<ReconciledCompilationSelection,'schema_version'|'profile_id'>{
 readonly schema_version:typeof COMPOSED_RECONCILED_COMPILATION_VERSION;
 readonly profile_id:typeof COMPOSED_RECONCILED_TYPESCRIPT_PROFILE;
 readonly value_compositions:readonly Readonly<{composition:OperationValueComposition;absence_failures:ComposedWorkflowAction['absence_failures']}>[];
}
export class ReconciledCompilationError extends Error {
 readonly exitCode=22;
 constructor(readonly code:string,readonly pointer:string,message:string){super(code+':'+pointer+':'+message);this.name='ReconciledCompilationError';}
}
const fail=(pointer:string,message:string):never=>{throw new ReconciledCompilationError('DS_RECONCILED_COMPILATION',pointer,message);};
function closed(value:unknown,names:readonly string[],pointer:string):Record<string,unknown>{
 if(!value||typeof value!=='object'||Array.isArray(value)||canonicalJson(Object.keys(value).sort())!==canonicalJson([...names].sort()))fail(pointer,'unknown or missing fields');
 return value as Record<string,unknown>;
}
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
function exact(actual:readonly string[],expected:readonly string[],pointer:string){
 if(new Set(actual).size!==actual.length||canonicalJson([...actual].sort())!==canonicalJson([...expected].sort()))fail(pointer,'exact qualified binding coverage required');
}
/** Decode authored data only. Graph-dependent checks remain in compilation. */
export function decodeReconciledCompilationSelection(value:unknown):ReconciledCompilationSelection{
 assertInterfaceData(value);
 const row=closed(value,['schema_version','profile_id','language','module_root','layout_version','value_profile','field_bindings','factories','operations','workflows'],'/selection');
 if(row.schema_version!==RECONCILED_COMPILATION_VERSION||row.profile_id!==RECONCILED_TYPESCRIPT_PROFILE||row.language!=='typescript'||row.layout_version!==RESOLVED_ARTIFACT_LAYOUT||row.value_profile!==EXACT_UINT64_PROFILE)fail('/selection','unsupported explicit version/profile/language/layout/value combination');
 if(typeof row.module_root!=='string'||row.module_root.length>256||!row.module_root.split('/').every(s=>/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(s)?.[0]===s))fail('/module_root','normalized portable module root required');
 for(const key of ['field_bindings','factories','operations','workflows'])if(!Array.isArray(row[key])||(row[key] as unknown[]).length>256)fail('/'+key,'bounded array required');
 for(const [index,factory] of (row.factories as unknown[]).entries()){
  const f=closed(factory,['selector','base_validators','extensions'],'/factories/'+index);
  if(typeof f.selector!=='string'||!Array.isArray(f.base_validators)||!Array.isArray(f.extensions))fail('/factories/'+index,'authored factory binding required');
 }
 const operations=(row.operations as unknown[]).map(decodeOperationActionBindings);
 const workflows=(row.workflows as unknown[]).map((value,index)=>{
  const p='/workflows/'+index,w=closed(value,['selector','inputs','event_inputs','steps','compensations','result','recovery'],p);
  const calls=(values:unknown,id:string)=>{
   if(!Array.isArray(values))return fail(p+'/'+id,'array required');
   return values.map(v=>({...closed(v,[id,'arguments','events'],p+'/'+id),action_sha256:'0'.repeat(64)}));
  };
  const recovery=closed(w.recovery,['dependency_semantics','tie_break'],p+'/recovery');
  if(recovery.dependency_semantics!=='needed-compensations-only'||recovery.tie_break!=='reverse-completion')fail(p+'/recovery','unsupported explicit recovery selection');
  const decoded=decodeWorkflowBindings({schema_version:WORKFLOW_BINDINGS_VERSION,selector:w.selector,inputs:w.inputs,event_inputs:w.event_inputs,steps:calls(w.steps,'step_id'),compensations:calls(w.compensations,'compensation_id'),result:w.result});
  const strip=<T extends {action_sha256:string}>(call:T)=>{const {action_sha256,...rest}=call;return rest;};
  return {selector:decoded.selector,inputs:decoded.inputs,event_inputs:decoded.event_inputs,steps:decoded.steps.map(strip),compensations:decoded.compensations.map(strip),result:decoded.result,recovery:{dependency_semantics:'needed-compensations-only' as const,tie_break:'reverse-completion' as const}};
 });
 return freeze({...structuredClone(row),operations,workflows} as unknown as ReconciledCompilationSelection);
}

const checked=new WeakSet<object>();
export function decodeComposedReconciledCompilationSelection(value:unknown):ComposedReconciledCompilationSelection{
 assertInterfaceData(value);
 const row=closed(value,['schema_version','profile_id','language','module_root','layout_version','value_profile','field_bindings','factories','operations','workflows','value_compositions'],'/selection');
 if(row.schema_version!==COMPOSED_RECONCILED_COMPILATION_VERSION||row.profile_id!==COMPOSED_RECONCILED_TYPESCRIPT_PROFILE)fail('/selection','explicit composed version and profile required');
 const {value_compositions,...base}=row;
 const old=decodeReconciledCompilationSelection({...base,schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE});
 if(!Array.isArray(value_compositions)||value_compositions.length>256)fail('/value_compositions','bounded array required');
 const rows=(value_compositions as unknown[]).map((value,i)=>{
  const row=closed(value,['composition','absence_failures'],'/value_compositions/'+i);
  const composition=decodeOperationValueComposition(row.composition);
  if(!Array.isArray(row.absence_failures)||row.absence_failures.length>256)fail('/absence_failures','bounded array required');
  const absence_failures=(row.absence_failures as unknown[]).map(value=>{
   const a=closed(value,['binding','code'],'/absence_failures');
   if(typeof a.binding!=='string'||typeof a.code!=='string'||/^[A-Z][A-Z0-9_]{0,127}$/.exec(a.code)?.[0]!==a.code)fail('/absence_failures','explicit binding and code required');
   return {binding:a.binding as string,code:a.code as string};
  }).sort((a,b)=>a.binding<b.binding?-1:a.binding>b.binding?1:0);
  return {composition,absence_failures};
 }).sort((a,b)=>a.composition.operation_ref<b.composition.operation_ref?-1:a.composition.operation_ref>b.composition.operation_ref?1:0);
 exact(rows.map(row=>row.composition.operation_ref),old.operations.map(a=>a.selector),'/value_compositions');
 return freeze({...old,schema_version:COMPOSED_RECONCILED_COMPILATION_VERSION,profile_id:COMPOSED_RECONCILED_TYPESCRIPT_PROFILE,value_compositions:rows});
}
export type ReconciledProjectPlan=ReturnType<typeof planCompiledReconciledProject>;
export type ComposedReconciledProjectPlan=ReturnType<typeof planCompiledComposedReconciledProject>;
export function assertReconciledProjectPlan(value:unknown):asserts value is ReconciledProjectPlan|ComposedReconciledProjectPlan {
 if(!value||typeof value!=='object'||!checked.has(value))fail('/plan','registered reconciled project required');
}
/** Construct checked bindings and generator selections from one immutable graph. */
export function planCompiledReconciledProject(graph:CompiledProjectGraph,value:unknown){
 assertCompiledProjectSnapshot(graph);
 return planCompiledProjectCore(graph,decodeReconciledCompilationSelection(value));
}
export function planCompiledComposedReconciledProject(graph:CompiledProjectGraph,value:unknown){
 assertCompiledProjectSnapshot(graph);
 return planCompiledProjectCore(graph,decodeComposedReconciledCompilationSelection(value));
}
function planCompiledProjectCore<S extends ReconciledCompilationSelection|ComposedReconciledCompilationSelection>(graph:CompiledProjectGraph,selection:S){
 assertCompiledProjectSnapshot(graph);
 const composed='value_compositions' in selection;
 if(composed&&sha256(source('composed_project'))!==COMPOSED_PROJECT_CONTRACT_SHA256)fail('/definition','composed project definition drift');
 if(sha256(source('reconciled_compilation'))!==RECONCILED_COMPILATION_DEFINITION_SHA256)fail('/definition','compiler definition drift');
 if(sha256(source('public_composition_integration'))!==PUBLIC_COMPOSITION_INTEGRATION_DEFINITION_SHA256)fail('/definition','public composition integration definition drift');
 const certificate=createCompiledProjectCertificate(graph),roots=(kind:string)=>graph.nodes.filter(n=>n.kind===kind).map(n=>n.selector).sort();
 const known=new Set(['Entity','Value Object','Enum','Rule','Calculation','Policy','Query','Operation','Workflow','State Machine','Mapping','Event','Interface']);
 if(!graph.nodes.length||graph.nodes.some(n=>!known.has(n.kind)))fail('/nodes','nonempty supported metatype project required');
 const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},source('composition'));
 const dataRoots=[...roots('Entity'),...roots('Value Object'),...roots('Enum')].sort();
 if(!dataRoots.length&&selection.field_bindings.length)fail('/field_bindings','no domain fields to bind');
 const fields=dataRoots.length?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:dataRoots,bindings:selection.field_bindings},source('field')):null;
 exact(selection.factories.map(f=>f.selector),[...roots('Entity'),...roots('Value Object')],'/factories');
 exact(selection.operations.map(a=>a.selector),roots('Operation'),'/operations');
 exact(selection.workflows.map(w=>w.selector),roots('Workflow'),'/workflows');
 if(composed&&!fields)fail('/fields','composed project requires its actual checked domain field closure');
 const legacyActions=composed?[]:selection.operations.map(a=>compileOperationActionBindings(graph,boundary,fields,a,source('operation_action')));
 const composedActions:ComposedWorkflowAction[]=composed?selection.operations.map(a=>{
  const row=selection.value_compositions.find(row=>row.composition.operation_ref===a.selector)!;
  return {action:compileComposedOperation(graph,boundary,fields!,row.composition,a),absence_failures:row.absence_failures};
 }):[];
 const actions=[...legacyActions,...composedActions.map(row=>row.action)];
 const common={configuration:source('configuration'),base:source('base'),typescript:source('typescript')};
 const rules={...common,rule_contract:source('rule'),collection_contract:source('rule_collection'),predicate_contract:source('rule_predicate'),numeric_contract:source('rule_numeric'),exact_contract:source('rule_exact'),literal_contract:source('rule_literal'),structured_contract:source('rule_structured'),field_contract:source('field')};
 const factories={...rules,factory_contract:source('factory'),enum_provider:source('enum_provider')};
 const events={...common,event_contract:source('event')};
 const operations={operation_contract:source('operation'),factory_contract:source('factory'),enum_provider:source('enum_provider'),rules,events};
 const layout={language:'typescript' as const,module_root:selection.module_root},exactSelection={...layout,value_profile:EXACT_UINT64_PROFILE,boundary_sha256:boundary.boundary_sha256};
 const requests:ResolvedGeneratorRequest[]=[];
 const request=(r:ResolvedGeneratorRequest)=>requests.push(r);
 if(fields){
  if(selection.factories.length)request({kind:'factories',fields,selection:{schema_version:'domainspec.configured-factories-selection/v12-candidate',...layout,field_compilation_sha256:fields.compilation_sha256,rule_selection:{schema_version:STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE},factories:selection.factories},sources:factories});
  else request({kind:'algebraic-enums',fields,selection:{schema_version:'domainspec.configured-algebraic-enums-selection/v1-candidate',...layout,field_compilation_sha256:fields.compilation_sha256,factories:[]},sources:{standalone_contract:source('standalone_sum'),factories}});
 }
 if(roots('Rule').length)request({kind:'rules',fields:null,selection:{schema_version:STRUCTURED_RULE_VERSION,...layout,value_profile:EXACT_UINT64_PROFILE,roots:roots('Rule')},sources:rules});
 for(const version of [1,2] as const){
  const selected=graph.nodes.filter(n=>n.kind==='Calculation'&&(n.body.typed_contract as {schema_version?:string}|undefined)?.schema_version==='domainspec.typed-calculation/v'+version).map(n=>n.selector).sort();
  if(selected.length){if(version===1)request({kind:'calculations-v1',fields:null,selection:{schema_version:'domainspec.configured-calculations-selection/v1-candidate',...exactSelection,roots:selected},sources:{...common,calculation_contract:source('calculation_v1')}});
  else request({kind:'calculations-v2',fields:null,selection:{schema_version:'domainspec.configured-calculations-selection/v2-candidate',...exactSelection,roots:selected},sources:{...common,calculation_contract:source('calculation_v2')}});}
 }
 if(graph.nodes.some(n=>n.kind==='Calculation'&&!['domainspec.typed-calculation/v1','domainspec.typed-calculation/v2'].includes((n.body.typed_contract as {schema_version?:string}|undefined)?.schema_version??'')))fail('/Calculation','explicit supported typed Calculation required');
 const domainMappings=graph.nodes.filter(n=>n.kind==='Mapping'&&(n.body.typed_contract as {schema_version?:string}|undefined)?.schema_version!=='domainspec.typed-mapping/v3').map(n=>n.selector).sort();
 if(roots('Query').length||domainMappings.length){
  if(!fields)fail('/fields','Query or domain Mapping requires its actual checked domain closure');
  if(roots('Query').length)request({kind:'queries',fields:fields!,selection:{schema_version:'domainspec.configured-queries-selection/v1-candidate',...exactSelection,field_compilation_sha256:fields!.compilation_sha256,roots:roots('Query')},sources:{...common,query_contract:source('query')}});
  if(domainMappings.length)request({kind:'mappings',fields:fields!,selection:{schema_version:'domainspec.configured-mappings-selection/v1-candidate',...exactSelection,field_compilation_sha256:fields!.compilation_sha256,roots:domainMappings},sources:{...common,mapping_contract:source('mapping')}});
 }
 if(roots('Policy').length)request({kind:'policies',fields,selection:{schema_version:'domainspec.configured-policies-selection/v1-candidate',...exactSelection,field_compilation_sha256:fields?.compilation_sha256??null,rule_selection:STRUCTURED_RULE_VERSION,roots:roots('Policy')},sources:{policy_contract:source('policy'),rules}});
 if(roots('Event').length)request({kind:'events',fields:null,selection:{schema_version:'domainspec.configured-events-selection/v1-candidate',...layout,value_profile:'domainspec.event-values/v1-candidate',boundary_sha256:boundary.boundary_sha256,roots:roots('Event')},sources:events});
 if(legacyActions.length)request({kind:'operations',fields,selection:{schema_version:'domainspec.configured-operations-selection/v1-candidate',...layout,actions:legacyActions,factories:selection.factories},sources:operations});
 if(composedActions.length)request({kind:'composed-operations',fields:fields!,selection:{schema_version:'domainspec.configured-composed-operations-selection/v1-candidate',...layout,actions:composedActions,factories:selection.factories},sources:source('composed_operation')});
 for(const authored of selection.workflows){
  const node=graph.nodes.find(n=>n.selector===authored.selector)!;
  const declared=decodeWorkflowOccurrences(node.body.typed_contract),refs=workflowOperationRefs(declared);
  const used=actions.filter(a=>refs.includes(a.bindings.selector));
  const steps=authored.steps.map(call=>{const operation=declared.steps.find(s=>s.step_id===call.step_id)?.operation_ref,action=used.find(a=>a.bindings.selector===operation);if(!action)return fail('/workflows/steps','unknown source occurrence or missing action');return {...call,action_sha256:action.action_sha256};});
  const compensations=authored.compensations.map(call=>{const operation=declared.compensations.find(s=>s.compensation_id===call.compensation_id)?.operation_ref,action=used.find(a=>a.bindings.selector===operation);if(!action)return fail('/workflows/compensations','unknown source occurrence or missing action');return {...call,action_sha256:action.action_sha256};});
  const {recovery,...bindings}=authored;
  const value={...bindings,schema_version:WORKFLOW_BINDINGS_VERSION,steps,compensations};
  const composedUsed=composedActions.filter(row=>refs.includes(row.action.bindings.selector));
  const workflow=composed?compileComposedWorkflowBindings(graph,boundary,fields!,composedUsed,value,source('workflow_binding'),source('composed_workflow')):compileWorkflowBindings(graph,boundary,fields,legacyActions.filter(a=>refs.includes(a.bindings.selector)),value,source('workflow_binding'));
  const policy=selectWorkflowRecoveryPolicy(workflow,{schema_version:WORKFLOW_RECOVERY_POLICY_VERSION,workflow_sha256:workflow.workflow_sha256,contract_sha256:WORKFLOW_RECOVERY_CONTRACT_SHA256,...recovery},source('workflow_recovery'));
  if(composed){
   const operation_plan=planComposedOperations(graph,boundary,fields!,{schema_version:'domainspec.configured-composed-operations-selection/v1-candidate',...layout,actions:composedUsed,factories:selection.factories});
   request({kind:'composed-workflows',fields:fields!,selection:{schema_version:'domainspec.composed-workflow-selection/v1-candidate',...layout,workflow,policy,operation_plan},sources:source('composed_workflow')});
  }else request({kind:'workflows',fields,selection:{schema_version:'domainspec.configured-workflow-selection/v1-candidate',...layout,workflow,policy,actions:legacyActions.filter(a=>refs.includes(a.bindings.selector)),factories:selection.factories},sources:{workflow_contract:source('workflow'),materialization_contract:source('workflow_materialization'),outcome_contract:source('workflow_outcome'),recovery_contract:source('workflow_recovery'),operations}});
 }
 if(roots('State Machine').length)request({kind:'state-machines',fields,selection:{schema_version:'domainspec.configured-state-machines-selection/v1-candidate',...layout,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null,roots:roots('State Machine')},sources:{state_machine_contract:source('state_machine'),rules}});
 const publicRoots=graph.nodes.filter(n=>n.kind==='Interface'||n.kind==='Mapping'&&(n.body.typed_contract as {schema_version?:string}|undefined)?.schema_version==='domainspec.typed-mapping/v3').map(n=>n.selector).sort();
 if(publicRoots.length)request({kind:'public-boundaries',fields,selection:{schema_version:'domainspec.configured-public-boundaries-selection/v1-candidate',...layout,value_profile:EXACT_UINT64_PROFILE,roots:publicRoots},sources:{...common,generation_contract:source('public_boundary'),public_mapping_contract:source('public_mapping_value_object'),interface_contract:source('interface')}});
 const resolvedSelection={...layout,layout_version:selection.layout_version,graph_sha256:certificate.graph_sha256,boundary_sha256:boundary.boundary_sha256,requests};
 const resolved=composed?planResolvedComposedArtifacts(graph,boundary,{schema_version:RESOLVED_COMPOSED_SELECTION_VERSION,...resolvedSelection},source('resolved_artifact'),source('composed_project')):planResolvedArtifacts(graph,boundary,{schema_version:RESOLVED_ARTIFACT_SELECTION_VERSION,...resolvedSelection},source('resolved_artifact'));
 const represented=new Set(resolved.modules.flatMap(m=>m.qualified_selectors));
 if(graph.nodes.some(n=>!represented.has(n.selector)))fail('/coverage','every project node must have a native realization');
 const composition=graph.compositions?.length?planResolvedCompositionBindings(graph,resolved,source('resolved_composition_bindings')):null;
 const body={schema_version:'domainspec.reconciled-project-plan/v1-candidate' as const,selection,definition_sha256:RECONCILED_COMPILATION_DEFINITION_SHA256,...(composed?{composition_contract_sha256:COMPOSED_PROJECT_CONTRACT_SHA256}:{}),source_capsule_sha256:getReconciledSourceCapsule().capsule_sha256,checking_scope:'whole-project' as const,node_selectors:graph.nodes.map(n=>n.selector).sort(),resolved,composition,composition_integration_sha256:PUBLIC_COMPOSITION_INTEGRATION_DEFINITION_SHA256,authority_effect:'none' as const};
 const result=freeze({...body,plan_sha256:sha256(canonicalJson(body))});checked.add(result);return result;
}

export function planReconciledProject(sourceRoot:string,selection:unknown):ReconciledProjectPlan {
 const graph=loadCompiledProjectGraph(sourceRoot),result=planCompiledReconciledProject(graph,selection);
 if(loadCompiledProjectGraph(sourceRoot).source_manifest.manifest_sha256!==graph.source_manifest.manifest_sha256)fail('/source','source changed during planning');
 return result;
}

export function planComposedReconciledProject(sourceRoot:string,selection:unknown):ComposedReconciledProjectPlan{
 const graph=loadCompiledProjectGraph(sourceRoot),result=planCompiledComposedReconciledProject(graph,selection);
 if(loadCompiledProjectGraph(sourceRoot).source_manifest.manifest_sha256!==graph.source_manifest.manifest_sha256)fail('/source','source changed during planning');
 return result;
}

/** Exact byte projection, not a second generation path or graph-edge traversal. */
export function selectReconciledArtifacts(plan:ReconciledProjectPlan|ComposedReconciledProjectPlan,roots:readonly string[]|null=null){
 assertReconciledProjectPlan(plan);assertInterfaceData(roots);
 if(roots!==null&&(!Array.isArray(roots)||!roots.length||roots.length>256||new Set(roots).size!==roots.length||roots.some(s=>typeof s!=='string'||!plan.node_selectors.includes(s))))fail('/roots','unique existing qualified roots required');
 const compositionModules=plan.composition?.modules.map(m=>({...m,qualified_selectors:[] as string[],metatypes:[] as string[],artifact_role:'composition-adapter' as const,request_sha256s:[] as string[]}))??[];
 const compare=(a:{relative_path:string},b:{relative_path:string})=>a.relative_path<b.relative_path?-1:a.relative_path>b.relative_path?1:0;
 const selected=roots===null?plan.node_selectors:[...roots].sort(),modules=[...plan.resolved.modules,...compositionModules].sort(compare);
 const paths=new Set(modules.filter(m=>m.qualified_selectors.some(s=>selected.includes(s))).map(m=>m.relative_path));
 let grew=true;while(grew){grew=false;for(const m of modules)if(paths.has(m.relative_path))for(const i of m.imports)if(i.target_path&&!paths.has(i.target_path)){paths.add(i.target_path);grew=true;}}
 const artifacts=[...plan.resolved.artifacts,...(plan.composition?.artifacts??[])].filter(a=>roots===null||paths.has(a.relative_path)).sort(compare);
 const body={schema_version:'domainspec.reconciled-artifact-view/v1-candidate' as const,project_plan_sha256:plan.plan_sha256,roots:selected,checking_scope:plan.checking_scope,modules:modules.filter(m=>roots===null||paths.has(m.relative_path)),artifacts,authority_effect:'none' as const};
 return freeze({...body,view_sha256:sha256(canonicalJson(body))});
}
