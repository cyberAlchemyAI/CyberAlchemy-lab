import {closeSync,constants,fchmodSync,fstatSync,lstatSync,openSync,readSync,writeSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest,reject,sha256} from './contracts.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import {assertBusinessAuthoringReviewCurrent,type PreparedBusinessAuthoringReview} from './business-review.js';
import type {BusinessDecision,LegacyMeaningSubject} from './business-authoring-protocol.js';
import {validateBusinessAuthoringContractV2} from './business-authoring-schema-v2.js';
import {createBusinessReviewSubjectOwnerV2,assertSourceBusinessReviewOwnerV2,type DirectBusinessReviewContextV2,type RegisteredSourceBusinessReviewV2,type SourceBusinessReviewOwnerV2} from './business-review.js';
import type {BusinessDecisionV2,BusinessReviewOwnerV2,PreparedBusinessReviewV2,CapturedBusinessDecisionV2,AcceptedBusinessReviewV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessCoreRecipeOwnerV2} from './business-authoring-stages-v2.js';

/** Explicit local fixture/user decisions, without owner authentication or executable carriers.
 * Post-create failures preserve bounded residue: Node has no inode-conditional unlink,
 * so deleting by pathname could remove another writer's replacement. No failure path deletes files.
 * Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md; B06.2 owns accepted materialization. */
export interface BusinessDecisionRequest {readonly decision_id:string;readonly owner:string;readonly outcome:'accepted'|'declined';readonly reviewed_digest:string}
export interface CapturedBusinessDecision {
 readonly kind:'captured-business-decision';readonly review:PreparedBusinessAuthoringReview;
 readonly decision:BusinessDecision;readonly file:Readonly<{path:string;sha256:string;bytes:number}>;
 readonly authority_effect:'none';
}
export interface AcceptedBusinessDecision {
 readonly kind:'accepted-business-decision';readonly review:PreparedBusinessAuthoringReview;readonly capture:CapturedBusinessDecision;
 readonly subject:BusinessDecision['subject'];readonly legacy_meaning_subjects:readonly LegacyMeaningSubject[];
 readonly definition_closure:BusinessDecision['definition_closure'];readonly authority_effect:'none';
}
interface Physical {readonly dev:bigint;readonly ino:bigint;readonly size:bigint;readonly mode:bigint;readonly mtime:bigint;readonly ctime:bigint}
interface ParentIdentity {readonly path:string;readonly dev:bigint;readonly ino:bigint}
interface Parent {readonly file:string;readonly fd:number;readonly leaf:string;readonly parents:readonly ParentIdentity[]}
interface FileCapture {readonly file:CapturedBusinessDecision['file'];readonly physical:Physical;readonly parents:readonly ParentIdentity[];readonly text:string}
const captures=new WeakMap<object,{review:PreparedBusinessAuthoringReview;file:FileCapture;fingerprint:string}>();
const accepted=new WeakMap<object,{review:PreparedBusinessAuthoringReview;capture:CapturedBusinessDecision;fingerprint:string}>();
const maxBytes=16777216;
function fail(code:string,at:string,message:string):never{return reject('BUSINESS_DECISION_'+code,at,message);}
function physical(stat:BigIntStats):Physical {return {dev:stat.dev,ino:stat.ino,size:stat.size,mode:stat.mode,mtime:stat.mtimeNs,ctime:stat.ctimeNs};}
function samePhysical(a:Physical,b:Physical):boolean {return a.dev===b.dev&&a.ino===b.ino&&a.size===b.size&&a.mode===b.mode&&a.mtime===b.mtime&&a.ctime===b.ctime;}
function sameParents(a:readonly ParentIdentity[],b:readonly ParentIdentity[]):boolean {return a.length===b.length&&a.every((item,index)=>item.path===b[index]?.path&&item.dev===b[index]?.dev&&item.ino===b[index]?.ino);}
function absoluteFile(value:string):string {
 if(typeof value!=='string'||!value||value.length>4096||!path.isAbsolute(value)||value.includes('\\')||value.includes('\0')||path.normalize(value)!==value||value.endsWith(path.sep)||value.split(path.sep).some(part=>part==='.'||part==='..'))fail('PATH','/file','an explicit normalized absolute file path is required');
 return value;
}
function parentIdentities(directory:string):readonly ParentIdentity[] {
 let current=path.parse(directory).root;const result:ParentIdentity[]=[];
 const check=()=>{let stat:BigIntStats;try{stat=lstatSync(current,{bigint:true});}catch{return fail('PATH',current,'existing parent directories are required');}if(stat.isSymbolicLink())fail('SYMLINK',current,'parent symlinks are forbidden');if(!stat.isDirectory())fail('PATH',current,'parent must be a directory');result.push({path:current,dev:stat.dev,ino:stat.ino});};
 check();for(const part of directory.slice(current.length).split(path.sep).filter(Boolean)){current=path.join(current,part);check();}return result;
}
function openParent(value:string):Parent {
 const file=absoluteFile(value),directory=path.dirname(file),parents=parentIdentities(directory);let fd:number;
 try{fd=openSync(directory,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW|constants.O_NONBLOCK);}catch{return fail('PATH',directory,'parent ownership cannot be opened safely');}
 try{
  const stat=fstatSync(fd,{bigint:true}),expected=parents[parents.length-1]!;
  if(!stat.isDirectory()||stat.dev!==expected.dev||stat.ino!==expected.ino||!sameParents(parents,parentIdentities(directory)))fail('FILE_DRIFT',file,'parent changed while opening');
  return {file,fd,leaf:path.basename(file),parents};
 }catch(error){closeSync(fd);throw error;}
}
// Linux package boundary: an opened parent descriptor anchors effects to the inspected inode.
// The /proc link is internal descriptor addressing, never a caller-supplied symlink path.
const anchored=(parent:Parent)=>`/proc/self/fd/${parent.fd}/${parent.leaf}`;
function assertParent(parent:Parent):void {if(!sameParents(parent.parents,parentIdentities(path.dirname(parent.file))))fail('FILE_DRIFT',parent.file,'parent path ownership changed');}
function captureAt(parent:Parent):FileCapture {
 assertParent(parent);const filename=anchored(parent);let before:BigIntStats;
 try{before=lstatSync(filename,{bigint:true});}catch{return fail('PATH',parent.file,'decision file is unavailable');}
 if(before.isSymbolicLink())fail('SYMLINK',parent.file,'decision symlinks are forbidden');
 if(!before.isFile())fail('FILE_KIND',parent.file,'regular decision file required');
 if(before.size>BigInt(maxBytes))fail('FILE_BUDGET',parent.file,'decision exceeds the closed byte budget');
 let fd:number;try{fd=openSync(filename,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);}catch{return fail('FILE_DRIFT',parent.file,'decision cannot be opened safely');}
 const parts:Buffer[]=[];let bytes=0;
 try{
  const opened=fstatSync(fd,{bigint:true});if(!opened.isFile()||!samePhysical(physical(before),physical(opened)))fail('FILE_DRIFT',parent.file,'decision changed while opening');
  for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>maxBytes)fail('FILE_BUDGET',parent.file,'decision grew past its byte budget');parts.push(buffer.subarray(0,count));}
  if(!samePhysical(physical(before),physical(fstatSync(fd,{bigint:true}))))fail('FILE_DRIFT',parent.file,'decision changed while reading');
 }finally{closeSync(fd);}
 const after=lstatSync(filename,{bigint:true});assertParent(parent);
 if(!after.isFile()||!samePhysical(physical(before),physical(after))||BigInt(bytes)!==before.size)fail('FILE_DRIFT',parent.file,'decision path changed during capture');
 const buffer=Buffer.concat(parts);let text:string;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(buffer);}catch{return fail('FILE_ENCODING',parent.file,'decision must be exact UTF-8 JSON');}
 return {file:Object.freeze({path:parent.file,sha256:sha256(buffer),bytes}),physical:physical(after),parents:parent.parents,text};
}
function captureFile(file:string):FileCapture {const parent=openParent(file);try{return captureAt(parent);}finally{closeSync(parent.fd);}}
function moduleIdentity():string {
 const value=captureFile(fileURLToPath(import.meta.url));
 return dataDigest({sha256:value.file.sha256,bytes:value.file.bytes,physical:Object.fromEntries(Object.entries(value.physical).map(([key,item])=>[key,String(item)])),parents:value.parents.map(item=>({path:item.path,dev:String(item.dev),ino:String(item.ino)}))});
}
const executingModule=moduleIdentity();
function assertModule():void {let current:string;try{current=moduleIdentity();}catch{return fail('MODULE_STALE','/','owning decision implementation is unavailable or changed');}if(current!==executingModule)fail('MODULE_STALE','/','reload the owning implementation after byte or physical identity changes');}
function exactDecision(review:PreparedBusinessAuthoringReview,input:unknown):BusinessDecision {
 const decision=validateBusinessAuthoringContract<BusinessDecision>('decision',input);
 if(!decision.decision_id.trim()||!decision.owner.trim())fail('REVIEW_MISMATCH','/decision','nonblank explicit decision identity and owner required');
 if(decision.owner!==review.review.model_identity.owner||dataDigest(decision.subject)!==dataDigest(review.subject)||dataDigest(decision.legacy_meaning_subjects)!==dataDigest(review.legacy_meaning_subjects)||dataDigest(decision.definition_closure)!==dataDigest(review.definition_closure))fail('REVIEW_MISMATCH','/decision','decision must match the exact current model/version/owner/aggregate/legacy/definition scope');
 return decision;
}
function decodeDecision(review:PreparedBusinessAuthoringReview,file:FileCapture):BusinessDecision {
 let input:unknown;try{input=JSON.parse(file.text);}catch{return fail('FILE_JSON',file.file.path,'decision must contain one exact JSON record');}return exactDecision(review,input);
}
function registerCapture(review:PreparedBusinessAuthoringReview,file:FileCapture):CapturedBusinessDecision {
 const decision=decodeDecision(review,file),value:CapturedBusinessDecision=Object.freeze({kind:'captured-business-decision',review,decision,file:file.file,authority_effect:'none'});
 captures.set(value,{review,file,fingerprint:dataDigest(value)});assertBusinessDecisionCurrent(value);return value;
}
export function captureBusinessDecision(review:PreparedBusinessAuthoringReview,absoluteFilePath:string):CapturedBusinessDecision {
 assertBusinessAuthoringReviewCurrent(review);assertModule();const file=captureFile(absoluteFilePath);assertBusinessAuthoringReviewCurrent(review);return registerCapture(review,file);
}
function requestPayload(review:PreparedBusinessAuthoringReview,input:BusinessDecisionRequest):BusinessDecision {
 const request=captureJson(input) as unknown as BusinessDecisionRequest;
 if(!request||typeof request!=='object'||Array.isArray(request)||Object.keys(request).length!==4||!['decision_id','owner','outcome','reviewed_digest'].every(key=>Object.hasOwn(request,key))||typeof request.decision_id!=='string'||!request.decision_id.trim()||request.decision_id.length>4096||typeof request.owner!=='string'||!request.owner.trim()||request.owner.length>4096||!['accepted','declined'].includes(request.outcome)||typeof request.reviewed_digest!=='string'||!/^[a-f0-9]{64}$/.test(request.reviewed_digest))fail('REQUEST','/request','closed bounded explicit decision_id, owner, outcome and reviewed_digest are required');
 if(request.owner!==review.review.model_identity.owner||request.reviewed_digest!==review.subject.digest)fail('REVIEW_MISMATCH','/request','explicit owner and reviewed digest must match the current reviewed business subject');
 return exactDecision(review,{schema_version:'craft.business-decision/v1-candidate',decision_id:request.decision_id,owner:request.owner,outcome:request.outcome,subject:review.subject,legacy_meaning_subjects:review.legacy_meaning_subjects,definition_closure:review.definition_closure,authority_effect:'none'});
}
export function recordBusinessDecision(review:PreparedBusinessAuthoringReview,request:BusinessDecisionRequest,absoluteNewFilePath:string):CapturedBusinessDecision {
 assertBusinessAuthoringReviewCurrent(review);assertModule();const decision=requestPayload(review,request),parent=openParent(absoluteNewFilePath);
 const bytes=Buffer.from(JSON.stringify(decision,null,2)+'\n','utf8');let fd:number|undefined,owned:{dev:bigint;ino:bigint}|undefined;
 try{
  try{fd=openSync(anchored(parent),constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW|constants.O_NONBLOCK,0o600);}
  catch(error){if((error as NodeJS.ErrnoException).code==='EEXIST')return fail('DESTINATION_OCCUPIED',parent.file,'occupied destinations always reject unchanged, including identical repeats');return fail('PATH',parent.file,'new decision could not be created exclusively');}
  const created=fstatSync(fd,{bigint:true});owned={dev:created.dev,ino:created.ino};if(!created.isFile())fail('FILE_KIND',parent.file,'exclusive regular decision file required');
  fchmodSync(fd,0o600);assertParent(parent);assertBusinessAuthoringReviewCurrent(review);assertModule();
  let offset=0;while(offset<bytes.length){const written=writeSync(fd,bytes,offset,bytes.length-offset,null);if(written<=0)fail('FILE_DRIFT',parent.file,'complete decision write required');offset+=written;}
  const after=fstatSync(fd,{bigint:true});if(!after.isFile()||after.dev!==owned.dev||after.ino!==owned.ino||after.size!==BigInt(bytes.length)||(after.mode&0o777n)!==0o600n)fail('FILE_DRIFT',parent.file,'written file ownership/size/private mode differs');
  closeSync(fd);fd=undefined;assertParent(parent);assertBusinessAuthoringReviewCurrent(review);assertModule();
  const captured=captureAt(parent);if(captured.physical.dev!==owned.dev||captured.physical.ino!==owned.ino||captured.file.sha256!==sha256(bytes))fail('FILE_DRIFT',parent.file,'actual written decision was replaced or changed');
  return registerCapture(review,captured);
 }finally{try{if(fd!==undefined)closeSync(fd);}finally{closeSync(parent.fd);}}
}
export function assertBusinessDecisionCurrent(capture:CapturedBusinessDecision):void {
 const state=captures.get(capture);if(!state)fail('UNREGISTERED','/','only a captured decision registered by this owner is current');
 assertBusinessAuthoringReviewCurrent(state.review);assertModule();
 let current:FileCapture;try{current=captureFile(state.file.file.path);}catch(error){if((error as {code?:string}).code==='BUSINESS_DECISION_SYMLINK')throw error;return fail('STALE',state.file.file.path,'decision file or parent ownership changed or disappeared');}
 if(capture.review!==state.review||!samePhysical(current.physical,state.file.physical)||!sameParents(current.parents,state.file.parents)||current.file.sha256!==state.file.file.sha256||current.file.bytes!==state.file.file.bytes||dataDigest(capture)!==state.fingerprint)fail('STALE',state.file.file.path,'captured decision bytes, physical identity or data changed');
 exactDecision(state.review,capture.decision);
}
export function requireAcceptedBusinessDecision(review:PreparedBusinessAuthoringReview,capture:CapturedBusinessDecision):AcceptedBusinessDecision {
 assertBusinessAuthoringReviewCurrent(review);assertBusinessDecisionCurrent(capture);
 if(capture.review!==review)fail('FOREIGN_REVIEW','/review','re-capture explicitly for this exact original review owner');
 if(capture.decision.outcome!=='accepted')fail('DECLINED','/decision/outcome','an explicit matching accepted decision is required');
 const result:AcceptedBusinessDecision=Object.freeze({kind:'accepted-business-decision',review,capture,subject:review.subject,legacy_meaning_subjects:review.legacy_meaning_subjects,definition_closure:review.definition_closure,authority_effect:'none'});
 accepted.set(result,{review,capture,fingerprint:dataDigest(result)});assertAcceptedBusinessDecisionCurrent(result);return result;
}
export function assertAcceptedBusinessDecisionCurrent(value:AcceptedBusinessDecision):void {
 const state=accepted.get(value);if(!state)fail('UNREGISTERED','/','only the exact registered accepted decision guard is current');
 assertBusinessAuthoringReviewCurrent(state.review);assertBusinessDecisionCurrent(state.capture);
 if(value.review!==state.review||value.capture!==state.capture||state.capture.review!==state.review||state.capture.decision.outcome!=='accepted'||dataDigest(value)!==state.fingerprint)fail('STALE','/','exact accepted review, capture and scope must remain current');
}

/** Additive v2 closed decision protocol. Selected and source-only owner kinds are
 * intentionally distinct. Open Questions: K02 actual selected acceptance join. */
export type BusinessDecisionRequestV2=BusinessDecisionRequest;
export interface SourceBusinessDecisionV2 {
 readonly kind:'captured-source-business-decision-v2';readonly review:RegisteredSourceBusinessReviewV2;
 readonly decision:BusinessDecisionV2;readonly file:CapturedBusinessDecisionV2['file'];readonly authority_effect:'none';
}
export interface AcceptedSourceBusinessReviewV2 {
 readonly kind:'accepted-source-business-review-v2';readonly review:RegisteredSourceBusinessReviewV2;
 readonly decision:SourceBusinessDecisionV2;readonly authority_effect:'none';
}
interface CaptureV2<R> {readonly kind:string;readonly review:R;readonly decision:BusinessDecisionV2;readonly file:CapturedBusinessDecisionV2['file'];readonly authority_effect:'none'}
interface AcceptedV2<R,C> {readonly kind:string;readonly review:R;readonly decision:C;readonly authority_effect:'none'}
interface DecisionProtocolV2<R,C,A> {
 captureDecision(review:R,file:string):C;recordDecision(review:R,request:BusinessDecisionRequestV2,file:string):C;
 assertDecisionCurrent(decision:C):void;requireAccepted(review:R,decision:C):A;assertAcceptedCurrent(accepted:A):void;
}
function exactDirectDecision<R extends DirectBusinessReviewContextV2>(review:R,input:unknown):BusinessDecisionV2 {
 const decision=validateBusinessAuthoringContractV2('decision',input);
 if(!decision.owner.trim()||decision.owner!==review.subject.owner||decision.subject.sha256!==review.review_sha256||decision.capture_sha256!==review.source_capture.capture_sha256||decision.executable_sha256!==review.subject.executable_sha256||decision.assurance_sha256!==review.subject.assurance_sha256)fail('REVIEW_MISMATCH','/decision-v2','decision must match this exact owner, reviewed subject, source capture, executable and optional assurance');
 return decision;
}
/** JSON.parse alone discards duplicate names; scan decoded property tokens first. */
function decisionJsonV2(text:string,file:string):unknown {
 const stack:Set<string>[]=[];
 try{
  for(let i=0;i<text.length;i++){
   const character=text[i];
   if(character==='{')stack.push(new Set());else if(character==='}')stack.pop();
   else if(character==='"'){
    const start=i;for(i++;i<text.length&&text[i]!=='"';i++)if(text[i]==='\\')i++;
    if(i>=text.length)fail('FILE_JSON',file,'unterminated decision string');
    let end=i+1;while(/[\t\n\r ]/.test(text[end]??'x'))end++;
    if(text[end]===':'&&stack.length){const key=JSON.parse(text.slice(start,i+1)) as string,keys=stack[stack.length-1]!;if(keys.has(key))fail('FILE_JSON',file,'duplicate decoded decision member');keys.add(key);}
   }
  }return JSON.parse(text);
 }catch(error){if((error as {code?:string}).code?.startsWith('BUSINESS_DECISION_'))throw error;return fail('FILE_JSON',file,'one exact nonduplicate JSON record required');}
}
function decisionProtocolV2<R extends DirectBusinessReviewContextV2,C extends CaptureV2<R>,A extends AcceptedV2<R,C>>(
 assertReview:(review:R)=>void,kinds:Readonly<{capture:C['kind'];accepted:A['kind']}>,
):DecisionProtocolV2<R,C,A> {
 const ownedCaptures=new WeakMap<object,{review:R;file:FileCapture;fingerprint:string}>();
 const ownedAccepted=new WeakMap<object,{review:R;decision:C;fingerprint:string}>();
 const assertDecisionCurrent=(value:C):void=>{
  const state=value&&typeof value==='object'?ownedCaptures.get(value):undefined;if(!state)fail('UNREGISTERED','/decision-v2','original decision from this exact owner required');
  assertReview(state.review);assertModule();let current:FileCapture;
  try{current=captureFile(state.file.file.path);}catch{return fail('STALE',state.file.file.path,'decision file or parent ownership changed');}
  if(value.review!==state.review||!samePhysical(current.physical,state.file.physical)||!sameParents(current.parents,state.file.parents)||current.file.sha256!==state.file.file.sha256||dataDigest(value)!==state.fingerprint)fail('STALE',state.file.file.path,'original decision physical identity, bytes or data changed');
  exactDirectDecision(state.review,value.decision);
 };
 const register=(review:R,file:FileCapture):C=>{
  const decision=exactDirectDecision(review,decisionJsonV2(file.text,file.file.path));
  const metadata=Object.freeze({...file.file,device:String(file.physical.dev),inode:String(file.physical.ino),mtime_ns:String(file.physical.mtime)});
  const value=Object.freeze({kind:kinds.capture,review,decision,file:metadata,authority_effect:'none'}) as unknown as C;
  ownedCaptures.set(value,{review,file,fingerprint:dataDigest(value)});assertDecisionCurrent(value);return value;
 };
 const assertAcceptedCurrent=(value:A):void=>{
  const state=value&&typeof value==='object'?ownedAccepted.get(value):undefined;if(!state)fail('UNREGISTERED','/accepted-v2','original accepted review from this exact owner required');
  assertReview(state.review);assertDecisionCurrent(state.decision);
  if(value.review!==state.review||value.decision!==state.decision||state.decision.review!==state.review||state.decision.decision.outcome!=='accepted'||dataDigest(value)!==state.fingerprint)fail('STALE','/accepted-v2','original accepted scope changed');
 };
 return Object.freeze({captureDecision(review:R,file:string):C{
  assertReview(review);assertModule();const captured=captureFile(file);assertReview(review);return register(review,captured);
 },recordDecision(review:R,input:BusinessDecisionRequestV2,file:string):C{
  assertReview(review);assertModule();const request=captureJson(input) as unknown as BusinessDecisionRequestV2;
  if(!request||typeof request!=='object'||Array.isArray(request)||Object.keys(request).length!==4||!['decision_id','owner','outcome','reviewed_digest'].every(key=>Object.hasOwn(request,key))||request.reviewed_digest!==review.review_sha256)fail('REQUEST','/request-v2','exact explicit decision identity, owner, outcome and current reviewed digest required');
  const decision=exactDirectDecision(review,{schema_version:'craft.business-decision/v2-candidate',decision_id:request.decision_id,owner:request.owner,outcome:request.outcome,subject:{algorithm:'sha256',canonicalization:'craft.business-review-keysort/v2',sha256:request.reviewed_digest},capture_sha256:review.source_capture.capture_sha256,executable_sha256:review.subject.executable_sha256,assurance_sha256:review.subject.assurance_sha256,authority_effect:'none'});
  const parent=openParent(file),bytes=Buffer.from(JSON.stringify(decision,null,2)+'\n');let fd:number|undefined;
  try{
   try{fd=openSync(anchored(parent),constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW|constants.O_NONBLOCK,0o600);}catch(error){if((error as NodeJS.ErrnoException).code==='EEXIST')return fail('DESTINATION_OCCUPIED',file,'occupied decision destinations reject unchanged');return fail('PATH',file,'exclusive decision create failed');}
   const created=fstatSync(fd,{bigint:true});if(!created.isFile())fail('FILE_KIND',file,'exclusive regular decision required');
   fchmodSync(fd,0o600);assertParent(parent);assertReview(review);assertModule();
   let offset=0;while(offset<bytes.length){const n=writeSync(fd,bytes,offset,bytes.length-offset,null);if(n<=0)fail('FILE_DRIFT',file,'complete decision write required');offset+=n;}
   const stat=fstatSync(fd,{bigint:true});if(!stat.isFile()||stat.dev!==created.dev||stat.ino!==created.ino||stat.size!==BigInt(bytes.length)||(stat.mode&0o777n)!==0o600n)fail('FILE_DRIFT',file,'written decision identity/size/private mode changed');
   closeSync(fd);fd=undefined;assertParent(parent);assertReview(review);assertModule();const captured=captureAt(parent);
   if(captured.physical.dev!==created.dev||captured.physical.ino!==created.ino||captured.file.sha256!==sha256(bytes))fail('FILE_DRIFT',file,'written decision replaced before capture');
   return register(review,captured);
  }finally{try{if(fd!==undefined)closeSync(fd);}finally{closeSync(parent.fd);}}
 },assertDecisionCurrent,requireAccepted(review:R,decision:C):A{
  assertReview(review);assertDecisionCurrent(decision);
  if(decision.review!==review)fail('FOREIGN_REVIEW','/review-v2','re-capture explicitly for this exact original review');
  if(decision.decision.outcome!=='accepted')fail('DECLINED','/decision-v2/outcome','an explicit matching accepted decision is required');
  const value=Object.freeze({kind:kinds.accepted,review,decision,authority_effect:'none'}) as unknown as A;
  ownedAccepted.set(value,{review,decision,fingerprint:dataDigest(value)});assertAcceptedCurrent(value);return value;
 },assertAcceptedCurrent});
}
export interface RecordingBusinessReviewOwnerV2 extends BusinessReviewOwnerV2 {
 recordDecision(review:PreparedBusinessReviewV2,request:BusinessDecisionRequestV2,file:string):CapturedBusinessDecisionV2;
 render(review:PreparedBusinessReviewV2):string;
}
/** Full selected owner; the exact U03 recipe instance remains the admission gate. */
export function createBusinessReviewOwnerV2(recipes:BusinessCoreRecipeOwnerV2):RecordingBusinessReviewOwnerV2 {
 const subjects=createBusinessReviewSubjectOwnerV2(recipes);
 const decisions=decisionProtocolV2<PreparedBusinessReviewV2,CapturedBusinessDecisionV2,AcceptedBusinessReviewV2>(subjects.assertCurrent,{capture:'captured-business-decision-v2',accepted:'accepted-business-review-v2'});
 return Object.freeze({...subjects,...decisions});
}
export type SourceBusinessDecisionOwnerV2=DecisionProtocolV2<RegisteredSourceBusinessReviewV2,SourceBusinessDecisionV2,AcceptedSourceBusinessReviewV2>;
/** Positive component custody without fabricating any selected/native handle. */
export function createSourceBusinessDecisionOwnerV2(subjects:SourceBusinessReviewOwnerV2):SourceBusinessDecisionOwnerV2 {
 assertSourceBusinessReviewOwnerV2(subjects);const original=subjects.assertCurrent;
 const assertReview=(review:RegisteredSourceBusinessReviewV2)=>{assertSourceBusinessReviewOwnerV2(subjects);if(subjects.assertCurrent!==original)fail('OWNER_STALE','/source-review-v2','original source owner changed');subjects.assertCurrent(review);};
 return decisionProtocolV2<RegisteredSourceBusinessReviewV2,SourceBusinessDecisionV2,AcceptedSourceBusinessReviewV2>(assertReview,{capture:'captured-source-business-decision-v2',accepted:'accepted-source-business-review-v2'});
}
