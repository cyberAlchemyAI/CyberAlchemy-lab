import path from 'node:path';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCheckedWorkflowBindings, COMPOSED_WORKFLOW_CONTRACT_SHA256, type CheckedWorkflowBindings} from '../typed-operation/workflow-bindings.js';
import {assertCheckedWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_CONTRACT_SHA256, type CheckedWorkflowRecoveryPolicy} from '../typed-operation/workflow-recovery.js';
import {WORKFLOW_OUTCOME_CONTRACT_SHA256} from '../typed-operation/workflow-outcomes.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezeWorkflow, workflowObject} from '../typed-backend/workflow-occurrences.js';
import {planConfiguredOperations, CONFIGURED_OPERATION_VERSION, type ConfiguredOperationSelection, type OperationConfigurationSources} from './configured-operations.js';
import {renderWorkflowMaterialization} from './workflow-materialization-source.js';
import {renderConfiguredWorkflow} from './configured-workflow-source.js';
import type {PlannedArtifact} from './contracts.js';
import {assertConfiguredComposedOperationsPlan, type ConfiguredComposedOperationsPlan} from './configured-composed-operations.js';
import {getReconciledSource as source} from './reconciled-sources.js';
import {composedPrecommitStages} from '../typed-operation/composed-settlement.js';
export const CONFIGURED_WORKFLOW_VERSION='domainspec.configured-workflow-selection/v1-candidate';
export const WORKFLOW_GENERATION_CONTRACT_SHA256='6b6da704b6478b66525e0b2b91240ab136fac0698ca04a57527c1f9b0c635aa2';
export interface ConfiguredWorkflowSelection {
 readonly schema_version:typeof CONFIGURED_WORKFLOW_VERSION;readonly language:'typescript';readonly module_root:string;
 readonly workflow:CheckedWorkflowBindings;readonly policy:CheckedWorkflowRecoveryPolicy;
 readonly actions:ConfiguredOperationSelection['actions'];readonly factories:ConfiguredOperationSelection['factories'];
}
export interface WorkflowConfigurationSources {
 readonly workflow_contract:string;readonly materialization_contract:string;readonly outcome_contract:string;readonly recovery_contract:string;
 readonly operations:OperationConfigurationSources;
}
const fail=(m:string):never=>{throw new TypeError('DS_CONFIGURED_WORKFLOW:'+m);};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>'com'+(i+1)+' lpt'+(i+1)).join(' ')).split(' '));
const closed=(v:unknown,names:readonly string[])=>{
 if(!v||typeof v!=='object'||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))return fail('plain input');
 const d=Object.getOwnPropertyDescriptors(v);
 if(Reflect.ownKeys(d).some(k=>typeof k!=='string'||!names.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))return fail('inert input');
 workflowObject(v,names);
};
export function planConfiguredWorkflow(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,selection:ConfiguredWorkflowSelection,sources:WorkflowConfigurationSources){
 assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);if(fields!==null)assertCompiledProjectFields(fields);
 closed(selection,['schema_version','language','module_root','workflow','policy','actions','factories']);
 closed(sources,['workflow_contract','materialization_contract','outcome_contract','recovery_contract','operations']);
 if(selection.schema_version!==CONFIGURED_WORKFLOW_VERSION||selection.language!=='typescript')return fail('selection');
 const workflow=selection.workflow,policy=selection.policy;assertCheckedWorkflowBindings(workflow);assertCheckedWorkflowRecoveryPolicy(policy);
 if(policy.workflow!==workflow)return fail('policy Workflow identity');
 const certificate=createCompiledProjectCertificate(graph);
 if(workflow.certificate.graph_sha256!==certificate.graph_sha256||workflow.boundary_sha256!==boundary.boundary_sha256||workflow.field_compilation_sha256!==(fields?.compilation_sha256??null))return fail('stale Workflow');
 for(const [source,hash]of [[sources.workflow_contract,WORKFLOW_GENERATION_CONTRACT_SHA256],[sources.outcome_contract,WORKFLOW_OUTCOME_CONTRACT_SHA256],[sources.recovery_contract,WORKFLOW_RECOVERY_CONTRACT_SHA256]])
  if(typeof source!=='string'||sha256(source)!==hash)return fail('definition drift');
 const operationPlan=planConfiguredOperations(graph,boundary,fields,{schema_version:CONFIGURED_OPERATION_VERSION,language:selection.language,module_root:selection.module_root,actions:selection.actions,factories:selection.factories},sources.operations);
 return finishWorkflowPlan(graph,fields,selection,sources,operationPlan);
}

export interface ComposedWorkflowSelection {
 readonly schema_version:'domainspec.composed-workflow-selection/v1-candidate';
 readonly language:'typescript'; readonly module_root:string;
 readonly workflow:CheckedWorkflowBindings; readonly policy:CheckedWorkflowRecoveryPolicy;
 readonly operation_plan:ConfiguredComposedOperationsPlan;
}

/** Native composition only; no publication, provider invocation or automatic compensation. */
export function planConfiguredComposedWorkflow(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields,selection:ComposedWorkflowSelection,contractSource:string){
 assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);assertCompiledProjectFields(fields);
 closed(selection,['schema_version','language','module_root','workflow','policy','operation_plan']);
 if(selection.schema_version!=='domainspec.composed-workflow-selection/v1-candidate'||selection.language!=='typescript')return fail('composed selection');
 if(typeof contractSource!=='string'||sha256(contractSource)!==COMPOSED_WORKFLOW_CONTRACT_SHA256)return fail('composed definition drift');
 const workflow=selection.workflow,policy=selection.policy,operations=selection.operation_plan;
 assertCheckedWorkflowBindings(workflow);assertCheckedWorkflowRecoveryPolicy(policy);assertConfiguredComposedOperationsPlan(operations);
 if(workflow.composition_contract_sha256!==COMPOSED_WORKFLOW_CONTRACT_SHA256)return fail('composed Workflow required');
 const certificate=createCompiledProjectCertificate(graph);
 if(policy.workflow!==workflow||workflow.certificate.graph_sha256!==certificate.graph_sha256||workflow.boundary_sha256!==boundary.boundary_sha256||workflow.field_compilation_sha256!==fields.compilation_sha256)return fail('stale composed Workflow');
 if(operations.certificate.graph_sha256!==certificate.graph_sha256||operations.selection.module_root!==selection.module_root||operations.selection.language!==selection.language)return fail('stale composed operation plan');
 // Each checked action additionally carries exact boundary and field custody.
 for(const row of operations.selection.actions)if(row.action.boundary_sha256!==boundary.boundary_sha256||row.action.field_compilation_sha256!==fields.compilation_sha256)return fail('stale composed action evidence');
 for(const call of [...workflow.steps,...workflow.compensations]){
  const row=operations.selection.actions.find(row=>row.action.bindings.selector===call.operation_ref);
  if(!row||canonicalJson(call.precommit_stages)!==canonicalJson(composedPrecommitStages(row.action,row.absence_failures)))return fail('composed settlement vocabulary mismatch');
 }
 const common={configuration:source('configuration'),base:source('base'),typescript:source('typescript')};
 const rules={...common,rule_contract:source('rule'),collection_contract:source('rule_collection'),predicate_contract:source('rule_predicate'),numeric_contract:source('rule_numeric'),exact_contract:source('rule_exact'),literal_contract:source('rule_literal'),structured_contract:source('rule_structured'),field_contract:source('field')};
 const sources:WorkflowConfigurationSources={workflow_contract:source('workflow'),materialization_contract:source('workflow_materialization'),outcome_contract:source('workflow_outcome'),recovery_contract:source('workflow_recovery'),operations:{operation_contract:source('operation'),factory_contract:source('factory'),enum_provider:source('enum_provider'),rules,events:{...common,event_contract:source('event')}}};
 return finishWorkflowPlan(graph,fields,selection,sources,operations);
}

function finishWorkflowPlan(graph:CompiledProjectGraph,fields:CompiledProjectFields|null,selection:ConfiguredWorkflowSelection|ComposedWorkflowSelection,sources:WorkflowConfigurationSources,operationPlan:ReturnType<typeof planConfiguredOperations>|ConfiguredComposedOperationsPlan){
 const workflow=selection.workflow,policy=selection.policy,certificate=createCompiledProjectCertificate(graph);
 const required=new Map([...workflow.steps,...workflow.compensations].map(s=>[s.operation_ref,s.action_sha256]));
 if(operationPlan.modules.length!==required.size||operationPlan.modules.some(m=>required.get(m.selector)!==m.descriptor.action_sha256))return fail('exact action closure');
 const [feature,id]=workflow.bindings.selector.split(':') as [string,string];
 // Operation planning already enforces safe feature/action/module-root segments.
 if(![feature,id].every(v=>/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(v)?.[0]===v&&!reserved.has(v)))return fail('unsafe Workflow selector');
 const config=JSON.parse(sources.operations.rules.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='Workflow');
 if(cell?.role!=='application/workflows'||canonicalJson(cell.blocked_by)!=='["DSR-011","DSR-017"]')return fail('Workflow role');
 const overlay=JSON.parse(sources.operations.rules.typescript).representation_overlays.find((o:{contract_id:string})=>o.contract_id==='workflow.profile-representation');
 const protocol=overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='typescript.bound-workflow/v1');
 if(protocol?.form_id!=='typescript.workflow-step-orchestrator')return fail('Workflow protocol');
 const relative_path=selection.module_root+'/features/'+feature+'/src/'+cell.role+'/'+id+'.ts';
 const material_path=relative_path.replace(/\.ts$/,'.material.ts'),provider_path=relative_path.replace(/\.ts$/,'.provider.ts');
 const material=renderWorkflowMaterialization(graph,workflow,fields,sources.materialization_contract);
 const artifacts:PlannedArtifact[]=[...operationPlan.artifacts];
 const add=(relative_path:string,content:string)=>{
  if(artifacts.some(a=>a.relative_path===relative_path))return fail('artifact collision');
  artifacts.push({relative_path,content,sha256:sha256(content),size_bytes:Buffer.byteLength(content)});
 };
 add(material_path,material.content);
 const rel=(target:string)=>{const p=path.posix.relative(path.posix.dirname(provider_path),target).replace(/\.ts$/,'.js');return p.startsWith('.')?p:'./'+p;};
 const imports=[...new Set(workflow.steps.map(s=>s.operation_ref))].sort().map((selector,i)=>{
  const m=operationPlan.modules.find(m=>m.selector===selector)!;
  return {selector,path:rel(m.relative_path),symbol:m.callable,local:'forward'+i,action_sha256:m.descriptor.action_sha256,descriptor_sha256:m.descriptor.descriptor_sha256};
 });
 const rendered=renderConfiguredWorkflow(workflow,policy,rel(material_path),imports);
 add(provider_path,rendered);
 const body={schema_version:'domainspec.generated-workflow-descriptor/v1-candidate',protocol_id:'typescript.bound-workflow/v1',form_id:'typescript.workflow-step-orchestrator',primary_callable_count:1,selector:workflow.bindings.selector,workflow_sha256:workflow.workflow_sha256,
  policy_sha256:policy.policy_sha256,contract_sha256:WORKFLOW_GENERATION_CONTRACT_SHA256,material_sha256:material.sha256,provider_sha256:sha256(rendered),
  ...(selection.schema_version==='domainspec.composed-workflow-selection/v1-candidate'?{composition_contract_sha256:COMPOSED_WORKFLOW_CONTRACT_SHA256}:{}),
  operation_plan_sha256:operationPlan.plan_sha256,operation_imports:imports,compensation_execution:false,publication:false,authority_effect:'none'};
 const descriptor=freezeWorkflow({...body,descriptor_sha256:sha256(canonicalJson(body))});
 const callable='workflow'+id.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
 add(relative_path,'import {execute} from '+JSON.stringify('./'+id+'.provider.js')+';\nexport type {WorkflowInput,WorkflowIdentity,WorkflowDependencies,WorkflowOutcome} from '+JSON.stringify('./'+id+'.provider.js')+';\nexport const '+callable+'=Object.freeze(Object.assign(execute,{descriptor:'+literal(descriptor)+'}));\n');
 artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
 const normalized=selection.schema_version==='domainspec.composed-workflow-selection/v1-candidate'
  ?{schema_version:selection.schema_version,language:selection.language,module_root:selection.module_root,workflow_sha256:workflow.workflow_sha256,policy_sha256:policy.policy_sha256,operation_plan_sha256:operationPlan.plan_sha256}
  :{...selection,actions:operationPlan.selection.actions,factories:operationPlan.selection.factories};
 const plan={schema_version:selection.schema_version==='domainspec.composed-workflow-selection/v1-candidate'?'domainspec.composed-workflow-plan/v1-candidate':'domainspec.configured-workflow-plan/v1-candidate',selection:normalized,certificate,operation_plan:operationPlan,
  modules:[{selector:workflow.bindings.selector,relative_path,provider_path,material_path,callable,descriptor}],artifacts,authority_effect:'none'};
 return freezeWorkflow({...plan,plan_sha256:sha256(canonicalJson(plan))});
}
function literal(v:unknown):string {
 if(Array.isArray(v))return 'Object.freeze(['+v.map(literal).join(',')+'])';
 if(v&&typeof v==='object')return 'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+JSON.stringify(k)+']:'+literal(x)).join(',')+'})';
 return JSON.stringify(v);
}
