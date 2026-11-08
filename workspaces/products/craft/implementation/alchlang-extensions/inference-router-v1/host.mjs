import {createNodeServiceServer} from '../../implementation/dist/node-service-host.js';
import {createDispatcher} from './dispatch.mjs';
import {createIdempotentDispatcher} from './idempotency.mjs';
// Operator-owned public scope; tenant authentication/authorization deferred. See HOST.md.
const fail=code=>{throw Object.assign(new Error(code),{code});};
export function createPublicHandler({serviceFactory,modelsMapper,capabilitiesMapper,errorMapper,admissionMapper,catalogs,estimateContext,store={},maxRequestBytes=65536,...dispatchConfig}){
 if(typeof dispatchConfig.token!=='string'||!dispatchConfig.token||!['invocationFactory','streamFactory','custodyFactory'].every(k=>typeof dispatchConfig[k]==='function')||![serviceFactory,modelsMapper,capabilitiesMapper,errorMapper,admissionMapper].every(f=>typeof f==='function')||typeof estimateContext!=='function'||!Number.isSafeInteger(maxRequestBytes)||maxRequestBytes<1||maxRequestBytes>65536)fail('INVALID_HOST_CONFIG');
 const configured=structuredClone(catalogs);
 if(!configured?.balanced||Object.keys(configured).some(k=>!['balanced','cost','latency'].includes(k)))fail('INVALID_HOST_CONFIG');
 for(const catalog of Object.values(configured)){
  if(!catalog.policy_version||!Array.isArray(catalog.providers)||catalog.providers.length>100)fail('INVALID_HOST_CONFIG');
  catalog.tenant_id='public';
  for(const row of catalog.providers){
   // Availability here is operator configuration, not a tenant authorization decision.
   row.tenant_allowed=true;
   if(!row.enabled)continue;
   const binding=dispatchConfig.bindings.find(b=>b.id===row.binding_id&&b.version===row.binding_version&&b.model===row.model);
   if(!binding||row.task!=='text.generate'||!Number.isSafeInteger(row.context_limit)||row.context_limit<1||!Number.isSafeInteger(row.output_limit)||row.output_limit<1||typeof row.streaming!=='boolean')fail('INVALID_HOST_CONFIG');

  }
 }
 const dispatcher=createDispatcher(dispatchConfig);
 const retentionMs=store.retentionMs??60000;
 // Flatten the transport containers without selecting, grouping, or projecting offerings.
 const providers=Object.values(configured).flatMap(c=>c.providers);
 let discovery;
 const discover=()=>discovery??=(async()=>{
  const models=await modelsMapper({providers});
  const capabilities=await capabilitiesMapper({providers,strategies:Object.keys(configured),retention_ms:retentionMs});
  return {models,capabilities:capabilities.value};
 })();
 const custody=createIdempotentDispatcher({custodyFactory:dispatchConfig.custodyFactory,...store,dispatch:({request,...rest})=>{const {routing_strategy,...routingRequest}=request;return dispatcher({...rest,request:routingRequest});}});
 return serviceFactory({maxRequestBytes,contexts:{models:{providers},capabilities:{providers,strategies:Object.keys(configured),retention_ms:retentionMs}},operations:{
  ExecuteInference:async(value,_env,{signal,headers})=>{
   const admission=await admissionMapper({strategy:value.strategy,...(value.model===undefined?{}:{model:value.model}),strategies:Object.keys(configured),models:(await discover()).models.models.map(m=>m.id)});
   if(admission.code!=='OK')fail(admission.code);
   const catalog=configured[value.strategy];
   // Synchronous operator estimator supplies a conservative total context requirement.
   const required=estimateContext(structuredClone({messages:value.messages,model:value.model,max_output_tokens:value.max_output_tokens}));
   if(!Number.isSafeInteger(required)||required<value.max_output_tokens)fail('INVALID_CONTEXT_ESTIMATE');
   const result=await custody.run({request:{request_id:'host',tenant_id:'public',routing_strategy:value.strategy,task:value.task,...(value.model===undefined?{}:{model:value.model}),required_context_tokens:required,max_output_tokens:value.max_output_tokens,stream:value.stream},catalog,messages:value.messages,idempotencyKey:headers.get('idempotency-key')??undefined,signal});
   return result;
  }
 }});
}

export function createPublicServer(config){
 const handle=createPublicHandler(config);
 return createNodeServiceServer(handle,handle.errorResponse);
}
