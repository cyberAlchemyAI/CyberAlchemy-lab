import {genericClaimReference} from '../generic/assurance-source.js';
import {resolveGenericTransactionProfile,resolveGenericEventProfile,resolveGenericTransactionBounds,resolveGenericKeyedProfile} from '../generic/profile-resolver.js';
/** Original Core source custody, independent of all Alch handles and DTOs.
 * Captures declared source/assets only; creates no native/profile/decision owner.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,readlinkSync,realpathSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreParentIdentityDigestTrustedV1} from './commerce-core-parent-digest-v1.js';
import {CoreCommerceSourceError,coreFreeze,coreSha256,coreRelativePath,coreSourceFail as fail,coreSourceChildren as children,coreSourceDescendants as descendants,
 coreSourceTokens as tokens,coreSourceText as text,type CoreSourceRange} from './commerce-core-syntax.js';
import {reconstructCoreCommerceModule,reconstructCoreCommerceSources,type CoreCommerceReconstruction,type CoreCommerceModule} from './commerce-core-reconstruction.js';

export interface CoreCommerceSourceCapture {readonly kind:'original-core-commerce-source-capture/v1-candidate'}
export interface CoreCommerceCapturedFile {readonly path:string;readonly sha256:string;readonly bytes:number;readonly text:string}
export interface CoreCommerceSourceInspection {
 readonly kind:'core-commerce-source-inspection/v1-candidate';readonly capture_sha256:string;readonly capture_mode?:'keyed-query-entry'|'atomic-state-entry'|'external-read-entry'|'external-write-entry'|'event-handoff-entry';
 readonly application_path:string;readonly reconstruction:CoreCommerceReconstruction;
 readonly files:readonly CoreCommerceCapturedFile[];readonly authority_effect:'none';
}
export interface CoreCommerceSourceOwner {
 prepare(root:string,applicationPath?:string):CoreCommerceSourceCapture;
 inspect(capture:CoreCommerceSourceCapture):CoreCommerceSourceInspection;
 assertCurrent(capture:CoreCommerceSourceCapture):void;
 dispose(capture:CoreCommerceSourceCapture):void;
}
interface PhysicalFile {readonly data:CoreCommerceCapturedFile;readonly fingerprint:string;readonly identity:Readonly<{realRoot:string;resolved:string;binding:string;physicalParents:string;stamp:readonly string[]}>}
const location=(p:string):CoreSourceRange=>({path:p,start:0,end:0});
type ParentIdentity=Readonly<{path:string;device:string;inode:string;mode:string;link:string|null}>;
const parentIdentity=(file:string):ParentIdentity=>{const stat=lstatSync(file,{bigint:true});return {path:file,device:String(stat.dev),inode:String(stat.ino),mode:String(stat.mode),link:stat.isSymbolicLink()?readlinkSync(file):null};};
function parents(file:string,memo?:Map<string,ParentIdentity>):ParentIdentity[] {
 let cursor=path.parse(file).root;const out:ParentIdentity[]=[];
 for(const part of ['',...file.slice(cursor.length).split(path.sep)]){
  if(part)cursor=path.join(cursor,part);
  let identity=memo?.get(cursor);if(!identity){identity=parentIdentity(cursor);memo?.set(cursor,identity);}out.push(identity);
 }return out;
}
function assertParentsCurrent(memo:Map<string,ParentIdentity>):void {
 for(const [file,before] of memo){const now=parentIdentity(file);
  if(now.device!==before.device||now.inode!==before.inode||now.mode!==before.mode||now.link!==before.link)
   fail('StaleOwner',location(file),'source ancestor changed during currentness check');
 }
}
function directory(root:string):string {
 if(typeof root!=='string'||root.length>4096||!path.isAbsolute(root)||path.normalize(root)!==root||/[\\\u0000-\u001f\u007f]/.test(root))fail('InvalidContract',location(String(root).slice(0,4096)),'normalized absolute root required');
 const actual=realpathSync(root),st=lstatSync(actual);if(!st.isDirectory())fail('InvalidContract',location(root),'source root must be a directory');return actual;
}
const physicalStamp=(st:BigIntStats)=>[st.dev,st.ino,st.size,st.mode,st.mtimeNs,st.ctimeNs].map(String);
function assertOriginalIdentity(root:string,realRoot:string,file:PhysicalFile,memo:Map<string,ParentIdentity>):void {
 const relative=file.data.path,source=path.join(root,relative),identity=file.identity,lexicalParents=parents(source,memo);
 // The same phase already lstat-checked every component. A fully physical,
 // unchanged lexical path needs no second ancestor walk inside realpathSync.
 // Aliases (including hidden intermediate symlink chains) still resolve afresh.
 // The complete phase is followed by assertParentsCurrent; no cache survives it.
 const resolved=source===identity.resolved&&lexicalParents.every(parent=>parent.link===null)?source:realpathSync(source);
 if(realRoot!==identity.realRoot||resolved!==identity.resolved||coreParentIdentityDigestTrustedV1(lexicalParents)!==identity.binding||coreParentIdentityDigestTrustedV1(parents(resolved,memo))!==identity.physicalParents)fail('StaleOwner',location(relative),'captured source path changed');
 const stat=lstatSync(resolved,{bigint:true});if(!stat.isFile()||stat.size>1048576n||physicalStamp(stat).some((part,i)=>part!==identity.stamp[i]))fail('StaleOwner',location(relative),'captured source physical identity changed');
}
function readOriginal(root:string,relative:string):PhysicalFile {
 if(!coreRelativePath(relative))fail('InvalidContract',location(relative),'normalized relative captured file required');
 const realRoot=directory(root),file=path.join(root,relative),resolved=realpathSync(file);
 if(resolved!==realRoot&&!resolved.startsWith(realRoot+path.sep))fail('InvalidContract',location(relative),'captured path escapes original root');
 const binding=parents(file),physicalParents=parents(resolved),before=lstatSync(resolved,{bigint:true});
 const stamp=physicalStamp;
 if(!before.isFile()||before.size>1048576n)fail('ResourceLimit',location(relative),'bounded regular original file required');
 const fd=openSync(resolved,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),parts:Buffer[]=[];let bytes=0;
 try{
  if(dataDigest(stamp(fstatSync(fd,{bigint:true})))!==dataDigest(stamp(before)))fail('StaleOwner',location(relative),'file changed while opening');
  for(;;){const b=Buffer.alloc(65536),n=readSync(fd,b,0,b.length,null);if(!n)break;bytes+=n;if(bytes>1048576)fail('ResourceLimit',location(relative),'file read bound');parts.push(b.subarray(0,n));}
  if(dataDigest(stamp(fstatSync(fd,{bigint:true})))!==dataDigest(stamp(before)))fail('StaleOwner',location(relative),'file changed during capture');
 }finally{closeSync(fd);}
 if(directory(root)!==realRoot||realpathSync(file)!==resolved||coreParentIdentityDigestTrustedV1(parents(file))!==coreParentIdentityDigestTrustedV1(binding)||coreParentIdentityDigestTrustedV1(parents(resolved))!==coreParentIdentityDigestTrustedV1(physicalParents)||dataDigest(stamp(lstatSync(resolved,{bigint:true})))!==dataDigest(stamp(before))||bytes!==Number(before.size))fail('StaleOwner',location(relative),'source/root/path ownership changed during capture');
 const buffer=Buffer.concat(parts);let text:string;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(buffer);}catch{return fail('Syntax',location(relative),'strict original UTF-8 required');}
 const data=coreFreeze({path:relative,sha256:coreSha256(buffer),bytes,text});
 return {data,fingerprint:dataDigest({root,realRoot,resolved,binding,physicalParents,stamp:stamp(before),sha256:data.sha256}),identity:{realRoot,resolved,binding:coreParentIdentityDigestTrustedV1(binding),physicalParents:coreParentIdentityDigestTrustedV1(physicalParents),stamp:stamp(before)}};
}
/** Closed duplicate-aware bounded JSON. Identity/config data cannot be a handle. */
export function parseCoreCommerceJson(text:string,file:string):unknown {
 const at=location(file);if(Buffer.byteLength(text)>1048576)fail('ResourceLimit',at,'JSON byte limit');let position=0,nodes=0;
 const ws=()=>{while(/[ \n\r\t]/.test(text[position]??'x'))position++;};
 const string=():string=>{
  const start=position++;while(position<text.length&&text[position]!=='"'){if(text[position]==='\\')position++;position++;}
  if(text[position++]!=='"')fail('Syntax',at,'unterminated JSON string');let s:string;
  try{s=JSON.parse(text.slice(start,position)) as string;}catch{return fail('Syntax',at,'invalid JSON string');}
  if(Buffer.from(s).toString('utf8')!==s)fail('Syntax',at,'JSON requires Unicode scalars');return s;
 };
 const value=(depth:number):unknown=>{
  if(depth>64||++nodes>100000)fail('ResourceLimit',at,'JSON nesting/node limit');ws();const c=text[position];
  if(c==='"')return string();
  if(c==='{'){
   position++;ws();const out:Record<string,unknown>=Object.create(null),keys=new Set<string>();if(text[position]==='}'){position++;return out;}
   for(;;){ws();if(text[position]!=='"')fail('Syntax',at,'JSON key expected');const key=string();if(keys.has(key))fail('InvalidContract',at,'duplicate decoded JSON key');keys.add(key);ws();if(text[position++]!==':')fail('Syntax',at,'JSON colon expected');out[key]=value(depth+1);ws();const sep=text[position++];if(sep==='}')return out;if(sep!==',')fail('Syntax',at,'JSON object separator expected');}
  }
  if(c==='['){position++;ws();const out:unknown[]=[];if(text[position]===']'){position++;return out;}for(;;){out.push(value(depth+1));ws();const sep=text[position++];if(sep===']')return out;if(sep!==',')fail('Syntax',at,'JSON array separator expected');}}
  for(const [token,v] of [['true',true],['false',false],['null',null]]as const)if(text.startsWith(token,position)){position+=token.length;return v;}
  const match=/-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/y;match.lastIndex=position;const m=match.exec(text);if(!m)fail('Syntax',at,'invalid JSON value');position=match.lastIndex;const n=Number(m[0]);if(!Number.isSafeInteger(n))fail('InvalidContract',at,'metadata numbers must be safe integers');return n;
 };
 const result=value(0);ws();if(position!==text.length)fail('Syntax',at,'trailing JSON');return coreFreeze(result);
}
function pointer(value:unknown,fragment:string,where:CoreSourceRange):void {
 if(!fragment)return;if(!fragment.startsWith('/'))fail('InvalidContract',where,'JSON pointer must begin with slash');let current=value;
 for(const raw of fragment.slice(1).split('/')){if(/~(?![01])/.test(raw))fail('InvalidContract',where,'invalid JSON pointer escape');const key=raw.replace(/~1/g,'/').replace(/~0/g,'~');if(Array.isArray(current)&&!/^(0|[1-9][0-9]*)$/.test(key))fail('UnknownReference',where,'noncanonical array pointer');if(!current||typeof current!=='object'||!Object.hasOwn(current,key))fail('UnknownReference',where,'captured JSON pointer is absent');current=(current as Record<string,unknown>)[key];}
}
function referencedFile(modulePath:string,reference:string):{path:string;fragment:string}|null {
 const hash=reference.indexOf('#'),file=hash<0?reference:reference.slice(0,hash),fragment=hash<0?'':reference.slice(hash+1);
 // URIs/registered ABI references are not filesystem paths. Only explicit local
 // supported file extensions enter capture; every caller retains its source span.
 if(!/\.(?:alch|json|lean|smt2|als|tla|dl)$/.test(file))return null;
 const relative=file.includes('/')?file:path.posix.join(path.posix.dirname(modulePath),file);
 if(!coreRelativePath(relative))fail('InvalidContract',location(reference),'source reference must remain a normalized relative file');return {path:relative,fragment};
}
// Bind source implementations at module load; a later code replacement requires
// a fresh owning process, rather than silently inheriting its old private owners.
const ownFile=fileURLToPath(import.meta.url),extension=path.extname(ownFile),codeRoot=path.dirname(ownFile);
const codeNames=['commerce-core-source-owner','commerce-core-syntax','commerce-core-reconstruction','commerce-core-grammar','commerce-core-parent-digest-v1'];
const codeEpoch=()=>dataDigest([...codeNames.map(name=>readOriginal(codeRoot,name+extension).fingerprint),readOriginal(path.dirname(codeRoot),'profile-engine/contracts'+extension).fingerprint]);
const loadedCodeEpoch=codeEpoch();
const codePin=pinCoreImplementation(import.meta.url,['commerce-core-syntax'+extension,'commerce-core-reconstruction'+extension,'commerce-core-grammar'+extension,'commerce-core-parent-digest-v1'+extension,'../profile-engine/contracts'+extension]);
const ownerRegistry=new WeakSet<object>();
export function assertCoreCommerceSourceOwner(owner:CoreCommerceSourceOwner):void {if(!owner||typeof owner!=='object'||!ownerRegistry.has(owner))fail('ForeignOwner',location('application.alch'),'original Core source owner factory instance required');}
export function createCoreCommerceSourceOwner(captureMode:'legacy'|'keyed-query-entry'|'atomic-state-entry'|'external-read-entry'|'external-write-entry'|'event-handoff-entry'='legacy'):CoreCommerceSourceOwner {
 if(captureMode!=='legacy'&&captureMode!=='keyed-query-entry'&&captureMode!=='atomic-state-entry'&&captureMode!=='external-read-entry'&&captureMode!=='external-write-entry'&&captureMode!=='event-handoff-entry')fail('InvalidContract',location('source-mode'),'exact source capture mode required');
 const keyedNames=['profile-resolver','composition-capabilities',...((captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry')?['assurance-source','transaction-data-v1']:[]),...((captureMode==='external-write-entry'||captureMode==='event-handoff-entry')?['external-write-source','external-write-profile','external-write-data-v1','external-write-identity']:[]),...(captureMode==='event-handoff-entry'?['event-data-v1','event-handoff-source']:[])];
 const keyedCode=()=>captureMode!=='legacy'?dataDigest(keyedNames.map(n=>readOriginal(path.dirname(codeRoot),'generic/'+n+extension).fingerprint)):null,keyedEpoch=keyedCode(),keyedPin=captureMode==='legacy'?null:pinCoreImplementation(import.meta.url,keyedNames.map(n=>'../generic/'+n+extension));
 const owned=new WeakMap<object,{root:string;rootBinding:string;files:readonly PhysicalFile[];inspection:CoreCommerceSourceInspection;disposed:boolean}>();
 const current=(capture:CoreCommerceSourceCapture):void=>{
  const state=capture&&typeof capture==='object'?owned.get(capture):undefined;if(!state)fail('ForeignOwner',location('application.alch'),'original capture from this exact Core owner required');if(state.disposed)fail('DisposedOwner',location('application.alch'),'Core source capture disposed');
  try{
   codePin.assertCurrent();keyedPin?.assertCurrent();const parentMemo=new Map<string,ParentIdentity>();
   if(coreParentIdentityDigestTrustedV1(parents(state.root,parentMemo))!==state.rootBinding)fail('StaleOwner',location(state.inspection.application_path),'original Core implementation/root changed');
   const realRoot=directory(state.root);
   for(const file of state.files)assertOriginalIdentity(state.root,realRoot,file,parentMemo);
   assertParentsCurrent(parentMemo);
  }catch(error){if(error instanceof CoreCommerceSourceError&&error.diagnostics[0]?.code==='StaleOwner')throw error;fail('StaleOwner',location(state.inspection.application_path),'original file/path/implementation unavailable or changed');}
 };
 const owner:CoreCommerceSourceOwner=Object.freeze({prepare(root:string,applicationPath='application.alch'){
  try{
  directory(root);codePin.assertCurrent();
  const rootBinding=coreParentIdentityDigestTrustedV1(parents(root)),files=new Map<string,PhysicalFile>(),modules:CoreCommerceModule[]=[];let bytes=0;
  const read=(file:string)=>{let f=files.get(file);if(!f){if((captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry')&&realpathSync(path.join(root,file))!==path.join(root,file))fail('InvalidContract',location(file),'atomic capture requires physical unaliased files');f=readOriginal(root,file);bytes+=f.data.bytes;if(files.size>=128||bytes>4194304)fail('ResourceLimit',location(file),'source closure bound');files.set(file,f);}return f.data;};
  const application=reconstructCoreCommerceModule(read(applicationPath).text,applicationPath);modules.push(application);
  const applications=application.declarations.filter(d=>d.interface_kind==='application-composition');if(applications.length!==1)fail('InvalidContract',application.syntax,'one root application composition required');
  const paths:string[]=[];for(const c of descendants(applications[0]!.syntax,'application-clause')){const ts=tokens(c).filter(t=>!t.layout);if(ts[0]?.token==='source')paths.push(text(children(c,'reference')[0]!));}
  if(new Set(paths).size!==paths.length||paths.includes(applicationPath))fail('DuplicateSymbol',application.syntax,'source closure repeats a module path');
  if(paths.length>=((captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry')?34:32))fail('ResourceLimit',application.syntax,'module count');
  for(const p of paths){if(!p.endsWith('.alch'))fail('InvalidContract',location(p),'declared module source must be .alch');modules.push(reconstructCoreCommerceModule(read(p).text,p));}
  const jsons=new Map<string,unknown>();
  const parameterClause=captureMode==='event-handoff-entry'?descendants(application.syntax,'interface-clause').find(n=>tokens(n).filter(t=>!t.layout)[0]?.token==='parameters'):undefined;
  const parameterReference=parameterClause&&descendants(parameterClause,'reference')[0];
  const parameterFile=parameterReference&&referencedFile(applicationPath,text(parameterReference));
  const eventSelection=captureMode==='event-handoff-entry'&&parameterFile&&!parameterFile.fragment?parseCoreCommerceJson(read(parameterFile.path).text,parameterFile.path) as {capabilities?:unknown}:undefined;
  const eventCaps=Array.isArray(eventSelection?.capabilities)?eventSelection.capabilities:[];
  const captureExternal=captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry'&&eventCaps.includes('external-read-preflight');
  const captureWrite=captureMode==='external-write-entry'||captureMode==='event-handoff-entry'&&eventCaps.includes('external-write-preflight');
  if(captureExternal){
   const generation=read('contracts/external-generation.json'),value=parseCoreCommerceJson(generation.text,generation.path) as any;
   const required=['schema_version','bindings','calls','files','recipes','authored_paths','template_manifest'];
   if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).sort().join(',')!==required.sort().join(',')||value.schema_version!=='craft.generic-external-generation/v1-candidate'||!Array.isArray(value.files)||value.files.length>96||!Array.isArray(value.bindings)||value.bindings.length>16||!Array.isArray(value.calls)||!Array.isArray(value.recipes)||!Array.isArray(value.authored_paths)||typeof value.template_manifest!=='string')fail('InvalidContract',application.syntax,'closed captured external generation inventory required');
   jsons.set(generation.path,value);const seen=new Set<string>();
   for(const row of value.files){
    if(!row||typeof row!=='object'||Object.keys(row).sort().join(',')!=='bytes,path,sha256'||typeof row.path!=='string'||!coreRelativePath(row.path)||seen.has(row.path)||row.path===generation.path||!row.path.startsWith('generated/external-')&&!row.path.startsWith('contracts/external-'))fail('InvalidContract',application.syntax,'unique reserved external generated asset required');
    seen.add(row.path);const actual=read(row.path);if(actual.sha256!==row.sha256||actual.bytes!==row.bytes)fail('InvalidContract',application.syntax,'actual external generated asset identity differs');
    if(row.path.endsWith('.json'))jsons.set(row.path,parseCoreCommerceJson(actual.text,row.path));
    else if(row.path.endsWith('.alch')&&!modules.some(m=>m.path===row.path))fail('MissingMapping',application.syntax,'generated technical module omitted from root');
   }
   if(!seen.has(value.template_manifest)||!seen.has('contracts/external-composition.json'))fail('MissingMapping',application.syntax,'actual external template/composition closure required');
  }
  if(captureWrite){const selected=read('contracts/external-write-bindings.json');jsons.set(selected.path,parseCoreCommerceJson(selected.text,selected.path));}
  if(captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry'){const b=read('contracts/transactions.json');jsons.set(b.path,resolveGenericTransactionBounds(b.text,b.path));for(const m of modules)for(const d of m.declarations)if(d.surface==='FormalClaim'){const ref=genericClaimReference(d,m.path);const a=read(ref.path);if(a.bytes>262144)fail('ResourceLimit',d.syntax,'opaque claim asset byte bound');}}
  for(const m of modules)for(const node of descendants(m.syntax,'reference')){
   const ref=referencedFile(m.path,text(node));if(!ref){const abi=descendants(m.syntax,'interface-clause').some(c=>tokens(c).filter(t=>!t.layout)[0]?.token==='abi'&&descendants(c,'reference').some(r=>r.start===node.start&&r.end===node.end));if((captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'||captureMode==='event-handoff-entry')&&!abi)fail('InvalidContract',node,'atomic source reference must name a supported captured asset or an actual ABI clause');continue;}
   if(ref.path.endsWith('.alch')){if(!modules.some(m=>m.path===ref.path))fail('UnknownReference',node,'module not in declared application source closure');continue;}
   const data=read(ref.path);if(ref.path.endsWith('.json')){if(!jsons.has(ref.path))jsons.set(ref.path,parseCoreCommerceJson(data.text,ref.path));pointer(jsons.get(ref.path),ref.fragment,node);}else if(ref.fragment)fail('InvalidContract',node,'only JSON files have contract pointers');
  }
  const object=(value:unknown,where:CoreSourceRange):Record<string,unknown>=>{if(!value||typeof value!=='object'||Array.isArray(value))fail('InvalidContract',where,'identity object required');return value as Record<string,unknown>;};
  for(const c of descendants(applications[0]!.syntax,'application-clause'))if(tokens(c).filter(t=>!t.layout)[0]?.token==='source-identities'){
   const ref=referencedFile(applicationPath,text(children(c,'reference')[0]!));if(!ref)fail('InvalidContract',c,'source identity contract must be a captured file');
   const manifest=object(jsons.get(ref.path),c);
   if(manifest.schema_version!=='craft.commerce-source-contract-identities/v1-candidate'||manifest.root!==applicationPath||manifest.application!==applications[0]!.id||!Array.isArray(manifest.modules)||!Array.isArray(manifest.contract_assets))fail('InvalidContract',c,'exact source identity contract/application required');
   const seenModules=new Set<string>(),seenAssets=new Set<string>();
   for(const raw of manifest.modules){const row=object(raw,c),artifact=object(row.artifact,c);if(typeof artifact.path!=='string'||seenModules.has(artifact.path))fail('DuplicateSymbol',c,'unique source identity path required');seenModules.add(artifact.path);const m=modules.find(m=>m.path===artifact.path);if(!m||m.module!==row.module||row.version!==1||m.sha256!==artifact.sha256||m.bytes!==artifact.bytes)fail('StaleOwner',c,'identity metadata differs from actual captured module');}
   if(seenModules.size!==modules.length)fail('MissingMapping',c,'identity metadata omits a declared source');
   for(const raw of manifest.contract_assets){const row=object(raw,c);if(typeof row.path!=='string'||seenAssets.has(row.path)||!row.path.endsWith('.json')||row.path===ref.path)fail('InvalidContract',c,'unique JSON asset identity required');seenAssets.add(row.path);const actual=read(row.path);if(actual.sha256!==row.sha256||actual.bytes!==row.bytes)fail('StaleOwner',c,'identity metadata differs from actual contract');if(!jsons.has(row.path))jsons.set(row.path,parseCoreCommerceJson(actual.text,row.path));}
   for(const p of jsons.keys())if(p!==ref.path&&!seenAssets.has(p))fail('MissingMapping',c,'identity metadata omits a referenced contract');
  }
  if(captureMode!=='legacy'){
   const asset=(head:string)=>{const clauses=descendants(applications[0]!.syntax,'interface-clause').filter(n=>tokens(n).filter(t=>!t.layout)[0]?.token===head);if(clauses.length!==1)fail('MissingMapping',application.syntax,'keyed capture requires actual '+head);const reference=descendants(clauses[0]!,'reference')[0],ref=reference&&referencedFile(applicationPath,text(reference));if(!ref||ref.fragment)fail('InvalidContract',application.syntax,'keyed selection requires full captured JSON file');return read(ref.path);};
   const profile=asset('parameters'),bounds=asset('computation-bounds'),raw=parseCoreCommerceJson(bounds.text,bounds.path) as any;
   if(raw?.schema_version!=='craft.generic-compute-bounds/v1-candidate'||raw.computation?.required_schema_version!=='craft.generic-computation/v1-candidate'||raw.computation?.required_semantics_revision!=='ordered-metered-generic-v1-candidate')fail('InvalidContract',application.syntax,'keyed source bounds discriminator required');
   if(captureMode==='event-handoff-entry'){const tx=read('contracts/transactions.json');resolveGenericEventProfile(profile.text,profile.path,raw.computation.limits,resolveGenericTransactionBounds(tx.text,tx.path));}else if(captureMode==='atomic-state-entry'||captureMode==='external-read-entry'||captureMode==='external-write-entry'){const tx=read('contracts/transactions.json');resolveGenericTransactionProfile(profile.text,profile.path,raw.computation.limits,resolveGenericTransactionBounds(tx.text,tx.path));}else resolveGenericKeyedProfile(profile.text,profile.path,raw.computation.limits);
  }
  // Reparse captured text through Core reconstruction. No frontend object, label,
  // digest or caller-supplied owner participates in this boundary.
  const reconstruction=reconstructCoreCommerceSources(modules.map(m=>({path:m.path,text:read(m.path).text})),captureMode),captured=[...files.values()].sort((a,b)=>a.data.path<b.data.path?-1:1);
  const inspection=coreFreeze({kind:'core-commerce-source-inspection/v1-candidate' as const,...(captureMode!=='legacy'?{capture_mode:captureMode}:{}),capture_sha256:dataDigest({...(captureMode!=='legacy'?{capture_mode:captureMode,keyed_code:keyedEpoch}:{}),root,rootBinding,files:captured.map(f=>({path:f.data.path,fingerprint:f.fingerprint})),code:loadedCodeEpoch}),application_path:applicationPath,reconstruction,files:captured.map(f=>f.data),authority_effect:'none' as const});
  const handle=Object.freeze({kind:'original-core-commerce-source-capture/v1-candidate' as const});owned.set(handle,{root,rootBinding,files:captured,inspection,disposed:false});current(handle);return handle;
  }catch(error){if(error instanceof CoreCommerceSourceError)throw error;fail('UnknownReference',location(applicationPath),'declared original source/root/contract file unavailable');}
 },inspect(capture:CoreCommerceSourceCapture){current(capture);return owned.get(capture)!.inspection;},assertCurrent:current,dispose(capture:CoreCommerceSourceCapture){current(capture);owned.get(capture)!.disposed=true;}});
 ownerRegistry.add(owner);return owner;
}
