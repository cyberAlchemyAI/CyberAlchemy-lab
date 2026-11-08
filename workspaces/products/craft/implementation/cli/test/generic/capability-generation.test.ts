/** C03 generated wiring and actual native fixture dispatch over original owners.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,existsSync,mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {types as nativeFixtureDiagnostics} from 'node:util';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createGenericBundledApplicationOwner,createGenericCompositionOwner,createGenericGeneratedCapabilityOwner,createGenericHttpCompositionOwner} from '../../src/generic/public-sdk.js';
import {captureGenericCapabilityPackage} from '../../src/generic/capability-resource.js';
import {GENERIC_NATIVE_VECTOR_TYPE_V1} from '../../src/generic/capability-data-v1.js';
import {createGenericAuthFixture,loadGenericFixture,prepareGenericFixtureRuntime} from '../../src/generic/testing.js';
import {coreSha256} from '../../src/commerce/commerce-core-syntax.js';
import {dataDigest} from '../../src/profile-engine/contracts.js';
import {capabilityFixture} from './capability-fixtures.js';

const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const frontend=path.join(repo,'language/capabilities/alchlang/plans/general-compiler-v1/implementation/examples/generic-capabilities');
const c07=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/contracts/C07');
const nativeFixture=fileURLToPath(new URL('./fixtures/capability-resource/',import.meta.url));
const wire=(value:unknown)=>new TextEncoder().encode(JSON.stringify(value));
const plain=(value:unknown)=>JSON.parse(JSON.stringify(value));
const errorCode=(code:string)=>(error:any)=>(error?.diagnostics?.[0]?.code??error?.code)===code;
const maximum='18446744073709551615';

function business(field='id',agent=false){return `module Example version 1

value-object Request:
  ${field} UInt64
  verified Bool

interface Model:
  kind bounded-schema
  exposes Request

mapping Echo:
  input request Request
  target Request
  total true
  field ${field} <- request.${field}
  field verified <- request.verified

operation Answer:
  input request Request
  output Request
  return Echo(request)
${agent?`
entity OwnedRequest:
  owner Craft.Generated.Auth.ReadySubjectId
  id UInt64
  value Request
  identity owner, id

query ReadOwnedRequest:
  input id UInt64
  context actor Craft.Generated.Auth.CustomerContext
  source stored OwnedRequest
  output optional<Request>
  where stored.owner == actor.customerId and stored.id == id and actor.currentActionAllowed
  project stored.value
  on-missing return none
  on-unavailable fail read-unavailable

entry Example.ReadOwnedRequestEntry:
  invokes Example.ReadOwnedRequest
  interaction request-response
  access:
    authenticated customer
    permission example.read-own
    auth-resource example
    auth-action read-own
    auth-scope example
`:''}`;}

function setup(t:test.TestContext,options:{field?:string;agent?:boolean;resource?:string}={}){
 const directory=mkdtempSync(path.join(tmpdir(),'craft-capability-generation-'));
 const cleanup:Array<()=>unknown|Promise<unknown>>=[];t.after(async()=>{try{for(const close of cleanup.reverse())await close();}finally{rmSync(directory,{recursive:true,force:true});}});
 const consumer=path.join(directory,'consumer'),packageRoot=path.join(consumer,'node_modules/@craft-fixtures/capability-native');
 mkdirSync(path.dirname(packageRoot),{recursive:true});cpSync(nativeFixture,packageRoot,{recursive:true});
 if(options.resource)writeFileSync(path.join(packageRoot,'resource.mjs'),options.resource);
 const source=business(options.field,options.agent),profile=JSON.parse(readFileSync(path.join(options.agent?c07:frontend,'profile.json'),'utf8'));
 if(options.agent)profile.services=[{id:'ExampleService',module:'Example'}];
 mkdirSync(path.join(directory,'contracts'));writeFileSync(path.join(directory,'business.alch'),source);writeFileSync(path.join(directory,'profile.json'),JSON.stringify(profile));
 writeFileSync(path.join(directory,'contracts/bounds.json'),readFileSync(path.join(options.agent?c07:path.join(frontend,'contracts'),'bounds.json')));
 const {selection,kernel}=capabilityFixture();
 selection.source_sha256=coreSha256(source);selection.profile_sha256=coreSha256(readFileSync(path.join(directory,'profile.json')));
 selection.bindings[0].contract.result_type='Example.Request';
 selection.realizations[0].implementation={package:'@craft-fixtures/capability-native',version:'1.0.0',sha256:captureGenericCapabilityPackage(packageRoot).sha256,export:'./resource'};
 selection.realizations[0].target={destination:'fixture://selected',api:'resource/v1',model_or_harness:options.agent?'fixture-query-harness':'fixture-echo',revision:'1',mutability:'immutable'};
 if(options.agent){
  selection.bindings[0].contract={kind:'agent-run/v1',operation:'agent.run',input_type:'Example.Request',result_type:'Example.Request',required_capabilities:['readonly-tools','local-inspect'],loop_owner:'selected-harness',tools:[{name:'lookup',entry:'Example.ReadOwnedRequestEntry',query:'Example.ReadOwnedRequest',argument_codec:{kind:'scalar',name:'UInt64'},result_codec:{kind:'optional',element:{kind:'record',name:'Example.Request'}},effect:'read-only'}],checkpoint_version:'1'};
  selection.bindings[0].bounds.max_tool_calls=1;
  Object.assign(selection.realizations[0],{contract:'agent-run/v1',operations:['agent.run'],capabilities:['readonly-tools','local-inspect']});selection.realizations[0].bounds.max_tool_calls=1;
  kernel.integration_bindings[0].contract_ref='agent-run/v1';kernel.provider_profiles[0].capability_set=['agent-run/v1','readonly-tools','local-inspect'];
 }
 const save=()=>{selection.kernel.sha256=dataDigest(kernel);writeFileSync(path.join(directory,'kernel.json'),JSON.stringify(kernel));writeFileSync(path.join(directory,'selection.json'),JSON.stringify(selection));};save();
 return {directory,consumer,packageRoot,selection,kernel,save,cleanup:(close:()=>unknown|Promise<unknown>)=>cleanup.push(close),output:path.join(directory,'generated'),input:{sourcePath:path.join(directory,'business.alch'),profilePath:path.join(directory,'profile.json'),capabilitySelectionPath:path.join(directory,'selection.json')}};
}
function accept(owner:any,handle:any,directory:string,name='decision.json'){const review=owner.review(handle,'C03-generated-native-fixture');owner.accept(handle,{decision_id:'C03-test',owner:'C03-generated-native-fixture',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(directory,name));}
async function generate(t:test.TestContext,options:Parameters<typeof setup>[1]={}){
 const f=setup(t,options),composition=createGenericCompositionOwner(),handle=await composition.prepare(f.input);f.cleanup(()=>composition.dispose(handle));accept(composition,handle,f.directory);
 const manifest=composition.generate(handle,{...(options.agent?{entry:'Example.ReadOwnedRequestEntry'}:{operation:'Example.Answer'}),outputDirectory:f.output} as any) as any;
 const plan=JSON.parse(readFileSync(path.join(f.output,'capability-wiring.json'),'utf8'));
 return {...f,composition,handle,manifest,plan,binding:plan.bindings[0]};
}
function dispatch(f:{output:string;plan:unknown;composition:unknown;handle:any;consumer:string},runtime?:any){return createGenericGeneratedCapabilityOwner(pathToFileURL(path.join(f.output,'capabilities.mjs')).href,f.plan,f.composition,f.handle,{consumerRoot:f.consumer,...(runtime?{runtime}:{})});}
async function decode(f:Awaited<ReturnType<typeof generate>>,relativePath:string,value:unknown){const codec=await import(pathToFileURL(path.join(f.output,relativePath)).href);return codec.decode(wire(value));}

test('C03 source/profile/native-resource lineage emits executable exact UInt64 codecs and direct dispatch',async t=>{
 const f=await generate(t),owner=dispatch(f);f.cleanup(()=>owner.close());
 const value={id:maximum,verified:true},result=await owner.invoke('Example.Selection',wire(value),{deadline_ms:Date.now()+29000});
 assert.deepEqual(plain(result.value),value);assert.deepEqual(JSON.parse(new TextDecoder().decode(result.wire)),value);
 assert.equal(result.contract,'inference/v1');assert.equal(result.resource,'Example.RuntimeResource');assert.match(result.qualification,/no-provider-qualification/);
 assert.deepEqual(plain(f.manifest.capability_wiring),f.plan);assert.equal(f.plan.source_sha256,coreSha256(readFileSync(f.input.sourcePath)));assert.equal(f.plan.profile_sha256,coreSha256(readFileSync(f.input.profilePath)));
 const schema=JSON.parse(readFileSync(path.join(f.output,f.binding.result.schema_path),'utf8'));
 assert.deepEqual(schema.required,['id','verified']);assert.equal(schema.properties.id.type,'string');assert.equal(schema.additionalProperties,false);
 for(const value of [{id:'18446744073709551616',verified:true},{id:1,verified:true},{id:'01',verified:true},{id:maximum,verified:true,private:true}])await assert.rejects(owner.invoke('Example.Selection',wire(value),{deadline_ms:Date.now()+29000}),errorCode('TypeMismatch'));
 const graph=JSON.parse(readFileSync(path.join(f.output,'system-graph.json'),'utf8')),bridge=JSON.parse(readFileSync(path.join(f.output,'business-system-bridge.json'),'utf8'));
 const node=graph.nodes.find((n:any)=>n.id==='capability:Example.Selection'),resource=graph.nodes.find((n:any)=>n.id==='capability-resource:Example.Selection'),link=bridge.links.find((l:any)=>l.system==='capability:Example.Selection');
 assert.equal(node.artifact,'capabilities.mjs');assert.equal(node.result_schema,f.binding.result.schema_path);assert.deepEqual(node.source_to_profile,{source:f.plan.source_sha256,profile:f.plan.profile_sha256});
 assert.equal(resource.kind,'selected-native-resource');assert.equal(resource.harness_owner,null);assert.equal(link.result_schema_sha256,f.binding.result.schema_sha256);assert.equal(link.result_decoder_sha256,f.binding.result.decoder_sha256);assert.deepEqual(link.tools,[]);
 assert.equal(f.binding.harness_owner,null);assert.equal(f.binding.tool_mediation,'disabled');assert.deepEqual(f.binding.tools,[]);
 const generated=readFileSync(path.join(f.output,'capabilities.mjs'),'utf8');assert.match(generated,/from '@domainspec-v2\/cli\/generic'/);assert.doesNotMatch(generated,/agent-reasoning-engine|mcp__are|capability-context|\/src\/|agent-runtime/);
 const coverage=JSON.parse(readFileSync(path.join(f.output,'capability-coverage.json'),'utf8'));assert.match(JSON.stringify(coverage),/Example.Selection/);assert.match(JSON.stringify(coverage),/capabilities.mjs/);
 await assert.rejects(owner.invoke('unselected',wire(value),{deadline_ms:Date.now()+29000}),errorCode('UnknownReference'));
 writeFileSync(path.join(f.output,f.binding.result.decoder_path),readFileSync(path.join(f.output,f.binding.result.decoder_path),'utf8')+'\n');assert.throws(()=>owner.assertCurrent(),errorCode('StaleOwner'));
});

test('C03 renaming checked business fields regenerates schema and decoder together and rejects old wire',async t=>{
 const original=await generate(t),renamed=await generate(t,{field:'reference'});
 assert.notEqual(original.binding.result.schema_sha256,renamed.binding.result.schema_sha256);assert.notEqual(original.binding.result.decoder_sha256,renamed.binding.result.decoder_sha256);
 const schema=JSON.parse(readFileSync(path.join(renamed.output,renamed.binding.result.schema_path),'utf8'));assert.deepEqual(schema.required,['reference','verified']);assert.equal(schema.properties.id,undefined);
 assert.equal((await decode(renamed,renamed.binding.result.decoder_path,{id:maximum,verified:true})).ok,false);
 assert.equal((await decode(renamed,renamed.binding.result.decoder_path,{reference:maximum,verified:true})).ok,true);
 const owner=dispatch(renamed);renamed.cleanup(()=>owner.close());assert.deepEqual(plain((await owner.invoke('Example.Selection',wire({reference:maximum,verified:true}),{deadline_ms:Date.now()+29000})).value),{reference:maximum,verified:true});
});

test('C03 generated result decoder rejects invalid bytes returned by actual selected native fixture',async t=>{
 const f=await generate(t,{resource:`export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,async invoke(){return new TextEncoder().encode('{"id":"18446744073709551616","verified":true}');}});}\n`}),owner=dispatch(f);f.cleanup(()=>owner.close());
 await assert.rejects(owner.invoke('Example.Selection',wire({id:'23',verified:true}),{deadline_ms:Date.now()+29000}),errorCode('TypeMismatch'));
});

test('C03 missing/competing native bindings, unsupported requirements and private package paths refuse before output',async t=>{
 for(const mutate of [(f:ReturnType<typeof setup>)=>f.selection.bindings[0].realization_ref='Absent',(f:ReturnType<typeof setup>)=>f.selection.bindings.push({...f.selection.bindings[0],id:'Competing'}),(f:ReturnType<typeof setup>)=>f.selection.bindings[0].contract.required_capabilities.push('readonly-tools'),(f:ReturnType<typeof setup>)=>f.selection.realizations[0].implementation.package='/private/owner',(f:ReturnType<typeof setup>)=>f.selection.realizations[0].implementation.export='./../private']){
  const f=setup(t);mutate(f);f.save();await assert.rejects(async()=>{const owner=createGenericCompositionOwner(),h=await owner.prepare(f.input);accept(owner,h,f.directory);owner.generate(h,{operation:'Example.Answer',outputDirectory:f.output});},(error:any)=>/^CAPABILITY_/.test(error.code));assert.equal(existsSync(f.output),false);
 }
});

test('C03 agent harness dispatch mediates generated tool codecs through the original protected Query',async t=>{
 const resource=`export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,harness_owner:s.target.model_or_harness,async invoke(r){if(!Object.isFrozen(r.tool_schemas)||r.tool_schemas.length!==1||r.tool_schemas[0].name!=='lookup'||r.tool_schemas[0].argument_schema.type!=='string')throw Error('generated tool schemas required');const input=JSON.parse(new TextDecoder().decode(r.input));return r.toolBroker.invoke('lookup',new TextEncoder().encode(JSON.stringify(input.id)));}});}\n`;
 const generated=await generate(t,{agent:true,resource});
 const applicationPath=path.join(generated.output,'application.mjs'),application=readFileSync(applicationPath,'utf8'),serialized=application.match(/const bundle=(.*);\nexport/);assert.ok(serialized,'emitted public bundle data');
 const bundle=JSON.parse(serialized[1]!),composition=createGenericBundledApplicationOwner(pathToFileURL(applicationPath).href,bundle),handle=await composition.prepare();generated.cleanup(()=>composition.dispose(handle));accept(composition,handle,generated.directory,'reopened-decision.json');
 const f={...generated,composition,handle};assert.deepEqual(plain((composition.inspect(handle) as any).capability_bindings!.selection),generated.selection);
 const auth=await createGenericAuthFixture(f.composition,f.handle,{ownedDirectory:path.join(f.directory,'auth'),subjects:[{id:'fixture-reviewer',evidence:'private-evidence',session:'private-session'}],grants:[{subject:'fixture-reviewer',entry:'Example.ReadOwnedRequestEntry'}]});f.cleanup(()=>auth.close());
 const setupRuntime=await prepareGenericFixtureRuntime(f.composition,f.handle,{service:'ExampleService',ownedDirectory:path.join(f.directory,'store'),nativeAuth:auth.nativeAuth}),runtime=setupRuntime.runtime;f.cleanup(()=>runtime.close());
 const expected={id:maximum,verified:true};loadGenericFixture(setupRuntime.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[{entity:'Example.OwnedRequest',value:{owner:'fixture-reviewer',id:maximum,value:expected}},{entity:'Example.OwnedRequest',value:{owner:'other-reviewer',id:maximum,value:{id:maximum,verified:false}}}]}));
 const owner=dispatch(f,runtime);f.cleanup(()=>owner.close());const actor=auth.actor(runtime,'fixture-reviewer','Example.ReadOwnedRequestEntry'),context=await owner.openContext(actor,'Example.ReadOwnedRequestEntry','Example.Selection',{deadline_ms:Date.now()+29000,tool_names:['lookup'],max_tool_calls:1});
 const result=await owner.invoke('Example.Selection',wire({id:maximum,verified:false}),{deadline_ms:Date.now()+28000,context});assert.deepEqual(plain(result.value),expected);assert.equal(runtime.inspect().lookup_attempts,1);
 assert.equal(f.binding.contract.kind,'agent-run/v1');assert.equal(f.binding.harness_owner,'fixture-query-harness');assert.equal(f.binding.tool_mediation,'original-c02-query-context/v1');assert.equal(f.binding.tools[0].argument_parameter,'id');assert.equal(f.binding.tools[0].entry,'Example.ReadOwnedRequestEntry');
 const bridge=JSON.parse(readFileSync(path.join(f.output,'business-system-bridge.json'),'utf8')).links.find((l:any)=>l.system==='capability:Example.Selection');assert.equal(bridge.harness_owner,'fixture-query-harness');assert.equal(bridge.tools[0].argument_codec_sha256,f.binding.tools[0].argument.decoder_sha256);assert.equal(bridge.tools[0].query,'Example.ReadOwnedRequest');
 await assert.rejects(owner.invoke('Example.Selection',wire({id:maximum,verified:true}),{deadline_ms:Date.now()+28000}),errorCode('ForeignOwner'));
 const revoked=await owner.openContext(actor,'Example.ReadOwnedRequestEntry','Example.Selection',{deadline_ms:Date.now()+29000,tool_names:['lookup'],max_tool_calls:1});auth.setPermission('fixture-reviewer','Example.ReadOwnedRequestEntry',false);await assert.rejects(owner.invoke('Example.Selection',wire(expected),{deadline_ms:Date.now()+28000,context:revoked}));assert.equal(runtime.inspect().lookup_attempts,1);
});


test('C03 selected capability survives original protected HTTP generation and atomic bundle reopen',async t=>{
 const f=setup(t),fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C09/schedule-http-second-domain-source-001/fixture'),authored=path.join(f.directory,'http-authored');
 cpSync(fixture,authored,{recursive:true});const sourcePath=path.join(authored,'business.alch'),profilePath=path.join(authored,'contracts/selected-profile.json'),httpProfilePath=path.join(authored,'contracts/http-profile.json');
 const source=readFileSync(sourcePath,'utf8')+'\nvalue-object NativeProposal:\n  id UInt64\n  verified Bool\n\ninterface NativeModel:\n  kind bounded-schema\n  exposes NativeProposal\n';writeFileSync(sourcePath,source);
 f.selection.source_sha256=coreSha256(source);f.selection.profile_sha256=coreSha256(readFileSync(profilePath));Object.assign(f.selection.bindings[0],{interface:'Schedule.NativeModel',contract:{...f.selection.bindings[0].contract,input_type:'Schedule.NativeProposal',result_type:'Schedule.NativeProposal'}});f.kernel.integration_bindings[0].logical_boundary_ref='Schedule.NativeModel';f.kernel.failure_mappings[0].boundary_ref='Schedule.NativeModel';f.save();
 const composition=createGenericHttpCompositionOwner(),handle=await composition.prepare({sourcePath,profilePath,httpProfilePath,capabilitySelectionPath:f.input.capabilitySelectionPath});f.cleanup(()=>composition.dispose(handle));accept(composition,handle,f.directory);
 const before=composition.inspect(handle),manifest=composition.generate(handle,{entry:'Schedule.ReserveBookingEntry',outputDirectory:f.output}) as any;
 const applicationPath=path.join(f.output,'application.mjs'),application=readFileSync(applicationPath,'utf8'),serialized=application.match(/const bundle=(.*);\nexport/);assert.ok(serialized);
 const bundle=JSON.parse(serialized[1]!),restored=createGenericBundledApplicationOwner(pathToFileURL(applicationPath).href,bundle),restoredHandle=await restored.prepare();f.cleanup(()=>restored.dispose(restoredHandle));accept(restored,restoredHandle,f.directory,'reopened-decision.json');
 const after=restored.inspect(restoredHandle) as any;assert.equal(after.transport_semantics_sha256,before.transport_semantics_sha256);assert.deepEqual(plain(after.http_contract.entries),plain(before.http_contract.entries));assert.equal(after.capability_bindings.bindings[0].interface,'Schedule.NativeModel');
 const plan=JSON.parse(readFileSync(path.join(f.output,'capability-wiring.json'),'utf8')),native=createGenericGeneratedCapabilityOwner(pathToFileURL(path.join(f.output,'capabilities.mjs')).href,plan,restored,restoredHandle,{consumerRoot:f.consumer});f.cleanup(()=>native.close());
 assert.deepEqual(plain((await native.invoke('Example.Selection',wire({id:maximum,verified:true}),{deadline_ms:Date.now()+29000})).value),{id:maximum,verified:true});assert.equal(manifest.capability_wiring.bindings[0].interface,'Schedule.NativeModel');
 const graph=JSON.parse(readFileSync(path.join(f.output,'system-graph.json'),'utf8'));assert.equal(graph.nodes.filter((node:any)=>node.kind==='injected-http-handler').length,2);assert.ok(graph.nodes.some((node:any)=>node.id==='storage:ScheduleService'&&node.kind==='sqlite-atomic-command-store'));
});


test('C03 unsupported strict business shapes and absent agent tool mediation reject before publication',async t=>{
 for(const agent of [false,true]){
  const f=setup(t,{agent});
  if(agent){f.selection.bindings[0].bounds.max_tool_calls=0;f.selection.realizations[0].bounds.max_tool_calls=0;}
  else{const source=readFileSync(f.input.sourcePath,'utf8').replace('  verified Bool','  verified Bool\n  invariant id > 0');writeFileSync(f.input.sourcePath,source);f.selection.source_sha256=coreSha256(source);}
  f.save();const composition=createGenericCompositionOwner(),handle=await composition.prepare(f.input);f.cleanup(()=>composition.dispose(handle));accept(composition,handle,f.directory);
  assert.throws(()=>composition.generate(handle,{...(agent?{entry:'Example.ReadOwnedRequestEntry'}:{operation:'Example.Answer'}),outputDirectory:f.output} as any),errorCode('UnsupportedCapability'));assert.equal(existsSync(f.output),false);
 }
});

test('C03 dispatch ignores poisoned file codec cache and copies bounded bytes without caller getters',async t=>{
 const f=await generate(t);
 for(const relativePath of [f.binding.input.decoder_path,f.binding.result.decoder_path]){
  const filename=path.join(f.output,relativePath),original=readFileSync(filename,'utf8');
  writeFileSync(filename,"export function decode(){throw Error('POISONED_NODE_FILE_CODEC_CACHE');}\n");
  const poisoned=await import(pathToFileURL(filename).href);assert.throws(()=>poisoned.decode(wire({})),/POISONED_NODE_FILE_CODEC_CACHE/);
  writeFileSync(filename,original);
  // The file URL still resolves to the poisoned ESM cache after restoration.
  assert.strictEqual(await import(pathToFileURL(filename).href),poisoned);
 }
 const owner=dispatch(f);f.cleanup(()=>owner.close());let getters=0;
 const decorate=(input:Uint8Array)=>{
  for(const key of ['buffer','byteLength','byteOffset','constructor'])Object.defineProperty(input,key,{get(){getters++;throw Error('CALLER_BYTE_GETTER_EXECUTED');}});
  return input;
 };
 await assert.rejects(owner.invoke('Example.Selection',decorate(new Uint8Array(f.binding.bounds.max_input_bytes+1)),{deadline_ms:Date.now()+29000}),errorCode('ResourceLimit'));assert.equal(getters,0);
 const expected={id:maximum,verified:true},input=decorate(wire(expected)),result=await owner.invoke('Example.Selection',input,{deadline_ms:Date.now()+29000});
 assert.deepEqual(plain(result.value),expected);assert.deepEqual(JSON.parse(new TextDecoder().decode(result.wire)),expected);assert.equal(getters,0);
});

test('C03 vector.embed generates and dispatches reserved finite-vector results with exact dimensions',async t=>{
 const f=setup(t,{resource:`export function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,async invoke(r){const input=JSON.parse(new TextDecoder().decode(r.input));return new TextEncoder().encode(input.id==='2'?'[1,2]':input.id==='3'?'[1e999,0,2]':'[0.125,-0,2.5]');}});}\n`});
 f.selection.bindings[0].contract={kind:'inference/v1',operation:'vector.embed',input_type:'Example.Request',result_type:GENERIC_NATIVE_VECTOR_TYPE_V1,required_capabilities:['embeddings'],tools:'disabled',embedding:{dimensions:3,preprocessing_ref:'Example.VectorPreprocess',space_generation:'Example.EmbeddingSpace1'}};
 Object.assign(f.selection.realizations[0],{operations:['vector.embed'],capabilities:['embeddings'],schema:{dialect:'https://json-schema.org/draft/2020-12/schema',subset:'finite-vector/v1'}});f.kernel.provider_profiles[0].capability_set=['inference/v1','embeddings'];f.save();
 const frontendSource=await import(pathToFileURL(path.resolve(frontend,'../../src/generic-business-source.ts')).href),parsed=frontendSource.parseGenericBusinessSource(readFileSync(f.input.sourcePath,'utf8'),'business.alch',true,true);
 assert.equal(parsed.declarations.some((declaration:any)=>declaration.id===GENERIC_NATIVE_VECTOR_TYPE_V1),false);assert.equal(frontendSource.lowerGenericCapabilitySelectors([parsed],f.selection,'selection.json')[0].result_type,GENERIC_NATIVE_VECTOR_TYPE_V1);
 const composition=createGenericCompositionOwner(),handle=await composition.prepare(f.input);f.cleanup(()=>composition.dispose(handle));accept(composition,handle,f.directory);composition.generate(handle,{operation:'Example.Answer',outputDirectory:f.output});
 const plan=JSON.parse(readFileSync(path.join(f.output,'capability-wiring.json'),'utf8')),binding=plan.bindings[0],schema=JSON.parse(readFileSync(path.join(f.output,binding.result.schema_path),'utf8'));
 assert.deepEqual(binding.input.type,{kind:'record',name:'Example.Request'});assert.deepEqual(binding.result.type,{kind:'native-vector',dimensions:3});assert.deepEqual(binding.contract.embedding,{dimensions:3,preprocessing_ref:'Example.VectorPreprocess',space_generation:'Example.EmbeddingSpace1'});
 assert.equal(schema.type,'array');assert.equal(schema.items.type,'number');assert.equal(schema.minItems,3);assert.equal(schema.maxItems,3);assert.equal(schema.items.minimum,-Number.MAX_VALUE);assert.equal(schema.items.maximum,Number.MAX_VALUE);
 const owner=dispatch({...f,composition,handle,plan});f.cleanup(()=>owner.close());const result=await owner.invoke('Example.Selection',wire({id:maximum,verified:true}),{deadline_ms:Date.now()+29000});
 assert.deepEqual(result.value,[0.125,0,2.5]);assert.ok(Object.isFrozen(result.value));assert.equal(Object.is((result.value as number[])[1],-0),false);assert.equal(new TextDecoder().decode(result.wire),'[0.125,0,2.5]');
 for(const id of ['2','3'])await assert.rejects(owner.invoke('Example.Selection',wire({id,verified:true}),{deadline_ms:Date.now()+29000}),errorCode('TypeMismatch'));
});

test('C03 final native disclosure reauthorizes used tool grants while the distinct root grant remains valid',async t=>{
 const f=setup(t,{agent:true}),marker='C03-native-disclosure-'+path.basename(f.directory),state={tool_returned:false,release:false};
 // Fixture diagnostics synchronize the test after actual tool completion; the
 // selected native ABI receives only its original generated Query broker.
 (nativeFixtureDiagnostics as any)[marker]=state;f.cleanup(()=>{delete (nativeFixtureDiagnostics as any)[marker];});
 const resource=`import {types as diagnostic} from 'node:util';\nexport function createCapabilityResource(s){return Object.freeze({abi:s.abi,operations:s.realization.operations,capabilities:s.realization.capabilities,harness_owner:s.target.model_or_harness,async invoke(r){const input=JSON.parse(new TextDecoder().decode(r.input)),result=await r.toolBroker.invoke('lookup',new TextEncoder().encode(JSON.stringify(input.id))),state=diagnostic[${JSON.stringify(marker)}];state.tool_returned=true;while(!state.release)await new Promise(resolve=>setTimeout(resolve,1));return result;}});}\n`;
 writeFileSync(path.join(f.packageRoot,'resource.mjs'),resource);f.selection.realizations[0].implementation.sha256=captureGenericCapabilityPackage(f.packageRoot).sha256;
 const source=readFileSync(f.input.sourcePath,'utf8')+`\nentry Example.NativeRootEntry:\n  invokes Example.ReadOwnedRequest\n  interaction request-response\n  access:\n    authenticated customer\n    permission example.native-run\n    auth-resource example\n    auth-action native-run\n    auth-scope example\n`;writeFileSync(f.input.sourcePath,source);f.selection.source_sha256=coreSha256(source);f.save();
 const composition=createGenericCompositionOwner(),handle=await composition.prepare(f.input);f.cleanup(()=>composition.dispose(handle));accept(composition,handle,f.directory);composition.generate(handle,{entry:'Example.NativeRootEntry',outputDirectory:f.output});
 const rootEntry='Example.NativeRootEntry',toolEntry='Example.ReadOwnedRequestEntry',subject='fixture-reviewer',auth=await createGenericAuthFixture(composition,handle,{ownedDirectory:path.join(f.directory,'auth'),subjects:[{id:subject,evidence:'private-evidence',session:'private-session'}],grants:[{subject,entry:rootEntry},{subject,entry:toolEntry}]});f.cleanup(()=>auth.close());
 const fixture=await prepareGenericFixtureRuntime(composition,handle,{service:'ExampleService',ownedDirectory:path.join(f.directory,'store'),nativeAuth:auth.nativeAuth}),runtime=fixture.runtime;f.cleanup(()=>runtime.close());
 const value={id:maximum,verified:true};loadGenericFixture(fixture.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[{entity:'Example.OwnedRequest',value:{owner:subject,id:maximum,value}}]}));
 const plan=JSON.parse(readFileSync(path.join(f.output,'capability-wiring.json'),'utf8')),owner=dispatch({...f,composition,handle,plan},runtime);f.cleanup(()=>owner.close());
 const actor=auth.actor(runtime,subject,rootEntry),context=await owner.openContext(actor,rootEntry,'Example.Selection',{deadline_ms:Date.now()+29000,tool_names:['lookup'],max_tool_calls:1});let disclosed=false,settled=false;
 const pending=owner.invoke('Example.Selection',wire(value),{deadline_ms:Date.now()+28000,context}).then(result=>{disclosed=true;return result;});void pending.then(()=>{settled=true;},()=>{settled=true;});
 try{
  const until=Date.now()+20000;while(!state.tool_returned){if(settled)await pending;if(Date.now()>=until)throw Error('bounded native tool-completion wait expired');await new Promise<void>(resolve=>setImmediate(resolve));}
  assert.equal(runtime.inspect().lookup_attempts,1);assert.equal(disclosed,false);auth.setPermission(subject,toolEntry,false);
  const prepared=runtime.prepareInput(runtime.entry(rootEntry),wire({id:maximum}));try{assert.equal((await runtime.authorize(actor,prepared)).ok,true,'distinct root grant remains authorized after tool revocation');}finally{runtime.disposePrepared(prepared);}
  state.release=true;await assert.rejects(pending,errorCode('ForeignOwner'));assert.equal(disclosed,false);assert.equal(runtime.inspect().lookup_attempts,1);
 }finally{state.release=true;await pending.catch(()=>{});}
});
