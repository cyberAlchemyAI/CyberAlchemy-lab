import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {CrossGeneratorBoundary} from './reconciled-cross-generator-boundary.js';
import {createCrossGeneratorWorkflowSurface} from './reconciled-cross-generator-workflow-surface.js';
import {createWorkflowProtocolReference,CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256} from './reconciled-cross-generator-workflow-reference.js';
import {isWorkflowCasesCapacity,WorkflowCasesUnavailable} from './reconciled-workflow-cases.js';
import {createWorkflowProtocolCases,WORKFLOW_PROTOCOL_CASES_DEFINITION_SHA256} from './reconciled-workflow-protocol-cases.js';
import {workflowVerificationDefinitions} from './reconciled-workflow-controls.js';
import {expandOperationProtocolRecipe} from './reconciled-cross-generator-operation.js';
import type {WorkflowExecutionCase} from './reconciled-workflow-execution-reference.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import {assertPolicyData} from '../typed-backend/policy-rules.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';

const registered=new WeakSet<object>();
const fail=(s:string):never=>{throw new TypeError('CROSS_GENERATOR_WORKFLOW:'+s);};
const probeRow=(r:any,cases=r.cases)=>({selector:r.selector,adapter:r.adapter,relative_path:r.relative_path,provider_path:r.provider_path,material_path:r.material_path,callable:r.callable,
 modules:r.modules,forward:r.forward,steps:r.steps,recipes:r.recipes,batches:r.batches,cases:cases.map((c:any)=>({id:c.id,data:c.data}))});
export function expandWorkflowProtocolCase(recipes:readonly FactRecipe[],data:any):WorkflowExecutionCase{
 return {...data,input:expandOperationProtocolRecipe(recipes,data.input),
  steps:data.steps.map((s:any)=>({...s,reads:s.reads.map((r:any)=>({...r,value:expandOperationProtocolRecipe(recipes,r.value)}))}))};
}
/** Entire existing finite family, with identity protocol expectations added, never a selected prefix. */
export function createCrossGeneratorWorkflowControls(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,boundary:CrossGeneratorBoundary,definition:string,operationDefinition:string,protocolDefinition:string,casesDefinition:string){
 if(typeof protocolDefinition!=='string'||sha256(protocolDefinition)!==CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256)fail('protocol definition drift');
 if(typeof casesDefinition!=='string'||sha256(casesDefinition)!==WORKFLOW_PROTOCOL_CASES_DEFINITION_SHA256)fail('cases definition drift');
 const surface=createCrossGeneratorWorkflowSurface(graph,plan,boundary,definition,operationDefinition),d=workflowVerificationDefinitions();
 const rows=surface.rows.map(row=>{
  const direct_edges=boundary.edges.filter(e=>e.importer_path===row.provider_path&&e.category==='generated-runtime').map(e=>e.edge_sha256);
  try{
   const reference=createWorkflowProtocolReference(graph,plan,surface,row.selector,protocolDefinition),node=graph.nodes.find(n=>n.selector===row.selector)!;
   const source=createWorkflowProtocolCases(node,graph,plan,{execution:d.execution,binding:d.binding,values:d.values,outcomes:d.outcomes},casesDefinition);
   let calls=0,bytes=Buffer.byteLength(canonicalJson(source.recipes));
   const cases=source.cases.map(c=>{
    const data=JSON.parse(c.values[0]!),expected=reference.expected(c.id,expandWorkflowProtocolCase(source.recipes,data));
    const semantic_sha256=sha256(canonicalJson(expected.semantic));
    if(c.expected.kind!=='value'||semantic_sha256!==c.expected.value)fail('source semantic mismatch');
    calls+=expected.calls.length;const result={id:c.id,data,expected:{calls:expected.calls,semantic_sha256}};bytes+=Buffer.byteLength(canonicalJson(result));
    if(calls>65536||bytes>33554432)throw new WorkflowCasesUnavailable('Workflow protocol whole family capacity');
    return result;
   });
   if(!cases.length||cases.length>16384)throw new WorkflowCasesUnavailable('Workflow protocol case capacity');
   const batches:{index:number;start:number;count:number}[]=[];
   const ready={...row,state:'ready' as const,adapter:'workflow-protocol' as const,direct_edges,cases,batches,recipes:source.recipes,dimensions:source.coverage,search:source.search,
    identity:{workflow:true,operations:row.forward.map(o=>({selector:o.selector,original:true}))}};
   // Count-only chunks can fit the input but overflow the actual call trace.
   // Reserve the largest allowed framing; only boundaries, never reference
   // observations, enter native input. Case order and content stay unchanged.
   const framing={index:3,start:16383,count:4096},controls_sha256='0'.repeat(64);
   const inputBase=Buffer.byteLength(canonicalJson({controls_sha256,protocol_sha256:CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256,
    cases_definition_sha256:WORKFLOW_PROTOCOL_CASES_DEFINITION_SHA256,batch:framing,rows:[probeRow({...ready,batches:Array(4).fill(framing)},[])]}));
   const outputBase=Buffer.byteLength(canonicalJson({controls_sha256,selector:ready.selector,identity:ready.identity,
    descriptor:ready.descriptor,material_descriptor:ready.material_descriptor,batch:framing,cases:[]}));
   let start=0,count=0,inputBytes=inputBase,outputBytes=outputBase;
   const append=()=>{if(batches.length>=4)throw new WorkflowCasesUnavailable('Workflow protocol native batch count');batches.push({index:batches.length,start,count});start+=count;count=0;inputBytes=inputBase;outputBytes=outputBase;};
   for(const c of cases){
    const inputSize=Buffer.byteLength(canonicalJson({id:c.id,data:c.data}))+1,outputSize=Buffer.byteLength(canonicalJson({id:c.id,...c.expected}))+1;
    if(count&&(count===4096||inputBytes+inputSize>8388608||outputBytes+outputSize>8388608))append();
    if(inputBase+inputSize>8388608||outputBase+outputSize>8388608)throw new WorkflowCasesUnavailable('Workflow protocol single-case envelope bytes');
    count++;inputBytes+=inputSize;outputBytes+=outputSize;
   }
   if(count)append();
   if(Buffer.byteLength(canonicalJson(ready))>33554432)throw new WorkflowCasesUnavailable('Workflow protocol complete family bytes');
   for(const batch of batches){
    const selected=cases.slice(batch.start,batch.start+batch.count);
    const input={controls_sha256,protocol_sha256:CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256,cases_definition_sha256:WORKFLOW_PROTOCOL_CASES_DEFINITION_SHA256,batch,rows:[probeRow(ready,selected)]};
    const output={controls_sha256,selector:ready.selector,identity:ready.identity,descriptor:ready.descriptor,material_descriptor:ready.material_descriptor,batch,cases:selected.map(c=>({id:c.id,...c.expected}))};
    if(Buffer.byteLength(canonicalJson(input))>8388608||Buffer.byteLength(canonicalJson(output))>8388608)throw new WorkflowCasesUnavailable('Workflow protocol native batch envelope bytes');
   }
   return ready;
  }catch(error){if(isWorkflowCasesCapacity(error))return {...row,state:'not_evaluable' as const,reason:error.message,direct_edges};throw error;}
 });
 const selected=new Set(rows.flatMap(r=>r.state==='ready'?r.direct_edges:[]));
 const body={schema_version:'domainspec.cross-generator-workflow-controls/v1-candidate' as const,definition_sha256:surface.definition_sha256,protocol_sha256:CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256,cases_definition_sha256:WORKFLOW_PROTOCOL_CASES_DEFINITION_SHA256,
  project_plan_sha256:plan.plan_sha256,source_manifest_sha256:surface.source_manifest_sha256,boundary_sha256:boundary.boundary_sha256,surface_sha256:surface.surface_sha256,rows,
  coverage:boundary.edges.map(e=>({edge_sha256:e.edge_sha256,category:e.category,state:selected.has(e.edge_sha256)?'direct-protocol-selected':'not_evaluable'})),authority_effect:'none' as const};
 const result=freezeWorkflow({...body,controls_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type CrossGeneratorWorkflowControls=ReturnType<typeof createCrossGeneratorWorkflowControls>;
export function assertCrossGeneratorWorkflowControls(v:unknown):asserts v is CrossGeneratorWorkflowControls{
 if(!v||typeof v!=='object'||!registered.has(v))fail('registered controls required');
}
/** Native input contains source bindings and cases, never expected answers or observed authority. */
export function crossGeneratorWorkflowProbe(controls:CrossGeneratorWorkflowControls){
 assertCrossGeneratorWorkflowControls(controls);
 return {controls_sha256:controls.controls_sha256,protocol_sha256:controls.protocol_sha256,cases_definition_sha256:controls.cases_definition_sha256,rows:controls.rows.flatMap(r=>r.state!=='ready'?[]:[probeRow(r)])};
}
/** Bounded transport only: every batch is required and one original identity registry must span them. */
export function crossGeneratorWorkflowBatchProbes(controls:CrossGeneratorWorkflowControls){
 assertCrossGeneratorWorkflowControls(controls);
 return controls.rows.flatMap(r=>r.state!=='ready'?[]:r.batches.map(batch=>{
  const payload={controls_sha256:controls.controls_sha256,protocol_sha256:controls.protocol_sha256,cases_definition_sha256:controls.cases_definition_sha256,batch,
   rows:[probeRow(r,r.cases.slice(batch.start,batch.start+batch.count))]};
  if(Buffer.byteLength(canonicalJson(payload))>8388608)fail('native batch capacity');
  return payload;
 }));
}
export function checkCrossGeneratorWorkflowObservations(controls:CrossGeneratorWorkflowControls,observations:unknown){
 assertCrossGeneratorWorkflowControls(controls);assertPolicyData(observations);
 const rows=controls.rows.filter(r=>r.state==='ready');
 if(!rows.length)fail('no ready Workflow families');
 const expected={controls_sha256:controls.controls_sha256,rows:rows.map(r=>({selector:r.selector,identity:r.identity,descriptor:r.descriptor,material_descriptor:r.material_descriptor,batches:r.batches,cases:r.cases.map(c=>({id:c.id,...c.expected}))}))};
 if(canonicalJson(observations)!==canonicalJson(expected))fail('observation mismatch');
 return {tested_workflow_count:rows.length,tested_case_count:rows.reduce((n,r)=>n+r.cases.length,0),tested_call_count:rows.reduce((n,r)=>n+r.cases.reduce((n,c)=>n+c.expected.calls.length,0),0),
  remaining:controls.rows.filter(r=>r.state!=='ready').map(r=>({selector:r.selector,reason:r.reason})),
  uncovered_runtime_edge_count:controls.coverage.filter(e=>e.category==='generated-runtime'&&e.state==='not_evaluable').length,
  public_cross_generator_behavior:'not_evaluable' as const,retained_execution:'not_evaluable' as const,authority_effect:'none' as const};
}
