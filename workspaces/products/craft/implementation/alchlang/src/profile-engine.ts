import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,readdirSync,lstatSync,rmSync,realpathSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {resolveTypeScriptCompiler} from './function-builder.js';
import {deriveProfileSources,assertLoweredProfileSourcesCurrent} from './profile-project-input.js';
import {prepareServicePlan,planPreparedService,assertPreparedServiceCurrent,disposePreparedService} from './service-builder.js';
import {prepareApplicationFilePlan,assertPreparedApplicationFileCurrent,disposePreparedApplicationFile} from './application-file-check.js';
import {prepareBusinessApplication,prepareBusinessApplicationCallables,assertPreparedBusinessApplicationCurrent,disposePreparedBusinessApplication} from './business-application-prepare.js';
// Open questions: business application frozen matrix and installed qualification BA15/18.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
type IdentityFile={key:string;path:string};
function identityFiles(directory:string,prefix:string):IdentityFile[]{
 const result:IdentityFile[]=[];const visit=(relative:string)=>{const folder=path.join(directory,relative);for(const entry of readdirSync(folder,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){const name=relative?relative+'/'+entry.name:entry.name,file=path.join(directory,name);if(lstatSync(file).isSymbolicLink())throw Error('PROFILE_IDENTITY_SYMLINK:'+file);if(entry.isDirectory())visit(name);else if(entry.isFile())result.push({key:prefix+'/'+name,path:file});else throw Error('PROFILE_IDENTITY_FILE_KIND:'+file);}};visit('');return result;
}
export interface PreparedProfileProject {readonly snapshot:any;readonly selection:any;readonly lowered?:ReturnType<typeof deriveProfileSources>;readonly composition:any;readonly compilerPath:string;readonly workspace:string}
const preparedProjects=new WeakMap<object,{compiler:Awaited<ReturnType<typeof loadDomainSpecCompiler>>;service?:Awaited<ReturnType<typeof prepareServicePlan>>;render:Readonly<Record<string,string>>;views:any;applications:Awaited<ReturnType<typeof prepareApplicationFilePlan>>[];businessApplications:ReturnType<typeof prepareBusinessApplication>[]}>();
export async function prepareProfileProject(projectPath:string,pinnedLock?:unknown):Promise<PreparedProfileProject>{
 const compiler=await loadDomainSpecCompiler();if(!compiler.profileEngine)throw Error('PROFILE_ENGINE_PEER_REQUIRED: rebuild or install the profile-enabled Craft package');
 const compilerPath=resolveTypeScriptCompiler(compiler.binding.package_root,process.env.ALCHLANG_TYPESCRIPT_COMPILER),engine=compiler.profileEngine;
 for(const name of ['validateProfileProjectInput','profileApplicationSelections','compileRequestApplicationBindingV1','composeRequestApplicationPlanV1','prepareRequestApplicationCallable','assertBusinessApplicationPlanCurrent'] as const)if(typeof engine[name]!=='function')throw Error('PROFILE_ENGINE_PEER_CAPABILITY_REQUIRED:'+name);
 const core=compiler.binding.package_root;
 const identity={engine:[...identityFiles(path.join(core,'dist'),'craft/dist'),...identityFiles(path.join(core,'contracts'),'craft/contracts'),...identityFiles(path.join(core,'lean'),'craft/lean'),...identityFiles(path.join(root,'dist'),'alch/dist'),...identityFiles(path.join(root,'runtime-sources'),'alch/runtime-sources'),{key:'craft/package.json',path:path.join(core,'package.json')},{key:'alch/package.json',path:path.join(root,'package.json')}],tools:[...identityFiles(path.dirname(path.dirname(compilerPath)),'typescript'),{key:'node',path:realpathSync(process.execPath)}]};
 const project=engine.validateProfileProjectInput(JSON.parse(readFileSync(path.resolve(projectPath),'utf8')));
 const workspace=mkdtempSync(path.join(os.tmpdir(),'alch-profile-project-'));let service:Awaited<ReturnType<typeof prepareServicePlan>>|undefined;const applications:Awaited<ReturnType<typeof prepareApplicationFilePlan>>[]=[],additionalSources:IdentityFile[]=[],callables:any[]=[],businessApplications:ReturnType<typeof prepareBusinessApplication>[]=[];
 try{
  for(const call of project.application_calls??[]){const application=await prepareApplicationFilePlan(path.resolve(path.dirname(path.resolve(projectPath)),call.source));applications.push(application);if(!application.whole)throw Error('PROFILE_APPLICATION_WHOLE_REQUIRED: existing checked application/whole-plan carrier required');
   const appRoot=path.dirname(application.loaded.source_path);for(const relative of Object.keys(application.loaded.inputs))additionalSources.push({key:'application:'+call.id+':'+(relative===path.basename(application.loaded.source_path)?'source':relative),path:path.join(appRoot,relative)});
   callables.push(engine.prepareApplicationCallable(application.graph,application.whole.wholeApplication,application.whole.runtimeBinding.binding,call,()=>assertPreparedApplicationFileCurrent(application)));
  }
  const snapshot=(project.schema_version==='craft.profile-project/v2-candidate'?engine.loadProfileProjectV2:engine.loadProfileProject)(path.resolve(projectPath),{...identity,additionalSources},pinnedLock),selection=engine.selectProfileConfiguration(snapshot);
  let lowered:ReturnType<typeof deriveProfileSources>|undefined;const functions:any[]=[];
  if(project.public_intents.length){
   lowered=deriveProfileSources(selection.input,engine,compiler,engine.profileTechnicalSelections(selection));
   for(const [relative,body]of Object.entries(lowered.files)){const target=path.join(workspace,relative);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,body,{flag:'wx'});}
   service=await prepareServicePlan(path.join(workspace,'service.alch'));const plan=planPreparedService(service),capturedService=service;
   functions.push(...service.functions.map((fn,index)=>({intent_id:selection.input.project.public_intents[index].id,source:selection.input.project.public_intents[index].source,graph:fn.graph,artifacts:plan.functions[index]!.artifacts,assert_current:()=>assertPreparedServiceCurrent(capturedService)})));
  }
  if(selection.business_applications){
   const choices=engine.profileApplicationSelections(selection);
   for(const model of selection.business_applications.applications){const prepared=prepareBusinessApplication(selection.business_applications,model.model.id,compiler);businessApplications.push(prepared);callables.push(...prepareBusinessApplicationCallables(prepared,choices,compiler));}
  }
  const composition=engine.composeProfile(selection,functions,callables),render=engine.renderProfilePlan(composition);
  const views=engine.projectProfileViews(composition);
  const prepared=Object.freeze({snapshot,selection,...(lowered?{lowered}:{}),composition,compilerPath,workspace});preparedProjects.set(prepared,{compiler,...(service?{service}:{}),render,views,applications,businessApplications});return prepared;
 }catch(error){if(service)disposePreparedService(service);for(const application of applications)disposePreparedApplicationFile(application);for(const application of businessApplications)disposePreparedBusinessApplication(application);rmSync(workspace,{recursive:true,force:true});throw error;}
}
function current(prepared:PreparedProfileProject){const state=preparedProjects.get(prepared);if(!state)throw Error('PROFILE_PROJECT_UNREGISTERED');if(prepared.lowered)assertLoweredProfileSourcesCurrent(prepared.lowered);state.compiler.profileEngine.assertCheckedCompositionCurrent(prepared.composition);if(state.service)assertPreparedServiceCurrent(state.service);for(const app of state.businessApplications)assertPreparedBusinessApplicationCurrent(app);return state;}
/** Returns current captured inert data: no writes, native compiler or runtime invocation. */
export function planProfileProject(prepared:PreparedProfileProject){const state=current(prepared);return {schema_version:'alchlang.profile-plan/v1',lock:prepared.snapshot.lock,composition:prepared.composition.data,files:state.render,views:state.views,claim_ceiling:'planned and linked; no runtime proof or admission',authority_effect:'none'};}
export function generateProfileProject(prepared:PreparedProfileProject,target:string){const state=current(prepared),engine=state.compiler.profileEngine,files=engine.compileProfileDomainFiles(prepared.snapshot,state.render,prepared.compilerPath),qualification=engine.qualifyNativeFiles(prepared.snapshot,files,prepared.compilerPath);current(prepared);return {output:engine.completeProfileOutput(prepared.snapshot,files,qualification,path.resolve(target)),qualification,lock:prepared.snapshot.lock,authority_effect:'none'};}
export function verifyProfileProject(prepared:PreparedProfileProject,target:string){const state=current(prepared),engine=state.compiler.profileEngine,files=engine.compileProfileDomainFiles(prepared.snapshot,state.render,prepared.compilerPath);engine.verifyProfileOutput(prepared.snapshot,path.resolve(target),files);return {status:'verified',output:path.resolve(target),lock_sha256:prepared.snapshot.lock.lock_sha256,claim_ceiling:'exact artifact inventory and current source/profile/core/tool bytes; not runtime proof or admission',authority_effect:'none'};}
export function disposeProfileProject(prepared:PreparedProfileProject){const state=preparedProjects.get(prepared);if(!state)throw Error('PROFILE_PROJECT_UNREGISTERED');preparedProjects.delete(prepared);if(state.service)disposePreparedService(state.service);for(const application of state.applications)disposePreparedApplicationFile(application);for(const app of state.businessApplications)disposePreparedBusinessApplication(app);rmSync(prepared.workspace,{recursive:true,force:true});}
export async function runProfileProjectCommand(args:readonly string[],io:{stdout(value:string):void;stderr(value:string):void}):Promise<number>{
 const help='alchlang profile generate-source <selection.json> [--children <catalog.json>] [--native-artifacts <catalog.json>] [--business <business.alch> --business-profile <profile.json> --http-profile <http.json>] [--implementation-root <directory>] --out <new-directory>\nalchlang profile check-source|compile-source <source.profile.json> [--source-root <directory>] [--implementation-root <directory>] [--out <new-directory>]\nalchlang profile select|check|plan|generate|view|verify <project.json> [--lock <lock.json>] [--out <directory>]\nSource profiles select admitted architecture, checked business roles and exact native factories; composed selections join their original generators. Supply the three business options together for application generation. Native resources require explicit operator configuration. Legacy project commands retain their own versioned consumers. Generation checks source and output; optional claims remain unproved. Local hosting, TDE, EVF and publication are deferred.';
 if(args.length===0||args[0]==='--help'){io.stdout(help);return 0;}
 let prepared:PreparedProfileProject|undefined;
 try{
  if(args[0]==='generate-source'){
   const [,selection,...rest]=args;if(!selection)throw Error('PROFILE_SELECTION_REQUIRED');const opts=new Map<string,string>();
   for(let i=0;i<rest.length;i+=2){const k=rest[i],v=rest[i+1];if(!k||!v||!['--business','--business-profile','--http-profile','--out','--children','--native-artifacts','--implementation-root'].includes(k)||opts.has(k))throw Error('PROFILE_SOURCE_GENERATE_OPTION');opts.set(k,v);}
   if(!opts.has('--out'))throw Error('PROFILE_SOURCE_OUTPUT_REQUIRED');if(['--business','--business-profile','--http-profile'].some(k=>opts.has(k))&&!['--business','--business-profile','--http-profile'].every(k=>opts.has(k)))throw Error('PROFILE_SOURCE_BUSINESS_INPUTS_REQUIRED');
   const compiler=await loadDomainSpecCompiler(),engine=compiler.profileEngine;if(!engine.createTechnicalProfileSourceOwner||!engine.createGenericHttpCompositionOwner)throw Error('PROFILE_SOURCE_PEER_REQUIRED');
   const owner=engine.createTechnicalProfileSourceOwner(),source=owner.prepareCompiled(path.resolve(selection)),sdk=engine.createGenericHttpCompositionOwner(),workspace=mkdtempSync(path.join(os.tmpdir(),'alch-profile-generate-'));let application:any;
   try{
    const inspected=owner.inspect(source);if(inspected.target_consumer!=='craft.technical-profile-composition/v1'&&!opts.has('--business'))throw Error('PROFILE_SOURCE_BUSINESS_INPUTS_REQUIRED');
    if(opts.has('--business')){application=await sdk.prepare({sourcePath:path.resolve(opts.get('--business')!),profilePath:path.resolve(opts.get('--business-profile')!),httpProfilePath:path.resolve(opts.get('--http-profile')!)});
    // Local build intent covers original source acceptance; this is not a user
    // approval prompt or a grant to an application's eventual runtime actor.
    const review=sdk.review(application,'technical-profile-cli');sdk.accept(application,{decision_id:'technical-profile-cli',owner:'technical-profile-cli',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(workspace,'source-acceptance.json'));}
    const outputDirectory=path.resolve(opts.get('--out')!);let result:any;
    if(inspected.target_consumer==='craft.generic-service-artifacts/v1-candidate'){
     if(!engine.createTechnicalProfileServiceArchitectureOwner)throw Error('PROFILE_SERVICE_SOURCE_PEER_REQUIRED');const producer=engine.createTechnicalProfileServiceArchitectureOwner({sourceOwner:owner,sourceHandle:source,sdk,application}),emitted=producer.emit({outputDirectory});result=producer.inspect(emitted);
    }else if(inspected.target_consumer==='craft.error-presentation/v1'){
     if(!engine.createTechnicalErrorPresentationApplicationOwner||!engine.createGenericErrorPresentationBinding||!engine.inspectGenericErrorPresentation)throw Error('PROFILE_ERROR_SOURCE_PEER_REQUIRED');const binding=engine.createGenericErrorPresentationBinding({sourceOwner:owner,sourceHandle:source,businessOwner:sdk,businessHandle:application}),entries=engine.inspectGenericErrorPresentation(binding).entries;if(!entries.length)throw Error('PROFILE_ERROR_ENTRY_REQUIRED');result=engine.createTechnicalErrorPresentationApplicationOwner({sourceOwner:owner,sourceHandle:source,sdk,application}).emit({entry:entries[0],outputDirectory});
    }else if(inspected.target_consumer==='craft.generic-business-bindings/v1-candidate'){
     if(!engine.createTechnicalBusinessBindingOwner)throw Error('PROFILE_BUSINESS_SOURCE_PEER_REQUIRED');const producer=engine.createTechnicalBusinessBindingOwner(sdk,application),bound=producer.resolve({sourceOwner:owner,sourceHandle:source}),bindings=producer.inspect(bound).bindings;
     if(bindings.length!==1)throw Error('PROFILE_BUSINESS_SOURCE_SINGLE_ENTRY_OUTPUT_REQUIRED');result=producer.generateJoined(bound,{owner:sdk,entry:bindings[0].entry,outputDirectory});
    }else if(inspected.target_consumer==='craft.technical-profile-composition/v1'){
     if(!engine.createTechnicalProfileCompositionOwner||!engine.captureGenericNativeProfileArtifact||!engine.inspectGenericNativeProfileArtifact)throw Error('PROFILE_COMPOSITION_SOURCE_PEER_REQUIRED');
     const children:any[]=[],childHandles:any[]=[];let producer:any;const artifacts=new Map<string,any>();
     const catalog=(key:string,field:string)=>{const file=opts.get(key);if(!file)return {root:process.cwd(),rows:[]};const root=path.dirname(path.resolve(file)),raw=JSON.parse(readFileSync(path.resolve(file),'utf8'));if(!raw||typeof raw!=='object'||Object.keys(raw).sort().join(',')!==field+',schema_version'||raw.schema_version!=='craft.technical-profile-'+field+'-catalog/v1'||!Array.isArray(raw[field]))throw Error('PROFILE_COMPOSITION_CATALOG');return {root,rows:raw[field] as unknown[]};};
     try{
      const sources=catalog('--children','children');for(const row of sources.rows){if(!row||typeof row!=='object'||Object.keys(row).join(',')!=='selection'||typeof (row as any).selection!=='string')throw Error('PROFILE_COMPOSITION_CHILD');const child=owner.prepareCompiled(path.resolve(sources.root,(row as any).selection));childHandles.push(child);children.push({sourceOwner:owner,sourceHandle:child});}
      const natives=catalog('--native-artifacts','artifacts');for(const row of natives.rows){if(!row||typeof row!=='object'||Object.keys(row).join(',')!=='directory'||typeof (row as any).directory!=='string')throw Error('PROFILE_COMPOSITION_NATIVE');const artifact=engine.captureGenericNativeProfileArtifact(path.resolve(natives.root,(row as any).directory)),identity=engine.inspectGenericNativeProfileArtifact(artifact),key=identity.name+'@'+identity.version;if(artifacts.has(key))throw Error('PROFILE_COMPOSITION_NATIVE_DUPLICATE');artifacts.set(key,artifact);}
      producer=engine.createTechnicalProfileCompositionOwner({sourceOwner:owner,sourceHandle:source,children,...(application?{business:{sdk,application}}:{}),artifacts});const composed=await producer.prepare();result=await producer.emit(composed,{outputDirectory,implementationRoot:path.resolve(opts.get('--implementation-root')??compiler.binding.package_root)});
     }finally{try{producer?.close();}finally{for(const child of childHandles)owner.dispose(child);}}
    }else throw Error('PROFILE_SOURCE_CONSUMER_REQUIRES_ITS_ORIGINAL_PROJECT_GENERATOR');
    io.stdout(JSON.stringify({status:'generated',output:outputDirectory,result,authority_effect:'none'},null,2));return 0;
   }finally{if(application)sdk.dispose(application);owner.dispose(source);rmSync(workspace,{recursive:true,force:true});}
  }
  if(['check-source','compile-source'].includes(args[0]!)){
   const [action,manifest,...rest]=args;if(!manifest)throw Error('PROFILE_SOURCE_MANIFEST_REQUIRED');
   const opts=new Map<string,string>();for(let i=0;i<rest.length;i+=2){const k=rest[i],v=rest[i+1];if(!k||!v||!['--source-root','--implementation-root','--out'].includes(k)||opts.has(k))throw Error('PROFILE_SOURCE_OPTION');opts.set(k,v);}
   if((action==='compile-source')!==opts.has('--out'))throw Error('PROFILE_SOURCE_OUTPUT_REQUIRED_ONLY_FOR_COMPILE');
   const compiler=await loadDomainSpecCompiler(),factory=compiler.profileEngine?.createTechnicalProfileSourceOwner;if(typeof factory!=='function')throw Error('PROFILE_SOURCE_PEER_REQUIRED: rebuild current Craft working compiler');
   const owner=factory(),handle=owner.prepare({sourceRoot:path.resolve(opts.get('--source-root')??path.dirname(manifest)),manifestPath:path.resolve(manifest)});
   try{const result=action==='check-source'?owner.inspect(handle):owner.inspect(handle).target_consumer==='craft.profile-engine/v1'?owner.publishArchitecture(handle,path.resolve(opts.get('--implementation-root')??compiler.binding.package_root),path.resolve(opts.get('--out')!)):owner.publishSelection(handle,path.resolve(opts.get('--out')!));io.stdout(JSON.stringify(result,null,2));return 0;}finally{owner.dispose(handle);}
  }
  const [command,project,...rest]=args;if(!command||!['select','check','plan','generate','view','verify'].includes(command)||!project)throw Error('PROFILE_COMMAND_USAGE: '+help);
  const options=new Map<string,string>();for(let i=0;i<rest.length;i+=2){const key=rest[i],value=rest[i+1];if(!key||!['--lock','--out'].includes(key)||!value||options.has(key))throw Error('PROFILE_COMMAND_OPTION');options.set(key,value);}
  if(['generate','verify'].includes(command)!==options.has('--out'))throw Error('PROFILE_COMMAND_OUTPUT: --out is required only for generate/verify');
  const lock=options.get('--lock');prepared=await prepareProfileProject(project,lock?JSON.parse(readFileSync(path.resolve(lock),'utf8')):undefined);
  const plan=planProfileProject(prepared),result=command==='select'?{lock:plan.lock}:command==='check'?{status:'checked',claim_ceiling:plan.claim_ceiling}:command==='view'?plan.views:command==='generate'?generateProfileProject(prepared,options.get('--out')!):command==='verify'?verifyProfileProject(prepared,options.get('--out')!):plan;
  io.stdout(JSON.stringify(result,null,2));return 0;
 }catch(error){io.stderr(JSON.stringify({status:'rejected',code:(error as any)?.code??'PROFILE_PROJECT_ERROR',message:(error as Error).message,authority_effect:'none'}));return 1;}
 finally{if(prepared)disposeProfileProject(prepared);}
}
