import assert from 'node:assert/strict';
import {execFileSync,spawnSync} from 'node:child_process';
import {cpSync,mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {createRequire,syncBuiltinESMExports} from 'node:module';
import test from 'node:test';

// PE01 conformance probe. Open questions: docs/PROFILE-CALLABLES.md.
// This validates real generated exports; it does not implement PE14's engine adapter.
const repo=path.resolve(import.meta.dirname,'../../../../../../../');
const prior=path.join(repo,'research/craft-alchlang-user-readiness-2026-10-12/profile-composition-orodi-research-2026-10-13/example');
const consumer=process.env.PROFILE_CALLABLE_CONSUMER??'/tmp/profile-engine-PE22-consumer';
const tsc=path.join(consumer,'node_modules/typescript/bin/tsc');
const sha=(value:string|Buffer)=>createHash('sha256').update(value).digest('hex');

test('actual generated function and Craft Operation fit checked value ports with explicit outcome semantics',async t=>{
 const stage=mkdtempSync(path.join(os.tmpdir(),'profile-callables-'));t.after(()=>rmSync(stage,{recursive:true,force:true}));
 cpSync(path.join(prior,'generated-application/src'),path.join(stage,'src'),{recursive:true});
 cpSync(path.join(consumer,'generated'),path.join(stage,'quote'),{recursive:true});
 writeFileSync(path.join(stage,'package.json'),'{"type":"module"}');
 const op='src/features/commerce/application/operations/receive-notice.ts';
 const functionEntry='quote/entries/Quote/app/function/index.mjs';
 // A conservative ABI declaration gives no invented type guarantee for legacy JS.
 // The typed adapter validates its unknown result against the pinned schema.
 writeFileSync(path.join(stage,functionEntry.replace('.mjs','.d.mts')),`export function invoke(input:unknown,env:Readonly<Record<string,string|undefined>>,io:{fetch?:typeof fetch;signal?:AbortSignal}):Promise<unknown>;\n`);
 const probe=`import {operationReceiveNotice} from './${op.replace('.ts','.js')}';
import {invoke as rawQuote} from './${functionEntry}';
type QuoteInput=Readonly<{request_id:string;sku:string;quantity:number}>;
type QuoteValue=Readonly<{request_id:string;sku:string;quantity:number;status:'quoted'|'unavailable';total_minor:string}>;
type OpInput=Parameters<typeof operationReceiveNotice>[0];
type OpValue=Extract<Awaited<ReturnType<typeof operationReceiveNotice>>,{status:'committed'}>['value'];
type OpFailure=Exclude<Awaited<ReturnType<typeof operationReceiveNotice>>,{status:'committed'}>;
type Fault=Readonly<{code:string}>;
export type Result<V,F>=Readonly<{status:'returned';value:V}>|Readonly<{status:'not-returned';failure:F}>;
export type Context=Readonly<{signal?:AbortSignal;cancellation?:'preflight'|'required';observe?:(event:Readonly<{phase:string;adapter:string}>)=>void}>;
export type Callable<I,V,P,F>=(input:I,ports:P,context?:Context)=>Promise<Result<V,F>>;
function emit(c:Context|undefined,phase:string,adapter:string){try{c?.observe?.({phase,adapter});}catch{}}
export const quote:Callable<QuoteInput,QuoteValue,{env:Readonly<Record<string,string|undefined>>;fetch:typeof fetch},Fault>=async(input,ports,context)=>{
 emit(context,'start','function');
 try{const value=await rawQuote(input,ports.env,{fetch:ports.fetch,...(context?.signal?{signal:context.signal}:{})});
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('PROFILE_CALLABLE_RESULT');
 const v=value as Record<string,unknown>;
 if(typeof v.request_id!=='string'||typeof v.sku!=='string'||typeof v.quantity!=='number'||!['quoted','unavailable'].includes(String(v.status))||typeof v.total_minor!=='string')throw Error('PROFILE_CALLABLE_RESULT');
 emit(context,'return','function');return {status:'returned',value:v as QuoteValue};
 }catch(error){emit(context,'failure','function');const e=error as {code?:unknown;message?:unknown};return {status:'not-returned',failure:{code:typeof e.code==='string'?e.code:e.message==='PROFILE_CALLABLE_RESULT'?'PROFILE_CALLABLE_RESULT':'FUNCTION_INTERNAL'}};}
};
export const notice:Callable<OpInput,OpValue,Parameters<typeof operationReceiveNotice>[1],OpFailure|Fault>=async(input,ports,context)=>{
 if(context?.cancellation==='required')return {status:'not-returned',failure:{code:'PROFILE_OPERATION_CANCELLATION_UNSUPPORTED'}};
 if(context?.signal?.aborted)return {status:'not-returned',failure:{code:'FUNCTION_CANCELLED'}};
 emit(context,'start','operation');const outcome=await operationReceiveNotice(input,ports);
 if(outcome.status==='committed'){emit(context,'return','operation');return {status:'returned',value:outcome.value};}
 emit(context,'failure','operation');return {status:'not-returned',failure:outcome};
};
`;
 writeFileSync(path.join(stage,'probe.ts'),probe);
 const config={compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',rootDir:'.',outDir:'js',types:[],lib:['ES2022','DOM']},files:['probe.ts']};
 writeFileSync(path.join(stage,'tsconfig.json'),JSON.stringify(config));
 execFileSync(process.execPath,[tsc,'-p',path.join(stage,'tsconfig.json')],{cwd:stage,encoding:'utf8'});
 // Copy actual JS closure unchanged to runtime destination; never import launcher.
 cpSync(path.join(stage,'quote'),path.join(stage,'js/quote'),{recursive:true});
 const forbidden={network:0,listen:0,process:0};const restorers:Array<()=>void>=[];const require=createRequire(import.meta.url);
 const intercept=(object:any,key:string,kind:keyof typeof forbidden)=>{const original=object[key];object[key]=()=>{forbidden[kind]++;throw Error('PROFILE_FORBIDDEN_RUNTIME_EFFECT:'+kind);};restorers.push(()=>{object[key]=original;});};
 intercept(globalThis,'fetch','network');
 for(const name of ['node:http','node:https']){const object=require(name);for(const key of ['request','get'])intercept(object,key,'network');intercept(object,'createServer','listen');}
 const net=require('node:net');for(const key of ['connect','createConnection'])intercept(net,key,'network');intercept(net,'createServer','listen');
 const child=require('node:child_process');for(const key of ['exec','execSync','execFile','execFileSync','spawn','spawnSync','fork'])intercept(child,key,'process');
 syncBuiltinESMExports();const restore=()=>{for(const fn of restorers.reverse())fn();syncBuiltinESMExports();};t.after(restore);
 const module=await import(pathToFileURL(path.join(stage,'js/probe.js')).href);
 let transports=0;const fetch:typeof globalThis.fetch=async()=>{transports++;return Response.json({sku:'S1',stock:5,unit_price_minor:1250});};
 const events:any[]=[];const env={INVENTORY_API_URL:'https://inventory.invalid/',INVENTORY_API_TOKEN:'fixture-only'};
 const result=await module.quote({request_id:'Q1',sku:'S1',quantity:3},{env,fetch},{observe:(e:any)=>events.push(e)});
 assert.deepEqual(result,{status:'returned',value:{request_id:'Q1',sku:'S1',quantity:3,status:'quoted',total_minor:'3750'}});
 const invalid=await module.quote({request_id:'Q1',sku:'S1',quantity:0},{env,fetch});assert.equal(invalid.status,'not-returned');
 assert.equal(transports,1,'input failure must not make a remote read');
 const missingEnvironment=await module.quote({request_id:'Q1',sku:'S1',quantity:3},{env:{},fetch});assert.equal(missingEnvironment.failure.code,'FUNCTION_ENV_REQUIRED');
 const malformedRemote:typeof globalThis.fetch=async()=>{transports++;return Response.json({sku:'S1',stock:'invalid',unit_price_minor:1250});};
 assert.equal((await module.quote({request_id:'Q1',sku:'S1',quantity:3},{env,fetch:malformedRemote})).failure.code,'FUNCTION_INTEGRATION_SCHEMA');
 const cancelled=new AbortController();cancelled.abort();assert.equal((await module.quote({request_id:'Q1',sku:'S1',quantity:3},{env,fetch},{signal:cancelled.signal})).failure.code,'FUNCTION_CANCELLED');
 let begins=0,commits=0,rollbacks=0;
 const ports=(status='committed',beginFails=false)=>({store:{begin:async()=>{begins++;if(beginFails)throw Error('fixture begin failure');return {read:async()=>{throw Error('unexpected read');},commit:async(batch:any)=>{commits++;assert.deepEqual(batch,{writes:[],events:[]});return {status};},rollback:async()=>{rollbacks++;}};}}});
 const success=await module.notice({request:{id:'7'}},ports(),{observe:(e:any)=>events.push(e)});
 assert.equal(success.status,'returned');assert.equal(success.value.id,7n);
 const rejected=await module.notice({request:{id:'7'}},ports('rejected'));assert.equal(rejected.status,'not-returned');assert.equal(rejected.failure.status,'rejected');assert.equal(rejected.failure.code,'COMMIT_REJECTED');assert.equal(rejected.failure.stage,'commit');assert.equal(rejected.failure.continuation,'return-notice-error');assert.equal(rollbacks,0,'commit rejection must not pretend that rollback establishes absence of effects');
 const malformed=await module.notice({request:{id:'-1'}},ports());assert.equal(malformed.failure.code,'OPERATION_INPUT');assert.equal(malformed.failure.stage,'input');
 const uncertain=await module.notice({request:{id:'7'}},ports('indeterminate'));assert.equal(uncertain.failure.status,'indeterminate');assert.equal(uncertain.failure.code,'COMMIT_INDETERMINATE');assert.equal(uncertain.failure.cleanupFailed,false);
 const failed=await module.notice({request:{id:'7'}},ports('committed',true));assert.equal(failed.failure.code,'BEGIN_FAILED');assert.equal(failed.failure.stage,'begin');
 const before=begins;assert.equal((await module.notice({request:{id:'7'}},ports(),{cancellation:'required'})).failure.code,'PROFILE_OPERATION_CANCELLATION_UNSUPPORTED');assert.equal(begins,before);
 assert.equal((await module.notice({request:{id:'7'}},ports(),{signal:cancelled.signal})).failure.code,'FUNCTION_CANCELLED');assert.equal(begins,before);
 assert.deepEqual(events.map(e=>[e.adapter,e.phase]),[['function','start'],['function','return'],['operation','start'],['operation','return']]);
 assert.deepEqual(forbidden,{network:0,listen:0,process:0});restore();
 // Native falsifiers target the real Operation's exported input/value contracts.
 for(const [name,negative] of [['input',`import {notice} from './probe.js';notice({request:{id:true}},{});`],['result',`import {operationReceiveNotice} from './${op.replace('.ts','.js')}';type V=Extract<Awaited<ReturnType<typeof operationReceiveNotice>>,{status:'committed'}>['value'];const bad:V={id:'wrong'};`],['port',`import {notice} from './probe.js';notice({request:{id:'7'}},{store:{begin:async()=>({})}});`],['environment',`import {quote} from './probe.js';quote({request_id:'Q1',sku:'S1',quantity:3},{env:{INVENTORY_API_URL:true},fetch});`],['missing-export',`import {absent} from './${op.replace('.ts','.js')}';absent();`]] as const){
  writeFileSync(path.join(stage,'negative.ts'),negative);writeFileSync(path.join(stage,'negative-config.json'),JSON.stringify({...config,compilerOptions:{...config.compilerOptions,noEmit:true},files:['negative.ts']}));
  const checked=spawnSync(process.execPath,[tsc,'-p',path.join(stage,'negative-config.json')],{cwd:stage,encoding:'utf8'});assert.notEqual(checked.status,0,name);
 }
 const evidence={task:'PE01',compatibility:'compatible',scope:'value invocation via registered typed adapter; Operation outcomes preserved; no required in-flight cancellation',function:{artifact:functionEntry,export:'invoke',sha256:sha(readFileSync(path.join(stage,functionEntry)))},operation:{artifact:op,export:'operationReceiveNotice',sha256:sha(readFileSync(path.join(stage,op)))},checks:['native typed adapter','real function value and input failure','function cancellation','Operation committed/rejected/indeterminate/begin failure','failure stage/continuation/cleanup retained','required cancellation rejection before effects','preflight cancellation','observation lifecycle','five native input/result/port/environment/export negatives','runtime missing environment and malformed provider shape'],fake_transport_calls:transports,fake_begins:begins,fake_commits:commits,fake_rollbacks:rollbacks,forbidden_runtime_attempts:forbidden,authority_effect:'none'};
 if(process.env.PROFILE_CALLABLE_EVIDENCE)writeFileSync(process.env.PROFILE_CALLABLE_EVIDENCE,JSON.stringify(evidence,null,2)+'\n');
});
