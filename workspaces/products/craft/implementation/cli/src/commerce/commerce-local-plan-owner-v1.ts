/** Original source-derived local read/Operation/transaction plan custody.
 * Plans do not execute effects or establish native commit/resource evidence.
 * Open Questions: docs/COMMERCE-LOCAL-PLANS-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCoreCommerceStageSourceOwner,createCoreCommerceSemanticStageComponent,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {createCommercePureCallOwner,type CommercePureCallOwner,type CommercePureCallHandle} from './commerce-computation-call-owner.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {ReadPlanV1,EffectPlanV1,TransactionPlanV1,TransactionStepV1,RecordDefinitionV1,SourceIdentityV1,SourceSpanV1} from './commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url));
const code=pinCoreImplementation(import.meta.url,['commerce-core-source-owner'+ext,'commerce-core-semantic-owner'+ext,'commerce-core-stage-owner'+ext,'commerce-core-physical'+ext,'commerce-core-syntax'+ext,'commerce-computation-domain'+ext,'commerce-computation-call-owner'+ext,'commerce-data-v1'+ext,'../profile-engine/contracts'+ext]);
const where={path:'application.alch',start:0,end:0};
export interface CommerceLocalReadHandleV1 {readonly kind:'original-commerce-local-read-plan/v1-candidate'}
export interface CommerceLocalOperationHandleV1 {readonly kind:'original-commerce-local-operation-plan/v1-candidate'}
export interface CommerceLocalTransactionHandleV1 {readonly kind:'original-commerce-local-transaction-plan/v1-candidate'}
export interface CommerceLocalMutationClosureV1 {
 readonly path:string;readonly operation:'create'|'update'|'record-event';readonly target:string;
 readonly source:SourceIdentityV1;readonly span:SourceSpanV1;readonly record:RecordDefinitionV1;
 readonly assigned_fields:readonly string[];readonly original_row_required:boolean;
 readonly expected_version_required:boolean;readonly next_version_check:'original-row+expected-version+exact-one-increment-before-write'|'not-applicable';
}
export interface CommerceLocalTransactionInspectionV1 {
 readonly path:string;readonly plan:TransactionPlanV1;readonly mutations:readonly CommerceLocalMutationClosureV1[];
 readonly handler_execution:'original-native-disposition-required;never-label-inferred';
 readonly provisional_aliases:'escape-only-after-original-commit';readonly authority_effect:'none';
}
export interface CommerceLocalOperationInspectionV1 {
 readonly operation:string;readonly source:SourceIdentityV1;readonly span:SourceSpanV1;
 readonly source_capture_sha256:string;readonly semantic_executable_sha256:string;readonly code_epoch_sha256:string;
 readonly plan:EffectPlanV1;readonly plan_sha256:string;readonly pure_call_paths:readonly string[];
 readonly transactions:readonly CommerceLocalTransactionInspectionV1[];
 readonly execution:'not-performed';readonly invocation_protocol:'qualified-async-outcome-required-from-native-runtime';
 readonly qualification:'original-source-checked-local-plan-only;not-native-effect-or-application-acceptance';readonly authority_effect:'none';
}
export interface CommerceLocalReadInspectionV1 {
 readonly query:string;readonly source:SourceIdentityV1;readonly span:SourceSpanV1;readonly source_capture_sha256:string;
 readonly semantic_executable_sha256:string;readonly code_epoch_sha256:string;readonly plan:ReadPlanV1;readonly plan_sha256:string;
 readonly execution:'not-performed';readonly qualification:'original-source-checked-local-read-only;not-store-row-or-result-custody';readonly authority_effect:'none';
}
export interface CommerceLocalPlanOwnerV1 {
 bindRead(id:string):CommerceLocalReadHandleV1;checkRead(plan:ReadPlanV1):CommerceLocalReadHandleV1;
 inspectRead(handle:CommerceLocalReadHandleV1):CommerceLocalReadInspectionV1;
 bindOperation(id:string):CommerceLocalOperationHandleV1;checkOperation(plan:EffectPlanV1):CommerceLocalOperationHandleV1;
 inspectOperation(handle:CommerceLocalOperationHandleV1):CommerceLocalOperationInspectionV1;
 bindTransaction(operation:CommerceLocalOperationHandleV1,path:string):CommerceLocalTransactionHandleV1;
 inspectTransaction(handle:CommerceLocalTransactionHandleV1):CommerceLocalTransactionInspectionV1;
 bindPureCall(operation:CommerceLocalOperationHandleV1,path:string):Readonly<{owner:CommercePureCallOwner;handle:CommercePureCallHandle}>;
 assertReadCurrent(handle:CommerceLocalReadHandleV1):void;assertOperationCurrent(handle:CommerceLocalOperationHandleV1):void;
 disposeRead(handle:CommerceLocalReadHandleV1):void;disposeOperation(handle:CommerceLocalOperationHandleV1):void;
 assertParents(parents:Readonly<{sources:CoreCommerceSourceOwner;capture:CoreCommerceSourceCapture;
  semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;
  stage:CoreCommerceStageSourceOwner;source:CommerceSourceHandle;
  domain:CommerceComputationDomainOwner;baseline:CommerceComputationDomainHandle}>):void;
 assertCurrent():void;dispose():void;
}
type ReadState={view:CommerceLocalReadInspectionV1;disposed:boolean};
type OperationState={view:CommerceLocalOperationInspectionV1;calls:Map<string,CommercePureCallHandle>;disposed:boolean};
const owners=new WeakSet<object>();
export function assertCommerceLocalPlanOwnerV1(owner:CommerceLocalPlanOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original local plan owner required');owner.assertCurrent();}
export function createCommerceLocalPlanOwnerV1(sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle):CommerceLocalPlanOwnerV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);code.assertCurrent();semantics.assertSource(semantic,capture);
 const captured=sources.inspect(capture),checked=semantics.inspect(semantic),staged=stage.inspect(source),values=domain.inspect(baseline);
 if(captured.capture_sha256!==checked.source_capture_sha256||captured.capture_sha256!==staged.source_sha256||captured.capture_sha256!==values.source_capture_sha256)fail('ForeignOwner',where,'all local plan parents must retain the same original source capture');
 const component=createCoreCommerceSemanticStageComponent(stage,source),calls=createCommercePureCallOwner(stage,source,domain,baseline),modules=stage.moduleContracts(source);
 let disposed=false;const reads=new WeakMap<object,ReadState>(),operations=new WeakMap<object,OperationState>(),transactions=new WeakMap<object,{parent:OperationState;view:CommerceLocalTransactionInspectionV1}>(),allOperations=new Set<OperationState>();
 const current=()=>{if(disposed)fail('DisposedOwner',where,'local plan owner disposed');code.assertCurrent();
  // The semantic check validates the explicit capture; the domain check
  // validates its separate stage capture. Both distinct handles stay live.
  semantics.assertSource(semantic,capture);domain.assertCurrent(baseline);};
 const declaration=(id:string)=>{const module=modules.find(m=>m.declarations.some(d=>d.selector.module+'.'+d.selector.name===id)),row=module?.declarations.find(d=>d.selector.module+'.'+d.selector.name===id);if(!module||!row)fail('UnknownReference',where,'original declaration/source/span required');return {source:module.source,span:row.span};};
 const readCurrent=(h:CommerceLocalReadHandleV1)=>{current();const s=h&&typeof h==='object'?reads.get(h):undefined;if(!s)fail('ForeignOwner',where,'read belongs to another owner');if(s.disposed)fail('DisposedOwner',where,'read plan disposed');return s;};
 const operationCurrent=(h:CommerceLocalOperationHandleV1)=>{current();const s=h&&typeof h==='object'?operations.get(h):undefined;if(!s)fail('ForeignOwner',where,'Operation belongs to another owner');if(s.disposed)fail('DisposedOwner',where,'Operation plan disposed');for(const c of s.calls.values())calls.assertCurrent(c);return s;};
 const transactionViews=(plan:EffectPlanV1):readonly CommerceLocalTransactionInspectionV1[]=>{
  const out:CommerceLocalTransactionInspectionV1[]=[];let nodes=0;
  const record=(target:string)=>{const r=values.contract.values.records.find(r=>r.name===target);if(!r)fail('UnknownReference',where,'original mutation record type absent');return r;};
  const collect=(body:readonly TransactionStepV1[],p:string,participants:readonly string[],mutations:CommerceLocalMutationClosureV1[])=>{
   if(++nodes>65536||p.length>8192)fail('ResourceLimit',where,'finite transaction source layout required');
   body.forEach((step,i)=>{const at=p+'['+i+']';if(step.kind==='mutation'){
    const r=record(step.target),names=step.fields.map(f=>f.name),fields=Object.keys(r.fields),update=step.operation==='update';
    if(new Set(names).size!==names.length||names.some(n=>!fields.includes(n))||!update&&names.length!==fields.length)fail('MissingMapping',where,'exact declared create/Event fields or unique update fields required');
    if(step.operation==='record-event'?r.role!=='Event':r.role!=='Entity'||!participants.includes(step.target))fail('InvalidContract',where,'mutation must use actual declared Event or local atomic Entity participant');
    const versioned=update&&r.entity!==null&&r.entity.version!==null;if(update&&(!step.key||!step.expected_version||step.original_row!=='required-for-exact-key-and-store'))fail('MissingMapping',where,'update requires original row/key/expected version');
    if(versioned&&(!names.includes(r.entity!.version!)||step.version_validation!=='original-row+expected-version+exact-one-increment-before-write'))fail('MissingMapping',where,'versioned update requires explicit next-version validation');
    mutations.push(coreFreeze({path:at,operation:step.operation,target:step.target,...declaration(step.target),record:r,assigned_fields:names,original_row_required:update,expected_version_required:update,next_version_check:step.version_validation}));
   }else if(step.kind==='for')collect(step.body,at+'.body',participants,mutations);else if(step.kind==='conditional'){collect(step.then,at+'.then',participants,mutations);collect(step.otherwise,at+'.otherwise',participants,mutations);}});
  };
  const walk=(v:unknown,p:string)=>{if(!v||typeof v!=='object')return;if(++nodes>65536||p.length>8192)fail('ResourceLimit',where,'finite Operation layout required');if(Array.isArray(v)){v.forEach((x,i)=>walk(x,p+'['+i+']'));return;}const row=v as Record<string,unknown>;
   if(Array.isArray(row.participants)&&Array.isArray(row.body)&&Array.isArray(row.handlers)&&Array.isArray(row.native_requirements)){
    const t=row as unknown as TransactionPlanV1,mutations:CommerceLocalMutationClosureV1[]=[];collect(t.body,p+'.body',t.participants,mutations);out.push(coreFreeze({path:p,plan:t,mutations,handler_execution:'original-native-disposition-required;never-label-inferred',provisional_aliases:'escape-only-after-original-commit',authority_effect:'none'}));return;
   }for(const [key,value]of Object.entries(row))walk(value,p+'.'+key);
  };walk(plan,'$');return coreFreeze(out);
 };
 const bindRead=(proposal:ReadPlanV1):CommerceLocalReadHandleV1=>{current();const inert=captureJson(proposal)as unknown as ReadPlanV1,result=component.checkRead(inert,{...values.contract.values,root:inert.output});if(!result.ok){const d=result.diagnostics[0]!;fail(d.code,d,d.message);}const plan=result.value;if(plan.kind!=='local')fail('UnsupportedCapability',where,'native/delegated read producer joins belong to their original owners');const id=plan.query.module+'.'+plan.query.name,view:CommerceLocalReadInspectionV1=coreFreeze({query:id,...declaration(id),source_capture_sha256:captured.capture_sha256,semantic_executable_sha256:checked.executable_sha256,code_epoch_sha256:code.sha256,plan,plan_sha256:dataDigest(plan),execution:'not-performed',qualification:'original-source-checked-local-read-only;not-store-row-or-result-custody',authority_effect:'none'}),h=Object.freeze({kind:'original-commerce-local-read-plan/v1-candidate' as const});reads.set(h,{view,disposed:false});return h;};
 const bindOperation=(proposal:EffectPlanV1):CommerceLocalOperationHandleV1=>{current();const inert=captureJson(proposal)as unknown as EffectPlanV1,result=component.checkEffects(inert,{...values.contract.values,root:inert.result});if(!result.ok){const d=result.diagnostics[0]!;fail(d.code,d,d.message);}const plan=result.value;if(plan.protocol!==null)fail('UnsupportedCapability',where,'native/replay conformance protocols cannot become local invocable plans');const id=plan.operation.module+'.'+plan.operation.name,view:CommerceLocalOperationInspectionV1=coreFreeze({operation:id,...declaration(id),source_capture_sha256:captured.capture_sha256,semantic_executable_sha256:checked.executable_sha256,code_epoch_sha256:code.sha256,plan,plan_sha256:dataDigest(plan),pure_call_paths:calls.paths(plan),transactions:transactionViews(plan),execution:'not-performed',invocation_protocol:'qualified-async-outcome-required-from-native-runtime',qualification:'original-source-checked-local-plan-only;not-native-effect-or-application-acceptance',authority_effect:'none'}),h=Object.freeze({kind:'original-commerce-local-operation-plan/v1-candidate' as const}),s:OperationState={view,calls:new Map(),disposed:false};operations.set(h,s);allOperations.add(s);return h;};
 const retire=(s:OperationState)=>{s.disposed=true;for(const c of s.calls.values()){try{calls.dispose(c);}catch{/* A stale source already revokes the pure handle. No native resource exists here. */}}s.calls.clear();allOperations.delete(s);};
 const owner:CommerceLocalPlanOwnerV1=Object.freeze({bindRead(id:string){current();const plan=checked.reads.find(r=>r.query.module+'.'+r.query.name===id);if(!plan)fail('UnknownReference',where,'original Query absent');return bindRead(plan);},checkRead:bindRead,inspectRead(h:CommerceLocalReadHandleV1){return readCurrent(h).view;},bindOperation(id:string){current();const plan=checked.effects.find(r=>r.operation.module+'.'+r.operation.name===id);if(!plan)fail('UnknownReference',where,'original Operation absent');return bindOperation(plan);},checkOperation:bindOperation,inspectOperation(h:CommerceLocalOperationHandleV1){return operationCurrent(h).view;},
  bindTransaction(h:CommerceLocalOperationHandleV1,p:string){const s=operationCurrent(h),view=s.view.transactions.find(t=>t.path===p);if(!view)fail('UnknownReference',where,'original nested transaction path required');const t=Object.freeze({kind:'original-commerce-local-transaction-plan/v1-candidate' as const});transactions.set(t,{parent:s,view});return t;},inspectTransaction(h:CommerceLocalTransactionHandleV1){current();const t=h&&typeof h==='object'?transactions.get(h):undefined;if(!t)fail('ForeignOwner',where,'original local transaction handle required');if(t.parent.disposed)fail('DisposedOwner',where,'parent Operation disposed');return t.view;},
  bindPureCall(h:CommerceLocalOperationHandleV1,p:string){const s=operationCurrent(h);if(!s.view.pure_call_paths.includes(p))fail('UnknownReference',where,'original pure-call path required');let c=s.calls.get(p);if(!c){c=calls.bind(s.view.plan,p);s.calls.set(p,c);}return Object.freeze({owner:calls,handle:c});},
  assertReadCurrent(h:CommerceLocalReadHandleV1){readCurrent(h);},assertOperationCurrent(h:CommerceLocalOperationHandleV1){operationCurrent(h);},disposeRead(h:CommerceLocalReadHandleV1){readCurrent(h).disposed=true;},disposeOperation(h:CommerceLocalOperationHandleV1){retire(operationCurrent(h));},
  assertParents(parents:Parameters<CommerceLocalPlanOwnerV1['assertParents']>[0]){current();if(!parents||parents.sources!==sources||parents.capture!==capture||
   parents.semantics!==semantics||parents.semantic!==semantic||parents.stage!==stage||
   parents.source!==source||parents.domain!==domain||parents.baseline!==baseline)
   fail('ForeignOwner',where,'exact original local-plan parent owners and handles required');},
  assertCurrent:current,dispose(){if(disposed)return;for(const s of [...allOperations])retire(s);disposed=true;},
 });owners.add(owner);current();return owner;
}
