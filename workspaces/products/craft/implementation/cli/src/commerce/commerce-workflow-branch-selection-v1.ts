/** Interprets branches of one checked, original Workflow as inert data.
 * An external call result has no custody here: even a selected action cannot
 * authorize an Entry invocation, observation commit, journal write or dispatch.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {isDeepStrictEqual,types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {createCommerceWorkflowExpressionOwnerV1,type CommerceWorkflowExpressionOwnerV1,type CommerceWorkflowExpressionHandleV1,type CommerceWorkflowExpressionProducersV1} from './commerce-workflow-expression-v1.js';
import {assertCommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import {assertCommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import type {ValueSchemaV1,ValueTypeV1,WorkflowActionV1,WorkflowBranchV1,WorkflowStepV1} from './commerce-data-v1.js';

export class CommerceWorkflowBranchSelectionErrorV1 extends Error {
 constructor(readonly code:string){super(code);this.name='CommerceWorkflowBranchSelectionErrorV1';}
}
const bad=(code:string):never=>{throw new CommerceWorkflowBranchSelectionErrorV1(code);};
const plain=(value:unknown):value is Record<string,unknown>=>Boolean(value&&typeof value==='object'&&!Array.isArray(value)&&
 !host.isProxy(value)&&(Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null));
const field=(value:unknown,name:string):unknown=>{
 if(!plain(value))return undefined;
 const descriptor=Object.getOwnPropertyDescriptor(value,name);
 return descriptor?.enumerable&&Object.hasOwn(descriptor,'value')?descriptor.value:undefined;
};
const names=(value:unknown):readonly string[]|null=>{
 if(!plain(value))return null;
 const keys=Reflect.ownKeys(value);
 if(keys.some(key=>typeof key!=='string'||!Object.getOwnPropertyDescriptor(value,key)?.enumerable||
  !Object.hasOwn(Object.getOwnPropertyDescriptor(value,key)!,'value')))return null;
 return keys as string[];
};
const sameNames=(value:unknown,expected:readonly string[])=>{
 const actual=names(value);return actual!==null&&actual.length===expected.length&&expected.every(name=>actual.includes(name));
};
const unicode=(value:string)=>Buffer.from(value,'utf8').toString('utf8')===value;
const variant=(value:unknown):string|null=>typeof value==='string'?value:typeof field(value,'kind')==='string'?field(value,'kind') as string:null;

/** Generated Operation results use the public kind-plus-fields ABI, while
 * checked Workflow expressions use the private tag/fields representation.
 * The bridge admits only exact source-declared native shapes. */
function nativeToFlow(value:unknown,type:ValueTypeV1,schema:ValueSchemaV1,depth=0):unknown {
 if(depth>64)bad('InvalidResult');
 switch(type.kind){
  case 'record':{
   const definition=schema.records.find(row=>row.name===type.name);
   if(!definition||!sameNames(value,Object.keys(definition.fields)))bad('InvalidResult');
   const members=definition!.fields;
   return Object.freeze(Object.fromEntries(Object.entries(members).map(([name,member])=>
    [name,nativeToFlow(field(value,name),member,schema,depth+1)])));
  }
  case 'enum':case 'variant':{
   const enumName=type.kind==='variant'?(type as Extract<ValueTypeV1,{kind:'variant'}>).enum_name:type.name;
   const definition=schema.enums.find(row=>row.name===enumName);
   const tag=variant(value),choice=definition?.variants.find(row=>row.name===tag);
   if(!choice||type.kind==='variant'&&tag!==type.variant)bad('InvalidResult');
   if(definition!.variants.every(row=>!Object.keys(row.fields).length)){
    if(typeof value!=='string')bad('InvalidResult');return value;
   }
   const members=choice!.fields;
   if(!sameNames(value,['kind',...Object.keys(members)]))bad('InvalidResult');
   const fields=Object.freeze(Object.fromEntries(Object.entries(members).map(([name,member])=>
    [name,nativeToFlow(field(value,name),member,schema,depth+1)])));
   return Object.freeze({kind:tag,fields});
  }
  case 'list':{
   if(!Array.isArray(value)||host.isProxy(value)||Object.getPrototypeOf(value)!==Array.prototype||
      value.length<type.min_items||value.length>type.max_items||Reflect.ownKeys(value).length!==value.length+1)bad('InvalidResult');
   return Object.freeze((value as readonly unknown[]).map((item:unknown,index:number)=>{
    const descriptor=Object.getOwnPropertyDescriptor(value,String(index));
    if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InvalidResult');
    return nativeToFlow(item,type.element,schema,depth+1);
   }));
  }
  case 'optional':{
   if(sameNames(value,['kind'])&&field(value,'kind')==='none')return Object.freeze({kind:'none'});
   if(!sameNames(value,['kind','value'])||field(value,'kind')!=='some')bad('InvalidResult');
   return Object.freeze({kind:'some',value:nativeToFlow(field(value,'value'),type.element,schema,depth+1)});
  }
  default:return value;
 }
}

function flowToNative(value:unknown,type:ValueTypeV1,schema:ValueSchemaV1,depth=0):unknown {
 if(depth>64)bad('InvalidObservation');
 switch(type.kind){
  case 'record':{
   const definition=schema.records.find(row=>row.name===type.name);
   if(!definition)bad('InvalidObservation');
   const members=definition!.fields;
   return Object.freeze(Object.fromEntries(Object.entries(members).map(([name,member])=>
    [name,flowToNative(field(value,name),member,schema,depth+1)])));
  }
  case 'enum':case 'variant':{
   const enumName=type.kind==='variant'?(type as Extract<ValueTypeV1,{kind:'variant'}>).enum_name:type.name;
   const definition=schema.enums.find(row=>row.name===enumName);
   const tag=variant(value),choice=definition?.variants.find(row=>row.name===tag);
   if(!choice)bad('InvalidObservation');
   if(definition!.variants.every(row=>!Object.keys(row.fields).length))return value;
   const fields=field(value,'fields');
   return Object.freeze(Object.fromEntries([['kind',tag],...Object.entries(choice!.fields).map(([name,member])=>
    [name,flowToNative(field(fields,name),member,schema,depth+1)])]));
  }
  case 'list':return Object.freeze((value as readonly unknown[]).map(item=>flowToNative(item,type.element,schema,depth+1)));
  case 'optional':return field(value,'kind')==='none'?Object.freeze({kind:'none'}):
   Object.freeze({kind:'some',value:flowToNative(field(value,'value'),type.element,schema,depth+1)});
  default:return value;
 }
}

/** Shape validation is intentionally limited to checked value declarations.
 * A future original result owner must also attest the producing call/entry. */
function typed(value:unknown,type:ValueTypeV1,schema:ValueSchemaV1,depth=0):boolean {
 if(depth>64)return false;
 switch(type.kind){
  case 'scalar':return type.name==='Bool'?typeof value==='boolean':typeof value==='bigint'&&value>=0n&&value<=18446744073709551615n;
  case 'string':return typeof value==='string'&&unicode(value)&&Buffer.byteLength(value,'utf8')<=type.max_bytes&&[...value].length<=type.max_scalars;
  case 'literal':return value===type.value;
  case 'refinement':{
   const definition=schema.refinements.find(row=>row.name===type.name);
   return Boolean(definition&&typeof value==='string'&&unicode(value)&&typed(value,definition!.carrier,schema,depth+1)&&
    Buffer.byteLength(value,'utf8')>=definition!.min_utf8_bytes&&Buffer.byteLength(value,'utf8')<=definition!.max_utf8_bytes&&
    [...value].length>=definition!.min_unicode_scalars&&[...value].length<=definition!.max_unicode_scalars&&
    (!definition!.pattern||new RegExp(definition!.pattern,'u').test(value)));
  }
  case 'record':{
   const definition=schema.records.find(row=>row.name===type.name);
   return Boolean(definition&&sameNames(value,Object.keys(definition!.fields))&&
    Object.entries(definition!.fields).every(([name,t])=>typed(field(value,name),t,schema,depth+1)));
  }
  case 'enum':case 'variant':{
   const definition=schema.enums.find(row=>row.name===(type.kind==='enum'?type.name:(type as Extract<ValueTypeV1,{kind:'variant'}>).enum_name));
   const tag=variant(value),choice=definition?.variants.find(row=>row.name===tag);
   if(!choice||type.kind==='variant'&&tag!==type.variant)return false;
   if(definition!.variants.every(row=>Object.keys(row.fields).length===0))return typeof value==='string';
   const fields=field(value,'fields');
   return sameNames(value,['kind','fields'])&&sameNames(fields,Object.keys(choice.fields))&&
    Object.entries(choice.fields).every(([name,t])=>typed(field(fields,name),t,schema,depth+1));
  }
  case 'list':{
   if(!Array.isArray(value)||host.isProxy(value)||Object.getPrototypeOf(value)!==Array.prototype||
      value.length<type.min_items||value.length>type.max_items||Reflect.ownKeys(value).length!==value.length+1)return false;
   return value.every((item,index)=>Object.getOwnPropertyDescriptor(value,String(index))?.enumerable&&
    Object.hasOwn(Object.getOwnPropertyDescriptor(value,String(index))!,'value')&&typed(item,type.element,schema,depth+1));
  }
  case 'optional':return sameNames(value,['kind'])&&field(value,'kind')==='none'||
   sameNames(value,['kind','value'])&&field(value,'kind')==='some'&&typed(field(value,'value'),type.element,schema,depth+1);
  case 'outcome':return false;
 }
}

type Channel=WorkflowBranchV1['channel'];
export type CommerceWorkflowRemoteResultV1=
 {readonly channel:'result';readonly value:unknown}|
 {readonly channel:Exclude<Channel,'variant'>;readonly value?:never};
export interface CommerceWorkflowBranchDecisionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly step_name:string;
 readonly outcome:'selected'|'suspend-same-persisted-state';readonly reason:'matched'|'unhandled-result'|'invalid-result'|'failed-require'|'evaluation-failed'|'stale-context';
 readonly branch_index:number|null;readonly channel:Channel|null;readonly variant:string|null;
 readonly action:WorkflowActionV1|null;readonly observation:unknown|null;
 readonly retaining:WorkflowBranchV1['retaining'];readonly restriction:WorkflowBranchV1['restriction'];
 readonly original_journal:'retain';readonly qualification:'checked-source-branch-data-only;original-result-and-observation-commit-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowBranchPlanV1 {
 readonly step_name:string;readonly result:ValueTypeV1;readonly branches:readonly {readonly index:number;readonly channel:Channel;
  readonly variant:string|null;readonly guard_path:string|null;readonly require_path:string|null;readonly observe_path:string|null;
  readonly action:WorkflowActionV1}[];readonly authority_effect:'none';
}
export interface CommerceWorkflowBranchSelectionOwnerV1 {
 plans():readonly CommerceWorkflowBranchPlanV1[];
 /** Diagnostic only: caller context and result have no original producer custody. */
 interpret(stepName:string,result:CommerceWorkflowRemoteResultV1,context:Readonly<Record<string,unknown>>,
  producers?:CommerceWorkflowExpressionProducersV1):CommerceWorkflowBranchDecisionV1;
 /** Data-only evaluation against the snapshot captured before a same-service
  * commit. The caller must separately own the original result and commit. */
 selectCaptured(stepName:string,result:CommerceWorkflowRemoteResultV1,snapshotValue:unknown,
  producers?:CommerceWorkflowExpressionProducersV1):CommerceWorkflowBranchDecisionV1;
 /** Uses original current snapshot and step identity; result custody remains absent. */
 selectCurrent(identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
  result:CommerceWorkflowRemoteResultV1,producers?:CommerceWorkflowExpressionProducersV1):CommerceWorkflowBranchDecisionV1;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowBranchSelectionOwnerV1(owner:CommerceWorkflowBranchSelectionOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();
}
type Bound={readonly branch:WorkflowBranchV1;readonly index:number;readonly guard:CommerceWorkflowExpressionHandleV1|null;
 readonly require:CommerceWorkflowExpressionHandleV1|null;readonly observe:CommerceWorkflowExpressionHandleV1|null};

export function createCommerceWorkflowBranchSelectionOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
):CommerceWorkflowBranchSelectionOwnerV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);assertCommerceComputationDomainOwner(domain);
 const source=binding.inspect(),semanticView=semantics.inspect(semantic),domainView=domain.inspect(baseline),
  workflow=semanticView.workflows.find(row=>row.workflow.module+'.'+row.workflow.name===source.workflow.name);
 if(!workflow||semanticView.source_capture_sha256!==source.source_capture_sha256||
   domainView.source_capture_sha256!==source.source_capture_sha256||workflow.steps.length!==source.workflow.steps.length)
  bad('ForeignOwner');
 const expression=createCommerceWorkflowExpressionOwnerV1(binding,semantics,semantic,domain,baseline);
 try{
  const paths=new Set(expression.paths()),bound=new Map<string,{step:Extract<WorkflowStepV1,{kind:'remote'}>;branches:readonly Bound[]}>();
  for(let i=0;i<workflow!.steps.length;i++){
   const original=source.workflow.steps[i]!,step=workflow!.steps[i]!;
   if(original.name!==step.name||original.kind!==step.kind)bad('InvalidContract');
   if(step.kind!=='remote'||original.kind!=='remote')continue;
   if(original.call.entry!==step.call.entry||original.call.target!==step.call.target||
    original.call.role!==step.call.role||original.call.binding!==step.call.binding||
    original.branches.length!==step.branches.length)bad('InvalidContract');
   const branches=step.branches.map((branch,j):Bound=>{
    const core=original.branches[j]!;
    if(core.channel!==branch.channel||core.variant!==branch.variant||core.binding?.name!==branch.binding?.name||
     !isDeepStrictEqual(core.action,branch.action)||Boolean(core.guard)!==Boolean(branch.guard)||
     Boolean(core.require)!==Boolean(branch.require)||Boolean(core.observe)!==Boolean(branch.observe))bad('InvalidContract');
    const bind=(name:'guard'|'require'|'observe')=>{
     if(!branch[name])return null;
     const p=`$.steps[${i}].branches[${j}].${name}`;
     if(!paths.has(p))bad('InvalidContract');
     return expression.bind(p);
    };
    return {branch,index:j,guard:bind('guard'),require:bind('require'),observe:bind('observe')};
   });
   bound.set(step.name,{step,branches});
  }
  let disposed=false;
  const current=()=>{if(disposed)bad('DisposedOwner');expression.assertCurrent();};
  const suspension=(step:string,reason:CommerceWorkflowBranchDecisionV1['reason']):CommerceWorkflowBranchDecisionV1=>
   coreFreeze({workflow:source.workflow.name,source_capture_sha256:source.source_capture_sha256,step_name:step,
    outcome:'suspend-same-persisted-state' as const,reason,branch_index:null,channel:null,variant:null,action:null,observation:null,
    retaining:null,restriction:null,original_journal:'retain' as const,
    qualification:'checked-source-branch-data-only;original-result-and-observation-commit-required' as const,authority_effect:'none' as const});
  const interpret=(stepName:string,result:CommerceWorkflowRemoteResultV1,context:Readonly<Record<string,unknown>>,
   producers:CommerceWorkflowExpressionProducersV1={}):CommerceWorkflowBranchDecisionV1=>{
   current();const row=bound.get(stepName);
   if(!row)bad('UnknownReference');
   if(!plain(result)||!plain(context))return suspension(stepName,'invalid-result');
   let channel:Channel|null=null,tag:string|null=null;
   if(result.channel==='result'){
    if(!sameNames(result,['channel','value']))return suspension(stepName,'invalid-result');
    let normalized:unknown;
    try{normalized=nativeToFlow(result.value,row!.step.call.result,domainView.contract.values);}
    catch{return suspension(stepName,'invalid-result');}
    if(!typed(normalized,row!.step.call.result,domainView.contract.values))return suspension(stepName,'invalid-result');
    tag=variant(normalized);
    channel=tag===null?'success':'variant';
    result={channel:'result',value:normalized};
   }else if(['success','call-failure','contention','unavailable','evidence-conflict','unknown'].includes(result.channel)&&
    sameNames(result,['channel']))channel=result.channel;
   else return suspension(stepName,'invalid-result');
   const env:Record<string,unknown>=Object.assign(Object.create(null),context);
   if(result.channel==='result'&&row!.step.call.binding)env[row!.step.call.binding]=result.value;
   for(const item of row!.branches){
    const branch=item.branch;
    if(branch.channel!==channel||branch.channel==='variant'&&branch.variant!==tag)continue;
    const local=Object.assign(Object.create(null),env) as Record<string,unknown>;
    if(branch.binding){
     const fields=field(result.channel==='result'?result.value:undefined,'fields');
     const keys=names(fields);
     if(keys===null)return suspension(stepName,'invalid-result');
     local[branch.binding.name]=keys.length===1?field(fields,keys[0]!):result.channel==='result'?result.value:undefined;
    }
    try{
     if(item.guard){const value=expression.evaluate(item.guard,local,producers);if(typeof value!=='boolean')return suspension(stepName,'evaluation-failed');if(!value)continue;}
     if(item.require){const value=expression.evaluate(item.require,local,producers);if(typeof value!=='boolean')return suspension(stepName,'evaluation-failed');
      if(!value)return suspension(stepName,'failed-require');}
     let observation:unknown=item.observe?expression.evaluate(item.observe,local,producers):null;
     if(item.observe){const expected=expression.inspect(item.observe).result;
      if(!typed(observation,expected,domainView.contract.values))return suspension(stepName,'evaluation-failed');}
     if(item.observe)observation=flowToNative(observation,expression.inspect(item.observe).result,domainView.contract.values);
     current();return coreFreeze({workflow:source.workflow.name,source_capture_sha256:source.source_capture_sha256,step_name:stepName,
      outcome:'selected' as const,reason:'matched' as const,branch_index:item.index,channel:branch.channel,variant:branch.variant,
      action:branch.action,observation,retaining:branch.retaining,restriction:branch.restriction,
      original_journal:'retain' as const,qualification:'checked-source-branch-data-only;original-result-and-observation-commit-required' as const,
      authority_effect:'none' as const});
    }catch{return suspension(stepName,'evaluation-failed');}
   }
   return suspension(stepName,'unhandled-result');
  };
  const owner:CommerceWorkflowBranchSelectionOwnerV1=Object.freeze({
   plans(){current();return coreFreeze([...bound].map(([step_name,row])=>({step_name,result:row.step.call.result,
    branches:row.branches.map(item=>({index:item.index,channel:item.branch.channel,variant:item.branch.variant,
     guard_path:item.guard?expression.inspect(item.guard).path:null,require_path:item.require?expression.inspect(item.require).path:null,
     observe_path:item.observe?expression.inspect(item.observe).path:null,action:item.branch.action})),authority_effect:'none' as const})));},
   interpret,
   selectCaptured(stepName:string,result:CommerceWorkflowRemoteResultV1,snapshotValue:unknown,
    producers?:CommerceWorkflowExpressionProducersV1){
    current();const snapshotBinding=source.workflow.drivers.find(driver=>driver.kind==='snapshot')?.call.binding;
    if(!snapshotBinding)return suspension(stepName,'stale-context');
    const decision=interpret(stepName,result,{[snapshotBinding]:snapshotValue},producers);
    current();return decision;
   },
   selectCurrent(identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
    snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1,
    result:CommerceWorkflowRemoteResultV1,producers?:CommerceWorkflowExpressionProducersV1){
    current();assertCommerceWorkflowStepIdentityOwnerV1(identities);assertCommerceWorkflowSnapshotOwnerV1(snapshots);
    const initial=identities.inspect(identity);
    let selected:typeof initial,witness:ReturnType<CommerceWorkflowSnapshotOwnerV1['recheck']>;
    try{selected=identities.recheck(identity);witness=snapshots.recheck(snapshot);}
    catch{return suspension(initial.step_name,'stale-context');}
    if(selected.workflow!==source.workflow.name||witness.workflow!==source.workflow.name||
     selected.source_capture_sha256!==source.source_capture_sha256||witness.source_capture_sha256!==source.source_capture_sha256||
     selected.store_id!==witness.store_id||selected.order_id!==witness.order_id||selected.worker_id!==witness.worker_id||
     selected.worker_epoch!==witness.worker_epoch||selected.progress_version!==witness.progress_version)
     return suspension(selected.step_name,'stale-context');
    const snapshotBinding=source.workflow.drivers.find(driver=>driver.kind==='snapshot')?.call.binding;
    if(!snapshotBinding)return suspension(selected.step_name,'stale-context');
    const decision=interpret(selected.step_name,result,{[snapshotBinding]:witness.value},producers);
    try{identities.recheck(identity);snapshots.recheck(snapshot);current();return decision;}
    catch{return suspension(selected.step_name,'stale-context');}
   },assertCurrent:current,dispose(){if(disposed)return;disposed=true;expression.dispose();},
  });
  owners.add(owner);current();return owner;
 }catch(error){expression.dispose();throw error;}
}
