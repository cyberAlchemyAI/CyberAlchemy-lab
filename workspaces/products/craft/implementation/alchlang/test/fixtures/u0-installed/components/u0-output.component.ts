// H01 installed adaptation of craft/projects/domainspec-v2/impl/cli/test/u0-output.test.ts.
// All positive producers are actual packaged dist modules; negative-only custody stubs retain component scope.
// Open Questions: ../README.md and H01 CONTEXT. No original task file changed.
import test,{type TestContext} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const installedCore=path.join(process.env.U0_INSTALLED_CONSUMER!,'node_modules/@domainspec-v2/cli');
const {compileProject}=await import(pathToFileURL(path.join(installedCore,'dist','compilation/certificate.js')).href);
const {checkDirectBusinessSourceGraphV2}=await import(pathToFileURL(path.join(installedCore,'dist','formalization/direct-condition-binding.js')).href);
const {createDirectPureSourceComponentOwnerV2,createBusinessPureGenerationOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/application-adapter.js')).href);
const {createDirectSourceOutputOwnerV2,createBusinessOutputWriterOwnerV2,relocateU0EntrySourceDataV2,deriveDirectApiOutputDataV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-output.js')).href);
const {planBusinessOutputsV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-coverage-contract-v2.js')).href);
const {createBusinessCoreRecipeOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-recipes.js')).href);
const {createBusinessReviewOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-decision.js')).href);
const {createAuthoringBusinessInputOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-input.js')).href);
const {createBusinessDirectApplicationOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-application.js')).href);
const {createBusinessRequestStagesOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-request.js')).href);
const {createBusinessDirectCoverageOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-coverage.js')).href);
const {createBusinessCoverageViewsOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-views.js')).href);
const {U0_CONFIG_EXAMPLE}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/u0-realization-contract.js')).href);
const {loadAtomicPublicationNative}=await import(pathToFileURL(path.join(installedCore,'dist','generation/atomic-publication-native.js')).href);
// Positive output/currentness tests use real source/compiler/generated components.
// No accepted application, selected native basis or BusinessOutputResult is faked.
// Open Questions: V02 full original selected/bound/views output/runtime witness.
const cli=installedCore,root=process.env.U0_INSTALLED_CONSUMER!,alch=path.join(root,'node_modules/@cyberalchemy/alchlang/dist');
const original=fs.readFileSync(new URL('../business.alch',import.meta.url),'utf8');
const prefix='.domainspec-business-uout-';
async function fixture(t:TestContext,text=original){
 loadAtomicPublicationNative();
 const parser=await import(pathToFileURL(path.join(alch,'business-authoring-parser.js')).href),resolver=await import(pathToFileURL(path.join(alch,'business-authoring-resolve.js')).href),carriers=await import(pathToFileURL(path.join(alch,'business-authoring-carriers.js')).href),lower=await import(pathToFileURL(path.join(alch,'application-domain-lowering.js')).href);
 const business=resolver.resolveBusinessSpecV2(parser.parseBusinessSourceV2(text)),lowered=carriers.lowerDirectBusinessV2(business),formation=lower.lowerDirectApplicationDomainV2(lowered),directory=fs.mkdtempSync(path.join(os.tmpdir(),'craft-u11-'));t.after(()=>fs.rmSync(directory,{recursive:true,force:true}));
 const project=path.join(directory,'project'),parent=path.join(directory,'outputs');fs.mkdirSync(project);fs.mkdirSync(parent);fs.writeFileSync(path.join(parent,'sentinel'),'prior bytes');
 for(const [relative,content]of Object.entries(formation.projectFiles)){const file=path.join(project,relative);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,content as string);}
 const checked=checkDirectBusinessSourceGraphV2(compileProject(project).graph,{source:business.source,spec:business.data,executable:lowered.executable,assurance:lowered.assurance}),generation=createDirectPureSourceComponentOwnerV2(),source=generation.generate(checked),writer=createDirectSourceOutputOwnerV2(generation),target=path.join(parent,'application');
 return {directory,project,parent,target,checked,generation,source,writer,stages:()=>fs.readdirSync(parent).filter(name=>name.startsWith(prefix)),assertPrior:()=>assert.equal(fs.readFileSync(path.join(parent,'sentinel'),'utf8'),'prior bytes')};
}
function interceptWrites(run:()=>void,inject:(fd:number,content:unknown)=>void){
 const write=fs.writeFileSync;fs.writeFileSync=((file:any,...args:any[])=>{const result=(write as any)(file,...args);if(typeof file==='number')inject(file,args[0]);return result;}) as any;
 try{run();}finally{fs.writeFileSync=write;}
}
test('U11 real generated source publishes one exact fresh tree, then imports actual synchronous behavior',async t=>{
 const f=await fixture(t),result=f.writer.publish(f.source,f.target);assert.equal(result.kind,'published-direct-source-output-component-v2');assert.equal(Object.hasOwn(result,'rows'),false);assert.equal(result.files.length,6);assert.equal(f.stages().length,0);
 for(const file of f.source.files)assert.equal(fs.readFileSync(path.join(f.target,file.path),'utf8'),file.content);
 assert.equal(f.writer.check(f.source,f.target).kind,'checked-direct-source-output-component-v2');
 const callable=await f.generation.importGenerated(f.source,path.join(f.target,'invoke.mjs'));assert.equal(callable.invoke({id:9007199254740993n,verified:true}).kind,'completed');assert.equal(callable.invoke({id:1n,verified:false}).kind,'rejected');f.assertPrior();
});
test('U11 source module closure remains runnable after physical relocation without original output fallback',async t=>{
 const f=await fixture(t);f.writer.publish(f.source,f.target);const relocated=path.join(f.parent,'relocated');fs.renameSync(f.target,relocated);assert.equal(fs.existsSync(f.target),false);
 f.writer.check(f.source,relocated);const callable=await f.generation.importGenerated(f.source,path.join(relocated,'invoke.mjs')),result=callable.invoke({id:18446744073709551615n,verified:true});assert.equal(result.kind,'completed');if(result.kind==='completed')assert.equal(result.value.id,18446744073709551615n);
});
test('U11 existing empty, nonempty and symlink targets preserve all previous bytes and identities',async t=>{
 for(const kind of ['empty','nonempty','symlink']){
  const f=await fixture(t);if(kind==='symlink'){const outside=path.join(f.directory,'outside');fs.mkdirSync(outside);fs.writeFileSync(path.join(outside,'prior'),'unchanged');fs.symlinkSync(outside,f.target);}else{fs.mkdirSync(f.target);if(kind==='nonempty')fs.writeFileSync(path.join(f.target,'prior'),'unchanged');}
  const before=fs.lstatSync(f.target,{bigint:true});assert.throws(()=>f.writer.publish(f.source,f.target),{code:'DS_ATOMIC_EXISTS'});assert.equal(fs.lstatSync(f.target,{bigint:true}).ino,before.ino);if(kind!=='empty')assert.equal(fs.readFileSync(path.join(f.target,'prior'),'utf8'),'unchanged');assert.equal(f.stages().length,0);f.assertPrior();
 }
});
test('U11 relative, root, traversal and symbolic-parent output paths cannot redirect writes',async t=>{
 const f=await fixture(t);
 for(const target of ['relative','/',f.parent+'/../escape',f.target+'\n'])assert.throws(()=>f.writer.publish(f.source,target),/BUSINESS_OUTPUT_PATH/);
 const outside=path.join(f.directory,'outside');fs.mkdirSync(outside);const link=path.join(f.directory,'linked');fs.symlinkSync(outside,link);assert.throws(()=>f.writer.publish(f.source,path.join(link,'application')),/real parent|DS_ATOMIC_PARENT/);assert.deepEqual(fs.readdirSync(outside),[]);f.assertPrior();
});
test('U11 missing, truncated, same-inode changed and foreign output entries fail exact current checks without repair',async t=>{
 for(const kind of ['missing','truncated','changed','foreign']){
  const f=await fixture(t);f.writer.publish(f.source,f.target);const file=path.join(f.target,'invoke.mjs');
  if(kind==='missing')fs.unlinkSync(file);else if(kind==='foreign')fs.writeFileSync(path.join(f.target,'foreign'),'retain');else if(kind==='truncated')fs.truncateSync(file,1);else{const before=fs.statSync(file,{bigint:true});const fd=fs.openSync(file,'r+');try{fs.writeSync(fd,Buffer.from('!'),0,1,0);}finally{fs.closeSync(fd);}assert.equal(fs.statSync(file,{bigint:true}).ino,before.ino);}
  assert.throws(()=>f.writer.check(f.source,f.target),/BUSINESS_OUTPUT_TREE|ENOENT/);if(kind==='foreign')assert.equal(fs.readFileSync(path.join(f.target,'foreign'),'utf8'),'retain');f.assertPrior();
 }
});
test('U11 symlink substitution in an existing output is never followed or cleaned',async t=>{
 const f=await fixture(t);f.writer.publish(f.source,f.target);const file=path.join(f.target,'invoke.mjs'),outside=path.join(f.directory,'outside.mjs');fs.writeFileSync(outside,'outside');fs.unlinkSync(file);fs.symlinkSync(outside,file);
 assert.throws(()=>f.writer.check(f.source,f.target),/BUSINESS_OUTPUT_FILE/);assert.equal(fs.readFileSync(outside,'utf8'),'outside');assert.ok(fs.lstatSync(file).isSymbolicLink());f.assertPrior();
});
test('U11 partial-write failure retains its private stage and never creates a public target',async t=>{
 const f=await fixture(t),write=fs.writeFileSync;let interrupted=false;fs.writeFileSync=((file:any,...args:any[])=>{if(typeof file==='number'){interrupted=true;throw Error('injected write failure');}return (write as any)(file,...args);}) as any;
 try{assert.throws(()=>f.writer.publish(f.source,f.target),/injected write failure/);}finally{fs.writeFileSync=write;}
 assert.ok(interrupted);assert.equal(fs.existsSync(f.target),false);assert.equal(f.stages().length,1);f.assertPrior();
});
test('U11 source drift during staging stops finalization and preserves failed evidence',async t=>{
 const f=await fixture(t);let changed=false;
 interceptWrites(()=>assert.throws(()=>f.writer.publish(f.source,f.target),/BUSINESS_DIRECT_CONDITION_FILE_STALE/),()=>{if(changed)return;changed=true;const file=path.join(f.project,'specs/dispatching/nodes/can-process.json');fs.appendFileSync(file,'\n');});
 assert.ok(changed);assert.equal(fs.existsSync(f.target),false);assert.equal(f.stages().length,1);f.assertPrior();
});
test('U11 staged same-inode byte mutation is detected after atomic owner inventory checks',async t=>{
 const f=await fixture(t);let changed=false;
 interceptWrites(()=>assert.throws(()=>f.writer.publish(f.source,f.target),/BUSINESS_OUTPUT_TREE/),(fd)=>{if(changed)return;changed=true;fs.writeSync(fd,Buffer.from('!'),0,1,0);});
 assert.ok(changed);assert.equal(fs.existsSync(f.target),false);assert.equal(f.stages().length,1);f.assertPrior();
});
test('U11 a competing target appearing during staging survives kernel no-replace unchanged',async t=>{
 const f=await fixture(t);let competing:bigint|undefined;
 interceptWrites(()=>assert.throws(()=>f.writer.publish(f.source,f.target),{code:'DS_ATOMIC_EXISTS'}),()=>{if(competing)return;fs.mkdirSync(f.target);competing=fs.lstatSync(f.target,{bigint:true}).ino;fs.writeFileSync(path.join(f.target,'foreign'),'retain');});
 assert.equal(fs.lstatSync(f.target,{bigint:true}).ino,competing);assert.equal(fs.readFileSync(path.join(f.target,'foreign'),'utf8'),'retain');assert.equal(f.stages().length,1);f.assertPrior();
});
test('U11 renamed/symlinked output parent never redirects writes into a replacement directory',async t=>{
 const f=await fixture(t),moved=path.join(f.directory,'moved'),outside=path.join(f.directory,'outside');fs.mkdirSync(outside);fs.writeFileSync(path.join(outside,'foreign'),'retain');let changed=false;
 interceptWrites(()=>assert.throws(()=>f.writer.publish(f.source,f.target),/output parent identity changed|DS_ATOMIC_IDENTITY/),()=>{if(changed)return;changed=true;fs.renameSync(f.parent,moved);fs.symlinkSync(outside,f.parent);});
 assert.ok(changed);assert.deepEqual(fs.readdirSync(outside),['foreign']);assert.equal(fs.readFileSync(path.join(outside,'foreign'),'utf8'),'retain');assert.equal(fs.readFileSync(path.join(moved,'sentinel'),'utf8'),'prior bytes');assert.ok(fs.readdirSync(moved).some(name=>name.startsWith(prefix)));
});
test('U11 cloned/serialized generated source cannot become an output producer',async t=>{
 const f=await fixture(t);let traps=0;
 for(const source of [{...f.source},structuredClone(f.source),new Proxy(f.source,{get(){traps++;throw Error('trap');}})])assert.throws(()=>f.writer.publish(source,f.target),/BUSINESS_PURE_HANDLE/);
 assert.equal(traps,0);assert.equal(fs.existsSync(f.target),false);f.assertPrior();
});
test('U11 optional formal outputs stay explicitly unsupported and unavailable required outputs reject',()=>{
 const plan=planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind:'api-contracts',requiredness:'required'},{kind:'base-model',requiredness:'optional'}]);assert.deepEqual(plan.outputs.map((row:{state:string})=>row.state),['pending-producer','pending-producer','unsupported-optional']);
 for(const kind of ['base-model','conjecture-problems'] as const)assert.throws(()=>planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind,requiredness:'required'}]),/BUSINESS_V2_OUTPUT_UNSUPPORTED/);
});
test('U11 real generated callable and actual native HTTP components run through the relocated entry after construction files are removed',async t=>{
 const f=await fixture(t),construction=path.join(f.directory,'construction with spaces'),output=path.join(f.directory,'bundle'),relocated=path.join(f.directory,'relocated');fs.mkdirSync(construction);fs.mkdirSync(output);fs.mkdirSync(path.join(output,'callable'));fs.mkdirSync(path.join(output,'runtime'));
 for(const file of f.source.files)fs.writeFileSync(path.join(output,'callable',file.path),file.content);
 const native=path.join(cli,'profiles/node-http-entry-u0-v4/runtime'),compiled=path.join(f.directory,'native-compiled'),nativeFiles=['application-http.mts','u0-json-decode.ts','u0-values.ts','u0-json-encode.ts'];
 // Consume all four actual installed native assets; no source transpiler or @types/node dependency.
 for(const filename of nativeFiles){const name=filename.replace(/\.mts$/,'.mjs').replace(/\.ts$/,'.js');fs.copyFileSync(path.join(native,name),path.join(output,'runtime',name));}
 fs.writeFileSync(path.join(output,'package.json'),'{"type":"module","private":true}\n');
 const originalCallable=path.join(construction,'invoke.mjs'),originalHandler=path.join(construction,'application-http.mjs');
 // Real component assembly, not BoundU0EntryV2 or a selected/native subject.
 const entry='import {invoke} from '+JSON.stringify(pathToFileURL(originalCallable).href)+';\nimport {createU0HttpHandler} from '+JSON.stringify(pathToFileURL(originalHandler).href)+';\nexport {invoke as boundInvoke};\nexport const handler=createU0HttpHandler(invoke,'+JSON.stringify(U0_CONFIG_EXAMPLE)+','+JSON.stringify({rejection_code:f.checked.operation.rejection_code})+');\n';
 const data=relocateU0EntrySourceDataV2(entry,originalCallable,originalHandler);assert.equal(data.kind,'u0-entry-relocation-data-v2');assert.equal(Object.hasOwn(data,'subject'),false);assert.equal(data.content.includes(pathToFileURL(construction).href),false);fs.writeFileSync(path.join(output,'entry.mjs'),data.content);fs.renameSync(output,relocated);fs.rmSync(construction,{recursive:true});
 const vectors=[['{"id":"9007199254740993","verified":true}',200,'{"kind":"completed","value":{"id":"9007199254740993","verified":true}}'],['{"id":"2","verified":false}',422,'{"kind":"rejected","code":"delivery-verification-required"}'],['{"id":2,"verified":true}',400,'{"kind":"adapter-error","code":"invalid-request"}']];
 // Observe actual emitted JavaScript in plain Node: TSX can redirect static
 // .mjs imports to their adjacent .mts sources and split function identities.
 const runner="import assert from 'node:assert/strict';const actual=await import(process.argv[1]),invoke=await import(process.argv[2]);assert.equal(actual.boundInvoke,invoke.invoke);for(const [body,status,expected]of "+JSON.stringify(vectors)+"){const response=await actual.handler(new Request('http://component.test/confirm-delivery',{method:'POST',headers:{'content-type':'application/json'},body}));assert.equal(response.status,status);assert.equal(await response.text(),expected);}";
 const observed=spawnSync(process.execPath,['--input-type','module','-e',runner,pathToFileURL(path.join(relocated,'entry.mjs')).href,pathToFileURL(path.join(relocated,'callable/invoke.mjs')).href],{cwd:f.directory,encoding:'utf8'});assert.equal(observed.status,0,observed.stdout+observed.stderr);t.diagnostic('Actual installed compiled native components; relocation observed in plain Node without a private compiler or source fallback.');
});
test('U11 relocation data rejects missing/repeated import literals and unsupported runtime filenames',async t=>{
 const f=await fixture(t),callable=path.join(f.directory,'invoke.mjs'),handler=path.join(f.directory,'application-http.mjs'),text='import {invoke} from '+JSON.stringify(pathToFileURL(callable).href)+';\nimport {createU0HttpHandler} from '+JSON.stringify(pathToFileURL(handler).href)+';\n';
 assert.throws(()=>relocateU0EntrySourceDataV2('',callable,handler),/BUSINESS_OUTPUT_RELOCATION/);assert.throws(()=>relocateU0EntrySourceDataV2(text+text,callable,handler),/BUSINESS_OUTPUT_RELOCATION/);assert.throws(()=>relocateU0EntrySourceDataV2(text,callable,handler+'.ts'),/BUSINESS_OUTPUT_RELOCATION/);
});
function productionWriter(){
 let producers=0;
 const recipes=createBusinessCoreRecipeOwnerV2({assertCurrent(){producers++;throw Error('actual native required');},capture(){throw Error('actual capture required');}}),reviews=createBusinessReviewOwnerV2(recipes);
 const forwarding={generate(){throw Error('actual generated required');},async importGenerated(){throw Error('actual import required');},assertCurrent(){producers++;throw Error('actual original import required');}};
 const native={assertCurrent(){producers++;throw Error('actual basis required');},assertSelectionBasis(){throw Error('actual selected basis required');},assets(){throw Error('actual native assets required');}};
 const requests=createBusinessRequestStagesOwnerV2(recipes,forwarding,native),inputs=createAuthoringBusinessInputOwnerV2(recipes,reviews,requests),applications=createBusinessDirectApplicationOwnerV2(inputs,{capture(){producers++;throw Error('actual graph required');},assertCurrent(){throw Error('actual graph required');}}),generation=createBusinessPureGenerationOwnerV2(applications),coverage=createBusinessDirectCoverageOwnerV2(inputs,applications,requests,generation),views=createBusinessCoverageViewsOwnerV2(coverage);
 return {writer:createBusinessOutputWriterOwnerV2(applications,requests,generation,views,native),producers:()=>producers};
}
test('U11 raw/serialized application, bound/view and artifact data cannot finalize a production bundle',()=>{
 const {writer,producers}=productionWriter(),plan=planBusinessOutputsV2([{kind:'code',requiredness:'required'}]);let accessors=0;
 for(const fake of [{},{accepted:true},new Proxy({},{get(){accessors++;throw Error('trap');}})])assert.throws(()=>writer.prepareArtifacts(plan,fake as never,{} as never,{} as never),/UNREGISTERED/);
 const request={target:'/tmp/not-created-u11',plan,application:{} as any,bound:{} as any,views:{} as any,artifacts:[]};assert.throws(()=>writer.publish(request),/BUSINESS_OUTPUT_HANDLE/);assert.throws(()=>writer.check(request),/BUSINESS_OUTPUT_HANDLE/);assert.throws(()=>writer.publish({...request,get artifacts(){accessors++;return [];}}),/BUSINESS_OUTPUT_REQUEST/);assert.equal(producers(),0);assert.equal(accessors,0);assert.equal(fs.existsSync(request.target),false);
});

test('U11 API contract exposes fixed wire fields, exact integer domain and source-specific semantic aliases',async t=>{
 const text=original.replace('id UInt64','ack_id UInt64').replace('identity id','identity ack_id').replace('verified Bool','approved Bool').replace('condition item.verified','condition item.approved'),f=await fixture(t,text),api=deriveDirectApiOutputDataV2(f.checked,U0_CONFIG_EXAMPLE),payload=api.wire_payload as any;
 assert.deepEqual(payload.fields.map((row:any)=>[row.name,row.domain_field,row.json_type]),[['id','ack_id','string'],['verified','approved','boolean']]);assert.equal(payload.fields[0].minimum,'0');assert.equal(payload.fields[0].maximum,'18446744073709551615');assert.equal(payload.decoded_duplicate_members,'reject');assert.equal((api.mapping_owners as any[]).length,2);assert.equal((api.outcomes as any).rejected.code,f.checked.operation.rejection_code);
 assert.equal(Object.hasOwn(api,'native_basis'),false);assert.equal(Object.hasOwn(api,'realized_sha256'),false);
});
test('U11 API projection refuses raw source records and unsupported wire configuration',async t=>{
 const f=await fixture(t);assert.throws(()=>deriveDirectApiOutputDataV2({...f.checked},U0_CONFIG_EXAMPLE),/BUSINESS_DIRECT_CONDITION_HANDLE/);assert.throws(()=>deriveDirectApiOutputDataV2(f.checked,{...U0_CONFIG_EXAMPLE,request_bytes:1}),/U0_CONFIG_COVERAGE/);
});
