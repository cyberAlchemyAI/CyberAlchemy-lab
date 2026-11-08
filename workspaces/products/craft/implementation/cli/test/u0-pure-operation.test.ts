import test,{type TestContext} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync,renameSync,symlinkSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {compileProject} from '../src/compilation/certificate.js';
import {checkDirectBusinessSourceGraphV2} from '../src/formalization/direct-condition-binding.js';
import {renderConfiguredDirectPureOperationV2} from '../src/generation/configured-operation-source.js';
import {renderExactUInt64Support} from '../src/generation/configured-exact-uint64-source.js';
import {createDirectPureSourceComponentOwnerV2,createBusinessPureGenerationOwnerV2} from '../src/profile-engine/application-adapter.js';
import {createBusinessDirectApplicationOwnerV2} from '../src/profile-engine/business-authoring-application.js';
// Real source/compiled/typed/generated components; never a fabricated accepted
// application, selected native basis or production ImportedU0CallableV2.
// Open Questions: G01 original application witness; U08 actual late native join.
const root=path.resolve(import.meta.dirname,'../../../../../..'),alch=path.join(root,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src');
const original=readFileSync(new URL('profile-engine/fixtures/u0-v2/business.alch',import.meta.url),'utf8');
async function fixture(t:TestContext,text=original){
 const parser=await import(pathToFileURL(path.join(alch,'business-authoring-parser.ts')).href),resolver=await import(pathToFileURL(path.join(alch,'business-authoring-resolve.ts')).href),carriers=await import(pathToFileURL(path.join(alch,'business-authoring-carriers.ts')).href),lower=await import(pathToFileURL(path.join(alch,'application-domain-lowering.ts')).href);
 const business=resolver.resolveBusinessSpecV2(parser.parseBusinessSourceV2(text)),lowered=carriers.lowerDirectBusinessV2(business),formation=lower.lowerDirectApplicationDomainV2(lowered);
 const directory=mkdtempSync(path.join(os.tmpdir(),'craft-u05-'));t.after(()=>rmSync(directory,{recursive:true,force:true}));
 const project=path.join(directory,'project');mkdirSync(project);
 for(const [relative,content]of Object.entries(formation.projectFiles)){const target=path.join(project,relative);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,content as string);}
 const checked=checkDirectBusinessSourceGraphV2(compileProject(project).graph,{source:business.source,spec:business.data,executable:lowered.executable,assurance:lowered.assurance});
 const owner=createDirectPureSourceComponentOwnerV2(),generated=owner.generate(checked),output=path.join(directory,'generated');mkdirSync(output);
 for(const file of generated.files)writeFileSync(path.join(output,file.path),file.content);
 const entry=path.join(output,'invoke.mjs'),load=()=>owner.importGenerated(generated,entry);
 return {directory,project,checked,owner,generated,output,entry,load};
}
const plain=(value:unknown)=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==='bigint'?item.toString():item));
test('U05 real zero-claim typed source emits and imports synchronous completed and authored rejected module',async t=>{
 const f=await fixture(t),callable=await f.load();f.owner.assertCurrent(callable);
 assert.equal(f.checked.checked.transfer.spec.claims.length,0);assert.equal(callable.kind,'imported-direct-pure-source-component-v2');assert.equal(Object.hasOwn(callable,'application'),false);
 const completed=callable.invoke({id:31n,verified:true}),rejected=callable.invoke({id:32n,verified:false});
 assert.deepEqual(plain(completed),{kind:'completed',value:{id:'31',verified:true}});assert.deepEqual(plain(rejected),{kind:'rejected',code:'delivery-verification-required'});
 assert.equal(completed instanceof Promise,false);assert.equal(callable.invoke.length,1);
 const module=await import(pathToFileURL(f.entry).href);assert.equal(callable.invoke,module.invoke,'canonical URL retains original function identity for Q01');
});
test('U05 generated TypeScript strict-checks across the real emitted Rule/Operation/invocation closure',async t=>{
 const f=await fixture(t),tsc=path.resolve(import.meta.dirname,'../node_modules/typescript/bin/tsc');
 const result=spawnSync(process.execPath,[tsc,'--ignoreConfig','--noEmit','--strict','--noUncheckedIndexedAccess','--exactOptionalPropertyTypes','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--types','node','--skipLibCheck',...f.generated.files.filter(file=>file.path.endsWith('.mts')).map(file=>path.join(f.output,file.path))],{encoding:'utf8',cwd:path.resolve(import.meta.dirname,'..')});
 assert.equal(result.status,0,result.stdout+result.stderr);await f.load();
});
test('U05 generated source contains the real exact scalar producer and structured Rule specialization',async t=>{
 const f=await fixture(t),operation=f.generated.files.find(file=>file.path==='operation.mts')!.content,rule=f.generated.files.find(file=>file.path==='rule.mts')!.content;
 assert.ok(operation.includes(renderExactUInt64Support()));assert.ok(rule.includes('export const directGuard'));assert.ok(rule.includes('BUSINESS-DISPATCHING-SUBMISSION#verified')===false,'ontology references lower to statically checked access, not runtime lookup');
 for(const file of f.generated.files){for(const pattern of [/\basync\b/,/\bawait\b/,/store\./,/\btransaction\b/,/\bcommit\s*\(/,/\brollback\s*\(/,/\beval\s*\(/,/\bnew Function\b/,/\bobserve\b/,/\.\/.*src\//])assert.equal(pattern.test(file.content),false,file.path+':'+pattern);}
 await f.load();
});
test('U05 native UInt64 boundaries remain exact and successful outputs are fresh owned immutable records',async t=>{
 const f=await fixture(t),callable=await f.load();
 for(const id of [0n,1n,9007199254740991n,9007199254740992n,9007199254740993n,18446744073709551615n]){
  const input={id,verified:true},outcome=callable.invoke(input);assert.equal(outcome.kind,'completed');if(outcome.kind!=='completed')assert.fail();
  assert.equal(outcome.value.id,id);assert.notEqual(outcome.value,input);assert.equal(Object.getPrototypeOf(outcome.value),null);assert.ok(Object.isFrozen(outcome)&&Object.isFrozen(outcome.value));
  input.id=2n;input.verified=false;assert.equal(outcome.value.id,id);assert.equal(outcome.value.verified,true);
 }
});
test('U05 malformed native values throw a boundary error and cannot masquerade as business rejection',async t=>{
 const f=await fixture(t),callable=await f.load();
 for(const input of [null,undefined,true,[],Promise.resolve({id:1n,verified:false}),{id:1,verified:false},{id:'1',verified:false},{id:-1n,verified:false},{id:18446744073709551616n,verified:false},{id:1n,verified:0},{id:1n},{verified:false},{id:1n,verified:false,extra:1},new Number(1),{id:1n,verified:new Boolean(false)}]){
  assert.throws(()=>callable.invoke(input as never),error=>error instanceof TypeError&&(error as {code?:string}).code==='U0_INPUT_CONTRACT');
 }
});
test('U05 hostile descriptors, proxies, custom prototypes and thenables execute no callbacks',async t=>{
 const f=await fixture(t),callable=await f.load();let callbacks=0;
 const accessor=Object.defineProperties({}, {id:{enumerable:true,get(){callbacks++;return 1n;}},verified:{enumerable:true,value:false}});
 const hidden=Object.defineProperties({}, {id:{enumerable:true,value:1n},verified:{enumerable:false,value:false}});
 const proxy=new Proxy({id:1n,verified:false},{getPrototypeOf(){callbacks++;throw Error('trap');},ownKeys(){callbacks++;throw Error('trap');}});
 const inherited=Object.assign(Object.create({parent:true}),{id:1n,verified:false}),symbol={id:1n,verified:false,[Symbol()]:true},thenable={id:1n,verified:false,then(){callbacks++;}};
 for(const value of [accessor,hidden,proxy,inherited,symbol,thenable])assert.throws(()=>callable.invoke(value),/U0_INPUT_CONTRACT/);
 assert.equal(callbacks,0);const nullRecord=Object.assign(Object.create(null),{id:1n,verified:true});assert.equal(callable.invoke(nullRecord).kind,'completed');
});
test('U05 source-specific field aliases lower into the fixed native ABI',async t=>{
 const text=original.replace('id UInt64','ack_id UInt64').replace('identity id','identity ack_id').replace('verified Bool','approved Bool').replace('condition item.verified','condition item.approved');
 const f=await fixture(t,text),callable=await f.load();assert.deepEqual(plain(callable.invoke({id:99n,verified:true})),{kind:'completed',value:{id:'99',verified:true}});
 assert.equal(callable.invoke({id:99n,verified:false}).kind,'rejected');
 const domain=await import(pathToFileURL(path.join(f.output,'operation.mjs')).href);assert.deepEqual(plain(domain.runOperation({ack_id:4n,approved:true})),{kind:'completed',value:{ack_id:'4',approved:true}});
 assert.throws(()=>callable.invoke({ack_id:1n,approved:true} as never),/U0_INPUT_CONTRACT/);
});
test('U05 changing the authored rejection changes actual regenerated behavior',async t=>{
 const f=await fixture(t,original.replace('on-rejection delivery-verification-required','on-rejection acknowledgement-not-approved')),callable=await f.load();
 assert.deepEqual(plain(callable.invoke({id:1n,verified:false})),{kind:'rejected',code:'acknowledgement-not-approved'});
 assert.equal(callable.invoke({id:1n,verified:true}).kind,'completed');
});
test('U05 Operation/Rule Entity parameter names can change without runtime lookup or feature callbacks',async t=>{
 const text=original.replace('input item Submission','input delivery Submission').replace('condition item.verified','condition delivery.verified').replace('input request Submission','input envelope Submission').replace('CanProcess(item: request)','CanProcess(delivery: envelope)').replace('returns request','returns envelope');
 const f=await fixture(t,text),callable=await f.load();assert.equal(callable.invoke({id:8n,verified:true}).kind,'completed');assert.equal(callable.invoke({id:8n,verified:false}).kind,'rejected');
});
test('U05 cloned, effectful or unsupported graph/plan data cannot enter the pure source renderer',async t=>{
 const f=await fixture(t);
 for(const source of [{...f.checked},{...f.checked,operation:{...f.checked.operation,effects:[{kind:'write'}]}},new Proxy(f.checked,{})])assert.throws(()=>renderConfiguredDirectPureOperationV2(source as never),/BUSINESS_DIRECT_CONDITION_HANDLE/);
 await f.load();
});
test('U05 generation is deterministic for the same genuine source; component custody is instance-scoped',async t=>{
 const f=await fixture(t),again=f.owner.generate(f.checked);assert.equal(again.source_sha256,f.generated.source_sha256);assert.deepEqual(again.files,f.generated.files);
 assert.throws(()=>f.owner.assertSourceCurrent({...f.generated}),/BUSINESS_PURE_HANDLE/);
 await assert.rejects(()=>createDirectPureSourceComponentOwnerV2().importGenerated(f.generated,f.entry),/BUSINESS_PURE_HANDLE/);
 const callable=await f.load();assert.throws(()=>f.owner.assertCurrent({...callable}),/BUSINESS_PURE_HANDLE/);
 await assert.rejects(()=>f.owner.importGenerated(f.generated,f.entry),/BUSINESS_PURE_IMPORT_EPOCH/);
});
test('U05 tampered executable bytes reject before module evaluation',async t=>{
 const f=await fixture(t);writeFileSync(f.entry,readFileSync(f.entry,'utf8')+'\nglobalThis.__u05UnexpectedEvaluation=true;\n');
 await assert.rejects(f.load,/BUSINESS_PURE_EMITTED_BYTES/);assert.equal((globalThis as any).__u05UnexpectedEvaluation,undefined);
});
test('U05 changed generated typed source or imported Rule closure retires currentness',async t=>{
 const f=await fixture(t),callable=await f.load();writeFileSync(path.join(f.output,'rule.mjs'),readFileSync(path.join(f.output,'rule.mjs'),'utf8')+'\n');
 assert.throws(()=>f.owner.assertCurrent(callable),/BUSINESS_PURE_FILE_STALE/);
});
test('U05 identical executable inode replacement and symlink output are not fresh imports',async t=>{
 const f=await fixture(t),callable=await f.load(),old=readFileSync(f.entry);renameSync(f.entry,f.entry+'.old');writeFileSync(f.entry,old);
 assert.throws(()=>f.owner.assertCurrent(callable),/BUSINESS_PURE_FILE_STALE/);
 const other=await fixture(t);renameSync(other.entry,other.entry+'.old');symlinkSync(other.entry+'.old',other.entry);await assert.rejects(other.load,/BUSINESS_PURE_FILE/);
});
test('U05 original compiled source changes invalidate generated/imported custody',async t=>{
 const f=await fixture(t),callable=await f.load(),file=path.join(f.project,'specs/dispatching/nodes/can-process.json');writeFileSync(file,readFileSync(file,'utf8')+'\n');
 assert.throws(()=>f.owner.assertCurrent(callable),/BUSINESS_DIRECT_CONDITION_FILE_STALE/);
});
test('U05 application generation rejects raw inputs and source components before invoking a graph capture',async t=>{
 let captures=0;
 const applications=createBusinessDirectApplicationOwnerV2({form(){throw Error('unused');},assertCurrent(){throw Error('original selected input required');}},{capture(){captures++;throw Error('unused');},assertCurrent(){throw Error('unused');}});
 const owner=createBusinessPureGenerationOwnerV2(applications);
 assert.throws(()=>owner.generate({} as never),/BUSINESS_AUTHORING_APPLICATION_UNREGISTERED/);assert.equal(captures,0);
 const f=await fixture(t);await assert.rejects(()=>owner.importGenerated(f.generated as never,f.entry),/BUSINESS_PURE_HANDLE/);
 const callable=await f.load();assert.throws(()=>owner.assertCurrent(callable as never),/BUSINESS_PURE_HANDLE/);
});
