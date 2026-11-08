/** C13 original workflow driver over checked source and original C11/C12 owners.
 * Every effect goes through a fresh Entry authorization and original runtime;
 * the journal records identities and commitments but never grants dispatch.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {canonicalJson,dataDigest,type Json} from '../profile-engine/contracts.js';
import type {BinderV1} from '../commerce/commerce-data-v1.js';
import type {GenericFixtureActor} from './entry-authorization.js';
import type {GenericTransactionApplicationRuntime,GenericCommandTransfer,GenericPreparedCommand} from './invocation-owner.js';
import {assertGenericWorkflowRuntimeSource,inspectGenericWorkflowEventDelivery,
  requireGenericEventReceiverCommitReceipt} from './execution-session.js';
import type {GenericWorkflowSourceContractV1,GenericWorkflowStepV1} from './workflow-source.js';
import {GenericWorkflowStore,type WorkflowClaim,type WorkflowRunIdentity,type WorkflowStep} from './workflow-store.js';
import type {GenericEventRelayOwner} from './event-relay.js';
import {requireGenericEventRelayClaim} from './event-relay.js';
import type {GenericCommandResultV1,GenericCommandInspectionV1} from './transaction-data-v1.js';
import {mayCompensateProviderFailure} from './provider-effect-evidence.js';
import {requireGenericWorkflowRuntime,type GenericCompositionHandle} from './public-sdk.js';
import type {GenericContinuationDecisionV1} from './capability-data-v1.js';

export interface GenericWorkflowStagePort {readonly kind:'original-workflow-stage-port/v1'}
export interface GenericWorkflowStageRequest {readonly instance_sha256:string;readonly step:string;readonly attempt:number;readonly fence:number;readonly input:Uint8Array;readonly deadline_ms:number;readonly assertCurrent:()=>void;readonly retry_of?:string}
export type GenericWorkflowStageObservation=Readonly<{kind:'observed';output:Uint8Array;dispatch_evidence?:'proven-not-dispatched'}|{kind:'not-dispatched'}|{kind:'unknown'}|{kind:'no-effect-retry';original_attempt:string;not_before_ms:number;deadline_ms:number}>;
export interface GenericWorkflowStageImplementation {readonly capability_sha256:string;readonly execute:(request:GenericWorkflowStageRequest)=>Promise<GenericWorkflowStageObservation>;readonly inspect:(request:GenericWorkflowStageRequest)=>Promise<GenericWorkflowStageObservation>;readonly retry?:(request:GenericWorkflowStageRequest)=>Promise<GenericWorkflowStageObservation>;readonly assertCurrent:()=>void}
const stagePorts=new WeakMap<object,{runtime:GenericTransactionApplicationRuntime;source:string;binding:string;implementation:GenericWorkflowStageImplementation;current:()=>void}>();
/** Trusted native host registration seam. The host first qualifies its exact
 * selected resource/codec. This join proves original composition/runtime custody;
 * serialized descriptors and arbitrary handle-shaped values never dispatch. */
export function registerGenericWorkflowStagePort(composition:unknown,handle:GenericCompositionHandle,runtime:GenericTransactionApplicationRuntime,binding:string,implementation:GenericWorkflowStageImplementation):GenericWorkflowStagePort{
 const original=requireGenericWorkflowRuntime(composition,handle),source=original.contract;
 assertGenericWorkflowRuntimeSource(runtime,source);
 const selected=source.steps.filter(s=>s.capability_binding===binding);
 if(!selected.length||!implementation||!Object.isFrozen(implementation)||Object.keys(implementation).sort().join(',')!==(['assertCurrent','capability_sha256','execute','inspect',...(Object.hasOwn(implementation,'retry')?['retry']:[])].sort().join(','))||Object.hasOwn(implementation,'retry')&&typeof implementation.retry!=='function'||typeof implementation.execute!=='function'||typeof implementation.inspect!=='function'||typeof implementation.assertCurrent!=='function')throw Error('R03_STAGE_REGISTRATION');
 if(!HEX.test(implementation.capability_sha256)||selected.some(s=>s.capability_sha256!==implementation.capability_sha256))throw Error('R03_STAGE_CAPABILITY_IDENTITY');
 implementation.assertCurrent();
 const port=Object.freeze({kind:'original-workflow-stage-port/v1' as const});
 stagePorts.set(port,{runtime,source:dataDigest(source),binding,implementation,current:()=>{original.assertCurrent();assertGenericWorkflowRuntimeSource(runtime,source);implementation.assertCurrent();}});return port;
}

const extension=extname(fileURLToPath(import.meta.url));
const workflowCodePin=pinCoreImplementation(import.meta.url,[
  'workflow-source'+extension,'workflow-store'+extension,'workflow-driver'+extension,'execution-session'+extension,
  'invocation-owner'+extension,'public-sdk'+extension,'repository-plan'+extension,
  'entry-authorization'+extension,'provider-effect-evidence'+extension,
  '../profile-engine/contracts'+extension]);
const HEX=/^[0-9a-f]{64}$/;
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
function fail(code:string):never{throw Error(code);}
function checkedInput(source:GenericWorkflowSourceContractV1,text:string):Record<string,Json>{
  if(typeof text!=='string'||Buffer.byteLength(text)>1048576)fail('C13_WORKFLOW_INPUT_BOUND');
  let value:unknown;
  try{value=JSON.parse(text);}catch{fail('C13_WORKFLOW_INPUT_JSON');}
  if(!value||typeof value!=='object'||Array.isArray(value)||canonicalJson(value as Json)!==text)
    fail('C13_WORKFLOW_INPUT_NONCANONICAL');
  const object=value as Record<string,Json>,names=Object.keys(object).sort(),expected=source.parameters.map(p=>p.name).sort();
  if(JSON.stringify(names)!==JSON.stringify(expected)||!Object.hasOwn(object,source.correlation))
    fail('C13_WORKFLOW_INPUT_PARAMETERS');
  return object;
}
function wireFor(input:Record<string,Json>,parameters:readonly BinderV1[]|undefined):Uint8Array{
  if(!parameters)fail('C13_WORKFLOW_STEP_PARAMETERS');
  const projected:Record<string,Json>={};
  for(const parameter of parameters){
    if(!Object.hasOwn(input,parameter.name))fail('C13_WORKFLOW_INPUT_PARAMETERS');
    projected[parameter.name]=input[parameter.name]!;
  }
  return Buffer.from(canonicalJson(projected as Json));
}
function storeSteps(source:GenericWorkflowSourceContractV1):WorkflowStep[]{
  return source.steps.map(step=>({name:step.name,entry_id:step.entry,
    entry_contract_sha256:step.entry_contract_sha256,
    kind:step.kind==='local-command'?'operation':step.kind==='provider-command'?'provider':step.kind==='model-command'?'model':step.kind==='document-command'?'document':step.kind==='index-command'?'index':step.kind==='agent-run-command'?'agent-run':'event',
    ...(step.kind==='provider-command'?{binding_sha256:dataDigest(step.provider_write_bindings??[])}:{}),
    ...(step.kind==='event-await'?{binding_sha256:step.event_binding_sha256!}:{}),
    ...(step.compensation_entry?{compensation_entry_id:step.compensation_entry,
      compensation_contract_sha256:step.compensation_contract_sha256!}:{}),
    ...(step.continuation_entry?{continuation_entry_id:step.continuation_entry,continuation_contract_sha256:step.continuation_contract_sha256!,maximum_attempts:step.maximum_attempts!}:{})}));
}
/** Durable identity uses the exact checked content closure. The live runtime
 * still compares the original physical capture and original owner in
 * assertGenericWorkflowRuntimeSource before every action. No serialized digest
 * can stand in for those handles. */
export function workflowPersistentContract(source:GenericWorkflowSourceContractV1):GenericWorkflowSourceContractV1{
  if(!HEX.test(source.source_closure_sha256))fail('C13_WORKFLOW_SOURCE_CLOSURE');
  return Object.freeze({...source,source_capture_sha256:source.source_closure_sha256});
}
export function workflowCompatibilitySha256(source:GenericWorkflowSourceContractV1):string{
  const persistent=workflowPersistentContract(source);
  workflowCodePin.assertCurrent();
  return dataDigest({implementation_sha256:workflowCodePin.sha256,workflow:source.workflow,service:source.service,
    source_capture_sha256:persistent.source_capture_sha256,profile_sha256:source.profile_sha256,
    base_application_sha256:source.base_application_sha256,contract_sha256:dataDigest(persistent)});
}
function expectedIdentity(source:GenericWorkflowSourceContractV1,inputCanonicalJson:string,
  clientKey:string,startTupleSha256:string):WorkflowRunIdentity{
  const input=checkedInput(source,inputCanonicalJson);
  return Object.freeze({workflow_id:source.workflow,owner_service:source.service,
    source_capture_sha256:source.source_closure_sha256,profile_sha256:source.profile_sha256,
    contract_sha256:dataDigest(workflowPersistentContract(source)),correlation_name:source.correlation,
    correlation_canonical_json:canonicalJson(input[source.correlation]!),
    start_client_key:clientKey,start_command_tuple_sha256:startTupleSha256,
    input_canonical_json:inputCanonicalJson,steps:storeSteps(source)});
}
function stepKey(instance:string,index:number,kind:'command'|'compensation'):string{
  return 'c13-'+sha(canonicalJson({instance,index,kind}));
}
function lastCommitment(history:readonly {step_index:number;commitment_json:string}[],kind:string,step:number):Record<string,unknown>{
  for(let index=history.length-1;index>=0;index--){
    const row=history[index]!;
    const value=JSON.parse(row.commitment_json) as Record<string,unknown>;
    if(value.kind===kind&&row.step_index===step)return value;
  }
  fail('C13_WORKFLOW_COMMITMENT_MISSING');
}
function lastEffectiveKind(history:readonly {commitment_json:string}[]):string{
  for(let index=history.length-1;index>=0;index--){
    const kind=(JSON.parse(history[index]!.commitment_json) as {kind:string}).kind;
    if(kind!=='claim'&&kind!=='renew-lease'&&kind!=='native-retry-release')return kind;
  }
  fail('C13_WORKFLOW_COMMITMENT_MISSING');
}
type Transfer=Readonly<{prepared:GenericPreparedCommand;transfer:GenericCommandTransfer;
  tuple_sha256:string;input_sha256:string}>;
export type WorkflowAdvanceResult=Readonly<{kind:'advanced'|'waiting-event'|'suspended-unknown'|'needs-review'|'completed'|'compensated'|'auth-unavailable'|'waiting-condition'|'retry-later'|'cancelled'|'rejected';
  instance_sha256:string;state:string;active_claim:WorkflowClaim|null}>;
export interface GenericWorkflowWorkerOptions {
  readonly source:GenericWorkflowSourceContractV1;
  readonly runtime:GenericTransactionApplicationRuntime;
  readonly journal:GenericWorkflowStore;
  readonly journal_store_id:string;
  readonly actors:ReadonlyMap<string,GenericFixtureActor>;
  readonly relay?:GenericEventRelayOwner;
  readonly receiver?:GenericTransactionApplicationRuntime;
  readonly stagePorts?:ReadonlyMap<string,GenericWorkflowStagePort>;
}

/** One worker instance binds one selected Workflow and one service-owned
 * journal. The actor map supplies original Auth owner handles, not verdicts. */
export function createGenericWorkflowWorker(options:GenericWorkflowWorkerOptions){
  const {source,runtime,journal,actors}=options;
  const originalPorts=new Map(options.stagePorts??[]);
  const current=()=>{
    assertGenericWorkflowRuntimeSource(runtime,source);
    journal.assertOwner({store_id:options.journal_store_id,owner_service:source.service,
      compatibility_sha256:workflowCompatibilitySha256(source)});
    for(const step of source.steps)if(step.capability_binding){const p=originalPorts.get(step.capability_binding),r=p&&stagePorts.get(p);if(!r||r.runtime!==runtime||r.source!==dataDigest(source)||r.binding!==step.capability_binding)fail('R03_ORIGINAL_STAGE_PORT_REQUIRED');r.current();}
  };
  current();
  const command=async(entryId:string,wire:Uint8Array,clientKey:string):Promise<Transfer|null>=>{
    current();
    const actor=actors.get(entryId);
    if(!actor)return null;
    const entry=runtime.entry(entryId),prepared=runtime.prepareCommand(entry,wire,{client_key:clientKey});
    try{
      const grant=await runtime.authorize(actor,prepared);
      if(!grant.ok){runtime.disposePrepared(prepared);return null;}
      const transfer=await runtime.consume(grant.value,prepared);
      if(!transfer.ok){runtime.disposePrepared(prepared);return null;}
      const identity=runtime.inspectTransferredCommandIdentity(transfer.value);
      current();
      if(!HEX.test(identity.command_tuple_sha256)||!HEX.test(identity.canonical_input_sha256))
        fail('C13_WORKFLOW_COMMAND_IDENTITY');
      return {prepared,transfer:transfer.value,tuple_sha256:identity.command_tuple_sha256,
        input_sha256:identity.canonical_input_sha256};
    }catch(error){try{runtime.disposePrepared(prepared);}catch{}throw error;}
  };
  const retire=(transfer:Transfer)=>{try{runtime.disposePrepared(transfer.prepared);}catch{/* transfer is already retired */}};
  const inspect=async(transfer:Transfer):Promise<GenericCommandInspectionV1>=>{
    try{return await runtime.inspectCommand(transfer.transfer);}finally{retire(transfer);}
  };
  const execute=async(transfer:Transfer):Promise<GenericCommandResultV1>=>{
    try{return await runtime.executeCommand(transfer.transfer);}finally{retire(transfer);}
  };
  const checkTuple=(actual:string,expected:string)=>{
    if(actual!==expected)fail('C13_WORKFLOW_ORIGINAL_COMMAND_CHANGED');
  };
  const resultKind=(result:GenericCommandResultV1):'success'|'definite-failure'|'unknown'|'unavailable'=>{
    if(result.ok){
      if(result.observation.kind==='committed'||result.observation.kind==='replayed')
        return result.outcome.kind==='Returned'?'success':'definite-failure';
      if(result.observation.kind==='business-rejected'||result.observation.kind==='business-failed'||
        result.observation.kind==='rolled-back')return 'definite-failure';
    }
    if(result.observation.kind==='indeterminate'||
      (!result.ok&&result.error.code==='ExternalOutcomeUnknown'))return 'unknown';
    return 'unavailable';
  };
  const mayCompensateFailedStep=(step:GenericWorkflowStepV1,result:GenericCommandResultV1)=>
    step.kind==='local-command'||mayCompensateProviderFailure(step,runtime.provesProviderNoEffect(result));
  // Renewal preserves the fence, but replaces the lease timestamp and thus
  // invalidates every older claim handle. Keep the new handle through an
  // entire advance, including the original command's potentially slow work.
  type Lease=Readonly<{claim:()=>WorkflowClaim;renew:()=>WorkflowClaim}>;
  const leaseFor=(initial:WorkflowClaim):Lease=>{
    let active=initial;
    return Object.freeze({claim:()=>active,renew:()=>{
      active=journal.renewClaim(active,300000);
      return active;
    }});
  };
  const progress=(lease:Lease,kind:WorkflowAdvanceResult['kind']):WorkflowAdvanceResult=>{
    const claim=lease.claim(),after=journal.inspect(claim.instance_sha256);
    const active_claim=after.lease_until_ms>0&&!['completed','compensated','needs-review','cancelled','rejected'].includes(after.state)?lease.renew():null;
    return Object.freeze({kind,instance_sha256:claim.instance_sha256,state:after.state,active_claim});
  };
  const attemptFor=(snapshot:ReturnType<GenericWorkflowStore['inspect']>,index:number)=>1+snapshot.history.filter(row=>row.step_index===index&&(JSON.parse(row.commitment_json) as {kind:string}).kind==='retry-stage').length;
  const commitSuccessfulStep=async(lease:Lease,index:number,outcome:string,value:Json,compensation:boolean):Promise<WorkflowAdvanceResult>=>{
    if(compensation){journal.commitCompensation(lease.renew(),outcome);return progress(lease,'advanced');}
    const step=source.steps[index]!;
    if(!step.continuation_entry){journal.commitStep(lease.renew(),outcome);return progress(lease,'advanced');}
    let output=canonicalJson(value),evidence:'proven-not-dispatched'|undefined;
    if(step.capability_binding){
      const port=originalPorts.get(step.capability_binding)!,registered=stagePorts.get(port)!;
      const snapshot=journal.assertClaimCurrent(lease.renew());
      const nativeRetry=lastEffectiveKind(snapshot.history)==='native-retry-resume',retryCommitment=nativeRetry?lastCommitment(snapshot.history,'native-retry-resume',index):null;
      const request:GenericWorkflowStageRequest=Object.freeze({instance_sha256:snapshot.instance_sha256,step:step.name,attempt:attemptFor(snapshot,index),fence:lease.claim().fence,input:Buffer.from(output),deadline_ms:nativeRetry?Math.min(Number(retryCommitment!.deadline_ms),Date.now()+step.deadline_ms!):Date.now()+step.deadline_ms!,...(nativeRetry?{retry_of:String(retryCommitment!.original_attempt)}:{}),assertCurrent:()=>{current();journal.assertClaimCurrent(lease.claim());}});
      let timer:ReturnType<typeof setTimeout>|undefined;
      const bounded=async(fn:()=>Promise<GenericWorkflowStageObservation>)=>{
        request.assertCurrent();registered.current();
        try{return await Promise.race([Promise.resolve().then(fn),new Promise<GenericWorkflowStageObservation>(resolve=>{timer=setTimeout(()=>resolve({kind:'unknown'}),Math.max(1,request.deadline_ms-Date.now()));})]);}
        finally{if(timer)clearTimeout(timer);}
      };
      let observation:GenericWorkflowStageObservation;
      if(nativeRetry){if(!registered.implementation.retry)fail('R03_STAGE_RETRY_UNAVAILABLE');observation=await bounded(()=>registered.implementation.retry!(request));request.assertCurrent();}
      else{observation=await bounded(()=>registered.implementation.inspect(request));request.assertCurrent();if(observation.kind==='not-dispatched'){observation=await bounded(()=>registered.implementation.execute(request));request.assertCurrent();}}
      if(observation.kind==='no-effect-retry'){
        if(!registered.implementation.retry)fail('R03_STAGE_RETRY_UNAVAILABLE');if(observation.deadline_ms>request.deadline_ms)fail('R03_NATIVE_RETRY_BOUND');
        journal.waitNativeRetry(lease.renew(),{original_attempt:observation.original_attempt,not_before_ms:observation.not_before_ms,deadline_ms:observation.deadline_ms});return progress(lease,'retry-later');
      }
      if(observation.kind!=='observed'){
        const now=journal.assertClaimCurrent(lease.renew());if(now.state==='step-prepared')journal.suspendUnknown(lease.renew());
        return progress(lease,'suspended-unknown');
      }
      if(!(observation.output instanceof Uint8Array)||observation.output.byteLength>32768)fail('R03_STAGE_OUTPUT_BOUND');
      let decoded:Json;try{decoded=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(observation.output)) as Json;}catch{return fail('R03_STAGE_OUTPUT_INVALID');}
      output=canonicalJson(decoded);outcome=sha(output);evidence=observation.dispatch_evidence;
    }
    journal.commitStep(lease.renew(),outcome,output,evidence);return progress(lease,'advanced');
  };
  const continuationDecision=(value:Json,outcome:string,step:GenericWorkflowStepV1,snapshot:ReturnType<GenericWorkflowStore['inspect']>):GenericContinuationDecisionV1=>{
    if(!value||typeof value!=='object'||Array.isArray(value)||!('kind'in value)||typeof value.kind!=='string')fail('R03_CONTINUATION_RESULT');
    const v=value as Record<string,Json>,kind=v.kind;
    const reason=(key:string)=>{const s=v[key];if(typeof s!=='string'||!/^[A-Za-z_][A-Za-z0-9_.-]{0,255}$/.test(s))fail('R03_CONTINUATION_RESULT');return s;};
    const integer=(key:string)=>{const n=v[key];if(typeof n!=='string'||!/^(0|[1-9][0-9]{0,15})$/.test(n)||!Number.isSafeInteger(Number(n)))fail('R03_CONTINUATION_RESULT');return Number(n);};
    if(kind==='advance'||kind==='complete')return {kind,result_sha256:outcome};
    if(kind==='business-rejection')return {kind,code:reason('code')};
    if(kind==='wait')return {kind,condition:reason('condition'),deadline_ms:integer('deadline_ms')};
    if(kind==='review'||kind==='unknown'||kind==='cancel')return {kind,reason:reason('reason')};
    if(kind==='retry'){
      const committed=lastCommitment(snapshot.history,'commit-step',snapshot.step_index);
      if(step.capability_binding&&committed.dispatch_evidence!=='proven-not-dispatched')fail('R03_RETRY_REQUIRES_NO_DISPATCH');
      return {kind,attempt:integer('attempt'),maximum:integer('maximum'),not_before_ms:integer('not_before_ms'),dispatch_evidence:'proven-not-dispatched'};
    }
    return fail('R03_CONTINUATION_RESULT');
  };
  const continueStage=async(lease:Lease,index:number):Promise<WorkflowAdvanceResult>=>{
    current();let snapshot=journal.assertClaimCurrent(lease.renew());const step=source.steps[index]!;
    if(!step.continuation_entry||!step.continuation_parameters)fail('R03_CONTINUATION_SOURCE');
    if(snapshot.state==='waiting-condition'){
      const prior=lastCommitment(snapshot.history,'continuation-decision',index).decision as {kind:string;deadline_ms:number};
      if(Date.now()>=prior.deadline_ms){journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');}
    }
    const prior=snapshot.state==='continuation-prepared'?lastCommitment(snapshot.history,'prepare-continuation',index):null;
    const ordinal=prior?Number(prior.ordinal):snapshot.history.filter(row=>row.step_index===index&&(JSON.parse(row.commitment_json) as {kind:string}).kind==='prepare-continuation').length+1;
    const output=lastCommitment(snapshot.history,'commit-step',index).output_canonical_json;
    if(typeof output!=='string')fail('R03_STAGE_OUTPUT_MISSING');
    const input={...checkedInput(source,snapshot.identity.input_canonical_json),stageResult:JSON.parse(output) as Json,stageAttempt:String(attemptFor(snapshot,index)),stageRevision:String(ordinal)};
    const wire=wireFor(input,step.continuation_parameters),key='r03-'+sha(canonicalJson({instance:snapshot.instance_sha256,index,continuation:ordinal}));
    let transfer=await command(step.continuation_entry,wire,key);if(!transfer)return progress(lease,'auth-unavailable');
    if(prior){
      checkTuple(transfer.tuple_sha256,prior.command_tuple_sha256 as string);if(transfer.input_sha256!==prior.input_sha256)fail('R03_CONTINUATION_INPUT_CHANGED');
      const observed=await inspect(transfer);lease.renew();
      if(observed.kind==='committed'){
        if(observed.outcome.kind!=='Returned'){journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');}
        snapshot=journal.assertClaimCurrent(lease.renew());const decision=continuationDecision(observed.outcome.value as Json,observed.result_sha256,step,snapshot);
        journal.commitContinuation(lease.renew(),decision,observed.result_sha256);return progress(lease,decision.kind==='advance'?'advanced':decision.kind==='business-rejection'?'rejected':decision.kind==='wait'?'waiting-condition':decision.kind==='retry'?'retry-later':decision.kind==='cancel'?'cancelled':decision.kind==='complete'?'completed':'needs-review');
      }
      if(observed.kind!=='not-committed')return progress(lease,'suspended-unknown');
      transfer=await command(step.continuation_entry,wire,key);if(!transfer)return progress(lease,'auth-unavailable');
      checkTuple(transfer.tuple_sha256,prior.command_tuple_sha256 as string);
    }else journal.prepareContinuation(lease.renew(),transfer.tuple_sha256,transfer.input_sha256);
    const result=await execute(transfer);lease.renew();
    if(!result.ok||result.outcome.kind!=='Returned'||!['committed','replayed'].includes(result.observation.kind)){
      if(resultKind(result)==='definite-failure'){journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');}
      return progress(lease,'suspended-unknown');
    }
    if(!('result_sha256'in result.observation))fail('R03_CONTINUATION_RESULT');
    snapshot=journal.assertClaimCurrent(lease.renew());const decision=continuationDecision(result.outcome.value as Json,result.observation.result_sha256,step,snapshot);
    journal.commitContinuation(lease.renew(),decision,result.observation.result_sha256);
    return progress(lease,decision.kind==='advance'?'advanced':decision.kind==='business-rejection'?'rejected':decision.kind==='wait'?'waiting-condition':decision.kind==='retry'?'retry-later':decision.kind==='cancel'?'cancelled':decision.kind==='complete'?'completed':'needs-review');
  };
  const nextCommand=async(lease:Lease,index:number,compensation:boolean):Promise<WorkflowAdvanceResult>=>{
    current();
    const snapshot=journal.assertClaimCurrent(lease.renew()),input=checkedInput(source,snapshot.identity.input_canonical_json),step=source.steps[index];
    if(!step||step.kind==='event-await')fail('C13_WORKFLOW_STEP_SOURCE');
    const entryId=compensation?step.compensation_entry:step.entry;
    const parameters=compensation?step.compensation_parameters:step.parameters;
    if(!entryId)fail('C13_WORKFLOW_COMPENSATION_SOURCE');
    const attempt=attemptFor(snapshot,index)+(snapshot.state==='retry-later'?1:0);
    const wire=wireFor({...input,stageAttempt:String(attempt)},parameters),baseKey=stepKey(lease.claim().instance_sha256,index,compensation?'compensation':'command'),key=attempt===1?baseKey:baseKey+'-'+attempt;
    const prepared=compensation?snapshot.state==='compensating'&&
      lastEffectiveKind(snapshot.history)==='prepare-compensation':
      snapshot.state==='step-prepared'||snapshot.state==='suspended-unknown';
    const prior=prepared?lastCommitment(snapshot.history,
      compensation?'prepare-compensation':attempt>1?'retry-stage':'prepare-step',index):null;
    const transfer=await command(entryId,wire,key);
    if(!transfer)return progress(lease,'auth-unavailable');
    try{
    lease.renew();
    if(prior){
      checkTuple(transfer.tuple_sha256,prior.command_tuple_sha256 as string);
      if(transfer.input_sha256!==prior.input_sha256)fail('C13_WORKFLOW_INPUT_CHANGED');
      const observation=await inspect(transfer);
      lease.renew();
      checkTuple(observation.command_tuple_sha256,transfer.tuple_sha256);
      if(observation.kind==='committed'){
        if(observation.outcome.kind==='Returned'){
          return commitSuccessfulStep(lease,index,observation.result_sha256,observation.outcome.value as Json,compensation);
        }
        if(compensation){journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');}
        if(step.kind==='provider-command')journal.needsReview(lease.renew(),'external-reconciliation');
        else journal.definiteStepFailure(lease.renew(),observation.result_sha256);
        return progress(lease,step.kind==='provider-command'?'needs-review':'advanced');
      }
      if(observation.kind==='unavailable'||observation.kind==='fault'){
        if(!compensation&&snapshot.state==='step-prepared')journal.suspendUnknown(lease.renew());
        return progress(lease,'suspended-unknown');
      }
      // A proven not-committed transaction still re-enters the original C11
      // path with the exact same key; that owner inspects the durable effect.
    }else{
      if(compensation)journal.prepareCompensation(lease.renew(),step.name,transfer.tuple_sha256,transfer.input_sha256);
      else if(snapshot.state==='retry-later')journal.prepareRetryStep(lease.renew(),transfer.tuple_sha256,transfer.input_sha256);
      else journal.prepareStep(lease.renew(),step.name,transfer.tuple_sha256,transfer.input_sha256);
      // Transfer was authenticated before journal preparation and has not
      // dispatched yet. Execute this exact transfer after the durable write.
      const result=await execute(transfer);
      lease.renew();
      checkTuple(result.observation.command_tuple_sha256,transfer.tuple_sha256);
      const kind=resultKind(result);
      if(kind==='success'){
        if(!result.ok||result.outcome.kind!=='Returned'||!('result_sha256'in result.observation))fail('C13_WORKFLOW_RESULT');
        return commitSuccessfulStep(lease,index,result.observation.result_sha256,result.outcome.value as Json,compensation);
      }
      if(kind==='definite-failure'){
        const compensate=!compensation&&mayCompensateFailedStep(step,result);
        if(!compensate)journal.needsReview(lease.renew(),'external-reconciliation');
        else journal.definiteStepFailure(lease.renew(),result.observation.kind==='business-rejected'||result.observation.kind==='business-failed'||result.observation.kind==='rolled-back'?('result_sha256'in result.observation?result.observation.result_sha256:sha(canonicalJson(result as Json))):sha(canonicalJson(result as Json)));
        return progress(lease,compensate?'advanced':'needs-review');
      }
      if(!compensation)journal.suspendUnknown(lease.renew());
      return progress(lease,compensation?'auth-unavailable':'suspended-unknown');
    }
    // Inspection consumed the first transfer. A fresh READY frame is needed
    // before executing the original key; the tuple and input must still match.
    const retry=await command(entryId,wire,key);
    if(!retry)return progress(lease,'auth-unavailable');
    try{
    lease.renew();
    checkTuple(retry.tuple_sha256,prior!.command_tuple_sha256 as string);
    if(retry.input_sha256!==prior!.input_sha256)fail('C13_WORKFLOW_INPUT_CHANGED');
    const result=await execute(retry);
    lease.renew();
    checkTuple(result.observation.command_tuple_sha256,retry.tuple_sha256);
    const kind=resultKind(result);
    if(kind==='success'){
      const observation=result.observation;
      if(observation.kind!=='committed'&&observation.kind!=='replayed')fail('C13_WORKFLOW_RESULT');
      if(!result.ok||result.outcome.kind!=='Returned')fail('C13_WORKFLOW_RESULT');
      return commitSuccessfulStep(lease,index,observation.result_sha256,result.outcome.value as Json,compensation);
    }
    if(kind==='definite-failure'){
      const compensate=!compensation&&mayCompensateFailedStep(step,result);
      if(!compensate)journal.needsReview(lease.renew(),'external-reconciliation');
      else journal.definiteStepFailure(lease.renew(),'result_sha256'in result.observation?result.observation.result_sha256:sha(canonicalJson(result as Json)));
      return progress(lease,compensate?'advanced':'needs-review');
    }
    if(!compensation&&snapshot.state==='step-prepared')journal.suspendUnknown(lease.renew());
    return progress(lease,compensation?'auth-unavailable':'suspended-unknown');
    }catch(error){retire(retry);throw error;}
    }catch(error){retire(transfer);throw error;}
  };
  const advance=async(claim:WorkflowClaim):Promise<WorkflowAdvanceResult>=>{
    const lease=leaseFor(claim);
    current();
    const snapshot=journal.assertClaimCurrent(lease.renew()),index=snapshot.step_index;
    if(snapshot.identity.contract_sha256!==dataDigest(workflowPersistentContract(source))||
      snapshot.identity.source_capture_sha256!==source.source_closure_sha256||
      snapshot.identity.profile_sha256!==source.profile_sha256||
      canonicalJson(storeSteps(source) as Json)!==canonicalJson(snapshot.identity.steps as Json))
      fail('C13_WORKFLOW_SOURCE_CHANGED');
    if(snapshot.state==='claimed'){
      const input=checkedInput(source,snapshot.identity.input_canonical_json),wire=wireFor(input,source.start_parameters);
      const transferred=await command(source.start_entry,wire,snapshot.identity.start_client_key);
      if(!transferred)return progress(lease,'auth-unavailable');
      checkTuple(transferred.tuple_sha256,snapshot.identity.start_command_tuple_sha256);
      const observed=await inspect(transferred);
      lease.renew();
      checkTuple(observed.command_tuple_sha256,transferred.tuple_sha256);
      if(observed.kind==='committed'&&observed.outcome.kind==='Returned')
        return nextCommand(lease,0,false);
      if(observed.kind==='committed'){
        journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');
      }
      if(observed.kind==='not-committed'){
        const retry=await command(source.start_entry,wire,snapshot.identity.start_client_key);
        if(!retry)return progress(lease,'auth-unavailable');
        checkTuple(retry.tuple_sha256,snapshot.identity.start_command_tuple_sha256);
        const result=await execute(retry);
        lease.renew();
        checkTuple(result.observation.command_tuple_sha256,retry.tuple_sha256);
        if(resultKind(result)==='success')return nextCommand(lease,0,false);
        if(resultKind(result)==='definite-failure'){
          journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');
        }
      }
      return progress(lease,'auth-unavailable');
    }
    if(snapshot.state==='step-prepared'||snapshot.state==='suspended-unknown')return nextCommand(lease,index,false);
    if(snapshot.state==='continuation-prepared'||snapshot.state==='waiting-condition')return continueStage(lease,index);
    if(snapshot.state==='retry-later'){
      if(lastEffectiveKind(snapshot.history)==='native-no-effect-wait'){
        const pending=lastCommitment(snapshot.history,'native-no-effect-wait',index);
        if(Date.now()>=Number(pending.deadline_ms)){journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');}
        if(Date.now()<Number(pending.not_before_ms)){journal.releaseNativeRetry(lease.renew());return progress(lease,'retry-later');}
        journal.resumeNativeRetry(lease.renew());return nextCommand(lease,index,false);
      }
      const prior=lastCommitment(snapshot.history,'continuation-decision',index).decision as {kind:string;not_before_ms:number};
      if(Date.now()<prior.not_before_ms)return progress(lease,'retry-later');
      return nextCommand(lease,index,false);
    }
    if(snapshot.state==='step-committed'){
      if(source.steps[index]?.continuation_entry&&lastEffectiveKind(snapshot.history)!=='continuation-decision')return continueStage(lease,index);
      if(index===source.steps.length-1){journal.complete(lease.renew());return progress(lease,'completed');}
      const next=source.steps[index+1]!;
      if(next.kind==='event-await'){
        journal.waitForEvent(lease.renew(),next.name);return progress(lease,'waiting-event');
      }
      return nextCommand(lease,index+1,false);
    }
    if(snapshot.state==='compensating'){
      if(index<0){journal.finishCompensation(lease.renew());return progress(lease,'compensated');}
      return nextCommand(lease,index,true);
    }
    if(snapshot.state==='waiting-event'){
      const step=source.steps[index];
      if(!step||step.kind!=='event-await'||!step.event_binding||!options.receiver)
        return progress(lease,'waiting-event');
      // V4 reopen deliberately delays the full producer store until fresh
      // original Auth reaches READY. Re-enter the scheduled start identity
      // without dispatching it, then inspect the original Event owners.
      const startInput=checkedInput(source,snapshot.identity.input_canonical_json);
      const ready=await command(source.start_entry,wireFor(startInput,source.start_parameters),
        snapshot.identity.start_client_key);
      if(!ready)return progress(lease,'auth-unavailable');
      let startObservation:GenericCommandInspectionV1;
      try{
      lease.renew();
      checkTuple(ready.tuple_sha256,snapshot.identity.start_command_tuple_sha256);
      startObservation=await inspect(ready);
      lease.renew();
      }catch(error){retire(ready);throw error;}
      checkTuple(startObservation.command_tuple_sha256,snapshot.identity.start_command_tuple_sha256);
      if(startObservation.kind==='committed'&&startObservation.outcome.kind!=='Returned'){
        journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');
      }
      if(startObservation.kind!=='committed')return progress(lease,'auth-unavailable');
      const eventRelay=options.relay??runtime.openEventRelay();
      try{
      const provider=lastCommitment(snapshot.history,'prepare-step',index-1),
        causal=provider.command_tuple_sha256 as string;
      if(!HEX.test(causal))fail('C13_WORKFLOW_CAUSAL_IDENTITY');
      const acknowledged=await inspectGenericWorkflowEventDelivery(runtime,options.receiver,source,
        step.event_binding,causal);
      lease.renew();
      if(acknowledged.kind==='acknowledged'){
        journal.commitEvent(lease.renew(),acknowledged.occurrence_sha256,acknowledged.consumer_command_tuple_sha256);
        return progress(lease,'advanced');
      }
      if(acknowledged.kind==='collision'){
        journal.needsReview(lease.renew(),'external-reconciliation');return progress(lease,'needs-review');
      }
      if(acknowledged.kind!=='pending')return progress(lease,'waiting-event');
      const relayClaim=eventRelay.claimWorkflowEvent(step.event_binding,causal,300000);
      if(!relayClaim)return progress(lease,'waiting-event');
      const envelope=requireGenericEventRelayClaim(eventRelay,relayClaim).envelope;
      if(envelope.causal_command_tuple_sha256!==causal||envelope.binding_ref!==step.event_binding||
        envelope.binding_sha256!==step.event_binding_sha256||envelope.target_entry!==step.entry)
        fail('C13_WORKFLOW_EVENT_MISMATCH');
      const delivered=await eventRelay.deliver(relayClaim,options.receiver);
      lease.renew();
      if(!('receipt' in delivered))return progress(lease,'waiting-event');
      const receipt=requireGenericEventReceiverCommitReceipt(delivered.receipt,eventRelay,relayClaim);
      if(receipt.occurrence_sha256!==envelope.occurrence_sha256||receipt.envelope_sha256!==envelope.envelope_sha256)
        fail('C13_WORKFLOW_EVENT_RECEIPT');
      lease.renew();
      eventRelay.ack(relayClaim,delivered.receipt);
      const after=await inspectGenericWorkflowEventDelivery(runtime,options.receiver,source,
        step.event_binding,causal);
      lease.renew();
      if(after.kind!=='acknowledged')return progress(lease,'waiting-event');
      if(after.occurrence_sha256!==receipt.occurrence_sha256||
        after.consumer_command_tuple_sha256!==receipt.consumer_command_tuple_sha256)
        fail('C13_WORKFLOW_EVENT_RECEIPT');
      journal.commitEvent(lease.renew(),after.occurrence_sha256,after.consumer_command_tuple_sha256);
      return progress(lease,'advanced');
      }finally{if(!options.relay)eventRelay.close();}
    }
    fail('C13_WORKFLOW_STATE');
  };
  const scheduleStart=async(inputCanonicalJson:string,clientKey:string):Promise<{instance_sha256:string;created:boolean;result:GenericCommandResultV1}|null>=>{
    current();
    const input=checkedInput(source,inputCanonicalJson),wire=wireFor(input,source.start_parameters),
      transferred=await command(source.start_entry,wire,clientKey);
    if(!transferred)return null;
    try{
    const identity=expectedIdentity(source,inputCanonicalJson,clientKey,transferred.tuple_sha256);
    if(transferred.input_sha256!==sha(Buffer.from(wire).toString('utf8')))
      fail('C13_WORKFLOW_START_INPUT_CHANGED');
    const scheduled=journal.schedule(identity);
    const result=await execute(transferred);
    checkTuple(result.observation.command_tuple_sha256,identity.start_command_tuple_sha256);
    return {...scheduled,result};
    }catch(error){retire(transferred);throw error;}
  };
  return Object.freeze({scheduleStart,claimNext:(leaseMs:number)=>{current();return journal.claimNext(leaseMs);},
    renewClaim:(claim:WorkflowClaim,leaseMs:number)=>{current();return journal.renewClaim(claim,leaseMs);},
    advance,inspect:(id:string)=>{current();return journal.inspect(id);}});
}
