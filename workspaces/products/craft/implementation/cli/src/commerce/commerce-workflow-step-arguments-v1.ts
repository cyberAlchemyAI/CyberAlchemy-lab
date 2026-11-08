/** Inert source-bound arguments for the currently checked Workflow steps.
 * This does not authorize an Entry or prepare/commit a StepJournal row.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceWorkflowResumeSelectorBrandV1,type CommerceWorkflowResumeSelectorV1,type CommerceWorkflowResumeSelectionV1} from './commerce-workflow-resume-v1.js';
import {assertCommerceWorkflowSnapshotOwnerBrandV1,type CommerceWorkflowSnapshotOwnerV1,type CommerceWorkflowSnapshotHandleV1} from './commerce-workflow-snapshot-v1.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCommerceIdentityCallOwner,type CommerceIdentityCallOwner,type CommerceIdentityCallHandle} from './commerce-identity-call-owner.js';
import {createCommerceIdentityComponentOwner,type CommerceIdentityComponentHandle} from './commerce-identity-component.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {WorkflowContractV1} from './commerce-data-v1.js';

export class CommerceWorkflowStepArgumentsErrorV1 extends Error {
 readonly code:string;
 constructor(code:string,detail:string){super(detail);this.name='CommerceWorkflowStepArgumentsErrorV1';this.code=code;}
}
const bad=(code:string,detail:string):never=>{throw new CommerceWorkflowStepArgumentsErrorV1(code,detail);};
type RecordData=Readonly<Record<string,unknown>>;
const record=(v:unknown):v is RecordData=>!!v&&typeof v==='object'&&!Array.isArray(v)&&!host.isProxy(v)&&
 (Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
const field=(v:unknown,key:string):unknown=>{
 if(!record(v))bad('InputType','plain source argument data required');
 const d=Object.getOwnPropertyDescriptor(v,key);
 if(!d||!d.enumerable||!Object.hasOwn(d,'value'))bad('InputType','missing source argument field '+key);
 return d!.value;
};
const expression=(v:unknown):RecordData=>record(v)&&typeof field(v,'op')==='string'?v:bad('InvalidContract','checked expression data required');
const entries=(v:unknown):readonly [string,unknown][]=>{
 if(!record(v))bad('InvalidContract','plain source expression fields required');
 return Object.keys(v as object).map(key=>[key,field(v,key)] as const);
};
const optional=(v:unknown):{kind:'some'|'none';value?:unknown}=>{
 const kind=field(v,'kind');
 if(kind==='none')return {kind};
 if(kind==='some')return {kind,value:field(v,'value')};
 return bad('InputType','source optional value required');
};

export interface CommerceWorkflowStepArgumentsHandleV1 {readonly kind:'original-workflow-step-arguments/v1-candidate'}
export interface CommerceWorkflowStepArgumentsInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly step:string;
 readonly entry:string;readonly target:string;readonly role:'Operation'|'Query';
 readonly arguments:readonly {readonly parameter:string;readonly value:unknown}[];
 readonly order_id:string;readonly worker_id:string;readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly qualification:'inert-source-selected-step-arguments;entry-auth-codec-and-original-step-journal-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowStepArgumentsOwnerV1 {
 evaluate(resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):CommerceWorkflowStepArgumentsHandleV1;
 /** Returns the inspection already checked at the end of this synchronous evaluation. */
 evaluateChecked(resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshot:CommerceWorkflowSnapshotHandleV1):Readonly<{
   handle:CommerceWorkflowStepArgumentsHandleV1;inspection:CommerceWorkflowStepArgumentsInspectionV1;
   selectionInspection:ReturnType<CommerceWorkflowResumeSelectorV1['inspectSelection']>;
   snapshotInspection:ReturnType<CommerceWorkflowSnapshotOwnerV1['recheck']>}>;
 inspect(handle:CommerceWorkflowStepArgumentsHandleV1):CommerceWorkflowStepArgumentsInspectionV1;
 assertCurrent():void;dispose():void;
}

/** Materializes only the original identity native calls present inside the
 * checked step arguments. Directory is an existing absolute component output. */
export async function createCommerceWorkflowStepArgumentsOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 calls:CommerceIdentityCallOwner,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,directory:string,
):Promise<CommerceWorkflowStepArgumentsOwnerV1> {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);assertCommerceIdentityCallOwner(calls);
 const selected=binding.inspect(),workflow=selected.workflow,checked=semantics.inspect(semantic);
 if(checked.source_capture_sha256!==selected.source_capture_sha256)
  bad('ForeignOwner','Workflow source and semantic custody differ');
 const plan=checked.workflows.find(p=>p.workflow.module+'.'+p.workflow.name===workflow.name);
 if(!plan||plan.steps.length!==workflow.steps.length)bad('InvalidContract','original Workflow role plan required');
 const original=plan as WorkflowContractV1;
 for(let i=0;i<workflow.steps.length;i++){
  const actual=workflow.steps[i]!,prior=original.steps[i]!;
  if(actual.name!==prior.name||actual.kind!==prior.kind)bad('InvalidContract','source step order differs from checked role plan');
  if(actual.kind==='remote'&&prior.kind==='remote'&&
   (actual.call.entry!==prior.call.entry||actual.call.target!==prior.call.target||actual.call.role!==prior.call.role||
    dataDigest(actual.call.arguments.map(a=>a.parameter))!==dataDigest(prior.call.arguments.map(a=>a.parameter))))
   bad('InvalidContract','source call differs from checked role plan');
 }
 const domainValue=calls.sourceDomain();
 if(domainValue.source_capture_sha256!==selected.source_capture_sha256)bad('ForeignOwner','native call source differs from Workflow');
 const enums=new Map(domainValue.contract.values.enums.map(e=>[e.name,e]));
 const bindings=new Map<string,CommerceIdentityCallHandle>();
 let nodes=0;
 const admit=(v:unknown,p:string,depth=0):void=>{
  if(++nodes>65536||depth>64)bad('ResourceLimit','bounded source argument expression required');
  const e=expression(v),op=field(e,'op');
  switch(op){
   case 'literal':{const value=field(e,'value'),type=field(e,'type');
    if(field(type,'kind')!=='scalar'&&field(type,'kind')!=='string'&&field(type,'kind')!=='refinement')bad('UnsupportedCapability','source literal type');
    if(typeof value!=='boolean'&&typeof value!=='string')bad('InvalidContract','source literal value');return;}
   case 'var':if(field(e,'name')!=='snapshot')bad('UnsupportedCapability','only original snapshot binding supported');return;
   case 'field':if(typeof field(e,'field')!=='string')bad('InvalidContract','field selector');admit(field(e,'value'),p+'.value',depth+1);return;
   case 'none':return;
   case 'some':case 'require_some':case 'present':admit(field(e,'value'),p+'.value',depth+1);return;
   case 'if':admit(field(e,'condition'),p+'.condition',depth+1);admit(field(e,'then'),p+'.then',depth+1);admit(field(e,'else'),p+'.else',depth+1);return;
   case 'enum_value':for(const [name,value] of entries(field(e,'fields')))admit(value,p+'.fields.'+name,depth+1);return;
   case 'native_observation':{
    if(field(e,'abi')!=='craft.commerce-identity/v1-candidate'||field(e,'custody')!=='required-from-original-native-owner'||
       field(e,'placement')!=='original-source-expression-callsite')bad('UnsupportedCapability','unowned native source call');
    const handle=calls.bind(original,p),native=calls.inspect(handle).observation,args=field(e,'arguments');
    if(!Array.isArray(args)||field(e,'context')!==native.context||field(e,'method')!==native.method||field(e,'source_type')!==native.source_type||
       field(e,'abi')!==native.abi||(args as readonly unknown[]).length!==native.arguments.length)
     bad('InvalidContract','native source-call path/signature mismatch');
    for(let i=0;i<(args as readonly unknown[]).length;i++){
     const a=(args as readonly unknown[])[i],prior=native.arguments[i]!;
     if(field(a,'parameter')!==prior.parameter)bad('InvalidContract','native source parameter mismatch');
     admit(field(a,'value'),p+'.arguments['+i+'].value',depth+1);
    }
    bindings.set(p,handle);return;
   }
   default:bad('UnsupportedCapability','Workflow step argument operator '+String(op)+' requires a generic source evaluator');
  }
 };
 for(let i=0;i<workflow.steps.length;i++){
  const step=workflow.steps[i]!;if(step.kind!=='remote')continue;
  for(let j=0;j<step.call.arguments.length;j++)admit(step.call.arguments[j]!.value.evaluation,
   '$.steps['+i+'].call.arguments['+j+'].value.expression');
 }
 const originalStepPaths=calls.paths(original).filter(p=>p.startsWith('$.steps['));
 if(originalStepPaths.length!==bindings.size||originalStepPaths.some(p=>!bindings.has(p)))
  bad('InvalidContract','original Workflow native step paths differ from checked source');
 const components=createCommerceIdentityComponentOwner(calls,stage,source,domain,baseline);
 const component:CommerceIdentityComponentHandle=await components.materialize([...bindings.values()],directory);
 const owned=new WeakMap<object,CommerceWorkflowStepArgumentsInspectionV1>();let disposed=false;
 const current=()=>{
  if(disposed)bad('DisposedOwner','step argument owner retired');
  binding.assertCurrent();semantics.assertCurrent(semantic);
  components.assertCurrent(component);calls.assertCurrentSet([...bindings.values()]);
 };
 const evalNode=(v:unknown,p:string,snapshot:unknown,limit:{count:number},depth=0):unknown=>{
  if(++limit.count>4096||depth>64)bad('ResourceLimit','source step argument evaluation bound');
  const e=expression(v),op=field(e,'op'),sub=(key:string)=>evalNode(field(e,key),p+'.'+key,snapshot,limit,depth+1);
  switch(op){
   case 'literal':{const value=field(e,'value'),type=field(e,'type');return field(type,'kind')==='scalar'&&field(type,'name')==='UInt64'?BigInt(value as string):value;}
   case 'var':return snapshot;
   case 'field':return field(sub('value'),field(e,'field') as string);
   case 'none':return Object.freeze({kind:'none'});
   case 'some':return Object.freeze({kind:'some',value:sub('value')});
   case 'present':return optional(sub('value')).kind==='some';
   case 'require_some':{const value=optional(sub('value'));return value.kind==='some'?value.value:bad('OptionalAbsent','required source optional absent');}
   case 'if':{const condition=sub('condition');if(typeof condition!=='boolean')bad('InputType','source condition must be Bool');return sub(condition?'then':'else');}
   case 'enum_value':{
    const type=field(e,'type_name'),variant=field(e,'variant');if(typeof type!=='string'||typeof variant!=='string')bad('InvalidContract','source enum selector');
    const definition=enums.get(type as string);if(!definition||!definition.variants.some(x=>x.name===variant))bad('InvalidContract','original enum declaration required');
    const fields=Object.create(null) as Record<string,unknown>;
    for(const [name,value] of entries(field(e,'fields')))fields[name]=evalNode(value,p+'.fields.'+name,snapshot,limit,depth+1);
    return definition!.variants.every(x=>Object.keys(x.fields).length===0)?variant:Object.freeze({kind:variant,fields:Object.freeze(fields)});
   }
   case 'native_observation':{
    const handle=bindings.get(p);if(!handle)bad('ForeignOwner','original native source-call path required');
    const arguments_=field(e,'arguments');if(!Array.isArray(arguments_))bad('InvalidContract','source native arguments required');
    const values=(arguments_ as readonly unknown[]).map((a,i)=>evalNode(field(a,'value'),p+'.arguments['+i+'].value',snapshot,limit,depth+1));
    const result=components.evaluateBoundParameters(component,handle!,values);
    if(!result.ok)bad('ProducerValueRejected','original native identity producer rejected source arguments');
    return result.value;
   }
   default:return bad('UnsupportedCapability','unadmitted Workflow step operator');
  }
 };
 const evaluateChecked=(resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshotHandle:CommerceWorkflowSnapshotHandleV1)=>{
  if(disposed)bad('DisposedOwner','step argument owner retired');
  assertCommerceWorkflowResumeSelectorBrandV1(resume);assertCommerceWorkflowSnapshotOwnerBrandV1(snapshots);
  if(resume.workflow!==workflow.name)bad('ForeignOwner','resume selector belongs to another Workflow');
  // inspectSelection performs the original selection's full currentness check.
  const selectedStep=resume.inspectSelection(selection),witness=snapshots.recheck(snapshotHandle);
  if(selectedStep.outcome!=='selected'||selectedStep.action?.kind!=='step')bad('UnsupportedCapability','selected remote step required');
  if(selectedStep.workflow!==workflow.name||witness.workflow!==workflow.name||
     selectedStep.source_capture_sha256!==selected.source_capture_sha256||witness.source_capture_sha256!==selected.source_capture_sha256||
     selectedStep.order_id!==witness.order_id||selectedStep.worker_id!==witness.worker_id||
     selectedStep.worker_epoch!==witness.worker_epoch||selectedStep.progress_version!==witness.progress_version)
   bad('ForeignOwner','resume selection and original snapshot witness differ');
  const action=selectedStep.action as Extract<typeof selectedStep.action,{kind:'step'|'finish'}>;
  const step=workflow.steps.find(s=>s.name===action.target);
  if(!step||step.kind!=='remote')bad('UnsupportedCapability','selected action is not a remote source step');
  const remote=step as Extract<typeof step,{kind:'remote'}>;
  const i=workflow.steps.indexOf(remote),limit={count:0};
  const args=remote.call.arguments.map((a,j)=>({parameter:a.parameter,value:evalNode(a.value.evaluation,
   '$.steps['+i+'].call.arguments['+j+'].value.expression',witness.value,limit)}));
  current();const inspection=coreFreeze({workflow:workflow.name,source_capture_sha256:selected.source_capture_sha256,
   step:remote.name,entry:remote.call.entry,target:remote.call.target,role:remote.call.role,arguments:args,
   order_id:witness.order_id,worker_id:witness.worker_id,worker_epoch:witness.worker_epoch,
   progress_version:witness.progress_version,
   qualification:'inert-source-selected-step-arguments;entry-auth-codec-and-original-step-journal-required' as const,
   authority_effect:'none' as const});
  const handle=Object.freeze({kind:'original-workflow-step-arguments/v1-candidate' as const});
  owned.set(handle,inspection);return Object.freeze({handle,inspection,
   selectionInspection:selectedStep,snapshotInspection:witness});
 };
 return Object.freeze({evaluate(resume:CommerceWorkflowResumeSelectorV1,selection:CommerceWorkflowResumeSelectionV1,
  snapshots:CommerceWorkflowSnapshotOwnerV1,snapshotHandle:CommerceWorkflowSnapshotHandleV1){
  return evaluateChecked(resume,selection,snapshots,snapshotHandle).handle;
 },evaluateChecked,inspect(handle:CommerceWorkflowStepArgumentsHandleV1){current();const row=handle&&typeof handle==='object'?owned.get(handle):undefined;
  if(!row)bad('ForeignOwner','original step argument handle required');return row!;},
 assertCurrent(){current();},dispose(){current();disposed=true;components.dispose(component);}});
}
