/** Shared actual-owner fixtures for checked source service generation.
 * SDK and provider data are explicitly recorded fixtures. Runtime, Auth, source
 * custody, parser, retrieval and Workflow stay under their original owners.
 * Open Questions: goals/plans/craft-service-profile-extensions-2026-11-02/DESIGN.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,cpSync,copyFileSync,readFileSync,writeFileSync,rmSync,renameSync,existsSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {profileEngine} from '@domainspec-v2/cli';
import {captureGenericNativeProfileArtifact,generateGenericNativeVectorCodec} from '@domainspec-v2/cli/generic';
import {createGenericAuthFixture,prepareGenericFixtureRuntime} from '@domainspec-v2/cli/generic/testing';
import {applicationSelectors} from '@craft/ai-profiles/application';
import * as knowledge from '@craft/ai-profiles/application/knowledge';
import {createSourceReleaseService} from '@craft/ai-profiles/source-release';
import {createDocumentAuthority} from '@craft/ai-profiles/documents';
import {createDocumentParser} from '@craft/ai-profiles/parser';
import {createEmbeddedRetrieval,createRetrievalProfile} from '@craft/ai-profiles/retrieval';
import {createInferenceRuntime} from '@craft/ai-profiles/model';
import {createExposureLedger} from '@craft/ai-profiles/model/exposure';

const installedRoot=process.env.CRAFT_PROFILE_INPUT_INSTALLED_ROOT?path.resolve(process.env.CRAFT_PROFILE_INPUT_INSTALLED_ROOT):null;
const repository=installedRoot??fileURLToPath(new URL('../../../',import.meta.url));
const coreRoot=process.env.CRAFT_DOMAIN_CORE_ROOT?path.resolve(process.env.CRAFT_DOMAIN_CORE_ROOT):(installedRoot?path.join(installedRoot,'node_modules/@domainspec-v2/cli'):path.join(repository,'craft/projects/domainspec-v2/impl/cli'));
const frontend=installedRoot?path.join(installedRoot,'node_modules/@cyberalchemy/alchlang'):path.join(repository,'language/capabilities/alchlang/plans/general-compiler-v1/implementation');
const libraryRoot=process.env.CRAFT_KNOWLEDGE_PROFILE_LIBRARY_ROOT?path.resolve(process.env.CRAFT_KNOWLEDGE_PROFILE_LIBRARY_ROOT):path.join(installedRoot?coreRoot:path.join(repository,'craft/projects/domainspec-v2/impl/cli'),'examples/technical-profile-source');
const selectedLayout=process.env.CRAFT_KNOWLEDGE_PROFILE_LAYOUT??process.env.CRAFT_PROFILE_INPUT_LAYOUT??'ServiceAssembly';
assert.ok(['EntryModules','ServiceAssembly'].includes(selectedLayout));
const fullCases=selectedLayout==='ServiceAssembly'||process.env.CRAFT_KNOWLEDGE_PROFILE_FULL_CASES==='1';
const canonical=v=>JSON.stringify(v,(_k,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
const bytes=v=>new TextEncoder().encode(typeof v==='string'?v:canonical(v));
const json=file=>JSON.parse(readFileSync(file,'utf8'));
const publish=(file,value)=>{mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
const representation={model:'text-embedding-3-small',dimensions:1536,preprocessing:'utf8-exact-v1',space:'knowledge-fixture-1'};
const vectorGenerated=generateGenericNativeVectorCodec(1536,{id:'knowledge-profile-generated-vector',max_bytes:65536});
const vectorDecoder=await import('data:text/javascript;base64,'+Buffer.from(vectorGenerated.source).toString('base64'));
const vectorCodec={schema:vectorGenerated.schema,decode:vectorDecoder.decode};
const phase=label=>process.stderr.write('service fixture phase: '+label+'\n');
const families=[{name:'knowledge-ingestion',family:'knowledge-ingestion/domain-v1',profile:'Profiles.KnowledgeIngestionApplication',module:'KnowledgeIngestion'},{name:'permissioned-rag',family:'permissioned-rag/domain-v1',profile:'Profiles.PermissionedRagApplication',module:'PermissionedRag'}];

function fresh(t,label){
 const directory=mkdtempSync(path.join(installedRoot??tmpdir(),'knowledge-profile-'+label+'-'));
 t.after(()=>{if(process.env.CRAFT_KEEP_PROFILE_INPUT_TEST_OUTPUT==='1')t.diagnostic('Retained knowledge profile test directory '+directory);else rmSync(directory,{recursive:true,force:true});});
 return directory;
}
async function generate(t,kind,nativeDirectory,transportRoot){
 phase('generating '+kind.name);
 const reuse=JSON.parse(process.env.CRAFT_SERVICE_REUSE_GENERATED??'{}')[kind.name];
 if(reuse){const previous=path.resolve(reuse),directory=fresh(t,'reused-'+kind.name),state=path.join(directory,'state'),output=path.join(previous,'relocated-generated');mkdirSync(state,{mode:0o700});const metadata=json(path.join(output,'profile-inputs.json'));assert.equal(metadata.profile.businessInputContract,kind.family);t.diagnostic('Focused runtime debugging reuses already-generated '+output+'; no new formation/graph evidence');return {directory,state,output,metadata,profile:metadata.profile,selectors:applicationSelectors(metadata.profile),environment:json(path.join(libraryRoot,kind.name+'-application-example/environment.identity.json')),kind};}

 const directory=fresh(t,kind.name),project=path.join(directory,'project'),state=path.join(directory,'state');mkdirSync(project);mkdirSync(state,{mode:0o700});
 const example=path.join(libraryRoot,kind.name+'-application-example');
 for(const name of ['business.alch','entries.alch','application.json','environment.identity.json'])copyFileSync(path.join(example,name),path.join(project,name));
 const profileLibrary=path.join(directory,'library');cpSync(libraryRoot,profileLibrary,{recursive:true});
 const manifest=path.join(profileLibrary,kind.name+'-application.profile.json'),envelope=json(manifest);envelope.selection.arguments.options.layout=selectedLayout;publish(manifest,envelope);
 mkdirSync(path.join(project,'profiles'),{recursive:true});
 const source=profileEngine.createTechnicalProfileSourceOwner();let sourceHandle;
 try{sourceHandle=source.prepare({sourceRoot:profileLibrary,manifestPath:manifest});const inspected=source.inspect(sourceHandle);assert.equal(inspected.target_consumer,'craft.application-inputs/v1');assert.equal(inspected.id,kind.profile);assert.equal(inspected.topology.family,kind.family);source.publishSelection(sourceHandle,path.dirname(path.join(project,json(path.join(project,'application.json')).applicationProfile.selection)));}finally{if(sourceHandle)source.dispose(sourceHandle);}
 if(!installedRoot){
  const dest=path.join(project,'node_modules/@craft/ai-profiles');mkdirSync(path.dirname(dest),{recursive:true});cpSync(nativeDirectory,dest,{recursive:true});
  assert.ok(transportRoot,'original locked ARE transport package');cpSync(transportRoot,path.join(project,'node_modules/@cyberalchemy/are-model-transports'),{recursive:true});
  // The locked parser dependency is beside the captured package, like npm install.
  cpSync(path.join(repository,'implementation/craft-ai-profiles/native/documents/parser/node_modules/pdfjs-dist'),path.join(project,'node_modules/pdfjs-dist'),{recursive:true});
 }
 const output=path.join(project,'generated');
 const coreLoader=path.join(directory,'core-only-loader.mjs');
 if(!installedRoot)writeFileSync(coreLoader,`import {registerHooks} from 'node:module';import {pathToFileURL} from 'node:url';const paths=${JSON.stringify({'@domainspec-v2/cli':path.join(coreRoot,'dist/index.js'),'@domainspec-v2/cli/generic':path.join(coreRoot,'dist/generic/index.js'),'@domainspec-v2/cli/generic/testing':path.join(coreRoot,'dist/generic/testing.js')})};registerHooks({resolve(specifier,context,next){return paths[specifier]?{url:pathToFileURL(paths[specifier]).href,shortCircuit:true}:next(specifier,context);}});`);
 const command=['generate-application','--project',path.join(project,'application.json'),'--out',output,'--accept-local-review','knowledge-profile-local-owner'];
 const argv=installedRoot?[path.join(frontend,'dist/generic-composition-cli.js'),...command]:['--import',path.join(frontend,'node_modules/tsx/dist/loader.mjs'),'--import',coreLoader,path.join(frontend,'src/application-profile-cli.ts'),...command];
 const env={...process.env};if(installedRoot){delete env.CRAFT_WORKING_SDK_ROOT;delete env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;}else{env.CRAFT_WORKING_SDK_ROOT=coreRoot;env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT=coreRoot;}
 const result=spawnSync(process.execPath,argv,{cwd:repository,env,encoding:'utf8',maxBuffer:33554432,timeout:900000});
 writeFileSync(path.join(directory,'generation.stdout.log'),result.stdout??'');writeFileSync(path.join(directory,'generation.stderr.log'),result.stderr??'');
 assert.equal(result.status,0,'actual paired CLI generation failed: '+(result.error?.message??'')+'\n'+(result.stderr??'').slice(-10000));
 for(const name of ['application-intent.json','application-sources.json','stage-selection.json'])for(const folder of ['','contracts'])assert.equal(existsSync(path.join(project,folder,name)),false,'no handwritten '+name);
 const relocated=path.join(directory,'relocated-generated');renameSync(output,relocated);renameSync(project,path.join(directory,'generation-inputs'));
 const metadata=json(path.join(relocated,'profile-inputs.json'));
 assert.ok(['craft.generated-knowledge-inputs/v1','craft.generated-service-inputs/v1'].includes(metadata.schema));assert.equal(metadata.profile.businessInputContract,kind.family);assert.equal(metadata.layout,selectedLayout);
 if(kind.family.startsWith('knowledge-')||kind.family.startsWith('permissioned-')){assert.equal(metadata.query,undefined);assert.equal(metadata.provider,undefined);assert.equal(metadata.profile.executionAdmission,undefined);}
 const views=json(path.join(relocated,'profile-input-system-graph.json')),bridge=json(path.join(relocated,'profile-input-business-system-bridge.json'));
 assert.ok(views.nodes.length>0&&views.edges.length>0&&bridge.links.length>0);assert.ok(bridge.links.some(link=>link.business?.startsWith(kind.module+'.')));
 if(metadata.schema==='craft.generated-service-inputs/v1'){
  const selectors=applicationSelectors(metadata.profile),admission=views.nodes.find(node=>node.kind==='original-private-execution-admission');assert.ok(admission,'original private admission node');assert.equal(admission.entry,selectors.executionAdmission);assert.equal(admission.kernel.sha256,admission.kernel_file.sha256);assert.equal(admission.implementation.path,'native/application/service-admission.mjs');
  const admissionLink=bridge.links.find(link=>link.kind==='generated-private-admission-original-entry');assert.equal(admissionLink.business,selectors.executionAdmission);assert.ok(json(path.join(relocated,admissionLink.consumer_graph)).nodes.some(node=>node.id===admissionLink.consumer&&node.entry===selectors.executionAdmission));
  if(kind.family==='invoice-draft/domain-v1'){const owners=views.nodes.filter(node=>node.kind==='original-owner-input-binding');assert.deepEqual(owners.map(node=>node.field).sort(),['proposal','subjectId']);for(const owner of owners)assert.equal(owner.input_path,'review.'+owner.field);for(const node of views.nodes.filter(node=>node.kind==='derived-field-projection'&&['review','businessApproval','businessProposal'].includes(node.group)))assert.ok(node.input_path.startsWith('review.'));}
  if(kind.family==='marketing-campaign/domain-v1'){const observation=selectors.stages.find(stage=>stage.observation).observation,link=bridge.links.find(row=>row.business===kind.module+'.MetricsObservationRequest');assert.ok(link,'actual nominal metrics DTO bridge');const observedGraph=json(path.join(relocated,link.consumer_graph));assert.ok(observedGraph.nodes.some(node=>node.id===link.consumer&&node.entry===observation));assert.notEqual(observation,selectors.evaluate);}
 }

 phase('generated and relocated '+kind.name);
 return {directory,state,output:relocated,metadata,profile:metadata.profile,selectors:applicationSelectors(metadata.profile),environment:json(path.join(example,'environment.identity.json')),kind};
}
async function artifactFor(t){
 if(process.env.CRAFT_SERVICE_REUSE_NATIVE_ROOT){const directory=path.resolve(process.env.CRAFT_SERVICE_REUSE_NATIVE_ROOT);return {directory,artifact:captureGenericNativeProfileArtifact(directory)};}
 if(installedRoot){const directory=path.join(installedRoot,'node_modules/@craft/ai-profiles');return {directory,artifact:captureGenericNativeProfileArtifact(directory)};}
 const packageHost=fresh(t,'native'),directory=path.join(packageHost,'node_modules/@craft/ai-profiles');const {stageNativePackage}=await import('./build-native-package.mjs');stageNativePackage(directory);cpSync(path.join(repository,'implementation/craft-ai-profiles/native/documents/parser/node_modules/pdfjs-dist'),path.join(packageHost,'node_modules/pdfjs-dist'),{recursive:true});
 const {buildArePackages}=await import('./build-are-packages.mjs'),built=await buildArePackages(path.join(fresh(t,'are-package'),'build'),{verify:false}),transport=built.packages.find(p=>p.name==='@cyberalchemy/are-model-transports');assert.ok(transport);
 return {directory,transportRoot:transport.root,artifact:captureGenericNativeProfileArtifact(directory)};
}
function corpus(t,{observations,initialSources}={}){
 const directory=fresh(t,'corpus'),tenant='reference-knowledge',release=createSourceReleaseService({path:path.join(directory,'release.sqlite')}),documents=createDocumentAuthority({path:path.join(directory,'documents.sqlite'),releaseAuthority:release.authority,observations}),scope=knowledge.createKnowledgeExecutionScope(),calls=[];
 let proposal={subjectId:'1',sourceVersion:'3',answer:'The warranty lasts 12 months.',citationIds:['41'],refuses:false},completionHook,embeddingHook;
 const client={baseURL:'https://api.openai.com/v1',withOptions:options=>({maxRetries:options.maxRetries,timeout:options.timeout,baseURL:'https://api.openai.com/v1',responses:{async create(body){calls.push({operation:'text.structured',body,options});const hook=completionHook;completionHook=undefined;await hook?.();return {id:'recorded-knowledge-profile-'+calls.length,model:'gpt-6-luna',status:'completed',output:[{type:'message',content:[{type:'output_text',text:canonical(proposal)}]}],usage:{input_tokens:20,output_tokens:10}};}},embeddings:{async create(body){calls.push({operation:'vector.embed',body,options});const hook=embeddingHook;embeddingHook=undefined;await hook?.();return {model:'text-embedding-3-small',data:[{index:0,embedding:[1,...Array(1535).fill(0)]}],usage:{prompt_tokens:8,total_tokens:8}};}}})};
 const exposure= createExposureLedger({path:path.join(directory,'embedding-exposure.sqlite'),releasePort:release.port});exposure.authority.configureAllocation({id:'knowledge-embedding-budget',billingAccount:'fixture-billing',tenant,application:'knowledge-embedding-reference',maxAttempts:30,maxTokens:1000000,maxCostMicros:'100000'});
 const embeddingResource={id:'knowledge-embedding',provider:'openai',account:'model-fixture',billingAccount:'fixture-billing',tenant,application:'knowledge-embedding-reference',mode:'fixture',model:'gpt-6-luna',embeddingModel:representation.model,dimensions:1536,preprocessing:representation.preprocessing,generation:representation.space,pricePolicyRevision:'fixture-price-1',maxCostMicros:'100',maxTokens:10000,maxOutputTokens:512,timeoutMs:300000};
 const embeddingRuntime=createInferenceRuntime({path:path.join(directory,'embedding-effects.sqlite'),client,resource:embeddingResource,sourceRelease:release.port,exposure:exposure.port,assertCurrent:binding=>{documents.port.assertCurrent();if(binding)scope.current().assertCurrent();return true;},policy:{timeoutMs:300000}});
 const embeddings=knowledge.createKnowledgeEmbeddingPort({path:path.join(directory,'embedding-receipts.sqlite'),inference:embeddingRuntime,codec:vectorCodec,release,documentPort:documents.port,context:scope.current,representation,policyId:'knowledge-model'});
 const parser=createDocumentParser({nodePath:process.execPath}),retrieval=createEmbeddedRetrieval({path:path.join(directory,'index.sqlite'),documentPort:documents.port,embeddingPort:embeddings,parser,profile:createRetrievalProfile({embedding:representation})}),index=knowledge.createKnowledgeIndexPort({documents:documents.port,retrieval,parser,scope:scope.current});
 const put=(id,value,{version='3',aclRevision='4',readers=['alice','5'],mediaType='text/plain'}={})=>documents.authority.put({id,tenant,version,aclRevision,readers,classifications:['internal'],mediaType,bytes:value instanceof Uint8Array?value:bytes(value)});
 for(const [id,sink,recipient,actions]of [['ingestion-egress','local:index','alice',['candidate.review','index.activate']],['rag-egress','app:answer','alice',['candidate.review','answer']]])release.authority.setPolicy({id,revision:'4',tenants:[tenant],actions,sinks:[sink],recipients:[recipient],classifications:['internal']});
 release.authority.setPolicy({id:'knowledge-model',revision:'1',tenants:[tenant],actions:['vector.embed','text.structured'],sinks:['openai'],recipients:['model-fixture'],classifications:['internal'],processingDestinations:[{sink:'openai',recipient:'model-fixture'}]});
 const fixtures=path.join(libraryRoot,'knowledge-ingestion-application-example/fixtures');
 if(initialSources!==undefined){assert.ok(Array.isArray(initialSources));assert.deepEqual(initialSources.map(row=>row.id).sort(),['knowledge-a-1','knowledge-b-1'],'explicit two-source corpus fixture');for(const source of initialSources){assert.deepEqual(Object.keys(source).sort(),['id','mediaType','readers','value','version']);assert.equal(source.version,source.id==='knowledge-a-1'?'3':'7');assert.ok(typeof source.value==='string'||source.value instanceof Uint8Array);put(source.id,source.value,{version:source.version,mediaType:source.mediaType,readers:source.readers});}}
 else{put('knowledge-a-1',readFileSync(path.join(fixtures,'document-a.pdf')),{version:'3',mediaType:'application/pdf'});put('knowledge-b-1',readFileSync(path.join(fixtures,'document-b.pdf')),{version:'7',mediaType:'application/pdf'});} 
 t.after(()=>{retrieval.close();embeddings.close();embeddingRuntime.close();exposure.close();documents.close();release.close();});
 return {directory,tenant,release,documents,scope,embeddings,index,retrieval,parser,client,calls,put,proposal(value){proposal=value;},onCompletion(hook){completionHook=hook;},onEmbedding(hook){embeddingHook=hook;}};
}
async function provision(t,f,artifact,c,{ingestion,quality}={}){
 const selected=f.metadata.architecture?.runtimeApplication??'generated/application.mjs',generated=await import(pathToFileURL(path.join(f.output,selected)).href),composition=generated.createGeneratedApplicationOwner(),handle=await composition.prepare(),review=composition.review(handle,'knowledge-fixture-host');
 composition.accept(handle,{decision_id:'knowledge-fixture-host',owner:'knowledge-fixture-host',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(f.state,'host-acceptance.json'));
 const selectors=f.selectors,entries=[...new Set([selectors.start,selectors.principal,selectors.job,selectors.stage,selectors.status,selectors.evaluate,selectors.publicEvaluate,selectors.effectEvaluate,selectors.capture,...selectors.stages.flatMap(s=>[s.entry,s.continuation,s.evaluate,s.observation])].filter(Boolean))];
 const auth=await createGenericAuthFixture(composition,handle,{ownedDirectory:path.join(f.state,'auth'),sessionTtlSeconds:7200,subjects:[{id:'alice',evidence:'alice-evidence',session:'alice-session'},{id:'stranger',evidence:'stranger-evidence',session:'stranger-session'}],grants:entries.map(entry=>({subject:'alice',entry}))});
 const runtimeState=await prepareGenericFixtureRuntime(composition,handle,{service:f.profile.service,ownedDirectory:path.join(f.state,'store'),nativeAuth:auth.nativeAuth});
 const resources={composition,handle,runtime:runtimeState.runtime,nativeAuth:auth.nativeAuth,actorIssuer:auth,workerSubject:'alice',customerSubject:'alice',storePath:runtimeState.storePath,artifacts:new Map([[f.metadata.native.name+'@'+f.metadata.native.version,artifact]]),journal:{directory:path.join(f.state,'workflow')},release:c.release,documents:c.documents.port,knowledge:{scope:c.scope,index:c.index}};
 if(ingestion){resources.knowledge.ingestion=ingestion;resources.knowledge.queryEmbeddings=c.embeddings;resources.knowledge.quality=quality;resources.knowledge.cachePath=path.join(f.state,'cache.sqlite');const inf=f.environment.inference;resources.model={client:c.client,identity:inf,path:path.join(f.state,'model-effects.sqlite'),resource:{id:f.profile.id+'-model',provider:'openai',account:'model-fixture',billingAccount:'fixture-billing',tenant:f.profile.scope,application:f.profile.id,mode:'fixture',model:inf.model,embeddingModel:representation.model,dimensions:1536,preprocessing:representation.preprocessing,generation:representation.space,pricePolicyRevision:'fixture-price-1',maxCostMicros:'100',maxTokens:10000,maxOutputTokens:512,timeoutMs:inf.deadline_ms},exposure:{path:path.join(f.state,'model-exposure.sqlite'),allocations:[{id:f.profile.id+'-model-budget',billingAccount:'fixture-billing',tenant:f.profile.scope,application:f.profile.id,maxAttempts:30,maxTokens:1000000,maxCostMicros:'100000'}]}};}
 const bootstrap=await import(pathToFileURL(path.join(f.output,'application-bootstrap.mjs')).href);let app;
 const open=async mode=>{app=await bootstrap.open({resources,mode});return app;};
 const reopen=async()=>{await app.close();app=null;return open('reopen');};
 t.after(async()=>{await app?.close();await runtimeState.runtime.close();await auth.close();composition.dispose(handle);});
 return {...f,resources,auth,composition,handle,runtime:runtimeState.runtime,open,reopen,get app(){return app;}};
}
async function submit(f,run){const response=await f.app.submit(new Request('https://fixture.test/api/'+f.profile.id+'/runs',{method:'POST',headers:{'content-type':'application/json','idempotency-key':f.profile.id+'-'+run},body:canonical({id:'1',run})}));assert.equal(response.status,200,await response.clone().text());return response.json();}
async function finish(f,scheduled,{claim,expectRejected=false}={}){let last;for(let i=0;i<12;i++){last=await f.app.advance({claim});assert.ok(last,'scheduled work available');claim=last.claim;if(['completed','rejected'].includes(last.result.kind)){assert.equal(last.result.kind,expectRejected?'rejected':'completed',canonical(last));return last;}assert.equal(last.result.kind,'advanced',canonical(last));}assert.fail('bounded original workflow did not finish');}
function originalControl(){return {subjectId:'1',objectVersion:'2',sourceVersion:'3',policyVersion:'4',recipientId:'5',inputDigest:'0'.repeat(64),outputDigest:'0'.repeat(64),manifestDigest:'0'.repeat(64),expiresAt:String(Date.now()+3600000),approved:false};}


export {generate,artifactFor,corpus,provision,submit,finish,originalControl,families,libraryRoot,selectedLayout,canonical,bytes,json,publish,representation,fresh};
