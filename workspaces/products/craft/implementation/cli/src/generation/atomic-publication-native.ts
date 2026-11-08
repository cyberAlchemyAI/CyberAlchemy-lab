import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {ATOMIC_NATIVE} from './atomic-publication-native.generated.js';

interface AtomicNative {renameNoReplace(parentFd:number,sourceLeaf:string,targetLeaf:string):void;}
let cached:Readonly<AtomicNative>|undefined;
function fail(code:string,message:string):never {throw Object.assign(new Error(message),{code});}
function same(a:fs.BigIntStats,b:fs.BigIntStats):boolean {return a.dev===b.dev&&a.ino===b.ino;}

/** Internal lazy adapter. Importing the compiler never extracts or loads native code. */
export function loadAtomicPublicationNative():Readonly<AtomicNative> {
 // Native syscalls cannot enforce Node's path-level permission sandbox. Never bypass it.
 if(process.permission)fail('DS_NATIVE_PERMISSION','Output writing is unavailable under Node permission mode. Planning and artifact-currentness inspection remain available; use a normal CLI process for output writing. No permissions were changed.');
 if(cached)return cached;
 if(process.platform!==ATOMIC_NATIVE.build.platform||process.arch!==ATOMIC_NATIVE.build.arch)
  fail('DS_NATIVE_PLATFORM','atomic publication requires Linux x64');
 const bytes=Buffer.from(ATOMIC_NATIVE.base64,'base64');
 if(bytes.length!==ATOMIC_NATIVE.size_bytes||crypto.createHash('sha256').update(bytes).digest('hex')!==ATOMIC_NATIVE.sha256)
  fail('DS_NATIVE_INTEGRITY','atomic publication payload integrity mismatch');
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'domainspec-native-load-'));
 let directoryFd:number|undefined,fileFd:number|undefined,directoryIdentity:fs.BigIntStats|undefined;
 let fileIdentity:fs.BigIntStats|undefined,native:AtomicNative|undefined;
 try{
  directoryIdentity=fs.lstatSync(directory,{bigint:true});
  directoryFd=fs.openSync(directory,fs.constants.O_RDONLY|fs.constants.O_DIRECTORY|fs.constants.O_NOFOLLOW);
  if(!same(directoryIdentity,fs.fstatSync(directoryFd,{bigint:true})))fail('DS_NATIVE_IDENTITY','native extraction directory changed');
  const file=`/proc/self/fd/${directoryFd}/primitive.node`;
  fileFd=fs.openSync(file,fs.constants.O_RDWR|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);
  fileIdentity=fs.fstatSync(fileFd,{bigint:true});
  fs.writeFileSync(fileFd,bytes);
  const observed=Buffer.alloc(bytes.length+1);
  const count=fs.readSync(fileFd,observed,0,observed.length,0);
  if(count!==bytes.length||!observed.subarray(0,count).equals(bytes))fail('DS_NATIVE_INTEGRITY','native extraction integrity mismatch');
  if(!same(fileIdentity,fs.lstatSync(file,{bigint:true})))fail('DS_NATIVE_IDENTITY','native extraction file changed');
  fs.unlinkSync(file);fileIdentity=undefined;
  // dlopen the held, unlinked inode, not a mutable extraction pathname.
  const module={exports:{}};
  process.dlopen(module,`/proc/self/fd/${fileFd}`);
  native=module.exports as AtomicNative;
  if(typeof native.renameNoReplace!=='function')fail('DS_NATIVE_API','native atomic rename export is missing');
 }finally{
  try{
   // Never recursively delete a directory that could contain foreign files.
   if(directoryFd!==undefined&&fileIdentity){
    const file=`/proc/self/fd/${directoryFd}/primitive.node`;
    try{if(same(fileIdentity,fs.lstatSync(file,{bigint:true})))fs.unlinkSync(file);}
    catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
   }
  }finally{
   try{if(fileFd!==undefined)fs.closeSync(fileFd);}
   finally{if(directoryFd!==undefined)fs.closeSync(directoryFd);}
  }
  if(directoryIdentity){
   try{if(same(directoryIdentity,fs.lstatSync(directory,{bigint:true})))fs.rmdirSync(directory);}
   catch(error){if(!['ENOENT','ENOTEMPTY'].includes((error as NodeJS.ErrnoException).code??''))throw error;}
  }
 }
 cached=Object.freeze(native!);
 return cached;
}
