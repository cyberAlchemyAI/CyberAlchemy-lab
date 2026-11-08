import {lstatSync,readFileSync,openSync,readSync,closeSync,statSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {dataDigest,reject,validateProfilePackage,validateProfileProject,type ProfilePackage,type ProfileProject,type ProfileLock,type PackageReference} from './contracts.js';
import {createProfileLock,assertProfileLockMatches} from './lock.js';
import {validateProfileProjectV2,validateProfilePackageV2,validateBusinessApplication,type ProfileProjectV2,type ProfilePackageV2} from './contracts-v2.js';

/** Read/hash only. Native/template assets are never imported or evaluated.
 * Open questions: PE10 completion and PE19 complete core/tool manifest qualification. */
export interface IdentityFile {readonly key:string;readonly path:string}
export interface CapturedFile {readonly key:string;readonly path:string;readonly root:string;readonly relative:string;readonly sha256:string;readonly bytes:number;readonly text?:string}
export interface LoadedPackage {readonly id:string;readonly root:string;readonly data:ProfilePackage;readonly manifest_sha256:string;readonly asset_sha256:string;readonly assets:Readonly<Record<string,CapturedFile>>}
export interface ProfileSnapshot {readonly project_path:string;readonly project:ProfileProject;readonly sources:Readonly<Record<string,CapturedFile>>;readonly packages:readonly LoadedPackage[];readonly lock:ProfileLock}
export interface LoadedPackageV2 extends Omit<LoadedPackage,'data'>{readonly data:ProfilePackageV2}
export interface ProfileSnapshotV2 extends Omit<ProfileSnapshot,'project'|'packages'>{readonly project:ProfileProjectV2;readonly packages:readonly (LoadedPackage|LoadedPackageV2)[]}
export interface LoaderIdentity {readonly engine:readonly IdentityFile[];readonly tools:readonly IdentityFile[];readonly additionalSources?:readonly IdentityFile[]}
const snapshots=new WeakMap<object,readonly CapturedFile[]>();
const ownedBytes=16777216,identityBytes=536870912;
function noSymlinks(absolute:string):void {
 let current=path.parse(absolute).root;
 for(const part of absolute.slice(current.length).split(path.sep).filter(Boolean)){
  current=path.join(current,part);let info;try{info=lstatSync(current);}catch{return reject('PROFILE_FILE_MISSING',absolute,'declared closure path is missing');}
  if(info.isSymbolicLink())reject('PROFILE_PATH_SYMLINK',absolute,'symlinks cannot supply selected closure bytes');
 }
}
function ownedPath(root:string,relative:string):string {
 if(path.isAbsolute(relative)||relative.includes('\\')||relative.split('/').some(p=>!p||p==='.'||p==='..'))reject('PROFILE_PATH_ESCAPE',relative,'owned relative path required');
 const result=path.resolve(root,relative);if(!result.startsWith(path.resolve(root)+path.sep))reject('PROFILE_PATH_ESCAPE',relative,'outside owned root');noSymlinks(result);return result;
}
function capture(root:string,relative:string,key:string,text:boolean):CapturedFile {
 const absolute=ownedPath(root,relative),before=lstatSync(absolute);
 if(!before.isFile())reject('PROFILE_FILE_KIND',key,'regular file required');
 if(before.size>(text?ownedBytes:identityBytes))reject('PROFILE_FILE_BUDGET',key,'selected file exceeds byte budget');
 const hash=createHash('sha256');let body:string|undefined;
 if(text){const bytes=readFileSync(absolute);hash.update(bytes);try{body=new TextDecoder('utf-8',{fatal:true}).decode(bytes);}catch{return reject('PROFILE_FILE_ENCODING',key,'owned source/template/native asset must be UTF-8 text');}}
 else {const fd=openSync(absolute,'r'),buffer=Buffer.alloc(65536);try{for(;;){const count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;hash.update(buffer.subarray(0,count));}}finally{closeSync(fd);}}
 const after=statSync(absolute);if(before.size!==after.size||before.ino!==after.ino||before.mtimeMs!==after.mtimeMs)reject('PROFILE_FILE_DRIFT',key,'file changed during capture');
 return Object.freeze({key,path:absolute,root:path.resolve(root),relative,sha256:hash.digest('hex'),bytes:after.size,...(body!==undefined?{text:body}:{})});
}
function json(file:CapturedFile):unknown {try{return JSON.parse(file.text!);}catch{return reject('PROFILE_FILE_JSON',file.key,'invalid declared JSON');}}
function identities(files:readonly IdentityFile[],prefix:string,all:CapturedFile[]):string {
 if(!files.length)reject('PROFILE_IDENTITY_MISSING',prefix,'exact engine/tool file manifest required');
 const keys=new Set<string>(),rows:CapturedFile[]=[];
 for(const item of files){if(!item.key||keys.has(item.key))reject('PROFILE_IDENTITY_CONFLICT',prefix,'unique portable identity keys required');keys.add(item.key);const absolute=path.resolve(item.path);const captured=capture(path.dirname(absolute),path.basename(absolute),prefix+':'+item.key,false);rows.push(captured);all.push(captured);}
 return dataDigest(rows.sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0).map(f=>({key:f.key,sha256:f.sha256,bytes:f.bytes})));
}
export function loadProfileProject(projectPath:string,identity:LoaderIdentity,pinnedLock?:unknown):ProfileSnapshot {
 return loadProfileProjectInternal(projectPath,identity,pinnedLock,'v1') as ProfileSnapshot;
}
/** V2 capture is separate from v1 source semantics; no package code executes. */
export function loadProfileProjectV2(projectPath:string,identity:LoaderIdentity,pinnedLock?:unknown):ProfileSnapshotV2 {
 return loadProfileProjectInternal(projectPath,identity,pinnedLock,'v2') as ProfileSnapshotV2;
}
function loadProfileProjectInternal(projectPath:string,identity:LoaderIdentity,pinnedLock:unknown,version:'v1'|'v2'):ProfileSnapshot|ProfileSnapshotV2 {
 const absolute=path.resolve(projectPath),root=path.dirname(absolute),all:CapturedFile[]=[];
 const projectFile=capture(root,path.basename(absolute),'source:project',true);all.push(projectFile);
 const project=version==='v1'?validateProfileProject(json(projectFile)):validateProfileProjectV2(json(projectFile));const sources:Record<string,CapturedFile>=Object.create(null);sources[path.basename(absolute)]=projectFile;
 for(const declared of identity.additionalSources??[]){if(Object.hasOwn(sources,declared.key)||!declared.key.startsWith('application:'))reject('PROFILE_SOURCE_CONFLICT',declared.key,'unique application closure key required');const absoluteSource=path.resolve(declared.path);if(!absoluteSource.startsWith(root+path.sep))reject('PROFILE_PATH_ESCAPE',declared.key,'application closure belongs to project root');const file=capture(root,path.relative(root,absoluteSource),declared.key,true);sources[declared.key]=file;all.push(file);}
 for(const call of project.application_calls??[])if(!sources['application:'+call.id+':source'])reject('PROFILE_APPLICATION_FRONTEND_REQUIRED',call.id,'registered frontend must capture the exact complete application source closure');
 let sourceBytes=Object.values(sources).reduce((sum,file)=>sum+file.bytes,0);if(sourceBytes>ownedBytes||Object.keys(sources).length>10000)reject('PROFILE_SOURCE_BUDGET','/','bounded complete source closure required');
 const selectedSources=[...project.domain_sources,...(project.integration_configuration===undefined?[]:[project.integration_configuration]),...(project.schema_version==='craft.profile-project/v2-candidate'?project.application_models.flatMap(m=>[m.source,m.semantics]):[])];
 for(const relative of project.schema_version==='craft.profile-project/v2-candidate'?[...new Set(selectedSources)]:selectedSources){
  if(Object.hasOwn(sources,relative))reject('PROFILE_SOURCE_CONFLICT',relative,'distinct selected source/config paths required');
  const file=capture(root,relative,'source:'+relative,true);sources[relative]=file;all.push(file);sourceBytes+=file.bytes;
  if(sourceBytes>ownedBytes)reject('PROFILE_SOURCE_BUDGET',relative,'source closure exceeds byte budget');
 }
 if(project.schema_version==='craft.profile-project/v2-candidate')for(const model of project.application_models)validateBusinessApplication(json(sources[model.semantics]!));
 const active=new Set<string>(),packages=new Map<string,LoadedPackage|LoadedPackageV2>(),claims=new Map<string,{root:string;sha256:string}>(),byRoot=new Map<string,LoadedPackage|LoadedPackageV2>();let totalBytes=sourceBytes,totalFiles=all.length;
 const visit=(packageRoot:string,ref:Omit<PackageReference,'sha256'> & {readonly sha256?:string},depth:number):void=>{
  if(depth>32||packages.size>=128)reject('PROFILE_DEPENDENCY_BUDGET',ref.id,'finite dependency depth/count exceeded');
  const resolved=path.resolve(packageRoot);noSymlinks(resolved);
  if(active.has(resolved))reject('PROFILE_DEPENDENCY_CYCLE',ref.id,'dependency cycle');
  const cached=byRoot.get(resolved);if(cached){if(cached.id!==ref.id||cached.data.version!==ref.version||ref.sha256&&cached.manifest_sha256!==ref.sha256)reject('PROFILE_DEPENDENCY_CONFLICT',ref.id,'cached dependency identity/version/digest differs');return;}
  const manifest=capture(resolved,'profile.json','package:'+ref.id,true);totalBytes+=manifest.bytes;totalFiles++;
  if(ref.sha256&&ref.sha256!==manifest.sha256)reject('PROFILE_DEPENDENCY_DIGEST',ref.id,'dependency manifest differs from pin');
  const raw=json(manifest) as {schema_version?:string};const data=version==='v2'&&raw.schema_version==='craft.profile-package/v2-candidate'?validateProfilePackageV2(raw):validateProfilePackage(raw);if(data.id!==ref.id||data.version!==ref.version)reject('PROFILE_DEPENDENCY_VERSION',ref.id,'selected identity/version differs');
  const claim=claims.get(data.id);if(claim&&(claim.root!==resolved||claim.sha256!==manifest.sha256))reject('PROFILE_DEPENDENCY_CONFLICT',ref.id,'competing roots/versions for one identity');claims.set(data.id,{root:resolved,sha256:manifest.sha256});
  const prior=packages.get(data.id);if(prior){if(prior.root!==resolved||prior.manifest_sha256!==manifest.sha256)reject('PROFILE_DEPENDENCY_CONFLICT',ref.id,'two roots/versions for one package identity');return;}
  active.add(resolved);all.push(manifest);
  const assets:Record<string,CapturedFile>=Object.create(null);let packageBytes=manifest.bytes;
  for(const asset of data.assets){const file=capture(resolved,asset.path,'asset:'+data.id+':'+asset.id,true);if(file.sha256!==asset.sha256)reject('PROFILE_ASSET_DIGEST',asset.id,'asset bytes differ from declared digest');assets[asset.id]=file;all.push(file);packageBytes+=file.bytes;totalBytes+=file.bytes;totalFiles++;}
  if(packageBytes>data.budgets.bytes||totalBytes>ownedBytes||totalFiles>10000)reject('PROFILE_CLOSURE_BUDGET',data.id,'package/closure byte or file limit exceeded');
  for(const dep of data.dependencies)visit(path.resolve(resolved,dep.path),dep,depth+1);
  active.delete(resolved);
  const loaded=Object.freeze({id:data.id,root:resolved,data,manifest_sha256:manifest.sha256,asset_sha256:dataDigest(Object.values(assets).sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0).map(f=>({key:f.key,sha256:f.sha256,bytes:f.bytes}))),assets:Object.freeze(assets)}) as LoadedPackage|LoadedPackageV2;
  packages.set(data.id,loaded);byRoot.set(resolved,loaded);
 };
 for(const ref of project.profiles)visit(path.resolve(root,ref.path),ref,0);
 const selected=[...packages.values()].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 const lock=createProfileLock({engine_sha256:identities(identity.engine,'engine',all),tool_sha256:identities(identity.tools,'tool',all),source_sha256:dataDigest(Object.values(sources).sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0).map(f=>({key:f.key,sha256:f.sha256,bytes:f.bytes}))),packages:selected.map(p=>({id:p.id,version:p.data.version,sha256:p.manifest_sha256,asset_sha256:p.asset_sha256}))});
 if(pinnedLock!==undefined)assertProfileLockMatches(lock,pinnedLock);
 const snapshot=Object.freeze({project_path:absolute,project,sources:Object.freeze(sources),packages:Object.freeze(selected),lock}) as ProfileSnapshot|ProfileSnapshotV2;snapshots.set(snapshot,Object.freeze(all));assertProfileSnapshotCurrent(snapshot);return snapshot;
}
export function assertProfileSnapshotCurrent(snapshot:ProfileSnapshot|ProfileSnapshotV2):void {
 const files=snapshots.get(snapshot);if(!files)reject('PROFILE_SNAPSHOT_UNREGISTERED','/','rebuild persisted data through the loader; JSON is not a current process object');
 for(const file of files){const current=capture(file.root,file.relative,file.key,false);if(current.sha256!==file.sha256||current.bytes!==file.bytes)reject('PROFILE_SNAPSHOT_STALE',file.key,'selected closure bytes changed');}
}
/** Exposes pinned identity metadata, not mutable bytes or an admission certificate. */
export function profileSnapshotFiles(snapshot:ProfileSnapshot|ProfileSnapshotV2):readonly CapturedFile[] {
 const files=snapshots.get(snapshot);if(!files)reject('PROFILE_SNAPSHOT_UNREGISTERED','/','unknown process snapshot');return files;
}
