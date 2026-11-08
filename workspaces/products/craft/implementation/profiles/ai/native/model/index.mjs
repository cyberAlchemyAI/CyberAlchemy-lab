import {createEffectDispatcher} from '../effects/index.mjs';
import {createSelectedOpenAITransport,projectStrictSchema} from './transport.mjs';
import {canonical,digest} from '../source-release/index.mjs';
import {capture,copyBytes,freeze,assert,count,text} from '../shared.mjs';

export const INFERENCE_ABI='inference-port/v1';
const operations=['text.generate','text.structured','vector.embed'];
const unknownUsage=()=>({input_tokens:null,output_tokens:null,cache_read_tokens:null,reasoning_tokens:null});

/** Generated host supplies original checked tenant/context/codec custody. This
 * runtime never authenticates caller JSON or executes authored business rules.
 * Every paid call traverses source release, the one exposure owner and R02.
 * Open Questions: README.md. */
export function createInferenceRuntime({path,client,resource:rawResource,sourceRelease,exposure,assertCurrent:hostCurrent,observer,now=Date.now,policy={}}) {
 const resource=freeze(capture(rawResource));for(const k of ['id','account','billingAccount','tenant','application','preprocessing','generation','pricePolicyRevision'])text(resource[k],k);
 assert(resource.provider==='openai'&&['fixture','provider'].includes(resource.mode),'UnsupportedCapability','selected OpenAI resource and actual mode');
 count(resource.maxTokens,'maxTokens');assert(resource.maxTokens>0,'InvalidContract','positive token exposure');
 const maxOutputTokens=resource.maxOutputTokens??Math.min(4096,Math.floor(resource.maxTokens/2));count(maxOutputTokens,'maxOutputTokens');assert(maxOutputTokens>0,'InvalidContract','positive output bound');
 const inputOverheadTokens=resource.inputOverheadTokens??128;count(inputOverheadTokens,'inputOverheadTokens',65536);assert(inputOverheadTokens>=128,'InvalidContract','minimum selected request-envelope allowance');
 const transport=createSelectedOpenAITransport({client,model:resource.model,embedding_model:resource.embeddingModel,dimensions:resource.dimensions,timeout_ms:resource.timeoutMs??30000,maximum_output_tokens:maxOutputTokens});
 assert(sourceRelease?.abi==='source-release-port/v1'&&exposure?.abi==='model-exposure-ledger/v1'&&typeof hostCurrent==='function','ForeignOwner','original source/exposure/current owners');
 let closed=false;
 const current=b=>{assert(!closed&&hostCurrent(b)===true,'StaleOwner','current original execution authority');if(b)assert(b.tenant===resource.tenant&&b.resourceId===resource.id,'ForeignOwner','selected resource scope');return true;};
 const resourceIdentity=freeze({runtime_id:resource.runtimeId??'inference:'+resource.id,tenant:resource.tenant,application:resource.application,resource_id:resource.id,mode:resource.mode});
 async function execute(ctx){
  const owned=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(ctx.payload));current(ctx.binding);
  const result=await transport.invoke({operation:owned.operation,input:new TextEncoder().encode(owned.prompt),result_schema:owned.resultSchema,signal:ctx.signal,max_output_tokens:owned.maxOutputTokens,tools:[],store:false});
  if(ctx.signal.aborted)return {kind:'unknown',reason:'cancelled',result};
  return result.kind==='unknown'||result.kind==='unavailable'?{kind:'unknown',reason:result.reason??'provider-unknown',result}:
   {kind:'confirmed',receipt:result.response_id??'native-observation:'+digest(canonical(result)),result};
 }
 const dispatcher=createEffectDispatcher({path,releasePort:sourceRelease,assertCurrent:current,observer,now,policy,
  slots:operations.map(operation=>({id:operation,kind:'model',provider:'openai',account:resource.account,operation,resourceId:resource.id,action:operation,sink:'openai',recipient:resource.account,execute,
   validateObservation:o=>o.kind==='confirmed'&&typeof o.receipt==='string'&&o.result&&['candidate','refusal','incomplete','invalid'].includes(o.result.kind)}))});
 async function decodedResult(outcome,request,reservation,attemptId,{readOnly=false}={}){
  let result=outcome.result??{kind:'unknown',reason:outcome.reason??'dispatch-unknown',usage:unknownUsage(),response_id:null};
  const usage=result.usage??unknownUsage();
  if(!readOnly&&Number.isSafeInteger(usage.input_tokens)&&Number.isSafeInteger(usage.output_tokens)){
   exposure.observeUsage(reservation,{attemptId,fence:request.context.fence,inputTokens:usage.input_tokens,outputTokens:usage.output_tokens,receiptId:result.response_id??'native-observation:'+digest(canonical(result))});
  }else if(!readOnly)exposure.markUnknown(reservation,{attemptId,fence:request.context.fence,reason:'usage-unknown'});
  current();
  const accounting=readOnly?null:exposure.inspect(reservation);
  const base={abi:INFERENCE_ABI,attemptId,...(reservation?{reservationId:reservation.id}:{}),usage,exposure:accounting?.exposure??null,...(readOnly?{exposure_state:'original-ledger-not-read'}:{}),usage_state:usage.input_tokens===null||usage.output_tokens===null?'unknown':'observed',resource:resourceIdentity,model:request.operation==='vector.embed'?resource.embeddingModel:resource.model,
   ...(request.operation==='vector.embed'?{embeddingSpace:{model:resource.embeddingModel,dimensions:resource.dimensions,preprocessing:resource.preprocessing,generation:resource.generation}}:{})};
  if(outcome.kind==='unknown'&&result.kind==='candidate')return freeze({...base,kind:'unknown',reason:'dispatch-authority-unknown'});
  if(result.kind!=='candidate')return freeze({...base,kind:result.kind,reason:result.reason??'provider-outcome'});
  const wire=Uint8Array.from(result.wire??[]);if(wire.byteLength>request.limits.max_output_bytes)return freeze({...base,kind:'invalid',reason:'output-byte-bound'});
  assert(typeof request.decodeResult==='function','ForeignOwner','original generated result decoder');
  const checked=await request.decodeResult(wire);current();if(request.signal?.aborted||now()>=request.deadline_ms)return freeze({...base,kind:'unknown',reason:'cancelled-or-deadline'});
  if(!checked?.ok||!(checked.wire instanceof Uint8Array))return freeze({...base,kind:'invalid',reason:'generated-business-result-codec'});
  return Object.freeze({...base,kind:'candidate',value:checked.value,wire:new Uint8Array(checked.wire)});
 }
 function invocation(request){
   current();const {context}=request;assert(context&&context.tenant===resource.tenant,'ForeignOwner','generated original authority context');
   for(const k of ['principal','approvalRevision','sourceRevision','policyId'])text(context[k],k);count(context.fence,'fence');
   text(request.intentId,'intentId');text(request.bindingId,'bindingId');assert(operations.includes(request.operation),'UnsupportedCapability','finite inference operation');
   assert(typeof request.decodeResult==='function','ForeignOwner','generated result decoder before I/O');
   const limits=capture(request.limits);for(const k of ['max_input_bytes','max_output_bytes'])count(limits[k],k,1048576);
   assert(!limits.max_tool_calls&&limits.max_model_attempts===1,'UnsupportedCapability','tools disabled and one attempt owner');
   count(request.deadline_ms,'deadline');assert(request.deadline_ms>now()&&request.deadline_ms-now()<=(resource.timeoutMs??30000),'StaleOwner','bounded current deadline');
   if(request.signal?.aborted)return {cancelled:true};
   const input=copyBytes(request.input,limits.max_input_bytes);let inputText;try{inputText=new TextDecoder('utf-8',{fatal:true}).decode(input);}catch{assert(false,'InvalidContract','UTF8 generated input');}
   const strictProjection=request.operation==='text.structured'?projectStrictSchema(request.result_schema):null;
   const resultSchema=capture(request.result_schema);
   if(request.operation==='text.generate')assert(resultSchema.type==='string','UnsupportedCapability','text generation requires original string result');
   if(request.operation==='vector.embed')assert(resultSchema.type==='array'&&resultSchema.minItems===1536&&resultSchema.maxItems===1536,'UnsupportedCapability','exact selected vector dimensions');
   const prompt=resource.promptTemplate?canonical({instruction:resource.promptTemplate,input:inputText}):inputText;
   const conservativeInput=Buffer.byteLength(prompt)+(strictProjection?Buffer.byteLength(canonical(strictProjection.schema)):0)+inputOverheadTokens,output=request.operation==='vector.embed'?0:maxOutputTokens;
   assert(conservativeInput+output<=resource.maxTokens,'ResourceLimit','declared maximum token exposure must cover input and output');
   sourceRelease.describeManifest(context.manifest);
   const payload=new TextEncoder().encode(canonical({operation:request.operation,prompt,resultSchema,limits,policyId:context.policyId,bindingId:request.bindingId,model:request.operation==='vector.embed'?resource.embeddingModel:resource.model,maxOutputTokens,preprocessing:resource.preprocessing,generation:resource.generation}));
   const prepareRequest={intentId:request.intentId,slotId:request.operation,tenant:context.tenant,principal:context.principal,resourceId:resource.id,action:request.operation,approvalRevision:context.approvalRevision,sourceRevision:context.sourceRevision,fence:context.fence,payload,deadlineAt:request.deadline_ms,cause:{binding:request.bindingId,operation:request.operation,manifestId:context.manifest.id}};
   return {context,limits,input,prompt,payload,prepareRequest};
 }
 const runtime=Object.freeze({
  abi:INFERENCE_ABI,
  inspect(){current();return resourceIdentity;},
  assertCurrent(){current();},
  async invoke(request){
   const preparedInvocation=invocation(request);if(preparedInvocation.cancelled)return freeze({abi:INFERENCE_ABI,kind:'unknown',reason:'cancelled-before-dispatch',usage:unknownUsage(),usage_state:'unknown'});
   const {context,limits,input,prompt,payload,prepareRequest}=preparedInvocation;const prepared=dispatcher.prepare(prepareRequest);
   const attemptId=prepared.attemptId;
   const reservation=exposure.reserve({requestId:request.intentId,attemptId,billingAccount:resource.billingAccount,tenant:resource.tenant,application:resource.application,modelId:request.operation==='vector.embed'?resource.embeddingModel:resource.model,promptSha256:digest(prompt),inputSha256:digest(input),payloadSha256:digest(payload),destination:'openai',resourceId:resource.id,fence:context.fence,maxTokens:resource.maxTokens,...(resource.maxCostMicros===undefined?{}:{maxCostMicros:resource.maxCostMicros,pricePolicyRevision:resource.pricePolicyRevision}),...(request.runId?{runId:request.runId,childId:request.childId}:{})});
   const prior=dispatcher.getAttempt(attemptId);
   if(prepared.kind==='existing'){
    if(prior.observation)return decodedResult(prior.observation,request,reservation,attemptId);
    exposure.markUnknown(reservation,{attemptId,fence:context.fence,reason:'reopened-original-attempt'});return freeze({abi:INFERENCE_ABI,kind:'unknown',reason:'original-provider-inspection-required',attemptId,reservationId:reservation.id,exposure:exposure.inspect(reservation).exposure,usage:unknownUsage(),usage_state:'unknown'});
   }
   const ticket=sourceRelease.issueRelease({manifest:context.manifest,policyId:context.policyId,attemptId,fence:context.fence,resourceId:resource.id,action:request.operation,sink:'openai',recipient:resource.account,payload,expiresAt:Math.min(request.deadline_ms,now()+300000)});
   exposure.markRelease(reservation,{ticket});
   const outcome=await exposure.dispatch({reservation,dispatcher,attemptId,ticket,signal:request.signal});current();
   return decodedResult(outcome,request,reservation,attemptId);
  },
  async inspectInvocation(request){
   const calculated=invocation(request);if(calculated.cancelled)return freeze({abi:INFERENCE_ABI,kind:'unknown',reason:'cancelled-inspection',usage:unknownUsage(),usage_state:'unknown',exposure:null});
   const original=dispatcher.inspectIntent(request.intentId);if(!original)return freeze({abi:INFERENCE_ABI,kind:'not-dispatched'});
   // A new current Workflow claimant may inspect the same old attempt. The
   // original attempt fence is validated from owned storage, never rewritten;
   // the current host/READY owner independently authorizes this inspection.
   const found=dispatcher.inspectIntent(request.intentId,{...calculated.prepareRequest,fence:original.binding.fence});
   if(!found.observation||found.state==='prepared')return freeze({abi:INFERENCE_ABI,kind:'unknown',reason:'original-provider-inspection-required',attemptId:found.attemptId,usage:unknownUsage(),usage_state:'unknown',exposure:null});
   return decodedResult(found.observation,request,null,found.attemptId,{readOnly:true});
  },
  inspectAttempt(id){current();return dispatcher.getAttempt(id);},
  close(){if(closed)return;dispatcher.close();closed=true;},
 });current();return runtime;
}

/** Checked-native host supplies an already constructed trusted controller and
 * enriches each generated request with original authority and generated codec.
 * No ambient SDK, process credentials or network fallback can be created here. */
export function createCapabilityResource({controller,bindInvocation,operations:selectedOperations=operations,capabilities=['text-output','structured-output','embeddings']}) {
 assert(controller?.abi===INFERENCE_ABI&&typeof controller.assertCurrent==='function'&&typeof bindInvocation==='function','ForeignOwner','trusted generated inference host');
 assert(Array.isArray(selectedOperations)&&selectedOperations.length&&selectedOperations.every(op=>operations.includes(op))&&Array.isArray(capabilities)&&capabilities.every(c=>['text-output','structured-output','embeddings'].includes(c)),'UnsupportedCapability','selected inference descriptor');
 return Object.freeze({abi:'craft.native-capability-resource/v1',operations:[...selectedOperations],capabilities:[...capabilities],
  async invoke(request){controller.assertCurrent();assert(selectedOperations.includes(request.operation),'UnsupportedCapability','selected inference operation');const bound=await bindInvocation(request);controller.assertCurrent();const outcome=await controller.invoke({...request,...bound});controller.assertCurrent();assert(outcome.kind==='candidate','InvalidContract','candidate required for typed business stage: '+outcome.kind);return new Uint8Array(outcome.wire);},
  dispose(){controller.close();},
 });
}
