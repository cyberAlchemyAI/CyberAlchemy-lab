import {createNodeServiceServer} from '../../../implementation/dist/node-service-host.js';
import {createDispatcher} from '../dispatch.mjs';
import {createIdempotentDispatcher} from '../idempotency.mjs';
// Operator bindings for the generated protected service. Open Questions: PLAN.md.
const fail=code=>{throw Object.assign(new Error(code),{code});};
export function createProtectedHandler({security,catalogMapper,requirementMapper,serviceFactory,servicePlan,modelsMapper,capabilitiesMapper,errorMapper,admissionMapper,catalogs,estimateContext,store={},maxRequestBytes=65536,...dispatchConfig}){
 if(servicePlan?.authentication!=='auth-foundation'||servicePlan?.authorization!=='tenant-permissions'||servicePlan?.scope!=='tenant-principal'||![security?.authenticate,security?.check,security?.scope,catalogMapper,requirementMapper,serviceFactory,admissionMapper,estimateContext].every(f=>typeof f==='function'))fail('INVALID_HOST_CONFIG');
 const configured=structuredClone(catalogs);
 if(!configured?.balanced||Object.keys(configured).some(k=>!['balanced','cost','latency'].includes(k)))fail('INVALID_HOST_CONFIG');
 for(const catalog of Object.values(configured)){
  if(!catalog.policy_version||!Array.isArray(catalog.providers)||catalog.providers.length>100)fail('INVALID_HOST_CONFIG');
  for(const row of catalog.providers){if(!row.enabled)continue;const binding=dispatchConfig.bindings.find(b=>b.id===row.binding_id&&b.version===row.binding_version&&b.model===row.model);
   if(!binding||row.task!=='text.generate'||!Number.isSafeInteger(row.context_limit)||row.context_limit<1||!Number.isSafeInteger(row.output_limit)||row.output_limit<1||typeof row.streaming!=='boolean')fail('INVALID_HOST_CONFIG');}
 }
 const dispatcher=createDispatcher(dispatchConfig),retentionMs=store.retentionMs??60000;
 const custody=createIdempotentDispatcher({custodyFactory:dispatchConfig.custodyFactory,...store,dispatch:({request,...rest})=>{const {routing_strategy,...routingRequest}=request;return dispatcher({...rest,request:routingRequest});}});
 const permission=async(context,purpose,resource)=>(await requirementMapper({purpose,resource,tenant:context.tenant})).value;
 async function decisions(context,requirements){return security.check(context,await Promise.all(requirements.map(([purpose,resource])=>permission(context,purpose,resource))));}
 async function requireAccess(context,requirements){if((await decisions(context,requirements)).some(x=>!x))fail('FORBIDDEN');}
 const aliases=[...new Set(Object.values(configured).flatMap(c=>c.providers.filter(p=>p.enabled).map(p=>p.model)))];
 const strategies=Object.keys(configured);
 const contexts={models:{providers:[]},capabilities:{providers:[],strategies:[],retention_ms:retentionMs}};
 async function prepareRequest(request){
  const context=await security.authenticate(request);
  const requirements=[['discover','inference-catalog'],...strategies.map(x=>['use',x]),...aliases.map(x=>['invoke',x]),...aliases.map(x=>['stream',x])];
  const result=await decisions(context,requirements);if(!result[0])fail('FORBIDDEN');
  const allowedStrategies=strategies.filter((_,n)=>result[1+n]);
  const allowed=new Set(aliases.filter((_,n)=>result[1+strategies.length+n]));
  const streaming=new Set(aliases.filter((_,n)=>result[1+strategies.length+aliases.length+n]));
  const catalogs=Object.fromEntries(await Promise.all(allowedStrategies.map(async strategy=>[strategy,{...configured[strategy],tenant_id:context.tenant,providers:(await catalogMapper({providers:configured[strategy].providers.map(row=>({...row,tenant_allowed:allowed.has(row.model),streaming:row.streaming&&streaming.has(row.model)}))})).providers}])));
  const providers=Object.values(catalogs).flatMap(c=>c.providers);
  return {contexts:{models:{providers},capabilities:{providers,strategies:allowedStrategies,retention_ms:retentionMs}},state:{context,catalogs,allowed,streaming}};
 }
 const handle=serviceFactory({maxRequestBytes,contexts,prepareRequest,operations:{ExecuteInference:async(value,_env,{signal,headers,state})=>{
  const {context,catalogs,allowed,streaming}=state;
  if(!Object.hasOwn(catalogs,value.strategy)||value.model!==undefined&&(!allowed.has(value.model)||value.stream&&!streaming.has(value.model)))fail('FORBIDDEN');
  const catalog=catalogs[value.strategy];
  const admission=await admissionMapper({strategy:value.strategy,...(value.model===undefined?{}:{model:value.model}),strategies:Object.keys(catalogs),models:(await modelsMapper({providers:catalog.providers})).models.map(m=>m.id)});
  if(admission.code!=='OK')fail(admission.code);
  const required=estimateContext(structuredClone({messages:value.messages,model:value.model,max_output_tokens:value.max_output_tokens}));
  if(!Number.isSafeInteger(required)||required<value.max_output_tokens)fail('INVALID_CONTEXT_ESTIMATE');
  const authorizeModel=model=>requireAccess(context,[['discover','inference-catalog'],['use',value.strategy],['invoke',model],...(value.stream?[['stream',model]]:[])]);
  return custody.run({request:{request_id:'host',tenant_id:context.tenant,routing_strategy:value.strategy,task:value.task,...(value.model===undefined?{}:{model:value.model}),required_context_tokens:required,max_output_tokens:value.max_output_tokens,stream:value.stream},catalog,messages:value.messages,idempotencyKey:headers.get('idempotency-key')??undefined,custodyScope:security.scope(context),signal,beforeAttempt:binding=>authorizeModel(binding.model),beforeReplay:result=>authorizeModel(result.model)});
 }}});
 return Object.assign(handle,{close:()=>custody.close()});
}
export function createProtectedServer(config){const handle=createProtectedHandler(config);const server=createNodeServiceServer(handle,handle.errorResponse);server.once('close',()=>handle.close());return server;}
