/** Generated input integration only: original native bootstrap, source/model
 * factories and Workflow remain the execution owners.
 * Open Questions: README.md#open-questions.
 */
import {readFileSync,lstatSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {randomUUID} from 'node:crypto';
import {types} from 'node:util';
import * as core from '@domainspec-v2/cli/generic';
import {assert,capture,canonical,sha256,freeze} from '../shared.mjs';
import {validateApplicationProfile,applicationSelectors} from './compiler.mjs';
import {createApplicationAccess} from './access.mjs';
import {createApplicationSourceGateway} from './gateway.mjs';
import {createApplicationQuerySource} from './query-sources.mjs';
import {createApplicationModelResource,createApplicationProposalStage,preloadApplicationNativeModule} from './model.mjs';
import {createApplicationObservations} from './observations.mjs';
import {createApplicationWorkflow} from './runtime.mjs';

const within=(root,file)=>{const rel=path.relative(root,file);return rel!==''&&!path.isAbsolute(rel)&&rel!=='..'&&!rel.startsWith('..'+path.sep);};
function physical(root,relative){assert(typeof relative==='string'&&!path.isAbsolute(relative)&&!relative.includes('\\')&&relative.split('/').every(v=>v&&v!=='.'&&v!=='..'),'InvalidContract','contained generated artifact path');const file=path.resolve(root,relative);assert(within(root,file)&&realpathSync(file)===file&&lstatSync(file).isFile(),'InvalidContract','physical original generated artifact');return file;}
function readPinned(file,retainBytes=false){const stat=lstatSync(file,{bigint:true});assert(stat.isFile()&&!stat.isSymbolicLink()&&stat.nlink===1n&&stat.size<=16777216n,'ResourceLimit','bounded original generated artifact');const bytes=readFileSync(file);assert(BigInt(bytes.length)===stat.size,'StaleOwner','generated artifact changed while read');return {file,sha256:sha256(bytes),byteLength:bytes.length,...(retainBytes?{bytes}:{})};}
const same=(a,b,label)=>assert(canonical(a)===canonical(b),'ForeignOwner',label);
// Original host owners contain methods and Maps. Validate their option container
// without serializing or copying those branded resources into inert JSON.
function preferenceSourceOptions(value){assert(value&&typeof value==='object'&&!types.isProxy(value)&&Object.getPrototypeOf(value)===Object.prototype,'InvalidContract','plain original Query resource options');const descriptors=Object.getOwnPropertyDescriptors(value),keys=Reflect.ownKeys(descriptors);assert(keys.every(key=>typeof key==='string'&&['inputs','releaseAuthority','adapterId','subject'].includes(key)&&descriptors[key].enumerable&&Object.hasOwn(descriptors[key],'value'))&&['inputs','releaseAuthority'].every(key=>Object.hasOwn(descriptors,key)),'InvalidContract','closed original Query resource fields');return Object.fromEntries(keys.map(key=>[key,descriptors[key].value]));}


/** resources are original host resources, never caller-created authority JSON.
 * This function generates no grants and starts no listener/background worker.
 * mode selects the original application-store mode; resources.journal.mode may
 * explicitly select a different original journal mode after partial startup.
 * The caller supplies its existing private state parent. Local acceptance notes
 * live there; the original Workflow driver alone creates its journal directory. */
export async function openGeneratedApplication({directory,resources,mode='reopen',expectedMetadataSha256}){
 assert(typeof directory==='string'&&path.isAbsolute(directory),'InvalidContract','absolute generated application directory');directory=path.resolve(directory);
 assert(realpathSync(directory)===directory&&lstatSync(directory).isDirectory(),'InvalidContract','physical generated application directory');assert(resources&&typeof resources==='object'&&!Array.isArray(resources)&&['create','reopen'].includes(mode),'InvalidContract','existing host resources and explicit runtime mode');
 const workflowMode=resources.journal?.mode??mode;assert(['create','reopen'].includes(workflowMode),'InvalidContract','explicit original workflow journal mode');
 const journalDirectory=resources.journal?.directory;assert(typeof journalDirectory==='string'&&path.isAbsolute(journalDirectory)&&path.normalize(journalDirectory)===journalDirectory&&journalDirectory!==directory&&!within(directory,journalDirectory),'InvalidContract','private journal outside captured application');
 const metadataFile=physical(directory,'profile-inputs.json'),metadataPin=readPinned(metadataFile,true);
 assert(typeof expectedMetadataSha256==='string'&&/^[a-f0-9]{64}$/.test(expectedMetadataSha256)&&metadataPin.sha256===expectedMetadataSha256,'StaleOwner','generated bootstrap metadata identity');
 const metadata=JSON.parse(new TextDecoder('utf8',{fatal:true}).decode(metadataPin.bytes));delete metadataPin.bytes;
 if(metadata.schema==='craft.generated-service-inputs/v1'){const {openGeneratedServiceApplication}=await import('./service-bootstrap.mjs');return openGeneratedServiceApplication({directory,resources,mode,expectedMetadataSha256});}
 if(metadata.schema==='craft.generated-knowledge-inputs/v1'){const {openGeneratedKnowledgeApplication}=await import('./knowledge-bootstrap.mjs');return openGeneratedKnowledgeApplication({directory,resources,mode,expectedMetadataSha256});}
 assert(metadata.schema==='craft.generated-application-inputs/v1','UnsupportedCapability','generated application input metadata');
 assert(Array.isArray(metadata.files)&&metadata.files.length>0&&metadata.files.length<=1024,'ResourceLimit','bounded generated input inventory');
 const pins=[metadataPin],names=new Set();let aggregateBytes=metadataPin.byteLength;for(const f of metadata.files){assert(f&&typeof f.path==='string'&&/^[a-f0-9]{64}$/.test(f.sha256)&&!names.has(f.path),'InvalidContract','unique generated artifact inventory');names.add(f.path);const pin=readPinned(physical(directory,f.path));aggregateBytes+=pin.byteLength;assert(aggregateBytes<=67108864,'ResourceLimit','bounded generated application aggregate');same(pin.sha256,f.sha256,'generated artifact identity');pins.push(pin);}
 const profile=validateApplicationProfile(metadata.profile),selectors=applicationSelectors(profile),env=metadata.environment;
 same(selectors,metadata.selectors,'generated selector identity');assert(profile.sourceSelection&&metadata.query&&metadata.inference&&metadata.provider&&metadata.native,'InvalidContract','complete generated source/native input closure');
 const runtimeApplication=metadata.architecture?.runtimeApplication??'generated/application.mjs';assert(names.has(runtimeApplication),'InvalidContract','selected runtime application belongs to pinned inventory');
 if(metadata.architecture){assert(['EntryModules','ServiceAssembly'].includes(metadata.layout)&&metadata.architecture.layout===metadata.layout&&typeof metadata.architecture.directory==='string'&&runtimeApplication.startsWith(metadata.architecture.directory+'/'),'InvalidContract','selected original layout runtime application');const workflow=metadata.architecture.workflowIntegration;if(workflow)assert(workflow.owner==='createApplicationWorkflow'&&workflow.service_facade_complete_application===false&&/^[a-f0-9]{64}$/.test(workflow.contract_sha256),'InvalidContract','original application workflow integration provenance');}
 const artifactKey=metadata.native.name+'@'+metadata.native.version,artifacts=resources.artifacts;
 assert(artifacts instanceof Map&&artifacts.has(artifactKey),'InvalidContract','captured original native artifacts');const artifact=artifacts.get(artifactKey),native=core.inspectGenericNativeProfileArtifact(artifact);same({name:native.name,version:native.version,sha256:native.sha256},metadata.native,'exact generated native package');
 assert(resources.actorIssuer&&typeof resources.actorIssuer.actor==='function'&&typeof resources.workerSubject==='string'&&typeof resources.customerSubject==='string','InvalidContract','existing original host actor issuer and named principals');
 const release=resources.release,documents=resources.documents?.port??resources.documents,modelOptions=resources.model;
 assert(release?.port?.abi==='source-release-port/v1'&&release.authority&&documents?.abi==='craft.document-authority/v1','ForeignOwner','original source release and document resources');
 assert(modelOptions&&modelOptions.client&&modelOptions.resource&&modelOptions.exposure&&typeof modelOptions.path==='string','InvalidContract','original model resource/client/exposure configuration');
 const expectedInference=metadata.inference.inferenceOptions,modelResource=capture(modelOptions.resource);
 same({model:modelResource.model,mode:modelResource.mode,tenant:modelResource.tenant,application:modelResource.application},{model:expectedInference.target.model_or_harness,mode:expectedInference.mode,tenant:profile.scope,application:profile.id},'model resource/identity');
 assert(modelResource.timeoutMs===expectedInference.bounds.deadline_ms&&modelResource.maxOutputTokens<=modelResource.maxTokens&&modelResource.maxTokens>0,'ForeignOwner','selected model deadline and token bounds');
 assert(typeof modelOptions.client.baseURL==='string','InvalidContract','selected model client public destination');same(modelOptions.client.baseURL.replace(/\/$/,''),expectedInference.target.destination.replace(/\/$/,''),'model transport destination');
 assert(modelOptions.identity&&typeof modelOptions.identity==='object','InvalidContract','selected model public identity/budgets');same(modelOptions.identity,env.inference,'selected model public identity/budgets');
 assert(resources.nativeResources instanceof Map&&resources.nativeResources.has(metadata.provider.resourceId),'InvalidContract','original native composition resources');
 const providerResource=resources.nativeResources.get(metadata.provider.resourceId);same(providerResource?.connector?.account,env.crm.account,'selected CRM account');same(providerResource?.dispatch?.policy?.maxAttempts??3,env.effect.maxAttempts,'selected provider attempt budget');assert(providerResource?.release===release,'ForeignOwner','same original source release owner');
 let composition=resources.composition,handle=resources.handle,runtime=resources.runtime,installed,query,observations=resources.observations,model,host,exposure,app,preloaded;
 const ownComposition=!composition,ownRuntime=!runtime,ownObservations=!observations;let closed=false,closing,opened=false;const activeCalls=new Set(),preferenceSources=new Set();
 const pinCurrent=()=>{assert(!closed,'StaleOwner','generated application closed');for(const p of pins)same(readPinned(p.file).sha256,p.sha256,'generated inputs changed');core.assertGenericNativeProfileArtifact(artifact);};
 const current=()=>{pinCurrent();if(opened){composition.assertCurrent(handle);runtime.assertCurrent();installed.assertCurrent();model.assertCurrent();}};
 const track=operation=>{assert(!closing&&!closed,'StaleOwner','generated application closing');const pending=(async()=>{current();const result=await operation();current();return result;})();activeCalls.add(pending);pending.then(()=>activeCalls.delete(pending),()=>activeCalls.delete(pending));return pending;};
 async function cleanup(){const errors=[];const attempt=async fn=>{try{await fn();}catch(e){errors.push(e);}};if(app)await attempt(()=>app.close());if(host)await attempt(()=>host.close());if(model)await attempt(()=>model.close());if(exposure)await attempt(()=>exposure.close());if(ownObservations&&observations)await attempt(()=>observations.close());if(preloaded)await attempt(()=>preloaded.close?.());for(const source of preferenceSources)await attempt(()=>source.close());preferenceSources.clear();if(query)await attempt(()=>query.close());if(installed)await attempt(()=>installed.close());if(ownRuntime&&runtime)await attempt(()=>runtime.close());if(ownComposition&&composition&&handle)await attempt(()=>composition.dispose(handle));if(errors.length)throw new AggregateError(errors,'Generated application original-owner cleanup failed');}
 try{
  pinCurrent();assert((composition&&handle)||(!composition&&!handle),'InvalidContract','borrow complete original application owner/handle or reopen generated bundle');
  if(!composition){const generated=await import(pathToFileURL(physical(directory,runtimeApplication)).href);assert(typeof generated.createGeneratedApplicationOwner==='function','UnsupportedCapability','original generated application factory');composition=generated.createGeneratedApplicationOwner();handle=await composition.prepare();const acceptanceParent=path.dirname(journalDirectory),parentStat=lstatSync(acceptanceParent);assert(realpathSync(acceptanceParent)===acceptanceParent&&parentStat.isDirectory()&&!parentStat.isSymbolicLink()&&(parentStat.mode&0o077)===0,'InvalidContract','existing private state parent for local acceptance');const reviewer='generated-profile-host',review=composition.review(handle,reviewer);composition.accept(handle,{decision_id:'generated-runtime-local-acceptance',owner:reviewer,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(acceptanceParent,'local-open-'+randomUUID()+'.json'));}
  composition.assertCurrent(handle);const original=composition.inspect(handle),source=original.authored_input?.primary_source;assert(source&&source.sha256===sha256(readFileSync(physical(directory,'generated/model/business.alch'))),'ForeignOwner','same original generated business source');
  if(!runtime){assert(resources.nativeAuth&&typeof resources.storePath==='string'&&path.isAbsolute(resources.storePath),'InvalidContract','existing native Auth and private store');runtime=await composition.openRuntime(handle,{service:profile.service,storePath:resources.storePath,mode,nativeAuth:resources.nativeAuth});}
  const actor=(subject,entry)=>{current();return resources.actorIssuer.actor(runtime,subject,entry);};
  const access=createApplicationAccess({composition,handle,runtime,profile,...(resources.credentialLease?{credentialLease:resources.credentialLease}:{})});
  const worker=entry=>resources.actorIssuer.actor(runtime,resources.workerSubject,entry),customer=entry=>resources.actorIssuer.actor(runtime,resources.customerSubject,entry);
  const bootstrap=await import(pathToFileURL(physical(directory,metadata.provider.compositionDirectory+'/native-bootstrap.mjs')).href);
  installed=await bootstrap.install({artifacts,resources:resources.nativeResources,applicationArtifact:artifact});
  const inspected=installed.inspectProviders(),selected=inspected.find(row=>row.alias===metadata.provider.alias);assert(selected&&selected.capability_sha256===metadata.provider.capability_sha256,'ForeignOwner','exact generated source provider selection');
  query=await createApplicationQuerySource({composition,handle,runtime,actor:worker(metadata.query.entry),entry:metadata.query.entry,releaseAuthority:release.authority,adapterId:metadata.query.adapterId,subjectInputs:metadata.query.subjectInputs,resultView:metadata.query.resultView});
  const gateway=createApplicationSourceGateway({...profile.sourceSelection,access,documents,release,adapters:new Map([[metadata.query.adapterId,query]])});
  if(!observations)observations=createApplicationObservations();const observationBinding=observations.createBinding();
  preloaded=await preloadApplicationNativeModule({artifact,realization:metadata.inference.selection.realizations[0]});
  model=createApplicationModelResource({access,gateway,artifact,preloaded,entries:[selectors.stages[0].entry],bindingId:metadata.inference.bindingId,policyId:profile.id+'-model',resourceId:modelResource.id,createController(assertCurrent,namespace){
   exposure=namespace.createExposureLedger({path:modelOptions.exposure.path,releasePort:release.port,observer:observationBinding.observer});
   assert(Array.isArray(modelOptions.exposure.allocations)&&modelOptions.exposure.allocations.length>0&&modelOptions.exposure.allocations.length<=100,'InvalidContract','bounded selected operator exposure allocations');for(const allocation of modelOptions.exposure.allocations){assert(allocation.tenant===profile.scope&&allocation.application===profile.id,'ForeignOwner','selected exposure allocation scope');exposure.authority.configureAllocation(allocation);}
   return observationBinding.attach(namespace.createInferenceRuntime({path:modelOptions.path,client:modelOptions.client,resource:modelResource,sourceRelease:release.port,exposure:exposure.port,observer:observationBinding.observer,assertCurrent,policy:modelOptions.policy??{timeoutMs:expectedInference.bounds.deadline_ms}}));
  }});
  host=core.createGenericNativeCapabilityHost(composition,handle,{runtime,bindings:new Map([[metadata.inference.bindingId,model.configuration]])});
  const proposal=createApplicationProposalStage({resource:model,host,gateway,capability_sha256:metadata.inference.capability_sha256}),providers=await installed.createProviderStages({access,gateway}),provider=providers.get(metadata.provider.alias);
  assert(provider?.capability_sha256===metadata.provider.capability_sha256,'ForeignOwner','same installed provider stage identity');
  const actors=new Map([[selectors.start,customer(selectors.start)],...selectors.stages.flatMap(s=>[[s.entry,worker(s.entry)],[s.continuation,worker(s.continuation)]])]);
  app=await createApplicationWorkflow({composition,handle,runtime,profile,actors,handlers:new Map([[metadata.inference.bindingId,proposal],[metadata.provider.bindingId,provider]]),journal:{...resources.journal,mode:workflowMode},observations,observationRuntime:model});
  opened=true;current();
  return Object.freeze({...app,runtime,access,actor,assertCurrent:current,createPreferenceSource(options){return track(async()=>{const selected=preferenceSourceOptions(options);assert(selected.inputs instanceof Map&&selected.releaseAuthority&&(selected.adapterId===undefined||selected.adapterId==='crm-preferences')&&(selected.subject===undefined||typeof selected.subject==='string'),'InvalidContract','original grouped preference source selection');let source;try{source=await createApplicationQuerySource({composition,handle,runtime,actor:actor(selected.subject??resources.workerSubject,metadata.query.entry),entry:metadata.query.entry,releaseAuthority:selected.releaseAuthority,adapterId:selected.adapterId??'crm-preferences',inputs:selected.inputs});current();preferenceSources.add(source);return source;}catch(error){source?.close();throw error;}});},inspectGeneration(){current();return freeze(capture({schema:metadata.schema,profile,query:metadata.query,native:metadata.native,provider:metadata.provider,architecture:metadata.architecture??null,qualification:'original-owner-local-runtime;no-provider-model-production-qualification'}));},approvalBinding(person,work){return track(async()=>{const snapshot=await gateway.load(person,work);return gateway.binding(snapshot);});},submit(request,person){return track(()=>app.submit(request,person??customer(selectors.start)));},advance(options){return track(()=>app.advance(options));},status(person,key){return track(()=>app.status(person,key));},async close(){if(closing)return closing;closing=(async()=>{await Promise.allSettled([...activeCalls]);closed=true;return cleanup();})();return closing;}});
 }catch(error){closed=true;try{await cleanup();}catch(cleanupError){throw new AggregateError([error,cleanupError],'Generated application open and cleanup failed',{cause:error});}throw error;}
}
