/** Exact original-source formation and genuine Auth/Query capability contexts.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import test from 'node:test';import {DatabaseSync} from 'node:sqlite';import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';import {tmpdir} from 'node:os';import {fileURLToPath} from 'node:url';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.js';
import {createGenericCapabilityContextOwner,isGenericCapabilityScalarOperand} from '../../src/generic/capability-context.js';
import {createGenericCapabilityFormationOwner} from '../../src/generic/capability-owner.js';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.js';
import {dataDigest} from '../../src/profile-engine/contracts.js';import {coreSha256} from '../../src/commerce/commerce-core-syntax.js';
import {capabilityFixture} from './capability-fixtures.js';
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url)),frontend=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
const c07=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C07');
const err=(code:string)=>(error:any)=>(error?.diagnostics?.[0]?.code??error?.code)===code;
function files(mode:'pure'|'agent'|'search'='pure'){
 const dir=mkdtempSync(path.join(tmpdir(),'craft-capability-owner-'));mkdirSync(path.join(dir,'contracts'));
 const src=mode==='pure'?readFileSync(path.join(frontend,'examples/generic-capabilities/business.alch'),'utf8'):readFileSync(path.join(c07,'context-request.alch'),'utf8')+'\ninterface Model:\n  kind bounded-schema\n  exposes Request, Decision\n';
 const actualSource=src;
 writeFileSync(path.join(dir,'business.alch'),actualSource);writeFileSync(path.join(dir,'profile.json'),readFileSync(path.join(mode==='pure'?path.join(frontend,'examples/generic-capabilities'):c07,'profile.json')));writeFileSync(path.join(dir,'contracts/bounds.json'),readFileSync(path.join(mode==='pure'?path.join(frontend,'examples/generic-capabilities/contracts'):c07,'bounds.json')));
 const {selection,kernel}=capabilityFixture();selection.source_sha256=coreSha256(actualSource);selection.profile_sha256=coreSha256(readFileSync(path.join(dir,'profile.json')));
 if(mode!=='pure'){
  const contract=mode==='agent'?{kind:'agent-run/v1',operation:'agent.run',input_type:'ReviewDesk.Request',result_type:'ReviewDesk.Decision',required_capabilities:['readonly-tools'],loop_owner:'selected-harness',tools:[{name:'ReadOwn',entry:'ReviewDesk.ReadOwnedRequestEntry',query:'ReviewDesk.ReadOwnedRequest',argument_codec:{kind:'scalar',name:'UInt64'},result_codec:{kind:'optional',element:{kind:'record',name:'ReviewDesk.Request'}},effect:'read-only'}],checkpoint_version:'1'}:{kind:'search/v1',operation:'search.query',input_type:'ReviewDesk.Request',result_type:'ReviewDesk.Decision',required_capabilities:['bounded-search'],search:{technique:'keyword',collection:'ReviewDesk.OwnedRequest',top_k:2,max_candidates:10,filter_fields:['id'],filter_operators:['eq','in'],tenant_scope:'original-owner-required',source_access:'original-owner-required',embedding_space:null}};
  selection.bindings[0].interface='ReviewDesk.Model';selection.bindings[0].contract=contract;selection.bindings[0].bounds.max_tool_calls=mode==='agent'?6:0;
  selection.realizations[0].contract=contract.kind;selection.realizations[0].operations=[contract.operation];selection.realizations[0].capabilities=mode==='agent'?['readonly-tools','local-inspect']:['bounded-search'];selection.realizations[0].bounds.max_tool_calls=mode==='agent'?6:0;
  kernel.integration_bindings[0].logical_boundary_ref='ReviewDesk.Model';kernel.integration_bindings[0].contract_ref=contract.kind;kernel.failure_mappings[0].boundary_ref='ReviewDesk.Model';kernel.provider_profiles[0].capability_set=[contract.kind,...selection.realizations[0].capabilities];
 }
 selection.kernel.sha256=dataDigest(kernel);writeFileSync(path.join(dir,'kernel.json'),JSON.stringify(kernel));writeFileSync(path.join(dir,'selection.json'),JSON.stringify(selection));
 return {dir,selection,kernel,input:{sourcePath:path.join(dir,'business.alch'),profilePath:path.join(dir,'profile.json'),capabilitySelectionPath:path.join(dir,'selection.json')},close(){rmSync(dir,{recursive:true,force:true});}};
}
async function waitForLookup(runtime:any,baseline:number,pending:Promise<unknown>){
 let settled=false,failure:unknown;void pending.then(()=>{settled=true;},error=>{settled=true;failure=error;});const deadline=Date.now()+30000;
 while(runtime.inspect().lookup_attempts===baseline){if(settled)throw failure??new Error('tool settled before its expected lookup');if(Date.now()>=deadline)throw new Error('bounded wait for protected Query lookup expired');await new Promise<void>(resolve=>setImmediate(resolve));}
}
function accept(owner:any,h:any,dir:string){const review=owner.review(h,'capability-owner-test');owner.accept(h,{decision_id:'capability-test',owner:'capability-owner-test',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,'decision.json'));}
test('checked source capabilities retain exact formation identities and original handle currentness',async()=>{
 const f=files(),owner=createGenericCompositionOwner();try{
  const h=await owner.prepare(f.input),projection=owner.inspectCapabilities(h)!;assert.equal(projection.bindings[0]!.interface,'Example.Model');assert.equal(projection.authority_effect,'none');assert.match(projection.qualification,/formation-only/);
  assert.throws(()=>owner.inspectCapabilities({...h}),err('ForeignOwner'));assert.throws(()=>createGenericCapabilityFormationOwner({}as any,{}as any,{}as any,{}as any),err('ForeignOwner'));
  accept(owner,h,f.dir);const output=path.join(f.dir,'output'),manifest=owner.generate(h,{operation:'Example.Answer',outputDirectory:output}) as any;
  assert.equal(manifest.capability_bindings.selection_sha256,projection.selection_sha256);assert.ok(manifest.files.some((v:any)=>v.path==='capability-bindings.json'));
  const graph=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));assert.equal(graph.nodes.find((n:any)=>n.id==='capability:Example.Selection').contract_sha256,projection.bindings[0]!.contract_sha256);
  writeFileSync(path.join(f.dir,'kernel.json'),JSON.stringify(f.kernel)+'\n');assert.throws(()=>owner.assertCurrent(h),err('StaleOwner'));
 }finally{f.close();}
});
test('unexposed, forged and unsupported source capability contracts reject before generation',async()=>{
 for(const mutation of [(s:any)=>s.bindings[0].contract.result_type='Example.Absent',(s:any)=>s.source_sha256='f'.repeat(64),(s:any)=>s.bindings[0].interface='Example.Answer']){
  const f=files();try{mutation(f.selection);writeFileSync(path.join(f.dir,'selection.json'),JSON.stringify(f.selection));await assert.rejects(createGenericCompositionOwner().prepare(f.input));}finally{f.close();}
 }
});
test('agent tools execute the original protected Query with typed codecs, current grants and private bounded context',async()=>{
 const f=files('agent'),owner=createGenericCompositionOwner();let runtime:any,auth:any;try{
  const h=await owner.prepare(f.input);accept(owner,h,f.dir);
  auth=await createGenericAuthFixture(owner,h,{ownedDirectory:path.join(f.dir,'auth'),subjects:[{id:'fixture-reviewer-a',evidence:'private-evidence',session:'private-session'},{id:'fixture-reviewer-c',evidence:'other-evidence',session:'other-session'}],grants:['fixture-reviewer-a','fixture-reviewer-c'].flatMap(subject=>[{subject,entry:'ReviewDesk.ReadOwnedRequestEntry'},{subject,entry:'ReviewDesk.ApproveOwnedRequestEntry'}])});
  const setup=await prepareGenericFixtureRuntime(owner,h,{service:'ReviewDeskService',ownedDirectory:path.join(f.dir,'store'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;
  loadGenericFixture(setup.fixture,new Uint8Array(readFileSync(path.join(c07,'context-fixture-rows.json'))));
  const contexts=createGenericCapabilityContextOwner(owner,h,runtime),actor=auth.actor(runtime,'fixture-reviewer-a','ReviewDesk.ReadOwnedRequestEntry'),open=()=>contexts.open(actor,'ReviewDesk.ApproveOwnedRequestEntry','Example.Selection',{deadline_ms:Date.now()+29000,tool_names:['ReadOwn'],max_tool_calls:6});
  const ctx=await open(),view=contexts.inspect(ctx);assert.equal(view.tenant,'review-desk');assert.deepEqual(view.source_scope,['ReviewDesk.OwnedRequest']);assert.throws(()=>contexts.inspect({...ctx}),err('ForeignOwner'));
  assert.throws(()=>createGenericCapabilityContextOwner({...owner},h,runtime),err('ForeignOwner'));assert.throws(()=>createGenericCapabilityContextOwner(owner,h,{...runtime}),err('ForeignOwner'));
  const result=await contexts.invokeTool(ctx,'ReadOwn',new TextEncoder().encode('{"id":"23"}'));assert.equal(result.ok,true);assert.deepEqual(JSON.parse(JSON.stringify(result.outcome)),{kind:'Returned',value:JSON.parse(readFileSync(path.join(c07,'context-fixture-rows.json'),'utf8')).rows.find((v:any)=>v.value.owner==='fixture-reviewer-a'&&v.value.id==='23').value.value});assert.equal(runtime.inspect().lookup_attempts,1);assert.equal(contexts.manifest(ctx).dependencies.length,1);
  await assert.rejects(contexts.invokeTool(await open(),'ReadOwn',new TextEncoder().encode('{"id":"23","tenant":"other","grants":true}')));
  const other=await contexts.invokeTool(await open(),'ReadOwn',new TextEncoder().encode('{"id":"24"}'));assert.equal(other.ok,true);assert.deepEqual(other.outcome,{kind:'Returned',value:null});
  const revoked=await open();auth.setPermission('fixture-reviewer-a','ReviewDesk.ReadOwnedRequestEntry',false);assert.equal((await contexts.invokeTool(revoked,'ReadOwn',new TextEncoder().encode('{"id":"23"}'))).ok,false);assert.equal(runtime.inspect().lookup_attempts,2);
  auth.setPermission('fixture-reviewer-a','ReviewDesk.ReadOwnedRequestEntry',true);const next=await open();assert.throws(()=>contexts.assertCurrent(ctx),err('StaleOwner'));const waiting=contexts.invokeTool(next,'ReadOwn',new TextEncoder().encode('{"id":"23"}'));contexts.cancel(next);await assert.rejects(waiting,err('StaleOwner'));assert.equal(runtime.inspect().lookup_attempts,2);
  const during=await open(),baseline=runtime.inspect().lookup_attempts,pending=contexts.invokeTool(during,'ReadOwn',new TextEncoder().encode('{"id":"23"}'));
  await waitForLookup(runtime,baseline,pending);
  auth.setPermission('fixture-reviewer-a','ReviewDesk.ReadOwnedRequestEntry',false);await assert.rejects(pending);assert.equal(runtime.inspect().lookup_attempts,baseline+1);
  const otherActor=auth.actor(runtime,'fixture-reviewer-c','ReviewDesk.ReadOwnedRequestEntry'),otherContext=await contexts.open(otherActor,'ReviewDesk.ApproveOwnedRequestEntry','Example.Selection',{deadline_ms:Date.now()+29000,tool_names:['ReadOwn'],max_tool_calls:6}),outside=await contexts.invokeTool(otherContext,'ReadOwn',new TextEncoder().encode(JSON.stringify({id:'23'})));assert.equal(outside.ok,true);assert.deepEqual(outside.outcome,{kind:'Returned',value:null});
  auth.setPermission('fixture-reviewer-a','ReviewDesk.ReadOwnedRequestEntry',true);const beforeData=await open(),beforeCount=runtime.inspect().lookup_attempts,dataPending=contexts.invokeTool(beforeData,'ReadOwn',new TextEncoder().encode(JSON.stringify({id:'23'})));
  await waitForLookup(runtime,beforeCount,dataPending);
  const database=new DatabaseSync(setup.storePath);try{const table=runtime.inspect().storage.tables.find((v:any)=>v.entity==='ReviewDesk.OwnedRequest');database.prepare('UPDATE '+JSON.stringify(table.physical_name)+' SET '+JSON.stringify(table.row_column)+' = zeroblob(1)').run();}finally{database.close();}await assert.rejects(dataPending,err('StaleOwner'));
 }finally{if(runtime)await runtime.close();if(auth)await auth.close();f.close();}
});
test('bounded search derives source/tenant custody from the exact original collection Entry and rejects SQL/filter authority',async()=>{
 const f=files('search'),owner=createGenericCompositionOwner();let runtime:any,auth:any;try{
  const h=await owner.prepare(f.input);accept(owner,h,f.dir);auth=await createGenericAuthFixture(owner,h,{ownedDirectory:path.join(f.dir,'auth'),subjects:[{id:'fixture-reviewer-a',evidence:'private-evidence',session:'private-session'}],grants:[{subject:'fixture-reviewer-a',entry:'ReviewDesk.ReadOwnedRequestEntry'}]});
  runtime=(await prepareGenericFixtureRuntime(owner,h,{service:'ReviewDeskService',ownedDirectory:path.join(f.dir,'store'),nativeAuth:auth.nativeAuth})).runtime;
  const contexts=createGenericCapabilityContextOwner(owner,h,runtime),actor=auth.actor(runtime,'fixture-reviewer-a','ReviewDesk.ReadOwnedRequestEntry');
  await assert.rejects(contexts.open(actor,'ReviewDesk.ReadRequestEntry','Example.Selection',{deadline_ms:Date.now()+29000,tool_names:[],max_tool_calls:0}),err('ForeignOwner'));
  const ctx=await contexts.open(actor,'ReviewDesk.ReadOwnedRequestEntry','Example.Selection',{deadline_ms:Date.now()+29000,tool_names:[],max_tool_calls:0}),search=await contexts.prepareSearch(ctx,{text:'bounded',top_k:1,filters:[{field:'id',operator:'eq',value:'23'}]});
  assert.equal((contexts.inspectSearch(search) as any).context.tenant,'review-desk');assert.throws(()=>contexts.inspectSearch({...search}),err('ForeignOwner'));
  for(const request of [{text:'x',top_k:1,filters:[],tenant:'forged'},{text:'x',top_k:3,filters:[]},{text:'x',top_k:1,filters:[{field:'rawSql',operator:'eq',value:'select *'}]},{text:'x',top_k:1,filters:[{field:'id',operator:'execute',value:'23'}]},{text:'x',top_k:1,filters:[{field:'id',operator:'eq',value:'not-a-UInt64'}]}])await assert.rejects(contexts.prepareSearch(ctx,request));
  auth.setPermission('fixture-reviewer-a','ReviewDesk.ReadOwnedRequestEntry',false);await assert.rejects(contexts.prepareSearch(ctx,{text:'x',top_k:1,filters:[]}));assert.equal(runtime.inspect().lookup_attempts,0);
  contexts.cancel(ctx);assert.throws(()=>contexts.inspectSearch(search),err('StaleOwner'));
 }finally{if(runtime)await runtime.close();if(auth)await auth.close();f.close();}
});
test('source capability constructors reject mismatched tool codecs and unsupported search collection/filter codecs',async()=>{
 for(const [mode,mutate] of [['agent',(s:any)=>s.bindings[0].contract.tools[0].argument_codec={kind:'scalar',name:'Bool'}],['agent',(s:any)=>s.bindings[0].contract.tools[0].result_codec={kind:'record',name:'ReviewDesk.Request'}],['search',(s:any)=>s.bindings[0].contract.search.collection='ReviewDesk.Request'],['search',(s:any)=>s.bindings[0].contract.search.filter_fields=['absent']],['search',(s:any)=>s.bindings[0].contract.search.filter_fields=['value']]] as const){const f=files(mode);try{mutate(f.selection);writeFileSync(path.join(f.dir,'selection.json'),JSON.stringify(f.selection));await assert.rejects(createGenericCompositionOwner().prepare(f.input));}finally{f.close();}}
});

test('bounded scalar filter operands preserve canonical UInt64 and Unicode wire semantics',()=>{
 const string={kind:'string' as const,max_bytes:16,max_scalars:8};assert.equal(isGenericCapabilityScalarOperand(string,'valid'),true);assert.equal(isGenericCapabilityScalarOperand(string,'\ud800'),false);assert.equal(isGenericCapabilityScalarOperand({kind:'scalar',name:'UInt64'},'01'),false);assert.equal(isGenericCapabilityScalarOperand({kind:'scalar',name:'Bool'},'true'),false);
});
