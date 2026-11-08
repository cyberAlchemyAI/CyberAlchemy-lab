/** Source-bound data for one Workflow step's declared causal Entry binding.
 * This owner does not authorize Auth, a journal transition, or dispatch.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import {types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCommerceIdentityCallOwner,type CommerceIdentityCallOwner} from './commerce-identity-call-owner.js';
import {createCommerceWorkflowStepArgumentsOwnerV1,type CommerceWorkflowStepArgumentsOwnerV1} from './commerce-workflow-step-arguments-v1.js';
import {assertCommerceWorkflowStepIdentityOwnerBrandV1,type CommerceWorkflowStepIdentityOwnerV1,type CommerceWorkflowStepIdentityHandleV1} from './commerce-workflow-step-identity-v1.js';
import type {CommerceWorkflowResumeSelectorV1,CommerceWorkflowResumeSelectionV1} from './commerce-workflow-resume-v1.js';
import type {CommerceWorkflowSnapshotOwnerV1,CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {EntryContractV1,FlowExprV1,ValueTypeV1} from './commerce-data-v1.js';
import type {CoreFlowEvaluation} from './commerce-core-flow-evaluation.js';

export class CommerceWorkflowCausalProjectionErrorV1 extends Error {
 readonly code:string;
 constructor(code:string,detail:string){super(detail);this.name='CommerceWorkflowCausalProjectionErrorV1';this.code=code;}
}
function bad(code:string,detail:string):never {throw new CommerceWorkflowCausalProjectionErrorV1(code,detail);}
const plain=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v)&&!host.isProxy(v)&&
 (Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
const get=(v:unknown,key:string):unknown=>{
 if(!plain(v))bad('InputType','original projection requires a plain source record');
 const descriptor=Object.getOwnPropertyDescriptor(v,key);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('MissingCausalField','source field '+key+' is absent');
 return descriptor!.value;
};
const at=(v:unknown,names:readonly string[]):unknown=>names.reduce((value,name)=>get(value,name),v);
const has=(v:unknown,key:string)=>plain(v)&&Object.hasOwn(v,key);
const flowPath=(v:unknown):readonly string[]=>{
 if(!plain(v))return [];
 const node=v as {op:string;name?:unknown;field?:unknown;value?:unknown};
 if(node.op==='var'&&typeof node.name==='string')return [node.name];
 if(node.op==='field'&&node.value&&typeof node.field==='string')return [...flowPath(node.value),node.field];
 return [];
};
const sourceEqualities=(v:unknown,input:string,causal:string):ReadonlyMap<string,readonly string[]>=>{
 const found=new Map<string,string[]>();
 const visit=(node:unknown,depth:number)=>{
  if(depth>64||!plain(node))return;
  if(node.op==='binary'&&node.operator==='eq'){
   const left=flowPath(node.left),right=flowPath(node.right);
   const add=(a:readonly string[],b:readonly string[])=>{
    if(a.length===2&&b.length===2&&a[0]===causal&&b[0]===input){
     const rows=found.get(a[1]!)??[];rows.push(b[1]!);found.set(a[1]!,rows);
    }
   };
   add(left,right);add(right,left);
  }
  for(const child of Object.values(node))if(child&&typeof child==='object'){
   if(Array.isArray(child))for(const item of child)visit(item,depth+1);else visit(child,depth+1);
  }
 };
 visit(v,0);return found;
};
const equalData=(a:unknown,b:unknown):boolean=>{
 let fuel=0;
 const same=(left:unknown,right:unknown,depth:number):boolean=>{
  if(++fuel>8192||depth>64)bad('ResourceLimit','bounded source equality exceeded');
  if(left===right)return true;
  if(typeof left!==typeof right||!left||!right||typeof left!=='object')return false;
  if(Array.isArray(left)||Array.isArray(right))return Array.isArray(left)&&Array.isArray(right)&&
   left.length===right.length&&left.every((item,index)=>same(item,right[index],depth+1));
  if(!plain(left)||!plain(right))return false;
  const keys=Object.keys(left),other=Object.keys(right);
  return keys.length===other.length&&keys.every(key=>Object.hasOwn(right,key)&&
   same(get(left,key),get(right,key),depth+1));
 };
 return same(a,b,0);
};
const evaluate=(node:FlowExprV1,env:Readonly<Record<string,unknown>>):unknown=>{
 let fuel=0;
 const run=(e:FlowExprV1,scope:Readonly<Record<string,unknown>>,depth:number):unknown=>{
  if(++fuel>8192||depth>64)bad('ResourceLimit','bounded access condition exceeded');
  const sub=(v:FlowExprV1)=>run(v,scope,depth+1);
  switch(e.op){
   case 'literal':return e.type.kind==='scalar'&&e.type.name==='UInt64'?BigInt(e.value as string):e.value;
   case 'var':return get(scope,e.name);
   case 'field':return get(sub(e.value),e.field);
   case 'list':if(e.items.length>100)bad('ResourceLimit','source membership list too large');return Object.freeze(e.items.map(sub));
   case 'let':{
    const value=sub(e.value),next=Object.assign(Object.create(null),scope,{[e.binding.name]:value});
    return run(e.body,next,depth+1);
   }
   case 'fold':{
    const values=sub(e.source),initial=sub(e.initial);
    if(!Array.isArray(values)||values.length>100)bad('InputType','source fold requires a bounded list');
    let state:unknown=initial;
    for(const item of values){
     const next=Object.assign(Object.create(null),scope,{[e.state.name]:state,[e.item.name]:item});
     state=run(e.body,next,depth+1);
    }
    return state;
   }
   case 'binary':{
    const left=sub(e.left);
    if(e.operator==='and'&&left===false)return false;
    if(e.operator==='or'&&left===true)return true;
    const right=sub(e.right);
    if(e.operator==='eq')return equalData(left,right);
    if(e.operator==='and'||e.operator==='or'){
     if(typeof left!=='boolean'||typeof right!=='boolean')bad('InputType','Boolean access condition required');
     return right;
    }
    if(typeof left!=='bigint'||typeof right!=='bigint')bad('InputType','numeric access comparison requires UInt64');
    if(e.operator==='lt')return left<right;
    if(e.operator==='lte')return left<=right;
    if(e.operator==='gt')return left>right;
    if(e.operator==='gte')return left>=right;
    return bad('UnsupportedCapability','access condition operator '+e.operator);
   }
   default:return bad('UnsupportedCapability','access condition operator '+e.op);
  }
 };
 return run(node,env,0);
};

/** A source refinement, rather than a field-name convention, identifies each
 * fingerprint that must be the selected step's original replay fingerprint. */
export function assertOriginalCausalFingerprintFieldsV1(
 fields:Readonly<Record<string,ValueTypeV1>>,fingerprintTypes:ReadonlySet<string>,
 projection:Readonly<Record<string,unknown>>,originalFingerprint:string,
):void {
 for(const [field,type] of Object.entries(fields)){
  if(type.kind!=='refinement'||!fingerprintTypes.has(type.name))continue;
  if(!Object.hasOwn(projection,field)||projection[field]!==originalFingerprint)
   bad('ForeignOwner','source causal fingerprint differs from original step identity: '+field);
 }
}

export interface CommerceWorkflowCausalProjectionHandleV1 {readonly kind:'original-workflow-causal-projection/v1-candidate'}
export interface CommerceWorkflowCausalProjectionInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly step_name:string;readonly entry_id:string;readonly order_id:string;readonly worker_id:string;
 readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly command_id:string;readonly request_fingerprint:string;
 readonly binding_name:string;readonly required_fields:readonly string[];
 readonly arguments:Readonly<Record<string,unknown>>;readonly projection:Readonly<Record<string,unknown>>;
 readonly qualification:'source-selected-causal-data-only;committed-journal-and-fresh-auth-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowCausalProjectionPlanV1 {
 readonly step_name:string;readonly entry_id:string;readonly binding_name:string;
 readonly required_fields:readonly string[];readonly authority_effect:'none';
}
export interface CommerceWorkflowCausalProjectionOwnerV1 {
 plans():readonly CommerceWorkflowCausalProjectionPlanV1[];
 derive(identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
  resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):CommerceWorkflowCausalProjectionHandleV1;
 inspect(handle:CommerceWorkflowCausalProjectionHandleV1):CommerceWorkflowCausalProjectionInspectionV1;
 recheck(handle:CommerceWorkflowCausalProjectionHandleV1):CommerceWorkflowCausalProjectionInspectionV1;
 /** Identity only; recheck() supplies currentness before this is used as evidence. */
 hasExactSourceHandles(handle:CommerceWorkflowCausalProjectionHandleV1,
  identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):boolean;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowCausalProjectionOwnerV1(owner:CommerceWorkflowCausalProjectionOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner','original causal projection owner required');
 owner.assertCurrent();
}
interface Plan {readonly step_name:string;readonly entry:EntryContractV1;readonly binding:EntryContractV1['access']['resource_bindings'][number];
 readonly input_matches:ReadonlyMap<string,readonly string[]>;readonly inspection:CommerceWorkflowCausalProjectionPlanV1}

/** Only checked source, genuine worker snapshot, source-evaluated arguments,
 * and source-derived command identity can contribute to the projection. */
export async function createCommerceWorkflowCausalProjectionOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 calls:CommerceIdentityCallOwner,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,directory:string,
):Promise<CommerceWorkflowCausalProjectionOwnerV1> {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);assertCommerceIdentityCallOwner(calls);
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)
  bad('InvalidContract','normalized absolute component directory required');
 const selected=binding.inspect(),checked=semantics.inspect(semantic),workflow=selected.workflow,
  sourceDomain=domain.inspect(baseline);
 if(checked.source_capture_sha256!==selected.source_capture_sha256||
    sourceDomain.source_capture_sha256!==selected.source_capture_sha256||
    calls.sourceDomain().source_capture_sha256!==selected.source_capture_sha256)
  bad('ForeignOwner','checked Workflow, Entry, and identity producer sources must agree');
 const fingerprintTypes=new Set(sourceDomain.contract.values.refinements.filter(row=>row.carrier.kind==='string'&&
  row.min_utf8_bytes===64&&row.max_utf8_bytes===64&&row.pattern==='^[a-f0-9]{64}$').map(row=>row.name));
 if(!fingerprintTypes.size)bad('MissingMapping','checked source fingerprint refinement required');
 const role=checked.workflows.find(row=>row.workflow.module+'.'+row.workflow.name===workflow.name);
 if(!role||role.steps.length!==workflow.steps.length)bad('ForeignOwner','one checked Workflow role required');
 const snapshotDriver=workflow.drivers.filter(driver=>driver.kind==='snapshot'),
  claimDriver=workflow.drivers.filter(driver=>driver.kind==='claim');
 if(snapshotDriver.length!==1||claimDriver.length!==1||!snapshotDriver[0]!.call.binding||!snapshotDriver[0]!.guard)
  bad('UnsupportedCapability','one checked snapshot and claim driver required');
 const name=snapshotDriver[0]!.call.binding!,guard=snapshotDriver[0]!.guard!.evaluation,
  correlation=workflow.correlation.evaluation;
 if(guard.op!=='binary'||guard.operator!=='eq')bad('UnsupportedCapability','checked snapshot correlation equality required');
 const guardBinary=guard as {readonly left:CoreFlowEvaluation;readonly right:CoreFlowEvaluation};
 const left=flowPath(guardBinary.left),right=flowPath(guardBinary.right),
  orderPath=left[0]===name&&dataDigest(guardBinary.right)===dataDigest(correlation)?left.slice(1,-1):
   right[0]===name&&dataDigest(guardBinary.left)===dataDigest(correlation)?right.slice(1,-1):null;
 if(!orderPath?.length)bad('InvalidContract','source snapshot order root required');
 const versionField=workflow.ownership.find(row=>row.field==='version')?.field;
 if(!versionField)bad('UnsupportedCapability','source progress version ownership required');
 const progressPaths=claimDriver[0]!.call.arguments.map(argument=>flowPath(argument.value.evaluation))
  .filter(parts=>parts.length>=3&&parts[0]===name&&parts.at(-1)===versionField);
 if(progressPaths.length!==1)bad('InvalidContract','one checked progress root required');
 const progressPath=progressPaths[0]!.slice(1,-1);
 const plans:Plan[]=[];
 for(const step of workflow.steps){
  if(step.kind!=='remote')continue;
  const entry=checked.entries.find(row=>row.id===step.call.entry);
  if(!entry)bad('ForeignEntry','selected Workflow Entry absent');
  if(entry.invokes.module+'.'+entry.invokes.name!==step.call.target||
     entry.invokes.role!==step.call.role||entry.access.caller!==workflow.owner||
     entry.access.resource_phase!=='causal-before-invocation'||!entry.access.resource_condition||
     entry.parameters.length!==step.call.arguments.length||
     entry.parameters.some((parameter,index)=>parameter.name!==step.call.arguments[index]!.parameter))
   bad('ForeignEntry','selected Workflow call and protected Entry differ');
  const candidates=entry.access.resource_bindings.filter(row=>row.origin.kind==='workflow-journal'&&
   row.origin.declaration===workflow.name&&row.abi==='craft.commerce-causal-call/v1-candidate'&&
   row.selector.split('/').at(-1)==='original-step-journal');
  if(candidates.length!==1||entry.access.resource_bindings.length!==1)
   bad('MissingMapping','one source-declared original journal causal binding required');
  const causal=candidates[0]!;
  if(!causal.required_fields.length||causal.required_fields.length!==Object.keys(causal.fields).length||
     causal.required_fields.some(field=>!Object.hasOwn(causal.fields,field)))
   bad('InvalidContract','exact per-Entry causal projection fields required');
  const matches=sourceEqualities(entry.access.resource_condition.expression,'input',causal.name);
  plans.push({step_name:step.name,entry,binding:causal,input_matches:matches,
   inspection:coreFreeze({step_name:step.name,entry_id:entry.id,binding_name:causal.name,
    required_fields:causal.required_fields,authority_effect:'none' as const})});
 }
 if(!plans.length||new Set(plans.map(plan=>plan.step_name)).size!==plans.length)
  bad('InvalidContract','unique checked remote Workflow steps required');
 mkdirSync(directory,{recursive:true,mode:0o700});
 const argumentDirectory=path.join(directory,'arguments');mkdirSync(argumentDirectory,{mode:0o700});
 const argumentsOwner=await createCommerceWorkflowStepArgumentsOwnerV1(binding,semantics,semantic,calls,stage,source,domain,baseline,argumentDirectory);
 const byStep=new Map(plans.map(plan=>[plan.step_name,plan]));
 const held=new WeakMap<object,{inspection:CommerceWorkflowCausalProjectionInspectionV1;identities:CommerceWorkflowStepIdentityOwnerV1;
  identity:CommerceWorkflowStepIdentityHandleV1;resume:CommerceWorkflowResumeSelectorV1;selection:CommerceWorkflowResumeSelectionV1;
  snapshots:CommerceWorkflowSnapshotOwnerV1;snapshot:CommerceWorkflowSnapshotHandleV1}>();
 let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner','causal owner retired');binding.assertCurrent();semantics.assertCurrent(semantic);
  argumentsOwner.assertCurrent();};
 const project=(identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
  resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):CommerceWorkflowCausalProjectionInspectionV1=>{
  if(disposed)bad('DisposedOwner','causal owner retired');
  assertCommerceWorkflowStepIdentityOwnerBrandV1(identities);
  // Argument evaluation checks the causal owner dependencies, selected step,
  // and original snapshot. Identity is independently rechecked below. These
  // already-checked views remain valid during this synchronous projection.
  const evaluated=argumentsOwner.evaluateChecked(resume,selection,snapshots,snapshot),
   args=evaluated.inspection,id=identities.recheck(identity),
   witness=evaluated.snapshotInspection,choice=evaluated.selectionInspection,
   plan=byStep.get(id.step_name);
  if(!plan||choice.outcome!=='selected'||choice.action?.kind!=='step'||choice.action.target!==plan.step_name||
     choice.workflow!==workflow.name||id.workflow!==workflow.name||witness.workflow!==workflow.name||
     args.workflow!==workflow.name||choice.source_capture_sha256!==selected.source_capture_sha256||
     id.source_capture_sha256!==selected.source_capture_sha256||witness.source_capture_sha256!==selected.source_capture_sha256||
     args.source_capture_sha256!==selected.source_capture_sha256||id.store_id!==witness.store_id||
     id.order_id!==witness.order_id||id.order_id!==args.order_id||
     id.worker_id!==witness.worker_id||id.worker_id!==args.worker_id||
     id.worker_epoch!==witness.worker_epoch||id.worker_epoch!==args.worker_epoch||
     id.progress_version!==witness.progress_version||id.progress_version!==args.progress_version||
     args.step!==id.step_name||args.entry!==id.target_entry_id||args.entry!==plan.entry.id||
     args.target!==plan.entry.invokes.module+'.'+plan.entry.invokes.name||args.role!==plan.entry.invokes.role)
   bad('ForeignOwner','current step, snapshot, identity, arguments and protected Entry differ');
  const input:Record<string,unknown>=Object.create(null);
  for(const argument of args.arguments){
   if(Object.hasOwn(input,argument.parameter))bad('InvalidContract','duplicate source Entry argument');
   input[argument.parameter]=argument.value;
  }
  if(Object.keys(input).length!==plan.entry.parameters.length||
     plan.entry.parameters.some(parameter=>!Object.hasOwn(input,parameter.name)))
   bad('InvalidContract','checked Entry argument set differs from source step');
  const order=at(witness.value,orderPath),progress=at(witness.value,progressPath),projection:Record<string,unknown>=Object.create(null);
  for(const field of plan.binding.required_fields){
   let value:unknown,found=false;
   if(field==='commandId'){value=id.command_id;found=true;}
   else{
    const inOrder=has(order,field),inProgress=has(progress,field);
    if(inOrder&&inProgress)bad('AmbiguousCausalField','field exists in both source snapshot records: '+field);
    if(inOrder||inProgress){value=get(inOrder?order:progress,field);found=true;}
   }
   const matches=plan.input_matches.get(field)??[];
   if(!found&&matches.length===1&&Object.hasOwn(input,matches[0]!)){
    const candidate=input[matches[0]!];
    value=candidate;
    found=true;
   }
   if(!found)bad('MissingCausalField','required source causal field has no original value: '+field);
   if(field==='orderId'&&value!==id.order_id)bad('ForeignOwner','causal order differs from source identity');
   if(matches.some(parameter=>!equalData(input[parameter],value)))
    bad('ResourceConditionFalse','source argument differs from original causal field: '+field);
   projection[field]=value;
  }
  assertOriginalCausalFingerprintFieldsV1(plan.binding.fields,fingerprintTypes,projection,id.request_fingerprint);
  if(Object.hasOwn(projection,'commandId')&&projection.commandId!==id.command_id)
   bad('ForeignOwner','causal journal command differs from source identity');
  const env=Object.assign(Object.create(null),{input,[plan.binding.name]:projection});
  if(evaluate(plan.entry.access.resource_condition!.expression,env)!==true)
   bad('ResourceConditionFalse','declared protected Entry condition rejected original step data');
  return coreFreeze({workflow:workflow.name,source_capture_sha256:selected.source_capture_sha256,
   store_id:id.store_id,step_name:id.step_name,entry_id:id.target_entry_id,order_id:id.order_id,
   worker_id:id.worker_id,worker_epoch:id.worker_epoch,progress_version:id.progress_version,
   command_id:id.command_id,request_fingerprint:id.request_fingerprint,binding_name:plan.binding.name,
   required_fields:plan.binding.required_fields,arguments:input,projection,
   qualification:'source-selected-causal-data-only;committed-journal-and-fresh-auth-required' as const,
   authority_effect:'none' as const});
 };
 const owner:CommerceWorkflowCausalProjectionOwnerV1=Object.freeze({
  plans(){current();return coreFreeze(plans.map(plan=>plan.inspection));},
  derive(identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
   resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
   snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1){
   const inspection=project(identities,identity,resume,selection,snapshots,snapshot),
    handle:CommerceWorkflowCausalProjectionHandleV1=Object.freeze({kind:'original-workflow-causal-projection/v1-candidate'});
   held.set(handle,{inspection,identities,identity,resume,selection,snapshots,snapshot});return handle;
  },
  inspect(handle:CommerceWorkflowCausalProjectionHandleV1){current();const row=handle&&typeof handle==='object'?held.get(handle):undefined;
   if(!row)bad('ForeignOwner','original causal projection handle required');return row!.inspection;},
  recheck(handle:CommerceWorkflowCausalProjectionHandleV1){const row=handle&&typeof handle==='object'?held.get(handle):undefined;
   if(!row)bad('ForeignOwner','original causal projection handle required');
   // This private row retains only genuine, immutable source-derived handles.
   // Recheck every original mutable dependency on every use, including the
   // actual persisted snapshot. With identical snapshot and checked source/
   // native components, the already-derived pure projection is identical.
   // No freshness result is cached across this call, an await or an effect.
   current();
   row!.identities.recheck(row!.identity);
   // The exact identity recheck already reread its original snapshot and
   // checked its resume selection. Distinct matching handles must still be
   // checked independently; value equality cannot share mutable custody.
   if(!row!.identities.hasExactSourceHandles(row!.identity,row!.resume,row!.selection,row!.snapshots,row!.snapshot)){
    row!.resume.inspectSelection(row!.selection);
    row!.snapshots.recheck(row!.snapshot);
   }
   current();
   return row!.inspection;
  },
  hasExactSourceHandles(handle:CommerceWorkflowCausalProjectionHandleV1,
   identities:CommerceWorkflowStepIdentityOwnerV1,identity:CommerceWorkflowStepIdentityHandleV1,
   snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1){
   if(disposed)bad('DisposedOwner','causal owner retired');
   const row=handle&&typeof handle==='object'?held.get(handle):undefined;
   if(!row)bad('ForeignOwner','original causal projection handle required');
   return row.identities===identities&&row.identity===identity&&
    row.snapshots===snapshots&&row.snapshot===snapshot;
  },
  assertCurrent:current,dispose(){if(disposed)return;disposed=true;argumentsOwner.dispose();},
 });
 owners.add(owner);current();return owner;
}
