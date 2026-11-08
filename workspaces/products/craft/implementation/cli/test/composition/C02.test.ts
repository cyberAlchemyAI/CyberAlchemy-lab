/** Independent cumulative Rule + Operation expectations, frozen before implementation results.
 * Open Questions: r5/contracts/C02/oracle-v1.json. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,readdirSync,rmSync,existsSync,renameSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {parseCoreCommerceSyntax} from '../../src/commerce/commerce-core-syntax.js';
import {assertPureOperationPlan} from '../../src/generic/pure-operation.js';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createOriginalPureOperationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const cli=fileURLToPath(new URL('../../',import.meta.url));
const base=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5');
const contracts=path.join(base,'contracts/C02'),previous=path.join(base,'contracts/C01');
const source=readFileSync(path.join(contracts,'request.alch'),'utf8'),laboratory=readFileSync(path.join(contracts,'laboratory.alch'),'utf8');
const profile=JSON.parse(readFileSync(path.join(contracts,'profile.json'),'utf8')),bounds=JSON.parse(readFileSync(path.join(contracts,'bounds.json'),'utf8'));
const sha=(x:string|Buffer)=>createHash('sha256').update(x).digest('hex');
let sequence=0;
function recordArtifacts(out:string,manifest:unknown){if(!process.env.C02_EVIDENCE_DIR)return;const e=process.env.C02_EVIDENCE_DIR;mkdirSync(e,{recursive:true});const id=String(++sequence).padStart(3,'0');writeFileSync(path.join(e,'artifact-'+id+'.json'),JSON.stringify({manifest,files:readdirSync(out).map(p=>({path:p,sha256:sha(readFileSync(path.join(out,p))),bytes:readFileSync(path.join(out,p)).length}))},null,2)+'\n');if(sequence<=2)writeFileSync(path.join(e,'artifact-'+id+'-operation.mjs'),readFileSync(path.join(out,'operation.mjs')));}
const child=`import {pathToFileURL} from 'node:url';const [modulePath,base64]=process.argv.slice(1);const {evaluate}=await import(pathToFileURL(modulePath));const input=new Uint8Array(Buffer.from(base64,'base64'));const before=Buffer.from(input).toString('hex');const result=evaluate(input);console.log(JSON.stringify({result:result.ok?{...result,wire:Array.from(result.wire),value:JSON.parse(new TextDecoder().decode(result.wire))}:result,unchanged:before===Buffer.from(input).toString('hex')}));`;
function evaluate(out:string,input:unknown,file='operation.mjs',raw?:Uint8Array){const r=spawnSync(process.execPath,['--input-type=module','-e',child,path.join(out,file),Buffer.from(raw??Buffer.from(JSON.stringify(input))).toString('base64')],{cwd:out,env:{PATH:process.env.PATH,HOME:process.env.HOME},encoding:'utf8',timeout:30000,maxBuffer:1048576});assert.equal(r.status,0,`${r.error??''}\n${r.stderr}\n${r.stdout}`);const result=JSON.parse(r.stdout);assert.equal(result.unchanged,true);return result.result;}
async function fixture(text=source,p=profile,b=bounds,accepted=true){const dir=mkdtempSync(path.join(tmpdir(),'craft-independent-C02-'));assert.equal(dir.startsWith(root),false);const sourcePath=path.join(dir,'business.alch'),profilePath=path.join(dir,'profile.json');mkdirSync(path.join(dir,'contracts'));writeFileSync(sourcePath,text);writeFileSync(profilePath,JSON.stringify(p));writeFileSync(path.join(dir,'contracts/bounds.json'),JSON.stringify(b));const owner=createGenericCompositionOwner();try{const handle=await owner.prepare({sourcePath,profilePath});let review:any;if(accepted){review=owner.review(handle,'independent-C02-oracle');owner.accept(handle,{decision_id:'C02-explicit-acceptance',owner:'independent-C02-oracle',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,'decision.json'));}return {dir,owner,handle,review,sourcePath,profilePath,cleanup:()=>rmSync(dir,{recursive:true,force:true})};}catch(e){rmSync(dir,{recursive:true,force:true});throw e;}}
async function generated(text=source,operation='ReviewDesk.ApproveRequest',fuel?:number){const p=structuredClone(profile),b=structuredClone(bounds);if(fuel!==undefined){p.limits.fuel=fuel;b.computation.limits.fuel=fuel;}const f=await fixture(text,p,b),out=path.join(f.dir,'generated');try{const manifest=await f.owner.generate(f.handle,{operation,outputDirectory:out});recordArtifacts(out,manifest);return {...f,out,manifest};}catch(e){f.cleanup();throw e;}}
const returned=(value:unknown)=>({tag:'Returned',fields:{value}}),rejected=(code:string)=>({tag:'Rejected',fields:{code}}),failed=(code:string)=>({tag:'Failed',fields:{code}});
function successful(r:any,value:unknown){assert.equal(r.ok,true);assert.deepEqual(r.value,value);assert.ok(Number.isSafeInteger(r.fuel_used));}
function code(e:any){return e?.diagnostics?.[0]?.code??e?.code;}
async function sourceReject(text:string,wanted:string|readonly string[]){assert.doesNotThrow(()=>parseCoreCommerceSyntax(text,'business.alch'));await assert.rejects(()=>fixture(text),(e:any)=>{assert.ok((Array.isArray(wanted)?wanted:[wanted]).includes(code(e)),String(e));return true;});}

test('C02 original Rule controls return of identical input or explicit rejection',async()=>{const f=await generated();try{for(const verified of [true,false]){const request={verified,flagged:!verified};successful(evaluate(f.out,{request}),verified?returned(request):rejected('unverified'));}assert.equal(readFileSync(path.join(f.out,'operation.mjs'),'utf8').includes(root),false);}finally{f.cleanup();}});

test('C02 independently renamed Laboratory domain composes the same generic Rule and Operation',async()=>{const f=await generated(laboratory,'Laboratory.PublishSample');try{for(const released of [false,true]){const sample={released,quarantined:!released};successful(evaluate(f.out,{sample}),released?returned(sample):rejected('unreleased'));}}finally{f.cleanup();}});

test('C02 changing the called Rule changes Operation behavior without changing the Operation',async()=>{const f=await generated(source.replace('expression request.verified','expression request.flagged'));try{const request={verified:true,flagged:false};successful(evaluate(f.out,{request}),rejected('unverified'));successful(evaluate(f.out,{request:{verified:false,flagged:true}}),returned({verified:false,flagged:true}));}finally{f.cleanup();}});

test('C02 malformed wire and argument records are typed failures distinct from rejection',async()=>{const f=await generated();try{for(const request of [{verified:'true',flagged:false},{verified:1,flagged:false},{verified:true},{verified:true,flagged:false,extra:true},null,[]]){const r=evaluate(f.out,{request});assert.equal(r.ok,false);assert.equal(r.error?.code,'InputType');}const malformed=evaluate(f.out,null,'operation.mjs',Buffer.from('{bad'));assert.equal(malformed.ok,false);assert.ok(malformed.error?.code);}finally{f.cleanup();}});

test('C02 nested conditional, fallthrough, rejection and declared failure preserve source order',async()=>{
 const text=source.slice(0,source.indexOf('\noperation '))+`\noperation ApproveRequest:
  input request Request
  output Request
  when request.flagged:
    when IsVerified(request):
      on true fail flagged-verified
    otherwise:
      on true reject flagged-unverified
  otherwise:
    on not IsVerified(request) reject unverified
  return request
`;
 const f=await generated(text);try{
  successful(evaluate(f.out,{request:{verified:true,flagged:true}}),failed('flagged-verified'));
  successful(evaluate(f.out,{request:{verified:false,flagged:true}}),rejected('flagged-unverified'));
  successful(evaluate(f.out,{request:{verified:false,flagged:false}}),rejected('unverified'));
  successful(evaluate(f.out,{request:{verified:true,flagged:false}}),returned({verified:true,flagged:false}));
 }finally{f.cleanup();}
});

test('C02 sequential Rule guards share one source fuel budget and reject lazily',async()=>{
 const twice=source.replace('  return request','  on not IsVerified(request) reject second-unverified\n  return request');
 const one=await generated(),two=await generated(twice);try{
  const input={request:{verified:true,flagged:false}},a=evaluate(one.out,input),b=evaluate(two.out,input);
  successful(a,returned(input.request));successful(b,returned(input.request));assert.ok(b.fuel_used>a.fuel_used,'second Rule call must consume the shared meter');
  const bounded=await generated(twice,'ReviewDesk.ApproveRequest',a.fuel_used);try{const r=evaluate(bounded.out,input);assert.equal(r.ok,false);assert.equal(r.error?.code,'ResourceLimit');assert.equal(r.fuel_used,a.fuel_used);}finally{bounded.cleanup();}
  const firstRejected=evaluate(one.out,{request:{verified:false,flagged:false}}),secondRejected=evaluate(two.out,{request:{verified:false,flagged:false}});
  successful(firstRejected,rejected('unverified'));successful(secondRejected,rejected('unverified'));assert.equal(secondRejected.fuel_used,firstRejected.fuel_used,'later guard must not execute after rejection');
 }finally{one.cleanup();two.cleanup();}
});

test('C02 low declared fuel produces evaluation failure rather than a business outcome',async()=>{const f=await generated(source,'ReviewDesk.ApproveRequest',1);try{const r=evaluate(f.out,{request:{verified:true,flagged:false}});assert.equal(r.ok,false);assert.equal(r.error?.code,'ResourceLimit');assert.equal(Object.hasOwn(r,'value'),false);}finally{f.cleanup();}});

test('C02 invalid return type, unknown Rule and missing result path reject at the original checker',async()=>{
 await sourceReject(source.replace('  return request','  return true'),'TypeMismatch');
 await sourceReject(source.replace('IsVerified(request)','MissingRule(request)'),'UnknownReference');
 await sourceReject(source.replace('  return request\n',''),'MissingMapping');
});

test('C02 rejects unselected unsupported let/call steps and does not acquire effect ports',async()=>{
 const rootPart=source.slice(0,source.indexOf('\noperation '));
 const body=`\noperation ApproveRequest:\n  input request Request\n  output Request\n  when false:\n    let checked = IsVerified(request)\n  otherwise:\n    on not IsVerified(request) reject unverified\n  return request\n`;
 await sourceReject(rootPart+body,'UnsupportedCapability');
 const called=rootPart+`\noperation Helper:\n  input request Request\n  output Request\n  return request\n\noperation ApproveRequest:\n  input request Request\n  output Request\n  when false:\n    call value Helper(request)\n  otherwise:\n    on not IsVerified(request) reject unverified\n  return request\n`;
 await sourceReject(called,'UnsupportedCapability');
});

test('C02 existing C01 profile cannot admit an Operation',async()=>{const p=JSON.parse(readFileSync(path.join(previous,'profile.json'),'utf8'));await assert.rejects(()=>fixture(source,p),(e:any)=>code(e)==='UnsupportedCapability');});

test('C02 copied, foreign and disposed public handles cannot authorize Operation emission',async()=>{const f=await fixture(),g=await fixture();try{for(const handle of [{...f.handle},new Proxy(f.handle,{}),g.handle])await assert.rejects(async()=>f.owner.generate(handle,{operation:'ReviewDesk.ApproveRequest',outputDirectory:path.join(f.dir,'bad')}));f.owner.dispose(f.handle);await assert.rejects(async()=>f.owner.generate(f.handle,{operation:'ReviewDesk.ApproveRequest',outputDirectory:path.join(f.dir,'disposed')}));assert.equal(existsSync(path.join(f.dir,'bad')),false);}finally{f.cleanup();g.cleanup();}});

for(const target of ['source','profile','decision']as const)test('C02 stale '+target+' blocks generation',async()=>{const f=await fixture();try{const file=target==='source'?f.sourcePath:target==='profile'?f.profilePath:path.join(f.dir,'decision.json');writeFileSync(file+'.replacement',readFileSync(file));renameSync(file+'.replacement',file);await assert.rejects(async()=>f.owner.generate(f.handle,{operation:'ReviewDesk.ApproveRequest',outputDirectory:path.join(f.dir,'stale')}));assert.equal(existsSync(path.join(f.dir,'stale')),false);}finally{f.cleanup();}});

test('C02 missing review acceptance blocks generation',async()=>{const f=await fixture(source,profile,bounds,false);try{await assert.rejects(async()=>f.owner.generate(f.handle,{operation:'ReviewDesk.ApproveRequest',outputDirectory:path.join(f.dir,'unaccepted')}));assert.equal(existsSync(path.join(f.dir,'unaccepted')),false);}finally{f.cleanup();}});

test('C02 CLI generates standalone Operation with explicit local acceptance',async()=>{const f=await fixture();try{const out=path.join(f.dir,'cli-generated'),entry=path.join(root,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-composition-cli.ts');const r=spawnSync(process.execPath,['--import','tsx',entry,'generate','--source',f.sourcePath,'--profile',f.profilePath,'--operation','ReviewDesk.ApproveRequest','--out',out,'--accept-local-review','C02-cli-oracle'],{cwd:cli,encoding:'utf8',timeout:60000,maxBuffer:1048576});assert.equal(r.status,0,`${r.stderr}\n${r.stdout}`);successful(evaluate(out,{request:{verified:true,flagged:false}}),returned({verified:true,flagged:false}));successful(evaluate(out,{request:{verified:false,flagged:true}}),rejected('unverified'));}finally{f.cleanup();}});

test('C02 compiler preserves C01 generated executable bytes on original source and profile',async()=>{const text=readFileSync(path.join(previous,'request.alch'),'utf8'),p=JSON.parse(readFileSync(path.join(previous,'profile.json'),'utf8')),b=JSON.parse(readFileSync(path.join(previous,'bounds.json'),'utf8'));const f=await fixture(text,p,b);try{const out=path.join(f.dir,'rule');await f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:out});const prior=readFileSync(path.join(base,'evidence/C01/test-005-artifacts/artifact-001-rule.mjs'));assert.equal(sha(readFileSync(path.join(out,'rule.mjs'))),sha(prior));assert.equal(evaluate(out,{request:{verified:true,flagged:false}},'rule.mjs').value,true);}finally{f.cleanup();}});

test('C02 lineage binds the authored Operation and called Rule without input mutation',async()=>{const f=await fixture();try{const before=[sha(readFileSync(f.sourcePath)),sha(readFileSync(f.profilePath))],out=path.join(f.dir,'generated'),manifest=await f.owner.generate(f.handle,{operation:'ReviewDesk.ApproveRequest',outputDirectory:out});recordArtifacts(out,manifest);assert.deepEqual([sha(readFileSync(f.sourcePath)),sha(readFileSync(f.profilePath))],before);const text=JSON.stringify(manifest);assert.match(text,/ReviewDesk\.ApproveRequest/);assert.match(text,/ReviewDesk\.IsVerified/);for(const h of before)assert.ok(text.includes(h));}finally{f.cleanup();}});


test('C02 original EffectPlan rejects every hidden future/unknown control node even on false branches',async()=>{
 const f=await fixture();try{
  const plan=f.owner.inspect(f.handle).operations.find((p:any)=>p.operation.name==='ApproveRequest');assert.ok(plan);assert.equal(plan.schema_version,'craft.commerce-effects/v1-candidate');
  const names=new Set(['ReviewDesk.IsVerified']);assert.doesNotThrow(()=>assertPureOperationPlan(plan,names));
  const condition={result:{kind:'scalar',name:'Bool'},local_records:[],expression:{op:'literal',type:{kind:'scalar',name:'Bool'},value:false}};
  for(const kind of ['read','count','call','transaction','read-set','acknowledge','preflight','present','case','write','emit','external-call','workflow','unknown-effect']){
   const candidate=structuredClone(plan);candidate.body=[{kind:'conditional',condition,then:[{kind}],otherwise:candidate.body}];
   assert.throws(()=>assertPureOperationPlan(candidate,names),(e:any)=>code(e)==='UnsupportedCapability',kind);
  }
 }finally{f.cleanup();}
});

test('C02 EffectPlan refuses native expressions, foreign calls, contexts and protocols without minting custody',async()=>{
 const f=await fixture();try{
  const plan=f.owner.inspect(f.handle).operations.find((p:any)=>p.operation.name==='ApproveRequest'),names=new Set(['ReviewDesk.IsVerified']);
  for(const expression of [{op:'native_observation',method:'fetch'},{op:'unknown_future_node'},{op:'call',declaration:'Foreign.Read',arguments:[]}]){
   const candidate=structuredClone(plan);candidate.body=[{kind:'action',action:{kind:'return',value:{result:candidate.result,local_records:[],expression}}}];
   assert.throws(()=>assertPureOperationPlan(candidate,names),(e:any)=>code(e)==='UnsupportedCapability');
  }
  for(const change of [(p:any)=>p.contexts.push({binding:'fake'}),(p:any)=>p.protocol={kind:'native-capture'}]){const candidate=structuredClone(plan);change(candidate);assert.throws(()=>assertPureOperationPlan(candidate,names),(e:any)=>code(e)==='UnsupportedCapability');}
  await assert.rejects(async()=>f.owner.generate(plan as any,{operation:'ReviewDesk.ApproveRequest',outputDirectory:path.join(f.dir,'forged-plan')}));
 }finally{f.cleanup();}
});


test('C02 exact selector contract rejects both, missing, nontext and unresolved selectors',async()=>{
 const f=await fixture();try{
  for(const selection of [{},{rule:'ReviewDesk.IsVerified',operation:'ReviewDesk.ApproveRequest'},{operation:23},{operation:''},{operation:'ReviewDesk.Missing'},{rule:'ReviewDesk.Missing'}]){
   const out=path.join(f.dir,'bad-selector');await assert.rejects(async()=>f.owner.generate(f.handle,{...selection,outputDirectory:out}as any));assert.equal(existsSync(out),false);
  }
 }finally{f.cleanup();}
});

test('C02 Rule selection under Operation profile identifies the actual Rule module and output',async()=>{
 const f=await fixture();try{
  const out=path.join(f.dir,'selected-rule'),manifest=await f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:out});
  assert.deepEqual(manifest.selected_recipe,{kind:'Rule',module:'rule.mjs',recipe_sha256:manifest.profile.recipe_sha256});
  assert.equal(manifest.rule,'ReviewDesk.IsVerified');assert.equal(Object.hasOwn(manifest,'operation'),false);assert.equal(existsSync(path.join(out,'operation.mjs')),false);assert.equal(evaluate(out,{request:{verified:true,flagged:false}},'rule.mjs').value,true);
 }finally{f.cleanup();}
});

test('C02 no-Rule Operation-only input gives typed MissingMapping',async()=>{
 const text='module NoRule version 1\nvalue-object Request:\n  verified Bool\noperation Approve:\n  input request Request\n  output Request\n  return request\n';
 await sourceReject(text,'MissingMapping');
});

test('C02 flat controls and compact branching cannot exceed safe lowering bounds',async()=>{
 const prefix=source.slice(0,source.indexOf('\noperation '));
 const long=prefix+'\noperation ApproveRequest:\n  input request Request\n  output Request\n'+'  on not IsVerified(request) reject unverified\n'.repeat(500)+'  return request\n';
 const p=structuredClone(profile),b=structuredClone(bounds);p.limits.max_ast_nodes=2147483647;p.limits.max_ast_depth=2147483647;b.computation.limits=structuredClone(p.limits);
 await assert.rejects(async()=>{const f=await fixture(long,p,b);try{await f.owner.generate(f.handle,{operation:'ReviewDesk.ApproveRequest',outputDirectory:path.join(f.dir,'too-deep')});}finally{f.cleanup();}},(e:any)=>!(e instanceof RangeError)&&code(e)==='ResourceLimit');
 const branch='  when request.flagged:\n    on not IsVerified(request) reject unverified\n  otherwise:\n    on not IsVerified(request) reject unverified\n';
 const compact=prefix+'\noperation ApproveRequest:\n  input request Request\n  output Request\n'+branch.repeat(12)+'  return request\n';
 await assert.rejects(async()=>{const f=await fixture(compact);try{await f.owner.generate(f.handle,{operation:'ReviewDesk.ApproveRequest',outputDirectory:path.join(f.dir,'too-many-nodes')});}finally{f.cleanup();}},(e:any)=>!(e instanceof RangeError)&&code(e)==='ResourceLimit');
});

test('C02 original domain factory enforces capability admission even when bypassing SDK',async()=>{
 const text=source+'\ncalculation HiddenFuture:\n  pure\n  input flag Bool\n  result Bool\n  expression flag\n';
 assert.doesNotThrow(()=>parseCoreCommerceSyntax(text,'business.alch'));
 const dir=mkdtempSync(path.join(tmpdir(),'C02-direct-owner-'));try{
  mkdirSync(path.join(dir,'source'));mkdirSync(path.join(dir,'contracts'));writeFileSync(path.join(dir,'source/business.alch'),text);writeFileSync(path.join(dir,'contracts/bounds.json'),JSON.stringify(bounds));
  writeFileSync(path.join(dir,'application.alch'),'module CraftGenerated.Root version 1\ninterface Application:\n  kind application-composition\n  source source/business.alch\n  computation-bounds contracts/bounds.json\n');
  const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(dir,'application.alch'),semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
  await assert.rejects(async()=>{const domain=await createOriginalPureOperationDomainOwner(sources,capture,semantics,semantic);domain.check({source_node:'ReviewDesk.ApproveRequest'}as any);},(e:any)=>code(e)==='UnsupportedCapability');
 }finally{rmSync(dir,{recursive:true,force:true});}
});
