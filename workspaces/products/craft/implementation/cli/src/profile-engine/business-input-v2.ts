import {captureJson,dataDigest,ProfileRejected,reject} from './contracts.js';
import {validateBusinessApplication,type BusinessApplication,type BusinessApplicationModel} from './contracts-v2.js';
import {assertProfileSnapshotCurrent,type ProfileSnapshotV2,type LoadedPackageV2} from './loader.js';
import {assertAuthoringBusinessInputCurrent,type AuthoringBusinessInput} from './business-authoring-input.js';
import type {TypedTable} from './evaluate.js';

// Open questions: business-only application work pack. Input capture does not prove formal claims.
export interface BusinessApplicationSelector {readonly application_id:string;readonly source:string;readonly selector:string;readonly line:number;readonly text:string;readonly sha256:string}
export interface CapturedBusinessApplication {readonly model:BusinessApplicationModel;readonly source:string;readonly semantics:BusinessApplication;readonly selectors:readonly BusinessApplicationSelector[];readonly source_sha256:string;readonly semantics_sha256:string}
export interface BusinessInputV2 {readonly snapshot:ProfileSnapshotV2;readonly applications:readonly CapturedBusinessApplication[];readonly runtime:LoadedPackageV2;readonly formal_profile:unknown;readonly identity_algorithm:unknown;readonly source_sha256:string;readonly metadata_tables:Readonly<Record<'applications'|'application_models'|'application_declarations',TypedTable>>}
const checked=new WeakSet<object>();
export function prepareBusinessInputV2(snapshot:ProfileSnapshotV2):BusinessInputV2 {
 assertProfileSnapshotCurrent(snapshot);
 const runtimes=snapshot.packages.filter((p):p is LoadedPackageV2=>p.data.schema_version==='craft.profile-package/v2-candidate');
 if(snapshot.project.application_models.length&&runtimes.length!==1)reject('PROFILE_APPLICATION_RUNTIME_AMBIGUOUS','/profiles','one registered application mechanism owner required; selection ordering cannot resolve conflict');
 const runtime=runtimes[0];if(!runtime)reject('PROFILE_APPLICATION_RUNTIME_REQUIRED','/profiles','v2 business preparation requires a selected v2 application package');
 const applications=snapshot.project.application_models.map(model=>{
  const sourceFile=snapshot.sources[model.source],semanticFile=snapshot.sources[model.semantics];if(!sourceFile?.text||!semanticFile?.text)reject('PROFILE_APPLICATION_SOURCE_MISSING',model.id,'captured original source and semantics required');
  const source=sourceFile.text,semantics=validateBusinessApplication(JSON.parse(semanticFile.text)),selectors:BusinessApplicationSelector[]=[];let declaration:string|undefined,owners=0,domains=0;
  for(const [index,line] of source.split('\n').entries()){
   const trimmed=line.trim();if(!trimmed||trimmed.startsWith('#'))continue;
   if(line.includes('\t'))reject('PROFILE_BUSINESS_INDENT',model.id+':'+(index+1),'explicit space indentation required');
   if(!line.startsWith(' ')){
    if(/^domain\s/.test(line)){domains++;declaration=undefined;continue;}
    if(/^owner\s/.test(line)){owners++;if(line.slice(6).trim()!==semantics.owner)reject('PROFILE_BUSINESS_OWNER',model.id,'authored source and accepted meaning owner differ');declaration=undefined;continue;}
    const match=/^(formal-claim|rule|entity|value-object|mapping|operation)\s+([A-Za-z_][A-Za-z0-9_-]*)\s*:/.exec(line);
    if(!match)reject('PROFILE_BUSINESS_DECLARATION_UNSUPPORTED',model.id+':'+(index+1),'unsupported required business declaration or technical carrier');
    declaration=match[1]+':'+match[2];if(selectors.some(s=>s.selector===declaration))reject('PROFILE_BUSINESS_SELECTOR_DUPLICATE',declaration,'exact declaration identity required');
   }else{
    if(!declaration)reject('PROFILE_BUSINESS_CLAUSE_ORPHAN',model.id+':'+(index+1),'clause must belong to an authored declaration');
    if(/^(transport|runtime|endpoint|path|method|url-env|secret-env|timeout-ms|max-bytes|provider|execution|interpretation|native)\b/.test(trimmed))reject('PROFILE_TECHNICAL_SOURCE_FORBIDDEN',model.id+':'+(index+1),'no technical companion clause in business source');
   }
   selectors.push(Object.freeze({application_id:model.id,source:model.source,selector:line.startsWith(' ')?declaration+'#clause:'+(index+1):declaration!,line:index+1,text:line,sha256:sourceFile.sha256}));
  }
  if(owners!==1||domains!==1)reject('PROFILE_BUSINESS_IDENTITY',model.id,'one exact domain/owner required');
  for(const intent of snapshot.project.application_intents.filter(i=>i.application_id===model.id)){
   if(!selectors.some(s=>s.selector==='operation:'+intent.operation_ref)||!selectors.some(s=>s.selector==='mapping:'+intent.mapping_ref))reject('PROFILE_APPLICATION_INTENT_UNKNOWN',intent.id,'public Mapping and Operation must be explicitly authored');
  }
  return Object.freeze({model,source,semantics,selectors:Object.freeze(selectors),source_sha256:sourceFile.sha256,semantics_sha256:semanticFile.sha256});
 });
 const data=runtime.data.application_runtime,read=(id:string)=>{const asset=runtime.assets[id];if(!asset?.text)reject('PROFILE_RUNTIME_ASSET_REQUIRED',id,'captured formal resource required');return captureJson(JSON.parse(asset.text));};
 const metadata_tables=captureJson({
  applications:{fields:{id:'string',source:'string',selector:'string',application_id:'string',mapping_ref:'string'},rows:snapshot.project.application_intents.map(intent=>({id:intent.id,source:applications.find(a=>a.model.id===intent.application_id)!.model.source,selector:intent.operation_ref,application_id:intent.application_id,mapping_ref:intent.mapping_ref}))},
  application_models:{fields:{id:'string',source:'string',semantics:'string'},rows:snapshot.project.application_models},
  application_declarations:{fields:{id:'string',source:'string',selector:'string',application_id:'string'},rows:applications.flatMap(a=>a.selectors.filter(s=>!s.selector.includes('#clause:')).map(s=>({id:s.selector.split(':')[1]!,source:s.source,selector:s.selector,application_id:a.model.id})))},
 }) as unknown as BusinessInputV2['metadata_tables'];
 const input=Object.freeze({snapshot,applications:Object.freeze(applications),runtime,formal_profile:read(data.formal_profile_asset),identity_algorithm:read(data.identity_algorithm_asset),source_sha256:snapshot.lock.source_sha256,metadata_tables});checked.add(input);assertBusinessInputV2Current(input);return input;
}
function registeredV2(input:BusinessInputV2|AuthoringBusinessInput):input is BusinessInputV2 {return checked.has(input);}
export function assertBusinessInputV2Current(input:BusinessInputV2|AuthoringBusinessInput):void {
 if(registeredV2(input)){assertProfileSnapshotCurrent(input.snapshot);return;}
 try{assertAuthoringBusinessInputCurrent(input);}
 catch(error){if(error instanceof ProfileRejected&&error.code==='BUSINESS_AUTHORING_INPUT_UNREGISTERED')reject('PROFILE_BUSINESS_INPUT_UNREGISTERED','/','prepare the exact captured v2 or authoring input in this process');throw error;}
}
