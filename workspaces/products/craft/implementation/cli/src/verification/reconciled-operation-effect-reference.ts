import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson} from '../input/source-manifest.js';
import {assertReconciledProjectPlan,type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {assertCheckedOperationAction,type CheckedOperationAction} from '../typed-operation/action-bindings.js';
import type {TypedType} from '../typed-operation/contracts.js';
import {createStructuralFacts,type FactRecipe} from './reconciled-rule-facts.js';
import {operationReferenceValue,OperationReferenceUnsupported,type OperationFixtureMode} from './reconciled-operation-reference.js';
import {captureOperationRecipe,createOperationValueReference,operationReferenceEvent,operationReferenceFields} from './reconciled-operation-values.js';
import type {FactoryBinding} from '../generation/configured-factories.js';
import {eventReferenceIdentity} from '../generation/event-reference-identity.js';

export interface OperationEffectFixture {
 readonly reads:readonly Readonly<{slot:string;value:FactRecipe;throws?:boolean}>[];
 readonly clocks:readonly Readonly<{slot:string;value:string|null|number;mode?:'return'|'throw'|'missing'}>[];
}
/** Independent expectation only. All execution occurs in a separate explicit fixture.
 * Source graph, checked action and selected factory providers must agree first.
 */
export function createEffectfulOperationReference(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,action:CheckedOperationAction){
 assertCompiledProjectSnapshot(graph);assertReconciledProjectPlan(plan);assertCheckedOperationAction(action);
 const certificate=createCompiledProjectCertificate(graph),b=action.bindings;
 if(action.certificate.graph_sha256!==certificate.graph_sha256||plan.resolved.certificate.graph_sha256!==certificate.graph_sha256||
    canonicalJson(plan.selection.operations.find(v=>v.selector===b.selector))!==canonicalJson(b))throw new TypeError('OPERATION_REFERENCE_BINDING');
 const selected=plan.resolved.requests.filter(r=>r.kind==='operations').flatMap(r=>(r.selection as {actions:readonly CheckedOperationAction[]}).actions).filter(a=>a.bindings.selector===b.selector);
 if(selected.length!==1||selected[0]!.action_sha256!==action.action_sha256)throw new TypeError('OPERATION_REFERENCE_ACTION');
 return createBoundEffectfulOperationReference(graph,action,plan.selection.factories);
}
/** Source oracle shared by native adapters after their own registered-plan checks. */
export function createBoundEffectfulOperationReference(graph:CompiledProjectGraph,action:CheckedOperationAction,bindings:readonly FactoryBinding[]){
 assertCompiledProjectSnapshot(graph);assertCheckedOperationAction(action);
 if(action.certificate.graph_sha256!==createCompiledProjectCertificate(graph).graph_sha256)throw new TypeError('OPERATION_REFERENCE_BINDING');
 const b=action.bindings,values=createOperationValueReference(graph),factories=new Map(bindings.map(f=>[f.selector,f]));
 const eventReferenceScalar=(selector:string)=>eventReferenceIdentity(graph,selector,reason=>{throw new OperationReferenceUnsupported(reason);}).scalar;
 const roots=[...b.guards.map(g=>g.selector),...bindings.flatMap(f=>f.base_validators.map(v=>v.rule))];
 const facts=createStructuralFacts(graph,roots,[b.result.value,...b.guards.flatMap(g=>g.arguments.map(a=>a.value))]);
 const ensure=(type:TypedType,v:any,depth=0):void=>{
  if(depth>64)throw new OperationReferenceUnsupported('OPERATION_REFERENCE_OWNED_DEPTH');
  if(type.kind==='scalar')return;
  if(type.kind==='optional'){if(v!==null)ensure(type.element,v,depth+1);return;}
  if(type.kind==='list'||type.kind==='set'){v.forEach((x:any)=>ensure(type.element,x,depth+1));return;}
  if(type.kind==='sum'){const variant=type.variants.find(x=>x.name===v.variant)!;if(variant.payload)ensure(variant.payload,v.payload,depth+1);return;}
  const d=values.get(type);
  if(d.kind==='Enum'){ensure({kind:'sum',variants:d.variants},v,depth+1);return;}
  for(const p of d.properties)ensure(p.type as TypedType,v[p.name],depth+1);
  const factory=factories.get(type.selector);
  if(!factory?.base_validators.length)throw new OperationReferenceUnsupported('OPERATION_REFERENCE_FACTORY:'+type.selector);
  for(const validator of factory.base_validators){
   const rule=facts.reference.rules.get(validator.rule);if(!rule)throw new OperationReferenceUnsupported('OPERATION_REFERENCE_FACTORY_RULE:'+validator.rule);
   const arguments_=new Map(validator.arguments.map(a=>{
    let value=v;for(const segment of a.path??[a.field!])value=value[segment];
    return [a.parameter,{type:rule.parameters.find(p=>p.name===a.parameter)!.type,value}] as const;
   }));
   if(!facts.reference.evaluate(validator.rule,arguments_))throw new TypeError('OPERATION_REFERENCE_OWNED');
  }
 };
 const expected=(recipe:FactRecipe,fixture:OperationEffectFixture,mode:OperationFixtureMode='committed')=>{
  const trace:string[]=[],batches:unknown[]=[],read_requests:unknown[]=[],clock_calls:string[]=[];
  let stage='input',scope=new Map<string,{type:TypedType;value:any}>(),captured:any;
  const finish=(outcome:any)=>({outcome:operationReferenceValue(outcome),trace,batches,read_calls:read_requests.length,
   settled_before_begin:false,settled_before_commit:false,settled_before_rollback:false,getter_reads:0,input_changed:false,
   read_requests,clock_calls,settled_before_read:false,read_changed:false});
  const failure=(status:string,code:string,cleanupFailed=false)=>({status,stage,code,continuation:action.failure_continuation,cleanupFailed});
  const abort=(status:string,code:string)=>{
   trace.push('rollback',mode==='rollback-throw'?'rollback-rejected':'rollback-resolved');return finish(failure(status,code,mode==='rollback-throw'));
  };
  const rethrowUnsupported=(e:unknown)=>{if(e instanceof OperationReferenceUnsupported)throw e;};
  try{
   captured=captureOperationRecipe(recipe);
   operationReferenceFields(captured,[...b.inputs.map(p=>p.name),...b.events.map(e=>e.parameter)]);
   scope=new Map(b.inputs.map(p=>[p.name,{type:p.type,value:values.normalize(p.type,captured[p.name])}]));
  }catch(e){rethrowUnsupported(e);return finish(failure('failed','OPERATION_INPUT'));}
  stage='begin';
  const generated=action.events.filter(e=>e.contract.occurred_at_policy==='generated');
  if(generated.some(e=>{const clock=fixture.clocks.find(c=>c.slot===e.slot);return !clock||clock.mode==='missing';}))return finish(failure('failed','BEGIN_FAILED'));
  trace.push('begin');if(mode==='begin-throw'){trace.push('begin-rejected');return finish(failure('failed','BEGIN_FAILED'));}trace.push('begin-resolved');
  try{
   stage='read';
   for(const read of action.reads){
    const key=values.normalize(read.identity.type,values.value(read.key,scope).value),row=fixture.reads.find(r=>r.slot===read.slot);
    read_requests.push(operationReferenceValue({slot:read.slot,target:read.target,key}));trace.push('read:'+read.slot);
    trace.push('read:'+read.slot+(row?.throws?'-rejected':'-resolved'));
    if(row?.throws)throw new TypeError('OPERATION_REFERENCE_READ');
    if(!row)throw new OperationReferenceUnsupported('OPERATION_REFERENCE_READ_FIXTURE:'+read.slot);
    const raw=captureOperationRecipe(row.value,'read');if(raw===null)return abort('failed','READ_NOT_FOUND');
    const value=values.normalize({kind:'named',selector:read.target},raw);
    if(values.key(read.identity.type,key)!==values.key(read.identity.type,value[read.identity.name]))return abort('failed','READ_IDENTITY_MISMATCH');
    scope.set(read.parameter,{type:{kind:'named',selector:read.target},value});
   }
   stage='guard';
   for(const guard of b.guards)if(!facts.reference.guard(guard,scope))return abort('rejected','RULE_REJECTED:'+guard.selector);
   stage='write-validation';
   const writes=action.writes.map(w=>{
    const type:TypedType={kind:'named',selector:w.target},value=values.normalize(type,values.value(w.value,scope).value);ensure(type,value);
    return {slot:w.slot,target:w.target,mode:w.mode,value};
   });
   stage='event';
   const events=action.events.map(e=>({slot:e.slot,target:e.target,value:operationReferenceEvent(e.contract,captured[e.parameter],()=>{
    clock_calls.push(e.slot);const c=fixture.clocks.find(c=>c.slot===e.slot)!;
    if(c.mode==='throw')throw new TypeError('OPERATION_REFERENCE_CLOCK');return c.value;
   },eventReferenceScalar)}));
   stage='result';const result=values.normalize(b.result.type,values.value(b.result.value,scope).value);ensure(b.result.type,result);
   stage='commit';trace.push('commit');batches.push(operationReferenceValue({writes,events}));
   trace.push(mode==='commit-throw'?'commit-rejected':'commit-resolved');
   if(mode==='committed'||mode==='rollback-throw')return finish({status:'committed',value:result});
   if(mode==='rejected')return finish(failure('rejected','COMMIT_REJECTED'));
   if(mode==='indeterminate')return finish(failure('indeterminate','COMMIT_INDETERMINATE'));
   return finish(failure('indeterminate',['receipt-empty','receipt-unknown'].includes(mode)?'INVALID_COMMIT_RECEIPT':'COMMIT_UNCERTAIN'));
  }catch(e){rethrowUnsupported(e);return abort('failed','OPERATION_FAILED');}
 };
 const checkOwned=(type:TypedType,recipe:FactRecipe)=>{const value=values.normalize(type,captureOperationRecipe(recipe));ensure(type,value);return value;};
 return {action,facts,values,expected,checkOwned,eventReferenceScalar};
}
