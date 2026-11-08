/** Original source/entry/typed-input and local-call invocation custody.
 * Business-resource, worker, command and generated-frame custody remain separate.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual,types as host} from 'node:util';
import {dataDigest,captureJson} from '../profile-engine/contracts.js';
import {pinCoreImplementation,pinCorePhysicalCaptures,writeCoreExclusiveFile,type CorePhysicalFile} from './commerce-core-physical.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {generateCommerceValueCodecBundle} from './commerce-value-codec-generation.js';
import {evaluateCommerceFlowDataV1} from './commerce-flow-expression-data-v1.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalOperationHandleV1,type CommerceLocalReadHandleV1} from './commerce-local-plan-owner-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1,type CommerceInvocationAuthorizationV1} from './commerce-entry-context-v1.js';
import type {CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';
import type {CommerceServiceStorageOwnerV1,CommerceClaimJournalV1} from './commerce-service-storage-v1.js';
import type {CommerceWorkerContextOwnerV1,CommerceWorkerContextV1} from './commerce-worker-context-v1.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceWorkflowWorkerStepAdmissionV1} from './commerce-workflow-worker-step-admission-v1.js';
import {deriveCommerceWorkflowWorkerCommandIdentityV1} from './commerce-workflow-worker-command-identity-v1.js';
import {inspectCommerceWorkflowAnyObservationAdmissionV1,type CommerceWorkflowAnyObservationAdmissionV1} from './commerce-workflow-observation-admission-any-v1.js';
import type {CommerceWorkflowObservationCommitBindingV1} from './commerce-workflow-observation-commit-binding-v1.js';
import {createCommerceEntryGuardPureOwnerV1,type CommerceEntryGuardPureOwnerV1} from './commerce-entry-guard-pure-v1.js';
import type {CommerceWorkflowProtectedCallBindingV1} from './commerce-workflow-protected-call-binding-v1.js';
import type {EffectPlanV1,ReadPlanV1,OperationCallV1,FlowExprV1,BinderV1,ValueTypeV1,EntryContractV1,RoleSelectorV1} from './commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-core-physical'+ext,'commerce-core-stage-owner'+ext,'commerce-computation-domain'+ext,'commerce-value-codec-generation'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-entry-context-v1'+ext,'commerce-workflow-coordination-binding-v1'+ext,'commerce-workflow-worker-step-admission-v1'+ext,'commerce-workflow-worker-command-identity-v1'+ext,'commerce-workflow-observation-admission-any-v1'+ext,'commerce-entry-guard-pure-v1'+ext,'commerce-flow-expression-data-v1'+ext,'../profile-engine/contracts'+ext]);
export class CommerceSourceInvocationErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceSourceInvocationErrorV1';}}
function bad(code:string):never {throw new CommerceSourceInvocationErrorV1(code);}
function closed(value:unknown,keys:readonly string[]):asserts value is Readonly<Record<string,CommerceNativeValue>> {
 if(!value||typeof value!=='object'||Array.isArray(value)||host.isProxy(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))bad('InputType');
 const ds=Object.getOwnPropertyDescriptors(value),names=Reflect.ownKeys(value);
 if(names.length!==keys.length||names.some(k=>typeof k!=='string'||!keys.includes(k))||keys.some(k=>!ds[k]?.enumerable||!Object.hasOwn(ds[k]!,'value')))bad('InputType');
}
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const x of Object.values(v))freeze(x);Object.freeze(v);}return v;};
type Target={role:'Operation';handle:CommerceLocalOperationHandleV1;plan:EffectPlanV1}|{role:'Query';handle:CommerceLocalReadHandleV1;plan:Extract<ReadPlanV1,{kind:'local'}>};
type WorkerEvidence={storage:CommerceServiceStorageOwnerV1;binding:CommerceWorkflowCoordinationBindingV1;journal:CommerceClaimJournalV1|null;protectedCall:CommerceWorkflowProtectedCallBindingV1|null;observation:CommerceWorkflowAnyObservationAdmissionV1|null;owner:CommerceWorkerContextOwnerV1;context:CommerceWorkerContextV1;transactionFinished:boolean};
type State={target:Target;entry:EntryContractV1;root:CommerceInvocationAuthorizationV1;parent:State|null;path:string|null;parameters:Readonly<Record<string,CommerceNativeValue>>;input_sha256:string;depth:number;retired:boolean;worker:WorkerEvidence|null};
export interface CommerceSourceInvocationOwnerV1 {
 prepareTarget(selector:RoleSelectorV1):void;
 begin(authorization:CommerceInvocationAuthorizationV1,parameters:unknown):CommerceOperationInvocationHandle;
 beginWorker(authorization:CommerceInvocationAuthorizationV1,parameters:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1):Promise<CommerceOperationInvocationHandle>;
 beginWorkerRead(authorization:CommerceInvocationAuthorizationV1,parameters:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1):Promise<CommerceOperationInvocationHandle>;
 beginWorkflowWorkerStep(authorization:CommerceInvocationAuthorizationV1,parameters:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,protectedCall:CommerceWorkflowProtectedCallBindingV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1):CommerceOperationInvocationHandle;
 beginWorkflowObservation(authorization:CommerceInvocationAuthorizationV1,parameters:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,admission:CommerceWorkflowAnyObservationAdmissionV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1):Promise<CommerceOperationInvocationHandle>;
 deriveLocalCall(parent:CommerceOperationInvocationHandle,callPath:string,boundArguments:unknown):CommerceOperationInvocationHandle;
 inspect(invocation:CommerceOperationInvocationHandle):Readonly<{operation:string;role:'Operation'|'Query';service:string;entry:string;source_sha256:string;input_sha256:string;parent_call_path:string|null;depth:number;root_invocation_id:string;argument_custody:'root-exact-authorized-input;local-typed-bound-arguments';actual_business_resource_owners_qualified:false;qualification:'original-entry-source-and-local-call-custody-only;generated-expression-frame-and-business-resource-owners-required';authority_effect:'none'}>;
 parameters(invocation:CommerceOperationInvocationHandle):Readonly<Record<string,CommerceNativeValue>>;
 principalIdentity(invocation:CommerceOperationInvocationHandle):Readonly<{kind:'customer'|'service';id:string;authority_effect:'none'}>;
 operation(invocation:CommerceOperationInvocationHandle):CommerceLocalOperationHandleV1;
 read(invocation:CommerceOperationInvocationHandle):CommerceLocalReadHandleV1;
 context(invocation:CommerceOperationInvocationHandle,sourcePath:string):CommerceNativeValue;
 workerObservation(invocation:CommerceOperationInvocationHandle,sourcePath:string,args:readonly CommerceNativeValue[]):boolean;
 workerCommandIdentity(invocation:CommerceOperationInvocationHandle,transactionPath:string):Readonly<{journal_entry:string;command_id:string;request_fingerprint:string}>|null;
 isWorkflowObservationInvocation(invocation:CommerceOperationInvocationHandle):boolean;
 inspectWorkflowObservationCommitBinding(invocation:CommerceOperationInvocationHandle,transactionPath:string):CommerceWorkflowObservationCommitBindingV1;
 withWorkerTransaction<T>(invocation:CommerceOperationInvocationHandle,storage:CommerceServiceStorageOwnerV1,transactionPath:string,execute:()=>T):T;
 assertTarget(invocation:CommerceOperationInvocationHandle,plans:CommerceLocalPlanOwnerV1,sourceSha:string,target:string):void;
 retire(invocation:CommerceOperationInvocationHandle):void;assertCurrent(invocation?:CommerceOperationInvocationHandle):void;dispose():void;
}
const owners=new WeakSet<object>(),claimedRoots=new WeakSet<object>();
export function isCommerceSourceInvocationOwnerV1(value:unknown):value is CommerceSourceInvocationOwnerV1 {return !!value&&typeof value==='object'&&owners.has(value);}
export function assertCommerceSourceInvocationOwnerV1(owner:CommerceSourceInvocationOwnerV1):void {if(!isCommerceSourceInvocationOwnerV1(owner))bad('ForeignOwner');owner.assertCurrent();}

/** No supplied evaluator, principal projection, business callback or native
 * handle issuer is accepted. All code and contexts come from original owners. */
export async function createCommerceSourceInvocationOwnerV1(stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,plans:CommerceLocalPlanOwnerV1,auth:CommerceEntryContextOwnerV1,directory:string):Promise<CommerceSourceInvocationOwnerV1> {
 assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);assertCommerceLocalPlanOwnerV1(plans);assertCommerceEntryContextOwnerV1(auth);pin.assertCurrent();
 const sourceView=stage.inspect(source),domainView=domain.inspect(baseline),sourceSha=sourceView.source_sha256;
 if(domainView.source_capture_sha256!==sourceSha||auth.inspect().source_sha256!==sourceSha)bad('ForeignSource');
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)bad('OutputPath');
 mkdirSync(directory,{mode:0o700});const files:CorePhysicalFile[]=[],bundle=generateCommerceValueCodecBundle(stage,source,domain,baseline);
 files.push(writeCoreExclusiveFile(path.join(directory,'package.json'),'{"type":"module"}\n'));
 for(const f of bundle.files){files.push(writeCoreExclusiveFile(path.join(directory,f.path),f.text));files.push(writeCoreExclusiveFile(path.join(directory,f.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(f.text)));}
 const physical=pinCorePhysicalCaptures(files);
 const loaded=await import(pathToFileURL(path.join(directory,'values-and-codecs.js')).href),codecs=loaded.createCommerceValueCodecs();
 let disposed=false;const states=new WeakMap<object,State>(),workerTransactions=new WeakMap<State,{workerId:string}>(),schemas=new Map<string,unknown>(),entries=stage.moduleContracts(source).flatMap(m=>m.entries),guardOwners=new Map<string,CommerceEntryGuardPureOwnerV1>();
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();stage.assertCurrent(source);domain.assertCurrent(baseline);plans.assertCurrent();assertCommerceEntryContextOwnerV1(auth);physical.assertCurrent();};
 const targets=new Map<string,Target>();
 const target=(id:string,role:'Operation'|'Query'):Target=>{const key=role+':'+id,cached=targets.get(key);if(cached){if(cached.role==='Operation')plans.assertOperationCurrent(cached.handle);else plans.inspectRead(cached.handle);return cached;}
  if(role==='Operation'){const handle=plans.bindOperation(id),view=plans.inspectOperation(handle);if(view.source_capture_sha256!==sourceSha)bad('ForeignSource');if(view.plan.protocol!==null)bad('ExternalProducerRequired');const result:Target={role,handle,plan:view.plan};targets.set(key,result);return result;}
  const handle=plans.bindRead(id),view=plans.inspectRead(handle);if(view.source_capture_sha256!==sourceSha||view.plan.kind!=='local')bad('UnsupportedQuery');const result:Target={role,handle,plan:view.plan};targets.set(key,result);return result;
 };
 const id=(t:Target)=>t.role==='Operation'?t.plan.operation.module+'.'+t.plan.operation.name:t.plan.query.module+'.'+t.plan.query.name;
 const check=(s:State,observationAdmission=true):ReturnType<typeof auth.inspectInvocation>=>{if(s.retired)bad('RetiredInvocation');if(s.parent)check(s.parent,observationAdmission);const view=auth.inspectInvocation(s.root);if(s.worker){s.worker.binding.assertCurrent();if(!workerTransactions.has(s)&&!s.worker.transactionFinished){if(s.worker.journal)s.worker.storage.assertClaimJournalCurrent(s.worker.journal);if(s.worker.protectedCall)s.worker.protectedCall.recheck();if(observationAdmission&&s.worker.observation)s.worker.observation.assertCurrent();s.worker.owner.assertContextCurrent(s.worker.context);}}if(s.target.role==='Operation')plans.assertOperationCurrent(s.target.handle);else plans.inspectRead(s.target.handle);return view;};
 const checked=(h:CommerceOperationInvocationHandle)=>{current();const s=h&&typeof h==='object'?states.get(h):undefined;if(!s)bad('ForeignInvocation');return {s,v:check(s)};};
 const owned=(h:CommerceOperationInvocationHandle)=>checked(h).s;
 // Immutable source metadata is not a resource/admission or effect witness.
 // Still check exact custody, source, root Auth, worker claim and plan on every
 // access. Full inspections and every context/effect/transaction method above
 // and below retain the original observation admission. No check is cached.
 const metadata=(h:CommerceOperationInvocationHandle)=>{
  current();const s=h&&typeof h==='object'?states.get(h):undefined;
  if(!s)bad('ForeignInvocation');check(s,false);return s;
 };
 const schema=(type:ValueTypeV1)=>{const k=dataDigest(type);let h=schemas.get(k);if(!h){const r=codecs.checkCommerceSchema({...domainView.contract.values,root:type});if(!r.ok)bad('UnsupportedParameterType');h=r.value;schemas.set(k,h);}return h;};
 const copy=(parameters:readonly BinderV1[],input:unknown)=>{closed(input,parameters.map(p=>p.name));const out:Record<string,CommerceNativeValue>=Object.create(null),wire:Record<string,string>=Object.create(null);for(const p of parameters){const r=codecs.copyCommerceValue(schema(p.type),input[p.name]);if(!r.ok)bad('InputType');const e=codecs.encodeCommerceValue(schema(p.type),r.value);if(!e.ok)bad('InputType');out[p.name]=r.value;wire[p.name]=new TextDecoder('utf8',{fatal:true}).decode(e.value);}const text='{'+Object.keys(wire).sort().map(k=>JSON.stringify(k)+':'+wire[k]).join(',')+'}';if(Buffer.byteLength(text)>domainView.contract.limits.max_value_bytes)bad('InputBound');return {parameters:freeze(out),input_sha256:createHash('sha256').update(text).digest('hex')};};
 const mint=(s:State)=>{const h=Object.freeze({kind:'original-source-owned-operation-invocation/v1-candidate'}) as unknown as CommerceOperationInvocationHandle;states.set(h,s);check(s);return h;};
 const atPath=(s:State,p:string)=>{if(typeof p!=='string'||p.length>8192)bad('UnknownSourcePath');const found=new Map<string,unknown>();let n=0;const walk=(v:unknown,at:string,depth:number)=>{if(!v||typeof v!=='object')return;if(++n>65536||depth>128)bad('SourceBound');found.set(at,v);if(Array.isArray(v))v.forEach((x,i)=>walk(x,at+'['+i+']',depth+1));else for(const [k,x]of Object.entries(v))walk(x,at+'.'+k,depth+1);};walk(s.target.plan,'$',0);return found.get(p)??bad('UnknownSourcePath');};
 const owner:CommerceSourceInvocationOwnerV1=Object.freeze({
  prepareTarget(selector:RoleSelectorV1){current();const s=captureJson(selector) as unknown as RoleSelectorV1;closed(s,['module','name','role']);if(typeof s.module!=='string'||typeof s.name!=='string'||!(['Operation','Query'] as string[]).includes(s.role))bad('UnsupportedTarget');target(s.module+'.'+s.name,s.role as 'Operation'|'Query');},
  begin(root:CommerceInvocationAuthorizationV1,input:unknown){current();const v=auth.inspectInvocation(root);if(claimedRoots.has(root))bad('AlreadyAcquired');const entry=entries.find(e=>e.id===v.entry)??bad('UnknownEntry');if(entry.access.worker_lifetime!=='not-applicable')bad('WorkerProducerRequired');const t=target(entry.invokes.module+'.'+entry.invokes.name,entry.invokes.role==='Operation'?'Operation':entry.invokes.role==='Query'?'Query':bad('UnsupportedTarget'));
   if(v.source_sha256!==sourceSha||v.operation!==id(t)||entry.service!==t.plan.service||dataDigest(entry.parameters)!==dataDigest(t.plan.parameters))bad('ForeignInvocation');
   const copied=copy(t.plan.parameters,input);if(copied.input_sha256!==v.input_sha256)bad('ForeignAuthorizedInput');const h=mint({target:t,entry,root,parent:null,path:null,...copied,depth:0,retired:false,worker:null});claimedRoots.add(root);return h;
  },
  async beginWorker(root:CommerceInvocationAuthorizationV1,input:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1){
   current();const storeModule=await import('./commerce-service-storage-v1.js'),workerModule=await import('./commerce-worker-context-v1.js');
   storeModule.assertCommerceServiceStorageOwnerV1(storage);assertCommerceWorkflowCoordinationBindingV1(binding);workerModule.assertCommerceWorkerContextOwnerV1(workerOwner);
   storage.assertClaimJournalCurrent(journal);workerOwner.assertContextCurrent(workerContext);
   const j=storage.inspectClaimJournal(journal),w=workerOwner.inspectContext(workerContext),store=storage.inspect(),workflow=binding.inspect(),v=auth.inspectInvocation(root);
   if(claimedRoots.has(root))bad('AlreadyAcquired');
   const entry=entries.find(e=>e.id===v.entry)??bad('UnknownEntry');
   if(entry.access.worker_lifetime!=='requires-original-local-worker-owner'||entry.access.resource_phase!=='causal-before-invocation'||
    entry.access.principal_kind!=='service'||entry.access.resource_bindings.length!==1||!entry.access.resource_condition)
    bad('WorkerProducerRequired');
   const causal=entry.access.resource_bindings[0]!;
   if(causal.origin.kind!=='workflow-journal'||causal.origin.declaration!==j.workflow||
    causal.selector.split('/').at(-1)!=='original-step-journal'||causal.required_fields.length!==1||causal.required_fields[0]!=='orderId'||
    j.target_entry_id!==entry.id||j.step_name!=='claim'||j.phase!=='Prepared'||
    j.source_capture_sha256!==sourceSha||w.source_capture_sha256!==sourceSha||workflow.source_capture_sha256!==sourceSha||
    j.store_id!==store.store_id||w.store_id!==store.store_id||j.order_id!==w.order_id||
    j.workflow!==w.workflow||j.workflow!==workflow.workflow.name||j.occurrence_id!==w.occurrence_id||j.worker_id!==w.worker_id||j.worker_epoch!==w.worker_epoch||
    store.service!==entry.service||workflow.owner_service!==store.service||
    workflow.workflow.drivers.filter(driver=>driver.kind==='claim'&&driver.call.entry===entry.id&&driver.call.target===entry.invokes.module+'.'+entry.invokes.name).length!==1)
    bad('ForeignWorkerEvidence');
   const t=target(entry.invokes.module+'.'+entry.invokes.name,'Operation');
   if(v.source_sha256!==sourceSha||v.operation!==id(t)||entry.service!==t.plan.service||
    dataDigest(entry.parameters)!==dataDigest(t.plan.parameters)||
    !t.plan.contexts.some(context=>context.binding==='worker'&&context.source_type==='Shop.Values.WorkerContext'))
    bad('ForeignInvocation');
   const copied=copy(t.plan.parameters,input);
   if(copied.input_sha256!==v.input_sha256||copied.parameters.orderId!==j.order_id)bad('ForeignAuthorizedInput');
   const progress=storage.inspectStoredRecord(workflow.workflow.durable_state,0,{orderId:j.order_id});
   if(!progress||typeof progress!=='object'||Array.isArray(progress)||
    (progress as Record<string,unknown>).orderId!==j.order_id||
    (progress as Record<string,unknown>).version!==copied.parameters.expectedProgressVersion)
    bad('StaleWorkerSnapshot');
   let fuel=0;const projection=Object.freeze({orderId:j.order_id}),env=Object.freeze({input:copied.parameters,[causal.name]:projection});
   const allowed=evaluateCommerceFlowDataV1(entry.access.resource_condition.expression,'$.access.resource_condition.expression',env,{
    charge(){if(++fuel>4096)bad('ResourceLimit');},pure(){return bad('UnsupportedWorkerGuard');},native(){return bad('UnsupportedWorkerGuard');},
    context(){return bad('UnsupportedWorkerGuard');},isNullaryEnum(){return false;},
   });
   if(allowed!==true)bad('Forbidden');
   const h=mint({target:t,entry,root,parent:null,path:null,...copied,depth:0,retired:false,worker:{storage,binding,journal,protectedCall:null,observation:null,owner:workerOwner,context:workerContext,transactionFinished:false}});
   claimedRoots.add(root);return h;
  },
  async beginWorkerRead(root:CommerceInvocationAuthorizationV1,input:unknown,storage:CommerceServiceStorageOwnerV1,binding:CommerceWorkflowCoordinationBindingV1,journal:CommerceClaimJournalV1,workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1){
   current();const storeModule=await import('./commerce-service-storage-v1.js'),workerModule=await import('./commerce-worker-context-v1.js');
   storeModule.assertCommerceServiceStorageOwnerV1(storage);assertCommerceWorkflowCoordinationBindingV1(binding);workerModule.assertCommerceWorkerContextOwnerV1(workerOwner);
   storage.assertClaimJournalCurrent(journal);workerOwner.assertContextCurrent(workerContext);
   const j=storage.inspectClaimJournal(journal),w=workerOwner.inspectContext(workerContext),store=storage.inspect(),workflow=binding.inspect(),v=auth.inspectInvocation(root);
   if(claimedRoots.has(root))bad('AlreadyAcquired');
   const entry=entries.find(e=>e.id===v.entry)??bad('UnknownEntry'),snapshot=workflow.workflow.drivers.filter(driver=>driver.kind==='snapshot'),
    claim=workflow.workflow.drivers.filter(driver=>driver.kind==='claim');
   if(entry.invokes.role!=='Query'||entry.access.worker_lifetime!=='requires-original-local-worker-owner'||
    entry.access.resource_phase!=='causal-before-invocation'||entry.access.principal_kind!=='service'||
    entry.access.resource_bindings.length!==1||!entry.access.resource_condition||
    snapshot.length!==1||snapshot[0]!.call.entry!==entry.id||snapshot[0]!.call.target!==entry.invokes.module+'.'+entry.invokes.name||
    claim.length!==1||claim[0]!.call.entry!==j.target_entry_id)
    bad('WorkerProducerRequired');
   const causal=entry.access.resource_bindings[0]!;
   if(causal.origin.kind!=='workflow-journal'||causal.origin.declaration!==j.workflow||
    causal.selector.split('/').at(-1)!=='original-step-journal'||causal.required_fields.length!==1||causal.required_fields[0]!=='orderId'||
    j.step_name!=='claim'||j.phase!=='Prepared'||j.source_capture_sha256!==sourceSha||w.source_capture_sha256!==sourceSha||
    workflow.source_capture_sha256!==sourceSha||j.store_id!==store.store_id||w.store_id!==store.store_id||
    j.order_id!==w.order_id||j.workflow!==w.workflow||j.workflow!==workflow.workflow.name||
    j.occurrence_id!==w.occurrence_id||j.worker_id!==w.worker_id||j.worker_epoch!==w.worker_epoch||
    store.service!==entry.service||workflow.owner_service!==store.service||!w.progress_claim_qualified)
    bad('ForeignWorkerEvidence');
   const t=target(entry.invokes.module+'.'+entry.invokes.name,'Query');
   if(v.source_sha256!==sourceSha||v.operation!==id(t)||entry.service!==t.plan.service||
    dataDigest(entry.parameters)!==dataDigest(t.plan.parameters)||
    !t.plan.contexts.some(context=>context.binding==='worker'&&context.source_type==='Shop.Values.WorkerContext'))
    bad('ForeignInvocation');
   const copied=copy(t.plan.parameters,input);
   if(copied.input_sha256!==v.input_sha256||copied.parameters.orderId!==j.order_id)bad('ForeignAuthorizedInput');
   let fuel=0;const projection=Object.freeze({orderId:j.order_id}),env=Object.freeze({input:copied.parameters,[causal.name]:projection});
   const allowed=evaluateCommerceFlowDataV1(entry.access.resource_condition.expression,'$.access.resource_condition.expression',env,{
    charge(){if(++fuel>4096)bad('ResourceLimit');},pure(){return bad('UnsupportedWorkerGuard');},native(){return bad('UnsupportedWorkerGuard');},
    context(){return bad('UnsupportedWorkerGuard');},isNullaryEnum(){return false;},
   });
   if(allowed!==true)bad('Forbidden');
   const h=mint({target:t,entry,root,parent:null,path:null,...copied,depth:0,retired:false,worker:{storage,binding,journal,protectedCall:null,observation:null,owner:workerOwner,context:workerContext,transactionFinished:false}});
   claimedRoots.add(root);return h;
  },
  beginWorkflowWorkerStep(root:CommerceInvocationAuthorizationV1,input:unknown,storage:CommerceServiceStorageOwnerV1,
   binding:CommerceWorkflowCoordinationBindingV1,protectedCall:CommerceWorkflowProtectedCallBindingV1,
   workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1){
   current();binding.assertCurrent();
   const v=auth.inspectInvocation(root);
   if(claimedRoots.has(root))bad('AlreadyAcquired');
   const entry=entries.find(candidate=>candidate.id===v.entry)??bad('UnknownEntry');
   const call=assertCommerceWorkflowWorkerStepAdmissionV1(entry,sourceSha,protectedCall,storage,workerOwner,workerContext);
   const workflow=binding.inspect();
   if(workflow.workflow.name!==call.workflow||workflow.owner_service!==storage.inspect().service||
    workflow.source_capture_sha256!==sourceSha||
    (entry.invokes.role!=='Operation'&&entry.invokes.role!=='Query'))bad('ForeignWorkerEvidence');
   const t=target(call.target,entry.invokes.role);
   if(v.source_sha256!==sourceSha||v.operation!==id(t)||entry.service!==t.plan.service||
    dataDigest(entry.parameters)!==dataDigest(t.plan.parameters)||
    !t.plan.contexts.some(context=>context.binding==='worker'&&context.source_type==='Shop.Values.WorkerContext'))
    bad('ForeignInvocation');
   const copied=copy(t.plan.parameters,input);
   if(copied.input_sha256!==v.input_sha256||Object.keys(copied.parameters).length!==Object.keys(call.arguments).length||
    Object.keys(copied.parameters).some(name=>!Object.hasOwn(call.arguments,name)||!isDeepStrictEqual(copied.parameters[name],call.arguments[name],{skipPrototype:true}))||
    copied.parameters.orderId!==call.order_id)bad('ForeignAuthorizedInput');
   const progress=storage.inspectStoredRecord(workflow.workflow.durable_state,0,{orderId:call.order_id});
   if(!progress||typeof progress!=='object'||Array.isArray(progress)||
    (progress as Record<string,unknown>).orderId!==call.order_id||
    (progress as Record<string,unknown>).version!==call.progress_version)
    bad('StaleWorkerSnapshot');
   const causal=entry.access.resource_bindings[0]!;
   let fuel=0;
   const allowed=evaluateCommerceFlowDataV1(entry.access.resource_condition!.expression,'$.access.resource_condition.expression',
    Object.freeze({input:copied.parameters,[causal.name]:call.causal_projection}),{
     charge(){if(++fuel>4096)bad('ResourceLimit');},pure(){return bad('UnsupportedWorkerGuard');},
     native(){return bad('UnsupportedWorkerGuard');},context(){return bad('UnsupportedWorkerGuard');},isNullaryEnum(){return false;},
    });
   if(allowed!==true)bad('Forbidden');
   const h=mint({target:t,entry,root,parent:null,path:null,...copied,depth:0,retired:false,
    worker:{storage,binding,journal:null,protectedCall,observation:null,owner:workerOwner,context:workerContext,transactionFinished:false}});
   claimedRoots.add(root);return h;
  },
  async beginWorkflowObservation(root:CommerceInvocationAuthorizationV1,input:unknown,storage:CommerceServiceStorageOwnerV1,
   binding:CommerceWorkflowCoordinationBindingV1,admission:CommerceWorkflowAnyObservationAdmissionV1,
   workerOwner:CommerceWorkerContextOwnerV1,workerContext:CommerceWorkerContextV1){
   current();const storeModule=await import('./commerce-service-storage-v1.js'),workerModule=await import('./commerce-worker-context-v1.js');
   storeModule.assertCommerceServiceStorageOwnerV1(storage);workerModule.assertCommerceWorkerContextOwnerV1(workerOwner);
   assertCommerceWorkflowCoordinationBindingV1(binding);workerOwner.assertContextCurrent(workerContext);
   const admitted=inspectCommerceWorkflowAnyObservationAdmissionV1(admission).inspection;
   const v=auth.inspectInvocation(root),store=storage.inspect(),
    workflow=binding.inspect(),worker=workerOwner.inspectContext(workerContext);
   if(claimedRoots.has(root))bad('AlreadyAcquired');
   const entry=entries.find(candidate=>candidate.id===v.entry)??bad('UnknownEntry');
   const causal=entry.access.resource_bindings[0];
   if(entry.id!==admitted.entry_id||entry.service!==store.service||
    entry.invokes.role!=='Operation'||entry.invokes.module+'.'+entry.invokes.name!==admitted.target||
    entry.access.principal_kind!=='service'||entry.access.caller!==workflow.owner_service||
    entry.access.worker_lifetime!=='requires-original-local-worker-owner'||
    entry.access.resource_phase!=='causal-before-invocation'||
    entry.access.resource_bindings.length!==1||!causal||!entry.access.resource_condition||
    causal.origin.kind!=='worker-observation'||causal.origin.declaration!==workflow.workflow.durable_state||
    causal.selector.split('/').at(-1)!=='original-worker-observation'||
    admitted.source_capture_sha256!==sourceSha||workflow.source_capture_sha256!==sourceSha||
    store.source_capture_sha256!==sourceSha||worker.source_capture_sha256!==sourceSha||
    admitted.workflow!==workflow.workflow.name||admitted.store_id!==store.store_id||
    admitted.order_id!==worker.order_id||admitted.worker_id!==worker.worker_id||
    admitted.worker_epoch!==worker.worker_epoch||admitted.occurrence_id!==worker.occurrence_id||
    !worker.progress_claim_qualified)
    bad('ForeignWorkerEvidence');
   const t=target(admitted.target,'Operation');
   if(v.source_sha256!==sourceSha||v.operation!==id(t)||entry.service!==t.plan.service||
    dataDigest(entry.parameters)!==dataDigest(t.plan.parameters)||
    !t.plan.contexts.some(context=>context.binding==='worker'&&context.source_type==='Shop.Values.WorkerContext'))
    bad('ForeignInvocation');
   const copied=copy(t.plan.parameters,input);
   // Source-typed records can use ordinary or null prototypes. Preserve exact
   // data and the authorized canonical hash without treating prototypes as data.
   if(copied.input_sha256!==v.input_sha256||
    Object.keys(copied.parameters).length!==Object.keys(admitted.input).length||
    Object.keys(copied.parameters).some(name=>!Object.hasOwn(admitted.input,name)||
     !isDeepStrictEqual(copied.parameters[name],admitted.input[name as keyof typeof admitted.input],{skipPrototype:true})))
    bad('ForeignAuthorizedInput');
   let guard=guardOwners.get(entry.id);
   if(!guard){guard=createCommerceEntryGuardPureOwnerV1(stage,source,domain,baseline,entry,codecs);guardOwners.set(entry.id,guard);}
   let fuel=0;
   const allowed=evaluateCommerceFlowDataV1(entry.access.resource_condition.expression,
    '$.access.resource_condition.expression',Object.freeze({input:copied.parameters,[causal.name]:admitted.causal_projection}),{
     charge(){if(++fuel>4096)bad('ResourceLimit');},
     pure(path,args){return guard!.evaluate(path,args);},
     native(){return bad('UnsupportedWorkerGuard');},context(){return bad('UnsupportedWorkerGuard');},
     isNullaryEnum(){return false;},
    });
   if(allowed!==true)bad('Forbidden');
   admission.assertCurrent();workerOwner.assertContextCurrent(workerContext);
   const h=mint({target:t,entry,root,parent:null,path:null,...copied,depth:0,retired:false,
    worker:{storage,binding,journal:null,protectedCall:null,observation:admission,
     owner:workerOwner,context:workerContext,transactionFinished:false}});
   claimedRoots.add(root);return h;
  },
  deriveLocalCall(h:CommerceOperationInvocationHandle,p:string,input:unknown){const parent=owned(h);if(parent.worker?.transactionFinished)bad('WorkerTransactionFinished');if(parent.depth>=32)bad('CallDepth');const call=atPath(parent,p) as OperationCallV1;
   if(!call||typeof call!=='object'||!Array.isArray(call.arguments)||!Array.isArray(call.contexts)||!['Operation','Query'].includes(call.role)||typeof call.target!=='string')bad('NotSourceCall');
   if(call.entry!==null||call.authorization!=='original-local-context-forwarding-required')bad('FreshEntryAuthorizationRequired');
   const t=target(call.target,call.role);if(t.plan.service!==parent.target.plan.service)bad('CrossServiceLocalCall');
   if(t.plan.contexts.some(c=>!call.contexts.some(f=>f.parameter===c.binding&&f.source_type===c.source_type&&parent.target.plan.contexts.some(p=>p.binding===f.binding&&p.source_type===f.source_type))))bad('MissingSourceContextForwarding');
   const copied=copy(t.plan.parameters,input);return mint({target:t,entry:parent.entry,root:parent.root,parent,path:p,...copied,depth:parent.depth+1,retired:false,worker:parent.worker});
  },
  inspect(h:CommerceOperationInvocationHandle){const {s,v}=checked(h);return freeze({operation:id(s.target),role:s.target.role,service:s.target.plan.service!,entry:s.entry.id,source_sha256:sourceSha,input_sha256:s.input_sha256,parent_call_path:s.path,depth:s.depth,root_invocation_id:String(v.invocation_id),argument_custody:'root-exact-authorized-input;local-typed-bound-arguments' as const,actual_business_resource_owners_qualified:false as const,qualification:'original-entry-source-and-local-call-custody-only;generated-expression-frame-and-business-resource-owners-required' as const,authority_effect:'none' as const});},
  parameters(h:CommerceOperationInvocationHandle){return metadata(h).parameters;},
  principalIdentity(h:CommerceOperationInvocationHandle){
   const s=owned(h),scope=auth.inspectScope(auth.principalScope(s.root));
   if(scope.kind==='customer'&&s.entry.access.principal_kind==='customer'&&typeof scope.customerId==='string'&&scope.customerId.length)
    return freeze({kind:'customer' as const,id:scope.customerId,authority_effect:'none' as const});
   if(scope.kind==='service'&&s.entry.access.principal_kind==='service'&&typeof scope.serviceId==='string'&&scope.serviceId.length&&scope.serviceId===s.entry.access.caller)
    return freeze({kind:'service' as const,id:scope.serviceId,authority_effect:'none' as const});
   bad('ForeignPrincipal');
  },
  operation(h:CommerceOperationInvocationHandle){const s=metadata(h);if(s.target.role!=='Operation')bad('NotOperation');return s.target.handle;},
  read(h:CommerceOperationInvocationHandle){const s=metadata(h);if(s.target.role!=='Query')bad('NotQuery');return s.target.handle;},
  context(h:CommerceOperationInvocationHandle,p:string){const s=owned(h),node=atPath(s,p) as Extract<FlowExprV1,{op:'private_context'}>;if(node.op!=='private_context')bad('NotSourceContext');
   if(node.source_type==='Shop.Values.WorkerContext'){
    if(!s.worker||s.worker.transactionFinished||node.binding!=='worker'||Object.keys(node.fields).length!==1||!Object.hasOwn(node.fields,'workerId'))bad('NativeContextProducerRequired');
    const workerId=workerTransactions.get(s)?.workerId??s.worker.owner.inspectContext(s.worker.context).worker_id,
     value=codecs.copyCommerceValue(schema(node.fields.workerId!),workerId);
    if(!value.ok)bad('NativeContextProducerRequired');return freeze({workerId:value.value});
   }
   const scope=auth.inspectScope(auth.principalScope(s.root)),expected=node.source_type==='Shop.Values.CustomerContext'?'customer':node.source_type==='Shop.Values.ServiceContext'?'service':bad('NativeContextProducerRequired');if(scope.kind!==expected)bad('ForeignContextKind');const out:Record<string,CommerceNativeValue>=Object.create(null);for(const [name,type]of Object.entries(node.fields)){if(!Object.hasOwn(scope,name))bad('NativeContextProducerRequired');const r=codecs.copyCommerceValue(schema(type),scope[name]);if(!r.ok)bad('NativeContextProducerRequired');out[name]=r.value;}return freeze(out);},
  workerObservation(h:CommerceOperationInvocationHandle,p:string,args:readonly CommerceNativeValue[]){
   const s=owned(h),node=atPath(s,p) as FlowExprV1;
   if(!s.worker||s.worker.transactionFinished||workerTransactions.has(s)||node.op!=='native_observation'||node.context!=='worker'||
    node.source_type!=='Shop.Values.WorkerContext'||node.abi!=='craft.commerce-worker-context/v1-candidate'||
    node.placement!=='original-source-expression-callsite'||node.custody!=='required-from-original-native-owner'||
    !Array.isArray(args)||host.isProxy(args)||args.length!==node.arguments.length)
    bad('NativeContextProducerRequired');
   const context=s.worker.context;
   s.worker.owner.assertContextCurrent(context);
   if(typeof s.parameters.orderId==='string')s.worker.owner.assertOrder(context,s.parameters.orderId);
   if(node.method==='isOrdersWorker'&&args.length===0)return context.isOrdersWorker();
   if(node.method==='provesNeverDispatched'&&args.length===1&&typeof args[0]==='string')return context.provesNeverDispatched(args[0]);
   if((node.method==='owns'||node.method==='provesVacantOrQuiescentPredecessor')&&args.length===2&&typeof args[1]==='bigint'){
    const candidate=args[0],owner=candidate&&typeof candidate==='object'&&!Array.isArray(candidate)&&!host.isProxy(candidate)?candidate as Record<string,unknown>:null;
    if(!owner||!['none','some'].includes(String(owner.kind))||
     (owner.kind==='none'&&Object.keys(owner).length!==1)||
     (owner.kind==='some'&&(Object.keys(owner).length!==2||typeof owner.value!=='string')))
     bad('InputType');
    const workerOwner=owner as {kind:'none'}|{kind:'some';value:string};
    return node.method==='owns'?context.owns(workerOwner,args[1]):context.provesVacantOrQuiescentPredecessor(workerOwner,args[1]);
   }
   bad('NativeContextProducerRequired');
  },
  workerCommandIdentity(h:CommerceOperationInvocationHandle,transactionPath:string){
   const s=owned(h);if(!s.worker)return null;
   if(s.parent!==null||s.depth!==0||s.target.role!=='Operation'||s.worker.transactionFinished)bad('ForeignWorkerEvidence');
   if(s.worker.observation)return null;
   if(s.worker.protectedCall)return deriveCommerceWorkflowWorkerCommandIdentityV1(plans,s.target.handle,s.worker.protectedCall,transactionPath);
   if(!s.worker.journal)bad('ForeignWorkerEvidence');
   const workflow=s.worker.binding.inspect(),journal=s.worker.storage.inspectClaimJournal(s.worker.journal),
    worker=s.worker.owner.inspectContext(s.worker.context),original=plans.inspectOperation(s.target.handle);
   const drivers=workflow.workflow.drivers.filter(driver=>driver.kind==='claim');
   if(drivers.length!==1||drivers[0]!.call.entry!==s.entry.id||drivers[0]!.call.target!==id(s.target)||
    original.transactions.length!==1||original.transactions[0]!.path!==transactionPath||
    journal.target_entry_id!==s.entry.id||journal.workflow!==workflow.workflow.name||journal.phase!=='Prepared'||
    journal.store_id!==worker.store_id||journal.order_id!==worker.order_id||
    journal.occurrence_id!==worker.occurrence_id||journal.worker_id!==worker.worker_id||journal.worker_epoch!==worker.worker_epoch||
    journal.source_capture_sha256!==sourceSha)
    bad('ForeignWorkerEvidence');
   return freeze({journal_entry:journal.target_entry_id,command_id:journal.command_id,request_fingerprint:journal.request_fingerprint});
  },
  withWorkerTransaction<T>(h:CommerceOperationInvocationHandle,storage:CommerceServiceStorageOwnerV1,transactionPath:string,execute:()=>T):T {
   const s=owned(h);
   if(!s.worker||s.worker.storage!==storage||s.parent!==null||typeof execute!=='function'||workerTransactions.has(s)||s.worker.transactionFinished)
    bad('ForeignWorkerEvidence');
   if(!s.worker.observation)owner.workerCommandIdentity(h,transactionPath);
   const projection=s.worker.owner.inspectContext(s.worker.context);
   workerTransactions.set(s,{workerId:projection.worker_id});
   try{
    const result=execute();
    if(result&&typeof result==='object'&&typeof (result as {then?:unknown}).then==='function')bad('AsyncWorkerTransaction');
    if((s.worker.protectedCall||s.worker.observation)&&result&&typeof result==='object'&&
     (result as {kind?:unknown}).kind==='committed')s.worker.transactionFinished=true;
    return result;
   }catch(error){if(s.worker.protectedCall||s.worker.observation)s.worker.transactionFinished=true;throw error;}
   finally{workerTransactions.delete(s);check(s);}
  },
  isWorkflowObservationInvocation(h:CommerceOperationInvocationHandle){const observation=owned(h).worker?.observation;return observation!==null&&observation!==undefined;},
  inspectWorkflowObservationCommitBinding(h:CommerceOperationInvocationHandle,transactionPath:string):CommerceWorkflowObservationCommitBindingV1 {
   const s=owned(h);
   if(s.parent!==null||s.target.role!=='Operation'||!s.worker?.observation||
    s.worker.transactionFinished||typeof transactionPath!=='string')bad('ForeignWorkerEvidence');
   const workflow=s.worker.binding.inspect(),store=s.worker.storage.inspect(),
    worker=s.worker.owner.inspectContext(s.worker.context),
    admitted=inspectCommerceWorkflowAnyObservationAdmissionV1(s.worker.observation),
    observed=admitted.inspection,original=plans.inspectOperation(s.target.handle),
    transactions=original.transactions.filter(row=>row.path===transactionPath);
   if(transactions.length!==1||s.entry.id!==observed.entry_id||id(s.target)!==observed.target||
    observed.source_capture_sha256!==sourceSha||observed.workflow!==workflow.workflow.name||
    observed.store_id!==store.store_id||observed.order_id!==worker.order_id||
    observed.occurrence_id!==worker.occurrence_id||observed.worker_id!==worker.worker_id||
    observed.worker_epoch!==worker.worker_epoch||
    !transactions[0]!.plan.participants.includes('Orders.Order')||
    !transactions[0]!.plan.participants.includes(workflow.workflow.durable_state)||
    Object.keys(s.parameters).length!==Object.keys(observed.input).length||
    Object.keys(s.parameters).some(name=>!Object.hasOwn(observed.input,name)||
     !isDeepStrictEqual(s.parameters[name],observed.input[name as keyof typeof observed.input],{skipPrototype:true})))
    bad('ForeignWorkerEvidence');
   const common={workflow:observed.workflow,source_capture_sha256:sourceSha,store_id:store.store_id,
    consumer_entry_id:observed.consumer_entry_id,occurrence_id:observed.occurrence_id,
    order_id:observed.order_id,observation_entry_id:observed.entry_id,
    worker_id:worker.worker_id,worker_epoch:worker.worker_epoch,
    expected_progress_version:observed.input.expectedProgressVersion,
    observation:observed.input.observation,authority_effect:'none' as const};
   if(admitted.kind==='local')return freeze({kind:'local' as const,...common,
    local_step:admitted.inspection.local_step,next_step:admitted.inspection.next_step});
   const remote=admitted.inspection;
   if(!transactions[0]!.plan.participants.includes(workflow.journal_entity)||
    remote.progress_version!==common.expected_progress_version)bad('ForeignWorkerEvidence');
   const journalWorker=admitted.kind==='remote-result'?
    {id:remote.worker_id,epoch:remote.worker_epoch}:
    {id:admitted.inspection.predecessor_worker_id,epoch:admitted.inspection.predecessor_worker_epoch};
   return freeze({kind:'dispatched-step' as const,...common,
    step_name:remote.step_name,target_entry_id:remote.remote_entry_id,
    journal_entity:workflow.journal_entity,
    command_id:remote.command_id,request_fingerprint:remote.request_fingerprint,
    journal_worker_id:journalWorker.id,journal_worker_epoch:journalWorker.epoch,
    journal_key:{consumerEntryId:remote.consumer_entry_id,occurrenceId:remote.occurrence_id,
     stepName:remote.step_name,commandId:remote.command_id},
    source:admitted.kind==='remote-result'?'remote-result' as const:'quiescent-recovery' as const});
  },
  assertTarget(h:CommerceOperationInvocationHandle,p:CommerceLocalPlanOwnerV1,hash:string,name:string){const s=owned(h);if(p!==plans||hash!==sourceSha||id(s.target)!==name)bad('ForeignInvocation');},
  retire(h:CommerceOperationInvocationHandle){owned(h).retired=true;},assertCurrent(h?:CommerceOperationInvocationHandle){if(h)owned(h);else current();},dispose(){if(disposed)return;disposed=true;for(const guard of guardOwners.values())guard.dispose();},
 });owners.add(owner);current();return owner;
}
