import {constants,openSync,closeSync,readSync,fstatSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {TextDecoder} from 'node:util';
import type {BusinessSpecData,ParsedBusinessSource,ResolvedBusinessSpec,BusinessClaim} from './business-authoring-protocol.js';
import {assertParsedBusinessSourceCurrent,parseBusinessSource} from './business-authoring-parser.js';
import {businessReject,businessCanonical,businessHash,businessDataDigest,businessSourceKey,businessSymbol,freezeBusinessData,BusinessSourceRejected} from './business-authoring-model.js';
import {parseFormalProposition} from './formal-claim.js';
import {CompilationRejected} from './model.js';
import type {ParsedBusinessSourceV2,ResolvedBusinessSpecV2} from './business-authoring-protocol-v2.js';
import type {BusinessResolverOwnerV2} from './business-authoring-stages-v2.js';
import {assertParsedBusinessSourceV2Current,parseBusinessSourceV2} from './business-authoring-parser.js';
import {alchDirectExecutableDigestV2,alchOptionalAssuranceDigestV2} from './business-authoring-identity-v2.js';
// Open questions: semantic interpretation/execution and acceptance belong to B03/B04 onward.
type State={parsed:ParsedBusinessSource;fingerprint:string;disposed:boolean;physical?:()=>void};
const resolvedRegistry=new WeakMap<object,State>();
export function assertResolvedBusinessSpecCurrent(value:ResolvedBusinessSpec):void {
  const state=value&&typeof value==='object'?resolvedRegistry.get(value):undefined;
  if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'registered resolved spec required');
  if(state.disposed)businessReject('BUSINESS_DISPOSED',value.source.path,1,1,'resolved spec was disposed');
  assertParsedBusinessSourceCurrent(state.parsed);
  if(businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',value.source.path,1,1,'resolved spec changed');
  state.physical?.();
}
export function disposeResolvedBusinessSpec(value:ResolvedBusinessSpec):void {
  const state=value&&typeof value==='object'?resolvedRegistry.get(value):undefined;
  if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'registered resolved spec required');
  if(state.disposed)businessReject('BUSINESS_DISPOSED',value.source.path,1,1,'resolved spec already disposed');
  state.disposed=true;
}
export function resolveBusinessSpec(parsed:ParsedBusinessSource):ResolvedBusinessSpec {
  assertParsedBusinessSourceCurrent(parsed);
  const data=parsed.data,source=parsed.source.path;
  const fail=(code:string,kind:string,id:string,clause:string,message:string):never=>{
    const base=kind+':'+id,span=data.source_spans.find(s=>(s.selector.startsWith(base+'/'+clause+'/line:')||s.selector.startsWith(base+'/'+clause+':')))??data.source_spans.find(s=>s.selector.startsWith(base+'/line:'));
    return businessReject(code,source,span?.line??1,span?.column??1,message);
  };
  const index=<T extends {id:string}>(items:readonly T[])=>new Map(items.map(x=>[x.id,x]));
  const entities=index(data.entities),requirements=index(data.requirements),definitions=index(data.definitions),claims=index(data.claims),rules=index(data.rules),operations=index(data.operations);
  const target=<T>(map:Map<string,T>,ref:string,kind:string,id:string,clause:string):T=>map.get(ref)??fail('BUSINESS_REFERENCE',kind,id,clause,'unknown explicit reference '+ref);
  if(data.operations.length>16||data.capabilities.length>16||data.operations.length+data.capabilities.length>32)businessReject('BUSINESS_SOURCE_BUDGET',source,1,1,'operation/exposure entry budget exceeded');
  for(const entity of data.entities){
    if(!entity.fields.some(f=>f.name===entity.identity))fail('BUSINESS_REFERENCE','entity',entity.id,'identity','identity must select a declared field');
  }
  for(const definition of data.definitions){
    target(requirements,definition.requirement_ref,'definition',definition.id,'requirement');
    const entity=target(entities,definition.input.type_ref,'definition',definition.id,'input');
    if(definition.boolean_field.root!==definition.input.name)fail('BUSINESS_REFERENCE','definition',definition.id,'boolean-field','Boolean path root must be the explicit input');
    const field=entity.fields.find(f=>f.name===definition.boolean_field.path[0]);
    if(!field)fail('BUSINESS_REFERENCE','definition',definition.id,'boolean-field','Boolean path must select a declared Entity field');
    if(field!.type!=='Bool')fail('BUSINESS_TYPE','definition',definition.id,'boolean-field','definition must select a Bool field');
  }
  for(const claim of data.claims){
    target(requirements,claim.requirement_ref,'formal-claim',claim.id,'requirement');
    const sorts=new Map(claim.sorts.map(s=>[s.name,s]));
    const names=new Set<string>();
    for(const item of [...claim.sorts,...claim.predicates,...claim.constants]){
      const normalized=businessSymbol(item.name);
      if(names.has(normalized))fail('BUSINESS_AMBIGUOUS','formal-claim',claim.id,'proposition','formal signature names collide');names.add(normalized);
    }
    for(const sort of claim.sorts)target(entities,sort.type_ref,'formal-claim',claim.id,'sort:'+sort.name);
    for(const constant of claim.constants)target(sorts,constant.sort_ref,'formal-claim',claim.id,'constant:'+constant.name);
    for(const predicate of claim.predicates){
      const sort=target(sorts,predicate.sort_refs[0]!,'formal-claim',claim.id,'predicate:'+predicate.name);
      const definition=target(definitions,predicate.definition_ref,'formal-claim',claim.id,'predicate:'+predicate.name);
      if(definition.input.type_ref!==sort.type_ref)fail('BUSINESS_TYPE','formal-claim',claim.id,'predicate:'+predicate.name,'predicate sort Entity differs from definition input Entity');
    }
    validateProposition(claim,(code,message)=>fail(code,'formal-claim',claim.id,'proposition',message));
  }
  for(const rule of data.rules){
    const entity=target(entities,rule.input.type_ref,'rule',rule.id,'input'),claim=target(claims,rule.claim_ref,'rule',rule.id,'claim');
    const constants=new Map(claim.constants.map(c=>[c.name,c])),mapped=new Set<string>();
    for(const binding of rule.bindings){
      const constant=target(constants,binding.constant_ref,'rule',rule.id,'bind:'+binding.constant_ref);
      if(binding.parameter_ref!==rule.input.name)fail('BUSINESS_REFERENCE','rule',rule.id,'bind:'+binding.constant_ref,'binding must name the explicit Rule input');
      if(mapped.has(binding.parameter_ref))fail('BUSINESS_AMBIGUOUS','rule',rule.id,'bind:'+binding.constant_ref,'backend cannot bind multiple constants to one parameter');mapped.add(binding.parameter_ref);
      const sort=claim.sorts.find(s=>s.name===constant.sort_ref)!;
      if(sort.type_ref!==entity.id)fail('BUSINESS_TYPE','rule',rule.id,'bind:'+binding.constant_ref,'constant sort differs from parameter Entity');
    }
    if(rule.bindings.length!==claim.constants.length||claim.constants.some(c=>!rule.bindings.some(b=>b.constant_ref===c.name)))fail('BUSINESS_REQUIRED','rule',rule.id,'bind','bind every formal constant exactly once');
  }
  for(const operation of data.operations){
    target(entities,operation.input.type_ref,'operation',operation.id,'input');target(entities,operation.output_ref,'operation',operation.id,'output');
    if(operation.output_ref!==operation.input.type_ref)fail('BUSINESS_TYPE','operation',operation.id,'output','whole-input output must equal input Entity');
    if(operation.result.root!==operation.input.name||operation.result.path.length)fail('BUSINESS_REFERENCE','operation',operation.id,'returns','return must name the whole explicit input');
    if(operation.guards.length!==1)fail('BUSINESS_UNSUPPORTED','operation',operation.id,'requires','exactly one Rule guard supported');
    const guard=operation.guards[0]!,rule=target(rules,guard.rule_ref,'operation',operation.id,'requires');
    if(rule.input.type_ref!==operation.input.type_ref)fail('BUSINESS_TYPE','operation',operation.id,'requires','guard Entity differs from operation input');
    if(guard.arguments.length!==1||guard.arguments[0]!.parameter!==rule.input.name||guard.arguments[0]!.value.root!==operation.input.name||guard.arguments[0]!.value.path.length)fail('BUSINESS_REFERENCE','operation',operation.id,'requires','guard arguments must explicitly map the Rule parameter to the whole operation input');
  }
  const publicNames=new Set<string>();
  for(const capability of data.capabilities){
    target(operations,capability.operation_ref,'capability',capability.id,'invokes');
    const normalized=businessSymbol(capability.public_name);if(publicNames.has(normalized))fail('BUSINESS_AMBIGUOUS','capability',capability.id,'public-name','colliding public name');publicNames.add(normalized);
  }
  const result=freezeBusinessData<ResolvedBusinessSpec>({kind:'resolved-business-spec',data,source:parsed.source,business_sha256:businessDataDigest(data)},source);
  resolvedRegistry.set(result,{parsed,fingerprint:businessHash(businessCanonical(result)),disposed:false});return result;
}
function validateProposition(claim:BusinessClaim,fail:(code:string,message:string)=>never):void {
  // Reuse the existing finite formal parser. This validates data; it proves/executes nothing.
  const tokens=claim.proposition.match(/[A-Za-z_][A-Za-z0-9_.-]*|[^\s]/g)??[];
  let depth=0;for(const token of tokens){if(token==='('&&++depth>64)fail('BUSINESS_SOURCE_BUDGET','formula nesting exceeds capture depth');if(token===')')depth--;}
  if(tokens.length>10000||tokens.filter(t=>['not','implies','forall','exists'].includes(t)).length>64)fail('BUSINESS_SOURCE_BUDGET','formula recursion budget exceeded');
  if(tokens.some(t=>t==='forall'||t==='exists'))fail('BUSINESS_UNSUPPORTED','quantifiers are outside epoch 1');
  try{parseFormalProposition(claim.proposition,{sorts:claim.sorts.map(s=>({name:s.name})),functions:[],predicates:claim.predicates.map(p=>({name:p.name,parameter_sorts:[...p.sort_refs]})),constants:claim.constants.map(c=>({name:c.name,sort:c.sort_ref}))});}
  catch(error){if(error instanceof CompilationRejected){const code=error.issues[0]?.code??'FOL_SYNTAX';fail(/UNKNOWN|UNBOUND|UNUSED/.test(code)?'BUSINESS_REFERENCE':/SORT_MISMATCH|ARITY/.test(code)?'BUSINESS_TYPE':/DUPLICATE/.test(code)?'BUSINESS_AMBIGUOUS':'BUSINESS_SYNTAX',error.message);}throw error;}
}
type FileCapture={text:string;fingerprint:string};
function captureFile(root:string,relative:string):FileCapture {
  const reject=(code:string,message:string):never=>businessReject(code,relative,1,1,message);
  let cursor=path.parse(root).root;const directories:string[]=[cursor];
  for(const segment of root.slice(cursor.length).split(path.sep).filter(Boolean)){cursor=path.join(cursor,segment);directories.push(cursor);}
  cursor=root;for(const part of relative.split('/').slice(0,-1)){cursor=path.join(cursor,part);directories.push(cursor);}
  const ownership:string[]=[];
  try{
    for(const directory of directories){const stat=lstatSync(directory,{bigint:true});if(stat.isSymbolicLink())reject('BUSINESS_SOURCE_SYMLINK','symlink directory forbidden');if(!stat.isDirectory())reject('BUSINESS_SOURCE_PATH','source ancestor must be a directory');ownership.push(`${directory}:${stat.dev}:${stat.ino}`);}
    const filename=path.join(root,relative),before=lstatSync(filename,{bigint:true});
    if(before.isSymbolicLink())reject('BUSINESS_SOURCE_SYMLINK','source symlink forbidden');if(!before.isFile())reject('BUSINESS_SOURCE_PATH','regular source file required');if(before.size>1048576n)reject('BUSINESS_SOURCE_BUDGET','source exceeds 1 MiB');
    const fd=openSync(filename,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
    let buffer:Buffer;
    try{
      const opened=fstatSync(fd,{bigint:true});if(!opened.isFile()||opened.dev!==before.dev||opened.ino!==before.ino)reject('BUSINESS_SOURCE_DRIFT','file ownership changed while opening');
      const chunks:Buffer[]=[];let total=0;
      for(;;){const chunk=Buffer.alloc(Math.min(65536,1048577-total));const read=readSync(fd,chunk,0,chunk.length,null);if(!read)break;total+=read;if(total>1048576)reject('BUSINESS_SOURCE_BUDGET','source exceeds 1 MiB');chunks.push(chunk.subarray(0,read));}
      buffer=Buffer.concat(chunks);const after=fstatSync(fd,{bigint:true});
      if(after.size!==before.size||after.mtimeNs!==before.mtimeNs||after.ctimeNs!==before.ctimeNs)reject('BUSINESS_SOURCE_DRIFT','source changed during capture');
    }finally{closeSync(fd);}
    const afterPath=lstatSync(filename,{bigint:true});
    if(afterPath.isSymbolicLink())reject('BUSINESS_SOURCE_SYMLINK','source replaced by symlink');
    if(afterPath.dev!==before.dev||afterPath.ino!==before.ino||afterPath.mtimeNs!==before.mtimeNs||afterPath.ctimeNs!==before.ctimeNs)reject('BUSINESS_SOURCE_DRIFT','source path changed during capture');
    for(const [index,directory] of directories.entries()){const stat=lstatSync(directory,{bigint:true});if(stat.isSymbolicLink())reject('BUSINESS_SOURCE_SYMLINK','source ancestor replaced by symlink');if(!stat.isDirectory()||ownership[index]!==`${directory}:${stat.dev}:${stat.ino}`)reject('BUSINESS_SOURCE_DRIFT','source ancestor ownership changed');}
    let text:string;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(buffer);}catch{return reject('BUSINESS_SYNTAX','source must contain valid UTF-8');}
    return {text,fingerprint:businessHash(businessCanonical({ownership,dev:String(before.dev),ino:String(before.ino),size:String(before.size),mtime:String(before.mtimeNs),ctime:String(before.ctimeNs),sha256:businessHash(buffer)}))};
  }catch(error){if(error instanceof BusinessSourceRejected)throw error;return reject('BUSINESS_SOURCE_PATH','source is unavailable or ownership cannot be captured');}
}
export function prepareBusinessSpecFile(root:string,relative:string):ResolvedBusinessSpec {
  businessSourceKey(relative);
  if(typeof root!=='string'||!path.isAbsolute(root)||root.includes('\0')||root.split(path.sep).some(part=>part==='.'||part==='..'))businessReject('BUSINESS_SOURCE_PATH',relative,1,1,'absolute source root required');
  const absolute=path.resolve(root),captured=captureFile(absolute,relative),result=resolveBusinessSpec(parseBusinessSource(captured.text,relative));
  resolvedRegistry.get(result)!.physical=()=>{
    let current:FileCapture;
    try{current=captureFile(absolute,relative);}catch(error){if(error instanceof BusinessSourceRejected&&error.code==='BUSINESS_SOURCE_SYMLINK')throw error;businessReject('BUSINESS_SOURCE_DRIFT',relative,1,1,'captured source is unavailable or changed');}
    if(current.fingerprint!==captured.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',relative,1,1,'captured source bytes or ownership changed');
  };
  assertResolvedBusinessSpecCurrent(result);return result;
}

type StateV2={parsed:ParsedBusinessSourceV2;fingerprint:string;disposed:boolean;physical?:()=>void};
const resolvedRegistryV2=new WeakMap<object,StateV2>();
/** Source/reference owner only. It never forms Core selection/acceptance or executes claims. */
export function resolveBusinessSpecV2(parsed:ParsedBusinessSourceV2):ResolvedBusinessSpecV2 {
 assertParsedBusinessSourceV2Current(parsed);
 const data=parsed.data,source=parsed.source.path;
 const fail=(code:string,kind:string,id:string,clause:string,message:string):never=>{
  const spans=data.source_spans,start=spans.findIndex(s=>s.column===1&&(s.text===kind+' '+id+':'||kind==='formal-claim'&&s.text.startsWith('formal-claim '+id+' version ')));
  const end=spans.findIndex((s,i)=>i>start&&s.column===1),local=start<0?[]:spans.slice(start,end<0?undefined:end);
  const prefix=clause.replace(':',' '),span=local.find(s=>s.text.trimStart().startsWith(prefix+' '))??local[0];
  return businessReject(code,source,span?.line??1,span?.column??1,message);
 };
 const index=<T extends {id:string}>(rows:readonly T[])=>new Map(rows.map(row=>[row.id,row]));
 const entities=index(data.entities),requirements=index(data.requirements),definitions=index(data.definitions),rules=index(data.rules),operations=index(data.operations);
 const target=<T>(items:Map<string,T>,ref:string,kind:string,id:string,clause:string):T=>items.get(ref)??fail('BUSINESS_REFERENCE',kind,id,clause,'unknown explicit reference '+ref);
 const entity=data.entities[0]!;
 if(entity.fields.length!==2||entity.fields.filter(f=>f.type==='UInt64').length!==1||entity.fields.filter(f=>f.type==='Bool').length!==1)fail('BUSINESS_TYPE','entity',entity.id,'identity','U0 requires exactly one UInt64 and one Bool field');
 const identity=entity.fields.find(field=>field.name===entity.identity);
 if(!identity)fail('BUSINESS_REFERENCE','entity',entity.id,'identity','identity must name a declared field');
 if(identity!.type!=='UInt64')fail('BUSINESS_TYPE','entity',entity.id,'identity','identity must select the exact UInt64 field');
 for(const rule of data.rules){
  target(requirements,rule.requirement_ref,'rule',rule.id,'requirement');
  const input=target(entities,rule.input.type_ref,'rule',rule.id,'input'),path=rule.condition.value;
  if(path.root!==rule.input.name)fail('BUSINESS_REFERENCE','rule',rule.id,'condition','condition root must name the explicit Rule input');
  const field=input.fields.find(value=>value.name===path.path[0]);
  if(!field)fail('BUSINESS_REFERENCE','rule',rule.id,'condition','condition must select an explicit Entity field');
  if(field!.type!=='Bool')fail('BUSINESS_TYPE','rule',rule.id,'condition','condition must be a Bool field');
 }
 for(const operation of data.operations){
  target(entities,operation.input.type_ref,'operation',operation.id,'input');
  target(entities,operation.output_ref,'operation',operation.id,'output');
  if(operation.output_ref!==operation.input.type_ref)fail('BUSINESS_TYPE','operation',operation.id,'output','identity return must have the input Entity type');
  if(operation.result.root!==operation.input.name||operation.result.path.length)fail('BUSINESS_REFERENCE','operation',operation.id,'returns','result must name the entire explicit input');
  const guard=operation.guards[0]!,rule=target(rules,guard.rule_ref,'operation',operation.id,'requires');
  if(rule.input.type_ref!==operation.input.type_ref)fail('BUSINESS_TYPE','operation',operation.id,'requires','guard input Entity differs from Operation input');
  const argument=guard.arguments[0]!;
  if(argument.parameter!==rule.input.name||argument.value.root!==operation.input.name||argument.value.path.length)fail('BUSINESS_REFERENCE','operation',operation.id,'requires','guard must map the explicit Rule parameter to the whole Operation input');
 }
 for(const entry of data.entries)target(operations,entry.operation_ref,'entry',entry.id,'invokes');
 // Optional assurance is still well-formed authored source. It cannot repair an
 // omitted condition or contribute a hidden executable predicate.
 for(const definition of data.definitions){
  target(requirements,definition.requirement_ref,'definition',definition.id,'requirement');
  const input=target(entities,definition.input.type_ref,'definition',definition.id,'input');
  if(definition.boolean_field.root!==definition.input.name)fail('BUSINESS_REFERENCE','definition',definition.id,'boolean-field','definition root differs from its explicit input');
  const field=input.fields.find(value=>value.name===definition.boolean_field.path[0]);
  if(!field)fail('BUSINESS_REFERENCE','definition',definition.id,'boolean-field','definition field is undeclared');
  if(field!.type!=='Bool')fail('BUSINESS_TYPE','definition',definition.id,'boolean-field','definition must select a Bool field');
 }
 for(const claim of data.claims){
  target(requirements,claim.requirement_ref,'formal-claim',claim.id,'requirement');
  const sorts=new Map(claim.sorts.map(sort=>[sort.name,sort])),names=new Set<string>();
  for(const item of [...claim.sorts,...claim.predicates,...claim.constants]){
   const normalized=businessSymbol(item.name);
   if(names.has(normalized))fail('BUSINESS_AMBIGUOUS','formal-claim',claim.id,'proposition','formal signature names collide');names.add(normalized);
  }
  for(const sort of claim.sorts)target(entities,sort.type_ref,'formal-claim',claim.id,'sort:'+sort.name);
  for(const constant of claim.constants)target(sorts,constant.sort_ref,'formal-claim',claim.id,'constant:'+constant.name);
  for(const predicate of claim.predicates){
   const sort=target(sorts,predicate.sort_refs[0]!,'formal-claim',claim.id,'predicate:'+predicate.name);
   const definition=target(definitions,predicate.definition_ref,'formal-claim',claim.id,'predicate:'+predicate.name);
   if(definition.input.type_ref!==sort.type_ref)fail('BUSINESS_TYPE','formal-claim',claim.id,'predicate:'+predicate.name,'predicate sort and definition Entity differ');
  }
  for(const ref of claim.subject_refs)if(!rules.has(ref)&&!operations.has(ref))fail('BUSINESS_REFERENCE','formal-claim',claim.id,'subject:'+ref,'assurance subject must be a declared Rule or Operation');
  validateProposition(claim,(code,message)=>fail(code,'formal-claim',claim.id,'proposition',message));
 }
 const result=freezeBusinessData<ResolvedBusinessSpecV2>({kind:'resolved-business-spec-v2',data,source:parsed.source,executable_sha256:alchDirectExecutableDigestV2(data),assurance_sha256:alchOptionalAssuranceDigestV2(data)},source);
 resolvedRegistryV2.set(result,{parsed,fingerprint:businessHash(businessCanonical(result)),disposed:false});return result;
}
export function assertResolvedBusinessSpecV2Current(value:ResolvedBusinessSpecV2):void {
 const state=value&&typeof value==='object'?resolvedRegistryV2.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original successor resolved source required');
 if(state.disposed)businessReject('BUSINESS_DISPOSED',value.source.path,1,1,'successor source was disposed');
 assertParsedBusinessSourceV2Current(state.parsed);
 if(businessHash(businessCanonical(value))!==state.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',value.source.path,1,1,'successor source changed');
 state.physical?.();
}
export function disposeResolvedBusinessSpecV2(value:ResolvedBusinessSpecV2):void {
 const state=value&&typeof value==='object'?resolvedRegistryV2.get(value):undefined;
 if(!state)businessReject('BUSINESS_HANDLE','business.alch',1,1,'original successor resolved source required');
 if(state.disposed)businessReject('BUSINESS_DISPOSED',value.source.path,1,1,'successor source already disposed');
 state.disposed=true;
}
export function prepareBusinessSpecFileV2(root:string,relative:string):ResolvedBusinessSpecV2 {
 businessSourceKey(relative);
 if(typeof root!=='string'||!path.isAbsolute(root)||root.includes('\0')||root.split(path.sep).some(part=>part==='.'||part==='..'))businessReject('BUSINESS_SOURCE_PATH',relative,1,1,'absolute source root required');
 const absolute=path.resolve(root),capture=captureFile(absolute,relative),result=resolveBusinessSpecV2(parseBusinessSourceV2(capture.text,relative));
 resolvedRegistryV2.get(result)!.physical=()=>{
  let current:FileCapture;
  try{current=captureFile(absolute,relative);}catch(error){if(error instanceof BusinessSourceRejected&&error.code==='BUSINESS_SOURCE_SYMLINK')throw error;businessReject('BUSINESS_SOURCE_DRIFT',relative,1,1,'captured successor source is unavailable');}
  if(current.fingerprint!==capture.fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',relative,1,1,'captured successor bytes or path ownership changed');
 };
 assertResolvedBusinessSpecV2Current(result);return result;
}
export const BUSINESS_RESOLVER_OWNER_V2:BusinessResolverOwnerV2=Object.freeze({resolve:resolveBusinessSpecV2,prepareFile:prepareBusinessSpecFileV2,assertCurrent:assertResolvedBusinessSpecV2Current,dispose:disposeResolvedBusinessSpecV2});
export function resolveVersionedBusinessSpec(parsed:ParsedBusinessSource|ParsedBusinessSourceV2):ResolvedBusinessSpec|ResolvedBusinessSpecV2 {
 return parsed.kind==='parsed-business-source-v2'?resolveBusinessSpecV2(parsed):resolveBusinessSpec(parsed);
}
