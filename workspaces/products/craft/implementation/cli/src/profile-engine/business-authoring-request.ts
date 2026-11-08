import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,writeSync,fchmodSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {captureJson,dataDigest,reject,sha256} from './contracts.js';
import {assertBusinessRecipeSelectionCurrent,type BusinessRecipeSelection} from './business-authoring-recipes.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import {BUSINESS_AUTHORING_LIMITS,BUSINESS_AUTHORING_RECIPE,type BusinessDerivationOrigin,type BusinessLoweringLedger,type BusinessScalar} from './business-authoring-protocol.js';
import type {BusinessRecipeModelInput} from './business-authoring-normalization-protocol.js';
import type {BusinessApplicationIntent} from './contracts-v2.js';
import {decodeRequestApplicationSourceV1,type RequestApplicationEntryV1,type RequestApplicationSourceV1} from '../system-integration/request-application-source-v1.js';
import {decodeRequestApplicationSourceV2,REQUEST_APPLICATION_SOURCE_V2_MODULE_URL,type RequestApplicationIntentSourceV2} from '../system-integration/request-application-source-v1.js';
import {composeDirectRequestApplicationPlanDataV2,REQUEST_APPLICATION_PLAN_V2_MODULE_URL} from '../generation/request-application-plan-v1.js';
import {checkCoreDirectBusinessRecipeV2,type CoreDirectRecipeDataV2} from './business-authoring-recipes.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2} from './business-authoring-identity-v2.js';
import type {BusinessCoreRecipeOwnerV2,BusinessPureGenerationOwnerV2,BusinessRequestStagesOwnerV2,ImportedU0CallableV2,BoundU0EntryV2,U0FileArtifactV2} from './business-authoring-stages-v2.js';
import type {BusinessRecipeSelectionV2,BusinessEarlyRequestsV2} from './business-authoring-identity-protocol-v2.js';
import type {U0ResolvedNativeBasis,U0RealizedApplicationSubject,U0InjectedHandler,U0WireConfiguration} from './u0-realization-contract.js';

/** Pure B07.1 protocol declarations. Alch must insert/parse these before later checked compilation.
 * No acceptance, graph or callable is constructed. Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md. */
export interface BusinessAuthoringRequestMapping {
 readonly exposure_id:string;readonly exposure_key:string;readonly public_name:string;readonly operation_id:string;
 readonly mapping_id:string;readonly operation_selector:string;readonly mapping_selector:string;
 readonly input_parameter:'body';readonly input_entity:string;
 readonly fields:readonly Readonly<{target:string;path:readonly ['body',string];type:BusinessScalar}>[];
 readonly source_fragment:string;readonly declaration_binding:Readonly<{ontology:string;meaning:string}>;
}
export interface BusinessAuthoringRequestModel {
 readonly model_id:string;readonly feature:string;readonly source_fragment:string;
 readonly mappings:readonly BusinessAuthoringRequestMapping[];
 readonly declaration_bindings:Readonly<Record<string,Readonly<{ontology:string;meaning:string}>>>;
 readonly project_intents:readonly BusinessApplicationIntent[];readonly request_source:RequestApplicationSourceV1;
}
export interface BusinessAuthoringRequestPreparation {
 readonly kind:'business-authoring-request-preparation';readonly selection:BusinessRecipeSelection;
 readonly models:readonly BusinessAuthoringRequestModel[];readonly project_intents:readonly BusinessApplicationIntent[];
 readonly request_source:RequestApplicationSourceV1;readonly ledger:BusinessLoweringLedger;
 readonly derivation_sha256:string;readonly authority_effect:'none';
}
const registry=new WeakMap<object,{selection:BusinessRecipeSelection;module:string;digest:string}>();
const artifact='business-authoring-request-preparation.json';
function fail(code:string,at:string,message:string):never{return reject('BUSINESS_REQUEST_'+code,at,message);}
function symbol(value:string,at:string,separator='-'):string {
 const result=value.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
 if(!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(result)||['constructor','prototype','__proto__'].includes(value))fail('IDENTITY',at,'unsupported backend identity');
 return result.replaceAll('-',separator);
}
function reserve(set:Set<string>,value:string,at:string):void {if(set.has(value))fail('COLLISION',at,'identity or route collision; explicit names cannot be renamed');set.add(value);}
function bounded(value:string,max:number,at:string):string {if(Buffer.byteLength(value,'ascii')>max)fail('IDENTITY_BUDGET',at,'generated identity exceeds its fixed limit');return value;}
function sourceClause(model:BusinessRecipeModelInput,kind:string,id:string,clause:(text:string)=>boolean):BusinessDerivationOrigin {
 const spans=model.spec.source_spans,header=spans.find(span=>span.text===`${kind} ${id}:`);
 if(!header)fail('ORIGIN','/models/'+model.model_id,'exact original declaration span required');
 const next=spans.find(span=>span.line>header!.line&&span.column===1),selected=spans.find(span=>span.line>header!.line&&(!next||span.line<next.line)&&clause(span.text.trim()));
 if(!selected)fail('ORIGIN','/models/'+model.model_id,'exact original clause/field span required');
 return {kind:'business',source:model.source.path,selector:selected!.selector,sha256:model.source.sha256};
}
function implementationIdentity():Readonly<{fingerprint:string;sha256:string}> {
 const filename=fileURLToPath(import.meta.url);let cursor=path.parse(filename).root;const owners:string[]=[];
 for(const part of filename.slice(cursor.length).split(path.sep).filter(Boolean)){cursor=path.join(cursor,part);const info=lstatSync(cursor,{bigint:true});if(info.isSymbolicLink())fail('IMPLEMENTATION_STALE',filename,'implementation cannot use substituted symlinks');owners.push(`${info.dev}:${info.ino}`);}
 const before=lstatSync(filename,{bigint:true});if(!before.isFile()||before.size>16777216n)fail('IMPLEMENTATION_STALE',filename,'bounded regular implementation required');
 const fd=openSync(filename,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),buffers:Buffer[]=[];let bytes=0;
 try{
  const opened=fstatSync(fd,{bigint:true});if(!opened.isFile()||opened.dev!==before.dev||opened.ino!==before.ino)fail('IMPLEMENTATION_STALE',filename,'implementation changed while opening');
  for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>16777216)fail('IMPLEMENTATION_STALE',filename,'implementation byte budget exceeded');buffers.push(buffer.subarray(0,count));}
  const after=fstatSync(fd,{bigint:true});if(after.size!==before.size||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs)fail('IMPLEMENTATION_STALE',filename,'implementation changed while reading');
 }finally{closeSync(fd);}
 const after=lstatSync(filename,{bigint:true});if(after.dev!==before.dev||after.ino!==before.ino||after.ctimeNs!==before.ctimeNs||after.mtimeNs!==before.mtimeNs)fail('IMPLEMENTATION_STALE',filename,'implementation path changed');
 const content=sha256(Buffer.concat(buffers));return {fingerprint:dataDigest({owners,sha256:content,bytes,mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)}),sha256:content};
}
const executingImplementation=implementationIdentity().fingerprint;
export function prepareBusinessAuthoringRequests(selection:BusinessRecipeSelection):BusinessAuthoringRequestPreparation {
 assertBusinessRecipeSelectionCurrent(selection);
 const implementation=implementationIdentity();if(implementation.fingerprint!==executingImplementation)fail('IMPLEMENTATION_STALE','/','reload the changed implementation before preparing requests');
 const wire=selection.technical.wire;validateBusinessAuthoringContract('wire',wire);
 if(wire.method!=='POST'||wire.body!=='whole-input'||selection.requirements.effects!=='none')fail('WIRE','/technical/wire','only the selected whole-body public POST convention is supported');
 const profileOrigin:BusinessDerivationOrigin={kind:'profile',source:'profile:'+selection.technical.profile_id,selector:'/authoring/wire',sha256:selection.technical.manifest_sha256};
 const adapterOrigin:BusinessDerivationOrigin={kind:'semantic-adapter',source:'craft.business-authoring-request/v1-candidate',selector:'identity-mapping/1-candidate',sha256:implementation.sha256};
 const models:BusinessAuthoringRequestModel[]=[],allIntents:BusinessApplicationIntent[]=[],allEntries:RequestApplicationEntryV1[]=[],ledger:BusinessLoweringLedger['entries'][number][]=[];
 const features=new Set<string>(),exposureKeys=new Set<string>(),mappingIds=new Set<string>(),selectors=new Set<string>(),publicIds=new Set<string>(),publicSymbols=new Set<string>(),routes=new Set<string>(),routeSymbols=new Set<string>(),ontologies=new Set<string>();
 const record=(id:string,pointer:string,origins:readonly BusinessDerivationOrigin[])=>ledger.push({id,origins,target:{artifact,pointer}});
 for(const [modelIndex,model] of selection.models.entries()){
  const feature=symbol(model.model_id,'/models/'+modelIndex),base='/models/'+modelIndex;
  reserve(features,feature,base+'/feature');
  const authored=[...model.spec.entities,...model.spec.rules,...model.spec.operations,...model.spec.definitions,...model.spec.claims,...model.spec.requirements,...model.spec.capabilities];
  const localSymbols=new Set<string>();for(const declaration of authored)reserve(localSymbols,symbol(declaration.id,base+'/declarations'),base+'/declarations');
  const mappings:BusinessAuthoringRequestMapping[]=[],bindings:Record<string,{ontology:string;meaning:string}>=Object.create(null),intents:BusinessApplicationIntent[]=[],entries:RequestApplicationEntryV1[]=[];
  const exposures=[...model.behavior.exposures].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
  if(!exposures.length)fail('EXPOSURE',base,'an application model must have an explicit public exposure');
  for(const [mappingIndex,exposure] of exposures.entries()){
   const at=base+'/mappings/'+mappingIndex,exposureSymbol=symbol(exposure.id,at+'/exposure_id'),exposureKey=feature+'-'+exposureSymbol;
   reserve(exposureKeys,exposureKey,at+'/exposure_key');
   const operation=model.behavior.operations.find(operation=>operation.operation_ref===exposure.operation_ref),authoredOperation=model.spec.operations.find(operation=>operation.id===exposure.operation_ref);
   if(!operation||!authoredOperation||exposure.audience!=='public'||operation.effects.length||operation.input.type.entity_ref!==operation.output.entity_ref||operation.result.path.length||operation.result.root!==operation.input.name)fail('CORRESPONDENCE',at,'whole-input zero-effects operation and explicit public exposure required');
   const entity=model.spec.entities.find(entity=>entity.id===operation!.input.type.entity_ref);if(!entity)fail('CORRESPONDENCE',at+'/input_entity','declared input Entity required');
   const fieldNames=new Set<string>();for(const field of entity!.fields){reserve(fieldNames,symbol(field.name,at+'/fields','_'),at+'/fields');if(!['UInt64','String','Bool'].includes(field.type))fail('TYPE',at+'/fields','unsupported request field scalar');}
   const mappingId=bounded('CraftRequest_'+symbol(model.model_id,at,'_')+'_'+symbol(exposure.id,at,'_'),128,at+'/mapping_id'),mappingSymbol=symbol(mappingId,at+'/mapping_id');
   reserve(mappingIds,mappingId,at+'/mapping_id');reserve(localSymbols,mappingSymbol,at+'/mapping_id');
   const mappingSelector=bounded(feature+':'+mappingSymbol,256,at+'/mapping_selector'),operationSelector=bounded(feature+':'+symbol(operation!.operation_ref,at+'/operation_id'),256,at+'/operation_selector');
   reserve(selectors,mappingSelector,at+'/mapping_selector');
   const publicName=exposure.public_name,publicSymbol=symbol(publicName,at+'/public_name');
   reserve(publicIds,publicName,at+'/public_name');reserve(publicSymbols,publicSymbol,at+'/public_name');
   const route=wire.route_prefix+publicName;bounded(route,256,at+'/route');reserve(routes,route,at+'/route');
   const normalizedRoute=route.split('/').filter(Boolean).map(part=>symbol(part,at+'/route')).join('/');reserve(routeSymbols,normalizedRoute,at+'/route');
   const fields=[...entity!.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0).map(field=>({target:field.name,path:['body',field.name] as const,type:field.type}));
   if(fields.length!==operation!.input.type.fields.length||fields.some((field,index)=>field.target!==operation!.input.type.fields[index]?.name||field.type!==operation!.input.type.fields[index]?.type))fail('CORRESPONDENCE',at+'/fields','exact complete typed input field identity required');
   const fragment=`mapping ${mappingId}:\n  input body ${entity!.id}\n  target ${entity!.id}\n  total true\n${fields.map(field=>`  field ${field.target} <- body.${field.target}\n`).join('')}`;
   const binding={ontology:'PROTOCOL-'+feature.toUpperCase()+'-'+exposureSymbol.toUpperCase()+'-REQUEST',meaning:`Protocol identity Mapping from the whole request body to ${entity!.id} without changing declared fields.`};
   if(binding.meaning.length>4096||!/^PROTOCOL-[A-Z0-9]+(?:-[A-Z0-9]+)+$/.test(binding.ontology))fail('METADATA',at,'bounded technical Mapping metadata required');reserve(ontologies,binding.ontology,at+'/declaration_binding/ontology');
   mappings.push({exposure_id:exposure.id,exposure_key:exposureKey,public_name:publicName,operation_id:operation!.operation_ref,mapping_id:mappingId,operation_selector:operationSelector,mapping_selector:mappingSelector,input_parameter:'body',input_entity:entity!.id,fields,source_fragment:fragment,declaration_binding:binding});bindings[mappingId]=binding;
   const intent:BusinessApplicationIntent={id:publicName,application_id:model.model_id,operation_ref:operation!.operation_ref,mapping_ref:mappingId,mapping_arguments:{body:{root:'body',path:[]}},access:{kind:'public'}};
   const entry:RequestApplicationEntryV1={id:publicName,operation_ref:operationSelector,mapping_ref:mappingSelector,mapping_arguments:[{parameter:'body',path:[]}],request_parameter:symbol(operation!.input.name,at+'/request_parameter','_'),route:{method:'POST',path:route},access:{kind:'public'}};
   intents.push(intent);allIntents.push(intent);entries.push(entry);allEntries.push(entry);
   const inputOrigin=sourceClause(model,'operation',operation!.operation_ref,text=>text===`input ${authoredOperation!.input.name} ${entity!.id}`),exposureOrigin=sourceClause(model,'capability',exposure.id,text=>text===`invokes ${operation!.operation_ref}`);
   const origins=[inputOrigin,exposureOrigin,profileOrigin,adapterOrigin];
   record(exposureKey+'/mapping',at+'/source_fragment',origins);record(exposureKey+'/declaration',at+'/declaration_binding',origins);
   record(exposureKey+'/intent',base+'/project_intents/'+mappingIndex,origins);record(exposureKey+'/request',base+'/request_source/entries/'+mappingIndex,origins);
   for(const [fieldIndex,field] of fields.entries())record(exposureKey+'/field/'+field.target,at+'/fields/'+fieldIndex,[sourceClause(model,'entity',entity!.id,text=>text.startsWith(`${field.target} ${field.type} meaning `)),inputOrigin,exposureOrigin,profileOrigin,adapterOrigin]);
  }
  const requestSource=decodeRequestApplicationSourceV1({schema_version:'domainspec.request-application-source/v1-candidate',source_id:feature,entries});
  models.push({model_id:model.model_id,feature,source_fragment:mappings.map(mapping=>mapping.source_fragment).join('\n'),mappings,declaration_bindings:bindings,project_intents:intents,request_source:requestSource});
 }
 if(!allEntries.length||allEntries.length>BUSINESS_AUTHORING_LIMITS.intents||allEntries.length>BUSINESS_AUTHORING_LIMITS.total_entries)fail('ENTRY_BUDGET','/models','bounded complete explicit public entries required');
 const source=decodeRequestApplicationSourceV1({schema_version:'domainspec.request-application-source/v1-candidate',source_id:'business-authoring-requests',entries:allEntries});
 const lowering=validateBusinessAuthoringContract<BusinessLoweringLedger>('ledger',{schema_version:'craft.business-lowering/v1-candidate',recipe_ref:BUSINESS_AUTHORING_RECIPE,business_sha256:selection.business_sha256,lock_sha256:selection.technical.lock_sha256,entries:ledger,authority_effect:'none'});
 const body=captureJson({kind:'business-authoring-request-preparation',models,project_intents:allIntents,request_source:source,ledger:lowering,authority_effect:'none'}) as unknown as Omit<BusinessAuthoringRequestPreparation,'selection'|'derivation_sha256'>;
 const content={...body,selection},digest=dataDigest(content),result=Object.freeze({...content,derivation_sha256:digest});
 registry.set(result,{selection,module:implementation.fingerprint,digest});assertBusinessAuthoringRequestsCurrent(result);return result;
}
export function assertBusinessAuthoringRequestsCurrent(value:BusinessAuthoringRequestPreparation):void {
 const state=registry.get(value);if(!state)fail('UNREGISTERED','/','only the original Core-registered preparation is current');
 assertBusinessRecipeSelectionCurrent(state.selection);
 let identity:string;try{identity=implementationIdentity().fingerprint;}catch{return fail('IMPLEMENTATION_STALE','/','owning request implementation is unavailable or changed');}
 const {derivation_sha256,...content}=value;
 if(value.selection!==state.selection||identity!==state.module||derivation_sha256!==state.digest||dataDigest(content)!==state.digest)fail('STALE','/','request preparation data or owning implementation changed');
}

/** Pure source/Mapping intent projection, not an early handle or native binding.
 * Open Questions: Q02 current selected flow and U08 real late artifact witness. */
export function deriveDirectBusinessRequestSourceV2(transfer:unknown):RequestApplicationIntentSourceV2 {
 const checked=checkCoreDirectBusinessRecipeV2(transfer),spec=checked.transfer.spec,entity=spec.entities[0]!,operation=spec.operations[0]!,entry=spec.entries[0]!,roles=checked.roles;
 const origin=(kind:string,id:string,predicate:(text:string)=>boolean,tag:'entry'|'permission'|'operation-input'|'entity-field')=>{
  const spans=spec.source_spans,header=spans.find(span=>span.text===kind+' '+id+':');if(!header)fail('ORIGIN','/request-v2','original containing declaration required');
  const next=spans.find(span=>span.line>header.line&&span.column===1);
  const matches=tag==='entry'?[header]:spans.filter(span=>span.line>header.line&&(!next||span.line<next.line)&&predicate(span.text.trim()));
  if(matches.length!==1)fail('ORIGIN','/request-v2','one exact original request fact required');const span=matches[0]!;
  return {kind:tag,source:span.source,selector:span.selector,sha256:span.source_sha256};
 };
 const entityProperty='BUSINESS-'+roles.feature.toUpperCase()+'-'+roles.selectors.entity.split(':')[1]!.toUpperCase();
 const payloadProperty='BUSINESS-'+roles.feature.toUpperCase()+'-'+roles.selectors.entry.split(':')[1]!.toUpperCase()+'-PAYLOAD';
 const fields=[...entity.fields].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);
 return decodeRequestApplicationSourceV2({schema_version:'domainspec.request-application-source/v2-candidate',model_id:spec.identity.namespace,source_sha256:checked.transfer.source.sha256,executable_sha256:checked.executable_sha256,
  entries:[{logical_id:entry.id,public_name:entry.public_name,operation_ref:roles.selectors.operation,rule_ref:roles.selectors.rule,interface_ref:roles.selectors.entry,permission:entry.permission,payload:{kind:'whole-input',parameter:operation.input.name,type_ref:entity.id},
   mappings:{input:roles.selectors.input_mapping,output:roles.selectors.output_mapping,fields:fields.map(field=>({name:field.name,scalar:field.type,identity:field.name===entity.identity,source_property:payloadProperty+'#'+field.name,target_property:entityProperty+'#'+field.name}))},
   origins:[origin('entry',entry.id,()=>true,'entry'),origin('entry',entry.id,text=>text==='permission public','permission'),origin('operation',operation.id,text=>text==='input '+operation.input.name+' '+operation.input.type_ref,'operation-input'),...fields.map(field=>origin('entity',entity.id,text=>text.startsWith(field.name+' '+field.type+' meaning '),'entity-field'))]}],authority_effect:'none'});
}
export interface U0RequestRuntimeFileV2 {
 readonly role:'decoder'|'values'|'encoder'|'handler';readonly basis_artifact_id:string;readonly artifact:U0FileArtifactV2;
}
/** Trusted SDK loader capability, never business/profile JSON. J01 retains the
 * actual selected-basis pointer and supplies actual registered runtime paths. */
export interface U0RequestNativeAssetsOwnerV2 {
 assertCurrent(basis:U0ResolvedNativeBasis):void;
 assertSelectionBasis(selection:BusinessRecipeSelectionV2,basis:U0ResolvedNativeBasis):void;
 assets(basis:U0ResolvedNativeBasis):readonly U0RequestRuntimeFileV2[];
}
export interface BusinessRequestStageImplementationV2 extends BusinessRequestStagesOwnerV2 {
 source(early:BusinessEarlyRequestsV2):RequestApplicationIntentSourceV2;
}
interface RequestOwnedFileV2 {artifact:U0FileArtifactV2;fingerprint:string;device:string;inode:string;parents:readonly Readonly<{path:string;dev:string;ino:string}>[]}
function requestFileV2(file:string):RequestOwnedFileV2 {
 if(typeof file!=='string'||file.length>4096||!path.isAbsolute(file)||path.normalize(file)!==file||/[\\\u0000-\u001f\u007f]/.test(file))fail('FILE','/native-v2','normalized absolute actual artifact required');
 const parents=()=>{
  let at=path.parse(file).root;const result:{path:string;dev:string;ino:string}[]=[];
  for(const part of ['',...path.dirname(file).slice(at.length).split(path.sep).filter(Boolean)]){
   if(part)at=path.join(at,part);const stat=lstatSync(at,{bigint:true});if(!stat.isDirectory()||stat.isSymbolicLink())fail('FILE',file,'original nonsymlink parent required');result.push({path:at,dev:String(stat.dev),ino:String(stat.ino)});
  }return result;
 };
 const chain=parents(),before=lstatSync(file,{bigint:true});if(!before.isFile()||before.isSymbolicLink()||before.size<1n||before.size>16777216n)fail('FILE',file,'bounded regular actual runtime file required');
 const physical=(stat:typeof before)=>[stat.dev,stat.ino,stat.size,stat.mode,stat.mtimeNs,stat.ctimeNs].map(String);
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);let size=0;const chunks:Buffer[]=[];
 try{
  if(dataDigest(physical(fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))fail('FILE_STALE',file,'file changed while opening');
  for(;;){const chunk=Buffer.alloc(65536),n=readSync(fd,chunk,0,chunk.length,null);if(!n)break;size+=n;if(size>16777216)fail('FILE',file,'actual artifact byte budget exceeded');chunks.push(chunk.subarray(0,n));}
  if(dataDigest(physical(fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))fail('FILE_STALE',file,'file changed while reading');
 }finally{closeSync(fd);}
 const after=lstatSync(file,{bigint:true});if(!after.isFile()||dataDigest(physical(after))!==dataDigest(physical(before))||size!==Number(before.size)||dataDigest(parents())!==dataDigest(chain))fail('FILE_STALE',file,'original file/parent identity changed');
 const artifact=Object.freeze({path:file,sha256:sha256(Buffer.concat(chunks)),bytes:size});return {artifact,fingerprint:dataDigest({artifact,parents:chain,physical:physical(before)}),device:String(before.dev),inode:String(before.ino),parents:chain};
}
function writeRequestFileV2(file:string,content:string,parent:RequestOwnedFileV2):RequestOwnedFileV2 {
 const directory=path.dirname(file),expected=parent.parents[parent.parents.length-1]!;
 if(directory!==expected.path)fail('OUTPUT','/request-v2','fresh request outputs must share the original owned callable directory');
 const fd=openSync(directory,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW|constants.O_NONBLOCK);let output:number|undefined;
 try{
  const stat=fstatSync(fd,{bigint:true});if(String(stat.dev)!==expected.dev||String(stat.ino)!==expected.ino)fail('FILE_STALE',file,'output parent changed');
  try{output=openSync(`/proc/self/fd/${fd}/${path.basename(file)}`,constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW|constants.O_NONBLOCK,0o600);}catch{return fail('OUTPUT_OCCUPIED',file,'request outputs must be new; no overwrite or cleanup by pathname');}
  fchmodSync(output,0o600);const created=fstatSync(output,{bigint:true}),bytes=Buffer.from(content);let offset=0;
  while(offset<bytes.length){const n=writeSync(output,bytes,offset,bytes.length-offset,null);if(n<=0)fail('OUTPUT',file,'complete fresh output write required');offset+=n;}
  const written=fstatSync(output,{bigint:true});if(!written.isFile()||created.dev!==written.dev||created.ino!==written.ino||written.size!==BigInt(bytes.length)||(written.mode&0o777n)!==0o600n)fail('OUTPUT',file,'fresh output identity/size/private mode differs');
  closeSync(output);output=undefined;const actual=requestFileV2(file);
  if(actual.device!==String(created.dev)||actual.inode!==String(created.ino)||actual.artifact.sha256!==sha256(bytes)||actual.parents[actual.parents.length-1]?.dev!==expected.dev||actual.parents[actual.parents.length-1]?.ino!==expected.ino)fail('OUTPUT',file,'fresh output path or bytes replaced');
  return actual;
 }finally{try{if(output!==undefined)closeSync(output);}finally{closeSync(fd);}}
}
const requestImplementationV2=()=>dataDigest({owner:implementationIdentity().fingerprint,source:requestFileV2(fileURLToPath(REQUEST_APPLICATION_SOURCE_V2_MODULE_URL)).fingerprint,plan:requestFileV2(fileURLToPath(REQUEST_APPLICATION_PLAN_V2_MODULE_URL)).fingerprint});
const executingRequestImplementationV2=requestImplementationV2();
/** Actual selected early/late registries. Successful handles are Q02/U08 witnesses,
 * not manufactured during source implementation or component contract tests. */
export function createBusinessRequestStagesOwnerV2(recipes:BusinessCoreRecipeOwnerV2,generation:BusinessPureGenerationOwnerV2,native:U0RequestNativeAssetsOwnerV2):BusinessRequestStageImplementationV2 {
 const recipeMethods=[recipes.select,recipes.assertCurrent,recipes.dispose],generationMethods=[generation.generate,generation.importGenerated,generation.assertCurrent],nativeMethods=[native.assertCurrent,native.assertSelectionBasis,native.assets];
 const earlyOwned=new WeakMap<object,{selection:BusinessRecipeSelectionV2;source:RequestApplicationIntentSourceV2;checked:CoreDirectRecipeDataV2;fingerprint:string}>();
 const boundOwned=new WeakMap<object,{early:BusinessEarlyRequestsV2;callable:ImportedU0CallableV2;basis:U0ResolvedNativeBasis;files:readonly RequestOwnedFileV2[];handler:U0InjectedHandler;fingerprint:string}>();
 const current=()=>{
  if(requestImplementationV2()!==executingRequestImplementationV2||[recipes.select,recipes.assertCurrent,recipes.dispose].some((m,i)=>m!==recipeMethods[i])||[generation.generate,generation.importGenerated,generation.assertCurrent].some((m,i)=>m!==generationMethods[i])||[native.assertCurrent,native.assertSelectionBasis,native.assets].some((m,i)=>m!==nativeMethods[i]))fail('OWNER_STALE','/request-v2','exact stage owners or implementation changed');
 };
 const assertEarlyCurrent=(early:BusinessEarlyRequestsV2):void=>{
  const state=early&&typeof early==='object'?earlyOwned.get(early):undefined;if(!state)fail('UNREGISTERED','/early-v2','original early handle from this exact owner required');
  current();recipes.assertCurrent(state.selection);
  if(early.selection!==state.selection||dataDigest(early)!==state.fingerprint)fail('STALE','/early-v2','original selected early data changed');
 };
 const boundFingerprint=(bound:BoundU0EntryV2)=>dataDigest({kind:bound.kind,early_sha256:bound.early.request_sha256,callable_sha256:bound.callable.artifact.sha256,basis_sha256:bound.basis.basis_sha256,handler_artifact:bound.handler_artifact,subject:bound.subject,authority_effect:bound.authority_effect});
 const assertBoundCurrent=(bound:BoundU0EntryV2):void=>{
  const state=bound&&typeof bound==='object'?boundOwned.get(bound):undefined;if(!state)fail('UNREGISTERED','/bound-v2','original bound entry from this exact owner required');
  assertEarlyCurrent(state.early);generation.assertCurrent(state.callable);native.assertCurrent(state.basis);native.assertSelectionBasis(state.early.selection,state.basis);
  if(bound.early!==state.early||bound.callable!==state.callable||bound.basis!==state.basis||bound.handler!==state.handler||boundFingerprint(bound)!==state.fingerprint)fail('STALE','/bound-v2','actual original native/early/callable lineage changed');
  for(const file of state.files)if(requestFileV2(file.artifact.path).fingerprint!==file.fingerprint)fail('FILE_STALE',file.artifact.path,'original native/generated file changed');
 };
 return Object.freeze({prepareEarly(selection:BusinessRecipeSelectionV2):BusinessEarlyRequestsV2{
  current();recipes.assertCurrent(selection);if(selection.models.length!==1)fail('MODEL','/early-v2','one selected pure U0 model required');
  const model=selection.models[0]!,transfer={source:model.source,spec:model.spec,executable:projectDirectExecutableV2(model.spec),assurance:projectOptionalAssuranceV2(model.spec)},checked=checkCoreDirectBusinessRecipeV2(transfer),source=deriveDirectBusinessRequestSourceV2(transfer),entry=model.spec.entries[0]!,operation=model.spec.operations[0]!;
  const body={kind:'business-early-requests-v2',entries:[{model_id:model.model_id,entry_id:entry.id,operation_ref:entry.operation_ref,rule_ref:model.spec.rules[0]!.id,permission:entry.permission,payload:{kind:'whole-input',parameter:operation.input.name,type_ref:operation.input.type_ref},unresolved_native_obligations:[{producer:'generated-callable',abi_ref:'craft.u0.pure-submission/v1-candidate'},{producer:'exact-codec',abi_ref:'craft.operation-json-post/v2-candidate'},{producer:'injected-handler',abi_ref:'craft.u0.pure-submission/v1-candidate'},{producer:'request-graph',abi_ref:'domainspec.direct-request-graph/v2-candidate'}]}],authority_effect:'none'};
  const data=captureJson(body) as unknown as Omit<BusinessEarlyRequestsV2,'selection'|'request_sha256'>;
  const early:BusinessEarlyRequestsV2=Object.freeze({...data,selection,request_sha256:dataDigest({...data,selection_sha256:selection.selection_sha256,source})});
  earlyOwned.set(early,{selection,source,checked,fingerprint:dataDigest(early)});assertEarlyCurrent(early);return early;
 },assertEarlyCurrent,source(early:BusinessEarlyRequestsV2){assertEarlyCurrent(early);return earlyOwned.get(early)!.source;},
 async bindLate(early:BusinessEarlyRequestsV2,callable:ImportedU0CallableV2,basis:U0ResolvedNativeBasis):Promise<BoundU0EntryV2>{
  assertEarlyCurrent(early);generation.assertCurrent(callable);native.assertCurrent(basis);native.assertSelectionBasis(early.selection,basis);
  const state=earlyOwned.get(early)!,application=callable.source.application,input=application.input;
  if(input.selection!==early.selection||input.early_requests!==early||input.model_id!==state.source.model_id||application.graph.input!==input||application.condition.graph!==application.graph||input.capture.capture_sha256!==early.selection.models[0]!.capture.capture_sha256||dataDigest(input.spec)!==dataDigest(state.checked.transfer.spec)||callable.source.abi!==basis.abi||basis.abi!=='craft.u0.pure-submission/v1-candidate'||basis.descriptor!=='node-http-entry-u0-v4'||early.selection.native_basis.basis_sha256!==basis.basis_sha256||early.selection.native_basis.sdk_sha256!==basis.sdk_sha256||early.selection.native_basis.configuration_sha256!==dataDigest(basis.configuration))fail('LINEAGE','/bound-v2','original input, early, selection, callable and basis must correspond');
  const runtime=captureJson(native.assets(basis)) as unknown as readonly U0RequestRuntimeFileV2[];
  if(!Array.isArray(runtime)||runtime.length!==4||new Set(runtime.map(row=>row.role)).size!==4)fail('NATIVE_ASSETS','/bound-v2','all four actual registered runtime roles required');
  const required={decoder:['decodeU0Json'],values:['formU0Submission','copyU0Submission'],encoder:['checkU0EncoderConfiguration','encodeU0Outcome','encodeU0AdapterError','u0WireBounds'],handler:['createU0HttpHandler']} as const;
  const files:RequestOwnedFileV2[]=[];
  for(const role of ['decoder','values','encoder','handler'] as const){
   const row=runtime.find(row=>row.role===role);if(!row||Object.keys(row).sort().join(',')!=='artifact,basis_artifact_id,role')fail('NATIVE_ASSETS','/bound-v2','closed native role resolution required');
   const records=basis.artifacts.filter(artifact=>artifact.requirement.artifact_id===row.basis_artifact_id);if(records.length!==1)fail('NATIVE_ASSETS','/bound-v2','one actual basis artifact for each runtime role required');
   const record=records[0]!,file=requestFileV2(row.artifact.path);
   if(dataDigest(file.artifact)!==dataDigest(row.artifact)||file.artifact.sha256!==record.sha256||file.artifact.bytes!==record.bytes||required[role].some(name=>!record.exports.includes(name)||!record.requirement.required_exports.includes(name)))fail('NATIVE_ASSETS','/bound-v2','actual runtime bytes/exports differ from selected basis');files.push(file);
  }
  if(new Set(files.map(f=>f.artifact.path)).size!==4||new Set(runtime.map(row=>row.basis_artifact_id)).size!==4)fail('NATIVE_ASSETS','/bound-v2','runtime role identities must be distinct');
  const callableFile=requestFileV2(callable.artifact.path);if(dataDigest(callableFile.artifact)!==dataDigest(callable.artifact))fail('FILE_STALE',callable.artifact.path,'actual generated callable bytes differ');
  files.push(callableFile);
  const encoder=await import(pathToFileURL(files[2]!.artifact.path).href) as {checkU0EncoderConfiguration?:(config:U0WireConfiguration,domain:{rejection_code:string})=>U0WireConfiguration};
  if(typeof encoder.checkU0EncoderConfiguration!=='function')fail('NATIVE_ASSETS','/bound-v2','actual selected encoder export required');
  const domain={rejection_code:state.checked.roles.rejection};encoder.checkU0EncoderConfiguration(basis.configuration,domain);
  assertEarlyCurrent(early);generation.assertCurrent(callable);native.assertCurrent(basis);native.assertSelectionBasis(early.selection,basis);
  for(const file of files)if(requestFileV2(file.artifact.path).fingerprint!==file.fingerprint)fail('FILE_STALE',file.artifact.path,'runtime/callable changed before native emission');
  const plan=composeDirectRequestApplicationPlanDataV2(state.source,{executable_sha256:state.checked.executable_sha256,capture_sha256:input.capture.capture_sha256,basis_sha256:basis.basis_sha256,callable:callable.artifact,infrastructure_handler:files[3]!.artifact,configuration:basis.configuration,rejection_code:domain.rejection_code,business_graph_sha256:application.graph.graph_sha256,entity_ref:state.checked.roles.selectors.entity,closures:application.graph.closures});
  const graphFile=writeRequestFileV2(plan.graph_file.path,plan.graph_file.content,callableFile),entryFile=writeRequestFileV2(plan.entry.path,plan.entry.content,callableFile);files.push(graphFile,entryFile);
  const imported=await import(pathToFileURL(entryFile.artifact.path).href) as {handler?:unknown;boundInvoke?:unknown};
  if(typeof imported.handler!=='function'||imported.boundInvoke!==callable.invoke)fail('NATIVE_EXPORT','/bound-v2','actual generated entry must import the original registered callable export');
  const body={kind:'realized-u0-application',executable_sha256:state.checked.executable_sha256,capture_sha256:input.capture.capture_sha256,basis_sha256:basis.basis_sha256,callable_sha256:callable.artifact.sha256,request_graph_sha256:graphFile.artifact.sha256,handler_sha256:entryFile.artifact.sha256,authority_effect:'none'};
  const subject=captureJson({...body,realized_sha256:dataDigest(body)}) as unknown as U0RealizedApplicationSubject;
  const bound:BoundU0EntryV2=Object.freeze({kind:'bound-u0-entry-v2',early,callable,basis,handler_artifact:entryFile.artifact,handler:imported.handler as U0InjectedHandler,subject,authority_effect:'none'});
  boundOwned.set(bound,{early,callable,basis,files,handler:bound.handler,fingerprint:boundFingerprint(bound)});assertBoundCurrent(bound);return bound;
 },assertBoundCurrent});
}
