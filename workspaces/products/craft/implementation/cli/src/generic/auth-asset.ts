/** Fixed selected-package asset custody. A self-consistent caller manifest is not authority.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
import {lstatSync,realpathSync,readFileSync,mkdirSync,chmodSync,openSync,closeSync,fstatSync,constants,type BigIntStats} from 'node:fs';
import {pinCoreImplementation,readCorePhysicalFile} from '../commerce/commerce-core-physical.js';
import {coreFreeze,CoreCommerceSourceError,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {dataDigest} from '../profile-engine/contracts.js';
const ext=path.extname(fileURLToPath(import.meta.url)),code=pinCoreImplementation(import.meta.url,['../commerce/commerce-core-physical'+ext]),root=fileURLToPath(new URL('../../profiles/generic-v1/',import.meta.url)),at={path:'generic-auth-asset',start:0,end:0};
const sha=(b:Uint8Array)=>createHash('sha256').update(b).digest('hex'),closed=(v:any,keys:readonly string[])=>{if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).sort().join(',')!==[...keys].sort().join(','))fail('InvalidContract',at,'closed selected native inventory required');};
interface FileIdentity {path:string;sha256:string;bytes:number;mode:number;physical:string}
const originalFileIdentities=new WeakMap<FileIdentity,Readonly<{parents:readonly (readonly string[])[];stamp:string}>>();
const file=(p:string,maximum=268435456):FileIdentity=>{if(!path.isAbsolute(p)||path.normalize(p)!==p||realpathSync(p)!==p)fail('StaleOwner',at,'physical selected asset required');let cursor=path.parse(p).root;const parents=[];for(const part of path.dirname(p).slice(cursor.length).split(path.sep).filter(Boolean)){cursor=path.join(cursor,part);const s=lstatSync(cursor,{bigint:true});if(s.isSymbolicLink()||!s.isDirectory())fail('StaleOwner',at,'physical asset ancestors required');parents.push([cursor,String(s.dev),String(s.ino),String(s.mode)]);}const before=lstatSync(p,{bigint:true}),stamp=(s:typeof before)=>[s.dev,s.ino,s.mode,s.size,s.mtimeNs,s.ctimeNs].join(':');if(!before.isFile()||before.isSymbolicLink()||before.size>BigInt(maximum))fail('StaleOwner',at,'bounded regular asset required');const b=readFileSync(p),after=lstatSync(p,{bigint:true});if(stamp(before)!==stamp(after)||b.length!==Number(after.size))fail('StaleOwner',at,'asset changed while reading');const pin={path:p,sha256:sha(b),bytes:b.length,mode:Number(after.mode&0o777n),physical:dataDigest({parents,stamp:stamp(after)})};originalFileIdentities.set(pin,{parents,stamp:stamp(after)});return pin;};
// Initial file() capture hashes every byte. Ordinary writers cannot restore a
// file's ctime; subsequent checks retain exact inode/mode/size/time and parent
// custody instead of repeatedly allocating and hashing the native libraries.
// Parent observations are local to one synchronous phase, never an await/call.
type AssetParent=readonly [string,string,string,string];
function assetParents(file:string,memo:Map<string,AssetParent>):readonly AssetParent[]{
 let cursor=path.parse(file).root;const result:AssetParent[]=[];
 for(const part of path.dirname(file).slice(cursor.length).split(path.sep).filter(Boolean)){
  cursor=path.join(cursor,part);let row=memo.get(cursor);
  if(!row){const stat=lstatSync(cursor,{bigint:true});if(!stat.isDirectory()||stat.isSymbolicLink())fail('StaleOwner',at,'physical selected asset ancestors required');row=[cursor,String(stat.dev),String(stat.ino),String(stat.mode)];memo.set(cursor,row);}
  result.push(row);
 }
 return result;
}
const assetStamp=(stat:BigIntStats)=>[stat.dev,stat.ino,stat.mode,stat.size,stat.mtimeNs,stat.ctimeNs].join(':');
function assertAssetFileIdentity(pin:FileIdentity,memo:Map<string,AssetParent>,anchor:boolean):void{
 const original=originalFileIdentities.get(pin);if(!original)fail('ForeignOwner',at,'original selected file capture required');
 const parents=assetParents(pin.path,memo),before=lstatSync(pin.path,{bigint:true});
 const sameParents=parents.length===original!.parents.length&&parents.every((row,i)=>row.length===original!.parents[i]!.length&&row.every((cell,j)=>cell===original!.parents[i]![j]));
 if(!before.isFile()||before.isSymbolicLink()||Number(before.size)!==pin.bytes||Number(before.mode&0o777n)!==pin.mode||!sameParents||assetStamp(before)!==original!.stamp)
  fail('StaleOwner',at,'selected native file changed');
 if(anchor){const fd=openSync(pin.path,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
  try{if(assetStamp(fstatSync(fd,{bigint:true}))!==assetStamp(before))fail('StaleOwner',at,'selected native file changed while opening');}
  finally{closeSync(fd);}
  if(assetStamp(lstatSync(pin.path,{bigint:true}))!==assetStamp(before))fail('StaleOwner',at,'selected native file changed while checking');
 }
}
function assertSelectedAssetFilesCurrent(files:readonly FileIdentity[]):void{
 const before=new Map<string,AssetParent>();for(const pin of files)assertAssetFileIdentity(pin,before,true);
 // Fresh parent and file observations close the whole file pass, including a
 // branch ancestor replaced after a leaf's descriptor was checked.
 const after=new Map<string,AssetParent>();for(const pin of files)assertAssetFileIdentity(pin,after,false);
}
export interface GenericSelectedAuthAsset {readonly kind:'original-generic-selected-auth-asset/v1-candidate'}
interface State {directory:string;directory_identity:string;binary:string;files:readonly FileIdentity[];manifest:Readonly<Record<string,unknown>>;migration:string;current:()=>void}
const assets=new WeakMap<object,State>();
/** Internal shared native producer consumes only an original registry member. */
export function assertGenericSelectedAuthAsset(h:GenericSelectedAuthAsset):State{const r=h&&typeof h==='object'?assets.get(h):undefined;if(!r)fail('ForeignOwner',at,'original selected native asset required');r.current();return r;}
export function loadOriginalGenericAuthAsset(ownedDirectory:string):GenericSelectedAuthAsset{try{return captureAsset(ownedDirectory);}catch(error){if(error instanceof CoreCommerceSourceError)throw error;return fail('StaleOwner',at,'selected native inventory/files unavailable or malformed');}}
function captureAsset(ownedDirectory:string):GenericSelectedAuthAsset{
 code.assertCurrent();if(typeof ownedDirectory!=='string'||!path.isAbsolute(ownedDirectory)||path.normalize(ownedDirectory)!==ownedDirectory||realpathSync(path.dirname(ownedDirectory))!==path.dirname(ownedDirectory))fail('InvalidContract',at,'fresh physical native work directory required');
 const familyFile=path.join(root,'family.json'),familyCapture=readCorePhysicalFile(familyFile),family=JSON.parse(familyCapture.text);closed(family,['schema_version','id','asset']);if(family.schema_version!=='craft.generic-native-family/v1-candidate'||family.id!=='generic-keyed-sqlite-auth/v1-candidate')fail('InvalidContract',at,'fixed selected native family required');const asset=family.asset;closed(asset,['id','binary','manifest','migration','platform','native_abi','auth_route_template','build_input_sha256','libraries']);
 if(asset.id!=='auth-foundation-ready'||asset.platform!=='linux-x64-glibc-2.43'||asset.native_abi!=='craft.commerce-auth-ready-bridge/v1-candidate'||asset.auth_route_template!=='commerce:{logical_entry_id}'||process.platform!=='linux'||process.arch!=='x64'||(process.report.getReport() as any).header.glibcVersionRuntime!=='2.43')fail('UnsupportedCapability',at,'selected native platform/ABI mismatch');
 const files:FileIdentity[]=[file(familyFile,1048576)];if(files[0]!.mode!==0o644)fail('StaleOwner',at,'family mode mismatch');
 for(const [key,relative,mode]of [['binary','assets/auth/craft-commerce-auth-ready-bridge-v1',0o755],['manifest','assets/auth/manifest.json',0o644],['migration','assets/auth/0002_auth_service_epoch.sql',0o644]] as const){const f=asset[key];closed(f,['path','sha256','bytes','mode']);if(f.path!==relative||f.mode!==mode)fail('InvalidContract',at,'fixed selected native path/mode required');const pin=file(path.join(root,relative));if(pin.sha256!==f.sha256||pin.bytes!==f.bytes||pin.mode!==mode)fail('StaleOwner',at,'asset differs from trusted family inventory');files.push(pin);}
 const manifestCapture=readCorePhysicalFile(path.join(root,asset.manifest.path)),manifest=JSON.parse(manifestCapture.text);closed(manifest,['schema_version','platform','native_abi','auth_route_template','binary','libraries','build','qualification']);closed(manifest.binary,['path','sha256','bytes','mode']);closed(manifest.build,['input_sha256','toolchain_receipt_sha256','dependency_metadata_sha256','include_closure_sha256','repository_launcher_sha256','command']);
 if(manifest.schema_version!=='craft.generic-auth-asset/v1-candidate'||manifest.platform!==asset.platform||manifest.native_abi!==asset.native_abi||manifest.auth_route_template!==asset.auth_route_template||manifest.binary.path!=='craft-commerce-auth-ready-bridge-v1'||manifest.binary.sha256!==asset.binary.sha256||manifest.binary.bytes!==asset.binary.bytes||manifest.binary.mode!==asset.binary.mode||manifest.build.input_sha256!==asset.build_input_sha256||dataDigest(manifest.libraries)!==dataDigest(asset.libraries))fail('InvalidContract',at,'manifest cannot override selected native inventory');
 if(!Array.isArray(asset.libraries)||asset.libraries.length<1||asset.libraries.length>32)fail('InvalidContract',at,'bounded exact native libraries required');const seen=new Set<string>();for(const lib of asset.libraries){closed(lib,['path','sha256','bytes']);if(seen.has(lib.path))fail('InvalidContract',at,'unique native library required');seen.add(lib.path);const p=file(lib.path);if(p.sha256!==lib.sha256||p.bytes!==lib.bytes)fail('StaleOwner',at,'selected host library mismatch');files.push(p);}
 if(readFileSync(files[1]!.path).subarray(0,4).toString('hex')!=='7f454c46')fail('InvalidContract',at,'actual selected ELF required');
 mkdirSync(ownedDirectory,{mode:0o700});chmodSync(ownedDirectory,0o700);const ds=lstatSync(ownedDirectory,{bigint:true}),directory_identity=[ds.dev,ds.ino,ds.mode].join(':'),h=Object.freeze({kind:'original-generic-selected-auth-asset/v1-candidate' as const});
 const current=()=>{code.assertCurrent();const d=lstatSync(ownedDirectory,{bigint:true});if(!d.isDirectory()||d.isSymbolicLink()||realpathSync(ownedDirectory)!==ownedDirectory||[d.dev,d.ino,d.mode].join(':')!==directory_identity)fail('StaleOwner',at,'native work directory changed');if(readCorePhysicalFile(familyFile).fingerprint!==familyCapture.fingerprint)fail('StaleOwner',at,'selected native family changed');assertSelectedAssetFilesCurrent(files);};
 assets.set(h,Object.freeze({directory:ownedDirectory,directory_identity,binary:files[1]!.path,files:coreFreeze(files),manifest:coreFreeze({family,asset_manifest:manifest,identity_sha256:dataDigest({family,manifest}),authority_effect:'none'}),migration:files[3]!.path,current}));current();return h;
}
