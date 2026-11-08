/** Original source accounting, no invented runtime/task completion evidence.
 * Open Questions: docs/COMMERCE-OBLIGATIONS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync,mkdirSync,renameSync,copyFileSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceObligationOwner,assertCoreCommerceObligationOwner} from '../../src/commerce/commerce-core-obligation-owner.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
const source=`module Test version 1
value-object Item:
  verified Bool
  amount UInt64
rule Eligible:
  input item Item
  expression item.verified
calculation Amount:
  pure
  input item Item
  result UInt64
  expression item.amount
policy Choose:
  input item Item
  result UInt64
  ordered-cases:
    verified when item.verified -> Amount(item)
    otherwise -> Amount(item)
operation Apply:
  input item Item
  output Item
  requires Eligible(item)
  return item
interface Application:
  kind application-composition
  service test module Test
  formal-claims optional
`;
const fixture=(run:(root:string)=>void)=>{const root=mkdtempSync(path.join(tmpdir(),'commerce-obligation-owner-'));try{writeFileSync(path.join(root,'application.alch'),source);run(root);}finally{rmSync(root,{recursive:true,force:true});}};
const setup=(root:string)=>{const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(root),semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture),owner=createCoreCommerceObligationOwner(sources,semantics),handle=owner.prepare(capture,semantic);return {sources,capture,semantics,semantic,owner,handle,report:owner.inspect(handle)};};
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
test('exact original syntax correspondence includes Policy and never claims execution',()=>fixture(root=>{const f=setup(root);assertCoreCommerceObligationOwner(f.owner);assert.equal(f.report.counts.declarations,6);assert.equal(f.report.counts.optional_claims,0);assert.ok(f.report.source_checks.some(r=>r.declaration==='Test.Choose'&&r.kind==='expression'));assert.equal(f.report.source_checks.length,f.sources.inspect(f.capture).reconstruction.obligations.length);assert.ok(f.report.source_checks.every(r=>r.status==='source-statically-checked'&&r.runtime_qualified===false));assert.equal(f.report.runtime_qualified,false);assert.match(f.report.qualification,/no-runtime-formal-proof-or-task-completion/);assert.ok(f.report.implementation_requirements.every(r=>r.status==='required-not-witnessed-by-source-accounting'));assert.ok(Object.isFrozen(f.report.source_checks));f.owner.assertProposal(f.handle,JSON.parse(JSON.stringify(f.report)));}));
test('matching display JSON cannot restore original handles or factory ownership',()=>fixture(root=>{const f=setup(root);for(const fake of [{...f.handle},Object.create(f.handle),new Proxy(f.handle,{}),JSON.parse(JSON.stringify(f.handle))])failure(()=>f.owner.inspect(fake),'ForeignOwner');failure(()=>f.owner.inspect(f.report as any),'ForeignOwner');failure(()=>assertCoreCommerceObligationOwner({...f.owner}),'ForeignOwner');failure(()=>createCoreCommerceObligationOwner({...f.sources},f.semantics),'ForeignOwner');failure(()=>createCoreCommerceObligationOwner(f.sources,{...f.semantics}),'ForeignOwner');}));
test('same-byte separately captured source and semantic handles cannot be mixed',()=>fixture(root=>{const f=setup(root),other=f.sources.prepare(root);failure(()=>f.owner.prepare(other,f.semantic),'ForeignOwner');const second=createCoreCommerceObligationOwner(f.sources,f.semantics);failure(()=>second.inspect(f.handle),'ForeignOwner');}));
for(const [name,mutate]of [
 ['missing source row',(p:any)=>p.source_checks.pop()],
 ['duplicate source row',(p:any)=>p.source_checks.push(p.source_checks[0])],
 ['changed source span',(p:any)=>p.source_checks[0].span.start++],
 ['wrong declaration',(p:any)=>p.source_checks[0].declaration='Other.Item'],
 ['changed service ownership',(p:any)=>p.ownership[0].service='other'],
 ['runtime status strengthening',(p:any)=>p.source_checks[0].runtime_qualified=true],
 ['missing implementation requirement',(p:any)=>p.implementation_requirements.pop()],
 ['invented runtime witness',(p:any)=>p.implementation_requirements[0].status='passed'],
 ['stale source identity',(p:any)=>p.source_capture_sha256='0'.repeat(64)],
]as const)test('proposal refuses '+name,()=>fixture(root=>{const f=setup(root),p=JSON.parse(JSON.stringify(f.report));mutate(p);failure(()=>f.owner.assertProposal(f.handle,p),'InvalidContract');}));
test('proposal accessors and proxies cannot execute while inspecting inert display data',()=>fixture(root=>{const f=setup(root);let invoked=false;const p={get counts(){invoked=true;return f.report.counts;}};assert.throws(()=>f.owner.assertProposal(f.handle,p));assert.equal(invoked,false);assert.throws(()=>f.owner.assertProposal(f.handle,new Proxy(f.report,{ownKeys(){invoked=true;throw Error('trap');}})));assert.equal(invoked,false);}));
for(const mode of ['source-byte','source-same-byte','semantic-dispose','source-dispose','obligation-dispose']as const)test('original obligation currentness rejects '+mode,()=>fixture(root=>{const f=setup(root);switch(mode){case'source-byte':writeFileSync(path.join(root,'application.alch'),source+'# changed\n');break;case'source-same-byte':writeFileSync(path.join(root,'replacement'),source);renameSync(path.join(root,'replacement'),path.join(root,'application.alch'));break;case'semantic-dispose':f.semantics.dispose(f.semantic);break;case'source-dispose':f.sources.dispose(f.capture);break;case'obligation-dispose':f.owner.dispose(f.handle);}failure(()=>f.owner.inspect(f.handle),mode.startsWith('source-')&&!mode.endsWith('dispose')?'StaleOwner':'DisposedOwner');}));
test('optional claims do not create executable source obligations',()=>fixture(root=>{const f=setup(root);mkdirSync(path.join(root,'claims'));writeFileSync(path.join(root,'claims/item.smt2'),'(set-logic ALL)\n');writeFileSync(path.join(root,'application.alch'),source+'formal-claim CheckedItem:\n  language smtlib2\n  source claims/item.smt2\n  targets Item\n');const next=setup(root);assert.equal(next.report.counts.optional_claims,1);assert.equal(next.report.counts.source_obligations,f.report.counts.source_obligations);assert.equal(next.report.executable_sha256,f.report.executable_sha256);assert.notEqual(next.report.assurance_sha256,f.report.assurance_sha256);assert.ok(!next.report.source_checks.some(r=>r.declaration==='Test.CheckedItem'));}));
test('scalar refinements have their own genuine value-source correspondence',()=>fixture(root=>{writeFileSync(path.join(root,'application.alch'),source+'value-object Identifier:\n  carrier String\n  utf8-bytes 1..8\n  unicode-scalars 1..8\n  pattern "^[a-z]{1,8}$"\n');const f=setup(root);assert.equal(f.report.counts.declarations,7);assert.ok(f.report.source_checks.some(r=>r.declaration==='Test.Identifier'&&r.checker==='value-source'));}));
for(const mode of ['bytes','same-bytes-replacement']as const)test('loaded obligation owner code pin rejects '+mode,()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-obligation-code-')),cli=fileURLToPath(new URL('../../',import.meta.url));try{
  mkdirSync(path.join(root,'src/commerce'),{recursive:true});mkdirSync(path.join(root,'src/profile-engine'));mkdirSync(path.join(root,'src/generic'));mkdirSync(path.join(root,'contracts'));mkdirSync(path.join(root,'business'));
  for(const name of readdirSync(path.join(cli,'src/commerce')))if(name.startsWith('commerce-core-')&&name.endsWith('.ts')||['commerce-data-v1.ts','commerce-registry-v1.ts'].includes(name))copyFileSync(path.join(cli,'src/commerce',name),path.join(root,'src/commerce',name));
  copyFileSync(path.join(cli,'src/profile-engine/contracts.ts'),path.join(root,'src/profile-engine/contracts.ts'));for(const name of ['assurance-source','profile-resolver','composition-capabilities'])copyFileSync(path.join(cli,'src/generic',name+'.ts'),path.join(root,'src/generic',name+'.ts'));for(const name of readdirSync(path.join(cli,'contracts')))if(name.endsWith('.json'))copyFileSync(path.join(cli,'contracts',name),path.join(root,'contracts',name));writeFileSync(path.join(root,'package.json'),'{"type":"module"}');writeFileSync(path.join(root,'business/application.alch'),source);
  const code=`import assert from 'node:assert/strict';import {readFileSync,writeFileSync,renameSync} from 'node:fs';import {pathToFileURL} from 'node:url';const root=process.argv[1],mode=process.argv[2];const load=n=>import(pathToFileURL(root+'/src/commerce/commerce-core-'+n+'.ts'));const {createCoreCommerceSourceOwner}=await load('source-owner'),{createCoreCommerceSemanticOwner}=await load('semantic-owner'),{createCoreCommerceObligationOwner}=await load('obligation-owner');const s=createCoreCommerceSourceOwner(),h=s.prepare(root+'/business'),m=createCoreCommerceSemanticOwner(s),v=m.check(h),o=createCoreCommerceObligationOwner(s,m),p=o.prepare(h,v),file=root+'/src/commerce/commerce-core-obligation-owner.ts',bytes=readFileSync(file);if(mode==='bytes')writeFileSync(file,Buffer.concat([bytes,Buffer.from(String.fromCharCode(10)+'//changed'+String.fromCharCode(10))]));else{writeFileSync(file+'.replacement',bytes);renameSync(file+'.replacement',file);}for(const f of [()=>o.assertCurrent(p),()=>createCoreCommerceObligationOwner(s,m)])assert.throws(f,e=>e.diagnostics?.[0]?.code==='StaleOwner');console.log('obligation-code-pin-passed');`;
  const result=spawnSync(process.execPath,['--import','tsx','--input-type=module','-e',code,root,mode],{cwd:cli,encoding:'utf8',maxBuffer:2097152});assert.equal(result.status,0,result.stderr);assert.match(result.stdout,/obligation-code-pin-passed/);
 }finally{rmSync(root,{recursive:true,force:true});}
});
test('actual ecommerce accounts for all2526 source obligations and204 declaration owners',()=>{const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)),f=setup(root);assert.deepEqual(f.report.counts,{declarations:204,optional_claims:0,source_obligations:2526,implementation_requirements:f.report.implementation_requirements.length});assert.equal(f.report.ownership.length,204);assert.equal(f.report.services.length,5);assert.equal(f.report.source_checks.filter(r=>r.kind==='interface-clause').length,104);assert.equal(f.semantics.inspect(f.semantic).interfaces.length,18);assert.equal(new Set(f.report.source_checks.map(r=>r.id)).size,2526);const surfaces=new Set(f.sources.inspect(f.capture).reconstruction.modules.flatMap(m=>m.declarations.map(d=>d.surface)));assert.equal(surfaces.size,13);assert.equal(surfaces.has('Policy'),false);assert.ok(f.report.ownership.some(o=>o.service===null&&o.category==='technical'));f.owner.assertCurrent(f.handle);});
