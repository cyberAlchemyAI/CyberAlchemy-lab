/** Independent C01 cumulative oracle. No implementation result defines expectations.
 * Open Questions: r5/contracts/C01/oracle-v1.json. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync,existsSync,readdirSync,renameSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {parseCoreCommerceSyntax} from '../../src/commerce/commerce-core-syntax.js';

const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const cli=fileURLToPath(new URL('../../',import.meta.url));
const contracts=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C01');
const source=readFileSync(path.join(contracts,'request.alch'),'utf8');
const laboratory=readFileSync(path.join(contracts,'laboratory.alch'),'utf8');
const profile=JSON.parse(readFileSync(path.join(contracts,'profile.json'),'utf8'));
const bounds=readFileSync(path.join(contracts,'bounds.json'),'utf8');
const sha=(bytes:string|Buffer)=>createHash('sha256').update(bytes).digest('hex');
let artifactSequence=0;
function recordArtifacts(dir:string,manifest:unknown){if(!process.env.C01_EVIDENCE_DIR)return;const evidence=process.env.C01_EVIDENCE_DIR;mkdirSync(evidence,{recursive:true});const id=String(++artifactSequence).padStart(3,'0'),files=readdirSync(dir).filter(name=>name.endsWith('.mjs')||name.endsWith('.json')).map(name=>({path:name,sha256:sha(readFileSync(path.join(dir,name))),bytes:readFileSync(path.join(dir,name)).length}));writeFileSync(path.join(evidence,`artifact-${id}.json`),JSON.stringify({manifest,files},null,2)+'\n');if(artifactSequence<=2)writeFileSync(path.join(evidence,`artifact-${id}-rule.mjs`),readFileSync(path.join(dir,'rule.mjs')));}
const diagnostics=(e:any)=>JSON.stringify({message:e?.message,code:e?.code,diagnostics:e?.diagnostics});
const childCode=`import {readFileSync} from 'node:fs';import {pathToFileURL} from 'node:url';const [modulePath,wireBase64]=process.argv.slice(1);const {evaluate}=await import(pathToFileURL(modulePath).href);const bytes=new Uint8Array(Buffer.from(wireBase64,'base64'));const before=Buffer.from(bytes).toString('hex');const result=evaluate(bytes);const after=Buffer.from(bytes).toString('hex');console.log(JSON.stringify({result:result.ok?{...result,wire:Array.from(result.wire),value:JSON.parse(new TextDecoder().decode(result.wire))}:result,unchanged:before===after}));`;
function outsideEvaluate(dir:string,input:unknown,raw?:Uint8Array){
 const wire=raw??Buffer.from(JSON.stringify(input));
 const r=spawnSync(process.execPath,['--input-type=module','-e',childCode,path.join(dir,'rule.mjs'),Buffer.from(wire).toString('base64')],{cwd:dir,env:{PATH:process.env.PATH,HOME:process.env.HOME},encoding:'utf8',timeout:30000,maxBuffer:1024*1024});
 assert.equal(r.status,0,`${r.error??''}\n${r.stderr}\n${r.stdout}`);
 const parsed=JSON.parse(r.stdout);assert.equal(parsed.unchanged,true);return parsed.result;
}
async function fixture(text=source,selected:any=profile,selectedBounds=bounds,acceptReview=true){
 const dir=mkdtempSync(path.join(tmpdir(),'craft-independent-C01-'));
 assert.equal(dir.startsWith(root),false,'generated evaluation must be outside repository');
 const sourcePath=path.join(dir,'business.alch'),profilePath=path.join(dir,'profile.json');
 writeFileSync(sourcePath,text);writeFileSync(profilePath,JSON.stringify(selected));mkdirSync(path.join(dir,'contracts'));writeFileSync(path.join(dir,'contracts/bounds.json'),selectedBounds);mkdirSync(path.join(dir,'proofs'));writeFileSync(path.join(dir,'proofs/assertion.smt2'),'(assert true)\n(check-sat)\n');
 const owner=createGenericCompositionOwner();
 try{const handle=await owner.prepare({sourcePath,profilePath});let review:any;if(acceptReview){review=owner.review(handle,'independent-C01-oracle');owner.accept(handle,{decision_id:'test-C01-acceptance',owner:'independent-C01-oracle',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,'review-decision.json'));}return {dir,sourcePath,profilePath,owner,handle,review,cleanup:()=>rmSync(dir,{recursive:true,force:true})};}
 catch(e){rmSync(dir,{recursive:true,force:true});throw e;}
}
async function generated(text=source,rule='ReviewDesk.IsVerified'){
 const f=await fixture(text),out=path.join(f.dir,'generated');
 try{const manifest=await f.owner.generate(f.handle,{rule,outputDirectory:out});recordArtifacts(out,manifest);return {...f,out,manifest};}
 catch(e){f.cleanup();throw e;}
}
async function rejectSource(text:string,code:string){await assert.rejects(()=>fixture(text),(e:any)=>{assert.equal(e?.diagnostics?.[0]?.code??e?.code,code,diagnostics(e));return true;});}
async function rejectHandle(f:Awaited<ReturnType<typeof fixture>>,handle:any){
 assert.throws(()=>f.owner.inspect(handle));
 assert.throws(()=>f.owner.assertCurrent(handle));
 await assert.rejects(async()=>f.owner.generate(handle,{rule:'ReviewDesk.IsVerified',outputDirectory:path.join(f.dir,'forged')}));
 assert.equal(existsSync(path.join(f.dir,'forged')),false);
}

test('C01 source/profile generate true and false through portable emitted ESM with no claims',async()=>{
 assert.doesNotMatch(source,/claim/);const f=await generated();try{
  for(const verified of [true,false]){const r=outsideEvaluate(f.out,{request:{verified,flagged:!verified}});assert.equal(r.ok,true);assert.equal(r.value,verified);assert.equal(typeof r.value,'boolean');}
  const js=readFileSync(path.join(f.out,'rule.mjs'),'utf8');assert.ok(js.length>0);assert.equal(js.includes(root),false);assert.doesNotMatch(js,/from\s+['"](?:\.\.|\/home\/|\/tmp\/)/);
 }finally{f.cleanup();}
});

test('C01 renamed independent Laboratory domain shares exact compiler and profile',async()=>{
 const f=await generated(laboratory,'Laboratory.MayPublish');try{
  for(const released of [false,true]){const r=outsideEvaluate(f.out,{sample:{released,quarantined:!released}});assert.equal(r.ok,true);assert.equal(r.value,released);}
 }finally{f.cleanup();}
});

test('C01 selected field is authored behavior, not verified/domain-name inference',async()=>{
 const f=await generated(source.replace('expression request.verified','expression request.flagged'));try{
  assert.equal(outsideEvaluate(f.out,{request:{verified:true,flagged:false}}).value,false);
  assert.equal(outsideEvaluate(f.out,{request:{verified:false,flagged:true}}).value,true);
 }finally{f.cleanup();}
});

for(const [name,input]of Object.entries({string:{request:{verified:'true',flagged:false}},number:{request:{verified:1,flagged:false}},null:{request:null},missing:{request:{flagged:false}},extra:{request:{verified:true,flagged:false,extra:true}},array:{request:[true,false]},wrong_argument:{other:{verified:true,flagged:false}}}))
 test('C01 malformed input '+name+' is failure distinct from false',async()=>{const f=await generated();try{const r=outsideEvaluate(f.out,input);assert.equal(r.ok,false);assert.ok(r.error?.code,'typed failures need explicit error code');assert.equal(Object.hasOwn(r,'value'),false);}finally{f.cleanup();}});

test('C01 malformed JSON bytes fail without returning false',async()=>{const f=await generated();try{const r=outsideEvaluate(f.out,null,Buffer.from('{bad'));assert.equal(r.ok,false);assert.ok(r.error?.code);}finally{f.cleanup();}});

test('C01 undeclared field is rejected during generation admission',async()=>{await rejectSource(source.replace('expression request.verified','expression request.unknown'),'UnknownReference');});

test('C01 nonboolean Rule condition cannot be admitted',async()=>{await rejectSource(source.replace('expression request.verified','expression 1'),'TypeMismatch');});

test('C01 forged, copied, proxied and foreign handles cannot authorize inspect or emission',async()=>{
 const f=await fixture(),other=await fixture();try{
  for(const h of [{}, {...f.handle},Object.create(f.handle),JSON.parse(JSON.stringify(f.handle)),new Proxy(f.handle,{}),other.handle])await rejectHandle(f,h);
 }finally{f.cleanup();other.cleanup();}
});

test('C01 disposed genuine handle cannot authorize emission',async()=>{const f=await fixture();try{f.owner.dispose(f.handle);await rejectHandle(f,f.handle);}finally{f.cleanup();}});

for(const changed of ['source','profile','bounds','same-byte-source-replacement','same-byte-profile-replacement','same-byte-bounds-replacement']as const)
 test('C01 stale '+changed+' invalidates genuine custody before output',async()=>{
  const f=await fixture();try{
   if(changed==='source')writeFileSync(f.sourcePath,source.replace('request.verified','request.flagged'));
   else if(changed==='profile')writeFileSync(f.profilePath,JSON.stringify({...profile,id:'altered'}));
   else if(changed==='bounds'){const b=JSON.parse(bounds);b.computation.limits.fuel++;writeFileSync(path.join(f.dir,'contracts/bounds.json'),JSON.stringify(b));}
   else{const file=changed==='same-byte-profile-replacement'?f.profilePath:changed==='same-byte-bounds-replacement'?path.join(f.dir,'contracts/bounds.json'):f.sourcePath;writeFileSync(file+'.replacement',readFileSync(file));renameSync(file+'.replacement',file);}
   await rejectHandle(f,f.handle);
  }finally{f.cleanup();}
 });

for(const [name,extra]of [
 ['Operation','\noperation Approve:\n  input request Request\n  output Request\n  return request\n'],
 ['Calculation','\ncalculation Hidden:\n  pure\n  input flag Bool\n  result Bool\n  expression flag\n'],
 ['ValueObject invariant',''],
 ['supplied claim','\nformal-claim ApprovalClaim:\n  language smtlib2\n  source proofs/assertion.smt2\n  targets IsVerified\n'],
]as const)test('C01 explicitly rejects unsupported '+name+' before successful output',async()=>{
 const text=name==='ValueObject invariant'?source.replace('  flagged Bool','  flagged Bool\n  invariant verified'):source+extra;
 assert.doesNotThrow(()=>parseCoreCommerceSyntax(text,'business.alch'),'negative witness must be valid existing source syntax');
 await rejectSource(text,'UnsupportedCapability');
});

for(const [name,edit]of [
 ['unknown target',(p:any)=>p.target='handwritten-callback'],
 ['invented capability',(p:any)=>p.capabilities.push('UnknownFutureCapability')],
 ['unknown recipe',(p:any)=>p.recipe='caller-evaluator'],
 ['zero fuel',(p:any)=>p.limits.fuel=0],
 ['different positive fuel',(p:any)=>p.limits.fuel++],
 ['missing limits',(p:any)=>delete p.limits],
 ['schema replacement',(p:any)=>p.schema_version='profile/anything'],
]as const)test('C01 rejects profile '+name,async()=>{const p=structuredClone(profile);edit(p);await assert.rejects(()=>fixture(source,p));});

test('C01 generation preserves source/profile bytes and records genuine source/profile lineage',async()=>{
 const f=await fixture();try{
  const before=[sha(readFileSync(f.sourcePath)),sha(readFileSync(f.profilePath))];
  const inspected=f.owner.inspect(f.handle),out=path.join(f.dir,'generated');
  const manifest=await f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:out});
  assert.deepEqual([sha(readFileSync(f.sourcePath)),sha(readFileSync(f.profilePath))],before);
  const evidence=JSON.stringify({inspected,manifest});
  for(const hash of before)assert.ok(evidence.includes(hash),'identity missing from checked/emission evidence: '+hash);
  assert.match(evidence,/ReviewDesk/);assert.match(evidence,/IsVerified/);assert.match(evidence,/node-pure/);
 }finally{f.cleanup();}
});

test('C01 source CLI consumes .alch and profile files and emits independently runnable result',async()=>{
 const f=await fixture();try{
  const out=path.join(f.dir,'cli-generated'),entry=path.join(root,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/generic-composition-cli.ts');
  const r=spawnSync(process.execPath,['--import','tsx',entry,'generate','--source',f.sourcePath,'--profile',f.profilePath,'--rule','ReviewDesk.IsVerified','--out',out,'--accept-local-review','independent-C01-oracle'],{cwd:cli,encoding:'utf8',timeout:60000,maxBuffer:1024*1024});
  assert.equal(r.status,0,`${r.error??''}\n${r.stderr}\n${r.stdout}`);
  assert.equal(outsideEvaluate(out,{request:{verified:true,flagged:false}}).value,true);
  assert.equal(outsideEvaluate(out,{request:{verified:false,flagged:true}}).value,false);
 }finally{f.cleanup();}
});

test('C01 missing Rule reference and occupied output directory reject without partial overwrite',async()=>{
 const f=await generated();try{
  const before=sha(readFileSync(path.join(f.out,'rule.mjs')));
  await assert.rejects(async()=>f.owner.generate(f.handle,{rule:'ReviewDesk.Missing',outputDirectory:path.join(f.dir,'bad-rule')}));
  assert.equal(existsSync(path.join(f.dir,'bad-rule')),false);
  await assert.rejects(async()=>f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:f.out}));
  assert.equal(sha(readFileSync(path.join(f.out,'rule.mjs'))),before);
 }finally{f.cleanup();}
});


test('C01 source-declared admitted low fuel reports ResourceLimit distinctly from false',async()=>{
 const p=structuredClone(profile);p.limits.fuel=1;
 const b=JSON.parse(bounds);b.computation.limits.fuel=1;
 const f=await fixture(source,p,JSON.stringify(b));try{
  const out=path.join(f.dir,'generated');await f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:out});
  const result=outsideEvaluate(out,{request:{verified:false,flagged:true}});
  assert.equal(result.ok,false);assert.equal(result.error?.code,'ResourceLimit');
 }finally{f.cleanup();}
});


test('C01 unaccepted and mismatched source review cannot authorize generation',async()=>{
 const f=await fixture(source,profile,bounds,false);try{
  await assert.rejects(async()=>f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:path.join(f.dir,'unaccepted')}));
  assert.equal(existsSync(path.join(f.dir,'unaccepted')),false);
  const review=f.owner.review(f.handle,'independent-C01-oracle');
  assert.match(review.review_sha256,/^[a-f0-9]{64}$/);
  assert.throws(()=>f.owner.accept(f.handle,{decision_id:'test-invalid',owner:'independent-C01-oracle',outcome:'accepted',reviewed_digest:'0'.repeat(64)},path.join(f.dir,'invalid-decision.json')));
  await assert.rejects(async()=>f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:path.join(f.dir,'still-unaccepted')}));
 }finally{f.cleanup();}
});


test('C01 declining an earlier accepted review revokes generation custody',async()=>{
 const f=await fixture();try{
  const review=f.review;
  assert.throws(()=>f.owner.accept(f.handle,{decision_id:'test-declined',owner:'independent-C01-oracle',outcome:'declined',reviewed_digest:review.review_sha256},path.join(f.dir,'declined-decision.json')));
  await assert.rejects(async()=>f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:path.join(f.dir,'after-decline')}));
  assert.equal(existsSync(path.join(f.dir,'after-decline')),false);
 }finally{f.cleanup();}
});

test('C01 accepted decision file byte changes invalidate custody',async()=>{
 const f=await fixture();try{
  const decision=path.join(f.dir,'review-decision.json');writeFileSync(decision,readFileSync(decision,'utf8')+'\n');
  await assert.rejects(async()=>f.owner.generate(f.handle,{rule:'ReviewDesk.IsVerified',outputDirectory:path.join(f.dir,'after-decision-change')}));
  assert.equal(existsSync(path.join(f.dir,'after-decision-change')),false);
 }finally{f.cleanup();}
});

test('C01 generated helper Rule calls compose Boolean and/or/not over the same typed record',async()=>{
 const text=source+'\nrule CanPublish:\n  input request Request\n  expression IsVerified(request) and not request.flagged or false\n';
 const f=await generated(text,'ReviewDesk.CanPublish');try{
  for(const verified of [false,true])for(const flagged of [false,true]){
   const result=outsideEvaluate(f.out,{request:{verified,flagged}});
   assert.equal(result.ok,true);assert.equal(result.value,verified&&!flagged);
  }
 }finally{f.cleanup();}
});

test('C01 generated scalar Bool arguments and equality preserve every truth-table row',async()=>{
 const text='module SignalLab version 1\nrule Agree:\n  input left Bool\n  input right Bool\n  expression left == right\n';
 const f=await generated(text,'SignalLab.Agree');try{
  for(const left of [false,true])for(const right of [false,true]){
   const result=outsideEvaluate(f.out,{left,right});
   assert.equal(result.ok,true);assert.equal(result.value,left===right);
  }
 }finally{f.cleanup();}
});

test('C01 recursive Rule calls reject before emission rather than consuming runtime stack',async()=>{
 const text=source.replace('expression request.verified','expression IsVerified(request)');
 assert.doesNotThrow(()=>parseCoreCommerceSyntax(text,'business.alch'));
 await rejectSource(text,'InvalidContract');
});
