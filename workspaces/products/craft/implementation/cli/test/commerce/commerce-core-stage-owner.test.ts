/** Shared source API, original-parent/currentness and source-bound data checks.
 * Open Questions: docs/COMMERCE-STAGE-API.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync,renameSync,mkdirSync,readFileSync,copyFileSync,readdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner,createCoreCommerceSemanticStageComponent,assertCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCoreCommerceReadContracts,createCoreCommerceEffectContracts} from '../../src/commerce/commerce-core-role-contracts.js';
import {coreCommerceValueSchema} from '../../src/commerce/commerce-core-stage-data.js';
import {checkCoreCommercePureSources} from '../../src/commerce/commerce-core-pure.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import type {CommerceSemanticComponent,CommerceSourceOwner,CommerceResult} from '../../src/commerce/commerce-stages-v1.js';
const source=`module Demo version 1
value-object Identifier:
  carrier String
  utf8-bytes 1..16
entity Counter:
  id UInt64
  amount UInt64
  identity id
calculation Amount:
  pure
  input value UInt64
  result UInt64
  expression value + 1
interface Service:
  kind trusted-context
  abi craft.test-service/v1-candidate
  custody private-registered-service-entry-owner
  fields context.json#/context/properties
  serializable false
  public-constructor forbidden
interface Auth:
  kind native-auth-owner
  abi craft.test-auth/v1-candidate
  admission auth-foundation-authorization-admission-service
  decision auth-foundation-authorization-ready-decision.authorize
  binding config/auth.json
  on-unresolved reject NativeImplementationUnavailable
query Read:
  input id UInt64
  source row Counter
  output optional<UInt64>
  where row.id == id
  project row.amount
  on-missing return none
operation Echo:
  input value UInt64
  context service Service
  output UInt64
  requires value > 0
  return value
interface Internal:
  kind internal
  exposes Read, Echo
entry Demo.EchoEntry:
  invokes Demo.Echo
  interaction request-response
  access:
    authenticated service
    permission demo.echo
    auth-resource demo
    auth-action echo
    auth-scope test
    auth-route test:Demo.EchoEntry
    caller demo
    context Service
    native-requires craft.context.current-owner/v1-candidate
    current-action before replay-and-effects
interface Application:
  kind application-composition
  source models/technical.alch
  service demo module Demo
  implementation Tech.Select
  parameters selection.json#/parameters
  computation-bounds config/bounds.json
  required-output code
  required-output api-contracts
  required-output business-graph
  required-output system-graph
  required-output business-system-bridge
  formal-claims optional
`;
const technical=`module Tech version 1
value-object Options:
  count UInt64
mapping Select:
  input options Options
  target Options
  total true
  field count <- options.count
interface Family:
  kind technical-profile-family
  family-contract config/family.json
  obligations config/family.json
  input checked technical Craft model with original owner
  output derived candidate package with actual resolved native basis
  callbacks forbidden
  unknown-primitive reject
  missing-producer reject
`;
const parameters={tablePrefix:'test_',requestBytes:4096,responseBytes:131072,bodyTimeoutMs:2000},limits={max_input_bytes:1048576,max_output_bytes:524288,max_value_bytes:524288,max_items:100,max_iterations:100,max_ast_nodes:4096,max_ast_depth:32,max_call_depth:32,fuel:100000};
const context={source_module:'Demo@1',context:{abi:'craft.test-service/v1-candidate',properties:{serviceId:'Identifier'}}},auth={abi:'craft.test-auth/v1-candidate',source_module:'Demo@1',policy_template_mapping:{entry_route:'test:logicalEntryId'}},bounds={schema_version:'craft.commerce-compute-bounds/v1-candidate',computation:{required_schema_version:'domainspec.iteration-expression/v2-candidate',required_semantics_revision:'ordered-metered-commerce-v2-candidate',limits}};
const texts=[{path:'application.alch',text:source},{path:'models/technical.alch',text:technical}],assets=[{path:'context.json',text:JSON.stringify(context)},{path:'config/auth.json',text:JSON.stringify(auth)},{path:'config/bounds.json',text:JSON.stringify(bounds)},{path:'config/family.json',text:'{}'},{path:'selection.json',text:JSON.stringify({parameters})}];
async function fixture(run:(f:Awaited<ReturnType<typeof setup>>,root:string)=>Promise<void>|void){const root=mkdtempSync(path.join(tmpdir(),'commerce-stage-'));try{for(const item of [...texts,...assets]){mkdirSync(path.dirname(path.join(root,item.path)),{recursive:true});writeFileSync(path.join(root,item.path),item.text);}await run(await setup(root),root);}finally{rmSync(root,{recursive:true,force:true});}}
async function setup(root:string){const sources=createCoreCommerceSourceOwner(),semantics=createCoreCommerceSemanticOwner(sources),owner=createCoreCommerceStageSourceOwner(sources,semantics),shared:CommerceSourceOwner=owner,source=await shared.prepare(root,'application.alch'),component:CommerceSemanticComponent=createCoreCommerceSemanticStageComponent(owner,source);return {sources,semantics,owner,source,component,inspection:shared.inspect(source),modules:owner.moduleContracts(source)};}
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
const rejects=(r:CommerceResult<unknown>,code?:string)=>{assert.equal(r.ok,false);if(!r.ok&&code)assert.equal(r.diagnostics[0]!.code,code);};
test('shared source contract retains actual source identities and no selected native/output custody',()=>fixture(f=>{assertCoreCommerceStageSourceOwner(f.owner);assert.equal(f.inspection.modules.length,2);assert.equal(f.inspection.application.profile_source.module,'Tech');assert.equal(f.inspection.application.profile_mapping,'Tech.Select');assert.equal(Object.getPrototypeOf(f.inspection.application.parameters),null);assert.deepEqual({...f.inspection.application.parameters},parameters);assert.equal(f.inspection.native_basis_sha256,null);assert.equal(f.inspection.profile_sha256,null);assert.equal(f.inspection.output_sha256,null);assert.ok(Object.isFrozen(f.inspection.application));assert.equal(f.inspection.application.formal_claims_required,false);assert.deepEqual(f.inspection.application.entries,['Demo.EchoEntry']);f.owner.assertCurrent(f.source);}));
test('copied handles/owners/proxies/data cannot acquire original stage custody',()=>fixture(f=>{for(const fake of [{...f.source},JSON.parse(JSON.stringify(f.source)),Object.create(f.source),new Proxy(f.source,{})])failure(()=>f.owner.inspect(fake),'ForeignOwner');failure(()=>f.owner.inspect(f.inspection as any),'ForeignOwner');failure(()=>assertCoreCommerceStageSourceOwner({...f.owner}),'ForeignOwner');failure(()=>createCoreCommerceSemanticStageComponent({...f.owner},f.source),'ForeignOwner');failure(()=>createCoreCommerceStageSourceOwner({...f.sources},f.semantics),'ForeignOwner');}));
test('separate original stage factories cannot exchange matching handles',()=>fixture(async(f,root)=>{const other=await setup(root);failure(()=>other.owner.inspect(f.source),'ForeignOwner');failure(()=>createCoreCommerceSemanticStageComponent(other.owner,f.source),'ForeignOwner');}));
test('module component checks the complete exact closure and preserves data-only scope',()=>fixture(f=>{assert.equal(f.component.checkModule(f.modules[0]!,[...f.modules].reverse()).ok,true);rejects(f.component.checkModule(f.modules[0]!,f.modules.slice(0,1)),'InvalidContract');rejects(f.component.checkModule(f.modules[0]!,[...f.modules,f.modules[0]!]),'InvalidContract');const m=JSON.parse(JSON.stringify(f.modules[0]));m.declarations.pop();rejects(f.component.checkModule(m,f.modules),'InvalidContract');assert.equal(f.component.checkModule(f.inspection as any,f.modules).ok,false);}));
for(const [name,edit]of [
 ['identity',(m:any)=>m.source.artifact.sha256='0'.repeat(64)],
 ['span',(m:any)=>m.declarations[0].span.start++],
 ['permission',(m:any)=>m.entries[0].access.permission='demo.admin'],
 ['claim requirement',(m:any)=>m.formal_claims_required=true],
 ['invented source owner',(m:any)=>m.source_owner={kind:'accepted'}],
]as const)test('module comparison rejects changed '+name,()=>fixture(f=>{const m=JSON.parse(JSON.stringify(f.modules[0]));edit(m);rejects(f.component.checkModule(m,f.modules),'InvalidContract');}));
test('computation component accepts only the exact source formula and captured bounds',()=>fixture(f=>{const contract=createCoreCommerceComputationContract(texts,'Demo.Amount',limits);assert.equal(f.component.checkComputation(contract).ok,true);const changed=JSON.parse(JSON.stringify(contract));changed.limits.fuel++;rejects(f.component.checkComputation(changed),'InvalidContract');changed.limits.fuel--;changed.functions.find((d:any)=>d.name==='Demo.Amount').body.right.value='2';rejects(f.component.checkComputation(changed),'InvalidContract');}));
test('read/effect components bind both actual checked role and full source value schema',()=>fixture(f=>{const pure=checkCoreCommercePureSources(texts),read=createCoreCommerceReadContracts(texts,assets)[0]!,effect=createCoreCommerceEffectContracts(texts,assets)[0]!,rv=coreCommerceValueSchema(pure,read.output),ev=coreCommerceValueSchema(pure,effect.result);assert.equal(f.component.checkRead(read,rv).ok,true);assert.equal(f.component.checkEffects(effect,ev).ok,true);const changed=JSON.parse(JSON.stringify(rv));changed.records.find((r:any)=>r.name==='Demo.Counter').fields.amount={kind:'scalar',name:'Bool'};rejects(f.component.checkRead(read,changed),'InvalidContract');const effects=JSON.parse(JSON.stringify(effect));effects.body.shift();rejects(f.component.checkEffects(effects,ev),'InvalidContract');const reads=JSON.parse(JSON.stringify(read));reads.predicate.expression={op:'literal',type:{kind:'scalar',name:'Bool'},value:true};rejects(f.component.checkRead(reads,rv),'InvalidContract');}));
for(const mode of ['bytes','same-bytes','asset','dispose']as const)test('stage and bound component reject '+mode+' after capture',()=>fixture((f,root)=>{if(mode==='bytes')writeFileSync(path.join(root,'application.alch'),source+'# changed\n');if(mode==='same-bytes'){writeFileSync(path.join(root,'replacement'),source);renameSync(path.join(root,'replacement'),path.join(root,'application.alch'));}if(mode==='asset')writeFileSync(path.join(root,'selection.json'),JSON.stringify({parameters:{...parameters,tablePrefix:'other_'}}));if(mode==='dispose')f.owner.dispose(f.source);failure(()=>f.owner.inspect(f.source),mode==='dispose'?'DisposedOwner':'StaleOwner');rejects(f.component.checkModule(f.modules[0]!,f.modules),mode==='dispose'?'DisposedOwner':'StaleOwner');}));
test('inert component validation refuses getters and proxies without executing them',()=>fixture(f=>{let called=false;const input={get source(){called=true;return f.modules[0]!.source;}};rejects(f.component.checkModule(input as any,f.modules),'InvalidContract');rejects(f.component.checkComputation(new Proxy({} as any,{ownKeys(){called=true;return [];}})),'InvalidContract');assert.equal(called,false);}));
test('invalid source-stage application is rejected rather than filled with a fictitious profile',()=>fixture(async(f,root)=>{writeFileSync(path.join(root,'application.alch'),source.replace('  implementation Tech.Select\n',''));await assert.rejects(()=>f.owner.prepare(root,'application.alch'),(e:any)=>e.diagnostics?.[0]?.code==='MissingMapping');}));
test('optional claims keep captured language/file/targets without gating source execution',()=>fixture(async(f,root)=>{mkdirSync(path.join(root,'claims'));writeFileSync(path.join(root,'claims/amount.smt2'),'(set-logic ALL)\n');writeFileSync(path.join(root,'application.alch'),source+'formal-claim AmountClaim:\n  language smtlib2\n  source claims/amount.smt2\n  targets Amount\n');const next=await setup(root);const claim=next.modules[0]!.formal_claims[0]!;assert.equal(claim.language,'smtlib2');assert.equal(claim.source.path,'claims/amount.smt2');assert.deepEqual(claim.targets,[{module:'Demo',role:'Calculation',name:'Amount'}]);assert.equal(next.component.checkModule(next.modules[0]!,next.modules).ok,true);assert.equal(next.inspection.application.formal_claims_required,false);}));
for(const [name,edit]of [
 ['open parameter keys',(p:any)=>p.extra='unbounded'],
 ['unsupported request bytes',(p:any)=>p.requestBytes=8192],
 ['unvalidated SQL prefix',(p:any)=>p.tablePrefix='x;drop_table'],
]as const)test('stage projection rejects '+name,()=>fixture(async(f,root)=>{const p={...parameters};edit(p);writeFileSync(path.join(root,'selection.json'),JSON.stringify({parameters:p}));await assert.rejects(()=>f.owner.prepare(root,'application.alch'),(e:any)=>e.diagnostics?.[0]?.code==='InvalidContract');}));
test('actual ecommerce stage adapter retains all14modules and22 entries;Workflow data cannot erase permissions or recovery',async()=>{const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)),f=await setup(root),rows=JSON.parse(readFileSync(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/role-producer-contracts-final-11.json',import.meta.url),'utf8'));assert.equal(f.modules.length,14);assert.equal(f.inspection.application.entries.length,22);assert.equal(f.inspection.application.services.length,5);assert.equal(f.component.checkWorkflow(rows.workflows[0],rows.entries).ok,true);const changed=JSON.parse(JSON.stringify(rows.workflows[0]));changed.defaults.call_failure='continue';rejects(f.component.checkWorkflow(changed,rows.entries),'InvalidContract');const entries=JSON.parse(JSON.stringify(rows.entries));entries[0].access.permission='admin';rejects(f.component.checkWorkflow(rows.workflows[0],entries),'InvalidContract');assert.equal(f.component.checkModule(f.modules[0]!,f.modules).ok,true);f.owner.dispose(f.source);});
for(const mode of ['bytes','same-byte-replacement']as const)test('source-stage code pin invalidates existing handles and a new factory after '+mode,async()=>{
 const root=mkdtempSync(path.join(tmpdir(),'commerce-stage-code-')),cli=fileURLToPath(new URL('../../',import.meta.url));try{
  for(const d of ['src/commerce','src/profile-engine','contracts','business'])mkdirSync(path.join(root,d),{recursive:true});
  for(const name of readdirSync(path.join(cli,'src/commerce')))if(name.startsWith('commerce-core-')&&name.endsWith('.ts')||['commerce-data-v1.ts','commerce-registry-v1.ts','commerce-stages-v1.ts'].includes(name))copyFileSync(path.join(cli,'src/commerce',name),path.join(root,'src/commerce',name));
  copyFileSync(path.join(cli,'src/profile-engine/contracts.ts'),path.join(root,'src/profile-engine/contracts.ts'));for(const name of readdirSync(path.join(cli,'contracts')))if(name.endsWith('.json'))copyFileSync(path.join(cli,'contracts',name),path.join(root,'contracts',name));writeFileSync(path.join(root,'package.json'),'{"type":"module"}');
  for(const item of [...texts,...assets]){const p=path.join(root,'business',item.path);mkdirSync(path.dirname(p),{recursive:true});writeFileSync(p,item.text);}
  const code=`import assert from 'node:assert/strict';import {readFileSync,writeFileSync,renameSync} from 'node:fs';import {pathToFileURL} from 'node:url';const root=process.argv[1],mode=process.argv[2],load=n=>import(pathToFileURL(root+'/src/commerce/commerce-core-'+n+'.ts'));const {createCoreCommerceSourceOwner}=await load('source-owner'),{createCoreCommerceSemanticOwner}=await load('semantic-owner'),{createCoreCommerceStageSourceOwner,createCoreCommerceSemanticStageComponent}=await load('stage-owner');const s=createCoreCommerceSourceOwner(),m=createCoreCommerceSemanticOwner(s),o=createCoreCommerceStageSourceOwner(s,m),h=await o.prepare(root+'/business','application.alch'),component=createCoreCommerceSemanticStageComponent(o,h),modules=o.moduleContracts(h),file=root+'/src/commerce/commerce-core-stage-data.ts',bytes=readFileSync(file);if(mode==='bytes')writeFileSync(file,Buffer.concat([bytes,Buffer.from(String.fromCharCode(10)+'//changed'+String.fromCharCode(10))]));else{writeFileSync(file+'.replacement',bytes);renameSync(file+'.replacement',file);}for(const run of [()=>o.assertCurrent(h),()=>createCoreCommerceStageSourceOwner(s,m)])assert.throws(run,e=>e.diagnostics?.[0]?.code==='StaleOwner');const r=component.checkModule(modules[0],modules);assert.equal(r.ok,false);assert.equal(r.diagnostics[0].code,'StaleOwner');console.log('stage-code-pin-passed');`;
  const result=spawnSync(process.execPath,['--import','tsx','--input-type=module','-e',code,root,mode],{cwd:cli,encoding:'utf8',maxBuffer:2097152});assert.equal(result.status,0,result.stderr);assert.match(result.stdout,/stage-code-pin-passed/);
 }finally{rmSync(root,{recursive:true,force:true});}
});
