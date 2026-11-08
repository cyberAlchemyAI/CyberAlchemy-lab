import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {types as nodeTypes} from 'node:util';
import {createHash} from 'node:crypto';
import {captureJson,dataDigest,reject} from './contracts.js';
import {validateProfilePackage,type ProfilePackage,type PackageReference} from './contracts.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import {assertBusinessAuthoringRelativePath,validateBusinessAuthoringProject,validateProfilePackageV3,type ProfilePackageV3} from './contracts-v3.js';
import type {BusinessAuthoringProject,BusinessAuthoringLoaderIdentity,BusinessAuthoringLock} from './business-authoring-protocol.js';
import type {CapturedFile} from './loader.js';

/** B05.1 read/hash custody, without recipe execution or acceptance.
 * Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md. */
export interface LoadedBusinessAuthoringPackage {
 readonly id:string;readonly root:string;readonly data:ProfilePackageV3|ProfilePackage;
 readonly manifest_sha256:string;readonly asset_sha256:string;readonly assets:Readonly<Record<string,CapturedFile>>;
}
export interface BusinessAuthoringSnapshot {
 readonly kind:'business-authoring-snapshot';readonly project_path:string;readonly project:BusinessAuthoringProject;
 readonly sources:Readonly<Record<string,CapturedFile>>;readonly packages:readonly LoadedBusinessAuthoringPackage[];
 readonly lock:BusinessAuthoringLock;
}
interface PhysicalIdentity {readonly dev:bigint;readonly ino:bigint;readonly size:bigint;readonly mtimeNs:bigint;readonly ctimeNs:bigint}
interface CapturedEntry {readonly file:CapturedFile;readonly physical:PhysicalIdentity;readonly nodes:readonly Readonly<{path:string;dev:bigint;ino:bigint}>[]}
const snapshots=new WeakMap<object,readonly CapturedEntry[]>();
const validationScopes=new WeakSet<object>();
const ownedBytes=16777216,identityBytes=536870912,maxFiles=10000;
// Exact supported technical contract bytes; package labels cannot redefine their implementation.
// These pins select the existing finite Operation runtime, not proof or native-code certification.
const runtimePins=Object.freeze({
 formal_profile_asset:'52edb96ec78053d160c8f89b75d08bc98af5ace486ff061537b53cc041715ef2',
 identity_algorithm_asset:'da26bed7b4ca21257de00f1e295063ae849959f85256f63790d67d885ee2c9cb',
 settlement_asset:'724d654b644895d18089e51cb86cd733b54d3ad7c90ce70d7bfa031e1ccbf5e1',
 transport_asset:'9a94cef566d9f1062323629233eac5425b1b8ee7d9ed026e7787af96bb67276a',
});
function info(absolute:string):BigIntStats {
 try{return lstatSync(absolute,{bigint:true});}catch{return reject('BUSINESS_PROFILE_FILE_MISSING',absolute,'selected closure path is missing');}
}
function pathNodes(absolute:string):CapturedEntry['nodes'] {
 let current=path.parse(absolute).root;const nodes:{path:string;dev:bigint;ino:bigint}[]=[];
 const parts=absolute.slice(current.length).split(path.sep).filter(Boolean);
 for(const [index,part] of parts.entries()){
  current=path.join(current,part);const stat=info(current);
  if(stat.isSymbolicLink())reject('BUSINESS_PROFILE_PATH_SYMLINK',current,'selected closure cannot use symlinks');
  if(index<parts.length-1&&!stat.isDirectory())reject('BUSINESS_PROFILE_FILE_KIND',current,'parent path must be a directory');
  nodes.push(Object.freeze({path:current,dev:stat.dev,ino:stat.ino}));
 }
 return Object.freeze(nodes);
}
function physical(stat:BigIntStats):PhysicalIdentity {return Object.freeze({dev:stat.dev,ino:stat.ino,size:stat.size,mtimeNs:stat.mtimeNs,ctimeNs:stat.ctimeNs});}
function samePhysical(a:PhysicalIdentity,b:PhysicalIdentity):boolean {return a.dev===b.dev&&a.ino===b.ino&&a.size===b.size&&a.mtimeNs===b.mtimeNs&&a.ctimeNs===b.ctimeNs;}
function capture(root:string,relative:string,key:string,text:boolean):CapturedEntry {
 assertBusinessAuthoringRelativePath(relative,key);const resolvedRoot=path.resolve(root),absolute=path.resolve(resolvedRoot,relative);
 if(!absolute.startsWith(resolvedRoot+path.sep))reject('BUSINESS_PROFILE_PATH_ESCAPE',key,'path escaped its owner');
 const nodes=pathNodes(absolute),before=info(absolute);
 if(!before.isFile())reject('BUSINESS_PROFILE_FILE_KIND',key,'regular file required');
 const budget=text?ownedBytes:identityBytes;
 if(before.size>BigInt(budget))reject('BUSINESS_PROFILE_FILE_BUDGET',key,'file exceeds capture budget');
 const hash=createHash('sha256'),parts:Buffer[]=[];let size=0,fd:number;
 try{fd=openSync(absolute,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);}catch{return reject('BUSINESS_PROFILE_FILE_DRIFT',key,'selected file could not be opened safely');}
 try{
  if(!samePhysical(physical(before),physical(fstatSync(fd,{bigint:true}))))reject('BUSINESS_PROFILE_FILE_DRIFT',key,'file replaced before capture');
  const buffer=Buffer.alloc(65536);
  for(;;){const count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;size+=count;if(size>budget)reject('BUSINESS_PROFILE_FILE_BUDGET',key,'file grew past capture budget');const bytes=buffer.subarray(0,count);hash.update(bytes);if(text)parts.push(Buffer.from(bytes));}
  if(!samePhysical(physical(before),physical(fstatSync(fd,{bigint:true}))))reject('BUSINESS_PROFILE_FILE_DRIFT',key,'file changed during capture');
 }finally{closeSync(fd);}
 const after=info(absolute),afterNodes=pathNodes(absolute);
 if(!samePhysical(physical(before),physical(after))||nodes.some((node,i)=>node.dev!==afterNodes[i]?.dev||node.ino!==afterNodes[i]?.ino)||BigInt(size)!==after.size)reject('BUSINESS_PROFILE_FILE_DRIFT',key,'selected path changed during capture');
 let body:string|undefined;
 if(text)try{body=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(Buffer.concat(parts));}catch{return reject('BUSINESS_PROFILE_FILE_ENCODING',key,'selected source/assets must be UTF-8');}
 const file=Object.freeze({key,path:absolute,root:resolvedRoot,relative,sha256:hash.digest('hex'),bytes:size,...(body===undefined?{}:{text:body})});
 return Object.freeze({file,physical:physical(after),nodes});
}
function json(file:CapturedFile):unknown {try{return JSON.parse(file.text!);}catch{return reject('BUSINESS_PROFILE_FILE_JSON',file.key,'selected JSON file is invalid');}}
function aggregate(files:readonly CapturedFile[]):string {return dataDigest([...files].sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0).map(file=>({key:file.key,sha256:file.sha256,bytes:file.bytes})));}

export function loadBusinessAuthoringProject(projectPath:string,identity:BusinessAuthoringLoaderIdentity,pinnedLock?:unknown):BusinessAuthoringSnapshot {
 if(typeof projectPath!=='string'||!projectPath||projectPath.includes('\0'))reject('BUSINESS_PROFILE_PROJECT_PATH','/','project file path required');
 const supplied=captureJson(identity) as unknown as BusinessAuthoringLoaderIdentity;
 if(!supplied||typeof supplied!=='object'||Object.keys(supplied).some(key=>key!=='engine'&&key!=='tools')||!Array.isArray(supplied.engine)||!Array.isArray(supplied.tools))reject('BUSINESS_PROFILE_IDENTITY_MISSING','/','closed engine/tool file manifests required');
 const absolute=path.resolve(projectPath),root=path.dirname(absolute),all:CapturedEntry[]=[],sources:Record<string,CapturedFile>=Object.create(null);
 const physicalOwners=new Map<string,string>();let totalBytes=0;
 const add=(entry:CapturedEntry,owned=true):CapturedFile=>{
  const physicalKey=entry.physical.dev+':'+entry.physical.ino,prior=physicalOwners.get(physicalKey);
  if(prior!==undefined)reject('BUSINESS_PROFILE_FILE_ALIAS',entry.file.key,'distinct closure entries cannot alias '+prior);
  physicalOwners.set(physicalKey,entry.file.key);all.push(entry);if(owned)totalBytes+=entry.file.bytes;
  if(totalBytes>ownedBytes||all.length>maxFiles)reject('BUSINESS_PROFILE_CLOSURE_BUDGET',entry.file.key,'bounded selected closure required');
  return entry.file;
 };
 const projectFile=add(capture(root,path.basename(absolute),'source:project',true));sources[path.basename(absolute)]=projectFile;
 const project=validateBusinessAuthoringProject(json(projectFile));
 for(const model of project.models){
  if(Object.hasOwn(sources,model.source))reject('BUSINESS_PROFILE_SOURCE_CONFLICT',model.source,'model cannot alias another selected file');
  sources[model.source]=add(capture(root,model.source,'source:'+model.source,true));
 }
 const decisions:CapturedFile[]=[];
 for(const selection of project.decisions){
  if(Object.hasOwn(sources,selection.path))reject('BUSINESS_PROFILE_SOURCE_CONFLICT',selection.path,'decision cannot alias another selected file');
  const file=add(capture(root,selection.path,'decision:'+selection.model_id,true));
  validateBusinessAuthoringContract('decision',json(file));sources[selection.path]=file;decisions.push(file);
 }
 const packages=new Map<string,LoadedBusinessAuthoringPackage>(),byRoot=new Map<string,LoadedBusinessAuthoringPackage>(),claims=new Map<string,string>(),active=new Set<string>();
 const visit=(packageRoot:string,reference:Omit<PackageReference,'sha256'> & {readonly sha256?:string},depth:number):void=>{
  if(depth>32)reject('BUSINESS_PROFILE_DEPENDENCY_BUDGET',reference.id,'dependency depth exceeded');
  const resolved=path.resolve(packageRoot);pathNodes(resolved);
  const claimed=claims.get(reference.id);if(claimed!==undefined&&claimed!==resolved)reject('BUSINESS_PROFILE_DEPENDENCY_CONFLICT',reference.id,'one root per package identity required');
  if(active.has(resolved))reject('BUSINESS_PROFILE_DEPENDENCY_CYCLE',reference.id,'dependency cycle');
  const prior=byRoot.get(resolved);
  if(prior){if(prior.id!==reference.id||prior.data.version!==reference.version||reference.sha256!==undefined&&prior.manifest_sha256!==reference.sha256)reject('BUSINESS_PROFILE_DEPENDENCY_CONFLICT',reference.id,'repeated package reference must match exactly');return;}
  if(claims.size>=128)reject('BUSINESS_PROFILE_DEPENDENCY_BUDGET',reference.id,'package count exceeded');claims.set(reference.id,resolved);
  const manifest=add(capture(resolved,'profile.json','package:'+reference.id,true));
  if(reference.sha256!==undefined&&reference.sha256!==manifest.sha256)reject('BUSINESS_PROFILE_DEPENDENCY_DIGEST',reference.id,'manifest differs from exact dependency pin');
  const raw=json(manifest) as {schema_version?:string}|null;
  // V1 may contribute existing technical roles. V2 application packages never become v3 owners.
  const data=raw?.schema_version==='craft.profile-package/v1'?validateProfilePackage(raw):validateProfilePackageV3(raw);
  if(data.id!==reference.id||data.version!==reference.version)reject('BUSINESS_PROFILE_DEPENDENCY_VERSION',reference.id,'selected package identity/version differs');
  active.add(resolved);const assets:Record<string,CapturedFile>=Object.create(null);let packageBytes=manifest.bytes;
  for(const asset of data.assets){const file=add(capture(resolved,asset.path,'asset:'+data.id+':'+asset.id,true));if(file.sha256!==asset.sha256)reject('BUSINESS_PROFILE_ASSET_DIGEST',asset.id,'selected asset differs from declared pin');assets[asset.id]=file;packageBytes+=file.bytes;}
  if(packageBytes>data.budgets.bytes)reject('BUSINESS_PROFILE_CLOSURE_BUDGET',data.id,'package bytes exceed declared budget');
  if(data.schema_version==='craft.profile-package/v3-candidate'){
   for(const [field,digest] of Object.entries(runtimePins)){
    const id=data.application_runtime[field as keyof typeof runtimePins],file=assets[id];
    if(!file||file.sha256!==digest)reject('BUSINESS_PROFILE_RUNTIME_COMPATIBILITY','/application_runtime/'+field,'asset is not the supported versioned Operation contract');
   }
   // Parse inert data as well as verifying the selected compatible bytes.
   json(assets[data.application_runtime.formal_profile_asset]!);json(assets[data.application_runtime.identity_algorithm_asset]!);
  }
  for(const dependency of data.dependencies){assertBusinessAuthoringRelativePath(dependency.path,'/dependencies/'+dependency.id+'/path');visit(path.resolve(resolved,dependency.path),dependency,depth+1);}
  active.delete(resolved);
  const loaded=Object.freeze({id:data.id,root:resolved,data,manifest_sha256:manifest.sha256,asset_sha256:aggregate(Object.values(assets)),assets:Object.freeze(assets)});
  packages.set(data.id,loaded);byRoot.set(resolved,loaded);
 };
 for(const reference of project.profiles)visit(path.resolve(root,reference.path),reference,0);
 const selected=[...packages.values()].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 if(selected.filter(pkg=>pkg.data.schema_version==='craft.profile-package/v3-candidate').length!==1)reject('BUSINESS_PROFILE_RUNTIME_AMBIGUOUS','/profiles','exactly one explicit authoring/runtime owner required');
 const roleOwners=new Map<string,string>();
 for(const pkg of selected)for(const capability of pkg.data.capabilities){
  const prior=roleOwners.get(capability.role);
  if(prior!==undefined)reject('BUSINESS_PROFILE_ROLE_OWNER_AMBIGUOUS','/profiles','role '+capability.role+' is claimed by '+prior+' and '+pkg.id);
  roleOwners.set(capability.role,pkg.id);
 }
 const identityPaths=new Set<string>();let identityTotal=0;
 const identities=(files:BusinessAuthoringLoaderIdentity['engine'],prefix:string):string=>{
  if(!files.length||files.length>maxFiles)reject('BUSINESS_PROFILE_IDENTITY_MISSING','/'+prefix,'bounded nonempty identity manifest required');
  const keys=new Set<string>(),rows:CapturedFile[]=[];
  for(const [index,item] of files.entries()){
   if(!item||typeof item!=='object'||Object.keys(item).length!==2||typeof item.key!=='string'||typeof item.path!=='string'||!item.path||item.path.includes('\0'))reject('BUSINESS_PROFILE_IDENTITY_CONFLICT',`/${prefix}/${index}`,'closed key/path identity required');
   assertBusinessAuthoringRelativePath(item.key,`/${prefix}/${index}/key`);
   if(keys.has(item.key))reject('BUSINESS_PROFILE_IDENTITY_CONFLICT',item.key,'identity key duplicated');keys.add(item.key);
   const target=path.resolve(item.path);if(identityPaths.has(target))reject('BUSINESS_PROFILE_IDENTITY_CONFLICT',item.key,'identity path duplicated');identityPaths.add(target);
   const file=add(capture(path.dirname(target),path.basename(target),prefix+':'+item.key,false),false);identityTotal+=file.bytes;
   if(identityTotal>identityBytes)reject('BUSINESS_PROFILE_IDENTITY_BUDGET',prefix,'identity closure exceeds byte budget');rows.push(file);
  }
  return aggregate(rows);
 };
 const body={schema_version:'craft.business-authoring-lock/v1-candidate' as const,engine_sha256:identities(supplied.engine,'engine'),tool_sha256:identities(supplied.tools,'tool'),source_sha256:aggregate(Object.values(sources).filter(file=>!file.key.startsWith('decision:'))),decision_sha256:aggregate(decisions),packages:selected.map(pkg=>({id:pkg.id,version:pkg.data.version,sha256:pkg.manifest_sha256,asset_sha256:pkg.asset_sha256}))};
 const lock=validateBusinessAuthoringContract<BusinessAuthoringLock>('lock',{...body,lock_sha256:dataDigest(body)});
 if(pinnedLock!==undefined){
  const pinned=validateBusinessAuthoringContract<BusinessAuthoringLock>('lock',pinnedLock),{lock_sha256,...pinnedBody}=pinned;
  if(dataDigest(pinnedBody)!==lock_sha256)reject('BUSINESS_PROFILE_LOCK_DIGEST','/lock_sha256','pinned lock digest is invalid');
  if(dataDigest(lock)!==dataDigest(pinned))reject('BUSINESS_PROFILE_LOCK_STALE','/','pinned lock must equal the complete recomputed selection');
 }
 const snapshot:BusinessAuthoringSnapshot=Object.freeze({kind:'business-authoring-snapshot',project_path:absolute,project,sources:Object.freeze(sources),packages:Object.freeze(selected),lock});
 snapshots.set(snapshot,Object.freeze(all));assertBusinessAuthoringSnapshotCurrent(snapshot);return snapshot;
}
export function assertBusinessAuthoringSnapshotCurrent(snapshot:BusinessAuthoringSnapshot):void {
 const files=snapshots.get(snapshot);if(!files)reject('BUSINESS_PROFILE_SNAPSHOT_UNREGISTERED','/','load original files in this process; serialized/cast snapshots are not custody');
 if(validationScopes.has(snapshot))return;
 for(const entry of files){
  const current=capture(entry.file.root,entry.file.relative,entry.file.key,false);
  if(current.file.sha256!==entry.file.sha256||!samePhysical(current.physical,entry.physical)||entry.nodes.some((node,i)=>node.dev!==current.nodes[i]?.dev||node.ino!==current.nodes[i]?.ino))reject('BUSINESS_PROFILE_SNAPSHOT_STALE',entry.file.key,'selected bytes or physical closure identity changed');
 }
}

/** Actual captured closure for trusted native qualification; no new registration or admission.
 * Open questions: docs/BUSINESS-AUTHORING.md. */
export function businessAuthoringSnapshotFiles(snapshot:BusinessAuthoringSnapshot):readonly CapturedFile[]{
 assertBusinessAuthoringSnapshotCurrent(snapshot);return Object.freeze(snapshots.get(snapshot)!.map(entry=>entry.file));
}

/** Trusted synchronous construction/currentness scope. Full byte/physical/ancestor validation
 * brackets the operation; nested pure owner checks reuse only that in-process scope.
 * Never encompass a final persistent output/decision effect. No async work is admitted.
 * Open questions: docs/BUSINESS-AUTHORING.md; this grants no acceptance or effects. */
export function withBusinessAuthoringSnapshotValidation<T>(snapshot:BusinessAuthoringSnapshot,operation:()=>T):T {
 const sync=(value:unknown):void=>{if(nodeTypes.isPromise(value)||nodeTypes.isProxy(value))reject('BUSINESS_PROFILE_ASYNC_VALIDATION','/','synchronous inert owner result required');if(value&&(typeof value==='object'||typeof value==='function')){let current:object|null=value as object;for(let depth=0;current;depth++){if(depth>64||nodeTypes.isProxy(current)||Object.getOwnPropertyDescriptor(current,'then'))reject('BUSINESS_PROFILE_ASYNC_VALIDATION','/','synchronous owner result without thenable behavior required');current=Object.getPrototypeOf(current);}}};
 const run=():T=>{if(nodeTypes.isAsyncFunction(operation))reject('BUSINESS_PROFILE_ASYNC_VALIDATION','/','synchronous owner construction required');const value=operation();sync(value);return value;};
 if(validationScopes.has(snapshot)){assertBusinessAuthoringSnapshotCurrent(snapshot);return run();}
 assertBusinessAuthoringSnapshotCurrent(snapshot);validationScopes.add(snapshot);
 try{return run();}finally{validationScopes.delete(snapshot);assertBusinessAuthoringSnapshotCurrent(snapshot);}
}
