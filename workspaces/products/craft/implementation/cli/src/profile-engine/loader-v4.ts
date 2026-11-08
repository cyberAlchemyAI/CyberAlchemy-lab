import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,readdirSync,statSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {captureJson,dataDigest,reject} from './contracts.js';
import {validateProfilePackageV4,type ProfilePackageV4} from './contracts-v4.js';
import {U0_RUNTIME_PINS_V4} from './u0-runtime-pins.generated.js';
import {U0_NATIVE_ABI,U0_SUCCESSOR_DESCRIPTOR,type U0ResolvedNativeBasis,type U0ResolvedArtifact} from './u0-realization-contract.js';
import type {U0RequestRuntimeFileV2} from './business-authoring-request.js';
/** Actual built-package capture. No source fallback or final application subject.
 * Open Questions: docs/U0-SHARED-CONTRACTS.md and later installed qualification. */
function fail(at:string,message:string):never{return reject('BUSINESS_PROFILE_V4',at,message);}
function info(file:string):BigIntStats {try{return lstatSync(file,{bigint:true});}catch{return fail(file,'closure member is missing');}}
const physical=(s:BigIntStats)=>[s.dev,s.ino,s.mode,s.size,s.mtimeNs,s.ctimeNs].map(String).join(':');
function parents(file:string){let at=path.parse(file).root;const rows:{path:string;identity:string}[]=[];for(const part of ['',...path.dirname(file).slice(at.length).split(path.sep).filter(Boolean)]){if(part)at=path.join(at,part);const s=info(at);if(!s.isDirectory()||s.isSymbolicLink())fail(at,'original nonsymlink directory required');rows.push({path:at,identity:String(s.dev)+':'+s.ino});}return rows;}
export interface U0CapturedFileV4 {readonly path:string;readonly sha256:string;readonly bytes:number;readonly text?:string;assertCurrent():void}
type ParentV4=Readonly<{path:string;identity:string}>;
// Private batch data: no public validation scope, callback, TTL or ambient cache.
const fileChecks=new WeakMap<object,Readonly<{parents:readonly ParentV4[];assertFile():void}>>();
function assertParent(row:ParentV4):void {const s=info(row.path);if(!s.isDirectory()||s.isSymbolicLink()||String(s.dev)+':'+s.ino!==row.identity)fail(row.path,'original bytes or physical closure changed');}

/** Trusted filesystem utility. Capturing data never registers a checked model. */
export function captureU0FileV4(filename:string,text=true):U0CapturedFileV4 {
 if(typeof filename!=='string'||!path.isAbsolute(filename)||path.normalize(filename)!==filename||/[\\\u0000-\u001f\u007f]/.test(filename)||filename.length>4096)fail('/file','normalized absolute path required');
 const chain=parents(filename),before=info(filename),limit=text?16777216:536870912;
 if(!before.isFile()||before.isSymbolicLink()||before.size<1n||before.size>BigInt(limit))fail(filename,'bounded nonempty regular file required');
 const key=physical(before),fd=openSync(filename,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),hash=createHash('sha256'),parts:Buffer[]=[];let bytes=0;
 try{if(physical(fstatSync(fd,{bigint:true}))!==key)fail(filename,'file changed while opening');const buffer=Buffer.alloc(65536);for(;;){const n=readSync(fd,buffer,0,buffer.length,null);if(!n)break;bytes+=n;if(bytes>limit)fail(filename,'file capture budget exceeded');hash.update(buffer.subarray(0,n));if(text)parts.push(Buffer.from(buffer.subarray(0,n)));}if(physical(fstatSync(fd,{bigint:true}))!==key)fail(filename,'file changed while reading');}finally{closeSync(fd);}
 const assertFile=()=>{if(physical(info(filename))!==key)fail(filename,'original bytes or physical closure changed');};
 const assertCurrent=()=>{assertFile();for(const row of chain)assertParent(row);};
 assertCurrent();if(BigInt(bytes)!==before.size)fail(filename,'captured size mismatch');
 let body:string|undefined;if(text)try{body=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(Buffer.concat(parts));}catch{return fail(filename,'fatal UTF-8 capture required');}
 const value=Object.freeze({path:filename,sha256:hash.digest('hex'),bytes,...(body===undefined?{}:{text:body}),assertCurrent});fileChecks.set(value,Object.freeze({parents:chain,assertFile}));return value;
}
function inventory(root:string):string[]{const result:string[]=[];const walk=(dir:string,depth:number)=>{if(depth>32)fail(dir,'closure depth exceeded');for(const name of readdirSync(dir).sort()){const file=path.join(dir,name),s=info(file);if(s.isSymbolicLink())fail(file,'closure symlink forbidden');if(s.isDirectory())walk(file,depth+1);else if(s.isFile())result.push(file);else fail(file,'unsupported closure member');if(result.length>10000)fail(root,'closure file budget exceeded');}};walk(root,0);return result;}
const moduleFile=fileURLToPath(import.meta.url),moduleAtImport=captureU0FileV4(moduleFile);
const loaded=new WeakMap<object,{files:readonly U0CapturedFileV4[];trees:readonly {root:string;files:readonly string[]}[];runtime:readonly U0RequestRuntimeFileV2[];disposed:boolean}>();
export interface LoadedU0ProfileV4 {readonly kind:'loaded-u0-profile-v4';readonly package_root:string;readonly profile:ProfilePackageV4;readonly manifest:U0CapturedFileV4;readonly basis:U0ResolvedNativeBasis;readonly node:U0CapturedFileV4}
export interface U0ProfileLoadOptionsV4 {readonly frontend_root?:string}
export async function loadBusinessU0ProfileV4(options:U0ProfileLoadOptionsV4={}):Promise<LoadedU0ProfileV4>{
 moduleAtImport.assertCurrent();if(!moduleFile.endsWith('/dist/profile-engine/loader-v4.js'))fail('/sdk','built public SDK required; source execution cannot resolve a native basis');
 const supplied=captureJson(options) as unknown as U0ProfileLoadOptionsV4;if(!supplied||typeof supplied!=='object'||Object.keys(supplied).some(key=>key!=='frontend_root')||supplied.frontend_root!==undefined&&typeof supplied.frontend_root!=='string')fail('/options','closed bootstrap options required');
 const root=path.resolve(path.dirname(moduleFile),'../..'),files:U0CapturedFileV4[]=[],trees:{root:string;files:readonly string[]}[]=[];
 const add=(filename:string,text=false)=>{const prior=files.find(file=>file.path===filename);if(prior)return prior;const file=captureU0FileV4(filename,text);files.push(file);if(files.reduce((n,f)=>n+f.bytes,0)>536870912)fail('/sdk','aggregate closure byte budget exceeded');return file;};
 const tree=(dir:string)=>{const names=inventory(dir);trees.push({root:dir,files:Object.freeze(names)});for(const name of names)add(name);};
 const packageFile=add(path.join(root,'package.json'),true),pkg=JSON.parse(packageFile.text!);if(pkg.name!=='@domainspec-v2/cli'||typeof pkg.version!=='string')fail('/sdk','actual Core package identity required');
 tree(path.join(root,'dist'));tree(path.join(root,'contracts'));
 const profileRoot=path.join(root,'profiles',U0_SUCCESSOR_DESCRIPTOR),manifest=add(path.join(profileRoot,'profile.json'),true),profile=validateProfilePackageV4(JSON.parse(manifest.text!));
 if(dataDigest(profile.assets)!==dataDigest(U0_RUNTIME_PINS_V4.assets)||dataDigest(profile.build)!==dataDigest(U0_RUNTIME_PINS_V4.build)||profile.build.node!==process.versions.node)fail('/profile','descriptor differs from compiled native/tool pins');
 const node=add(process.execPath),running=statSync('/proc/self/exe',{bigint:true}),onDisk=info(process.execPath);if(running.dev!==onDisk.dev||running.ino!==onDisk.ino)fail('/node','running Node differs from selected executable');
 if(supplied.frontend_root!==undefined){const frontend=path.resolve(supplied.frontend_root),frontPkg=add(path.join(frontend,'package.json'),true),p=JSON.parse(frontPkg.text!);if(!['@cyberalchemy/domainspec-cli-candidate','@cyberalchemy/alchlang'].includes(p.name))fail('/frontend','actual AlchLang package required');tree(path.join(frontend,'dist'));tree(path.join(frontend,'runtime-sources'));}
 const runtime:U0RequestRuntimeFileV2[]=[],artifacts:U0ResolvedArtifact[]=[];
 const resolved=(id:string,file:Pick<U0CapturedFileV4,'sha256'|'bytes'>,required:readonly string[],observed:readonly string[],version:string,origin:'registered-package'|'runtime-builtin'='registered-package')=>{
  if(required.some(name=>!observed.includes(name)))fail(id,'required actual export missing');
  const result=captureJson({kind:'resolved-native-artifact',requirement:{kind:'native-requirement',artifact_id:id,origin,version:{comparison:'exact',value:version},abi:U0_NATIVE_ABI,required_exports:required,supplying_runtime:'node',authority_effect:'none'},resolved_version:version,sha256:file.sha256,bytes:file.bytes,exports:observed,runtime_sha256:node.sha256,platform:process.platform,architecture:process.arch,authority_effect:'none'}) as unknown as U0ResolvedArtifact;artifacts.push(result);
 };
 for(const asset of profile.assets){const file=add(path.join(profileRoot,asset.path));if(file.sha256!==asset.sha256||file.bytes!==asset.bytes)fail(asset.path,'actual runtime differs from pinned bytes');const namespace=await import(pathToFileURL(file.path).href);for(const name of asset.exports)if(typeof namespace[name]!=='function')fail(asset.path,'actual callable export missing: '+name);resolved('u0:'+asset.role,file,asset.exports,Object.keys(namespace).sort(),pkg.version);runtime.push(Object.freeze({role:asset.role,basis_artifact_id:'u0:'+asset.role,artifact:Object.freeze({path:file.path,sha256:file.sha256,bytes:file.bytes})}));}
 const scalar=add(path.join(root,profile.scalar_producer.path));if(scalar.sha256!==profile.scalar_producer.sha256||scalar.bytes!==profile.scalar_producer.bytes)fail('/scalar','actual scalar producer differs from descriptor');
 const scalarModule=await import(pathToFileURL(scalar.path).href);if(typeof scalarModule.renderExactUInt64Support!=='function'||typeof scalarModule.renderExactUInt64Support()!=='string')fail('/scalar','actual scalar producer export required');resolved('u0:exact-uint64-source',scalar,['renderExactUInt64Support'],Object.keys(scalarModule).sort(),pkg.version);
 const sdkFiles=files.filter(file=>file!==node),sdk_sha256=dataDigest(sdkFiles.map(file=>({path:path.relative(root,file.path).split(path.sep).join('/'),sha256:file.sha256,bytes:file.bytes})).sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0));
 const publicApi=await import(pathToFileURL(path.join(root,'dist/index.js')).href);if(typeof publicApi.profileEngine?.createBusinessU0RuntimeV4!=='function')fail('/sdk','actual public bootstrap export missing');
 resolved('u0:public-sdk',{sha256:sdk_sha256,bytes:sdkFiles.reduce((n,f)=>n+f.bytes,0)},['createBusinessU0RuntimeV4'],Object.keys(publicApi.profileEngine).sort(),pkg.version);
 resolved('node',node,[],[],process.versions.node,'runtime-builtin');
 const body={kind:'resolved-u0-native-basis',abi:U0_NATIVE_ABI,descriptor:U0_SUCCESSOR_DESCRIPTOR,artifacts,configuration:profile.configuration,sdk_sha256,authority_effect:'none'},basis=captureJson({...body,basis_sha256:dataDigest(body)}) as unknown as U0ResolvedNativeBasis;
 const value=Object.freeze({kind:'loaded-u0-profile-v4' as const,package_root:root,profile,manifest,basis,node});loaded.set(value,{files:Object.freeze(files),trees:Object.freeze(trees),runtime:Object.freeze(runtime),disposed:false});assertLoadedU0ProfileV4Current(value);return value;
}
export function assertLoadedU0ProfileV4Current(value:LoadedU0ProfileV4):void {
 const state=value&&typeof value==='object'?loaded.get(value):undefined;if(!state||state.disposed)fail('/profile','original undisposed loaded profile required');moduleAtImport.assertCurrent();
 // Deduplicate common ancestors only within this synchronous physical pass.
 // Every captured file is checked before and after complete tree enumeration.
 // Parent paths are checked at both boundaries; nothing is cached between calls.
 const checks=state.files.map(file=>{const check=fileChecks.get(file);if(!check)fail('/profile','original captured file required');return check;});
 const directories=new Map<string,ParentV4>();for(const check of checks)for(const row of check.parents){const previous=directories.get(row.path);if(previous&&previous.identity!==row.identity)fail(row.path,'inconsistent captured ancestry');directories.set(row.path,row);}
 for(const row of directories.values())assertParent(row);for(const check of checks)check.assertFile();
 for(const tree of state.trees){const names=inventory(tree.root);if(names.length!==tree.files.length||names.some((name,index)=>name!==tree.files[index]))fail(tree.root,'closure inventory changed');}
 for(const check of checks)check.assertFile();for(const row of directories.values())assertParent(row);
}
export function loadedU0RuntimeFilesV4(value:LoadedU0ProfileV4):readonly U0RequestRuntimeFileV2[]{assertLoadedU0ProfileV4Current(value);return loaded.get(value)!.runtime;}
export function disposeLoadedU0ProfileV4(value:LoadedU0ProfileV4):void {assertLoadedU0ProfileV4Current(value);loaded.get(value)!.disposed=true;}
