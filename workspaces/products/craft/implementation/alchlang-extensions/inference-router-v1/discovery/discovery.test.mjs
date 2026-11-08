import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync,writeFileSync,rmSync,symlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkQueryIteration,buildQueryIteration} from '../../../implementation/dist/query-iteration.js';
import {createQueryIteration} from '../../../implementation/dist/query-iteration-runtime.js';
const here=fileURLToPath(new URL('./',import.meta.url));
const plan={sourceField:'ids',inputField:'value',itemField:'value',outputField:'records',maxItems:3,maxOutputBytes:128,maxInputBytes:128,timeoutMs:1000};
const source=async input=>({ids:input.ids});
const mapping=async ({context,item})=>({value:{id:item,label:context.label}});
const item=async value=>({value});
test('generic pure composition preserves source order, clones context and returns a complete bounded list',async()=>{
 const input={ids:['z','a'],label:'label'};const invoke=createQueryIteration(plan,source,mapping,item);const pending=invoke(input);input.label='changed';
 assert.deepEqual(await pending,{records:[{id:'z',label:'label'},{id:'a',label:'label'}]});
 assert.deepEqual(await invoke({ids:[],label:'empty'}),{records:[]});
});
test('item/input/output bounds reject without a partial result',async()=>{
 let calls=0;const counted=async x=>{calls++;return item(x);};
 await assert.rejects(createQueryIteration(plan,source,mapping,counted)({ids:['1','2','3','4'],label:'x'}),/ITEM_LIMIT/);assert.equal(calls,0);
 await assert.rejects(createQueryIteration(plan,source,mapping,counted)({ids:[],label:'x'.repeat(129)}),/INPUT_LIMIT/);assert.equal(calls,0);
 await assert.rejects(createQueryIteration({...plan,maxOutputBytes:20},source,mapping,counted)({ids:['a'],label:'x'}),/OUTPUT_LIMIT/);
 await assert.rejects(createQueryIteration({...plan,maxOutputBytes:1},source,mapping,item)({ids:[]}),/OUTPUT_LIMIT/);
});
test('first item failure stops iteration and cancellation/deadlines cannot return success',async()=>{
 let calls=0;const fail=async()=>{calls++;throw Error('ITEM_FAILED');};
 await assert.rejects(createQueryIteration(plan,source,mapping,fail)({ids:['a','b']}),/ITEM_FAILED/);assert.equal(calls,1);
 const controller=new AbortController();controller.abort();await assert.rejects(createQueryIteration(plan,source,mapping,item)({ids:[]},{},{signal:controller.signal}),/CANCELLED/);
 const during=new AbortController();const cancel=async x=>{during.abort();return item(x);};await assert.rejects(createQueryIteration(plan,source,mapping,cancel)({ids:['a','b']},{},{signal:during.signal}),/CANCELLED/);
 const slow=async x=>{await new Promise(r=>setTimeout(r,10));return source(x);};await assert.rejects(createQueryIteration({...plan,timeoutMs:1},slow,mapping,item)({ids:[]}),/TIMEOUT/);
});
async function fixture(fn){const dir=mkdtempSync(join(tmpdir(),'alch-iteration-negative-'));try{cpSync(here,dir,{recursive:true});await fn(dir);}finally{rmSync(dir,{recursive:true,force:true});}}
const replace=(dir,file,from,to)=>writeFileSync(join(dir,file),readFileSync(join(dir,file),'utf8').replace(from,to));
test('compiler resolves the typed pure source/mapping/item chain',async()=>{
 const checked=await checkQueryIteration(join(here,'models.alch'));assert.equal(checked.status,'valid');assert.equal(checked.plan.maxItems,100);
});
test('compiler rejects unknown or duplicate syntax, unsafe selectors and unsupported bounds/policy',async()=>{
 for(const [from,to]of [['concurrency 1','concurrency 2'],['order input','order sorted'],['partial-result reject','partial-result keep'],['max-items 100','max-items 101'],['max-output-bytes 65536','max-output-bytes 0'],['output-field models','output-field constructor'],['source-field aliases','source-field absent'],['profile query-iteration-v1','profile query-iteration-v1\nprofile query-iteration-v1'],['order input','order input\narbitrary executable']])await fixture(async dir=>{replace(dir,'models.alch',from,to);await assert.rejects(checkQueryIteration(join(dir,'models.alch')),/QUERY_ITERATION/);});
});
test('compiler rejects mismatched mapping interfaces and effectful or transitive dependencies',async()=>{
 await fixture(async dir=>{replace(dir,'summary-input.alch','item: identifier','item: string');await assert.rejects(checkQueryIteration(join(dir,'models.alch')),/incompatible interface/);});
 const remoteFiles=dir=>{for(const name of ['mapped-call','prepare','remote'])cpSync(join(here,'../support-audit/'+name+'.alch'),join(dir,name+'.alch'));};
 await fixture(async dir=>{remoteFiles(dir);replace(dir,'models.alch','"./model-summary.alch"','"./mapped-call.alch"');await assert.rejects(checkQueryIteration(join(dir,'models.alch')),/effectful dependency/);});
 await fixture(async dir=>{remoteFiles(dir);replace(dir,'model-summary.alch','owner inference-router-owner','import Effect from "./mapped-call.alch"\nowner inference-router-owner');await assert.rejects(checkQueryIteration(join(dir,'models.alch')),/effectful dependency/);});
});
test('module traversal/symlink escape and existing output reject before publication',async()=>{
 await fixture(async dir=>{replace(dir,'models.alch','"./aliases.alch"','"../aliases.alch"');await assert.rejects(checkQueryIteration(join(dir,'models.alch')),/relative module/);});
 await fixture(async dir=>{symlinkSync(join(here,'aliases.alch'),join(dir,'outside.alch'));replace(dir,'models.alch','"./aliases.alch"','"./outside.alch"');await assert.rejects(checkQueryIteration(join(dir,'models.alch')),/module escape/);});
 await assert.rejects(buildQueryIteration(join(here,'models.alch'),here),/output exists/);
});
