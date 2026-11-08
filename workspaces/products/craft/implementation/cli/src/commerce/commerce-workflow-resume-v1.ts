/** Source-ordered, inert Workflow resume selection. A selection is not a
 * dispatch permit: the step owner must reread the original snapshot and journal.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {types as host} from 'node:util';
import {coreFreeze} from './commerce-core-syntax.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceWorkerContextOwnerV1,type CommerceWorkerContextOwnerV1,type CommerceWorkerContextV1} from './commerce-worker-context-v1.js';
import {claimCommerceWorkflowFreshLocalSuccessorV1,recheckCommerceWorkflowFreshLocalSuccessorV1,type CommerceWorkflowFreshLocalSuccessorV1} from './commerce-workflow-fresh-local-successor-v1.js';
import type {CoreWorkflowAction} from './commerce-core-flow-workflow.js';

export class CommerceWorkflowResumeErrorV1 extends Error {
 readonly code:string;
 constructor(code:string,detail:string){super(detail);this.name='CommerceWorkflowResumeErrorV1';this.code=code;}
}
const bad=(code:string,detail:string):never=>{throw new CommerceWorkflowResumeErrorV1(code,detail);};
type Node=Readonly<Record<string,unknown>>;
const object=(value:unknown):value is Node=>!!value&&typeof value==='object'&&!Array.isArray(value)&&!host.isProxy(value)&&
 (Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
const field=(value:unknown,key:string):unknown=>{
 if(!object(value))return bad('InputType','resume input must be a plain data record');
 const descriptor=Object.getOwnPropertyDescriptor(value,key);
 if(!descriptor||!descriptor.enumerable||!Object.hasOwn(descriptor,'value'))return bad('InputType','resume input lacks '+key);
 return descriptor.value;
};
const node=(value:unknown):Node=>object(value)&&typeof field(value,'op')==='string'?value:bad('UnsupportedCapability','unsupported checked resume expression');
const primitive=(value:unknown):value is string|boolean|bigint=>typeof value==='string'||typeof value==='boolean'||typeof value==='bigint';

export interface CommerceWorkflowResumeSelectionV1 {readonly kind:'source-selected-workflow-resume/v1-candidate'}
export interface CommerceWorkflowResumeInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly order_id:string;
 readonly worker_id:string;readonly worker_epoch:bigint;readonly progress_version:bigint;
 readonly persisted_state:string;readonly source_case_index:number|null;
 readonly action:CoreWorkflowAction|null;
 readonly outcome:'selected'|'suspend-same-persisted-state';
 readonly qualification:'inert-source-ordered-resume-selection;current-original-snapshot-and-step-journal-recheck-required'|'inert-source-fresh-local-successor;current-original-snapshot-and-step-journal-recheck-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowResumeSelectorV1 {
 readonly workflow:string;
 inspectSourceCases():readonly {readonly state:string;readonly guarded:boolean;readonly action:CoreWorkflowAction}[];
 select(snapshot:unknown,context:CommerceWorkerContextV1):CommerceWorkflowResumeSelectionV1;
 selectLocalSuccessor(snapshot:unknown,context:CommerceWorkerContextV1,successor:CommerceWorkflowFreshLocalSuccessorV1):CommerceWorkflowResumeSelectionV1;
 inspectSelection(selection:CommerceWorkflowResumeSelectionV1):CommerceWorkflowResumeInspectionV1;
 assertSelectionCurrent(selection:CommerceWorkflowResumeSelectionV1):void;
 assertCurrent():void;
 dispose():void;
}
const owners=new WeakSet<object>();
/** Brand only. Follow immediately with a private method that checks currentness. */
export function assertCommerceWorkflowResumeSelectorBrandV1(owner:CommerceWorkflowResumeSelectorV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner','original resume selector required');
}
export function assertCommerceWorkflowResumeSelectorV1(owner:CommerceWorkflowResumeSelectorV1):void {
 assertCommerceWorkflowResumeSelectorBrandV1(owner);
 owner.assertCurrent();
}

export function createCommerceWorkflowResumeSelectorV1(
 binding:CommerceWorkflowCoordinationBindingV1,workerOwner:CommerceWorkerContextOwnerV1,
):CommerceWorkflowResumeSelectorV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceWorkerContextOwnerV1(workerOwner);
 const selected=binding.inspect(),workflow=selected.workflow;
 const worker=workflow.contexts.filter(c=>c.binding==='worker');
 if(worker.length!==1||worker[0]!.abi!=='craft.commerce-worker-context/v1-candidate')
  bad('InvalidContract','one checked private WorkerContext binding required');
 if(workflow.resume.length>workflow.defaults.max_transitions_per_resume||workflow.defaults.unhandled_resume!=='suspend-same-persisted-state')
  bad('ResourceLimit','checked resume cases exceed the source bound');
 const cases=workflow.resume.map((entry,index)=>({index,state:entry.state,guard:entry.guard?.evaluation??null,action:entry.action}));
 // Admission is closed over the expressions this implementation can evaluate.
 // A future syntax extension cannot silently turn into a false guard.
 const validate=(value:unknown,depth=0):void=>{
  if(depth>64)bad('ResourceLimit','resume expression depth');
  const e=node(value),op=field(e,'op');
  switch(op){
   case 'literal':{
    const type=field(e,'type');if(field(type,'kind')!=='scalar'||!primitive(field(e,'value')))
     bad('UnsupportedCapability','resume literal must be a checked scalar');
    return;
   }
   case 'var':if(field(e,'name')!=='snapshot')bad('UnsupportedCapability','resume binding requires an original value owner');return;
   case 'field':case 'present':case 'absent':validate(field(e,'value'),depth+1);return;
   case 'unary':if(field(e,'operator')!=='not')bad('UnsupportedCapability','resume unary operator');validate(field(e,'value'),depth+1);return;
   case 'binary':{
    if(!['eq','and','or','lt','lte','gt','gte'].includes(String(field(e,'operator'))))
     bad('UnsupportedCapability','resume binary operator');
    validate(field(e,'left'),depth+1);validate(field(e,'right'),depth+1);return;
   }
   case 'native_observation':{
    if(field(e,'context')!=='worker'||field(e,'source_type')!==worker[0]!.source_type||field(e,'abi')!==worker[0]!.abi||
       field(e,'custody')!=='required-from-original-native-owner'||field(e,'placement')!=='original-source-expression-callsite')
     bad('InvalidContract','resume native call lacks the original WorkerContext binding');
    const args=field(e,'arguments');if(!Array.isArray(args)||args.length>4)bad('InvalidContract','bounded worker method arguments required');
    for(const argument of args as readonly unknown[])validate(field(argument,'value'),depth+1);
    const method=field(e,'method');
    if(!['owns','isOrdersWorker','provesVacantOrQuiescentPredecessor','provesNeverDispatched'].includes(String(method)))
     bad('UnsupportedCapability','unknown private worker method in resume guard');
    if((args as readonly unknown[]).length!==({owns:2,isOrdersWorker:0,provesVacantOrQuiescentPredecessor:2,provesNeverDispatched:1} as Record<string,number>)[String(method)])
     bad('InvalidContract','private worker method arity differs from its native ABI');
    return;
   }
   case 'private_context':{
    if(field(e,'binding')!=='worker'||field(e,'source_type')!==worker[0]!.source_type||field(e,'abi')!==worker[0]!.abi||
       field(e,'custody')!=='required-from-original-native-owner'||field(e,'public_constructor')!==false)
     bad('InvalidContract','foreign private context in resume guard');
    return;
   }
   default:bad('UnsupportedCapability','resume expression operator '+String(op)+' is not executable');
  }
 };
 for(const entry of cases)if(entry.guard)validate(entry.guard);
 const selections=new WeakMap<object,{inspection:CommerceWorkflowResumeInspectionV1;context:CommerceWorkerContextV1;successor?:CommerceWorkflowFreshLocalSuccessorV1}>();
 let disposed=false;
 const current=()=>{
  if(disposed)bad('DisposedOwner','resume selector retired');
  binding.assertCurrent();workerOwner.assertCurrent();
  const now=binding.inspect();
  if(now.workflow.name!==workflow.name||now.source_capture_sha256!==selected.source_capture_sha256)
   bad('StaleOwner','checked Workflow source changed');
 };
 const evaluate=(expression:unknown,snapshot:unknown,context:CommerceWorkerContextV1,limit:{count:number},depth=0):unknown=>{
  if(++limit.count>4096||depth>64)bad('ResourceLimit','resume expression evaluation bound');
  const e=node(expression),op=field(e,'op'),sub=(key:string)=>evaluate(field(e,key),snapshot,context,limit,depth+1);
  switch(op){
   case 'literal':{
    const t=field(e,'type'),value=field(e,'value');
    if(!object(t)||field(t,'kind')!=='scalar')bad('UnsupportedCapability','resume literal type');
    if(field(t,'name')==='UInt64'){if(typeof value!=='string'||!/^\d+$/.test(value))bad('InputType','UInt64 literal');return BigInt(value as string);}
    if(!primitive(value))bad('InputType','scalar resume literal');return value;
   }
   case 'var':return field(e,'name')==='snapshot'?snapshot:bad('UnsupportedCapability','unavailable resume binding');
   case 'field':return field(sub('value'),String(field(e,'field')));
   case 'present':case 'absent':{
    const value=sub('value'),kind=field(value,'kind');
    if(kind!=='some'&&kind!=='none')bad('InputType','checked optional value required');
    if(kind==='none'&&Object.keys(value as Node).length!==1||kind==='some'&&(!Object.hasOwn(value as Node,'value')||Object.keys(value as Node).length!==2))
     bad('InputType','exact optional value required');
    return op==='present'?kind==='some':kind==='none';
   }
   case 'unary':{if(field(e,'operator')!=='not')bad('UnsupportedCapability','resume unary operator');const value=sub('value');if(typeof value!=='boolean')bad('InputType','Boolean guard required');return !value;}
   case 'binary':{
    const operator=field(e,'operator'),left=sub('left');
    if(operator==='and'||operator==='or'){
     if(typeof left!=='boolean')bad('InputType','Boolean guard required');
     if(operator==='and'&&!left||operator==='or'&&left)return left;
     const right=sub('right');if(typeof right!=='boolean')bad('InputType','Boolean guard required');return right;
    }
    const right=sub('right');
    if(!primitive(left)||typeof left!==typeof right)bad('InputType','comparable scalar guard values required');
    if(operator==='eq')return left===right;
    if(typeof left!=='bigint'||typeof right!=='bigint')bad('InputType','ordered UInt64 guard values required');
    if(operator==='lt')return (left as bigint)<(right as bigint);if(operator==='lte')return (left as bigint)<=(right as bigint);
    if(operator==='gt')return (left as bigint)>(right as bigint);if(operator==='gte')return (left as bigint)>=(right as bigint);
    bad('UnsupportedCapability','resume binary operator');
   }
   case 'private_context':return context;
   case 'native_observation':{
    const args=field(e,'arguments') as readonly Node[],values=args.map(arg=>evaluate(field(arg,'value'),snapshot,context,limit,depth+1));
    let result:unknown;switch(field(e,'method')){
     case 'isOrdersWorker':if(values.length!==0)bad('InputType','worker method arity');result=context.isOrdersWorker();break;
     case 'owns':if(values.length!==2||typeof values[1]!=='bigint')bad('InputType','worker method arguments');result=context.owns(values[0] as Parameters<CommerceWorkerContextV1['owns']>[0],values[1] as bigint);break;
     case 'provesVacantOrQuiescentPredecessor':if(values.length!==2||typeof values[1]!=='bigint')bad('InputType','worker method arguments');result=context.provesVacantOrQuiescentPredecessor(values[0] as Parameters<CommerceWorkerContextV1['provesVacantOrQuiescentPredecessor']>[0],values[1] as bigint);break;
     case 'provesNeverDispatched':if(values.length!==1||typeof values[0]!=='string')bad('InputType','worker method arguments');result=context.provesNeverDispatched(values[0] as string);break;
     default:bad('UnsupportedCapability','unknown private worker method');
    }
    if(typeof result!=='boolean')bad('InputType','worker observation must be Boolean');return result;
   }
   default:bad('UnsupportedCapability','resume expression operator unavailable');
  }
 };
 const owner:CommerceWorkflowResumeSelectorV1=Object.freeze({workflow:workflow.name,
  inspectSourceCases(){current();return coreFreeze(cases.map(entry=>({state:entry.state,guarded:entry.guard!==null,action:entry.action})));},
  select(snapshot:unknown,context:CommerceWorkerContextV1){
   current();workerOwner.assertContextCurrent(context);
   const claim=workerOwner.inspectContext(context);
   if(claim.workflow!==workflow.name||claim.source_capture_sha256!==selected.source_capture_sha256||!claim.progress_claim_qualified)
    bad('ForeignOwner','committed progress claim for this Workflow required');
   const order=field(snapshot,'order'),progress=field(snapshot,'progress'),orderId=field(order,'id'),progressOrderId=field(progress,'orderId');
   const state=field(progress,'state'),version=field(progress,'version'),epoch=field(progress,'workerEpoch'),progressOwner=field(progress,'workerOwner');
   if(typeof orderId!=='string'||orderId!==claim.order_id||progressOrderId!==orderId||typeof state!=='string'||
      typeof version!=='bigint'||version<1n||typeof epoch!=='bigint'||epoch!==claim.worker_epoch)
    bad('ForeignOwner','snapshot data differs from the committed worker claim');
   if(!object(progressOwner)||field(progressOwner,'kind')!=='some'||typeof field(progressOwner,'value')!=='string'||
      Object.keys(progressOwner).length!==2)
    bad('InputType','exact persisted worker owner value required');
   workerOwner.assertOrder(context,orderId as string);
   if(!context.owns(progressOwner as Parameters<CommerceWorkerContextV1['owns']>[0],epoch as bigint))
    bad('ForeignOwner','snapshot progress is not owned by this original worker');
   const budget={count:0};let chosen:typeof cases[number]|null=null;
   for(const entry of cases){if(entry.state!==state)continue;
    if(entry.guard===null){chosen=entry;break;}
    const result=evaluate(entry.guard,snapshot,context,budget);
    if(typeof result!=='boolean')bad('InputType','resume guard must return Boolean');
    if(result){chosen=entry;break;}
   }
   const inspection:CommerceWorkflowResumeInspectionV1=coreFreeze({workflow:workflow.name,source_capture_sha256:selected.source_capture_sha256,
    order_id:orderId as string,worker_id:claim.worker_id,worker_epoch:claim.worker_epoch,progress_version:version as bigint,persisted_state:state as string,
    source_case_index:chosen?.index??null,action:chosen?.action??null,outcome:chosen?'selected':'suspend-same-persisted-state',
    qualification:'inert-source-ordered-resume-selection;current-original-snapshot-and-step-journal-recheck-required',authority_effect:'none'});
   const handle:CommerceWorkflowResumeSelectionV1=Object.freeze({kind:'source-selected-workflow-resume/v1-candidate'});
   selections.set(handle,{inspection,context});return handle;
  },
  selectLocalSuccessor(snapshot:unknown,context:CommerceWorkerContextV1,successor:CommerceWorkflowFreshLocalSuccessorV1){
   current();const handle:CommerceWorkflowResumeSelectionV1=Object.freeze({kind:'source-selected-workflow-resume/v1-candidate'});
   const local=claimCommerceWorkflowFreshLocalSuccessorV1(successor,binding,workerOwner,context,snapshot,handle);
   const inspection:CommerceWorkflowResumeInspectionV1=coreFreeze({workflow:local.workflow,source_capture_sha256:local.source_capture_sha256,
    order_id:local.order_id,worker_id:local.worker_id,worker_epoch:local.worker_epoch,progress_version:local.progress_version,persisted_state:local.persisted_state,
    source_case_index:null,action:{kind:'step' as const,target:local.next_step},outcome:'selected' as const,
    qualification:'inert-source-fresh-local-successor;current-original-snapshot-and-step-journal-recheck-required' as const,authority_effect:'none' as const});
   selections.set(handle,{inspection,context,successor});return handle;
  },
  inspectSelection(handle:CommerceWorkflowResumeSelectionV1){owner.assertSelectionCurrent(handle);return selections.get(handle)!.inspection;},
  assertSelectionCurrent(handle:CommerceWorkflowResumeSelectionV1){current();const row=handle&&typeof handle==='object'?selections.get(handle):undefined;
   if(!row)bad('ForeignOwner','original source-selected resume handle required');
   if(row!.successor)recheckCommerceWorkflowFreshLocalSuccessorV1(row!.successor,handle);
   workerOwner.assertContextCurrent(row!.context);
   const claim=workerOwner.inspectContext(row!.context),view=row!.inspection;
   if(claim.workflow!==view.workflow||claim.source_capture_sha256!==view.source_capture_sha256||claim.order_id!==view.order_id||
      claim.worker_id!==view.worker_id||claim.worker_epoch!==view.worker_epoch||!claim.progress_claim_qualified)
    bad('StaleOwner','original WorkerContext no longer matches the resume selection');
  },
  assertCurrent:current,dispose(){disposed=true;},
 });
 owners.add(owner);current();return owner;
}
