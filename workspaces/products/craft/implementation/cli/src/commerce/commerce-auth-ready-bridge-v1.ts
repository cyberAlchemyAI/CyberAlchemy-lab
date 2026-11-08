/** Fixed original native build and bounded owned-pipe completion registry.
 * Projections are data; only this factory mints completion/database handles.
 * Open Questions: docs/COMMERCE-AUTH-READY-BRIDGE-V1.md#open-questions. */
import {assertGenericSelectedAuthAsset,type GenericSelectedAuthAsset} from '../generic/auth-asset.js';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawn,execFile,type ChildProcessWithoutNullStreams} from 'node:child_process';
import {promisify} from 'node:util';
import {constants,openSync,closeSync,fstatSync,lstatSync,readSync,readFileSync,mkdirSync,mkdtempSync,copyFileSync,chmodSync,readdirSync,realpathSync,writeFileSync,type BigIntStats} from 'node:fs';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';

export const COMMERCE_AUTH_READY_ABI_V1='craft.commerce-auth-ready-bridge/v1-candidate';
const ext=path.extname(fileURLToPath(import.meta.url));
const code=pinCoreImplementation(import.meta.url,['commerce-core-physical'+ext,'commerce-core-syntax'+ext,'../profile-engine/contracts'+ext]);
const repository=fileURLToPath(new URL('../'.repeat(7),import.meta.url));
const launcher=path.join(repository,'tools/toolchain/run');
const crate=path.join(repository,'auth-foundation/implementation/commerce-auth-ready-bridge-v1');
const runFile=promisify(execFile),INPUT=4096,OUTPUT=8192,ACTIVE=4,QUEUED=64,WAIT=2000;
export type AuthBridgeCodeV1='ForeignOwner'|'DisposedOwner'|'StaleOwner'|'InvalidRequest'|'MalformedResponse'|'NativeUnavailable'|'QueueFull'|'BridgeTimeout'|'Cancelled';
export class CommerceAuthBridgeErrorV1 extends Error {constructor(readonly code:AuthBridgeCodeV1){super(code);this.name='CommerceAuthBridgeErrorV1';}}
function bad(code:AuthBridgeCodeV1):never {throw new CommerceAuthBridgeErrorV1(code);}
export interface AuthPermissionV1 {readonly resource:string;readonly action:string;readonly scope:string}
export interface AuthInvocationBindingV1 {
 readonly invocation_id:string;readonly logical_entry_id:string;readonly bound_operation_id:string;
 readonly canonical_input_sha256:string;readonly checked_source_sha256:string;readonly profile_config_sha256:string;readonly native_basis_sha256:string;
 readonly actor_owner_identity:string;readonly causal_owner_identity:string|null;readonly target_service_id:string;readonly store_or_event_epoch:string;
}
export interface AuthBridgeRequestV1 {readonly abi:typeof COMMERCE_AUTH_READY_ABI_V1;readonly request:{readonly request_id:string;readonly authentication_evidence_ref:string;readonly route_id:string};readonly binding:AuthInvocationBindingV1;readonly expected_permission:AuthPermissionV1}
export interface AuthReadyProjectionV1 {
 readonly request_id:string;readonly authenticated_subject_id:string;readonly session_id:string;readonly required_permission:AuthPermissionV1;readonly scope_evidence_ref:string;
 readonly authentication_evidence_revision:string;readonly route_binding_revision:string;readonly current_authorization_revision:string;
 readonly evaluation_epoch_id:string;readonly decision_time:string;readonly policy_snapshot_sha256:string;
}
export interface AuthBridgeResponseV1 {readonly abi:typeof COMMERCE_AUTH_READY_ABI_V1;readonly request_id:string;readonly binding:AuthInvocationBindingV1;readonly outcome:'allow'|'deny'|'unavailable';readonly ready:AuthReadyProjectionV1|null}
export interface CommerceAuthCompletionV1 {readonly kind:'original-commerce-auth-pipe-completion/v1-candidate'}
export interface CommerceAuthFixtureDatabaseV1 {readonly kind:'original-commerce-auth-fixture-database/v1-candidate'}
type FilePin={path:string;sha256:string;bytes:number;physical:string;parents:readonly string[]};
// The initial capture hashes every byte. A file's ctime cannot be restored by
// an ordinary writer, so currentness can subsequently compare its anchored
// physical identity without rereading the entire native toolchain on every
// nested invocation check.
const sameParents=(a:readonly string[],b:readonly string[])=>a.length===b.length&&a.every((p,i)=>p===b[i]);
const samePin=(a:FilePin,b:FilePin)=>a.path===b.path&&a.sha256===b.sha256&&a.bytes===b.bytes&&a.physical===b.physical&&sameParents(a.parents,b.parents);
const stamp=(s:BigIntStats)=>[s.dev,s.ino,s.size,s.mode,s.mtimeNs,s.ctimeNs].map(String).join(':');
function parents(file:string):string[]{
 const directory=path.dirname(file),parts=directory.split(path.sep).filter(Boolean);let current=path.parse(file).root;const rows:string[]=[];
 for(const part of ['',...parts]){if(part)current=path.join(current,part);const s=lstatSync(current,{bigint:true});if(!s.isDirectory()||s.isSymbolicLink())bad('StaleOwner');rows.push(current+':'+s.dev+':'+s.ino);}return rows;
}
function pinFile(file:string):FilePin {
 if(!path.isAbsolute(file)||path.normalize(file)!==file)bad('StaleOwner');
 const ps=parents(file),before=lstatSync(file,{bigint:true});if(!before.isFile()||before.isSymbolicLink()||before.size>1073741824n)bad('StaleOwner');
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),hash=createHash('sha256');
 try{if(stamp(fstatSync(fd,{bigint:true}))!==stamp(before))bad('StaleOwner');const block=Buffer.alloc(65536);for(;;){const n=readSync(fd,block,0,block.length,null);if(!n)break;hash.update(block.subarray(0,n));}if(stamp(fstatSync(fd,{bigint:true}))!==stamp(before))bad('StaleOwner');}finally{closeSync(fd);}
 if(stamp(lstatSync(file,{bigint:true}))!==stamp(before)||!sameParents(parents(file),ps))bad('StaleOwner');
 return {path:file,sha256:hash.digest('hex'),bytes:Number(before.size),physical:stamp(before),parents:ps};
}
function assertPinnedFileIdentityCurrent(p:FilePin):void {
 if(!path.isAbsolute(p.path)||path.normalize(p.path)!==p.path)bad('StaleOwner');
 const before=lstatSync(p.path,{bigint:true});
 if(!before.isFile()||before.isSymbolicLink()||Number(before.size)!==p.bytes||stamp(before)!==p.physical)bad('StaleOwner');
 const fd=openSync(p.path,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
 try{if(stamp(fstatSync(fd,{bigint:true}))!==p.physical)bad('StaleOwner');}finally{closeSync(fd);}
 if(stamp(lstatSync(p.path,{bigint:true}))!==p.physical)bad('StaleOwner');
}
/** Check shared parent paths once on each side of the complete file pass.
 * Files still retain their original open/fstat/lstat identity checks; this
 * removes repeated walks of the same ancestors across native source pins. */
function assertPinnedFilesCurrent(files:readonly FilePin[]):void {
 const directories=new Map<string,FilePin>();
 for(const pin of files){const directory=path.dirname(pin.path),prior=directories.get(directory);
  if(prior&&!sameParents(prior.parents,pin.parents))bad('StaleOwner');
  if(!prior)directories.set(directory,pin);
 }
 const checkParents=()=>{for(const pin of directories.values())if(!sameParents(parents(pin.path),pin.parents))bad('StaleOwner');};
 checkParents();for(const pin of files)assertPinnedFileIdentityCurrent(pin);checkParents();
}
const id=(s:unknown):s is string=>typeof s==='string'&&s.length>0&&Buffer.byteLength(s)<=256&&!/\p{Cc}/u.test(s)&&Buffer.from(s).toString('utf8')===s;
const digest=(s:unknown):s is string=>typeof s==='string'&&/^[0-9a-f]{64}$/.test(s);
function closed(v:any,names:readonly string[],code:AuthBridgeCodeV1):void {if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==names.length||names.some(k=>!Object.hasOwn(v,k)))bad(code);}
function permission(v:any,code:AuthBridgeCodeV1):void {closed(v,['resource','action','scope'],code);if(![v.resource,v.action,v.scope].every(id))bad(code);}
function binding(v:any,code:AuthBridgeCodeV1):void {
 closed(v,['invocation_id','logical_entry_id','bound_operation_id','canonical_input_sha256','checked_source_sha256','profile_config_sha256','native_basis_sha256','actor_owner_identity','causal_owner_identity','target_service_id','store_or_event_epoch'],code);
 if(![v.invocation_id,v.logical_entry_id,v.bound_operation_id,v.actor_owner_identity,v.target_service_id,v.store_or_event_epoch].every(id)||v.causal_owner_identity!==null&&!id(v.causal_owner_identity)||![v.canonical_input_sha256,v.checked_source_sha256,v.profile_config_sha256,v.native_basis_sha256].every(digest))bad(code);
}
export function captureCommerceAuthRequestV1(proposal:AuthBridgeRequestV1):AuthBridgeRequestV1 {
 let r:any;try{r=captureJson(proposal);}catch{return bad('InvalidRequest');}
 closed(r,['abi','request','binding','expected_permission'],'InvalidRequest');closed(r.request,['request_id','authentication_evidence_ref','route_id'],'InvalidRequest');
 binding(r.binding,'InvalidRequest');permission(r.expected_permission,'InvalidRequest');
 if(r.abi!==COMMERCE_AUTH_READY_ABI_V1||![r.request.request_id,r.request.authentication_evidence_ref,r.request.route_id].every(id)||r.request.route_id!=='commerce:'+r.binding.logical_entry_id||Buffer.byteLength(JSON.stringify(r))>INPUT)bad('InvalidRequest');return r;
}
/** Closed-frame codec only. Its returned DTO cannot mint a completion/context. */
export function checkCommerceAuthResponseV1(bytes:Uint8Array,expected:AuthBridgeRequestV1):AuthBridgeResponseV1 {
 const request=captureCommerceAuthRequestV1(expected);if(!(bytes instanceof Uint8Array)||bytes.byteLength>OUTPUT)bad('MalformedResponse');
 let text:string,r:any;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);r=JSON.parse(text);if(JSON.stringify(r)!==text)bad('MalformedResponse');}catch{return bad('MalformedResponse');}
 closed(r,['abi','request_id','binding','outcome','ready'],'MalformedResponse');binding(r.binding,'MalformedResponse');
 if(r.abi!==COMMERCE_AUTH_READY_ABI_V1||r.request_id!==request.request.request_id||dataDigest(r.binding)!==dataDigest(request.binding)||!['allow','deny','unavailable'].includes(r.outcome))bad('MalformedResponse');
 if(r.outcome==='allow'){
  const p=r.ready;closed(p,['request_id','authenticated_subject_id','session_id','required_permission','scope_evidence_ref','authentication_evidence_revision','route_binding_revision','current_authorization_revision','evaluation_epoch_id','decision_time','policy_snapshot_sha256'],'MalformedResponse');permission(p.required_permission,'MalformedResponse');
  if(p.request_id!==r.request_id||![p.authenticated_subject_id,p.session_id,p.scope_evidence_ref].every(id)||dataDigest(p.required_permission)!==dataDigest(request.expected_permission)||!digest(p.policy_snapshot_sha256))bad('MalformedResponse');
  for(const n of [p.authentication_evidence_revision,p.route_binding_revision,p.current_authorization_revision,p.evaluation_epoch_id,p.decision_time])if(typeof n!=='string'||! /^(0|[1-9][0-9]{0,19})$/.test(n)||BigInt(n)>18446744073709551615n)bad('MalformedResponse');
  if(p.evaluation_epoch_id==='0')bad('MalformedResponse');
 }else if(r.ready!==null)bad('MalformedResponse');
 return coreFreeze(r);
}
type Database={directory:string;file:string;directoryIdentity:string;identity:string|null};
type Job={database:Database;request:AuthBridgeRequestV1;signal:AbortSignal|undefined;resolve:(h:CommerceAuthCompletionV1)=>void;reject:(e:Error)=>void;child:ChildProcessWithoutNullStreams|null;failed:boolean;done:boolean;deadline:number;timer:ReturnType<typeof setTimeout>;hard:ReturnType<typeof setTimeout>|null;settled:Promise<void>;settle:()=>void;abort:()=>void};
type Completion={database:Database;request:AuthBridgeRequestV1;response:AuthBridgeResponseV1};
type NativeState={directory:string;binary:FilePin;files:readonly FilePin[];manifest:Readonly<Record<string,unknown>>;disposed:boolean;disposal:Promise<void>|null;databases:WeakMap<object,Database>;completions:WeakMap<object,Completion>;active:Set<Job>;queue:Job[];current:()=>void;pump:()=>void};
const owners=new WeakMap<object,NativeState>();
export interface CommerceAuthNativeOwnerV1 {
 readonly kind:'original-commerce-auth-native-owner/v1-candidate';
 execute(database:CommerceAuthFixtureDatabaseV1,request:AuthBridgeRequestV1,signal?:AbortSignal):Promise<CommerceAuthCompletionV1>;
 inspectCompletion(completion:CommerceAuthCompletionV1):Readonly<{request:AuthBridgeRequestV1;response:AuthBridgeResponseV1;qualification:string;authority_effect:'none'}>;
 assertCompletionDatabase(completion:CommerceAuthCompletionV1,database:CommerceAuthFixtureDatabaseV1):void;
 inspect():Readonly<Record<string,unknown>>;inspectWork():Readonly<{active:number;queued:number;unsettled:number}>;
 assertCurrent():void;dispose():Promise<void>;
}
const native=(owner:CommerceAuthNativeOwnerV1):NativeState=>{const r=owner&&typeof owner==='object'?owners.get(owner):undefined;if(!r)bad('ForeignOwner');return r;};
export function assertCommerceAuthNativeOwnerV1(owner:CommerceAuthNativeOwnerV1):void {native(owner).current();}
function databaseCurrent(s:NativeState,h:CommerceAuthFixtureDatabaseV1):Database {
 const d=h&&typeof h==='object'?s.databases.get(h):undefined;if(!d||d.identity===null)bad('ForeignOwner');
 databaseRecordCurrent(d);return d;
}
function databaseRecordCurrent(d:Database):void {
 try{
 const directory=lstatSync(d.directory,{bigint:true}),f=lstatSync(d.file,{bigint:true});
 if(directory.isSymbolicLink()||!directory.isDirectory()||[directory.dev,directory.ino,directory.mode].join(':')!==d.directoryIdentity||f.isSymbolicLink()||!f.isFile()||[f.dev,f.ino,f.mode].join(':')!==d.identity)bad('StaleOwner');
 }catch{return bad('StaleOwner');}
}
/** Explicit developer producer, never a missing-artifact execution fallback.
 * Compiler, manifest, flags, environment and native program are fixed here. */
export async function produceCommerceAuthNativeOwnerV1(directory:string):Promise<CommerceAuthNativeOwnerV1> {
 code.assertCurrent();if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)bad('InvalidRequest');
 parents(directory);mkdirSync(directory,{mode:0o700});
 const env:NodeJS.ProcessEnv={PATH:process.env.PATH??'/usr/bin:/bin',HOME:process.env.HOME??'',LANG:'C.UTF-8'};
 const call=async(command:string,args:string[])=>{const r=await runFile(command,args,{cwd:repository,env,encoding:'utf8',maxBuffer:33554432});return r.stdout;};
 const manifest=path.join(crate,'Cargo.toml'),target=path.join(directory,'target');
 const metadata=JSON.parse(await call(launcher,['cargo','metadata','--offline','--locked','--format-version','1','--manifest-path',manifest]));
 const members=new Set<string>(),add=(p:string)=>members.add(realpathSync(p));
 const walk=(root:string)=>{for(const e of readdirSync(root,{withFileTypes:true})){if(e.isSymbolicLink()||['target','.git','node_modules'].includes(e.name))continue;const f=path.join(root,e.name);if(e.isDirectory())walk(f);else if(e.isFile()&&(/\.(rs|c|h|sql|toml|lock)$/.test(e.name)||e.name==='.cargo-checksum.json'))add(f);}};
 for(const p of metadata.packages)walk(path.dirname(p.manifest_path));
 for(const f of [...members])if(f.endsWith('.rs'))for(const m of readFileSync(f,'utf8').matchAll(/(?:include_str|include_bytes|include)!\(\s*"([^"]+)"/g)){const p=path.resolve(path.dirname(f),m[1]!);try{if(lstatSync(p).isFile())add(p);}catch{}}
 for(const name of ['tools/toolchain/run','tools/toolchain/lock.json','tools/toolchain/compiler.sh','rust-toolchain.toml'])add(path.join(repository,name));
 for(const tool of ['rustc','cargo'])add((await call(launcher,['rustup','which',tool])).trim());
 const sourcePins=[...members].sort().map(pinFile);
 const build=await call(launcher,['cargo','build','--offline','--locked','--message-format=json-render-diagnostics','--manifest-path',manifest,'--target-dir',target]);
 const messages=build.trim().split('\n').filter(Boolean).map(l=>JSON.parse(l));const artifacts=messages.filter(m=>m.reason==='compiler-artifact'&&m.executable&&m.target.name==='craft-commerce-auth-ready-bridge-v1');if(artifacts.length!==1)bad('NativeUnavailable');
 for(const p of sourcePins)if(!samePin(pinFile(p.path),p))bad('StaleOwner');
 const original=pinFile(artifacts[0].executable),binaryPath=path.join(directory,'auth-ready-bridge');copyFileSync(original.path,binaryPath,constants.COPYFILE_EXCL);chmodSync(binaryPath,0o700);const binary=pinFile(binaryPath);if(binary.sha256!==original.sha256)bad('StaleOwner');
 const linkage=await call('ldd',[binaryPath]),runtime=[...linkage.matchAll(/(\/\S+)\s+\(0x/g)].map(m=>pinFile(realpathSync(m[1]!)));if(runtime.length===0)bad('NativeUnavailable');
 const files=coreFreeze([...sourcePins,...runtime,binary]);
 const info=coreFreeze({kind:'actual-commerce-auth-native-component/v1-candidate',abi:COMMERCE_AUTH_READY_ABI_V1,code_epoch_sha256:code.sha256,node_runtime:{version:process.versions.node,platform:process.platform,architecture:process.arch},binary:{path:binary.path,sha256:binary.sha256,bytes:binary.bytes},members:files.map(({path,sha256,bytes})=>({path,sha256,bytes})),build:{command:launcher,manifest,flags:['build','--offline','--locked'],resolved_packages:metadata.packages.map((p:any)=>({name:p.name,version:p.version,source:p.source}))},scope:'actual fixed native component;not-application-basis-or-authenticated-entry-context',authority_effect:'none'});
 writeFileSync(path.join(directory,'native-component.json'),JSON.stringify(info,null,2)+'\n',{flag:'wx',mode:0o600});
 return createOwnedNative(directory,binary,files,info,()=>{});
}
/** Selected package producer; opaque registry member is the only accepted input. */
export function createCommerceAuthNativeOwnerFromSelectedAsset(asset:GenericSelectedAuthAsset):CommerceAuthNativeOwnerV1 {
 const selected=assertGenericSelectedAuthAsset(asset),binary=pinFile(selected.binary),files=selected.files.map(f=>pinFile(f.path));
 return createOwnedNative(selected.directory,binary,files,selected.manifest,()=>{assertGenericSelectedAuthAsset(asset);});
}
function createOwnedNative(directory:string,binary:FilePin,files:readonly FilePin[],info:Readonly<Record<string,unknown>>,selectedCurrent:()=>void):CommerceAuthNativeOwnerV1 {
 const binaryPath=binary.path;
 const s:NativeState={directory,binary,files,manifest:info,disposed:false,disposal:null,databases:new WeakMap(),completions:new WeakMap(),active:new Set(),queue:[],current(){if(s.disposed)bad('DisposedOwner');try{code.assertCurrent();selectedCurrent();assertPinnedFilesCurrent(files);}catch{return bad('StaleOwner');}},pump(){}};
 const finish=(job:Job)=>{if(job.done)return;job.done=true;clearTimeout(job.timer);if(job.hard)clearTimeout(job.hard);job.signal?.removeEventListener('abort',job.abort);s.active.delete(job);const i=s.queue.indexOf(job);if(i>=0)s.queue.splice(i,1);job.settle();s.pump();};
 const cancel=(job:Job,reason:AuthBridgeCodeV1)=>{if(job.done||job.failed)return;job.failed=true;job.reject(new CommerceAuthBridgeErrorV1(reason));if(job.child){job.child.kill('SIGTERM');job.hard=setTimeout(()=>job.child?.kill('SIGKILL'),200);job.hard.unref();}else finish(job);};
 const start=(job:Job)=>{
  if(performance.now()>=job.deadline){cancel(job,'BridgeTimeout');return;}
  try{s.current();databaseRecordCurrent(job.database);}catch{cancel(job,'StaleOwner');return;}if(performance.now()>=job.deadline){cancel(job,'BridgeTimeout');return;}s.active.add(job);
  const child=spawn(binaryPath,['--auth-db',job.database.file],{cwd:directory,env:{LANG:'C.UTF-8'},stdio:'pipe'});job.child=child;
  const stdout:Buffer[]=[],stderr:Buffer[]=[];let n=0,e=0;
  child.stdout.on('data',(b:Buffer)=>{n+=b.length;if(n>OUTPUT)cancel(job,'MalformedResponse');else stdout.push(b);});
  child.stderr.on('data',(b:Buffer)=>{e+=b.length;if(e>OUTPUT)cancel(job,'MalformedResponse');else stderr.push(b);});
  child.on('error',()=>cancel(job,'NativeUnavailable'));child.stdin.on('error',()=>cancel(job,'NativeUnavailable'));
  child.on('close',(exit,signal)=>{
   try{if(!job.failed){if(performance.now()>=job.deadline)bad('BridgeTimeout');s.current();databaseRecordCurrent(job.database);if(performance.now()>=job.deadline)bad('BridgeTimeout');if(exit!==0||signal!==null||e!==0)bad('NativeUnavailable');const response=checkCommerceAuthResponseV1(Buffer.concat(stdout),job.request);const h=Object.freeze({kind:'original-commerce-auth-pipe-completion/v1-candidate' as const});s.completions.set(h,{database:job.database,request:job.request,response});job.resolve(h);}}
   catch(error){if(!job.failed){job.failed=true;job.reject(error instanceof CommerceAuthBridgeErrorV1?error:new CommerceAuthBridgeErrorV1('NativeUnavailable'));}}
   finally{finish(job);}
  });
  child.stdin.end(JSON.stringify(job.request));
 };
 s.pump=()=>{if(s.disposed)return;while(s.active.size<ACTIVE&&s.queue.length){const job=s.queue.shift()!;if(!job.failed&&!job.done)start(job);}};
 const owner:CommerceAuthNativeOwnerV1=Object.freeze({kind:'original-commerce-auth-native-owner/v1-candidate' as const,
  async execute(h:CommerceAuthFixtureDatabaseV1,proposal:AuthBridgeRequestV1,signal?:AbortSignal){s.current();const database=databaseCurrent(s,h),request=captureCommerceAuthRequestV1(proposal);if(signal!==undefined&&!(signal instanceof AbortSignal))bad('InvalidRequest');if(signal?.aborted)bad('Cancelled');if(s.active.size>=ACTIVE&&s.queue.length>=QUEUED)bad('QueueFull');return new Promise<CommerceAuthCompletionV1>((resolve,reject)=>{let settle!:()=>void;const settled=new Promise<void>(r=>{settle=r;});const job:Job={database,request,signal,resolve,reject,child:null,failed:false,done:false,deadline:performance.now()+WAIT,timer:setTimeout(()=>{},0),hard:null,settled,settle,abort:()=>{}};clearTimeout(job.timer);job.timer=setTimeout(()=>cancel(job,'BridgeTimeout'),WAIT);job.abort=()=>cancel(job,'Cancelled');signal?.addEventListener('abort',job.abort,{once:true});s.queue.push(job);s.pump();});},
  inspectCompletion(h:CommerceAuthCompletionV1){s.current();const c=h&&typeof h==='object'?s.completions.get(h):undefined;if(!c)bad('ForeignOwner');return coreFreeze({request:c.request,response:c.response,qualification:'actual-owned-pipe-completion-data-only;not-private-entry-context',authority_effect:'none' as const});},
  assertCompletionDatabase(h:CommerceAuthCompletionV1,database:CommerceAuthFixtureDatabaseV1){s.current();const c=h&&typeof h==='object'?s.completions.get(h):undefined;if(!c||c.database!==databaseCurrent(s,database))bad('ForeignOwner');},
  inspect(){s.current();return s.manifest;},inspectWork(){return Object.freeze({active:s.active.size,queued:s.queue.length,unsettled:s.active.size});},assertCurrent(){s.current();},
  async dispose(){if(s.disposal)return s.disposal;s.disposed=true;const jobs=[...s.active,...s.queue];for(const job of jobs)cancel(job,'DisposedOwner');s.disposal=Promise.all(jobs.map(j=>j.settled)).then(()=>{});return s.disposal;},
 });owners.set(owner,s);s.current();return owner;
}
/** Internal fixture construction capability; absent from public SDK exports.
 * Creates only a fresh owned empty namespace, never adopts a supplied DB path. */
export function createCommerceAuthFixtureDatabaseV1(owner:CommerceAuthNativeOwnerV1):CommerceAuthFixtureDatabaseV1 {
 const s=native(owner);s.current();const directory=mkdtempSync(path.join(s.directory,'fixture-'));chmodSync(directory,0o700);const ds=lstatSync(directory,{bigint:true}),h=Object.freeze({kind:'original-commerce-auth-fixture-database/v1-candidate' as const});s.databases.set(h,{directory,file:path.join(directory,'auth.sqlite'),directoryIdentity:[ds.dev,ds.ino,ds.mode].join(':'),identity:null});return h;
}
export function inspectCommerceAuthFixtureDatabaseV1(owner:CommerceAuthNativeOwnerV1,h:CommerceAuthFixtureDatabaseV1):Readonly<{directory:string;file:string;qualification:string}> {
 const s=native(owner);s.current();const d=h&&typeof h==='object'?s.databases.get(h):undefined;if(!d)bad('ForeignOwner');return Object.freeze({directory:d.directory,file:d.file,qualification:'isolated-test-fixture-only;not-production-authentication'});
}
export function sealCommerceAuthFixtureDatabaseV1(owner:CommerceAuthNativeOwnerV1,h:CommerceAuthFixtureDatabaseV1):void {
 const s=native(owner);s.current();const d=h&&typeof h==='object'?s.databases.get(h):undefined;if(!d||d.identity!==null)bad('ForeignOwner');const f=lstatSync(d.file,{bigint:true});if(!f.isFile()||f.isSymbolicLink()||(f.mode&0o777n)!==0o600n)bad('InvalidRequest');d.identity=[f.dev,f.ino,f.mode].join(':');databaseCurrent(s,h);
}
