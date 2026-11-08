import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {loadAtomicPublicationNative} from './atomic-publication-native.js';

type Identity=fs.BigIntStats;
type Directory={fd:number,parentFd:number,name:string,identity:Identity};
type File={parentFd:number,name:string,identity:Identity};
const same=(a:Identity,b:Identity)=>a.dev===b.dev&&a.ino===b.ino;
const at=(fd:number,name:string)=>`/proc/self/fd/${fd}/${name}`;
function fail(code:string,message:string):never {throw Object.assign(new Error(message),{code});}
function inspect(file:string):Identity|undefined {
 try{return fs.lstatSync(file,{bigint:true});}catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')return undefined;throw error;}
}
function relative(value:string):string[] {
 const parts=value.split('/');
 if(path.posix.normalize(value)!==value||value.includes('\\')||parts.some(p=>!p||p==='.'||p==='..'||p.includes('\0')))
  fail('DS_ATOMIC_PATH','artifact path must be relative, normalized and contained');
 return parts;
}

/** Private sibling stage, exclusive writes, and one kernel no-replace publication. */
export function publishAtomicDirectory(target:string,artifacts:readonly {relative_path:string;content:string}[],prefix:string,beforeCommit?:(stagePath:string)=>void,options?:Readonly<{preserveFailedStage?:boolean}>):void {
 if(!path.isAbsolute(target)||path.resolve(target)!==target||target===path.parse(target).root)
  fail('DS_ATOMIC_PATH','normalized non-root absolute target required');
 if(!/^\.domainspec-[a-z-]+$/.test(prefix))fail('DS_ATOMIC_PATH','invalid private staging prefix');
 const paths=new Set<string>();
 for(const artifact of artifacts){relative(artifact.relative_path);if(paths.has(artifact.relative_path))fail('DS_ATOMIC_PATH','duplicate artifact path');paths.add(artifact.relative_path);}
 const parent=path.dirname(target),leaf=path.basename(target);
 if(inspect(target))fail('DS_ATOMIC_EXISTS','target already exists');
 const parentIdentity=inspect(parent);
 if(!parentIdentity?.isDirectory()||fs.realpathSync(parent)!==parent)fail('DS_ATOMIC_PARENT','real parent without symbolic ancestors required');
 // Load before creating a target stage; unavailable native support never falls back to overwrite.
 const native=loadAtomicPublicationNative();
 const parentFd=fs.openSync(parent,fs.constants.O_RDONLY|fs.constants.O_DIRECTORY|fs.constants.O_NOFOLLOW);
 const directories:Directory[]=[],files:File[]=[],byPath=new Map<string,Directory>();
 let published=false;
 const currentParent=()=>{
  const current=inspect(parent);
  if(!current||!same(parentIdentity,current)||!same(parentIdentity,fs.fstatSync(parentFd,{bigint:true}))||fs.realpathSync(parent)!==parent)
   fail('DS_ATOMIC_IDENTITY','output parent identity changed');
 };
 const currentDirectory=(dir:Directory)=>{
  const current=inspect(at(dir.parentFd,dir.name));
  if(!current||!same(dir.identity,current))fail('DS_ATOMIC_IDENTITY','staging directory identity changed');
 };
 function createDirectory(parentFd:number,name:string,mode:number):Directory {
  const file=at(parentFd,name);fs.mkdirSync(file,{mode});
  const identity=fs.lstatSync(file,{bigint:true});
  let fd:number|undefined;
  try{
   fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_DIRECTORY|fs.constants.O_NOFOLLOW);
   if(!same(identity,fs.fstatSync(fd,{bigint:true})))fail('DS_ATOMIC_IDENTITY','new directory identity changed');
   const directory={fd,parentFd,name,identity};directories.push(directory);return directory;
  }catch(error){
   if(fd!==undefined)fs.closeSync(fd);
   const current=inspect(file);
   if(!options?.preserveFailedStage&&current&&same(identity,current))try{fs.rmdirSync(file);}catch(cleanup){if(!['ENOENT','ENOTEMPTY','EEXIST'].includes((cleanup as NodeJS.ErrnoException).code??''))throw cleanup;}
   throw error;
  }
 }
 try{
  currentParent();
  const stage=createDirectory(parentFd,prefix+crypto.randomUUID(),0o700);byPath.set('',stage);
  for(const artifact of artifacts){
   const parts=relative(artifact.relative_path),name=parts.pop()!;let dir=stage,key='';
   currentDirectory(stage);
   for(const part of parts){
    currentDirectory(dir);key=key?key+'/'+part:part;
    let child=byPath.get(key);
    if(!child){child=createDirectory(dir.fd,part,0o755);byPath.set(key,child);}
    currentDirectory(child);dir=child;
   }
   currentDirectory(dir);
   const file=at(dir.fd,name),fd=fs.openSync(file,fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o644);
   try{files.push({parentFd:dir.fd,name,identity:fs.fstatSync(fd,{bigint:true})});fs.writeFileSync(fd,artifact.content,{encoding:'utf8'});}
   finally{fs.closeSync(fd);}
  }
  // Reject missing/replaced/foreign entries before publishing a supposedly complete tree.
  for(const file of files){const current=inspect(at(file.parentFd,file.name));if(!current||!same(file.identity,current))fail('DS_ATOMIC_IDENTITY','staged file identity changed');}
  for(const dir of directories){
   currentDirectory(dir);
   const expected=[...files.filter(f=>f.parentFd===dir.fd).map(f=>f.name),...directories.filter(d=>d.parentFd===dir.fd).map(d=>d.name)].sort();
   if(JSON.stringify(fs.readdirSync(at(dir.fd,'.')).sort())!==JSON.stringify(expected))fail('DS_ATOMIC_IDENTITY','staged inventory changed');
  }
  currentParent();currentDirectory(stage);beforeCommit?.(path.join(parent,stage.name));
  currentParent();currentDirectory(stage);
  try{native.renameNoReplace(parentFd,stage.name,leaf);}
  catch(error){if((error as NodeJS.ErrnoException).code==='EEXIST')fail('DS_ATOMIC_EXISTS','target appeared during publication');throw error;}
  published=true;
  currentParent();
  const result=inspect(at(parentFd,leaf));
  if(!result||!same(stage.identity,result))fail('DS_ATOMIC_IDENTITY','published directory identity changed');
 }finally{
  try{
   if(!published&&!options?.preserveFailedStage){
    // No recursive deletion, no traversal of replacement directories, no deletion of the public target.
    for(const file of files){const name=at(file.parentFd,file.name),current=inspect(name);if(current&&same(file.identity,current))fs.unlinkSync(name);}
    for(const dir of [...directories].reverse()){
     const name=at(dir.parentFd,dir.name),current=inspect(name);
     if(current&&same(dir.identity,current))try{fs.rmdirSync(name);}catch(error){if(!['ENOENT','ENOTEMPTY','EEXIST'].includes((error as NodeJS.ErrnoException).code??''))throw error;}
    }
   }
  }finally{for(const dir of directories)fs.closeSync(dir.fd);fs.closeSync(parentFd);}
 }
}
