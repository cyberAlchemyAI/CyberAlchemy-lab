import path from 'node:path';
import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {createWorkflowBinding} from './reconciled-workflow-binding.js';
import {workflowVerificationDefinitions} from './reconciled-workflow-controls.js';
import {createCrossGeneratorOperationSurface,type OperationSurfaceImport,type OperationSurfaceModule} from './reconciled-cross-generator-operation-surface.js';
import type {CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {WORKFLOW_MATERIALIZATION_CONTRACT_SHA256} from '../generation/workflow-materialization-source.js';

export const CROSS_GENERATOR_WORKFLOW_DEFINITION_SHA256='9fa395aa621f646cc5fbef5f00ac3822a41a53bd90d0eaba6e4cfec0df10908b';
const registered=new WeakSet<object>();
const fail=(message:string):never=>{throw new TypeError('CROSS_GENERATOR_WORKFLOW_SURFACE:'+message);};
const same=(a:unknown,b:unknown,reason:string)=>{if(canonicalJson(a)!==canonicalJson(b))fail(reason);};
const sorted=(v:readonly string[])=>[...new Set(v)].sort();
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
export interface WorkflowSurfaceImport extends Omit<OperationSurfaceImport,'target_path'>{
 readonly target_path:string|null;readonly namespace:boolean;readonly native_names?:readonly string[];
}
export interface WorkflowSurfaceModule extends Omit<OperationSurfaceModule,'imports'>{readonly imports:readonly WorkflowSurfaceImport[];}
const wrapperTypes=['WorkflowInput','WorkflowIdentity','WorkflowDependencies','WorkflowOutcome'];
const materialTypes=['WorkflowInput','CapturedInput','StepId','CapturedResult'];
const materialValues=['capture','captureResult','steps','compensations','result','descriptor'];

/** Exact source-derived incidence only. Original-call and custody evidence remain separate. */
export function createCrossGeneratorWorkflowSurface(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,boundary:CrossGeneratorBoundary,definition:string,operationDefinition:string){
 if(typeof definition!=='string'||sha256(definition)!==CROSS_GENERATOR_WORKFLOW_DEFINITION_SHA256)fail('definition drift');
 // This checks graph, plan and complete boundary registration/certificate identity.
 const operations=createCrossGeneratorOperationSurface(graph,plan,boundary,operationDefinition),definitions=workflowVerificationDefinitions();
 if(JSON.parse(getReconciledSource('configuration')).types.find((t:any)=>t.kind==='Workflow')?.role!=='application/workflows')fail('configured Workflow role');
 const rows=graph.nodes.filter(n=>n.kind==='Workflow').map(node=>{
  const binding=createWorkflowBinding(node,graph,plan,definitions.binding),{workflow,policy}=binding;
  const relative_path=plan.selection.module_root+'/features/'+node.feature_id+'/src/application/workflows/'+node.node_id+'.ts';
  const provider_path=relative_path.replace(/\.ts$/,'.provider.ts'),material_path=relative_path.replace(/\.ts$/,'.material.ts');
  same([binding.relative_path,binding.provider_path,binding.material_path],[relative_path,provider_path,material_path],'source paths');
  const forward=sorted(workflow.steps.map(s=>s.operation_ref)).map(selector=>operations.rows.find(r=>r.selector===selector)??fail('missing original forward Operation'));
  const modules=new Map<string,WorkflowSurfaceModule>();
  for(const row of forward)for(const m of row.modules){
   const value={...m,imports:m.imports.map(i=>({...i,namespace:false}))};
   if(modules.has(m.relative_path))same(modules.get(m.relative_path),value,'shared original Operation module');
   modules.set(m.relative_path,value);
  }
  const imp=(from:string,to:string,names:readonly string[],type_only=false,reexport=false,namespace=false,native_names?:readonly string[]):WorkflowSurfaceImport=>{
   const relative=path.posix.relative(path.posix.dirname(from),to).replace(/\.ts$/,'.js');
   return {specifier:relative.startsWith('.')?relative:'./'+relative,names:[...names].sort(),target_path:to,type_only,reexport,namespace,...(native_names?{native_names:[...native_names].sort()}:{})};
  };
  const own=(role:string,p:string,callable:string,value_exports:readonly string[],type_exports:readonly string[],imports:readonly WorkflowSurfaceImport[])=>{
   if(modules.has(p)||modules.size>=8192)fail('module capacity or duplicate');
   const captured=boundary.modules.find(m=>m.relative_path===p)??fail('missing source module');
   const artifact=plan.resolved.artifacts.find(a=>a.relative_path===p)??fail('missing source artifact');
   same(captured.qualified_selectors,[node.selector],'module owner');
   same(captured.exports,[...value_exports.map(name=>({name,kind:'value'})),...type_exports.map(name=>({name,kind:'type'}))].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:a.kind<b.kind?-1:1),'export kinds');
   const plain=(i:WorkflowSurfaceImport)=>{const {native_names,...rest}=i;return rest;};
   same(boundary.edges.filter(e=>e.importer_path===p).map(({specifier,names,target_path,type_only,reexport,namespace})=>({specifier,names,target_path,type_only,reexport,namespace})),imports.map(plain),'source imports');
   if(artifact.sha256!==captured.sha256||sha256(artifact.content)!==captured.sha256||Buffer.byteLength(artifact.content)!==artifact.size_bytes)fail('source bytes');
   modules.set(p,{selector:node.selector,role,relative_path:p,callable,value_exports:[...value_exports].sort(),type_exports:[...type_exports].sort(),imports,sha256:captured.sha256});
  };
  const members=['capture','captureResult','steps','result',...(workflow.compensations.length?['compensations']:[])];
  own('workflow-material',material_path,'',materialValues,materialTypes,[]);
  own('workflow-provider',provider_path,'execute',['execute','inspectOperationSettlement'],[...wrapperTypes,'RecoveryBinding','RecoveryBindings','OperationSettlement'],[
   {specifier:'node:crypto',names:['createHash'],target_path:null,type_only:false,reexport:false,namespace:false},
   imp(provider_path,material_path,[],false,false,true,members),imp(provider_path,material_path,['WorkflowInput'],true,true),
   imp(provider_path,material_path,['WorkflowInput'],true),
   ...forward.map(r=>imp(provider_path,r.relative_path,[r.callable]))
  ]);
  own('workflow-wrapper',relative_path,binding.callable,[binding.callable],wrapperTypes,[imp(relative_path,provider_path,['execute']),imp(relative_path,provider_path,wrapperTypes,true,true)]);
  const seen=new Set<string>(),pending=[relative_path];
  while(pending.length){const p=pending.pop()!;if(seen.has(p))continue;seen.add(p);const m=modules.get(p)??fail('missing derived module');m.imports.forEach(i=>{if(i.target_path)pending.push(i.target_path);});}
  same([...seen].sort(),[...modules.keys()].sort(),'unused derived dependency');
  same([...seen].sort(),binding.module_paths,'complete forward closure');
  const material_descriptor={schema_version:'domainspec.workflow-materialization-descriptor/v1-candidate',workflow_sha256:workflow.workflow_sha256,field_compilation_sha256:binding.fields?.compilation_sha256??null,
   contract_sha256:WORKFLOW_MATERIALIZATION_CONTRACT_SHA256,selector:node.selector,
   steps:workflow.steps.map(s=>({step_id:s.step_id,operation_ref:s.operation_ref,action_sha256:s.action_sha256})),
   compensations:workflow.compensations.map(c=>({compensation_id:c.compensation_id,for_step:c.for_step,operation_ref:c.operation_ref,action_sha256:c.action_sha256})),
   effect_contract:'pure-typed-materialization',invariant_execution:'not-performed',commit_evidence:'not-established',event_construction:'not-performed',authority_effect:'none'};
  return {selector:node.selector,kind:'Workflow' as const,state:'surface-ready' as const,relative_path,provider_path,material_path,callable:binding.callable,
   workflow_sha256:workflow.workflow_sha256,policy_sha256:policy.policy_sha256,descriptor:binding.descriptor,material_descriptor,
   modules:[...modules.values()].sort((a,b)=>a.relative_path<b.relative_path?-1:1),
   forward:forward.map(r=>({selector:r.selector,relative_path:r.relative_path,provider_path:r.provider_path,callable:r.callable,action_sha256:r.action_sha256,descriptor:r.descriptor})),
   steps:workflow.steps.map((s,index)=>({index,step_id:s.step_id,operation_ref:s.operation_ref,action_sha256:s.action_sha256,arguments:s.arguments,events:s.events})),
   compensations:workflow.compensations,compensation_execution:false as const,behavior_status:'not_evaluable' as const,native_status:'not_evaluable' as const};
 });
 const selectedPaths=new Set(rows.flatMap(r=>r.modules.map(m=>m.relative_path)));
 const body={schema_version:'domainspec.cross-generator-workflow-surface/v1-candidate' as const,definition_sha256:CROSS_GENERATOR_WORKFLOW_DEFINITION_SHA256,
  project_plan_sha256:plan.plan_sha256,source_manifest_sha256:graph.source_manifest.manifest_sha256,boundary_sha256:boundary.boundary_sha256,operation_surface_sha256:operations.surface_sha256,
  rows,coverage:boundary.edges.map(e=>({edge_sha256:e.edge_sha256,category:e.category,state:selectedPaths.has(e.importer_path)?'surface-bound':'uncovered',behavior_status:'not_evaluable' as const})),behavior_status:'not_evaluable' as const,authority_effect:'none' as const};
 const result=freeze({...body,surface_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorWorkflowSurface=ReturnType<typeof createCrossGeneratorWorkflowSurface>;
export function assertCrossGeneratorWorkflowSurface(v:unknown):asserts v is CrossGeneratorWorkflowSurface{
 if(!v||typeof v!=='object'||!registered.has(v))fail('registered Workflow surface required');
}
