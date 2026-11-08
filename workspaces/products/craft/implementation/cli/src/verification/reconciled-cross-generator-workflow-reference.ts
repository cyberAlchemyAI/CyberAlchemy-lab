import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {createWorkflowExecutionReference,WorkflowExecutionCapacity,type WorkflowExecutionCase} from './reconciled-workflow-execution-reference.js';
import {createWorkflowValueReference} from './reconciled-workflow-value-reference.js';
import {createWorkflowOutcomeReference,inspectWorkflowSettlementReference} from './reconciled-workflow-outcome-reference.js';
import {createEffectfulOperationReference} from './reconciled-operation-effect-reference.js';
import {captureOperationRecipe} from './reconciled-operation-values.js';
import {operationValueRecipe} from './reconciled-operation-cases.js';
import {operationReferenceValue,OperationReferenceUnsupported} from './reconciled-operation-reference.js';
import {workflowVerificationDefinitions} from './reconciled-workflow-controls.js';
import {assertCrossGeneratorWorkflowSurface,type CrossGeneratorWorkflowSurface} from './reconciled-cross-generator-workflow-surface.js';

export const CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256='9f43f5103f16fa48d5b23709fefb99f13918ca2ec392159b56b6d3527b5c046c';
export interface WorkflowProtocolCall {
 readonly provider:string;readonly role:'material'|'operation';readonly method:string;readonly occurrence:string|null;
 readonly arity:number;readonly arguments:unknown;readonly awaited:boolean;
 readonly result:Readonly<{kind:'error';name:'TypeError'}>|Readonly<{kind:'value';value:unknown;data_sha256:string;deep_frozen:true}>;
}
const fail=(s:string):never=>{throw new TypeError('WORKFLOW_PROTOCOL:'+s);};
function expectedValue(tagged:any):any{
 const [tag,value]=tagged;
 if(tag==='null')return null;
 if(tag==='bigint')return BigInt(value);
 if(['string','boolean','number'].includes(tag))return value;
 if(tag==='array')return value.map(expectedValue);
 if(tag==='record')return Object.fromEntries(value.map(([k,v]:[string,any])=>[k,expectedValue(v)]));
 return fail('independent value tag');
}

/** Independent source interpreter. Generated text and native outputs are never expected-answer inputs. */
export function createWorkflowProtocolReference(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,surface:CrossGeneratorWorkflowSurface,selector:string,definition:string){
 assertCrossGeneratorWorkflowSurface(surface);
 if(typeof definition!=='string'||sha256(definition)!==CROSS_GENERATOR_WORKFLOW_PROTOCOL_SHA256)fail('definition drift');
 if(surface.project_plan_sha256!==plan.plan_sha256)fail('foreign surface');
 const row=surface.rows.find(r=>r.selector===selector)??fail('missing Workflow');
 const node=graph.nodes.find(n=>n.selector===selector)??fail('missing source');
 const d=workflowVerificationDefinitions(),oracle=createWorkflowExecutionReference(node,graph,plan,{execution:d.execution,binding:d.binding,values:d.values,outcomes:d.outcomes});
 const {binding}=oracle,w=binding.workflow;
 if(w.workflow_sha256!==row.workflow_sha256||binding.policy.policy_sha256!==row.policy_sha256)fail('foreign Workflow binding');
 const values=createWorkflowValueReference(graph,w,d.values),outcomes=createWorkflowOutcomeReference(binding.policy,d.outcomes);
 const operations=new Map(binding.operations.map(o=>[o.action.bindings.selector,createEffectfulOperationReference(graph,plan,o.action)]));
 function expected(id:string,raw:unknown){
  if(typeof id!=='string'||!/^[a-z][a-z0-9-]{0,255}$/.test(id))fail('case identity');
  const c=oracle.captureCase(raw),semantic=oracle.expected(c),calls:WorkflowProtocolCall[]=[],identities=new WeakMap<object,string>();
  const bind=(value:any,token:string)=>{if(value!==null&&(typeof value==='object'||typeof value==='function')&&!identities.has(value))identities.set(value,token);return value;};
  const wire=(v:any,depth=0):any=>{
   if(depth>64)throw new WorkflowExecutionCapacity('Workflow protocol value depth');
   if(v!==null&&(typeof v==='object'||typeof v==='function')){const token=identities.get(v);if(token!==undefined)return ['identity',token];}
   if(v===null)return ['null'];
   if(typeof v==='bigint')return ['bigint',String(v)];
   if(typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return [typeof v,v];
   if(Array.isArray(v))return ['array',v.map(x=>wire(x,depth+1))];
   if(!v||typeof v!=='object')throw new OperationReferenceUnsupported('Workflow protocol active value');
   return ['record',Object.keys(v).sort().map(k=>[k,wire(v[k],depth+1)])];
  };
  const finish=()=>{
   const result={calls,semantic};
   if(Buffer.byteLength(canonicalJson(result))>8388608)throw new WorkflowExecutionCapacity('Workflow protocol case bytes');
   return freezeWorkflow(result);
  };
  const call=(provider:string,role:'material'|'operation',method:string,occurrence:string|null,args:any[],run:()=>any)=>{
   if(calls.length>=65536)throw new WorkflowExecutionCapacity('Workflow protocol call capacity');
   const index=calls.length,arguments_=method==='capture'?['array',[['source-input',id]]]:wire(args),common={provider,role,method,occurrence,arity:args.length,arguments:arguments_,awaited:role==='operation'};
   // Reserve the call position before evaluation; failures retain their occurrence.
   const record:any={...common,result:null};calls.push(record);
   try{
    const value=run();
    bind(value,'return:'+id+':'+index);
    if(role==='operation'&&value?.status==='committed')bind(value.value,'operation-value:'+id+':'+index);
    record.result={kind:'value',value:wire(value),data_sha256:sha256(canonicalJson(operationReferenceValue(value))),deep_frozen:true};
    return value;
   }catch(error){
    if(!(error instanceof TypeError))throw error;
    record.result={kind:'error',name:'TypeError'};throw error;
   }
  };
  // Identity validation precedes even material.capture, exactly as the semantic contract.
  if(Object.values(c.identity).some(v=>v.length>256||/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(v)?.[0]!==v))return finish();
  // Malformed recipes are rejected symbolically by the input oracle. The original
  // material call still occurs, so retain its source-input marker and TypeError.
  let source:any,invalidSource=false;
  try{source=captureOperationRecipe(c.input);}catch(error){if(!(error instanceof TypeError))throw error;invalidSource=true;}
  let input:ReturnType<typeof values.capture>;
  try{input=call(selector,'material','capture',null,[source],()=>{if(invalidSource)throw new TypeError('invalid symbolic input');return values.capture(source);});}
  catch(error){if(!(error instanceof TypeError))throw error;return finish();}
  const results:ReturnType<typeof values.captureResult>[]=[],events:any[]=[],dependencies=new Map(row.forward.map(o=>[o.selector,bind({},'dependency:'+id+':'+o.selector)]));
  const stopped=(local_error:string|null=null)=>{
   const evaluation=outcomes.evaluate({...c.identity,events,local_error}),intent=evaluation.recovery?.recovery_intent;
   if(intent)for(const entry of intent.plan){
    try{call(selector,'material','compensation.arguments',entry.compensation_id,[input,results],()=>values.compensation(input,entry.compensation_id,results));}
    catch(error){if(!(error instanceof TypeError))throw error;break;}
   }
   return finish();
  };
  for(const [index,step] of w.steps.entries()){
   let args:any;
   try{args=call(selector,'material','step.arguments',step.step_id,[input,results],()=>values.forward(input,step.step_id,results));}
   catch(error){if(!(error instanceof TypeError))throw error;events.push({step_id:step.step_id,kind:'not-started'});return stopped();}
   const operation=operations.get(step.operation_ref)??fail('missing forward Operation');
   const result=call(step.operation_ref,'operation','execute',step.step_id,[args,dependencies.get(step.operation_ref)],()=>expectedValue(operation.expected(operationValueRecipe(args),c.steps[index]!,c.steps[index]!.mode).outcome));
   events.push({step_id:step.step_id,kind:'returned',outcome:result});
   if(inspectWorkflowSettlementReference(result,step.failure_continuation).commit_status!=='committed')return stopped();
   try{results.push(call(selector,'material','captureResult',step.step_id,[input,step.step_id,result.value],()=>values.captureResult(input,step.step_id,result.value)));}
   catch(error){if(!(error instanceof TypeError))throw error;return stopped('committed-result-invalid');}
  }
  try{call(selector,'material','result',null,[input,results],()=>values.result(input,results));}
  catch(error){if(!(error instanceof TypeError))throw error;return stopped('result-materialization-failed');}
  return finish();
 }
 return Object.freeze({binding,captureCase:oracle.captureCase,expected});
}
