/** Explicit operator-selected native profile packages. This is trusted native
 * code with original host ports, not a sandbox or a caller plugin executor.
 * Fixture-only C03 loading remains unchanged.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import path from 'node:path';
import {lstatSync,readdirSync,readFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {registerHooks} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {coreFreeze,coreSha256,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import type {GenericCapabilityRealizationV1} from './capability-data-v1.js';
const at={path:'native-profile-resource',start:0,end:0};
export interface GenericNativeProfileArtifact {readonly kind:'original-native-profile-artifact/v1'}
type File={path:string;sha256:string;bytes:number;identity:string};
type Row={root:string;files:File[];sha256:string;manifest:any};
const artifacts=new WeakMap<object,Row>();
function inventory(root:string,expected?:ReadonlyMap<string,File>):File[]{const files:File[]=[];let total=0,dirs=0;const walk=(relative:string,depth:number)=>{
 if(++dirs>1024||depth>20)fail('ResourceLimit',at,'finite native package directories');const dir=path.join(root,relative),s=lstatSync(dir);if(!s.isDirectory()||s.isSymbolicLink())fail('InvalidContract',at,'original nonsymlink native package');
 for(const name of readdirSync(dir).sort()){if(name==='node_modules'||!name||/[\\%?#\u0000-\u001f]/.test(name))fail('UnsupportedCapability',at,'dependency packages belong in the separately installed locked closure');const relativePath=relative?relative+'/'+name:name,physical=path.join(root,relativePath),stat=lstatSync(physical,{bigint:true});if(stat.isSymbolicLink())fail('InvalidContract',at,'native package symlink rejected');if(stat.isDirectory()){walk(relativePath,depth+1);continue;}if(!stat.isFile()||stat.nlink!==1n||stat.size>16777216n)fail('InvalidContract',at,'regular bounded native package member');const identity=[stat.dev,stat.ino,stat.size,stat.mtimeNs,stat.ctimeNs,stat.mode].join(':'),prior=expected?.get(relativePath);if(expected&&(!prior||prior.identity!==identity))fail('StaleOwner',at,'original native package file identity changed');const bytes=expected?undefined:readFileSync(physical),length=Number(stat.size);total+=length;if(total>67108864||files.length>=1024)fail('ResourceLimit',at,'native package byte/file bound');const after=lstatSync(physical,{bigint:true});if(identity!==[after.dev,after.ino,after.size,after.mtimeNs,after.ctimeNs,after.mode].join(':'))fail('StaleOwner',at,'native package changed while captured');files.push({path:relativePath,sha256:prior?.sha256??coreSha256(bytes!),bytes:length,identity});}
 };walk('',0);return files.sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0);}
function tuple(files:File[]){return files.map(({path,sha256,bytes})=>({path,sha256,bytes}));}
function row(h:GenericNativeProfileArtifact){const r=h&&typeof h==='object'?artifacts.get(h):undefined;if(!r)fail('ForeignOwner',at,'original captured installed native package');const current=inventory(r.root,new Map(r.files.map(f=>[f.path,f])));if(dataDigest(current)!==dataDigest(r.files))fail('StaleOwner',at,'original native package bytes/identity changed');return r;}
/** Retain full byte capture, then check exact file inventory and ctime-bearing
 * physical identities at every use. Ordinary writes cannot restore ctime; actual
 * module loading additionally rechecks the selected bytes. No cross-call timeout
 * cache or stale file-fact reuse is introduced.
 * The same portable whole-package digest as C03; no ignored own-package files.
 * Dependencies are installed separately and retain their own package/lock identity. */
export function captureGenericNativeProfileArtifact(packageRoot:string){if(!path.isAbsolute(packageRoot)||path.normalize(packageRoot)!==packageRoot)fail('InvalidContract',at,'absolute installed native package root');const files=inventory(packageRoot),p=files.find(f=>f.path==='package.json');if(!p)fail('InvalidContract',at,'native package manifest');const manifest=JSON.parse(readFileSync(path.join(packageRoot,'package.json'),'utf8'));captureJson(manifest);const handle=Object.freeze({kind:'original-native-profile-artifact/v1' as const});artifacts.set(handle,{root:packageRoot,files,sha256:dataDigest({schema_version:'craft.native-capability-package-bytes/v1',files:tuple(files)}),manifest});return handle;}
export function inspectGenericNativeProfileArtifact(h:GenericNativeProfileArtifact){const r=row(h);return coreFreeze({name:r.manifest.name,version:r.manifest.version,sha256:r.sha256,files:tuple(r.files),license:r.manifest.license??'UNLICENSED'});}
export function assertGenericNativeProfileArtifact(h:GenericNativeProfileArtifact){row(h);}
export interface GenericNativeProfileFactorySelection {readonly package:string;readonly version:string;readonly export:string;readonly sha256:string;readonly factory:string}
/** Exact original-artifact loader for admitted native factory ABIs. The generic
 * capability loader below retains its createCapabilityResource requirement. */
export async function loadGenericNativeProfileFactory(h:GenericNativeProfileArtifact,selected:GenericNativeProfileFactorySelection){const r=row(h),s=captureJson(selected) as unknown as GenericNativeProfileFactorySelection;if(!s||typeof s!=='object'||Object.keys(s).sort().join(',')!=='export,factory,package,sha256,version'||typeof s.factory!=='string'||!/^[A-Za-z_][A-Za-z0-9_]{0,127}$/.test(s.factory))fail('InvalidContract',at,'exact native factory selection required');if(r.manifest.name!==s.package||r.manifest.version!==s.version||r.sha256!==s.sha256)fail('InvalidContract',at,'exact checked native package name/version/bytes');
 let entry=r.manifest.exports?.[s.export];if(s.export==='.'&&typeof r.manifest.exports==='string')entry=r.manifest.exports;if(entry&&typeof entry==='object')entry=entry.import;
 if(typeof entry!=='string'||!entry.startsWith('./')||entry.slice(2).split('/').some((x:string)=>!x||x==='..'||x==='.')||!r.files.some(f=>f.path===entry.slice(2)))fail('InvalidContract',at,'exact installed package export');
 const nonce=randomUUID(),inside=(file:string)=>file===r.root||file.startsWith(r.root+path.sep),captures=new Map(r.files.map(f=>[path.join(r.root,f.path),f]));
 const hooks=registerHooks({resolve(specifier,context,next){const result=next(specifier,context);if(result.url.startsWith('file:')){const u=new URL(result.url),file=fileURLToPath(u);if(inside(file)&&/\.(?:mjs|js)$/.test(file)){if(!captures.has(file))fail('UnsupportedCapability',at,'unselected native module');u.searchParams.set('craft-native-profile',nonce);return {...result,url:u.href};}}return result;},load(url,context,next){if(url.startsWith('file:')){const u=new URL(url);if(u.searchParams.get('craft-native-profile')===nonce){const f=captures.get(fileURLToPath(u));if(!f)fail('UnsupportedCapability',at,'native module outside captured package');row(h);const bytes=readFileSync(path.join(r.root,f.path));if(coreSha256(bytes)!==f.sha256)fail('StaleOwner',at,'native module changed');return {format:'module',source:bytes,shortCircuit:true};}}return next(url,context);}});
 try{const u=pathToFileURL(path.join(r.root,entry.slice(2)));u.searchParams.set('craft-native-profile',nonce);const namespace=await import(u.href);row(h);if(!Object.hasOwn(namespace,s.factory)||typeof namespace[s.factory]!=='function')fail('UnsupportedCapability',at,'selected native profile factory required');let closed=false;return {namespace,factory:namespace[s.factory] as (...args:unknown[])=>unknown,assertCurrent:()=>{if(closed)fail('DisposedOwner',at,'native factory owner closed');row(h);},close:()=>{if(!closed){closed=true;hooks.deregister();}}};}catch(e){hooks.deregister();throw e;}
}

export async function loadGenericNativeProfileModule(h:GenericNativeProfileArtifact,selected:GenericCapabilityRealizationV1){return loadGenericNativeProfileFactory(h,{...selected.implementation,factory:'createCapabilityResource'});}
