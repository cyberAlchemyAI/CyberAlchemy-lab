/** Stable command identity for a checked Workflow step. This owner evaluates
 * source expressions against an original current worker snapshot; the handle
 * is inert and cannot authorize an Entry, journal write, or provider call.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCommerceIdentityCallOwner,type CommerceIdentityCallOwner,type CommerceIdentityCallHandle} from './commerce-identity-call-owner.js';
import {createCommerceIdentityComponentOwner,type CommerceIdentityComponentHandle} from './commerce-identity-component.js';
import {createCommerceWorkflowStepArgumentsOwnerV1,type CommerceWorkflowStepArgumentsHandleV1} from './commerce-workflow-step-arguments-v1.js';
import {createCommerceWorkflowExpressionOwnerV1,type CommerceWorkflowExpressionHandleV1,type CommerceWorkflowExpressionCallsiteV1} from './commerce-workflow-expression-v1.js';
import type {CommerceWorkflowResumeSelectorV1,CommerceWorkflowResumeSelectionV1} from './commerce-workflow-resume-v1.js';
import type {CommerceWorkflowSnapshotOwnerV1,CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CoreWorkflowStep} from './commerce-core-flow-workflow.js';
import type {WorkflowContractV1} from './commerce-data-v1.js';
import type {CoreFlowEvaluation} from './commerce-core-flow-evaluation.js';

export class CommerceWorkflowStepIdentityErrorV1 extends Error {
 readonly code:string;
 constructor(code:string,detail:string){super(detail);this.name='CommerceWorkflowStepIdentityErrorV1';this.code=code;}
}
const bad=(code:string,detail:string):never=>{throw new CommerceWorkflowStepIdentityErrorV1(code,detail);};
type RemoteStep=Extract<CoreWorkflowStep,{kind:'remote'}>;
const remote=(step:CoreWorkflowStep|undefined):step is RemoteStep=>step?.kind==='remote';
const flowPath=(value:CoreFlowEvaluation):readonly string[]=>{
 const node=value as {readonly op:string;readonly name?:unknown;readonly field?:unknown;readonly value?:CoreFlowEvaluation};
 if(node.op==='var'&&typeof node.name==='string')return [node.name];
 if(node.op==='field'&&node.value&&typeof node.field==='string')return [...flowPath(node.value),node.field];
 return [];
};
const same=(a:unknown,b:unknown)=>dataDigest(a)===dataDigest(b);
const validKey=(v:unknown):v is string=>typeof v==='string'&&v.length>0&&Buffer.byteLength(v,'utf8')<=256&&
 Buffer.from(v).toString('utf8')===v;
const validFingerprint=(v:unknown):v is string=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);

export interface CommerceWorkflowStepIdentityHandleV1 {readonly kind:'original-workflow-step-identity/v1-candidate'}
export interface CommerceWorkflowStepIdentityInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly store_id:string;
 readonly step_name:string;readonly target_entry_id:string;readonly order_id:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly command_id:string;readonly request_fingerprint:string;
 readonly identity_source_step:string;
 readonly qualification:'original-source-command-identity-from-current-worker-snapshot;no-journal-or-dispatch-authority';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowStepIdentityPlanInspectionV1 {
 readonly step_name:string;readonly target_entry_id:string;readonly identity_source_step:string;
 readonly order_argument_path:string;readonly command_argument_path:string;readonly fingerprint_argument_path:string;
 readonly direct_command_argument_path:string|null;
 readonly authority_effect:'none';
}
export interface CommerceWorkflowStepIdentityOwnerV1 {
 plans():readonly CommerceWorkflowStepIdentityPlanInspectionV1[];
 derive(resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):CommerceWorkflowStepIdentityHandleV1;
 inspect(handle:CommerceWorkflowStepIdentityHandleV1):CommerceWorkflowStepIdentityInspectionV1;
 recheck(handle:CommerceWorkflowStepIdentityHandleV1):CommerceWorkflowStepIdentityInspectionV1;
 /** Identity only. recheck() supplies freshness for these exact retained handles. */
 hasExactSourceHandles(handle:CommerceWorkflowStepIdentityHandleV1,
  resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):boolean;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
/** Brand only. Follow immediately with a private method that checks currentness. */
export function assertCommerceWorkflowStepIdentityOwnerBrandV1(owner:CommerceWorkflowStepIdentityOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner','original Workflow step identity owner required');
}
export function assertCommerceWorkflowStepIdentityOwnerV1(owner:CommerceWorkflowStepIdentityOwnerV1):void {
 assertCommerceWorkflowStepIdentityOwnerBrandV1(owner);
 owner.assertCurrent();
}
interface Plan {
 readonly step:RemoteStep;readonly stepIndex:number;readonly companion:RemoteStep;readonly companionIndex:number;
 readonly orderIndex:number;readonly keyIndex:number;readonly fingerprintIndex:number;
 readonly directKeyIndex:number|null;readonly directFingerprintIndex:number|null;
 readonly order:CommerceWorkflowExpressionHandleV1;readonly key:CommerceWorkflowExpressionHandleV1;
 readonly fingerprint:CommerceWorkflowExpressionHandleV1;
 readonly inspection:CommerceWorkflowStepIdentityPlanInspectionV1;
}

/** The selected source already names its uncertainty/inspection companion.
 * A companion with a unique order, command, and fingerprint argument supplies
 * replay identity even when the immediate action uses only CAS versions. */
export async function createCommerceWorkflowStepIdentityOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 calls:CommerceIdentityCallOwner,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,directory:string,
):Promise<CommerceWorkflowStepIdentityOwnerV1> {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);assertCommerceIdentityCallOwner(calls);
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)
  bad('InvalidContract','normalized absolute component directory required');
 const selected=binding.inspect(),workflow=selected.workflow,checked=semantics.inspect(semantic),sourceDomain=domain.inspect(baseline);
 if(checked.source_capture_sha256!==selected.source_capture_sha256||
    sourceDomain.source_capture_sha256!==selected.source_capture_sha256||
    calls.sourceDomain().source_capture_sha256!==selected.source_capture_sha256)
  bad('ForeignOwner','Workflow, semantic, and source value domains differ');
 const plan=checked.workflows.find(p=>p.workflow.module+'.'+p.workflow.name===workflow.name);
 if(!plan||plan.steps.length!==workflow.steps.length)bad('InvalidContract','one matching checked original Workflow required');
 const original=plan as WorkflowContractV1;
 for(let i=0;i<workflow.steps.length;i++){
  const actual=workflow.steps[i]!,role=original.steps[i]!;
  if(actual.name!==role.name||actual.kind!==role.kind)bad('InvalidContract','Workflow step order differs from semantic source');
  if(actual.kind==='remote'&&role.kind==='remote'){
   if(actual.call.entry!==role.call.entry||actual.call.target!==role.call.target||actual.call.role!==role.call.role||
      actual.call.arguments.length!==role.call.arguments.length)bad('InvalidContract','Workflow call differs from semantic source');
   for(let j=0;j<actual.call.arguments.length;j++)if(actual.call.arguments[j]!.parameter!==role.call.arguments[j]!.parameter||
      !same(actual.call.arguments[j]!.value.evaluation,role.call.arguments[j]!.value.expression))
    bad('InvalidContract','Workflow argument differs from semantic source');
  }
 }
 const snapshots=workflow.drivers.filter(d=>d.kind==='snapshot');
 if(snapshots.length!==1||!snapshots[0]!.call.binding||!snapshots[0]!.guard)
  bad('UnsupportedCapability','one checked snapshot driver and correlation guard required');
 const snapshot=snapshots[0]!,guard=snapshot.guard!.evaluation,correlation=workflow.correlation.evaluation;
 if(guard.op!=='binary'||guard.operator!=='eq')bad('UnsupportedCapability','snapshot correlation equality required');
 const guardBinary=guard as {readonly op:'binary';readonly operator:'eq';readonly left:CoreFlowEvaluation;readonly right:CoreFlowEvaluation};
 const leftMatches=same(guardBinary.left,correlation),rightMatches=same(guardBinary.right,correlation);
 if(leftMatches===rightMatches)bad('InvalidContract','snapshot guard must compare original correlation exactly once');
 const orderExpression=leftMatches?guardBinary.right:guardBinary.left,orderPath=flowPath(orderExpression);
 if(orderPath.length<2||orderPath[0]!==snapshot.call.binding)
  bad('InvalidContract','snapshot order correlation path required');
 const fingerprints=new Set(sourceDomain.contract.values.refinements.filter(r=>r.carrier.kind==='string'&&
  r.min_utf8_bytes===64&&r.max_utf8_bytes===64&&r.pattern==='^[a-f0-9]{64}$').map(r=>r.name));
 if(fingerprints.size===0)bad('MissingMapping','checked source fingerprint type required');
 const expression=createCommerceWorkflowExpressionOwnerV1(binding,semantics,semantic,domain,baseline);
 const stepIndex=new Map(workflow.steps.map((step,index)=>[step.name,index] as const)),entryService=new Map(checked.entries.map(entry=>[entry.id,entry.service]));
 const fingerprintArg=(step:RemoteStep):number[]=>step.call.arguments.flatMap((argument,index)=>
  argument.value.type.kind==='refinement'&&fingerprints.has(argument.value.type.name)?[index]:[]);
 const planned:Plan[]=[];
 try{
  for(let index=0;index<workflow.steps.length;index++){
   const step=workflow.steps[index]!;if(!remote(step))continue;
   const ownFingerprints=fingerprintArg(step);
   if(ownFingerprints.length>1)bad('AmbiguousIdentity','multiple source fingerprint arguments');
   const candidates=new Set<number>();
   if(ownFingerprints.length===1)candidates.add(index);
   else for(const branch of step.branches){
    const action=branch.action;
    if(action.kind!=='step'||!(branch.channel==='unknown'||branch.channel==='call-failure'||
       branch.channel==='variant'&&(branch.variant==='Unknown'||branch.variant==='Pending')))continue;
    const next=stepIndex.get(action.target),target=next===undefined?undefined:workflow.steps[next];
    if(remote(target)&&fingerprintArg(target).length===1)candidates.add(next!);
   }
   if(candidates.size!==1)bad(candidates.size?'AmbiguousIdentity':'MissingIdentity',
    'one checked uncertainty companion with a fingerprint required for '+step.name);
   const companionIndex=[...candidates][0]!,companionCandidate=workflow.steps[companionIndex]!;
   if(!remote(companionCandidate))bad('InvalidContract','remote identity companion required');
   const companion=companionCandidate as RemoteStep;
   if(!entryService.has(step.call.entry)||entryService.get(step.call.entry)!==entryService.get(companion.call.entry))
    bad('ForeignEntry','step and identity companion must belong to the same selected service');
   const matchingOrder=companion.call.arguments.flatMap((argument,j)=>same(argument.value.evaluation,orderExpression)?[j]:[]);
   const matchingFingerprint=fingerprintArg(companion);
   if(matchingOrder.length!==1||matchingFingerprint.length!==1||matchingOrder[0]===matchingFingerprint[0]||
      companion.call.arguments.length!==3)
    bad('UnsupportedCapability','identity companion requires unique correlated order, command, and fingerprint arguments');
   const orderIndex=matchingOrder[0]!,fingerprintIndex=matchingFingerprint[0]!,keyIndex=[0,1,2].find(j=>j!==orderIndex&&j!==fingerprintIndex)!;
   const key=companion.call.arguments[keyIndex]!,keyType=key.value.type;
   if((keyType.kind!=='String'&&keyType.kind!=='refinement')||
      keyType.kind==='refinement'&&fingerprints.has(keyType.name))
    bad('TypeMismatch','source command identity must be string typed');
   const directKeys=step.call.arguments.flatMap((argument,j)=>same(argument.value.evaluation,key.value.evaluation)?[j]:[]);
   if(directKeys.length>1)bad('AmbiguousIdentity','duplicate original command expression in step');
   const directKeyIndex=directKeys.length===1?directKeys[0]!:null;
   if(companionIndex!==index&&directKeyIndex===null&&
      !step.branches.some(branch=>branch.channel==='unknown'&&branch.action.kind==='step'&&branch.action.target===companion.name))
    bad('MissingIdentity','indirect command key requires a declared unknown-result inspection edge');
   const argPath=(stepNumber:number,argNumber:number)=>'$.steps['+stepNumber+'].call.arguments['+argNumber+'].value';
   const orderPath=argPath(companionIndex,orderIndex),keyPath=argPath(companionIndex,keyIndex),
    fingerprintPath=argPath(companionIndex,fingerprintIndex);
   planned.push({step,stepIndex:index,companion,companionIndex,orderIndex,keyIndex,fingerprintIndex,
    directKeyIndex,directFingerprintIndex:ownFingerprints.length===1?ownFingerprints[0]!:null,
    order:expression.bind(orderPath),key:expression.bind(keyPath),fingerprint:expression.bind(fingerprintPath),
    inspection:coreFreeze({step_name:step.name,target_entry_id:step.call.entry,identity_source_step:companion.name,
     order_argument_path:orderPath,command_argument_path:keyPath,fingerprint_argument_path:fingerprintPath,
     direct_command_argument_path:directKeyIndex===null?null:argPath(index,directKeyIndex),authority_effect:'none' as const})});
  }
  const neededSites=new Map<string,CommerceIdentityCallHandle>();
  for(const plan of planned){
   const sites=expression.inspect(plan.fingerprint).callsites;
   for(const site of sites){
    if(site.kind!=='native'||site.abi!=='craft.commerce-identity/v1-candidate')
     bad('UnsupportedCapability','fingerprint expression requires an original supported identity producer');
    if(!neededSites.has(site.path)){
     const h=calls.bind(original,site.path),observed=calls.inspect(h).observation;
     if(observed.abi!==site.abi||observed.context!==site.context||observed.source_type!==site.source_type||
        observed.method!==site.method||observed.arguments.length!==site.argument_count)
      bad('InvalidContract','semantic native callsite differs from checked expression');
     neededSites.set(site.path,h);
    }
   }
  }
  mkdirSync(directory,{recursive:true,mode:0o700});
  const argumentDirectory=path.join(directory,'arguments'),fingerprintDirectory=path.join(directory,'fingerprints');
  mkdirSync(argumentDirectory,{mode:0o700});mkdirSync(fingerprintDirectory,{mode:0o700});
  const components=createCommerceIdentityComponentOwner(calls,stage,source,domain,baseline);
  const component:CommerceIdentityComponentHandle=await components.materialize([...neededSites.values()],fingerprintDirectory);
  let argumentsOwner:Awaited<ReturnType<typeof createCommerceWorkflowStepArgumentsOwnerV1>>;
  try{argumentsOwner=await createCommerceWorkflowStepArgumentsOwnerV1(binding,semantics,semantic,calls,
   stage,source,domain,baseline,argumentDirectory);}catch(error){components.dispose(component);throw error;}
  const byStep=new Map(planned.map(plan=>[plan.step.name,plan]));
  const owned=new WeakMap<object,{inspection:CommerceWorkflowStepIdentityInspectionV1;resume:CommerceWorkflowResumeSelectorV1;
   selection:CommerceWorkflowResumeSelectionV1;snapshots:CommerceWorkflowSnapshotOwnerV1;snapshot:CommerceWorkflowSnapshotHandleV1;
   arguments:CommerceWorkflowStepArgumentsHandleV1;plan:Plan}>();
  let disposed=false;
  const current=()=>{
   if(disposed)bad('DisposedOwner','Workflow step identity owner retired');
   binding.assertCurrent();semantics.assertCurrent(semantic);domain.assertCurrent(baseline);
   expression.assertCurrent();argumentsOwner.assertCurrent();components.assertCurrent(component);
   calls.assertCurrentSet([...neededSites.values()]);
  };
  const evaluate=(plan:Plan,value:unknown):{order:string;command:string;fingerprint:string}=>{
   const env={snapshot:value},producer={native:(site:CommerceWorkflowExpressionCallsiteV1,args:readonly unknown[])=>{
    const handle=neededSites.get(site.path);
    if(!handle||site.kind!=='native')bad('ForeignOwner','exact original fingerprint callsite required');
    const observation=calls.inspect(handle!).observation;
    if(observation.context!==site.context||observation.source_type!==site.source_type||
       observation.abi!==site.abi||observation.method!==site.method||observation.arguments.length!==args.length)
     bad('ForeignOwner','source fingerprint producer signature changed');
    const result=components.evaluateBoundParameters(component,handle!,args);
    if(!result.ok)bad('ProducerValueRejected','original identity producer rejected source arguments');
    return result.value;
   }};
   const order=expression.evaluate(plan.order,env),command=expression.evaluate(plan.key,env),
    fingerprint=expression.evaluate(plan.fingerprint,env,producer);
   if(!validKey(order))return bad('InputType','source correlated order value must be a bounded identifier');
   if(!validKey(command))return bad('InputType','source command value must be a bounded identifier');
   if(!validFingerprint(fingerprint))return bad('InputType','source fingerprint value must be a checked digest');
   return {order,command,fingerprint};
  };
  const recheck=(handle:CommerceWorkflowStepIdentityHandleV1):CommerceWorkflowStepIdentityInspectionV1=>{
   if(disposed)bad('DisposedOwner','Workflow step identity owner retired');
   const row=handle&&typeof handle==='object'?owned.get(handle):undefined;
   if(!row)bad('ForeignOwner','original Workflow step identity handle required');
   // This private row was minted only from branded owners. Their exact
   // selection/snapshot methods fully recheck custody below; repeating their
   // brand-current checks here adds no authority within this synchronous call.
   // The digest and arguments were derived once from this exact immutable
   // snapshot using checked deterministic source/native components. Rechecking
   // the original snapshot and those components proves their inputs unchanged;
   // recomputing every native digest here adds no freshness or authority.
   const selectedStep=row!.resume.inspectSelection(row!.selection),witness=row!.snapshots.recheck(row!.snapshot),
    args=argumentsOwner.inspect(row!.arguments),prior=row!.inspection;
   if(selectedStep.outcome!=='selected'||selectedStep.action?.kind!=='step'||
      selectedStep.action.target!==prior.step_name||selectedStep.workflow!==prior.workflow||
      selectedStep.source_capture_sha256!==prior.source_capture_sha256||
      selectedStep.order_id!==prior.order_id||selectedStep.worker_id!==prior.worker_id||
      selectedStep.worker_epoch!==prior.worker_epoch||selectedStep.progress_version!==prior.progress_version||
      witness.workflow!==prior.workflow||witness.source_capture_sha256!==prior.source_capture_sha256||
      witness.store_id!==prior.store_id||witness.order_id!==prior.order_id||witness.worker_id!==prior.worker_id||
      witness.worker_epoch!==prior.worker_epoch||witness.progress_version!==prior.progress_version||
      args.step!==prior.step_name||args.entry!==prior.target_entry_id||args.order_id!==prior.order_id||
      args.worker_id!==prior.worker_id||args.worker_epoch!==prior.worker_epoch||
      args.progress_version!==prior.progress_version)
    bad('StaleOwner','selected original step identity changed before journal use');
   const directKey=row!.plan.directKeyIndex;
   if(directKey!==null&&args.arguments[directKey]?.value!==prior.command_id)bad('StaleOwner','selected step command differs from source identity');
   const directFingerprint=row!.plan.directFingerprintIndex;
   if(directFingerprint!==null&&args.arguments[directFingerprint]?.value!==prior.request_fingerprint)
    bad('StaleOwner','selected step fingerprint differs from source identity');
   current();return prior;
  };
  const owner:CommerceWorkflowStepIdentityOwnerV1=Object.freeze({
   plans(){current();return coreFreeze(planned.map(plan=>plan.inspection));},
   derive(resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
    snapshots:CommerceWorkflowSnapshotOwnerV1,snapshotHandle:CommerceWorkflowSnapshotHandleV1){
    current();
    // Argument evaluation checks the exact selected remote step and rechecks
    // its original snapshot. Repeating those checks here adds no authority:
    // this handle is inert, and every later consumer performs full recheck.
    const argsHandle=argumentsOwner.evaluate(resume,selection,snapshots,snapshotHandle),
     args=argumentsOwner.inspect(argsHandle),witness=snapshots.inspect(snapshotHandle);
    const plan=byStep.get(args.step);
    if(!plan)bad('UnsupportedCapability','selected step has no checked source command identity');
    if(args.workflow!==workflow.name||witness.workflow!==workflow.name||
       args.source_capture_sha256!==selected.source_capture_sha256||
       witness.source_capture_sha256!==selected.source_capture_sha256||
       args.order_id!==witness.order_id||args.worker_id!==witness.worker_id||
       args.worker_epoch!==witness.worker_epoch||args.progress_version!==witness.progress_version)
     bad('ForeignOwner','resume selection and original worker snapshot differ');
    const identity=evaluate(plan!,witness.value);
    if(args.step!==plan!.step.name||args.entry!==plan!.step.call.entry||args.target!==plan!.step.call.target||
       args.role!==plan!.step.call.role||args.order_id!==witness.order_id||identity.order!==witness.order_id)
     bad('ForeignOwner','selected step arguments and source identity differ');
    if(plan!.directKeyIndex!==null&&args.arguments[plan!.directKeyIndex]?.value!==identity.command)
     bad('ForeignOwner','original step command differs from checked replay identity');
    if(plan!.directFingerprintIndex!==null&&args.arguments[plan!.directFingerprintIndex]?.value!==identity.fingerprint)
     bad('ForeignOwner','original step fingerprint differs from checked replay identity');
    const inspection:CommerceWorkflowStepIdentityInspectionV1=coreFreeze({workflow:workflow.name,
     source_capture_sha256:selected.source_capture_sha256,store_id:witness.store_id,
     step_name:plan!.step.name,target_entry_id:plan!.step.call.entry,order_id:witness.order_id,
     worker_id:witness.worker_id,worker_epoch:witness.worker_epoch,progress_version:witness.progress_version,
     command_id:identity.command,request_fingerprint:identity.fingerprint,
     identity_source_step:plan!.companion.name,
     qualification:'original-source-command-identity-from-current-worker-snapshot;no-journal-or-dispatch-authority' as const,
     authority_effect:'none' as const});
    const handle:CommerceWorkflowStepIdentityHandleV1=Object.freeze({kind:'original-workflow-step-identity/v1-candidate'});
    owned.set(handle,{inspection,resume,selection,snapshots,snapshot:snapshotHandle,arguments:argsHandle,plan:plan!});
    // The selected step, snapshot, arguments, and source identity were checked
    // above. The inert handle grants no effect; every later use calls recheck.
    current();return handle;
   },
   inspect(handle:CommerceWorkflowStepIdentityHandleV1){current();const row=handle&&typeof handle==='object'?owned.get(handle):undefined;
    if(!row)bad('ForeignOwner','original Workflow step identity handle required');return row!.inspection;},
   recheck,
   hasExactSourceHandles(handle:CommerceWorkflowStepIdentityHandleV1,
    resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
    snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1){
    if(disposed)bad('DisposedOwner','Workflow step identity owner retired');
    const row=handle&&typeof handle==='object'?owned.get(handle):undefined;
    if(!row)bad('ForeignOwner','original Workflow step identity handle required');
    return row!.resume===resume&&row!.selection===selection&&
     row!.snapshots===snapshots&&row!.snapshot===snapshot;
   },assertCurrent:current,
   dispose(){if(disposed)return;disposed=true;argumentsOwner.dispose();components.dispose(component);expression.dispose();
    for(const handle of neededSites.values())calls.dispose(handle);},
  });
  owners.add(owner);current();return owner;
 }catch(error){expression.dispose();throw error;}
}
