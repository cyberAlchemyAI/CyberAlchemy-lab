import {closeSync,constants,fstatSync,lstatSync,openSync,readSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest,ProfileRejected,reject,sha256} from './contracts.js';
import {validateBusinessApplication,type BusinessApplication} from './contracts-v2.js';
import type {ProfilePackageV3} from './contracts-v3.js';
import type {BusinessInputV2,CapturedBusinessApplication,BusinessApplicationSelector} from './business-input-v2.js';
import type {BusinessAuthoringSnapshot,LoadedBusinessAuthoringPackage} from './loader-v3.js';
import {businessAuthoringRecipeSnapshot} from './business-authoring-recipes.js';
import {assertAcceptedBusinessDecisionCurrent,type AcceptedBusinessDecision} from './business-decision.js';
import {assertBusinessAuthoringRequestsCurrent,type BusinessAuthoringRequestPreparation} from './business-authoring-request.js';
import type {BusinessRecipeModelInput} from './business-authoring-normalization-protocol.js';
import type {ReviewDefinition} from './business-authoring-protocol.js';
import type {BusinessInputOwnerV2,AuthoringBusinessInputV2,BusinessReviewOwnerV2,AcceptedBusinessReviewV2,BusinessRecipeSelectionV2,BusinessEarlyRequestsV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessCoreRecipeOwnerV2,BusinessRequestStagesOwnerV2} from './business-authoring-stages-v2.js';
import {checkCoreDirectBusinessRecipeV2} from './business-authoring-recipes.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2} from './business-authoring-identity-v2.js';

/** Accepted generated legacy data has an explicit owner; no v2 snapshot is registered.
 * Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md; callable/API realization is separate. */
export interface AuthoringBusinessCompatibility {readonly model_id:string;readonly source:string;readonly semantics:BusinessApplication}
export interface AuthoringBusinessInput {
 readonly kind:'business-authoring-input';readonly accepted:AcceptedBusinessDecision;readonly requests:BusinessAuthoringRequestPreparation;
 readonly compatibility:AuthoringBusinessCompatibility;readonly authoring_snapshot:BusinessAuthoringSnapshot;
 readonly snapshot:Readonly<{kind:'business-authoring-input-context';authoring_snapshot:BusinessAuthoringSnapshot;project:Readonly<{application_intents:BusinessAuthoringRequestPreparation['project_intents']}>}>;
 readonly runtime:LoadedBusinessAuthoringPackage & {readonly data:ProfilePackageV3};
 readonly applications:readonly CapturedBusinessApplication[];readonly formal_profile:unknown;readonly identity_algorithm:unknown;
 readonly source_sha256:string;readonly metadata_tables:BusinessInputV2['metadata_tables'];
 readonly provenance:Readonly<{kind:'generated-business-compatibility';original_source:BusinessRecipeModelInput['source'];decision_file:AcceptedBusinessDecision['capture']['file'];source:Readonly<{path:string;sha256:string;bytes:number}>;semantics:Readonly<{path:string;sha256:string;bytes:number}>}>;
}
const registry=new WeakMap<object,{accepted:AcceptedBusinessDecision;requests:BusinessAuthoringRequestPreparation;snapshot:BusinessAuthoringSnapshot;runtime:AuthoringBusinessInput['runtime'];fingerprint:string;module:string}>();
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const byId=<T extends {id:string}>(values:readonly T[])=>[...values].sort((a,b)=>compare(a.id,b.id));
const byName=<T extends {name:string}>(values:readonly T[])=>[...values].sort((a,b)=>compare(a.name,b.name));
const symbol=(value:string)=>value.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
function fail(code:string,at:string,message:string):never{return reject('BUSINESS_AUTHORING_INPUT_'+code,at,message);}
function same(actual:unknown,expected:unknown,at:string):void {if(dataDigest(actual)!==dataDigest(expected))fail('CORRESPONDENCE',at,'exact accepted business and generated request correspondence required');}
function moduleIdentity():string {
 try{
  const filename=fileURLToPath(import.meta.url);let cursor=path.parse(filename).root;const owners:string[]=[];
  const check=()=>{const stat=lstatSync(cursor,{bigint:true});if(stat.isSymbolicLink())fail('MODULE_STALE',filename,'implementation symlinks are forbidden');owners.push(`${stat.dev}:${stat.ino}`);};
  check();for(const part of filename.slice(cursor.length).split(path.sep).filter(Boolean)){cursor=path.join(cursor,part);check();}
  const before=lstatSync(filename,{bigint:true});if(!before.isFile()||before.size>16777216n)fail('MODULE_STALE',filename,'bounded regular implementation required');
  const fd=openSync(filename,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),parts:Buffer[]=[];let bytes=0;
  try{
   const current=fstatSync(fd,{bigint:true});if(!current.isFile()||current.dev!==before.dev||current.ino!==before.ino||current.size!==before.size||current.mtimeNs!==before.mtimeNs||current.ctimeNs!==before.ctimeNs)fail('MODULE_STALE',filename,'implementation changed while opening');
   for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>16777216)fail('MODULE_STALE',filename,'implementation exceeds budget');parts.push(buffer.subarray(0,count));}
   const after=fstatSync(fd,{bigint:true});if(after.size!==before.size||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs)fail('MODULE_STALE',filename,'implementation changed during capture');
  }finally{closeSync(fd);}
  const after=lstatSync(filename,{bigint:true});if(after.dev!==before.dev||after.ino!==before.ino||after.size!==before.size||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs||BigInt(bytes)!==before.size)fail('MODULE_STALE',filename,'implementation path changed');
  const finalOwners:string[]=[];cursor=path.parse(filename).root;const finalCheck=()=>{const stat=lstatSync(cursor,{bigint:true});if(stat.isSymbolicLink())fail('MODULE_STALE',filename,'implementation path changed');finalOwners.push(`${stat.dev}:${stat.ino}`);};finalCheck();for(const part of filename.slice(cursor.length).split(path.sep).filter(Boolean)){cursor=path.join(cursor,part);finalCheck();}
  same(finalOwners,owners,filename);
  return dataDigest({owners,bytes,sha256:sha256(Buffer.concat(parts)),mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)});
 }catch(error){if(error instanceof ProfileRejected)throw error;return fail('MODULE_STALE','/','owning implementation is unavailable');}
}
const executingModule=moduleIdentity();
function assertModule():string {const current=moduleIdentity();if(current!==executingModule)fail('MODULE_STALE','/','reload the owning implementation after changes');return current;}
function expectedSource(model:BusinessRecipeModelInput,requests:BusinessAuthoringRequestPreparation):string {
 const spec=model.spec,lines=[`domain ${spec.identity.namespace} ${JSON.stringify(spec.identity.title)}`,`owner ${spec.identity.owner}`];
 for(const claim of byId(spec.claims))lines.push(`formal-claim ${claim.id}:`,`  profile ${claim.logic_profile}`,...byName(claim.sorts).map(sort=>`  sort ${sort.name}`),...byName(claim.predicates).map(predicate=>`  predicate ${predicate.name}(${predicate.sort_refs.join(',')})`),...byName(claim.constants).map(constant=>`  constant ${constant.name}: ${constant.sort_ref}`),`  proposition ${claim.proposition}`,`  ceiling ${JSON.stringify(claim.ceiling)}`);
 for(const rule of byId(spec.rules))lines.push(`rule ${rule.id}:`,`  claim ${rule.claim_ref}`);
 for(const entity of byId(spec.entities))lines.push(`entity ${entity.id}:`,`  identity ${entity.identity}`,...byName(entity.fields).map(field=>`  ${field.name} ${field.type}`));
 for(const operation of byId(spec.operations))lines.push(`operation ${operation.id}:`,`  input ${operation.input.type_ref}`,`  output ${operation.output_ref}`,`  requires ${operation.guards[0]!.rule_ref}`);
 const request=requests.models.find(value=>value.model_id===model.model_id)!;
 return lines.join('\n')+'\n\n'+request.mappings.map(mapping=>mapping.source_fragment.trimEnd()).join('\n\n')+'\n';
}
function expectedSemantics(accepted:AcceptedBusinessDecision,requests:BusinessAuthoringRequestPreparation,model:BusinessRecipeModelInput):BusinessApplication {
 const spec=model.spec,review=accepted.review.review,feature=symbol(spec.identity.namespace),ontology=(id:string)=>`BUSINESS-${feature.toUpperCase()}-${symbol(id).toUpperCase()}`;
 const declarations:Record<string,unknown>=Object.create(null),claimMeanings:Record<string,unknown>=Object.create(null),operations:Record<string,unknown>=Object.create(null);
 for(const entity of byId(spec.entities))declarations[entity.id]={ontology:ontology(entity.id),meaning:entity.meaning,properties:Object.fromEntries(byName(entity.fields).map(field=>[field.name,{ontology:ontology(entity.id)+'#'+symbol(field.name).replaceAll('-','_'),meaning:field.meaning}]))};
 for(const rule of byId(spec.rules))declarations[rule.id]={ontology:ontology(rule.id),meaning:rule.meaning};
 for(const operation of byId(spec.operations)){
  declarations[operation.id]={ontology:ontology(operation.id),meaning:operation.meaning,failure_continuation:operation.on_rejection};
  operations[operation.id]={input_name:operation.input.name,guards:operation.guards.map(guard=>({rule:guard.rule_ref,arguments:{[guard.arguments[0]!.parameter]:{root:'request',path:[]}}})),result:{root:'request',path:[]}};
 }
 Object.assign(declarations,requests.models.find(value=>value.model_id===model.model_id)!.declaration_bindings);
 const definitions=new Map(review.definitions.map(definition=>[definition.definition_id,definition])),global=new Set(accepted.definition_closure.definition_ids);
 const globalBodies=[...global].sort(compare).map(id=>definitions.get(id));if(globalBodies.some(value=>!value)||dataDigest(globalBodies)!==accepted.definition_closure.digest)fail('CORRESPONDENCE','/definitions','accepted global definition closure changed');
 for(const claim of byId(spec.claims)){
  const requirement=spec.requirements.find(value=>value.id===claim.requirement_ref)!,rules=byId(spec.rules.filter(rule=>rule.claim_ref===claim.id)),linked=byId(spec.operations.filter(operation=>operation.guards.some(guard=>rules.some(rule=>rule.id===guard.rule_ref))));
  const input=(kind:string,value:typeof rules[number]|typeof linked[number])=>{const entity=spec.entities.find(entity=>entity.id===value.input.type_ref)!;return `${kind} ${value.id} input ${value.input.name}: ${entity.id} {${byName(entity.fields).map(field=>`${field.name}: ${field.type}`).join(', ')}}.`;};
  const meaning={schema_version:'domainspec-v2.business-meaning/v1-candidate',meaning_id:`Meaning:${feature}:${symbol(claim.id)}`,version:claim.version,owner:spec.identity.owner,domain_context:requirement.context,rule:requirement.meaning,applies_when:requirement.applies_when,actors:requirement.actors,inputs:[...rules.map(rule=>input('Rule',rule)),...linked.map(operation=>input('Operation',operation))],outcomes:linked.map(operation=>`Operation ${operation.id} returns ${operation.result.root}: ${operation.output_ref}; on-rejection ${operation.on_rejection}; effects none.`),examples:requirement.examples,counterexamples:requirement.counterexamples,boundaries:requirement.boundaries,claim_ceiling:claim.ceiling,authority_effect:'none',status:'accepted'};
  const subject=accepted.legacy_meaning_subjects.find(subject=>subject.meaning_id===meaning.meaning_id&&subject.version===meaning.version);
  if(!subject||subject.digest!==dataDigest(meaning))fail('CORRESPONDENCE','/claim_meanings/'+claim.id,'exact approved legacy subject required');
  const selected=new Set<string>(),active=new Set<string>();
  const resolve=(reference:string):ReviewDefinition=>{const matches=review.definitions.filter(value=>value.definition_id===reference||value.term===reference);if(matches.length!==1)fail('CORRESPONDENCE','/definitions','unambiguous explicit definition required');return matches[0]!;};
  const visit=(definition:ReviewDefinition,depth:number):void=>{if(depth>64||active.has(definition.definition_id)||!global.has(definition.definition_id))fail('CORRESPONDENCE','/definitions','accepted explicit closure required');if(selected.has(definition.definition_id))return;active.add(definition.definition_id);for(const reference of definition.depends_on)visit(resolve(reference),depth+1);active.delete(definition.definition_id);selected.add(definition.definition_id);};
  for(const predicate of claim.predicates){const matches=review.definitions.filter(value=>value.term===predicate.definition_ref);if(matches.length!==1)fail('CORRESPONDENCE','/definitions','explicit authored term required');visit(matches[0]!,0);}
  const ids=[...selected].sort(compare);
  claimMeanings[claim.id]={claim_id:`FormalClaim:${feature}:${symbol(claim.id)}`,version:claim.version,supersedes:claim.supersedes,business_meaning:meaning,owner_acceptance:{schema_version:'domainspec-v2.business-acceptance-decision/v1-candidate',decision_id:accepted.capture.decision.decision_id,owner:accepted.capture.decision.owner,outcome:'accepted',subject,authority_effect:'none'},definitions:ids.map(id=>({...definitions.get(id)!,status:'accepted'})),definition_refs:ids};
 }
 return {schema_version:'craft.business-application/v1-candidate',owner:spec.identity.owner,declarations,claim_meanings:claimMeanings,rule_meanings:model.formal.rule_meanings,operation_behaviors:operations,required_guarantees:requests.selection.technical.required_guarantees,value_invariant_bindings:{}} as BusinessApplication;
}
function fingerprint(input:AuthoringBusinessInput):string {return dataDigest({kind:input.kind,compatibility:input.compatibility,snapshot:{kind:input.snapshot.kind,project:input.snapshot.project},applications:input.applications,formal_profile:input.formal_profile,identity_algorithm:input.identity_algorithm,source_sha256:input.source_sha256,metadata_tables:input.metadata_tables,provenance:input.provenance});}
export function prepareAuthoringBusinessInput(accepted:AcceptedBusinessDecision,requests:BusinessAuthoringRequestPreparation,raw:AuthoringBusinessCompatibility):AuthoringBusinessInput {
 assertAcceptedBusinessDecisionCurrent(accepted);assertBusinessAuthoringRequestsCurrent(requests);const module=assertModule();
 if(accepted.review.selection!==requests.selection)fail('SELECTION','/requests','the original accepted selection and request preparation must match');
 const data=captureJson(raw) as unknown as AuthoringBusinessCompatibility;
 if(!data||typeof data!=='object'||Object.keys(data).length!==3||!['model_id','source','semantics'].every(key=>Object.hasOwn(data,key))||typeof data.model_id!=='string'||typeof data.source!=='string')fail('COMPATIBILITY','/compatibility','closed generated model_id/source/semantics required');
 if(data.model_id!==accepted.review.model_id)fail('MODEL','/model_id','original reviewed model required');
 const model=requests.selection.models.find(model=>model.model_id===data.model_id),request=requests.models.find(model=>model.model_id===data.model_id);if(!model||!request)fail('MODEL','/model_id','original selected model required');
 if(data.source!==expectedSource(model!,requests))fail('SOURCE','/source','exact canonical generated legacy source and original Mapping declarations required');
 const semantics=validateBusinessApplication(data.semantics);same(semantics,expectedSemantics(accepted,requests,model!),'/semantics');
 const compatibility=Object.freeze({model_id:data.model_id,source:data.source,semantics}),snapshot=businessAuthoringRecipeSnapshot(requests.selection);
 const runtimes=snapshot.packages.filter((runtime):runtime is AuthoringBusinessInput['runtime']=>runtime.data.schema_version==='craft.profile-package/v3-candidate');if(runtimes.length!==1)fail('RUNTIME','/profiles','one actual captured authoring runtime required');const runtime=runtimes[0]!;
 const semanticText=JSON.stringify(semantics,null,2)+'\n',sourceHash=sha256(data.source),semanticHash=sha256(semanticText),applicationModel={id:data.model_id,source:`derived/${data.model_id}/domain.alch`,semantics:`derived/${data.model_id}/semantics.json`},selectors:BusinessApplicationSelector[]=[];let declaration='';
 for(const [index,line] of data.source.split('\n').entries()){
  if(!line.trim()||/^(domain|owner) /.test(line))continue;
  if(!line.startsWith(' ')){const match=/^(formal-claim|rule|entity|operation|mapping) ([A-Za-z_][A-Za-z0-9_-]*):$/.exec(line);if(!match)fail('SOURCE','/source','canonical declaration required');declaration=match![1]+':'+match![2];}
  selectors.push({application_id:data.model_id,source:applicationModel.source,selector:line.startsWith(' ')?declaration+'#clause:'+(index+1):declaration,line:index+1,text:line,sha256:sourceHash});
 }
 const intents=requests.project_intents.filter(intent=>intent.application_id===data.model_id),owned=captureJson({applications:[{model:applicationModel,source:data.source,semantics,selectors,source_sha256:sourceHash,semantics_sha256:semanticHash}],project:{application_intents:intents},metadata_tables:{applications:{fields:{id:'string',source:'string',selector:'string',application_id:'string',mapping_ref:'string'},rows:intents.map(intent=>({id:intent.id,source:applicationModel.source,selector:intent.operation_ref,application_id:data.model_id,mapping_ref:intent.mapping_ref}))},application_models:{fields:{id:'string',source:'string',semantics:'string'},rows:[applicationModel]},application_declarations:{fields:{id:'string',source:'string',selector:'string',application_id:'string'},rows:selectors.filter(selector=>!selector.selector.includes('#clause:')).map(selector=>({id:selector.selector.split(':')[1]!,source:selector.source,selector:selector.selector,application_id:data.model_id}))}},provenance:{kind:'generated-business-compatibility',original_source:model!.source,decision_file:accepted.capture.file,source:{path:applicationModel.source,sha256:sourceHash,bytes:Buffer.byteLength(data.source)},semantics:{path:applicationModel.semantics,sha256:semanticHash,bytes:Buffer.byteLength(semanticText)}}}) as unknown as {applications:AuthoringBusinessInput['applications'];project:AuthoringBusinessInput['snapshot']['project'];metadata_tables:AuthoringBusinessInput['metadata_tables'];provenance:AuthoringBusinessInput['provenance']};
 const read=(id:string)=>{const asset=runtime.assets[id];if(asset?.text===undefined)fail('RUNTIME','/assets/'+id,'actual captured formal resource required');return captureJson(JSON.parse(asset!.text!));};
 const context=Object.freeze({kind:'business-authoring-input-context' as const,authoring_snapshot:snapshot,project:owned.project}),result:AuthoringBusinessInput=Object.freeze({kind:'business-authoring-input',accepted,requests,compatibility,authoring_snapshot:snapshot,snapshot:context,runtime,applications:owned.applications,formal_profile:read(runtime.data.application_runtime.formal_profile_asset),identity_algorithm:read(runtime.data.application_runtime.identity_algorithm_asset),source_sha256:snapshot.lock.source_sha256,metadata_tables:owned.metadata_tables,provenance:owned.provenance});
 registry.set(result,{accepted,requests,snapshot,runtime,module,fingerprint:fingerprint(result)});assertAuthoringBusinessInputCurrent(result);return result;
}
export function assertAuthoringBusinessInputCurrent(input:AuthoringBusinessInput):void {
 const state=input&&typeof input==='object'?registry.get(input):undefined;if(!state)fail('UNREGISTERED','/','the original registered authoring input is required; JSON is not custody');
 assertAcceptedBusinessDecisionCurrent(state.accepted);assertBusinessAuthoringRequestsCurrent(state.requests);
 if(assertModule()!==state.module||input.accepted!==state.accepted||input.requests!==state.requests||input.authoring_snapshot!==state.snapshot||input.snapshot.authoring_snapshot!==state.snapshot||input.runtime!==state.runtime||businessAuthoringRecipeSnapshot(state.requests.selection)!==state.snapshot||fingerprint(input)!==state.fingerprint)fail('STALE','/','original accepted/request/snapshot/runtime/module/data identities required');
}

/** Successor accepts original selected acceptance/early owners only. Source-only
 * component fixtures cannot supply these registries. Open Questions: U04/G01. */
export function createAuthoringBusinessInputOwnerV2(recipes:BusinessCoreRecipeOwnerV2,reviews:BusinessReviewOwnerV2,requests:BusinessRequestStagesOwnerV2):BusinessInputOwnerV2 {
 const original=[recipes.assertCurrent,reviews.assertAcceptedCurrent,reviews.assertCurrent,reviews.assertDecisionCurrent,requests.assertEarlyCurrent];
 const owned=new WeakMap<object,{selection:BusinessRecipeSelectionV2;accepted:AcceptedBusinessReviewV2;early:BusinessEarlyRequestsV2;fingerprint:string}>();
 const current=()=>{
  assertModule();if([recipes.assertCurrent,reviews.assertAcceptedCurrent,reviews.assertCurrent,reviews.assertDecisionCurrent,requests.assertEarlyCurrent].some((method,i)=>method!==original[i]))fail('OWNER_STALE','/input-v2','exact selected review/request owner methods changed');
 };
 const assertCurrent=(input:AuthoringBusinessInputV2):void=>{
  const state=input&&typeof input==='object'?owned.get(input):undefined;if(!state)fail('UNREGISTERED','/input-v2','original input from this exact owner required');
  current();recipes.assertCurrent(state.selection);reviews.assertAcceptedCurrent(state.accepted);requests.assertEarlyCurrent(state.early);
  if(input.selection!==state.selection||input.accepted!==state.accepted||input.early_requests!==state.early||state.accepted.review.selection!==state.selection||state.early.selection!==state.selection||dataDigest(input)!==state.fingerprint)fail('STALE','/input-v2','original selected acceptance/early/input correspondence changed');
 };
 return Object.freeze({form(selection:BusinessRecipeSelectionV2,modelId:string,accepted:AcceptedBusinessReviewV2,early:BusinessEarlyRequestsV2):AuthoringBusinessInputV2{
  current();recipes.assertCurrent(selection);reviews.assertAcceptedCurrent(accepted);requests.assertEarlyCurrent(early);
  const model=selection.models.find(row=>row.model_id===modelId);
  if(!model||accepted.review.selection!==selection||accepted.review.model_id!==modelId||accepted.decision.review!==accepted.review||early.selection!==selection||early.entries.length!==1||early.entries[0]!.model_id!==modelId)fail('CORRESPONDENCE','/input-v2','one identical original selection/model/review/decision/early scope required');
  const checked=checkCoreDirectBusinessRecipeV2({source:model.source,spec:model.spec,executable:projectDirectExecutableV2(model.spec),assurance:projectOptionalAssuranceV2(model.spec)});
  same(accepted.review.subject,checked.review,'/input-v2/review');same(accepted.review.source_capture,model.capture,'/input-v2/capture');
  if(accepted.decision.decision.outcome!=='accepted'||accepted.decision.decision.capture_sha256!==model.capture.capture_sha256||accepted.decision.decision.executable_sha256!==checked.executable_sha256||accepted.decision.decision.assurance_sha256!==checked.assurance_sha256)fail('CORRESPONDENCE','/input-v2/decision','exact accepted reviewed executable/assurance/source required');
  const entry=model.spec.entries[0]!,operation=model.spec.operations[0]!,rule=model.spec.rules[0]!,intent=early.entries[0]!;
  same({entry_id:intent.entry_id,operation_ref:intent.operation_ref,rule_ref:intent.rule_ref,permission:intent.permission,payload:intent.payload},{entry_id:entry.id,operation_ref:operation.id,rule_ref:rule.id,permission:entry.permission,payload:{kind:'whole-input',parameter:operation.input.name,type_ref:operation.input.type_ref}},'/input-v2/entry');
  const body={kind:'authoring-business-input-v2' as const,selection,model_id:modelId,spec:model.spec,accepted,early_requests:early,capture:model.capture,authority_effect:'none' as const};
  const input:AuthoringBusinessInputV2=Object.freeze({...body,input_sha256:dataDigest(body)});
  owned.set(input,{selection,accepted,early,fingerprint:dataDigest(input)});assertCurrent(input);return input;
 },assertCurrent});
}
