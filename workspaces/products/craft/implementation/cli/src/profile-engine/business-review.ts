import {closeSync,constants,fstatSync,lstatSync,openSync,readSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest,reject,sha256,ProfileRejected} from './contracts.js';
import {assertBusinessRecipeSelectionCurrent,type BusinessRecipeSelection} from './business-authoring-recipes.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import {BUSINESS_AUTHORING_CONTRACT,type BusinessDecision,type BusinessEntity,type BusinessReviewSubject,type LegacyMeaningSubject,type ReviewDefinition} from './business-authoring-protocol.js';
import type {BusinessRecipeModelInput} from './business-authoring-normalization-protocol.js';
import {checkCoreDirectBusinessRecipeV2,type CoreDirectRecipeDataV2} from './business-authoring-recipes.js';
import {validateBusinessAuthoringContractV2} from './business-authoring-schema-v2.js';
import type {BusinessReviewSubjectV2,PreparedBusinessReviewV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessCoreRecipeOwnerV2} from './business-authoring-stages-v2.js';

/** B04.1 inspectable candidate business scope, not producer authentication or acceptance.
 * Open questions: B04.2 decision capture and B06.2 accepted materialization remain separate. */
export interface PreparedBusinessAuthoringReview {
 readonly kind:'prepared-business-authoring-review';readonly selection:BusinessRecipeSelection;readonly model_id:string;
 readonly review:BusinessReviewSubject;readonly subject:BusinessDecision['subject'];readonly legacy_meaning_subjects:readonly LegacyMeaningSubject[];
 readonly definition_closure:BusinessDecision['definition_closure'];readonly technical:BusinessRecipeSelection['technical'];
 readonly review_sha256:string;readonly authority_effect:'none';
}
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const byId=<T extends {id:string}>(rows:readonly T[]):T[]=>[...rows].sort((a,b)=>compare(a.id,b.id));
const fields=(entity:BusinessEntity)=>[...entity.fields].sort((a,b)=>compare(a.name,b.name));
const registry=new WeakMap<object,{selection:BusinessRecipeSelection;module:string;fingerprint:string}>();
function fail(code:string,at:string,message:string):never{return reject('BUSINESS_REVIEW_'+code,at,message);}
function same(actual:unknown,expected:unknown,at:string):void {if(dataDigest(actual)!==dataDigest(expected))fail('CORRESPONDENCE',at,'review must retain the exact selected business model and finite normalization');}
function symbol(value:string,at:string):string {
 const key=value.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
 if(!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(key))fail('CORRESPONDENCE',at,'invalid backend identity; no inferred suffix or renaming');return key;
}
function implementationIdentity():string {
 try{
  const filename=fileURLToPath(import.meta.url);let cursor=path.parse(filename).root;const owners:string[]=[];
  for(const part of filename.slice(cursor.length).split(path.sep).filter(Boolean)){cursor=path.join(cursor,part);const stat=lstatSync(cursor,{bigint:true});if(stat.isSymbolicLink())fail('MODULE_STALE',filename,'review implementation cannot use substituted symlinks');owners.push(`${stat.dev}:${stat.ino}`);}
  const before=lstatSync(filename,{bigint:true});if(!before.isFile()||before.size>16777216n)fail('MODULE_STALE',filename,'bounded regular review implementation required');
  const fd=openSync(filename,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),parts:Buffer[]=[];let bytes=0;
  try{
   const opened=fstatSync(fd,{bigint:true});if(!opened.isFile()||opened.dev!==before.dev||opened.ino!==before.ino)fail('MODULE_STALE',filename,'review implementation changed while opening');
   for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>16777216)fail('MODULE_STALE',filename,'review implementation exceeds capture budget');parts.push(buffer.subarray(0,count));}
   const after=fstatSync(fd,{bigint:true});if(after.size!==before.size||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs)fail('MODULE_STALE',filename,'review implementation changed during capture');
  }finally{closeSync(fd);}
  const after=lstatSync(filename,{bigint:true});if(after.dev!==before.dev||after.ino!==before.ino||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs)fail('MODULE_STALE',filename,'review implementation path changed during capture');
  return dataDigest({owners,bytes,sha256:sha256(Buffer.concat(parts)),mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)});
 }catch(error){if(error instanceof ProfileRejected)throw error;return fail('MODULE_STALE','/','review implementation is unavailable or changed');}
}
const executingImplementation=implementationIdentity();

/** Reconstruct the finite B06 business-only subject independently of any frontend handle. */
function expectedReview(model:BusinessRecipeModelInput):BusinessReviewSubject {
 const spec=model.spec,feature=symbol(spec.identity.namespace,'/model_identity/namespace');
 const definitionId=(key:string)=>`DEF-${feature.toUpperCase()}-${symbol(key,'/definitions').toUpperCase()}`;
 const identities=new Set<string>();
 const definitions:ReviewDefinition[]=model.formal.definitions.map<ReviewDefinition>(normalized=>{
  const definition=spec.definitions.find(definition=>definition.id===normalized.definition_ref);
  if(!definition)fail('DEFINITION','/definitions','normalized definition must have an explicit source declaration');
  const requirement=spec.requirements.find(requirement=>requirement.id===definition!.requirement_ref)!;
  const id=definitionId(definition!.id);if(identities.has(id))fail('DEFINITION','/definitions','normalized definition IDs collide');identities.add(id);
  if(new Set(requirement.boundaries).size!==requirement.boundaries.length)fail('LEGACY','/definitions/forbidden_collapses','legacy definition boundaries require unique exact strings');
  return {definition_id:id,term:definition!.id,definition_kind:'predicate',formal:normalized.formal,plain_language:definition!.meaning,domain_context:requirement.context,depends_on:[],business_fact_refs:['#/inputs'],interpretation_refs:['#/rule'],source_concept_refs:[`business:${feature}:definition:${symbol(definition!.id,'/definitions')}`],forbidden_collapses:requirement.boundaries};
 }).sort((a,b)=>compare(a.definition_id,b.definition_id));
 const entities=new Map(spec.entities.map(entity=>[entity.id,entity]));
 const input=(kind:'Rule'|'Operation',id:string,name:string,entity:string):string=>`${kind} ${id} input ${name}: ${entity} {${fields(entities.get(entity)!).map(field=>`${field.name}: ${field.type}`).join(', ')}}.`;
 const subjects:LegacyMeaningSubject[]=byId(spec.claims).map<LegacyMeaningSubject>(claim=>{
  const requirement=spec.requirements.find(requirement=>requirement.id===claim.requirement_ref)!,rules=byId(spec.rules.filter(rule=>rule.claim_ref===claim.id));
  const operations=byId(spec.operations.filter(operation=>operation.guards.some(guard=>rules.some(rule=>rule.id===guard.rule_ref))));
  const draft={schema_version:'domainspec-v2.business-meaning/v1-candidate',meaning_id:`Meaning:${feature}:${symbol(claim.id,'/claims')}`,version:claim.version,owner:spec.identity.owner,domain_context:requirement.context,rule:requirement.meaning,applies_when:requirement.applies_when,actors:requirement.actors,
   inputs:[...rules.map(rule=>input('Rule',rule.id,rule.input.name,rule.input.type_ref)),...operations.map(operation=>input('Operation',operation.id,operation.input.name,operation.input.type_ref))],
   outcomes:operations.map(operation=>`Operation ${operation.id} returns ${operation.result.root}: ${operation.output_ref}; on-rejection ${operation.on_rejection}; effects none.`),examples:requirement.examples,counterexamples:requirement.counterexamples,boundaries:requirement.boundaries,claim_ceiling:claim.ceiling,authority_effect:'none'};
  for(const key of ['applies_when','actors','inputs','outcomes','boundaries'] as const){const values=draft[key];if(new Set(values).size!==values.length)fail('LEGACY','/legacy_meaning_subjects/'+claim.id,'legacy v1 string sets must retain unique exact authored values');}
  const bound=(value:unknown):void=>{if(typeof value==='string'&&(!value.trim()||value.length>4096))fail('LEGACY','/legacy_meaning_subjects/'+claim.id,'legacy text must be nonblank and bounded');if(value&&typeof value==='object')for(const child of Object.values(value))bound(child);};bound(draft);
  // Exact legacy canonicalization retains accepted status while excluding the later acceptance field.
  // This prospective hashing payload is local only; no status/acceptance object is returned.
  return {meaning_id:draft.meaning_id,version:claim.version,canonicalization:'domainspec-json-keysort-excluding-acceptance-v1',digest_algorithm:'sha256',digest:dataDigest({...draft,status:'accepted'})};
 }).sort((a,b)=>compare(a.meaning_id,b.meaning_id));
 return {schema_version:'craft.business-review/v1-candidate',normalization_contract:BUSINESS_AUTHORING_CONTRACT,model_identity:spec.identity,
  declarations:byId(spec.entities).map(entity=>({...entity,fields:fields(entity)})),definitions,
  claims:byId(spec.claims).map(claim=>({...claim,sorts:[...claim.sorts].sort((a,b)=>compare(a.name,b.name)),predicates:[...claim.predicates].sort((a,b)=>compare(a.name,b.name)),constants:[...claim.constants].sort((a,b)=>compare(a.name,b.name))})),
  interpretations:byId(spec.rules).map(rule=>({rule_ref:rule.id,...model.formal.rule_meanings[rule.id]!})),behaviors:byId(spec.operations),exposures:byId(spec.capabilities),requirements:byId(spec.requirements),legacy_meaning_subjects:subjects};
}
function selectedClosure(review:BusinessReviewSubject):BusinessDecision['definition_closure'] {
 const definitions=review.definitions,selected=new Set<string>(),active=new Set<string>();
 if(new Set(definitions.map(definition=>definition.definition_id)).size!==definitions.length||new Set(definitions.map(definition=>definition.term)).size!==definitions.length)fail('DEFINITION','/definitions','one distinct normalized identity and authored term per definition required');
 const resolve=(reference:string,raw=false):ReviewDefinition=>{
  const matches=definitions.filter(definition=>definition.term===reference||!raw&&definition.definition_id===reference);
  if(matches.length!==1)fail('DEFINITION','/definitions','unresolved or ambiguous exact definition reference '+reference);return matches[0]!;
 };
 const visit=(definition:ReviewDefinition,depth:number):void=>{
  if(depth>64)fail('DEFINITION','/definitions','definition dependency depth exceeded');
  if(active.has(definition.definition_id))fail('DEFINITION','/definitions','cyclic definition dependency');if(selected.has(definition.definition_id))return;
  if(new Set(definition.depends_on).size!==definition.depends_on.length)fail('DEFINITION','/definitions','duplicate explicit definition dependency');
  active.add(definition.definition_id);for(const dependency of definition.depends_on)visit(resolve(dependency),depth+1);active.delete(definition.definition_id);selected.add(definition.definition_id);
 };
 for(const claim of review.claims)for(const predicate of claim.predicates)visit(resolve(predicate.definition_ref,true),0);
 const bodies=definitions.filter(definition=>selected.has(definition.definition_id)).sort((a,b)=>compare(a.definition_id,b.definition_id));
 return {definition_ids:bodies.map(definition=>definition.definition_id),digest_algorithm:'sha256',digest:dataDigest(bodies)};
}
export function prepareBusinessAuthoringReview(selection:BusinessRecipeSelection,modelId:string,reviewSubject:unknown):PreparedBusinessAuthoringReview {
 assertBusinessRecipeSelectionCurrent(selection);
 const module=implementationIdentity();if(module!==executingImplementation)fail('MODULE_STALE','/','reload the owning review implementation after any change');
 const model=selection.models.find(model=>model.model_id===modelId);if(!model)fail('CORRESPONDENCE','/model_id','review model must select an original registered recipe model');
 const review=validateBusinessAuthoringContract<BusinessReviewSubject>('review',reviewSubject),expected=expectedReview(model!);
 same(review.legacy_meaning_subjects,expected.legacy_meaning_subjects,'/legacy_meaning_subjects');same(review,expected,'/review');
 const subject:BusinessDecision['subject']={model_id:review.model_identity.namespace,version:review.model_identity.version,canonicalization:'craft.business-review-keysort/v1',digest_algorithm:'sha256',digest:dataDigest(review)};
 const captured=captureJson({kind:'prepared-business-authoring-review',model_id:modelId,review,subject,legacy_meaning_subjects:review.legacy_meaning_subjects,definition_closure:selectedClosure(review),technical:selection.technical,authority_effect:'none'}) as unknown as Omit<PreparedBusinessAuthoringReview,'selection'|'review_sha256'>;
 const body={...captured,selection},result:PreparedBusinessAuthoringReview=Object.freeze({...body,review_sha256:dataDigest(body)});
 registry.set(result,{selection,module,fingerprint:dataDigest(result)});assertBusinessAuthoringReviewCurrent(result);return result;
}
export function assertBusinessAuthoringReviewCurrent(review:PreparedBusinessAuthoringReview):void {
 const state=review&&typeof review==='object'?registry.get(review):undefined;
 if(!state)fail('HANDLE','/','original registered prepared review required; JSON is not custody');
 assertBusinessRecipeSelectionCurrent(state.selection);
 if(implementationIdentity()!==state.module||review.selection!==state.selection||dataDigest(review)!==state.fingerprint)fail('MODULE_STALE','/','review implementation, selected closure or owned data changed');
}
export function renderBusinessAuthoringReview(value:PreparedBusinessAuthoringReview):string {
 assertBusinessAuthoringReviewCurrent(value);
 const review=value.review,lines:string[]=[`Business review: ${value.model_id} version ${review.model_identity.version}`,`Title: ${review.model_identity.title}`,`Authored owner: ${review.model_identity.owner}`,`Business subject (${value.subject.canonicalization}, ${value.subject.digest_algorithm}): ${value.subject.digest}`,'Authority effect: none','', 'Business requirements'];
 for(const requirement of review.requirements){
  lines.push(`Requirement ${requirement.id}`,`Context: ${requirement.context}`,`Meaning: ${requirement.meaning}`,'Applies when:',...requirement.applies_when.map(text=>'  '+text),'Actors (informational, not authentication):',...requirement.actors.map(text=>'  '+text),'Boundaries:',...requirement.boundaries.map(text=>'  '+text));
  for(const [label,cases] of [['Example',requirement.examples],['Counterexample',requirement.counterexamples]] as const)for(const scenario of cases)lines.push(`${label} ${scenario.case_id}`,`  Given: ${scenario.given}`,`  When: ${scenario.when}`,`  Then: ${scenario.then}`,`  Why: ${scenario.why}`);
 }
 lines.push('','Business Entity declarations');
 for(const entity of review.declarations)lines.push(`Entity ${entity.id}: ${entity.meaning}`,`  Identity field: ${entity.identity}`,...entity.fields.map(field=>`  ${field.name}: ${field.type} — ${field.meaning}`));
 lines.push('','Definitions and formal interpretations');
 for(const definition of review.definitions)lines.push(`Definition ${definition.definition_id} (${definition.term})`,`  Meaning: ${definition.plain_language}`,`  Context: ${definition.domain_context}`,`  Formal definition: ${definition.formal.definition}`,`  Expression: ${definition.formal.expression}`,...definition.formal.notation.map(notation=>`  Notation ${notation.symbol}: ${notation.meaning}`),`  Operational interpretation: ${definition.formal.operational_interpretation}`,`  Dependencies: ${definition.depends_on.join(', ')||'none'}`,`  Business facts: ${definition.business_fact_refs.join(', ')}`,`  Interpretation references: ${definition.interpretation_refs.join(', ')}`,`  Source concepts: ${definition.source_concept_refs.join(', ')}`,...definition.forbidden_collapses.map(text=>'  Boundary: '+text));
 lines.push('','Authored claims and Rule bindings');
 for(const claim of review.claims)lines.push(`Claim ${claim.id} version ${claim.version}; logic ${claim.logic_profile}; supersedes ${claim.supersedes??'none'}`,`  Requirement: ${claim.requirement_ref}`,...claim.sorts.map(sort=>`  Sort ${sort.name} interpreted-as ${sort.type_ref}`),...claim.predicates.map(predicate=>`  Predicate ${predicate.name}(${predicate.sort_refs.join(', ')}) defined-by ${predicate.definition_ref}`),...claim.constants.map(constant=>`  Constant ${constant.name}: ${constant.sort_ref}`),`  Proposition: ${claim.proposition}`,`  Ceiling: ${claim.ceiling}`);
 for(const interpretation of review.interpretations)lines.push(`Rule ${interpretation.rule_ref}`,`  Sorts: ${JSON.stringify(interpretation.sorts)}`,`  Constants: ${JSON.stringify(interpretation.constants)}`,`  Predicates: ${JSON.stringify(interpretation.predicates)}`);
 lines.push('','Operations and explicit public audience');
 for(const operation of review.behaviors)lines.push(`Operation ${operation.id}: ${operation.meaning}`,`  Input ${operation.input.name}: ${operation.input.type_ref}; output ${operation.output_ref}`,...operation.guards.map(guard=>`  Guard ${guard.rule_ref}: ${JSON.stringify(guard.arguments)}`),`  Returns ${operation.result.root}${operation.result.path.length?'.'+operation.result.path.join('.'):''}`,`  On rejection (continuation metadata, not executable recovery): ${operation.on_rejection}`,`  Effects: ${operation.effects.length?operation.effects.join(', '):'none'}`);
 for(const exposure of review.exposures)lines.push(`Exposure ${exposure.id}: ${exposure.public_name} invokes ${exposure.operation_ref}; audience ${exposure.audience}`);
 lines.push('','Prospective exact legacy subjects (no decision recorded)');
 for(const subject of value.legacy_meaning_subjects)lines.push(`${subject.meaning_id} version ${subject.version}: ${subject.digest}`,`  ${subject.canonicalization}; ${subject.digest_algorithm}`);
 lines.push(`Selected definition IDs: ${value.definition_closure.definition_ids.join(', ')||'none'}`,`Definition closure (${value.definition_closure.digest_algorithm}): ${value.definition_closure.digest}`,'','Proposed technical conventions — outside the business subject');
 const technical=value.technical;lines.push(`Profile: ${technical.profile_id} version ${technical.profile_version}`,`Transport: ${technical.transport}`,`Method: ${technical.wire.method}; body: ${technical.wire.body}; route prefix: ${technical.wire.route_prefix}`,`Limits: ${technical.wire.request_bytes} request bytes; ${technical.wire.timeout_ms} ms timeout`,'Layout: selected profile conventions; no generated layout is inspected by this review.',`Required guarantees: ${technical.required_guarantees.join(', ')}`,`Profile manifest: ${technical.manifest_sha256}`,`Profile assets: ${technical.asset_sha256}`,`Technical lock: ${technical.lock_sha256}`);
 assertBusinessAuthoringReviewCurrent(value);return lines.join('\n')+'\n';
}

/** Shared inspectable fields, never a registry assertion or application input.
 * Open Questions: K02 actual selected witness; source-only kinds remain separate. */
export interface DirectBusinessReviewContextV2 {
 readonly model_id:string;readonly subject:BusinessReviewSubjectV2;
 readonly source_capture:Readonly<{capture_sha256:string;source?:Readonly<{path:string;sha256:string;bytes:number}>}>;
 readonly review_sha256:string;readonly authority_effect:'none';
}
export interface BusinessReviewSubjectOwnerV2 {
 prepare(selection:PreparedBusinessReviewV2['selection'],modelId:string,subject:BusinessReviewSubjectV2):PreparedBusinessReviewV2;
 assertCurrent(review:PreparedBusinessReviewV2):void;
 render(review:PreparedBusinessReviewV2):string;
}
function directReviewSubject(transfer:unknown,subject:unknown):CoreDirectRecipeDataV2 {
 const checked=checkCoreDirectBusinessRecipeV2(transfer),actual=validateBusinessAuthoringContractV2('review',subject);
 same(actual,checked.review,'/review-v2');return checked;
}
function renderDirectReview(value:DirectBusinessReviewContextV2,selected:boolean):string {
 const subject=value.subject,lines=[`Business review: ${value.model_id} version ${subject.version}`,`Authored owner: ${subject.owner}`,`Business subject (craft.business-review-keysort/v2, sha256): ${value.review_sha256}`,`Source capture: ${value.source_capture.capture_sha256}`,'Authority effect: none',selected?'Selected native conventions are outside the business subject.':'Source-only review; no native selection or application acceptance.'];
 if(value.source_capture.source)lines.push(`Source: ${value.source_capture.source.path}; sha256 ${value.source_capture.source.sha256}; ${value.source_capture.source.bytes} bytes`);
 for(const requirement of subject.executable.requirements){
  lines.push('',`Requirement ${requirement.id}: ${requirement.meaning}`,`Context: ${requirement.context}`,...requirement.applies_when.map(s=>'Applies when: '+s),...requirement.actors.map(s=>'Informational actor: '+s),...requirement.boundaries.map(s=>'Boundary: '+s));
  for(const [label,cases]of [['Example',requirement.examples],['Counterexample',requirement.counterexamples]]as const)for(const row of cases)lines.push(`${label} ${row.case_id}: Given ${row.given}; When ${row.when}; Then ${row.then}; Why ${row.why}`);
 }
 for(const entity of subject.executable.entities)lines.push('',`Entity ${entity.id}: ${entity.meaning}`,`Identity field: ${entity.identity}`,...entity.fields.map(field=>`${field.name}: ${field.type} — ${field.meaning}`));
 for(const rule of subject.authored_rules)lines.push('',`Rule ${rule.id}: ${rule.meaning}`,`Input ${rule.input.name}: ${rule.input.type_ref}`,`Condition: ${rule.condition.value.root}.${rule.condition.value.path.join('.')} is true`);
 for(const operation of subject.executable.operations)lines.push('',`Operation ${operation.id}: ${operation.meaning}`,`Input ${operation.input.name}: ${operation.input.type_ref}; output ${operation.output_ref}`,...operation.guards.map(guard=>`Guard ${guard.rule_ref}: ${JSON.stringify(guard.arguments)}`),`Result: ${operation.result.root}${operation.result.path.map(p=>'.'+p).join('')}`,`On rejection: ${operation.on_rejection}`,`Effects: ${operation.effects.join(', ')||'none'}`);
 for(const entry of subject.executable.entries)lines.push(`Entry ${entry.id}: ${entry.public_name} invokes ${entry.operation_ref}; permission ${entry.permission.kind}`);
 lines.push('',`Optional assurance: ${subject.assurance.claims.length} claims; code generation does not require claims.`,`Executable: ${subject.executable_sha256}`,`Assurance: ${subject.assurance_sha256}`);
 for(const definition of subject.assurance.definitions)lines.push(`Definition ${definition.id}: ${definition.meaning}; ${definition.boolean_field.root}.${definition.boolean_field.path.join('.')}`);
 for(const claim of subject.assurance.claims)lines.push(`Claim ${claim.id} version ${claim.version}; logic ${claim.logic_profile}; supersedes ${claim.supersedes??'none'}`,`Requirement: ${claim.requirement_ref}`,...claim.sorts.map(sort=>`Sort ${sort.name}: ${sort.type_ref}`),...claim.predicates.map(predicate=>`Predicate ${predicate.name}(${predicate.sort_refs.join(', ')}): ${predicate.definition_ref}`),...claim.constants.map(constant=>`Constant ${constant.name}: ${constant.sort_ref}`),`Proposition: ${claim.proposition}`,`Subjects: ${claim.subject_refs.join(', ')}`,`Ceiling: ${claim.ceiling}`);
 return lines.join('\n')+'\n';
}
/** Implementation-stage factory; only the exact trusted recipe owner's registry
 * may supply a selected model. Actual loaded selection qualification is K02. */
export function createBusinessReviewSubjectOwnerV2(recipeOwner:BusinessCoreRecipeOwnerV2):BusinessReviewSubjectOwnerV2 {
 const methods=[recipeOwner.select,recipeOwner.assertCurrent,recipeOwner.dispose];
 const owned=new WeakMap<object,{selection:PreparedBusinessReviewV2['selection'];fingerprint:string}>();
 const current=()=>{
  if(implementationIdentity()!==executingImplementation||methods[0]!==recipeOwner.select||methods[1]!==recipeOwner.assertCurrent||methods[2]!==recipeOwner.dispose)fail('OWNER_STALE','/review-v2','review implementation or exact recipe owner changed');
 };
 const assertCurrent=(value:PreparedBusinessReviewV2):void=>{
  const state=value&&typeof value==='object'?owned.get(value):undefined;if(!state)fail('HANDLE','/review-v2','original selected review from this exact owner required');
  current();recipeOwner.assertCurrent(state.selection);
  if(value.selection!==state.selection||dataDigest(value)!==state.fingerprint)fail('CORRESPONDENCE','/review-v2','original review/selection changed');
 };
 return Object.freeze({prepare(selection:PreparedBusinessReviewV2['selection'],modelId:string,subject:BusinessReviewSubjectV2){
  current();recipeOwner.assertCurrent(selection);
  const model=selection.models.find(row=>row.model_id===modelId);if(!model)fail('CORRESPONDENCE','/model_id','original selected model required');
  const supplied=validateBusinessAuthoringContractV2('review',subject);
  const checked=directReviewSubject({source:model.source,spec:model.spec,executable:supplied.executable,assurance:supplied.assurance},supplied);
  if(checked.executable_sha256!==model.executable_sha256||checked.assurance_sha256!==model.assurance_sha256)fail('CORRESPONDENCE','/review-v2','selected executable and assurance differ');
  const value:PreparedBusinessReviewV2=Object.freeze({kind:'prepared-business-review-v2',selection,model_id:modelId,subject:checked.review,source_capture:model.capture,review_sha256:dataDigest(checked.review),authority_effect:'none'});
  recipeOwner.assertCurrent(selection);owned.set(value,{selection,fingerprint:dataDigest(value)});assertCurrent(value);return value;
 },assertCurrent,render(value:PreparedBusinessReviewV2){assertCurrent(value);const text=renderDirectReview(value,true);assertCurrent(value);return text;}});
}

/** Genuine source-only component custody. Deliberately not PreparedBusinessReviewV2:
 * it has no selection, profile/native basis or accepted application privilege. */
export interface RegisteredSourceBusinessReviewV2 extends DirectBusinessReviewContextV2 {
 readonly kind:'registered-source-business-review-v2';
 readonly source_capture:Readonly<{kind:'source-only-review-capture-v2';capture_sha256:string;source:Readonly<{path:string;sha256:string;bytes:number}>}>;
}
export interface SourceBusinessReviewOwnerV2 {
 prepare(absoluteSourceFile:string,transfer:unknown):RegisteredSourceBusinessReviewV2;
 assertCurrent(review:RegisteredSourceBusinessReviewV2):void;
 dispose(review:RegisteredSourceBusinessReviewV2):void;
 render(review:RegisteredSourceBusinessReviewV2):string;
}
const sourceReviewOwners=new WeakMap<object,{assertCurrent:SourceBusinessReviewOwnerV2['assertCurrent']}>();
export function assertSourceBusinessReviewOwnerV2(owner:SourceBusinessReviewOwnerV2):void {
 const state=owner&&typeof owner==='object'?sourceReviewOwners.get(owner):undefined;
 if(!state||state.assertCurrent!==owner.assertCurrent)fail('OWNER','/source-review-v2','original source-review owner factory instance required');
}
function sourceReviewFile(file:string):{text:string;fingerprint:string} {
 if(typeof file!=='string'||file.length>4096||!path.isAbsolute(file)||path.normalize(file)!==file||file.includes('\\')||/[\u0000-\u001f\u007f]/.test(file))fail('PATH','/source-review-v2','normalized absolute original source file required');
 const parents=()=>{
  let at=path.parse(file).root;const root=lstatSync(at,{bigint:true});
  if(!root.isDirectory()||root.isSymbolicLink())fail('SYMLINK',file,'original root directory required');
  const rows:Record<string,string>[]=[{path:at,dev:String(root.dev),ino:String(root.ino)}];
  for(const part of file.slice(at.length).split(path.sep).filter(Boolean)){
   at=path.join(at,part);const stat=lstatSync(at,{bigint:true});
   if(stat.isSymbolicLink()||at!==file&&!stat.isDirectory())fail('SYMLINK',file,'source/parent symlinks or non-directory parents reject');
   rows.push({path:at,dev:String(stat.dev),ino:String(stat.ino)});
  }return rows;
 };
 const beforeParents=parents(),before=lstatSync(file,{bigint:true});
 if(!before.isFile()||before.size<1n||before.size>1048576n)fail('SOURCE','/source-review-v2','bounded regular source required');
 const physical=(stat:typeof before)=>[stat.dev,stat.ino,stat.size,stat.mode,stat.mtimeNs,stat.ctimeNs].map(String);
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);const parts:Buffer[]=[];let bytes=0;
 try{
  if(dataDigest(physical(fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))fail('SOURCE_STALE',file,'source changed while opening');
  for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>1048576)fail('SOURCE',file,'source byte budget exceeded');parts.push(buffer.subarray(0,count));}
  if(dataDigest(physical(fstatSync(fd,{bigint:true})))!==dataDigest(physical(before)))fail('SOURCE_STALE',file,'source changed while reading');
 }finally{closeSync(fd);}
 const buffer=Buffer.concat(parts),after=lstatSync(file,{bigint:true});
 if(!after.isFile()||bytes!==Number(before.size)||dataDigest(physical(after))!==dataDigest(physical(before))||dataDigest(parents())!==dataDigest(beforeParents))fail('SOURCE_STALE',file,'source physical/parent identity changed');
 let text:string;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(buffer);}catch{return fail('SOURCE',file,'exact UTF-8 source required');}
 return {text,fingerprint:dataDigest({file,parents:beforeParents,physical:physical(before),sha256:sha256(buffer)})};
}
export function createSourceBusinessReviewOwnerV2():SourceBusinessReviewOwnerV2 {
 const owned=new WeakMap<object,{file:string;capture:string;fingerprint:string;disposed:boolean}>();
 const assertCurrent=(value:RegisteredSourceBusinessReviewV2):void=>{
  const state=value&&typeof value==='object'?owned.get(value):undefined;if(!state)fail('HANDLE','/source-review-v2','original source-only review from this exact owner required');
  if(state.disposed)fail('DISPOSED','/source-review-v2','source-only review disposed');
  if(implementationIdentity()!==executingImplementation||sourceReviewFile(state.file).fingerprint!==state.capture||dataDigest(value)!==state.fingerprint)fail('SOURCE_STALE','/source-review-v2','original source/module/data changed');
 };
 const owner:SourceBusinessReviewOwnerV2=Object.freeze({prepare(file:string,transfer:unknown){
  if(implementationIdentity()!==executingImplementation)fail('MODULE_STALE','/source-review-v2','reload changed review implementation');
  const checked=checkCoreDirectBusinessRecipeV2(transfer),captured=sourceReviewFile(file);
  if(captured.text!==checked.transfer.source.text)fail('CORRESPONDENCE',file,'original physical source differs from independently checked transfer');
  const {path:sourcePath,sha256:sourceHash,bytes:sourceBytes}=checked.transfer.source;
  const value=captureJson({kind:'registered-source-business-review-v2',model_id:checked.review.model_id,subject:checked.review,source_capture:{kind:'source-only-review-capture-v2',capture_sha256:captured.fingerprint,source:{path:sourcePath,sha256:sourceHash,bytes:sourceBytes}},review_sha256:dataDigest(checked.review),authority_effect:'none'}) as unknown as RegisteredSourceBusinessReviewV2;
  owned.set(value,{file,capture:captured.fingerprint,fingerprint:dataDigest(value),disposed:false});assertCurrent(value);return value;
 },assertCurrent,dispose(value:RegisteredSourceBusinessReviewV2){assertCurrent(value);owned.get(value)!.disposed=true;},render(value:RegisteredSourceBusinessReviewV2){assertCurrent(value);const result=renderDirectReview(value,false);assertCurrent(value);return result;}});
 sourceReviewOwners.set(owner,{assertCurrent});return owner;
}
