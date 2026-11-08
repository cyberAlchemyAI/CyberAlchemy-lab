/** Bounded physical-file custody used by the commerce source-stage owners.
 * Exclusive writes preserve failure residue; no pathname cleanup can delete a
 * competing writer's replacement. Open Questions: docs/COMMERCE-OWNERS.md. */
import {closeSync,constants,fchmodSync,fstatSync,lstatSync,openSync,readSync,writeSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSha256,coreSourceFail as fail,CoreCommerceSourceError} from './commerce-core-syntax.js';
export interface CorePhysicalFile {readonly file:Readonly<{path:string;sha256:string;bytes:number}>;readonly text:string;readonly fingerprint:string}
const at=(file:string)=>({path:file,start:0,end:0});
function absolute(file:string):void {if(typeof file!=='string'||file.length>4096||!path.isAbsolute(file)||path.normalize(file)!==file||file.endsWith('/')||/[\\\u0000-\u001f\u007f]/.test(file))fail('InvalidContract',at('file'),'normalized absolute regular file path required');}
type PhysicalParent=Readonly<{path:string;device:string;inode:string}>;
function parents(directory:string,memo?:Map<string,PhysicalParent>):readonly PhysicalParent[]{
 let cursor=path.parse(directory).root;const rows:PhysicalParent[]=[];
 for(const part of ['',...directory.slice(cursor.length).split(path.sep).filter(Boolean)]){
  if(part)cursor=path.join(cursor,part);
  let row=memo?.get(cursor);
  if(!row){
   const stat=lstatSync(cursor,{bigint:true});
   if(!stat.isDirectory()||stat.isSymbolicLink())fail('StaleOwner',at(directory),'original nonsymlink parent directories required');
   row={path:cursor,device:String(stat.dev),inode:String(stat.ino)};memo?.set(cursor,row);
  }
  rows.push(row);
 }
 return rows;
}
const stamp=(s:BigIntStats)=>[s.dev,s.ino,s.size,s.mode,s.mtimeNs,s.ctimeNs].map(String);
function sameParents(left:ReturnType<typeof parents>,right:ReturnType<typeof parents>):boolean {
 if(left.length!==right.length)return false;for(let i=0;i<left.length;i++){const a=left[i]!,b=right[i]!;if(a.path!==b.path||a.device!==b.device||a.inode!==b.inode)return false;}return true;
}
function sameStamp(left:readonly string[],right:readonly string[]):boolean {
 if(left.length!==right.length)return false;for(let i=0;i<left.length;i++)if(left[i]!==right[i])return false;return true;
}
function openedParent(file:string){absolute(file);const directory=path.dirname(file),before=parents(directory),fd=openSync(directory,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW|constants.O_NONBLOCK),same=()=>{const stat=fstatSync(fd,{bigint:true}),last=before.at(-1)!;if(String(stat.dev)!==last.device||String(stat.ino)!==last.inode||!sameParents(parents(directory),before))fail('StaleOwner',at(file),'original parent path changed');};try{same();return {fd,anchored:`/proc/self/fd/${fd}/${path.basename(file)}`,before,same};}catch(error){closeSync(fd);throw error;}}
/**
 * Check all files through directory FDs. Shared ancestors are sampled once
 * before opening and once again after every file has been checked. These
 * phase-local maps are discarded on return; no filesystem fact is cached
 * across owner checks, effects, awaits or caller callbacks.
 */
function assertCurrentIdentities(rows:readonly {file:string;identity:{parents:ReturnType<typeof parents>;physical:readonly string[]}}[]):void{
 const directories=new Map<string,{fd:number;before:ReturnType<typeof parents>}>();
 const beforeMemo=new Map<string,PhysicalParent>();
 try{
  for(const row of rows){
   absolute(row.file);
   const directory=path.dirname(row.file);
   let parent=directories.get(directory);
   if(!parent){
    const before=parents(directory,beforeMemo);
    if(!sameParents(before,row.identity.parents))fail('StaleOwner',at(row.file),'original parent identity changed');
    const fd=openSync(directory,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
    parent={fd,before};directories.set(directory,parent);
    const opened=fstatSync(fd,{bigint:true}),last=before.at(-1)!;
    if(String(opened.dev)!==last.device||String(opened.ino)!==last.inode)
     fail('StaleOwner',at(row.file),'original anchored directory changed while opening');
   }
   if(!sameParents(parent.before,row.identity.parents))fail('StaleOwner',at(row.file),'original parent identity changed');
   const anchored='/proc/self/fd/'+parent.fd+'/'+path.basename(row.file);
   const stat=lstatSync(anchored,{bigint:true});
   if(!stat.isFile()||stat.isSymbolicLink()||!sameStamp(stamp(stat),row.identity.physical))
    fail('StaleOwner',at(row.file),'original file identity changed');
  }
  const afterMemo=new Map<string,PhysicalParent>();
  for(const [directory,parent]of directories){
   const actual=fstatSync(parent.fd,{bigint:true}),last=parent.before.at(-1)!;
   if(String(actual.dev)!==last.device||String(actual.ino)!==last.inode||
    !sameParents(parents(directory,afterMemo),parent.before))
    fail('StaleOwner',at(directory),'original parent path changed during file checks');
  }
 }finally{for(const parent of directories.values())closeSync(parent.fd);}
}
type IdentityRow=Parameters<typeof assertCurrentIdentities>[0][number];
let identityPhase:Map<string,IdentityRow>|undefined;
/** Internal synchronous source/plan validation only. It may not surround an
 * await, business evaluation, native callback or effect. Nested pins share the
 * first physical sample; all sampled files are checked again before returning.
 * No file fact is cached between calls or after a caller callback can run. */
export function withCorePhysicalIdentityPhase<T>(work:()=>T):T{
 if(identityPhase)return work();
 const sampled=new Map<string,IdentityRow>();identityPhase=sampled;
 try{const result=work();if(result&&typeof result==='object'&&'then' in result)fail('InvalidContract',at('physical-phase'),'synchronous source validation required');return result;}
 finally{identityPhase=undefined;assertCurrentIdentities([...sampled.values()]);}
}
function assertPinnedIdentities(rows:readonly IdentityRow[]){
 if(!identityPhase){assertCurrentIdentities(rows);return;}
 const fresh:IdentityRow[]=[];
 for(const row of rows){const prior=identityPhase.get(row.file);if(prior){if(!sameParents(prior.identity.parents,row.identity.parents)||!sameStamp(prior.identity.physical,row.identity.physical))fail('StaleOwner',at(row.file),'conflicting original physical captures');}else fresh.push(row);}
 assertCurrentIdentities(fresh);for(const row of fresh)identityPhase.set(row.file,row);
}
function readAt(file:string,parent:ReturnType<typeof openedParent>,maximum:number):CorePhysicalFile {
 parent.same();const before=lstatSync(parent.anchored,{bigint:true});if(!before.isFile()||before.isSymbolicLink())fail('StaleOwner',at(file),'original nonsymlink regular file required');if(before.size<0n||before.size>BigInt(maximum))fail('ResourceLimit',at(file),'physical file byte budget');
 const fd=openSync(parent.anchored,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),chunks:Buffer[]=[];let bytes=0;
 try{if(!sameStamp(stamp(fstatSync(fd,{bigint:true})),stamp(before)))fail('StaleOwner',at(file),'file changed while opening');for(;;){const buffer=Buffer.alloc(65536),n=readSync(fd,buffer,0,buffer.length,null);if(!n)break;bytes+=n;if(bytes>maximum)fail('ResourceLimit',at(file),'physical read budget');chunks.push(buffer.subarray(0,n));}if(!sameStamp(stamp(fstatSync(fd,{bigint:true})),stamp(before)))fail('StaleOwner',at(file),'file changed while reading');}finally{closeSync(fd);}
 parent.same();if(!sameStamp(stamp(lstatSync(parent.anchored,{bigint:true})),stamp(before))||bytes!==Number(before.size))fail('StaleOwner',at(file),'original file replaced during capture');const buffer=Buffer.concat(chunks);let text:string;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(buffer);}catch{return fail('InvalidContract',at(file),'strict UTF8 physical file required');}
 const sha256=coreSha256(buffer);return coreFreeze({file:{path:file,sha256,bytes},text,fingerprint:dataDigest({file,parents:parent.before,physical:stamp(before),sha256})});
}
export function readCorePhysicalFile(file:string,maximum=1048576):CorePhysicalFile {
 if(!Number.isSafeInteger(maximum)||maximum<1||maximum>16777216)fail('InvalidContract',at('file'),'finite physical read limit required');try{const parent=openedParent(file);try{return readAt(file,parent,maximum);}finally{closeSync(parent.fd);}}catch(error){if(error instanceof CoreCommerceSourceError)throw error;return fail('StaleOwner',at('file'),'original physical file/parent unavailable or changed');}
}
export function writeCoreExclusiveFile(file:string,text:string):CorePhysicalFile {
 if(typeof text!=='string')fail('InvalidContract',at('file'),'explicit decision text required');const bytes=Buffer.from(text);if(bytes.length>1048576||bytes.toString('utf8')!==text)fail('InvalidContract',at('file'),'bounded strict UTF8 decision required');let parent:ReturnType<typeof openedParent>;try{parent=openedParent(file);}catch(error){if(error instanceof CoreCommerceSourceError)throw error;return fail('StaleOwner',at('file'),'original decision parent unavailable');}let fd:number|undefined;
 try{
  try{fd=openSync(parent.anchored,constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW|constants.O_NONBLOCK,0o600);}catch{return fail('InvalidContract',at(file),'exclusive new decision destination required;occupied files remain unchanged');}
  const created=fstatSync(fd,{bigint:true});if(!created.isFile())fail('StaleOwner',at(file),'new decision must be regular');fchmodSync(fd,0o600);parent.same();let offset=0;while(offset<bytes.length){const n=writeSync(fd,bytes,offset,bytes.length-offset,null);if(n<=0)fail('StaleOwner',at(file),'complete exclusive decision write required');offset+=n;}
  const after=fstatSync(fd,{bigint:true});if(after.dev!==created.dev||after.ino!==created.ino||after.size!==BigInt(bytes.length)||(after.mode&0o777n)!==0o600n)fail('StaleOwner',at(file),'written decision physical identity or private mode changed');closeSync(fd);fd=undefined;parent.same();const captured=readAt(file,parent,1048576),current=lstatSync(parent.anchored,{bigint:true});if(current.dev!==created.dev||current.ino!==created.ino||captured.file.sha256!==coreSha256(bytes))fail('StaleOwner',at(file),'exclusive decision replaced before capture');return captured;
 }finally{try{if(fd!==undefined)closeSync(fd);}finally{closeSync(parent.fd);}}
}
/** Pins actual owning code/contracts at module load. A new factory cannot
 * silently adopt replaced code already executing in this process. */
export function pinCoreImplementation(moduleUrl:string,relativeFiles:readonly string[]){
 const files=[fileURLToPath(moduleUrl),...relativeFiles.map(f=>fileURLToPath(new URL(f,moduleUrl)))];
 // A file's ctime cannot be restored by an ordinary writer. Rechecking its
 // anchored metadata and parent identity is therefore sufficient after the
 // initial full read, and avoids rehashing the same implementation files at
 // every nested runtime custody check.
 const identity=(file:string)=>{const parent=openedParent(file);try{const stat=lstatSync(parent.anchored,{bigint:true});if(!stat.isFile()||stat.isSymbolicLink())fail('StaleOwner',at(file),'original implementation file required');parent.same();return {parents:parent.before,physical:stamp(stat)};}finally{closeSync(parent.fd);}};
 const captured=files.map(file=>{const before=identity(file),read=readCorePhysicalFile(file),after=identity(file);if(!sameParents(before.parents,after.parents)||!sameStamp(before.physical,after.physical))fail('StaleOwner',at(file),'implementation changed during capture');return {file,fingerprint:read.fingerprint,identity:after};});
 const loaded=dataDigest(captured.map(({file,fingerprint})=>({path:file,fingerprint})));
 return Object.freeze({sha256:loaded,assertCurrent(){try{assertPinnedIdentities(captured);}catch{return fail('StaleOwner',at('implementation'),'original commerce implementation/contracts unavailable or replaced');}}});
}

/** Capture full file hashes once, then retain exact anchored physical identity.
 * A later ordinary write, including one that restores mtime, changes ctime. */
export function pinCorePhysicalCaptures(files:readonly CorePhysicalFile[]){
 const identity=(file:string)=>{const parent=openedParent(file);try{const stat=lstatSync(parent.anchored,{bigint:true});if(!stat.isFile()||stat.isSymbolicLink())fail('StaleOwner',at(file),'original captured file required');parent.same();return {parents:parent.before,physical:stamp(stat)};}finally{closeSync(parent.fd);}};
 // Preserve an explicitly bounded large artifact capture during the confirming
 // read. Ordinary source reads still use their original 1 MiB default; the
 // reader enforces its absolute 16 MiB ceiling here as everywhere else.
 const rows=files.map(captured=>{const before=identity(captured.file.path),actual=readCorePhysicalFile(captured.file.path,Math.max(1048576,captured.file.bytes)),after=identity(captured.file.path);if(actual.fingerprint!==captured.fingerprint||!sameParents(before.parents,after.parents)||!sameStamp(before.physical,after.physical))fail('StaleOwner',at(captured.file.path),'captured file changed during pin');return {file:captured.file.path,identity:after};});
 return Object.freeze({assertCurrent(){try{assertPinnedIdentities(rows);}catch{return fail('StaleOwner',at('physical-capture'),'captured file unavailable or replaced');}}});
}
