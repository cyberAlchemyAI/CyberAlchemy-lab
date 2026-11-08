/** Private execution of physically generated original Operation control.
 * Only source-selected root invocations enter; effect ports without original
 * owners fail closed. Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md#open-questions. */
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {isDeepStrictEqual,types as host} from 'node:util';
import {pinCoreImplementation,pinCorePhysicalCaptures,writeCoreExclusiveFile,type CorePhysicalFile} from './commerce-core-physical.js';
import {generateCommerceValueCodecBundle} from './commerce-value-codec-generation.js';
import {createCommerceOperationGenerationOwnerV1} from './commerce-operation-generation-owner-v1.js';
import {createCommerceIdentityCallOwner} from './commerce-identity-call-owner.js';
import {createCommerceIdentityComponentOwner} from './commerce-identity-component.js';
import {createCommerceGeneratedReadSetScopeV1} from './commerce-generated-read-set-v1.js';
import {selectCommerceGeneratedLocalReadKeyIndexV1} from './commerce-generated-local-read-key-v1.js';
import {commerceTransactionFailureAtV1} from './commerce-transaction-source-failure-v1.js';
import {commerceTransactionOutcomeMappingV1} from '../generation/commerce-effectful-operation-source-v1.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {assertCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,type CommerceServiceStorageFreshExecutionV1} from './commerce-service-storage-v1.js';
import type {CommerceDemoPayDispatchOwnerV1} from './commerce-demopay-dispatch-v1.js';
import type {CommerceSourceQueryRuntimeV1} from './commerce-source-query-runtime-v1.js';
import {assertCommerceWorkflowProtectedCallBindingV1,type CommerceWorkflowProtectedCallBindingV1} from './commerce-workflow-protected-call-binding-v1.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1} from './commerce-local-plan-owner-v1.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';
import type {ValueTypeV1} from './commerce-data-v1.js';
import type {CoreCommerceCrossServiceEventRelay} from '../generic/core-commerce-cross-service-event-relay.js';
import type {CoreCommerceEventAckSelection} from '../generic/core-commerce-event-ack-selection.js';
import type {CoreCommerceEventReceiverCommitOwner,CoreCommerceEventFreshReceiverCommit} from '../generic/core-commerce-event-receiver-commit.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-operation-generation-owner-v1'+ext,'commerce-selected-entry-auth-v1'+ext,'commerce-service-storage-v1'+ext,'commerce-source-query-runtime-v1'+ext,'commerce-workflow-protected-call-binding-v1'+ext,'commerce-identity-call-owner'+ext,'commerce-identity-component'+ext,'commerce-value-codec-generation'+ext,'commerce-generated-read-set-v1'+ext,'commerce-generated-local-read-key-v1'+ext,'commerce-transaction-source-failure-v1'+ext,'../generation/commerce-effectful-operation-source-v1'+ext,'../profile-engine/contracts'+ext]);
const where={path:'generated-operation-runtime',start:0,end:0};
function fail(code:string,_site:typeof where,message:string):never {const error=new Error(message);Object.assign(error,{code});throw error;}
const denied=(port:string):never=>fail('NativePortPending',where,'original '+port+' owner not yet joined');
type Value=CommerceNativeValue;
import type {CommerceFreshLocalObservationCommitV1} from './commerce-service-storage-v1.js';
type Outcome=Readonly<Record<string,unknown>>;
interface Codecs {
 checkCommerceSchema(value:unknown):{ok:true;value:unknown}|{ok:false};
 copyCommerceValue(schema:unknown,value:unknown):{ok:true;value:Value}|{ok:false};
 schemaForType(name:string):unknown;
 schemaForCallableArguments(value:unknown):unknown;
 encodeComputationParameters(schema:unknown,value:unknown):{ok:true;value:Uint8Array}|{ok:false};
 decodeComputationValue(schema:unknown,value:Uint8Array):{ok:true;value:Value}|{ok:false};
}
type SharedCodecArtifact={
 readonly stage:CoreCommerceStageSourceOwner;readonly source:CommerceSourceHandle;
 readonly domain:CommerceComputationDomainOwner;readonly baseline:CommerceComputationDomainHandle;
 readonly sourceSha:string;readonly familySha:string;
 readonly physical:ReturnType<typeof pinCorePhysicalCaptures>;
 readonly create:()=>Codecs;
};
// A selected Entry owner belongs to one original application assembly. Only
// generated, data-only codec bytes are shared; invocation/effect state is not.
const sharedCodecArtifacts=new WeakMap<object,Promise<SharedCodecArtifact>>();
const checked=<T>(result:{ok:true;value:T}|{ok:false},code:string):T=>result.ok?result.value:fail(code,where,'original generated value rejected');
type PreparedContinuation={parent:CommerceOperationInvocationHandle;child:CommerceOperationInvocationHandle;store:CommerceServiceStorageOwnerV1;sourcePath:string;attemptKey:string;orderId:string;requestFingerprint:string;amountMinor:bigint;currency:string;used:boolean};
type RuntimeOptions=Readonly<{demoPayDispatch?:CommerceDemoPayDispatchOwnerV1;externalQueries?:readonly CommerceSourceQueryRuntimeV1[];
 workflowProtectedCall?:CommerceWorkflowProtectedCallBindingV1;
 eventAck?:Readonly<{relay:CoreCommerceCrossServiceEventRelay;selection:CoreCommerceEventAckSelection;
  receiverCommit:CoreCommerceEventReceiverCommitOwner}>}>;
const continuations=new WeakMap<object,PreparedContinuation>();
const unresolvedCaptures=new WeakMap<object,{runtime:CommerceGeneratedOperationRuntimeV1;invocation:CommerceOperationInvocationHandle;sourcePath:string;reason:string}>();
export interface CommerceGeneratedOperationRuntimeV1 {
 run(invocation:CommerceOperationInvocationHandle):Promise<Outcome>;
 inspectFreshLocalObservationReturn(invocation:CommerceOperationInvocationHandle,result:unknown):Readonly<{receipt:object;commit:CommerceFreshLocalObservationCommitV1}>;
 inspectEventAcknowledgement(invocation:CommerceOperationInvocationHandle):CoreCommerceEventFreshReceiverCommit|null;
 inspectEventFingerprint(invocation:CommerceOperationInvocationHandle):string;
 assertStorage(owner:CommerceServiceStorageOwnerV1):void;
 consumeTransactionScope(token:CommerceGeneratedTransactionScopeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string):Readonly<Record<string,Value>>;
 inspect():Readonly<{operation:string;service:string;source_capture_sha256:string;qualification:'original-generated-control-replay-component;effect-ports-pending';authority_effect:'none'}>;
 assertCurrent():void;dispose():void;
}
export interface CommerceGeneratedTransactionScopeV1 {readonly kind:'original-generated-transaction-scope/v1-candidate'}
const runtimes=new WeakSet<object>();
export function assertCommerceGeneratedOperationRuntimeV1(owner:CommerceGeneratedOperationRuntimeV1):void {
 if(!owner||typeof owner!=='object'||!runtimes.has(owner))fail('ForeignOwner',where,'original generated Operation runtime required');
 owner.assertCurrent();
}

/** Public callers select a live source-owned invocation and output directory.
 * Only recursive execution can supply the private prepared continuation. */
async function createRuntime(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 plans:CommerceLocalPlanOwnerV1,selected:CommerceSelectedEntryAuthOwnerV1,
 storage:CommerceServiceStorageOwnerV1,root:CommerceOperationInvocationHandle,directory:string,
 options?:RuntimeOptions,continuation?:object,
):Promise<CommerceGeneratedOperationRuntimeV1> {
 assertCommerceLocalPlanOwnerV1(plans);assertCommerceSelectedEntryAuthOwnerV1(selected);assertCommerceServiceStorageOwnerV1(storage);pin.assertCurrent();
 if(options!==undefined){
  if(!options||typeof options!=='object'||host.isProxy(options)||![Object.prototype,null].includes(Object.getPrototypeOf(options)))
   fail('InvalidContract',where,'inert selected runtime options required');
  const descriptors=Object.getOwnPropertyDescriptors(options),keys=Reflect.ownKeys(options);
  if(!keys.length||keys.length>4||keys.some(key=>typeof key!=='string'||!['demoPayDispatch','externalQueries','workflowProtectedCall','eventAck'].includes(key))||
   keys.some(key=>!descriptors[key as string]?.enumerable||!Object.hasOwn(descriptors[key as string]!,'value')))
   fail('InvalidContract',where,'closed selected runtime options required');
 }
 const dispatchOwner=options?.demoPayDispatch;
 const workflowCall=options?.workflowProtectedCall;
 const eventAck=options?.eventAck;
 if(eventAck){
  if(!eventAck||typeof eventAck!=='object'||host.isProxy(eventAck)||
   ![Object.prototype,null].includes(Object.getPrototypeOf(eventAck))||
   Object.keys(eventAck).sort().join(',')!=='receiverCommit,relay,selection')
   fail('InvalidContract',where,'closed original Event acknowledgement owners required');
  const [relayModule,selectionModule,commitModule]=await Promise.all([
   import('../generic/core-commerce-cross-service-event-relay.js'),
   import('../generic/core-commerce-event-ack-selection.js'),
   import('../generic/core-commerce-event-receiver-commit.js'),
  ]);
  relayModule.assertCoreCommerceCrossServiceEventRelay(eventAck.relay);
  selectionModule.assertCoreCommerceEventAckSelection(eventAck.selection);
  commitModule.assertCoreCommerceEventReceiverCommitOwner(eventAck.receiverCommit);
 }
 if(workflowCall)assertCommerceWorkflowProtectedCallBindingV1(workflowCall);
 if(dispatchOwner){const module=await import('./commerce-demopay-dispatch-v1.js');module.assertCommerceDemoPayDispatchOwnerV1(dispatchOwner);}
 const externalQueries=new Map<string,CommerceSourceQueryRuntimeV1>();
 if(options?.externalQueries!==undefined){
  const supplied=options.externalQueries;
  if(!Array.isArray(supplied)||host.isProxy(supplied)||Object.getPrototypeOf(supplied)!==Array.prototype||
   supplied.length>64||Reflect.ownKeys(supplied).length!==supplied.length+1)
   fail('InvalidContract',where,'bounded selected external Query owners required');
  const module=await import('./commerce-source-query-runtime-v1.js');
  for(let i=0;i<supplied.length;i++){
   const descriptor=Object.getOwnPropertyDescriptor(supplied,String(i));
   if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))fail('InvalidContract',where,'dense original external Query owners required');
   const query=descriptor.value as CommerceSourceQueryRuntimeV1;module.assertCommerceSourceQueryRuntimeV1(query);
   if(externalQueries.has(query.query))fail('InvalidContract',where,'one selected Query owner per source Query required');
   externalQueries.set(query.query,query);
  }
 }
 const view=selected.inspectInvocation(root),selectedView=selected.inspect(),storeView=storage.inspect();
 if((view.depth===0)!==(view.parent_call_path===null)||view.role!=='Operation'||view.service!==storeView.service||
  view.source_sha256!==selectedView.source_capture_sha256||view.source_sha256!==storeView.source_capture_sha256||
  selectedView.family_sha256!==storeView.family_sha256)
  fail('ForeignInvocation',where,'live selected invocation must match original service/source/family');
 if(view.depth>0)selected.assertSelectedLocalChild(root,view.entry,view.operation);
 if(eventAck){
  const route=eventAck.relay.inspect().route,ack=eventAck.selection.inspect();
  if(view.depth!==0||view.entry!==route.entry||view.operation!==route.operation||
   view.service!==route.receiver_service||view.source_sha256!==route.source_capture_sha256||
   ack.source.entry!==route.entry||ack.source.operation!==route.operation||
   ack.receiver_store_id!==storeView.store_id||
   workflowCall||dispatchOwner)
   fail('ForeignInvocation',where,'exact original Event receiver runtime required');
 }
 if(workflowCall){
  const call=workflowCall.recheck(),principal=selected.principalIdentity(root),parameters=selected.parameters(root);
  if(view.depth!==0||view.entry!==call.entry_id||view.operation!==call.target||view.role!==call.role||
   view.source_sha256!==call.source_capture_sha256||principal.kind!=='service'||principal.id!==call.caller_service||
   Object.keys(parameters).length!==Object.keys(call.arguments).length||
   Object.keys(call.arguments).some(name=>!Object.hasOwn(parameters,name)||!isDeepStrictEqual(parameters[name],call.arguments[name])))
   fail('ForeignInvocation',where,'selected root must match the exact protected Workflow call');
 }
 const inherited=continuation&&typeof continuation==='object'?continuations.get(continuation):undefined;
 if(continuation&&(!inherited||inherited.child!==root||inherited.store!==storage||view.parent_call_path!==inherited.sourcePath))
  fail('ForeignInvocation',where,'exact private same-run prepared continuation required');
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)fail('OutputPath',where,'absolute generated runtime directory required');
 const operation=selected.operation(root),original=plans.inspectOperation(operation);
 if(original.operation!==view.operation||original.plan.service!==view.service||original.source_capture_sha256!==view.source_sha256)
  fail('ForeignInvocation',where,'selected invocation must retain its exact original Operation plan');
 mkdirSync(directory,{mode:0o700});
 const generated=createCommerceOperationGenerationOwnerV1(plans),control=generated.generateControl(operation),bundle=generated.files(control);
 const imported=generated.materialize(control,path.join(directory,'control'));
 await generated.importControlComponent(imported);
 const controlView=generated.inspect(imported),loaded:unknown=await import(pathToFileURL(path.join(String(controlView.directory),'operation-control.js')).href);
 if(!loaded||typeof loaded!=='object'||typeof (loaded as {runOperation?:unknown}).runOperation!=='function')fail('MissingGeneratedExport',where,'checked physical Operation control required');
 const runGenerated=(loaded as {runOperation:(parameters:unknown,runtime:unknown)=>Promise<Outcome>}).runOperation;
 let codecPromise=sharedCodecArtifacts.get(selected);
 if(!codecPromise){
  codecPromise=(async()=>{
   const codecDirectory=path.join(directory,'codecs');mkdirSync(codecDirectory,{mode:0o700});const files:CorePhysicalFile[]=[];
   files.push(writeCoreExclusiveFile(path.join(codecDirectory,'package.json'),'{"type":"module"}\n'));
   for(const file of generateCommerceValueCodecBundle(stage,source,domain,baseline).files){
    files.push(writeCoreExclusiveFile(path.join(codecDirectory,file.path),file.text));
    files.push(writeCoreExclusiveFile(path.join(codecDirectory,file.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(file.text)));
   }
   const codecModule:unknown=await import(pathToFileURL(path.join(codecDirectory,'values-and-codecs.js')).href);
   if(!codecModule||typeof codecModule!=='object'||typeof (codecModule as {createCommerceValueCodecs?:unknown}).createCommerceValueCodecs!=='function')
    fail('MissingGeneratedExport',where,'original generated codecs required');
   const physical=pinCorePhysicalCaptures(files);
   return Object.freeze({stage,source,domain,baseline,sourceSha:view.source_sha256,familySha:selectedView.family_sha256,
    physical,create:(codecModule as {createCommerceValueCodecs:()=>Codecs}).createCommerceValueCodecs});
  })();
  sharedCodecArtifacts.set(selected,codecPromise);
 }
 let sharedCodec:SharedCodecArtifact;
 try{sharedCodec=await codecPromise;}catch(error){if(sharedCodecArtifacts.get(selected)===codecPromise)sharedCodecArtifacts.delete(selected);throw error;}
 if(sharedCodec.stage!==stage||sharedCodec.source!==source||sharedCodec.domain!==domain||sharedCodec.baseline!==baseline||
  sharedCodec.sourceSha!==view.source_sha256||sharedCodec.familySha!==selectedView.family_sha256)
  fail('ForeignOwner',where,'shared codec must retain exact original selected source and domain');
 sharedCodec.physical.assertCurrent();
 const codecs=sharedCodec.create();
 const values=domain.inspect(baseline).contract.values,schemas=new Map<string,unknown>();
 const schema=(type:ValueTypeV1)=>{const key=JSON.stringify(type),existing=schemas.get(key);if(existing)return existing;const found=checked(codecs.checkCommerceSchema({...values,root:type}),'UnsupportedValueType');schemas.set(key,found);return found;};
 const copy=(type:ValueTypeV1,value:unknown,locals:readonly {name:string;fields:Readonly<Record<string,ValueTypeV1>>}[]=[]):Value=>{
  if(type.kind==='optional'){
   if(!value||typeof value!=='object'||Array.isArray(value))fail('InputType',where,'original optional required');
   const row=value as Record<string,unknown>;if(row.kind==='none'&&Object.keys(row).length===1)return Object.freeze({kind:'none'});
   if(row.kind==='some'&&Object.keys(row).length===2&&Object.hasOwn(row,'value'))return Object.freeze({kind:'some',value:copy(type.element,row.value,locals)});
   fail('InputType',where,'closed original optional required');
  }
  if(type.kind==='list'){
   if(!Array.isArray(value)||value.length<type.min_items||value.length>type.max_items)fail('InputType',where,'bounded original list required');
   return Object.freeze(value.map(item=>copy(type.element,item,locals)));
  }
  const local=type.kind==='record'?locals.find(item=>item.name===type.name):undefined;
  if(local){
   if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==Object.keys(local.fields).length)fail('InputType',where,'closed local record required');
   const out:Record<string,Value>=Object.create(null);for(const [name,field]of Object.entries(local.fields)){
    if(!Object.hasOwn(value,name))fail('InputType',where,'local record field required');out[name]=copy(field,(value as Record<string,unknown>)[name],locals);
   }return Object.freeze(out);
  }
  return checked(codecs.copyCommerceValue(schema(type),value),'InputType');
 };
 const calls=createCommerceIdentityCallOwner(sources,capture,stage,source,domain,baseline),callPaths=calls.paths(original.plan),callHandles=callPaths.map(p=>calls.bind(original.plan,p));
 const identityDirectory=path.join(directory,'identity');mkdirSync(identityDirectory,{mode:0o700});
 const nativeCalls=new Map(callPaths.map((p,i)=>[p,callHandles[i]!]));
 const identityOwner=nativeCalls.size?createCommerceIdentityComponentOwner(calls,stage,source,domain,baseline):undefined;
 const identity=identityOwner?await identityOwner.materialize(callHandles,identityDirectory):undefined;
 const sites=bundle.manifest.source_sites as Record<string,any>;
 const transactionScopes=new WeakMap<object,{invocation:CommerceOperationInvocationHandle;path:string;scope:Readonly<Record<string,Value>>}>();
 const settlements=new WeakMap<object,{path:string;sourceAction?:unknown;sourceActionPath?:string|null|undefined;recovery?:string}>();
 let disposed=false,running=false,workflowOriginalClaimed=false;
 const releasedOutcomes=new WeakMap<object,{returned:boolean;fresh:boolean;commits:readonly unknown[]}>();
 let eventAcknowledgement:CoreCommerceEventFreshReceiverCommit|null=null,eventResultReturned=false;
 let eventFingerprint:string|null=null;
 const current=(pureEvaluation=false)=>{if(disposed)fail('DisposedOwner',where,'generated runtime disposed');pin.assertCurrent();
  // Internal pure evaluation has no effect or caller callback and cannot
  // release the Operation result. Source metadata still checks current Auth
  // and the exact worker claim; all admissions, native/effect boundaries and
  // final result release use the full inspection. No authority is cached.
  if(pureEvaluation){if(selected.operation(root)!==operation)fail('ForeignInvocation',where,'original pure evaluation Operation required');}
  else selected.inspectInvocation(root);
  storage.assertCurrent();plans.assertOperationCurrent(operation);generated.inspect(imported);if(identityOwner&&identity)identityOwner.assertCurrent(identity);sharedCodec.physical.assertCurrent();eventAck?.relay.assertCurrent();eventAck?.selection.assertCurrent();eventAck?.receiverCommit.assertCurrent();};
 // Every private read-set method begins with this full currentness check.
 // Its immediate caller must not repeat the identical check without any
 // intervening work; post-read, effect and final-release checks remain full.
 const readSets=createCommerceGeneratedReadSetScopeV1(sites,current);
 const info=Object.freeze({operation:view.operation,service:view.service,source_capture_sha256:view.source_sha256,qualification:'original-generated-control-replay-component;effect-ports-pending' as const,authority_effect:'none' as const});
 const owner:CommerceGeneratedOperationRuntimeV1=Object.freeze({
  async run(invocation:CommerceOperationInvocationHandle){
   current();if(invocation!==root)fail('ForeignInvocation',where,'exact selected original root required');
   const present=selected.inspectInvocation(invocation);if(present.operation!==info.operation||present.service!==info.service||present.depth!==view.depth||present.parent_call_path!==view.parent_call_path)fail('ForeignInvocation',where,'selected invocation changed');
   if(running)fail('ConcurrentOperation',where,'one generated invocation at a time');
   running=true;
   eventAcknowledgement=null;eventResultReturned=false;eventFingerprint=null;
   try{
   if(workflowCall){
    const call=workflowCall.claimOriginalCall();
    if(call.entry_id!==view.entry||call.target!==view.operation||call.source_capture_sha256!==view.source_sha256)
     fail('ForeignInvocation',where,'original Workflow dispatch claim changed');
    workflowOriginalClaimed=true;
   }
   const parameters=selected.parameters(root);
   const committed=new Map<string,{execution:CommerceServiceStorageFreshExecutionV1;settlement:object;scope:Readonly<Record<string,Value>>}>(),observations=new WeakMap<object,string>(),countObservations=new Map<string,bigint>();
   const observe=<T extends object>(sourcePath:string,value:T):T=>{observations.set(value,sourcePath);return value;};
   let charged=0;const runtime=Object.freeze({
    assertCurrent(sourceSha:string,operationId:string,pathId:string){if(disposed||!running)fail('DisposedOwner',where,'generated Operation is not active');if(sourceSha!==info.source_capture_sha256||operationId!==info.operation||typeof pathId!=='string'||pathId.length>8192)fail('ForeignInvocation',where,'generated control does not match original source');},
    parameters(value:unknown){current();if(value!==parameters)fail('ForeignInvocation',where,'generated parameters must come from selected invocation');return value;},
    charge(){if(++charged>100000)fail('ResourceLimit',where,'bounded generated Operation required');if((charged&4095)===0)current();},
    validateRole(pathId:string,value:Value){const role=sites[pathId];if(!role||!role.result)fail('UnknownSourcePath',where,'original generated role path required');return copy(role.result,value,role.local_records??[]);},
    validateReturn(value:Value){return copy(original.plan.result,value);},
    context(pathId:string){current();return selected.context(root,pathId);},
    enumValue(_pathId:string,type:string,variant:string,fields:Readonly<Record<string,Value>>){const definition=values.enums.find(e=>e.name===type);if(!definition||!definition.variants.some(v=>v.name===variant))fail('UnknownSourcePath',where,'original enum variant required');const value=definition.variants.every(v=>!Object.keys(v.fields).length)?variant:{kind:variant,...fields};return copy({kind:'enum',name:type},value);},
    async pure(pathId:string,args:readonly Value[]){current(true);const bound=plans.bindPureCall(operation,pathId),binding=bound.owner.inspect(bound.handle);
     if(binding.caller!==info.operation||binding.source_capture_sha256!==info.source_capture_sha256||args.length!==binding.callee.parameters.length)fail('ForeignInvocation',where,'original pure call mismatch');
     const input=Object.fromEntries(binding.callee.parameters.map((p,i)=>[p.name,args[i]])),wire=checked(codecs.encodeComputationParameters(codecs.schemaForCallableArguments(binding.callee.declaration),input),'InputType');
     const result=bound.owner.evaluateBoundParameters(bound.handle,wire).observation.result;current(true);if(!result.ok)return {ok:false,code:result.error.code};
     return {ok:true,value:checked(codecs.decodeComputationValue(schema(binding.callee.result),result.wire),'InputType')};
    },
    async native(pathId:string,args:readonly Value[]){current();const site=sites[pathId];
     if(site?.op==='native_observation'&&site.abi==='craft.commerce-worker-context/v1-candidate'&&
      site.context==='worker'&&site.source_type==='Shop.Values.WorkerContext')
      return selected.workerObservation(root,pathId,args);
     if(site?.op==='native_observation'&&site.abi==='craft.commerce-service-context/v1-candidate'&&site.context==='service'&&site.source_type==='Shop.Values.ServiceContext'&&site.method==='ownsOrProvesQuiescentLocalCommand'){
      if(workflowCall&&view.depth===0){
       const proof=workflowCall.recheck(),principal=selected.principalIdentity(root);
       if(!workflowOriginalClaimed||site.arguments?.length!==1||args.length!==1||
        typeof args[0]!=='string'||args[0]!==proof.command_id||
        proof.entry_id!==view.entry||proof.target!==view.operation||
        principal.kind!=='service'||principal.id!==proof.caller_service)
        return denied('original Workflow service command ownership');
       return true;
      }
      const proof=inherited;
      if(!proof||proof.used||proof.child!==root||proof.store!==storage||site.arguments?.length!==1||site.arguments[0]?.value?.op!=='var'||site.arguments[0]?.value?.name!=='attemptKey'||args.length!==1||args[0]!==proof.attemptKey)
       return denied('same-run local command quiescence');
      proof.used=true;selected.inspectInvocation(proof.parent);selected.assertSelectedLocalChild(root,view.entry,view.operation);
      const attempt=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:proof.attemptKey});
      if(!attempt||typeof attempt!=='object'||Array.isArray(attempt))fail('StaleOwner',where,'same-run Prepared intent missing');
      const row=attempt as Record<string,unknown>;
      if(row.attemptKey!==proof.attemptKey||row.orderId!==proof.orderId||row.requestFingerprint!==proof.requestFingerprint||
       row.amountMinor!==proof.amountMinor||row.currency!==proof.currency||row.status!=='Intent'||row.dispatchState!=='Prepared'||row.version!==1n)
       fail('StaleOwner',where,'same-run Prepared intent changed before local command claim');
      current();return true;
     }
     const bound=nativeCalls.get(pathId)??denied('native observation');const binding=calls.inspect(bound);
     if(binding.caller!==info.operation||binding.service!==info.service||binding.source_capture_sha256!==info.source_capture_sha256)fail('ForeignInvocation',where,'original identity call mismatch');
     if(!identityOwner||!identity)return denied('identity observation');
     const result=identityOwner.evaluateBoundParameters(identity,bound,args);current();if(!result.ok)fail('ProducerValueRejected',where,'original identity producer rejected parameters');
     if(eventAck&&binding.observation.method==='eventFingerprint'){
      if(typeof result.value!=='string'||!/^[a-f0-9]{64}$/.test(result.value)||
       (eventFingerprint!==null&&eventFingerprint!==result.value))
       fail('ForeignSettlement',where,'one original source-generated Event fingerprint required');
      eventFingerprint=result.value;
     }
     return result.value;
    },
    async preflight(pathId:string){current();const site=sites[pathId];if(site?.kind!=='preflight'||site.invocation!==false||typeof site.target!=='string')fail('UnknownSourcePath',where,'checked noninvocable replay contract required');},
    async count(pathId:string){current();const site=sites[pathId];if(site?.kind!=='count'||typeof site.entity!=='string'||site.native_bound!=='bounded-native-count-required')fail('UnknownSourcePath',where,'checked native count site required');const count=storage.countStoredRecords(site.entity);current();countObservations.set(pathId,count);return count;},
    async read(pathId:string,key:Readonly<Record<string,Value>>,args:Readonly<Record<string,Value>>){readSets.assertRead(pathId);const site=sites[pathId];
     if(!site||site.kind!=='read')fail('UnknownSourcePath',where,'original generated read site required');
     if(site.call!==null){
      if(site.call?.role!=='Query'||site.call.authorization!=='fresh-original-entry-decision-required'||typeof site.call.target!=='string'||
       typeof site.call.entry!=='string'||Object.keys(key).length)denied('original external Query read');
      const query=externalQueries.get(site.call.target)??denied('selected external Query owner');query.assertCurrent();
      const started=await selected.beginDelegatedQuery(root,pathId+'.call',undefined,args);current();
      if(!started.ok)fail('AuthorizationDenied',where,'original external Query Entry denied by native Auth');
      const child=started.invocation;
      try{
       const childView=selected.inspectInvocation(child),parameters=selected.parameters(child);
       if(childView.entry!==site.call.entry||childView.operation!==query.query||childView.role!=='Query'||
        Object.keys(parameters).length!==Object.keys(args).length||
        Object.keys(args).some(name=>!Object.hasOwn(parameters,name)||!isDeepStrictEqual(parameters[name],args[name])))
        fail('ForeignInvocation',where,'generated read arguments must equal the original delegated Query request');
       let result:ReturnType<CommerceSourceQueryRuntimeV1['releaseSelected']>;
       try{
        if(query.selectedEntryMode(childView.entry)==='causal-service')
         result=query.executeSelectedService(selected,child);
        else{
         const witness=query.select(selected,child);
         result=query.releaseSelected(witness,selected,child);
        }
       }
       catch(error){if(error&&typeof error==='object'&&(error as {code?:unknown}).code==='ScopedResourceNotFound')
        return observe(pathId,Object.freeze({kind:'missing' as const}));throw error;}
       current();
       if(result.kind==='failed')return observe(pathId,Object.freeze({kind:'unavailable' as const}));
       if(result.kind==='rejected'){
        if(result.code==='resource-not-found')return observe(pathId,Object.freeze({kind:'missing' as const}));
        fail('AuthorizationDenied',where,'original external Query rejected outside its declared missing case');
       }
       if(result.kind!=='returned')fail('InvalidObservation',where,'original external Query result kind required');
       const value=result.value;
       if(value&&typeof value==='object'&&!Array.isArray(value)&&(value as Record<string,unknown>).kind==='none')
        return observe(pathId,Object.freeze({kind:'missing' as const}));
       if(!value||typeof value!=='object'||Array.isArray(value)||(value as Record<string,unknown>).kind!=='some')
        fail('InvalidObservation',where,'original external Query must return a checked optional value');
       const projected=(value as {value:Value}).value;
       return observe(pathId,Object.freeze({kind:'found' as const,value:copy(site.type.kind==='optional'?site.type.element:site.type,projected)}));
      }finally{selected.retire(child);}
     }
     if(typeof site.entity!=='string'||Object.keys(args).length||!site.key)denied('unbound local read');
     const keyIndex=selectCommerceGeneratedLocalReadKeyIndexV1(values,site,key);
     const row=storage.inspectStoredRecord(site.entity,keyIndex,key);current();return observe(pathId,row===null?Object.freeze({kind:'missing'}):Object.freeze({kind:'found',value:copy(site.type.kind==='optional'?site.type.element:site.type,row)}));
    },
    async call(pathId:string,args:Readonly<Record<string,Value>>){current();workflowCall?.recheck();readSets.assertWritable();const site=sites[pathId];
     if(!site||typeof site.target!=='string'||site.entry!==null||site.authorization!=='original-local-context-forwarding-required')denied('original source call');
     if(site.target==='Shop.DemoPay.Capture'){
      const dispatch=dispatchOwner??denied('DemoPay Capture dispatch');
      if(site.role!=='Operation'||view.depth<1)denied('selected provider call');
      const at=/^\$\.body\[(\d+)\]\.call$/.exec(pathId),position=at?Number(at[1]):-1;
      const predecessor=original.transactions.map(t=>({transaction:t,index:/^\$\.body\[(\d+)\]\.transaction$/.exec(t.path)}))
       .filter(t=>t.index&&Number(t.index[1])<position).sort((a,b)=>Number(b.index![1])-Number(a.index![1]))[0]?.transaction;
      const prior=predecessor&&committed.get(predecessor.path);
      if(!predecessor||!prior)return denied('fresh same-run dispatch transaction');
      committed.delete(predecessor.path);
      const permit=dispatch.prepare(prior.execution,owner,selected,root,predecessor.path),wire=await dispatch.send(permit);
      current();
      if(wire.kind==='observed'&&wire.matches_request){
       const result=wire.result,value=copy(site.result,{attemptKey:result.attemptKey,orderId:result.orderId,amountMinor:BigInt(result.amountMinor),currency:result.currency,
        status:result.status,providerReference:result.providerReference===null?{kind:'none'}:{kind:'some',value:result.providerReference}});
       return observe(pathId,Object.freeze({kind:'value' as const,value,commits:Object.freeze([]),unresolved:Object.freeze([])}));
      }
      const reason=wire.kind==='observed'?'malformed':wire.reason,transport=reason==='timeout'||reason==='transport'||reason==='provider-unavailable';
      const ticket=Object.freeze({kind:'original-demopay-capture-unresolved/v1-candidate' as const});
      unresolvedCaptures.set(ticket,{runtime:owner,invocation:root,sourcePath:pathId,reason});
      return observe(pathId,Object.freeze({kind:'indeterminate' as const,ticket,channel:transport?'on-transport-error':'on-invalid-response',has_value:false as const}));
     }
     if(site.role!=='Operation')denied('local Query execution');
     if(view.depth===0&&info.operation==='Payments.CapturePayment'&&site.target==='Payments.DispatchOriginalCapture'&&!dispatchOwner)
      return denied('DemoPay Capture dispatch');
     const child=selected.deriveLocalCall(root,pathId,args);
     let token:object|undefined,nested:CommerceGeneratedOperationRuntimeV1|undefined;
     try{
     const childView=selected.inspectInvocation(child);
     if(childView.service!==info.service||childView.entry!==view.entry||childView.depth!==view.depth+1||childView.parent_call_path!==pathId)
      fail('ForeignInvocation',where,'original selected local call changed');
     if(view.depth===0&&info.operation==='Payments.CapturePayment'&&site.target==='Payments.DispatchOriginalCapture'){
      const prepare=original.transactions.find(t=>t.plan.name==='PrepareCapture'),prior=prepare&&committed.get(prepare.path);
      if(!prepare||!prior)return denied('fresh PrepareCapture continuation');
      committed.delete(prepare.path);
      storage.consumeFreshCommit(prior.execution,owner,selected,root,prepare.path);
      const rootInput=selected.parameters(root),attemptKey=args.attemptKey,orderId=args.orderId,requestFingerprint=args.requestFingerprint;
      if(typeof attemptKey!=='string'||typeof orderId!=='string'||typeof requestFingerprint!=='string'||
       rootInput.attemptKey!==attemptKey||rootInput.orderId!==orderId||typeof rootInput.amountMinor!=='bigint'||typeof rootInput.currency!=='string')
       fail('ForeignInvocation',where,'fresh continuation must retain original selected request');
      const attempt=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey});
      if(!attempt||typeof attempt!=='object'||Array.isArray(attempt))fail('StaleOwner',where,'fresh Prepared intent missing');
      const row=attempt as Record<string,unknown>;
      if(row.attemptKey!==attemptKey||row.orderId!==orderId||row.requestFingerprint!==requestFingerprint||row.amountMinor!==rootInput.amountMinor||
       row.currency!==rootInput.currency||row.status!=='Intent'||row.dispatchState!=='Prepared'||row.version!==1n)
       fail('StaleOwner',where,'fresh Prepared intent does not match original source commit');
      token=Object.freeze({});continuations.set(token,{parent:root,child,store:storage,sourcePath:pathId,attemptKey,orderId,requestFingerprint,
       amountMinor:rootInput.amountMinor,currency:rootInput.currency,used:false});
     }
      const childOptions:RuntimeOptions|undefined=workflowCall||eventAck?
       options?.demoPayDispatch||options?.externalQueries?Object.freeze({
        ...(options?.demoPayDispatch?{demoPayDispatch:options.demoPayDispatch}:{}),
        ...(options?.externalQueries?{externalQueries:options.externalQueries}:{}),
       }):undefined:options;
      nested=await createRuntime(sources,capture,stage,source,domain,baseline,plans,selected,storage,child,path.join(directory,'local-'+randomUUID()),childOptions,token);
      const outcome=await nested.run(child);current();
      if(outcome.kind==='returned')return observe(pathId,Object.freeze({kind:'value' as const,value:outcome.value as Value,commits:outcome.commits as readonly unknown[],unresolved:Object.freeze([])}));
      if(outcome.kind==='failed'||outcome.kind==='rejected')return observe(pathId,Object.freeze({kind:outcome.kind,code:String(outcome.code),channel:null}));
      if(outcome.kind==='indeterminate'&&Array.isArray(outcome.tickets)&&outcome.tickets.length===1)
       return observe(pathId,Object.freeze(outcome.has_value?{kind:'indeterminate' as const,ticket:outcome.tickets[0],channel:null,has_value:true as const,value:outcome.value as Value}:{kind:'indeterminate' as const,ticket:outcome.tickets[0],channel:null,has_value:false as const}));
      fail('InvalidObservation',where,'bounded generated local Operation result required');
     }finally{try{nested?.dispose();}finally{if(token)continuations.delete(token);selected.retire(child);}}
    },
    assertObservation(pathId:string,observation:unknown){current();if(typeof observation==='bigint'&&sites[pathId]?.kind==='count'&&countObservations.get(pathId)===observation){countObservations.delete(pathId);return;}if(!observation||typeof observation!=='object'||observations.get(observation)!==pathId)fail('InvalidObservation',where,'exact generated read/call/count observation required');},
    async openReadSet(pathId:string){return readSets.open(pathId);},
    async closeReadSet(lease:unknown){readSets.close(lease);},
    async transaction(pathId:string,scope:Readonly<Record<string,Value>>){
     current();workflowCall?.recheck();readSets.assertWritable();const transaction=original.transactions.find(t=>t.path===pathId);if(!transaction)fail('UnknownSourcePath',where,'original generated transaction path required');
     const token=Object.freeze({kind:'original-generated-transaction-scope/v1-candidate' as const});
     transactionScopes.set(token,{invocation:root,path:pathId,scope});
     try{
      const executed=await storage.applyFreshGeneratedTransaction(owner,token,selected,root,pathId);
      current();
      const mapping=commerceTransactionOutcomeMappingV1(transaction.plan);
      let settlement:Readonly<Record<string,unknown>>;
      let sourceAction:unknown,sourceActionPath:string|null|undefined,recovery:string|undefined;
      if(executed.kind==='not-claimed')settlement=Object.freeze({kind:'rejected',code:executed.claim.kind==='not-fresh'?'CommandNotFresh':'StorageUnavailable',rollback:null});
      else if(executed.outcome.kind==='committed')settlement=Object.freeze({kind:'committed',receipt:executed.outcome.receipt,aliases:executed.outcome.result});
      else if(executed.outcome.kind==='indeterminate'){
       sourceAction=mapping.indeterminate.action??undefined;
       settlement=Object.freeze({kind:'indeterminate',ticket:executed.outcome.ticket,
        source_action:mapping.indeterminate.action,retain_original:mapping.indeterminate.retain_original,do_not_ack:mapping.indeterminate.do_not_ack});
      }
      else if(executed.outcome.kind==='unavailable-before-start')settlement=Object.freeze({kind:'failed',code:'transaction-unavailable',rollback:null});
      else if(executed.outcome.kind==='capacity-unavailable')settlement=Object.freeze({kind:'failed',code:'capacity-unavailable',rollback:executed.outcome.rollback});
      else {
       const originalFailure=storage.inspectSourceFailure(executed.outcome.rollback);
       if(originalFailure){
        const sourceFailure=commerceTransactionFailureAtV1(pathId,transaction.plan,originalFailure.source_path,originalFailure.source_action);
        if(!sourceFailure)fail('ForeignSourceFailure',where,'native rollback action must match the original checked transaction step');
        const action=sourceFailure.action;
        if(action.kind==='return'||action.kind==='invoke-return'){
         sourceAction=action;sourceActionPath=sourceFailure.action_path;
         settlement=Object.freeze({kind:'source-return-required',source_action:action,source_action_path:sourceActionPath,rollback:executed.outcome.rollback});
        }else settlement=Object.freeze({kind:action.kind==='reject'?'rejected':'failed',code:action.code,rollback:executed.outcome.rollback});
       }else {
        const decision=mapping[executed.outcome.kind];
        if(decision.recovery){recovery=decision.recovery;settlement=Object.freeze({kind:'generated-recovery-required',recovery,rollback:executed.outcome.rollback,source_path:pathId});}
        else if(decision.action?.kind==='return'||decision.action?.kind==='invoke-return'){
         sourceAction=decision.action;sourceActionPath=null;
         settlement=Object.freeze({kind:'source-return-required',source_action:sourceAction,source_action_path:null,rollback:executed.outcome.rollback});
        }else if(decision.action?.kind==='reject'||decision.action?.kind==='fail')settlement=Object.freeze({kind:decision.action.kind==='reject'?'rejected':'failed',code:decision.action.code,rollback:executed.outcome.rollback});
        else fail('MissingSourceOutcomeMapping',where,'source transaction rollback requires a checked disposition');
       }
      }
      settlements.set(settlement,{path:pathId,...sourceAction===undefined?{}:{sourceAction,sourceActionPath},...recovery===undefined?{}:{recovery}});
      if(executed.kind==='applied'&&executed.outcome.kind==='committed')committed.set(pathId,{execution:executed,settlement,scope});
      return settlement;
     }finally{transactionScopes.delete(token);}
    },
    assertTransaction(pathId:string,settlement:unknown){current();if(!settlement||typeof settlement!=='object'||settlements.get(settlement)?.path!==pathId)fail('ForeignSettlement',where,'exact original transaction settlement required');},
    assertSourceReturn(pathId:string,settlement:unknown,action:unknown){current();const row=settlement&&typeof settlement==='object'?settlements.get(settlement):undefined;
     if(!row||row.path!==pathId||row.sourceAction===undefined||dataDigest(row.sourceAction)!==dataDigest(action)||
      (settlement as {source_action_path?:unknown}).source_action_path!==row.sourceActionPath)fail('ForeignSettlement',where,'exact source rollback return required');},
    assertRecovery(pathId:string,settlement:unknown,plan:unknown){current();const row=settlement&&typeof settlement==='object'?settlements.get(settlement):undefined;
     const expected=(bundle.manifest.recovery_plans as readonly unknown[]|undefined)?.find(candidate=>candidate&&typeof candidate==='object'&&
      (candidate as {transaction_path?:unknown;kind?:unknown}).transaction_path===pathId&&(candidate as {kind?:unknown}).kind===row?.recovery);
     if(!row||row.path!==pathId||row.recovery===undefined||expected===undefined||dataDigest(expected)!==dataDigest(plan))
      fail('ForeignSettlement',where,'exact source recovery and proven rollback required');},
    async acknowledge(pathId:string,originalCommits:readonly unknown[]){
     current();const boundEvent=eventAck;
     if(!boundEvent)return denied('acknowledgement');
     const route=boundEvent.relay.inspect().route,source=boundEvent.selection.inspect().source;
     if(pathId!==source.acknowledge_path||view.entry!==source.entry||
      !Array.isArray(originalCommits)||host.isProxy(originalCommits)||originalCommits.length!==1||
      eventAcknowledgement!==null)
      fail('ForeignSettlement',where,'one exact original Event acknowledgement required');
     const matches=source.candidates.flatMap(candidate=>{
      const committedRow=committed.get(candidate.transaction_path);
      return committedRow?[{candidate,committedRow}]:[];
     });
     if(matches.length!==1)fail('ForeignSettlement',where,'one source-selected inbox transaction required');
     const {candidate,committedRow}=matches[0]!;
     const transaction=original.transactions.find(row=>row.path===candidate.transaction_path),
      inboxMutation=transaction?.plan.body.filter(step=>step.kind==='mutation'&&
       step.operation==='create'&&step.target===source.inbox_entity&&
       step.binding===candidate.inbox_binding);
     const inbox=inboxMutation?.[0];
     if(!inbox||inboxMutation?.length!==1||inbox.kind!=='mutation')
      fail('ForeignSettlement',where,'one checked source inbox mutation required');
     const fingerprintFields=inbox.fields.filter(field=>field.name==='eventFingerprint'),
      fingerprintExpression=fingerprintFields[0]?.value.expression;
     if(fingerprintFields.length!==1||!fingerprintExpression||fingerprintExpression.op!=='var')
      fail('ForeignSettlement',where,'original source-generated Event fingerprint binding required');
     const fingerprint=committedRow.scope[fingerprintExpression.name];
     if(typeof fingerprint!=='string'||!/^[a-f0-9]{64}$/.test(fingerprint))
      fail('ForeignSettlement',where,'checked source-generated Event fingerprint required');
     if(!Object.hasOwn(committedRow.settlement,'receipt')||
      originalCommits[0]!==(committedRow.settlement as {receipt:unknown}).receipt)
      fail('ForeignSettlement',where,'generated acknowledgement must retain exact native commit');
     const parameters=selected.parameters(root),event=parameters[route.argument];
     if(!event||typeof event!=='object'||Array.isArray(event)||host.isProxy(event))
      fail('ForeignInvocation',where,'original Event argument required');
     const metadata=(event as Record<string,unknown>).metadata;
     if(!metadata||typeof metadata!=='object'||Array.isArray(metadata)||host.isProxy(metadata)||
      typeof (metadata as Record<string,unknown>).eventId!=='string')
      fail('ForeignInvocation',where,'original Event occurrence identity required');
     const occurrenceId=(metadata as Record<string,unknown>).eventId;
     if(typeof occurrenceId!=='string')fail('ForeignInvocation',where,'original Event occurrence identity required');
     const ready=boundEvent.relay.readReady(occurrenceId);
     if(ready.kind!=='ready')fail('StaleOwner',where,'original producer outbox no longer ready');
     const occurrence=boundEvent.relay.inspectOccurrence(ready.occurrence);
     if(occurrence.route.entry!==route.entry||!isDeepStrictEqual(occurrence.event,event))
      fail('ForeignInvocation',where,'original Event differs from persisted producer occurrence');
     eventAcknowledgement=boundEvent.receiverCommit.acceptFresh({runtime:owner,selected,
      invocation:root,occurrence:ready.occurrence,transaction_path:candidate.transaction_path,
      execution:committedRow.execution,event_fingerprint:fingerprint});
     const witnessed=boundEvent.receiverCommit.inspectWitness(eventAcknowledgement);
     if(witnessed.occurrence_id!==occurrence.occurrence_id||
      witnessed.transaction_path!==candidate.transaction_path)
      fail('ForeignSettlement',where,'original Event receiver commit witness changed');
    },
   });
   const result=await runGenerated(parameters,runtime);readSets.assertReleased();
   if(eventAck&&result.kind==='returned'&&Array.isArray(result.commits)&&result.commits.length>0&&eventAcknowledgement===null)
    fail('ForeignSettlement',where,'committed Event must have original inbox acknowledgement');
   eventResultReturned=result.kind==='returned';
   if(!eventResultReturned)eventAcknowledgement=null;
   const value=result.value;
   releasedOutcomes.set(result,{returned:result.kind==='returned',fresh:!!value&&typeof value==='object'&&!Array.isArray(value)&&(value as Record<string,unknown>).fresh===true,
    commits:Object.freeze(Array.isArray(result.commits)?[...result.commits]:[])});
   return result;
   }finally{if(!eventResultReturned)eventAcknowledgement=null;running=false;}
  },
  inspectFreshLocalObservationReturn(invocation:CommerceOperationInvocationHandle,result:unknown){
   current();if(invocation!==root||running)fail('ForeignInvocation',where,'completed original local observation runtime required');
   const released=result&&typeof result==='object'?releasedOutcomes.get(result):undefined;
   if(!released?.returned||!released.fresh||released.commits.length!==1||!released.commits[0]||typeof released.commits[0]!=='object')
    fail('ForeignSettlement',where,'exact released fresh local observation outcome required');
   const receipt=released!.commits[0] as object,commit=storage.inspectFreshLocalObservationCommit(receipt);
   if(commit.operation!==info.operation||commit.binding.observation_entry_id!==view.entry||commit.binding.source_capture_sha256!==info.source_capture_sha256)
    fail('ForeignSettlement',where,'original local return and native receipt must share one invocation');
   return Object.freeze({receipt,commit});
  },
  inspectEventAcknowledgement(invocation:CommerceOperationInvocationHandle){
   current();if(!eventAck||invocation!==root||running||!eventResultReturned)
    fail('ForeignInvocation',where,'completed original Event runtime required');
   if(eventAcknowledgement)eventAck.receiverCommit.inspectWitness(eventAcknowledgement);
   return eventAcknowledgement;
  },
  inspectEventFingerprint(invocation:CommerceOperationInvocationHandle){
   current();if(!eventAck||invocation!==root||running||!eventResultReturned||
    eventFingerprint===null)
    fail('ForeignInvocation',where,'completed source-generated Event fingerprint required');
   return eventFingerprint;
  },
  assertStorage(other:CommerceServiceStorageOwnerV1){current();if(other!==storage)fail('ForeignOwner',where,'exact original service storage required');},
  consumeTransactionScope(token:CommerceGeneratedTransactionScopeV1,selectedAuth:CommerceSelectedEntryAuthOwnerV1,invocation:CommerceOperationInvocationHandle,transactionPath:string){
   current();if(!running||selectedAuth!==selected||invocation!==root)fail('ForeignInvocation',where,'exact active original invocation required');
   const row=token&&typeof token==='object'?transactionScopes.get(token):undefined;
   if(!row||row.invocation!==invocation||row.path!==transactionPath||!original.transactions.some(t=>t.path===transactionPath))
    fail('ForeignScope',where,'one-use generated transaction scope required');
   transactionScopes.delete(token);return row.scope;
  },
  inspect(){current();return info;},assertCurrent(){current();},
  dispose(){if(disposed)return;if(identityOwner&&identity)identityOwner.dispose(identity);disposed=true;},
 });runtimes.add(owner);current();return owner;
}

export async function createCommerceGeneratedOperationRuntimeV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 plans:CommerceLocalPlanOwnerV1,selected:CommerceSelectedEntryAuthOwnerV1,
 storage:CommerceServiceStorageOwnerV1,root:CommerceOperationInvocationHandle,directory:string,
 options?:RuntimeOptions,
):Promise<CommerceGeneratedOperationRuntimeV1> {
 return createRuntime(sources,capture,stage,source,domain,baseline,plans,selected,storage,root,directory,options);
}
