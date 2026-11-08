import path from 'node:path';
import {APPLICATION_PATHS as P,outputImport} from '../generation/output-layout.js';
import {captureJson,canonicalJson,reject,type Json} from './contracts.js';
import {assertCheckedCompositionCurrent,assertProfileSelectionCurrent,profileTechnicalSelections,type CheckedComposition} from './compose.js';
import type {LoadedPackage,LoadedPackageV2} from './loader.js';
import type {LoadedBusinessAuthoringPackage} from './loader-v3.js';
import {projectProfileViews} from './views.js';
import {renderApplicationCallableSource} from './application-adapter.js';
import {projectOperationalExpectations} from './operational-expectations.js';

/** Pure finite rendering over registered checked plans and locked assets.
 * Open questions: PE14 application callable and PE19 complete qualification. */
export function renderProfileTemplate(pkg:LoadedPackage|LoadedPackageV2|LoadedBusinessAuthoringPackage,id:string,parameters:Readonly<Record<string,Json>>):string {
 const values=captureJson(parameters) as Readonly<Record<string,Json>>;let operations=0,bytes=0;
 const typed=(key:string,value:Json|undefined,type:string|undefined):string=>{
  if(++operations>pkg.data.budgets.operations)reject('PROFILE_TEMPLATE_BUDGET',key,'operation budget exceeded');
  if(!type||value===undefined)reject('PROFILE_TEMPLATE_HOLE',key,'declared typed value required');
  if(type==='json')return canonicalJson(value);
  if(typeof value!=='string')reject('PROFILE_TEMPLATE_HOLE_TYPE',key,'string value required');
  if(type==='identifier'){if(!/^[A-Za-z_$][A-Za-z0-9_$]*$/.test(value)||['__proto__','constructor','prototype'].includes(value))reject('PROFILE_TEMPLATE_IDENTIFIER',key,'safe identifier required');return value;}
  if(type==='import-path'&&(!/^\.\.?\//.test(value)||value.includes('\\')||value.includes('\0')||value.split('/').some(p=>!p)||!/^\.{1,2}\/[A-Za-z0-9_./-]+$/.test(value)))reject('PROFILE_TEMPLATE_IMPORT',key,'relative generated import path required');
  return JSON.stringify(value);
 };
 const render=(name:string,scope:Readonly<Record<string,Json>>,stack:readonly string[]):string=>{
  if(stack.includes(name))reject('PROFILE_TEMPLATE_CYCLE',name,'cyclic template expansion');
  const asset=pkg.data.assets.find(a=>a.id===name),body=pkg.assets[name]?.text;
  if(!asset||asset.kind!=='template'||body===undefined)reject('PROFILE_TEMPLATE_UNOWNED',name,'captured package template required');
  const expand=(source:string,current:Readonly<Record<string,Json>>,depth:number):string=>{
   if(++operations>pkg.data.budgets.operations||depth>=pkg.data.budgets.depth)reject('PROFILE_TEMPLATE_BUDGET',name,'finite expansion budget exceeded');
   const token=/\{\{#each ([A-Za-z][A-Za-z0-9_]*)\}\}([\s\S]*?)\{\{\/each\}\}|\{\{> ([A-Za-z][A-Za-z0-9_-]*)\}\}|\{\{([A-Za-z][A-Za-z0-9_]*)\}\}/g;
   if(source.replace(token,'').includes('{{'))reject('PROFILE_TEMPLATE_SYNTAX',name,'only declared holes, each and includes supported');
   // Expand original tokens once. Inserted JSON/strings are never parsed as templates.
   const result=source.replace(token,(_all,each:string|undefined,part:string|undefined,include:string|undefined,hole:string|undefined)=>{
    if(each){const rows=current[each];if(!Array.isArray(rows)||rows.length>pkg.data.budgets.rows)reject('PROFILE_TEMPLATE_ITERATION',each,'bounded record array required');return rows.map(row=>{if(!row||typeof row!=='object'||Array.isArray(row))reject('PROFILE_TEMPLATE_ITERATION',each,'record rows required');return expand(part!,{...current,...row},depth+1);}).join('');}
    if(include){if(!asset.includes.includes(include))reject('PROFILE_TEMPLATE_INCLUDE',include,'include must be declared within package closure');return render(include,current,[...stack,name]);}
    return typed(hole!,current[hole!],asset.holes[hole!]);
   });
   bytes+=Buffer.byteLength(result);if(bytes>pkg.data.budgets.bytes)reject('PROFILE_TEMPLATE_BUDGET',name,'output byte budget exceeded');return result;
  };
  return expand(body,scope,stack.length);
 };
 return render(id,values,[]);
}

export function renderProfilePlan(composition:CheckedComposition):Readonly<Record<string,string>> {
 assertCheckedCompositionCurrent(composition);const snapshot=assertProfileSelectionCurrent(composition.selection),files:Record<string,string>=Object.create(null);
 const put=(file:string,body:string)=>{if(Object.hasOwn(files,file))reject('PROFILE_RENDER_COLLISION',file,'artifact has more than one renderer owner');files[file]=body;};
 for(const artifact of composition.artifacts)put(artifact.path,artifact.content);
 put('package.json','{"type":"module","private":true}\n');
 const technical=profileTechnicalSelections(composition.selection),entries=composition.data.components.filter(c=>c.role==='http-entry');
 for(const component of entries){
  const intent=composition.selection.input.project.public_intents.find(i=>component.origins.some(o=>o.selector==='public-intent:'+i.id))!,fn=composition.data.components.find(c=>c.role==='domain-function'&&component.depends_on.includes(c.id))!;
  const prefix=fn.artifact_paths.find(p=>p.endsWith('/'+P.entry))!.slice(0,-P.entry.length),entry=component.artifact_paths[0]!,choice=technical.find(c=>c.intent_id===intent.id)!;
  const wires=composition.selection.input.wire.filter(w=>w.source===intent.source);
  const modelFile=prefix+P.model,model=JSON.parse(files[modelFile]!);
  const bindings=wires.map(w=>({env:model.integrations[w.intent_id].urlEnv,secret:model.integrations[w.intent_id].secretEnv??null,wire:w.wire_schema,correspondence:w.correspondence,max_bytes:model.integrations[w.intent_id].maxBytes,timeout_ms:model.integrations[w.intent_id].timeout}));
  const config={method:choice.method,route:choice.route,input:intent.input_ref,success_status:choice.success_status,rejection_status:choice.rejection_status,request_bytes:choice.request_bytes,timeout_ms:choice.timeout_ms,outcomes:intent.outcomes,bindings};
  const selected=composition.selection.emissions.find(e=>e.emission.role==='http-entry'&&e.emission.fields.id===intent.id)!,pkg=snapshot.packages.find(p=>p.id===selected.package_id)!;
  const template=selected.emission.fields.template_ref;
  if(template!==undefined){const shared=composition.data.components.find(c=>c.role==='shared-http-port'&&component.depends_on.includes(c.id));put(entry,renderProfileTemplate(pkg,String(template),{callable:outputImport(entry,prefix+P.entry),boundary:outputImport(entry,prefix+P.runtime),model:outputImport(entry,modelFile),transport:outputImport(entry,shared?.artifact_paths[0]??'runtime/profile-http.mjs'),config:config as unknown as Json}));}
  else put(entry,`import {createInvoker} from ${JSON.stringify(outputImport(entry,prefix+P.entry))};\nimport {validateSchema,FunctionFault} from ${JSON.stringify(outputImport(entry,prefix+P.runtime))};\nimport model from ${JSON.stringify(outputImport(entry,modelFile))} with {type:'json'};\nimport {createPublicEntry} from ${JSON.stringify(outputImport(entry,'runtime/profile-http.mjs'))};\nexport const config=${canonicalJson(captureJson(config))};\nexport const handler=createPublicEntry(config,model,validateSchema,createInvoker,FunctionFault);\n`);
 }
 const dispatch=composition.data.components.find(c=>c.role==='http-dispatch')!,dispatcher=dispatch.artifact_paths[0]!;
 const applicationEntries:string[]=[];
 for(const application of composition.applications){const component=composition.data.components.find(c=>c.id==='application_operation_'+application.intent.id)!,selected=composition.selection.emissions.find(e=>e.emission.role==='application-operation'&&e.emission.fields.id===application.intent.id)!,prefix='applications/'+application.intent.id+'/',entry=component.artifact_paths.at(-1)!;
  let assembly:Readonly<{settlement_import:string;transport_import:string}>|undefined;
  if(application.kind==='request-application'){
   const runtime=composition.selection.business_applications!.runtime,choice=runtime.data.application_runtime;
   put(prefix+'src/empty-settlement.ts',runtime.assets[choice.settlement_asset]!.text!);
   const shared=component.depends_on.map(id=>composition.data.components.find(c=>c.id===id)!).find(c=>c.role==='shared-http-port');
   if(choice.transport==='entry-local')put(prefix+'src/application-http.mts',runtime.assets[choice.transport_asset]!.text!);
   const transport=choice.transport==='shared'?shared!.artifact_paths[0]!.replace(/^runtime\//,'runtime/lib/').replace(/\.mts$/,'.mjs'):prefix+'src/application-http.mjs';
   assembly={settlement_import:'./empty-settlement.js',transport_import:outputImport(prefix+'src/profile-entry.ts',transport)};
  }
  put(prefix+'src/profile-entry.ts',renderApplicationCallableSource(application,selected.emission.fields.technical as unknown as {request_bytes:number;timeout_ms:number},assembly));
  put(prefix+'package.json','{"type":"module","private":true}\n');
  put(entry,`import {handler as invoke} from ${JSON.stringify(outputImport(entry,prefix+'lib/profile-entry.js'))};\nexport const config=${canonicalJson({method:'POST',route:selected.emission.fields.route!})};\nexport const handler=invoke;\n`);applicationEntries.push(entry);
 }
 const routes=[...entries.map(c=>c.artifact_paths[0]!),...applicationEntries].map((file,index)=>({import:outputImport(dispatcher,file),alias:'entry'+index}));
 const selected=composition.selection.emissions.find(e=>e.emission.role==='http-dispatch')!,pkg=snapshot.packages.find(p=>p.id===selected.package_id)!;
 if(selected.emission.fields.template_ref!==undefined)put(dispatcher,renderProfileTemplate(pkg,String(selected.emission.fields.template_ref),{entries:routes as unknown as Json}));
 else put(dispatcher,routes.map(r=>`import * as ${r.alias} from ${JSON.stringify(r.import)};`).join('\n')+`\nconst entries=[${routes.map(r=>r.alias).join(',')}];\n/** @param {Request} request @param {Record<string,string|undefined>} [env] @param {{fetch?:typeof fetch,observe?:(event:any)=>void,signal?:AbortSignal,cancellation?:'preflight'|'required',applications?:Record<string,any>}} [io] @returns {Promise<Response>} */\nexport async function handler(request,env={},io={}){const entry=entries.find(e=>e.config.route===new URL(request.url).pathname);return entry?entry.handler(request,env,io):new Response(JSON.stringify({error:'NOT_FOUND'}),{status:404,headers:{'content-type':'application/json'}});}\n`);
 put('runtime/profile-http.mjs',PUBLIC_RUNTIME);
 for(const selected of composition.selection.emissions.filter(e=>e.emission.role==='operational-expectation'))put('evidence/operational/'+String(selected.emission.fields.id)+'.json',canonicalJson(captureJson(projectOperationalExpectations([selected.emission.fields.declaration],{source_sha256:composition.data.source_sha256,lock_sha256:composition.data.lock_sha256})))+'\n');
 for(const shared of composition.data.components.filter(c=>c.role==='shared-http-port')){const selected=composition.selection.emissions.find(e=>e.emission.role==='shared-http-port'&&shared.origins.some(o=>o.selector===e.emission.rule&&o.source===e.package_id+'/profile.json'))!,pkg=snapshot.packages.find(p=>p.id===selected.package_id)!;
  if(composition.selection.business_applications?.runtime.id===selected.package_id){const runtime=composition.selection.business_applications.runtime;put(shared.artifact_paths[0]!,runtime.assets[runtime.data.application_runtime.transport_asset]!.text!);continue;}
  const template=selected.emission.fields.template_ref;if(typeof template!=='string')reject('PROFILE_RENDER_SHARED_RECIPE',shared.id,'shared infrastructure requires a locked recipe');put(shared.artifact_paths[0]!,renderProfileTemplate(pkg,template,{runtime:outputImport(shared.artifact_paths[0]!,'runtime/profile-http.mjs')}));}
 const views=projectProfileViews(composition);for(const name of ['business','system','bridge'] as const){put('views/'+name+'.json',canonicalJson(captureJson(views[name]))+'\n');put('views/'+name+'.md',views.text[name]);}
 put('evidence/coverage.json',canonicalJson(captureJson(views.coverage))+'\n');put('evidence/composition.json',canonicalJson(captureJson(composition.data))+'\n');
 assertCheckedCompositionCurrent(composition);return Object.freeze(files);
}

// Reusable transport only. Business outcomes/computation stay in checked functions.
const PUBLIC_RUNTIME=`
export class PublicFault extends Error {constructor(code){super(code);this.code=code;}}
const fail=code=>{throw new PublicFault(code);};
async function text(body,limit,timeout){if(!body.body)return '';const reader=body.body.getReader(),chunks=[];let size=0,timed=false;const timer=setTimeout(()=>{timed=true;void reader.cancel().catch(()=>{});},timeout);try{for(;;){const item=await reader.read();if(item.done){if(timed)fail('FUNCTION_TIMEOUT');break;}size+=item.value.byteLength;if(size>limit){await reader.cancel();fail('FUNCTION_BODY_LIMIT');}chunks.push(item.value);}const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}return new TextDecoder('utf-8',{fatal:true}).decode(bytes);}finally{clearTimeout(timer);reader.releaseLock();}}
export function createPublicEntry(config,model,validate,createInvoker,IntegrationFault){
 const reply=(body,status)=>new Response(JSON.stringify(body),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
 /** @param {Request} request @param {Record<string,string|undefined>} [env] @param {{fetch?:typeof fetch,observe?:(event:any)=>void,signal?:AbortSignal}} [io] @returns {Promise<Response>} */
 return async function handler(request,env={},io={}){
  if(new URL(request.url).pathname!==config.route)return reply({error:'NOT_FOUND'},404);
  if(request.method!==config.method)return reply({error:'METHOD_NOT_ALLOWED'},405);
  if(request.headers.get('content-type')?.split(';')[0].trim()!=='application/json')return reply({error:'CONTENT_TYPE'},415);
  try{
   let input;try{input=JSON.parse(await text(request,config.request_bytes,config.timeout_ms));}catch(e){if(e instanceof PublicFault)throw e;fail('INVALID_JSON');}
   try{input=validate(model,config.input,input);}catch{fail('FUNCTION_INPUT_SCHEMA');}
   const adapted={...io,signal:io.signal?AbortSignal.any([request.signal,io.signal]):request.signal,fetch:async(url,options)=>{const transport=io.fetch??globalThis.fetch;const target=new URL(url),matches=config.bindings.filter(b=>{const location=env[b.env];if(!location)return false;const expected=new URL(location);return expected.origin===target.origin&&expected.pathname===target.pathname;});if(matches.length!==1)fail('FUNCTION_INTEGRATION_REQUIRED');const binding=matches[0];
    const response=await transport(url,options);if(!response.ok)return response;
    let wire;try{wire=JSON.parse(await text(response,binding.max_bytes,binding.timeout_ms));wire=validate({schemas:{[binding.wire.id]:binding.wire.fields}},binding.wire.id,wire);}catch(e){throw new IntegrationFault(e instanceof PublicFault?e.code==='FUNCTION_BODY_LIMIT'?'FUNCTION_INTEGRATION_LIMIT':e.code==='FUNCTION_TIMEOUT'?'FUNCTION_INTEGRATION_TIMEOUT':'FUNCTION_INTEGRATION_SCHEMA':'FUNCTION_INTEGRATION_SCHEMA');}
    const projected={};for(const [to,from]of Object.entries(binding.correspondence))projected[to]=wire[from];return new Response(JSON.stringify(projected),{status:response.status,headers:{'content-type':'application/json'}});
   }};
   const result=await createInvoker(io.observe).invoke(input,env,adapted),outcome=config.outcomes.find(o=>o.code===result.status);if(!outcome)fail('FUNCTION_RESPONSE_STATUS');return reply(result,outcome.kind==='success'?config.success_status:config.rejection_status);
  }catch(e){const code=typeof e?.code==='string'?e.code:String(e?.message??'').match(/CALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)/)?.[0]??'FUNCTION_INTERNAL';return reply({error:code},code==='INVALID_JSON'||code==='FUNCTION_INPUT_SCHEMA'?400:code==='FUNCTION_BODY_LIMIT'?413:code==='FUNCTION_ENV_REQUIRED'?503:code==='FUNCTION_INTEGRATION_TIMEOUT'||code==='FUNCTION_TIMEOUT'?504:code.startsWith('FUNCTION_INTEGRATION_')?502:code==='FUNCTION_INTERNAL'?500:409);}
 };
}
`;
