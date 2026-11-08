#!/usr/bin/env node
/** Source CLI for cumulative composition. No installed-archive qualification.
 * Open Questions: ../docs/GENERIC-APPLICATIONS.md#open-questions. */
import {readFileSync,realpathSync,statSync,constants,openSync,closeSync,readSync,fstatSync,lstatSync,mkdtempSync,readdirSync,rmSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {TextDecoder} from 'node:util';
import {COMMERCE_SOURCE_LIMITS,commerceRelativePath} from './commerce-source-lexer.js';
import {parseCommerceContractJson} from './commerce-source-capture.js';
import {sourceFail} from './commerce-source-model.js';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {parseGenericBusinessSource,lowerGenericCapabilitySelectors} from './generic-business-source.js';
import {parseCommerceModuleSource} from './commerce-source-parser.js';
import type {CommerceParsedModule} from './commerce-source-model.js';
import {defaultDomainSpecPackageRoot,DOMAINSPEC_PACKAGE,DOMAINSPEC_VERSION} from './domainspec-cli.js';
// Only the interface consumed by this bridge; no second schema or owner producer.
interface GenericCompositionBridge {
 prepare(input:{sourcePath:string;profilePath:string;additionalSourcePaths?:readonly string[];httpProfilePath?:string;externalProfilePath?:string;externalWriteSelectionPath?:string;capabilitySelectionPath?:string}):Promise<unknown>;
 review(handle:unknown,owner:string):{review_sha256:string};
 accept(handle:unknown,decision:{decision_id:string;owner:string;outcome:'accepted';reviewed_digest:string},decisionPath:string):unknown;
 generate(handle:unknown,selection:Record<string,string>):unknown;
 inspect(handle:unknown):unknown;
 inspectCapabilities(handle:unknown):unknown;
 assertCurrent(handle:unknown):void;
 exportFiniteBoolFormal(handle:unknown,selection:{rule:string}):unknown;
 exportWorkflowTlaFormal(handle:unknown):unknown;
 exportStructuralAlloyFormalFromSource(handle:unknown,request:{outputDirectory:string;entries:readonly string[]}):Promise<unknown>;
 exportWorkflowEventJoinFormalFromSource(handle:unknown,request:{outputDirectory:string;entries:readonly string[]}):Promise<unknown>;
 publishFormalExportDirectory(handle:unknown,joined:object,outputDirectory:string,artifacts:readonly {relative_path:string;content:string}[]):void;
 dispose(handle:unknown):void;
}
async function loadGenericCompositionOwner():Promise<GenericCompositionBridge>{
 const root=realpathSync(defaultDomainSpecPackageRoot());
 const contained=(target:string)=>{const relative=path.relative(root,target);return relative!==''&&!relative.startsWith('..'+path.sep)&&relative!=='..'&&!path.isAbsolute(relative);};
 const manifestPath=path.join(root,'package.json');
 const captureManifest=()=>{const physical=realpathSync(manifestPath);if(!contained(physical))throw Error('GENERIC_COMPOSITION_PACKAGE_ESCAPE');const before=statSync(physical,{bigint:true}),bytes=readFileSync(physical),after=statSync(physical,{bigint:true});const identity=(s:typeof before)=>[s.dev,s.ino,s.size,s.mtimeNs,s.ctimeNs].join(':');if(identity(before)!==identity(after))throw Error('GENERIC_COMPOSITION_PACKAGE_CHANGED');return {bytes,identity:physical+':'+identity(after)};};
 const before=captureManifest(),manifest=JSON.parse(before.bytes.toString('utf8'));
 if(manifest.name!==DOMAINSPEC_PACKAGE||manifest.version!==DOMAINSPEC_VERSION)throw Error('GENERIC_COMPOSITION_PACKAGE_IDENTITY: expected '+DOMAINSPEC_PACKAGE+'@'+DOMAINSPEC_VERSION);
 const extension=path.extname(fileURLToPath(import.meta.url));if(extension!=='.ts'&&extension!=='.js')throw Error('GENERIC_COMPOSITION_CLI_MODE');
 const selected=path.join(root,extension==='.ts'?'src/generic/public-sdk.ts':'dist/generic/public-sdk.js');let target:string;
 try{target=realpathSync(selected);}catch{throw Error('GENERIC_COMPOSITION_SDK_MISSING: '+selected);}
 if(!contained(target))throw Error('GENERIC_COMPOSITION_SDK_ESCAPE');
 const api=await import(pathToFileURL(target).href),after=captureManifest();
 if(before.identity!==after.identity||!before.bytes.equals(after.bytes)||realpathSync(selected)!==target)throw Error('GENERIC_COMPOSITION_PACKAGE_CHANGED');
 if(typeof api.createGenericCompositionOwner!=='function')throw Error('GENERIC_COMPOSITION_FACTORY_REQUIRED');
 const owner=api.createGenericCompositionOwner();if(!owner||['prepare','review','accept','generate','dispose'].some(k=>typeof owner[k]!=='function'))throw Error('GENERIC_COMPOSITION_OWNER_API_REQUIRED');
 return owner as GenericCompositionBridge;
}
// Preliminary frontend input only. Core independently recaptures physical custody.
function readBoundedFrontendFile(file:string):string {
 const span={path:file,start:0,end:0},bad=(code:'InvalidContract'|'ResourceLimit'|'StaleOwner'|'Syntax',message:string):never=>sourceFail(code,span,message);
 if(realpathSync(file)!==file)bad('InvalidContract','original normalized physical input path required');
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
 try{
  const before=fstatSync(fd,{bigint:true});if(!before.isFile())bad('InvalidContract','regular frontend input required');
  if(before.size>BigInt(COMMERCE_SOURCE_LIMITS.source_bytes))bad('ResourceLimit','frontend input exceeds1MiB');
  const chunks:Buffer[]=[];let total=0;
  for(;;){const buffer=Buffer.alloc(Math.min(65536,COMMERCE_SOURCE_LIMITS.source_bytes+1-total)),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;total+=count;if(total>COMMERCE_SOURCE_LIMITS.source_bytes)bad('ResourceLimit','frontend input grew beyond byte bound');chunks.push(buffer.subarray(0,count));}
  const after=fstatSync(fd,{bigint:true}),named=lstatSync(file,{bigint:true});
  const identity=(v:typeof before)=>[v.dev,v.ino,v.size,v.mtimeNs,v.ctimeNs].join(':');
  if(identity(before)!==identity(after)||identity(after)!==identity(named)||realpathSync(file)!==file||BigInt(total)!==after.size)bad('StaleOwner','frontend input changed during bounded read');
  try{return new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(Buffer.concat(chunks));}catch{return bad('Syntax','strict UTF8 frontend input required');}
 }finally{closeSync(fd);}
}
/** CLI selection is preliminary data. Core independently captures and checks
 * both exact profiles; a transport reference never grants runtime authority. */
function compositionProfiles(sourcePath:string,selectedPath:string,httpOption:string|undefined){
 let profilePath=selectedPath,httpProfilePath=httpOption;
 let profile=parseCommerceContractJson(readBoundedFrontendFile(profilePath),path.basename(profilePath)) as {schema_version?:unknown;capabilities?:unknown;application_profile?:unknown};
 if(profile?.schema_version==='craft.generic-http-profile/v1-candidate'){
  if(httpOption)throw Error('UnsupportedCapability: select one HTTP profile, not both --profile HTTP and --http-profile');
  const relative=profile.application_profile;
  if(typeof relative!=='string')throw Error('UnsupportedCapability: HTTP profile requires an explicit application_profile');
  commerceRelativePath(relative);
  if(!['contracts/selected-profile.json','selected-profile.json'].includes(relative))throw Error('UnsupportedCapability: HTTP application profile must be the exact declared selected-profile reference');
  httpProfilePath=profilePath;
  profilePath=relative==='selected-profile.json'?path.resolve(path.dirname(httpProfilePath),relative):path.resolve(path.dirname(sourcePath),relative);
  profile=parseCommerceContractJson(readBoundedFrontendFile(profilePath),relative) as typeof profile;
 }
 if(httpProfilePath){
  const transport=parseCommerceContractJson(readBoundedFrontendFile(httpProfilePath),path.basename(httpProfilePath)) as {schema_version?:unknown};
  if(transport?.schema_version!=='craft.generic-http-profile/v1-candidate')throw Error('UnsupportedCapability: exact HTTP transport profile required');
  if(profile?.schema_version!=='craft.generic-transaction-profile/v1-candidate'&&profile?.schema_version!=='craft.generic-event-profile/v1-candidate')
   throw Error('UnsupportedCapability: HTTP requires a stateful application profile');
 }
 return {profilePath,httpProfilePath,profile};
}
async function formalCompositionMain(args:readonly string[]){
 const usage='usage: formal-export --model smtlib2|tla+|alloy|workflow-event --source FILE --profile FILE [--http-profile FILE] [--additional-source FILE ...] [--external-profile FILE --external-write-selection FILE] (--rule MODULE.RULE | --workflow MODULE.WORKFLOW | --artifact-entry MODULE.ENTRY [--artifact-entry MODULE.ENTRY ...] | --workflow MODULE.WORKFLOW --artifact-entry MODULE.ENTRY [--artifact-entry MODULE.ENTRY ...]) --out NEW_DIRECTORY --accept-local-review OWNER';
 if(args.length<13||args.length>287||(args.length-1)%2!==0)throw Error(usage);
 const flags=new Map<string,string>(),additional:string[]=[],entries:string[]=[];
 const singletons=['--model','--source','--profile','--http-profile','--external-profile','--external-write-selection','--rule','--workflow','--out','--accept-local-review'];
 for(let i=1;i<args.length;i+=2){
  const key=args[i]!,value=args[i+1]!;if(!value||value.startsWith('--'))throw Error('formal export option requires its value');
  if(key==='--additional-source'){if(additional.length>=31)throw Error('at most31 additional sources');additional.push(value);}
  else if(key==='--artifact-entry'){if(entries.length>=128)throw Error('at most128 artifact Entries');entries.push(value);}
  else {if(!singletons.includes(key)||flags.has(key))throw Error('exact unique formal export arguments required');flags.set(key,value);}
 }
 if(['--model','--source','--profile','--out','--accept-local-review'].some(key=>!flags.has(key)))throw Error(usage);
 const modelKind=flags.get('--model');
 if(!['smtlib2','tla+','alloy','workflow-event'].includes(modelKind!))throw Error('UnsupportedCapability: formal model must be smtlib2, tla+, alloy or workflow-event');
 if(modelKind==='smtlib2'&&(!flags.has('--rule')||flags.has('--workflow')||entries.length)||
  modelKind==='tla+'&&(!flags.has('--workflow')||flags.has('--rule')||entries.length)||
  modelKind==='alloy'&&(!entries.length||flags.has('--rule')||flags.has('--workflow'))||
  modelKind==='workflow-event'&&(!entries.length||!flags.has('--workflow')||flags.has('--rule')))
  throw Error('UnsupportedCapability: model selector does not match the formal exporter');
 if(new Set(entries).size!==entries.length)throw Error('duplicate selected artifact Entry');
 const sourcePath=path.resolve(flags.get('--source')!),selectedProfilePath=path.resolve(flags.get('--profile')!),additionalSourcePaths=additional.map(file=>path.resolve(file));
 const {profilePath,httpProfilePath,profile}=compositionProfiles(sourcePath,selectedProfilePath,flags.has('--http-profile')?path.resolve(flags.get('--http-profile')!):undefined);
 const externalProfilePath=flags.has('--external-profile')?path.resolve(flags.get('--external-profile')!):undefined;
 const externalWriteSelectionPath=flags.has('--external-write-selection')?path.resolve(flags.get('--external-write-selection')!):undefined;
 if(externalWriteSelectionPath&&!externalProfilePath)throw Error('UnsupportedCapability: external write selection requires an external profile');
 if(!sourcePath.endsWith('.alch')||new Set([sourcePath,...additionalSourcePaths]).size!==1+additionalSourcePaths.length)throw Error('unique explicit .alch sources required');
 const root=path.dirname(sourcePath);for(const file of additionalSourcePaths){commerceRelativePath(path.relative(root,file).split(path.sep).join('/'));if(!file.endsWith('.alch'))throw Error('additional source must be .alch');}
 const event=profile?.schema_version==='craft.generic-event-profile/v1-candidate',atomic=event||profile?.schema_version==='craft.generic-transaction-profile/v1-candidate';
 if((additional.length||externalProfilePath||externalWriteSelectionPath)&&!atomic)throw Error('UnsupportedCapability: additional or external sources require a stateful profile');
 if(modelKind==='tla+'&&!event)throw Error('UnsupportedCapability: TLA+ requires the checked Event Workflow profile');
 if(modelKind==='workflow-event'&&!event)throw Error('UnsupportedCapability: Workflow/Event join requires the checked Event Workflow profile');
 if(modelKind==='alloy'&&!atomic)throw Error('UnsupportedCapability: Alloy requires a checked stateful application');
 if(modelKind==='smtlib2'&&(atomic||profile?.schema_version!=='craft.generic-pure-profile/v1-candidate'))throw Error('UnsupportedCapability: finite SMT-LIB requires a bounded pure profile');
 if(externalProfilePath)readBoundedFrontendFile(externalProfilePath);
 if(externalWriteSelectionPath)readBoundedFrontendFile(externalWriteSelectionPath);
 const capabilities=Array.isArray(profile.capabilities)?profile.capabilities:[],bounded=capabilities.includes('bounded-values'),states=capabilities.includes('StateMachine'),keyed=atomic||profile.schema_version==='craft.generic-keyed-query-profile/v1-candidate';
 let moduleBytes=0;for(const file of [sourcePath,...additionalSourcePaths]){
  const text=readBoundedFrontendFile(file);moduleBytes+=Buffer.byteLength(text);
  if(moduleBytes>COMMERCE_SOURCE_LIMITS.total_bytes)sourceFail('ResourceLimit',{path:file,start:0,end:0},'authored frontend modules exceed4MiB');
  // Stateful Core admission reconstructs the complete source independently.
  // The older frontend parser does not cover all checked Event/external syntax.
  if(!atomic)parseGenericBusinessSource(text,path.relative(root,file).split(path.sep).join('/'),bounded,states,keyed,atomic);
 }
 const owner=await loadGenericCompositionOwner();
 const required=modelKind==='smtlib2'?'exportFiniteBoolFormal':modelKind==='tla+'?'exportWorkflowTlaFormal':modelKind==='alloy'?'exportStructuralAlloyFormalFromSource':'exportWorkflowEventJoinFormalFromSource';
 if(typeof owner[required]!=='function'||typeof owner.assertCurrent!=='function'||typeof owner.publishFormalExportDirectory!=='function')throw Error('GENERIC_FORMAL_OWNER_API_REQUIRED');
 const outputDirectory=path.resolve(flags.get('--out')!);
 if(outputDirectory===path.parse(outputDirectory).root||realpathSync(path.dirname(outputDirectory))!==path.dirname(outputDirectory))throw Error('GENERIC_FORMAL_OUTPUT_PARENT');
 try{lstatSync(outputDirectory);throw Error('GENERIC_FORMAL_OUTPUT_EXISTS');}catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
 const handle=await owner.prepare({sourcePath,profilePath,...(httpProfilePath?{httpProfilePath}:{}),...(additional.length?{additionalSourcePaths}:{}),...(externalProfilePath?{externalProfilePath}:{}),...(externalWriteSelectionPath?{externalWriteSelectionPath}:{})});
 let failed=false,originalError:unknown;
 const stage=mkdtempSync(path.join(path.dirname(outputDirectory),'.alch-formal-'));
 const stageIdentity=lstatSync(stage,{bigint:true});
 const stageCurrent=()=>{const current=lstatSync(stage,{bigint:true});if(!current.isDirectory()||current.isSymbolicLink()||current.dev!==stageIdentity.dev||current.ino!==stageIdentity.ino||realpathSync(stage)!==stage)throw Error('GENERIC_FORMAL_STAGE_CHANGED');};
 try{
  stageCurrent();
  const reviewer=flags.get('--accept-local-review')!,review=owner.review(handle,reviewer);
  owner.accept(handle,{decision_id:'cli-local-formal-acceptance',owner:reviewer,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(stage,'decision.json'));
  let joined:unknown;
  if(modelKind==='smtlib2')joined=owner.exportFiniteBoolFormal(handle,{rule:flags.get('--rule')!});
  else if(modelKind==='tla+')joined=owner.exportWorkflowTlaFormal(handle);
  if(modelKind==='alloy')joined=await owner.exportStructuralAlloyFormalFromSource(handle,{outputDirectory:path.join(stage,'artifacts'),entries});
  else if(modelKind==='workflow-event')joined=await owner.exportWorkflowEventJoinFormalFromSource(handle,{outputDirectory:path.join(stage,'artifacts'),entries});
  if(!joined||typeof joined!=='object'||!('model'in joined)||!joined.model||typeof joined.model!=='object')throw Error('GENERIC_FORMAL_MODEL_REQUIRED');
  const model=joined.model as Record<string,unknown>;
  if(modelKind==='tla+'&&model.workflow!==flags.get('--workflow'))throw Error('UnsupportedCapability: selected Workflow differs from original checked source');
  if(modelKind==='workflow-event'&&(typeof model.workflow!=='object'||!model.workflow||
   (model.workflow as {id?:unknown}).id!==flags.get('--workflow')))throw Error('UnsupportedCapability: selected Workflow differs from original checked source');
  const textFiles=modelKind==='workflow-event'
   ?[{relative_path:'model.als',content:model.alloy},{relative_path:'model.tla',content:model.tla}]
   :[{relative_path:'model.'+(modelKind==='smtlib2'?'smt2':modelKind==='tla+'?'tla':'als'),
      content:model[modelKind==='smtlib2'?'smtlib2':modelKind==='tla+'?'tla':'alloy']}];
  if(model.language!==(modelKind==='workflow-event'?'alloy+tla+':modelKind)||
   textFiles.some(file=>typeof file.content!=='string'||!file.content.length))throw Error('GENERIC_FORMAL_MODEL_REQUIRED');
  const bytes=JSON.stringify(joined,null,2)+'\n',jsonFile='model.json';
  owner.assertCurrent(handle);
  const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
  const staged: {relative_path:string;content:string}[]=[];
  const collect=(directory:string,relative='')=>{
   stageCurrent();
   for(const name of readdirSync(directory).sort()){
    const local=relative?relative+'/'+name:name,absolute=path.join(directory,name),before=lstatSync(absolute,{bigint:true});
    if(before.isSymbolicLink())throw Error('GENERIC_FORMAL_STAGE_CHANGED');
    if(before.isDirectory()){collect(absolute,local);continue;}
    if(!before.isFile()||before.size>BigInt(COMMERCE_SOURCE_LIMITS.total_bytes))throw Error('GENERIC_FORMAL_STAGE_CHANGED');
    const content=readFileSync(absolute,'utf8'),after=lstatSync(absolute,{bigint:true});
    if(before.dev!==after.dev||before.ino!==after.ino||before.size!==after.size||before.mtimeNs!==after.mtimeNs||before.ctimeNs!==after.ctimeNs)throw Error('GENERIC_FORMAL_STAGE_CHANGED');
    staged.push({relative_path:local,content});
   }
  };
  collect(stage);
  if(!staged.some(file=>file.relative_path==='decision.json'))throw Error('GENERIC_FORMAL_DECISION_REQUIRED');
  const artifactManifest=(joined as {artifact_manifest?:{files?:readonly {path:string;sha256:string;bytes:number}[]}}).artifact_manifest;
  if(modelKind==='alloy'||modelKind==='workflow-event'){
   const expected=[...(artifactManifest?.files??[]).map(file=>'artifacts/'+file.path),'artifacts/service-inventory.json'].sort();
   const actual=staged.filter(file=>file.relative_path.startsWith('artifacts/')).map(file=>file.relative_path).sort();
   if(JSON.stringify(expected)!==JSON.stringify(actual))throw Error('GENERIC_FORMAL_ARTIFACT_INVENTORY');
   for(const file of artifactManifest?.files??[]){
    const captured=staged.find(candidate=>candidate.relative_path==='artifacts/'+file.path);
    if(!captured||sha(captured.content)!==file.sha256||Buffer.byteLength(captured.content)!==file.bytes)throw Error('GENERIC_FORMAL_ARTIFACT_CHANGED');
   }
   const inventory=staged.find(file=>file.relative_path==='artifacts/service-inventory.json');
   if(!inventory||inventory.content!==JSON.stringify(artifactManifest,null,2)+'\n')throw Error('GENERIC_FORMAL_ARTIFACT_CHANGED');
  }
  const permitted=new Set(modelKind==='alloy'||modelKind==='workflow-event'?['decision.json',...(artifactManifest?.files??[]).map(file=>'artifacts/'+file.path),'artifacts/service-inventory.json']:['decision.json']);
  if(staged.length!==permitted.size||staged.some(file=>!permitted.has(file.relative_path)))throw Error('GENERIC_FORMAL_STAGE_INVENTORY');
  const manifest={schema_version:'craft.generic-formal-cli-export/v1-candidate',language:modelKind==='workflow-event'?'alloy+tla+':modelKind,
   source_capture_sha256:model.source_capture_sha256,
   profile_sha256:model.profile_sha256??(model.profile_metadata as {sha256?:unknown}|undefined)?.sha256,
   artifact_inventory_sha256:modelKind==='alloy'?model.inventory_sha256:modelKind==='workflow-event'?model.emitted_inventory_sha256:null,
   files:[...textFiles.map(file=>({path:file.relative_path,sha256:sha(file.content as string),bytes:Buffer.byteLength(file.content as string)})),{path:jsonFile,sha256:sha(bytes),bytes:Buffer.byteLength(bytes)},...staged.map(file=>({path:file.relative_path,sha256:sha(file.content),bytes:Buffer.byteLength(file.content)}))],
   authority_effect:'none',claim_ceiling:model.claim_ceiling};
  stageCurrent();owner.publishFormalExportDirectory(handle,joined as object,outputDirectory,[...staged,...textFiles.map(file=>({relative_path:file.relative_path,content:file.content as string})),{relative_path:jsonFile,content:bytes},{relative_path:'manifest.json',content:JSON.stringify(manifest,null,2)+'\n'}]);
  process.stdout.write(JSON.stringify(manifest)+'\n');return manifest;
 }catch(error){failed=true;originalError=error;throw error;}
 finally{
  try{owner.dispose(handle);}catch(cleanup){if(failed)throw new AggregateError([originalError,cleanup],'CLI formal export and acquired-owner cleanup failed',{cause:originalError});throw cleanup;}
  finally{try{stageCurrent();rmSync(stage,{recursive:true});}catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}}
 }
}
export async function genericCompositionMain(args:readonly string[]){
 if(args[0]==='generate-application-system')return (await import('./application-profile-cli.js')).applicationSystemMain(args);
 if(args[0]==='generate-application')return (await import('./application-profile-cli.js')).applicationProfileMain(args);
 if(args[0]==='formal-export')return formalCompositionMain(args);
 const usage='usage: generate --source FILE --profile FILE [--http-profile FILE] [--capability-selection FILE] [--additional-source FILE ...] [--external-profile FILE --external-write-selection FILE] (--rule MODULE.RULE | --operation MODULE.OPERATION | --mapping MODULE.MAPPING | --calculation MODULE.CALCULATION | --policy MODULE.POLICY | --entry MODULE.ENTRY) --out NEW_DIRECTORY --accept-local-review OWNER; inspect --source FILE --profile FILE [--http-profile FILE] [--capability-selection FILE] [--additional-source FILE ...] [--external-profile FILE --external-write-selection FILE]';
 if(args.length===1&&args[0]==='--help'){process.stdout.write(usage+'\n');return;}
 const inspecting=args[0]==='inspect';
 if(!inspecting&&args[0]!=='generate'||args.length<(inspecting?5:11)||args.length>81||(args.length-1)%2!==0)throw Error(usage);
 const flags=new Map<string,string>(),additional:string[]=[],selectors=['--rule','--operation','--mapping','--calculation','--policy','--entry'],singletons=['--source','--profile','--http-profile','--capability-selection','--external-profile','--external-write-selection',...(inspecting?[]:[...selectors,'--out','--accept-local-review'])];
 for(let i=1;i<args.length;i+=2){const key=args[i]!,value=args[i+1]!;if(!value||value.startsWith('--'))throw Error('composition option requires its value');if(key==='--additional-source'){if(additional.length>=31)throw Error('at most31 additional sources');additional.push(value);}else{if(!singletons.includes(key)||flags.has(key))throw Error('exact unique composition arguments required');flags.set(key,value);}}
 if(['--source','--profile',...(inspecting?[]:['--out','--accept-local-review'])].some(k=>!flags.has(k))||!inspecting&&selectors.filter(k=>flags.has(k)).length!==1)throw Error('all composition arguments required');
 const sourcePath=path.resolve(flags.get('--source')!),selectedProfilePath=path.resolve(flags.get('--profile')!),additionalSourcePaths=additional.map(p=>path.resolve(p));
 const {profilePath,httpProfilePath,profile}=compositionProfiles(sourcePath,selectedProfilePath,flags.has('--http-profile')?path.resolve(flags.get('--http-profile')!):undefined);
 const externalProfilePath=flags.has('--external-profile')?path.resolve(flags.get('--external-profile')!):undefined;
 const externalWriteSelectionPath=flags.has('--external-write-selection')?path.resolve(flags.get('--external-write-selection')!):undefined;
 const capabilitySelectionPath=flags.has('--capability-selection')?path.resolve(flags.get('--capability-selection')!):undefined;
 if(externalWriteSelectionPath&&!externalProfilePath)throw Error('UnsupportedCapability: external write selection requires an external profile');
 if(!sourcePath.endsWith('.alch')||new Set([sourcePath,...additionalSourcePaths]).size!==1+additionalSourcePaths.length)throw Error('unique explicit .alch sources required');
 const root=path.dirname(sourcePath);for(const file of additionalSourcePaths){commerceRelativePath(path.relative(root,file).split(path.sep).join('/'));if(!file.endsWith('.alch'))throw Error('additional source must be .alch');}
 const atomic=profile?.schema_version==='craft.generic-transaction-profile/v1-candidate'||profile?.schema_version==='craft.generic-event-profile/v1-candidate';
 if(httpProfilePath&&!inspecting&&!flags.has('--entry'))throw Error('UnsupportedCapability: HTTP generation requires an Entry selection');
 if((additional.length||externalProfilePath||externalWriteSelectionPath)&&!atomic)throw Error('UnsupportedCapability: additional or external sources require a stateful profile');
 if(externalProfilePath)readBoundedFrontendFile(externalProfilePath);
 if(externalWriteSelectionPath)readBoundedFrontendFile(externalWriteSelectionPath);
 const selection=capabilitySelectionPath?parseCommerceContractJson(readBoundedFrontendFile(capabilitySelectionPath),path.basename(capabilitySelectionPath)):undefined;
 const capabilities=Array.isArray(profile?.capabilities)?profile.capabilities:[],bounded=capabilities.includes('bounded-values'),states=capabilities.includes('StateMachine'),keyed=atomic||profile?.schema_version==='craft.generic-keyed-query-profile/v1-candidate';
 const modules:CommerceParsedModule[]=[];
 let moduleBytes=0;for(const file of [sourcePath,...additionalSourcePaths]){
  const text=readBoundedFrontendFile(file),relative=path.relative(root,file).split(path.sep).join('/');moduleBytes+=Buffer.byteLength(text);
  if(moduleBytes>COMMERCE_SOURCE_LIMITS.total_bytes)sourceFail('ResourceLimit',{path:file,start:0,end:0},'authored frontend modules exceed4MiB');
  if(!atomic)modules.push(parseGenericBusinessSource(text,relative,bounded,states,keyed,atomic));
  else if(selection)modules.push(parseCommerceModuleSource(text,relative));
 }
 if(selection)lowerGenericCapabilitySelectors(modules,selection,capabilitySelectionPath!);
 // Core independently validates selectors, kernel and exact original files;
 // normalized frontend selectors and sidecar data confer no executable authority.
 const owner=await loadGenericCompositionOwner(),handle=await owner.prepare({sourcePath,profilePath,...(httpProfilePath?{httpProfilePath}:{}),...(additional.length?{additionalSourcePaths}:{}),...(externalProfilePath?{externalProfilePath}:{}),...(externalWriteSelectionPath?{externalWriteSelectionPath}:{}),...(capabilitySelectionPath?{capabilitySelectionPath}:{})});
 let failed=false,originalError:unknown,manifest:unknown;
 try{
  if(capabilitySelectionPath&&typeof owner.inspectCapabilities!=='function')throw Error('GENERIC_CAPABILITY_OWNER_API_REQUIRED');
  if(inspecting){
   owner.assertCurrent(handle);
   manifest=owner.inspect(handle);
  }else{
   const reviewer=flags.get('--accept-local-review')!,review=owner.review(handle,reviewer);
   owner.accept(handle,{decision_id:'cli-local-acceptance',owner:reviewer,outcome:'accepted',reviewed_digest:review.review_sha256},path.resolve(flags.get('--out')!)+'.decision.json');
   manifest=owner.generate(handle,{...(flags.has('--entry')?{entry:flags.get('--entry')!}:flags.has('--operation')?{operation:flags.get('--operation')!}:flags.has('--mapping')?{mapping:flags.get('--mapping')!}:flags.has('--calculation')?{calculation:flags.get('--calculation')!}:flags.has('--policy')?{policy:flags.get('--policy')!}:{rule:flags.get('--rule')!}),outputDirectory:path.resolve(flags.get('--out')!)});
  }
 }catch(error){failed=true;originalError=error;throw error;}
 finally{try{owner.dispose(handle);}catch(cleanup){if(failed)throw new AggregateError([originalError,cleanup],'CLI composition and acquired-owner cleanup failed',{cause:originalError});throw cleanup;}}
 process.stdout.write(JSON.stringify(manifest)+'\n');return manifest;
}
// npm invokes package bins through symlinks. Compare the physical entry file so
// the installed command actually runs instead of silently exiting with code 0.
if(process.argv[1]&&realpathSync(process.argv[1])===realpathSync(fileURLToPath(import.meta.url)))genericCompositionMain(process.argv.slice(2)).catch(error=>{process.stderr.write(JSON.stringify({ok:false,error:error instanceof Error?error.message:String(error),diagnostics:error?.diagnostics??[]})+'\n');process.exitCode=1;});
