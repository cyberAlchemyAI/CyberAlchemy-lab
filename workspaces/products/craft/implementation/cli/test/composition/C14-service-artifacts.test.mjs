import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync,unlinkSync,rmSync,mkdirSync,symlinkSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericCompositionOwner,requireGenericWorkflowRuntime} from '../../src/generic/public-sdk.ts';
import {createGenericAuthFixture,prepareGenericFixtureRuntime,loadGenericFixture} from '../../src/generic/testing.ts';
import {createGenericServiceArtifactOwner,assertGenericServiceArtifactOwner} from '../../src/generic/service-artifact-owner.ts';
import {GenericWorkflowStore} from '../../src/generic/workflow-store.ts';
import {workflowCompatibilitySha256} from '../../src/generic/workflow-worker.ts';
import {canonicalJson} from '../../src/profile-engine/contracts.ts';

const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const c10Fixture=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/tests-progress-history-002/fixtures/reviewdesk');
const oracle=JSON.parse(readFileSync(path.join(c10Fixture,'independent-oracle.json'),'utf8'));
const wire=value=>Buffer.from(JSON.stringify(value));
const withAdvancedClock=(milliseconds,action)=>{const now=Date.now;Date.now=()=>now()+milliseconds;try{return action();}finally{Date.now=now;}};

test('C14 rejects a lookalike service artifact owner before inspecting it',()=>{
 let inspected=false;
 assert.throws(()=>assertGenericServiceArtifactOwner(Object.freeze({inspect(){inspected=true;return {};}})),
  error=>error.diagnostics?.[0]?.code==='ForeignOwner');
 assert.equal(inspected,false);
});

test('C14 emits checked, separate producer and receiver service artifacts from one accepted application',async()=>{
 const root=workflowFixture(),work=path.dirname(root),sdk=createGenericCompositionOwner();
 let source,auth,producerRuntime,consumerRuntime,relay,generatedHandle,generatedAuth,generatedRuntime,generatedRelay,binding;
 try{
  source=await sdk.prepare({sourcePath:path.join(root,'business.alch'),
   additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),
   externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const review=sdk.review(source,'C14-service-source');
  sdk.accept(source,{decision_id:'C14-service-source',owner:'C14-service-source',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'C14-service-decision.json'));
  const emitter=createGenericServiceArtifactOwner(sdk,source),output=path.join(work,'C14-services');
  assert.doesNotThrow(()=>assertGenericServiceArtifactOwner(emitter));
  assert.throws(()=>assertGenericServiceArtifactOwner(Object.freeze({inspect:emitter.inspect})),
   error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  assert.throws(()=>emitter.emit({outputDirectory:path.join(work,'not-complete'),
   entries:[oracle.root_entry,'AuditService.RecordApprovedEntry'],requireCompleteApplication:true}),
   error=>error.diagnostics?.[0]?.code==='MissingMapping');
  const artifact=emitter.emit({outputDirectory:output,
   entries:[oracle.root_entry,'AuditService.RecordApprovedEntry']});
  const inventory=emitter.inspect(artifact);
  const packageScope=path.join(work,'node_modules/@domainspec-v2');
  mkdirSync(packageScope,{recursive:true});
  symlinkSync(fileURLToPath(new URL('../../',import.meta.url)),path.join(packageScope,'cli'),'dir');
  assert.deepEqual(inventory.services.map(service=>service.service).sort(),['AuditService','ReviewDeskService']);
  assert.equal(inventory.complete_application,false);
  assert.ok(inventory.missing_complete_application_classes.includes('service-repository-runtime-verification'));
  assert.ok(inventory.missing_complete_application_classes.includes('api-transport-adapter'));
  assert.ok(inventory.missing_complete_application_classes.includes('workflow-worker-runtime-verification'));
  assert.ok(inventory.missing_complete_application_classes.some(value=>value.startsWith('entry:')));
  assert.throws(()=>emitter.assertComplete(artifact),error=>error.diagnostics?.[0]?.code==='MissingMapping');
  assert.throws(()=>emitter.inspect(Object.freeze({kind:artifact.kind})),error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  const runtimeModules=new Map();
  for(const service of inventory.services){
   assert.equal(service.entries.length,1);
   assert.ok(service.entities.length>0);
   const entry=service.entries[0],module=readFileSync(path.join(output,service.directory,'service.mjs'),'utf8');
   assert.ok(module.includes(`from './entries/`));
   assert.ok(module.includes('export function createGeneratedServiceOwners'));
   assert.ok(module.includes('export function createGeneratedServiceHttpHandlers'));
   if(entry.interaction==='event'){
    assert.equal(entry.http_export,null);
    assert.ok(!module.includes(`from './entries/${entry.directory.split('/').at(-1)}/entry-http.mjs'`));
   }
   const serviceModule=await import(pathToFileURL(path.join(output,service.directory,'service.mjs')).href);
   assert.equal(serviceModule.serviceId,service.service);
   assert.deepEqual(serviceModule.entryIds,[entry.entry]);
   assert.equal(typeof serviceModule.createGeneratedServiceOwners()[entry.entry],'function');
   assert.ok(readFileSync(path.join(output,entry.directory,'application.mjs'),'utf8').includes('createGeneratedApplicationOwner'));
   const graph=JSON.parse(readFileSync(path.join(output,entry.directory,'system-graph.json'),'utf8'));
   const bridge=JSON.parse(readFileSync(path.join(output,entry.directory,'business-system-bridge.json'),'utf8'));
   assert.ok(graph.nodes.some(node=>node.id==='storage:'+service.service));
   assert.ok(bridge.links.some(link=>link.business===entry.entry&&link.system==='generated:'+entry.entry));
   const wiring=JSON.parse(readFileSync(path.join(output,service.directory,'service-wiring.json'),'utf8'));
   const serviceGraph=JSON.parse(readFileSync(path.join(output,service.directory,'service-system-graph.json'),'utf8'));
   const serviceBridge=JSON.parse(readFileSync(path.join(output,service.directory,'service-business-system-bridge.json'),'utf8'));
   assert.equal(wiring.service,service.service);
   assert.equal(wiring.application_contract_sha256,inventory.application_contract_sha256);
   assert.deepEqual(wiring.selected_entries,[entry.entry]);
   assert.equal(wiring.event_relay.bindings.length,1);
   assert.equal(wiring.event_relay.bindings[0].id,service.event_bindings[0]);
   assert.equal(wiring.worker?.executable_module??false,false);
   assert.equal(wiring.provider_adapter.provider_port_implementation,false);
   assert.equal(wiring.event_relay.relay_delivery_adapter,false);
   assert.ok(serviceGraph.nodes.some(node=>node.id==='entry:'+entry.entry&&node.manifest_sha256===entry.manifest_sha256));
   assert.ok(serviceGraph.nodes.some(node=>node.id==='runtime:'+service.service&&node.sha256===service.runtime_module_sha256));
   assert.ok(serviceGraph.edges.some(edge=>edge.from==='service:'+service.service&&edge.to==='runtime:'+service.service));
   assert.ok(serviceGraph.edges.some(edge=>edge.from==='runtime:'+service.service&&edge.to==='entry:'+entry.entry));
   assert.ok(serviceGraph.edges.some(edge=>edge.from==='runtime:'+service.service&&edge.to==='storage:'+entry.entry));
   assert.ok(serviceGraph.edges.some(edge=>edge.from==='runtime:'+service.service&&edge.to==='event:'+service.event_bindings[0]));
   assert.ok(serviceBridge.links.some(link=>link.business===service.service&&link.system==='runtime:'+service.service));
   assert.ok(serviceBridge.links.some(link=>link.business===entry.entry&&link.system==='entry:'+entry.entry));
   if(entry.interaction==='request-response'){
    assert.ok(serviceGraph.nodes.some(node=>node.id==='api:'+entry.entry&&node.sha256===entry.http_module_sha256));
    assert.ok(serviceGraph.edges.some(edge=>edge.from==='service:'+service.service&&edge.to==='api:'+entry.entry));
    assert.ok(serviceGraph.edges.some(edge=>edge.from==='runtime:'+service.service&&edge.to==='api:'+entry.entry));
    assert.ok(serviceBridge.links.some(link=>link.business===service.service&&link.system==='api:'+entry.entry));
    assert.ok(serviceBridge.links.some(link=>link.business===entry.entry&&link.system==='api:'+entry.entry));
   }else assert.ok(!serviceGraph.nodes.some(node=>node.id==='api:'+entry.entry));
   assert.ok(serviceGraph.edges.every(edge=>serviceGraph.nodes.some(node=>node.id===edge.from)&&serviceGraph.nodes.some(node=>node.id===edge.to)));
   assert.ok(serviceBridge.links.every(link=>serviceGraph.nodes.some(node=>node.id===link.system)));
   const runtimeModule=await import(pathToFileURL(path.join(output,service.directory,'runtime.mjs')).href);
   runtimeModules.set(service.service,runtimeModule);
   assert.equal(runtimeModule.serviceId,service.service);
   assert.equal(runtimeModule.sourceContractSha256,inventory.application_contract_sha256);
   assert.equal(runtimeModule.sourceCaptureSha256,inventory.source_capture_sha256);
   assert.equal(runtimeModule.executableSemanticsSha256,inventory.executable_semantics_sha256);
   assert.equal(runtimeModule.selectedProfileSha256,inventory.profile_sha256);
   await assert.rejects(runtimeModule.openGeneratedServiceArtifactRuntime(emitter,Object.freeze({kind:artifact.kind}),{}),
    error=>error.diagnostics?.[0]?.code==='ForeignOwner');
   await assert.rejects(runtimeModule.openGeneratedServiceArtifactRuntime({inspect:()=>({})},artifact,{}),
    /GENERATED_SERVICE_ARTIFACT_OWNER/);
   const opened=[];
   const runtime={openEventRelay:()=>({kind:'original-relay-placeholder'})};
   const fakeSdk={inspect:()=>sdk.inspect(source),openRuntime:async (_source,options)=>{opened.push(options);return runtime;}};
   await assert.rejects(runtimeModule.openGeneratedServiceRuntime(fakeSdk,source,{service:'forged'}),/GENERATED_SERVICE_RUNTIME_INPUT/);
   await assert.rejects(runtimeModule.openGeneratedServiceRuntime({inspect:()=>({expanded:{capture_sha256:'0'.repeat(64)}}),openRuntime:fakeSdk.openRuntime},source,{storePath:'/tmp/fixture',mode:'create',nativeAuth:{}}),/GENERATED_SERVICE_SOURCE_MISMATCH/);
   const result=await runtimeModule.openGeneratedServiceRuntime(fakeSdk,source,{storePath:'/tmp/fixture',mode:'create',nativeAuth:{}});
   assert.equal(result,runtime);
   assert.equal(opened[0].service,service.service);
   if(wiring.event_relay.bindings.some(binding=>binding.role!=='receiver')){
    assert.throws(()=>runtimeModule.openGeneratedServiceRelay({openEventRelay:runtime.openEventRelay}),/GENERATED_SERVICE_RUNTIME_OWNER/);
    assert.equal(runtimeModule.openGeneratedServiceRelay(result).kind,'original-relay-placeholder');
   }else assert.equal(runtimeModule.openGeneratedServiceRelay,undefined);
  }
  const producer=inventory.services.find(service=>service.workflow);
  const producerWiring=JSON.parse(readFileSync(path.join(output,producer.directory,'service-wiring.json'),'utf8'));
  const producerGraph=JSON.parse(readFileSync(path.join(output,producer.directory,'service-system-graph.json'),'utf8'));
  const producerBridge=JSON.parse(readFileSync(path.join(output,producer.directory,'service-business-system-bridge.json'),'utf8'));
  assert.equal(producerWiring.worker.id,producer.workflow);
  assert.equal(producerWiring.worker.required_entries_covered,false);
  assert.ok(producerWiring.provider_adapter.bindings.length>0);
  assert.ok(producerWiring.provider_adapter.bindings.every(binding=>producerGraph.edges.some(edge=>
   edge.from==='runtime:'+producer.service&&edge.to==='provider:'+binding.id&&edge.kind==='requires-checked-provider-binding')));
  assert.ok(producerGraph.edges.some(edge=>edge.from==='runtime:'+producer.service&&edge.to==='worker:'+producer.workflow));
  assert.ok(producerGraph.nodes.some(node=>node.id==='worker:'+producer.workflow&&node.artifact===producer.directory+'/worker.mjs'&&node.sha256===producer.worker_module_sha256));
  assert.ok(producerGraph.edges.filter(edge=>edge.from==='worker:'+producer.workflow).every(edge=>producerGraph.nodes.some(node=>node.id===edge.to)));
  assert.ok(producerBridge.links.some(link=>link.business===producer.workflow&&link.system==='worker:'+producer.workflow));
  const incompleteWorker=await import(pathToFileURL(path.join(output,producer.directory,'worker.mjs')).href);
  assert.equal(incompleteWorker.workflowId,producer.workflow);
  assert.ok(incompleteWorker.requiredEntryIds.length>2);
  assert.throws(()=>incompleteWorker.createGeneratedServiceWorkflowWorker(emitter,artifact,{}),/GENERATED_WORKFLOW_ENTRY_MISSING/);
  const receiverEntry=inventory.services.find(service=>service.service==='AuditService').entries[0];
  assert.equal(receiverEntry.interaction,'event');
  auth=await createGenericAuthFixture(sdk,source,{ownedDirectory:path.join(work,'C14-auth'),
   subjects:[{id:'c14-subject',evidence:'c14-evidence',session:'c14-session'}],grants:[]});
  const port={exchange:async()=>{throw Error('PROVIDER_NOT_INVOKED')}};
  producerRuntime=await runtimeModules.get('ReviewDeskService').openGeneratedServiceArtifactRuntime(emitter,artifact,{storePath:path.join(work,'C14-producer.sqlite'),mode:'create',nativeAuth:auth.nativeAuth,externalWritePort:port});
  consumerRuntime=await runtimeModules.get('AuditService').openGeneratedServiceArtifactRuntime(emitter,artifact,{storePath:path.join(work,'C14-consumer.sqlite'),mode:'create',nativeAuth:auth.nativeAuth});
  assert.ok(producerRuntime.entry(oracle.root_entry));
  assert.ok(consumerRuntime.entry('AuditService.RecordApprovedEntry'));
  relay=runtimeModules.get('ReviewDeskService').openGeneratedServiceArtifactRelay(emitter,artifact,producerRuntime);
  assert.equal(relay.kind,'original-generic-event-relay-owner/v1-candidate');
  assert.throws(()=>runtimeModules.get('ReviewDeskService').openGeneratedServiceArtifactRelay(emitter,artifact,consumerRuntime),
   error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  assert.throws(()=>emitter.openServiceRelay(artifact,'ReviewDeskService',consumerRuntime),error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  assert.throws(()=>emitter.openServiceRelay(artifact,'AuditService',consumerRuntime),error=>error.diagnostics?.[0]?.code==='UnsupportedCapability');
  assert.equal(runtimeModules.get('AuditService').openGeneratedServiceArtifactRelay,undefined);
  await assert.rejects(emitter.openServiceHttpDispatch(artifact,'ReviewDeskService',consumerRuntime),
   error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  await assert.rejects(emitter.openServiceHttpDispatch(artifact,'AuditService',consumerRuntime),
   error=>error.diagnostics?.[0]?.code==='UnsupportedCapability');
  const generatedHttpManifest=JSON.parse(readFileSync(path.join(output,producer.entries[0].directory,'manifest.json'),'utf8'));
  const generatedHttp=generatedHttpManifest.runtime_contract?.http;
  assert.deepEqual({
   entry:generatedHttpManifest.entry,
   profile:generatedHttpManifest.profile?.sha256,
   source:generatedHttpManifest.expanded?.capture_sha256,
   semantics:generatedHttpManifest.expanded?.executable_semantics_sha256,
   method:generatedHttp?.method,
   route:generatedHttp?.route,
   identity:generatedHttp?.identity,
   routes:generatedHttp?.routes,
  },{
   entry:oracle.root_entry,
   profile:sdk.inspect(source).profile.sha256,
   source:inventory.source_capture_sha256,
   semantics:inventory.executable_semantics_sha256,
   method:'POST',
   route:'/entries/'+oracle.root_entry.replaceAll('.','/'),
   identity:'injected-original-runtime-actor',
   routes:undefined,
  });
  const dispatch=await emitter.openServiceHttpDispatch(artifact,'ReviewDeskService',producerRuntime);
  const route='http://service.invalid/entries/'+oracle.root_entry.replaceAll('.','/');
  const wrongMethod=await dispatch(new Request(route));
  assert.equal(wrongMethod.status,405);
  const unauthenticated=await dispatch(new Request(route,{method:'POST',headers:{'content-type':'application/json','idempotency-key':'c14-http-noauth'},body:canonicalJson(oracle.operation_input)}));
  assert.equal(unauthenticated.status,401);
  assert.throws(()=>emitter.createServiceWorkflowWorker(artifact,'ReviewDeskService',{runtime:producerRuntime}),error=>error.diagnostics?.[0]?.code==='MissingMapping');
  binding=emitter.bindGeneratedApplication(artifact,oracle.root_entry);
  generatedHandle=await binding.owner.prepare();
  assert.equal(binding.entry,oracle.root_entry);
  assert.equal(binding.owner.inspect(generatedHandle).transaction_contract.schema_version,
   'craft.generic-transaction-application/v4-candidate');
  assert.equal(binding.owner.inspect(generatedHandle).transaction_contract.admission_mode,'event-handoff-entry');
  const generatedReview=binding.owner.review(generatedHandle,'C14-service-generated');
  binding.owner.accept(generatedHandle,{decision_id:'C14-service-generated',owner:'C14-service-generated',
   outcome:'accepted',reviewed_digest:generatedReview.review_sha256},path.join(work,'C14-service-generated-decision.json'));
  generatedAuth=await createGenericAuthFixture(binding.owner,generatedHandle,{ownedDirectory:path.join(work,'C14-generated-auth'),
   subjects:[{id:'c14-generated-subject',evidence:'c14-generated-evidence',session:'c14-generated-session'}],grants:[]});
  generatedRuntime=await runtimeModules.get('ReviewDeskService').openGeneratedServiceArtifactRuntime(emitter,artifact,{storePath:path.join(work,'C14-generated-producer.sqlite'),
   mode:'create',nativeAuth:generatedAuth.nativeAuth,externalWritePort:port},binding,generatedHandle);
  generatedRelay=runtimeModules.get('ReviewDeskService').openGeneratedServiceArtifactRelay(emitter,artifact,generatedRuntime);
  assert.equal(generatedRelay.kind,'original-generic-event-relay-owner/v1-candidate');
  assert.throws(()=>emitter.bindGeneratedApplication(artifact,'Other.ForgedEntry'),error=>error.diagnostics?.[0]?.code==='UnknownReference');
  const receiver=inventory.services.find(service=>service.service==='AuditService'),receiverModule=path.join(output,receiver.directory,'service.mjs');
  const original=readFileSync(receiverModule,'utf8');
  const sameSizeChange=(original[0]==='x'?'y':'x')+original.slice(1);
  assert.equal(Buffer.byteLength(sameSizeChange),Buffer.byteLength(original));
  writeFileSync(receiverModule,sameSizeChange);
  assert.throws(()=>emitter.inspect(artifact),error=>error.diagnostics?.[0]?.code==='StaleOwner');
  await assert.rejects(runtimeModules.get('ReviewDeskService').openGeneratedServiceArtifactRuntime(emitter,artifact,{}),
   error=>error.diagnostics?.[0]?.code==='StaleOwner');
  unlinkSync(receiverModule);
  assert.throws(()=>emitter.inspect(artifact));
  writeFileSync(receiverModule,original);
  assert.throws(()=>emitter.inspect(artifact),error=>error.diagnostics?.[0]?.code==='StaleOwner');
 }finally{generatedRelay?.close();relay?.close();if(generatedRuntime)await generatedRuntime.close();if(consumerRuntime)await consumerRuntime.close();if(producerRuntime)await producerRuntime.close();if(generatedAuth)await generatedAuth.close();if(auth)await auth.close();if(generatedHandle)try{binding?.owner.dispose(generatedHandle);}catch{}if(source)try{sdk.dispose(source);}catch{}rmSync(work,{recursive:true,force:true});}
});

test('C14 joins every Workflow-required generated Entry to the original worker owner',async()=>{
 const root=workflowFixture(),work=path.dirname(root),sdk=createGenericCompositionOwner();
 const peerRequests=[],exchanges=[];
 const peerScript=`const {createServer}=require('node:http');const target=process.argv[1],body=process.argv[2];const server=createServer((request,response)=>{process.send({kind:'request',method:request.method,url:request.url});if(request.method!=='GET'||request.url!==target){response.writeHead(404);response.end('{}');return;}response.writeHead(200,{'content-type':'application/json'});response.end(body);});server.listen(0,'127.0.0.1',()=>process.send({kind:'ready',port:server.address().port}));process.on('message',message=>{if(message==='close')server.close(()=>process.exit(0));});`;
 const peer=spawn(process.execPath,['-e',peerScript,oracle.provider_target,JSON.stringify(oracle.provider_response)],
  {stdio:['ignore','ignore','inherit','ipc']});
 peer.on('message',event=>{if(event?.kind==='request')peerRequests.push([event.method,event.url]);});
 let source,auth,producerSetup,consumerSetup,producerRuntime,consumerRuntime,relay,journalDb,binding,generatedHandle,completed=false;
 try{
  const ready=await Promise.race([
   new Promise((resolve,reject)=>{const onMessage=event=>{if(event?.kind==='ready'){peer.off('message',onMessage);resolve(event);}};peer.on('message',onMessage);peer.once('error',reject);}),
   once(peer,'exit').then(()=>{throw Error('controlled GET peer exited before ready');})
  ]);
  writeFileSync(path.join(root,'contracts/external-config.json'),JSON.stringify({
   schema_version:'craft.generic-external-read-config/v1-candidate',
   bindings:[{binding:oracle.configuration_binding,origin:`http://127.0.0.1:${ready.port}`}]
  })+'\n');
  source=await sdk.prepare({sourcePath:path.join(root,'business.alch'),
   additionalSourcePaths:[path.join(root,'audit-service.alch')],
   profilePath:path.join(root,'contracts/selected-profile.json'),
   externalProfilePath:path.join(root,'contracts/external-profile.json'),
   externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
  const review=sdk.review(source,'C14-worker-assembly');
  sdk.accept(source,{decision_id:'C14-worker-assembly',owner:'C14-worker-assembly',
   outcome:'accepted',reviewed_digest:review.review_sha256},path.join(work,'C14-worker-decision.json'));
  const checked=requireGenericWorkflowRuntime(sdk,source).contract;
  const required=[...new Set([checked.start_entry,...checked.steps.flatMap(step=>[
   step.entry,...(step.compensation_entry?[step.compensation_entry]:[])])])];
  const emitter=createGenericServiceArtifactOwner(sdk,source);
  const artifact=emitter.emit({outputDirectory:path.join(work,'C14-worker-services'),entries:required});
  const inventory=emitter.inspect(artifact);
  assert.ok(required.includes(oracle.root_entry),'the checked producer Entry must be emitted for V4 relay');
  binding=emitter.bindGeneratedApplication(artifact,oracle.root_entry);
  generatedHandle=await binding.owner.prepare();
  assert.equal(binding.owner.inspect(generatedHandle).transaction_contract.schema_version,
   'craft.generic-transaction-application/v4-candidate');
  assert.equal(binding.owner.inspect(generatedHandle).transaction_contract.admission_mode,'event-handoff-entry');
  const generatedReview=binding.owner.review(generatedHandle,'C14-worker-generated');
  binding.owner.accept(generatedHandle,{decision_id:'C14-worker-generated',owner:'C14-worker-generated',
   outcome:'accepted',reviewed_digest:generatedReview.review_sha256},path.join(work,'C14-worker-generated-decision.json'));
  const generatedChecked=requireGenericWorkflowRuntime(binding.owner,generatedHandle).contract;
  assert.equal(generatedChecked.workflow,checked.workflow);
  assert.deepEqual([generatedChecked.start_entry,...generatedChecked.steps.flatMap(step=>[
   step.entry,...(step.compensation_entry?[step.compensation_entry]:[])])].sort(),[...required].sort());
  assert.ok(required.every(entry=>inventory.services.some(service=>service.entries.some(row=>row.entry===entry))));
  const ownerService=inventory.services.find(service=>service.service===checked.service);
  const graph=JSON.parse(readFileSync(path.join(work,'C14-worker-services',ownerService.directory,'service-system-graph.json'),'utf8'));
  assert.ok(graph.nodes.some(node=>node.id==='worker:'+checked.workflow&&node.required_entries_covered));
  for(const requiredEntry of required){
   const node=graph.nodes.find(node=>node.id==='entry:'+requiredEntry);
   assert.ok(node&&node.artifact);
   assert.ok(readFileSync(path.join(work,'C14-worker-services',node.artifact),'utf8').includes('createGeneratedApplicationOwner'));
  }
  assert.equal(inventory.complete_application,false);
  assert.ok(inventory.missing_complete_application_classes.includes('workflow-worker-runtime-verification'));
  const customer='c14-worker-customer',operator='c14-worker-operator';
  auth=await createGenericAuthFixture(binding.owner,generatedHandle,{ownedDirectory:path.join(work,'C14-worker-auth'),
   subjects:[{id:customer,evidence:'c14-customer-evidence',session:'c14-customer-session'},
    {id:operator,evidence:'c14-operator-evidence',session:'c14-operator-session'}],
   grants:[{subject:customer,entry:checked.start_entry},
    ...[checked.steps[0].entry,checked.steps[0].compensation_entry,checked.steps[1].entry,
     'ReviewDesk.ReadStoredRequestEntry','ReviewDesk.ReadWorkflowReservationEntry'].map(entry=>({subject:operator,entry}))],
   sessionTtlSeconds:7200});
  producerSetup=await prepareGenericFixtureRuntime(binding.owner,generatedHandle,{service:checked.service,
   ownedDirectory:path.join(work,'C14-worker-producer'),nativeAuth:auth.nativeAuth});
  const rows=JSON.parse(readFileSync(path.join(c10Fixture,'fixture-rows.json'),'utf8'));
  for(const row of rows.rows)if(row.value?.value)row.value.value.providerCurrency='USD';
  loadGenericFixture(producerSetup.fixture,wire(rows));await producerSetup.runtime.close();producerSetup=null;
  consumerSetup=await prepareGenericFixtureRuntime(binding.owner,generatedHandle,{service:'AuditService',
   ownedDirectory:path.join(work,'C14-worker-consumer'),nativeAuth:auth.nativeAuth});
  loadGenericFixture(consumerSetup.fixture,wire({schema_version:'craft.generic-fixture-rows/v1-candidate',rows:[]}));
  await consumerSetup.runtime.close();consumerSetup=null;
  const port={async exchange(request){
   exchanges.push(request.path);
   const body=JSON.parse(Buffer.from(request.body).toString('utf8'));
   return {status:200,headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},
    body:wire({...body,status:'Captured',providerReference:'receipt-'+body.orderId})};
  }};
  producerRuntime=await emitter.openServiceRuntime(artifact,checked.service,{storePath:path.join(work,'C14-worker-producer','store.sqlite'),
   mode:'reopen',nativeAuth:auth.nativeAuth,externalWritePort:port},binding,generatedHandle);
  consumerRuntime=await emitter.openServiceRuntime(artifact,'AuditService',{storePath:path.join(work,'C14-worker-consumer','store.sqlite'),mode:'reopen',nativeAuth:auth.nativeAuth},binding,generatedHandle);
  auth.bindReceiver(consumerRuntime,checked.steps[2].entry);
  journalDb=new DatabaseSync(':memory:');
  const journalStoreId='C14.worker.assembly';
  const journal=new GenericWorkflowStore(journalDb,{store_id:journalStoreId,owner_service:checked.service,
   compatibility_sha256:workflowCompatibilitySha256(generatedChecked)});
  assert.throws(()=>emitter.createServiceWorkflowWorker(artifact,checked.service,{runtime:consumerRuntime,
   receiver:producerRuntime,journal,journal_store_id:journalStoreId,actors:new Map()}),
   error=>error.diagnostics?.[0]?.code==='ForeignOwner');
  const actors=new Map();
  actors.set(checked.start_entry,auth.actor(producerRuntime,customer,checked.start_entry));
  for(const entry of [checked.steps[0].entry,checked.steps[0].compensation_entry,checked.steps[1].entry])
   actors.set(entry,auth.actor(producerRuntime,operator,entry));
  const worker=emitter.createServiceWorkflowWorker(artifact,checked.service,{runtime:producerRuntime,
   receiver:consumerRuntime,journal,journal_store_id:journalStoreId,actors});
  assert.equal(typeof worker.scheduleStart,'function');assert.equal(worker.claimNext(1000),null);
  const workerModule=await import(pathToFileURL(path.join(work,'C14-worker-services',
   inventory.services.find(service=>service.service===checked.service).directory,'worker.mjs')).href);
  assert.deepEqual(workerModule.requiredEntryIds,[...required].sort());
  const generatedWorker=workerModule.createGeneratedServiceWorkflowWorker(emitter,artifact,{runtime:producerRuntime,
   receiver:consumerRuntime,journal,journal_store_id:journalStoreId,actors});
  assert.equal(typeof generatedWorker.advance,'function');
  assert.equal(generatedWorker.claimNext(1000),null);
  const started=await generatedWorker.scheduleStart(canonicalJson(oracle.operation_input),'c14-generated-start');
  assert.equal(started.result.ok,true,JSON.stringify(started.result));
  let claim=generatedWorker.claimNext(300000);assert.ok(claim);
  let progress=await generatedWorker.advance(claim);assert.equal(progress.state,'step-committed',JSON.stringify(progress));
  claim=progress.active_claim;assert.ok(claim);
  progress=await generatedWorker.advance(claim);assert.equal(progress.state,'step-committed',JSON.stringify({progress,peerRequests,exchanges,
   history:generatedWorker.inspect(started.instance_sha256).history.slice(-6)}));
  claim=progress.active_claim;assert.ok(claim);
  progress=await generatedWorker.advance(claim);assert.equal(progress.state,'waiting-event',JSON.stringify(progress));
  assert.deepEqual(exchanges,['/v1/capture']);
  assert.deepEqual(peerRequests,[['GET',oracle.provider_target]]);
  const providerCommit=generatedWorker.inspect(started.instance_sha256).history.findLast(row=>
   row.step_index===1&&JSON.parse(row.commitment_json).kind==='prepare-step');
  assert.ok(providerCommit);
  const providerTuple=JSON.parse(providerCommit.commitment_json).command_tuple_sha256;
  relay=emitter.openServiceRelay(artifact,checked.service,producerRuntime);
  const eventClaim=relay.claimWorkflowEvent(checked.steps[2].event_binding,providerTuple,300000);
  assert.ok(eventClaim);
  const delivered=await relay.deliver(eventClaim,consumerRuntime);
  assert.equal(delivered.kind,'committed',JSON.stringify(delivered));
  await relay.ack(eventClaim,delivered.receipt);
  assert.equal(relay.claimWorkflowEvent(checked.steps[2].event_binding,providerTuple,300000),null);
  claim=withAdvancedClock(300001,()=>generatedWorker.claimNext(300000));assert.ok(claim);
  progress=await generatedWorker.advance(claim);assert.equal(progress.state,'step-committed',JSON.stringify(progress));
  claim=progress.active_claim;assert.ok(claim);
  progress=await generatedWorker.advance(claim);assert.equal(progress.state,'completed',JSON.stringify(progress));
  assert.equal(generatedWorker.inspect(started.instance_sha256).state,'completed');
  assert.deepEqual(exchanges,['/v1/capture']);
  const receiverDb=new DatabaseSync(path.join(work,'C14-worker-consumer','store.sqlite'));
  try{assert.equal(receiverDb.prepare('SELECT count(*) AS n FROM _craft_event_inbox_v1').get().n,1);}
  finally{receiverDb.close();}
  completed=true;
 }finally{relay?.close();journalDb?.close();if(consumerRuntime)await consumerRuntime.close();if(producerRuntime)await producerRuntime.close();if(consumerSetup?.runtime)await consumerSetup.runtime.close();if(producerSetup?.runtime)await producerSetup.runtime.close();if(auth)await auth.close();if(generatedHandle)try{binding?.owner.dispose(generatedHandle);}catch{}if(source)try{sdk.dispose(source);}catch{}if(peer.exitCode===null){peer.send('close');await once(peer,'exit');}if(completed||process.env.C14_PRESERVE_FAILED_DIAGNOSTIC!=='1')rmSync(work,{recursive:true,force:true});else console.error('C14 preserved diagnostic fixture:',work);}
});
